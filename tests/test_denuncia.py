"""Base imponibile per cassa e dichiarazioni di concorso (ADR 0005 e 0006). Valori e fonti sono fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import (
    Corpus,
    Mese,
    Periodo,
    TipoEsito,
    calcola,
    calcola_annuale,
    calcola_denuncia,
    differenze,
    emetti_esito,
    spiega,
)
from paghe.errori import ConcorsoMancante, ConcorsoParziale, ErroreCalcolo, ErroreCorpus, ValiditaNonUniforme

R = "RAPPORTO-1"
AGOSTO = Mese(2026, 8)
SETTEMBRE = Mese(2026, 9)

ALIQUOTA = """
[[parametro]]
nome = "aliquota"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "0.10"
riferimento = "fittizio:aliquota"
"""

DIVISORI = """
[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "26"
riferimento = "fittizio:d"

[[parametro]]
nome = "anno"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "365"
riferimento = "fittizio:anno"
"""

REGOLE = """
[periodo_dichiarato]
servizio = "tipo_impiego"
fatti = ["qualifica"]

[[base]]
nome = "pens"
riferimento = "fittizio:base-pens"

[[regola]]
istituto = "stipendio"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio"
formula = "fatto.mensile"
maturazione = "giorni"
applica_se = "mensile"
conteggio = "lun_sab"
divisore = "d"
decimali = 2

[[regola]]
istituto = "straordinario"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:straordinario"
formula = "fatto.ore_pagate"
maturazione = "evento"
applica_se = "ore_pagate"

[[regola]]
istituto = "rimborso"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:rimborso"
formula = "fatto.spesa"
maturazione = "evento"
applica_se = "spesa"

[[regola]]
istituto = "trasferta"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:trasferta"
formula = "fatto.missione"
maturazione = "evento"
applica_se = "missione"

[[regola]]
istituto = "tredicesima"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:tredicesima"
formula = "fatto.mensile"
maturazione = "annuale"
applica_se = "mensile"
conteggio = "calendario"
divisore = "anno"
decimali = 2

[[regola]]
istituto = "contributo"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:contributo"
formula = "arrotonda(base.pens * parametro.aliquota, 2)"
maturazione = "periodo"

[[regola]]
istituto = "quota_lavoratore"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:quota"
formula = "arrotonda(importo.contributo / 4, 2)"
maturazione = "periodo"

[[concorso]]
istituto = "stipendio"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-stipendio"

[[concorso]]
istituto = "straordinario"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-straordinario"

[[concorso]]
istituto = "tredicesima"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-tredicesima"

[[concorso]]
istituto = "rimborso"
basi = ["pens"]
misura = "escluso"
dal = 2020-01-01
riferimento = "fittizio:concorso-rimborso"

[[concorso]]
istituto = "trasferta"
basi = ["pens"]
misura = "parziale"
dal = 2020-01-01
riferimento = "fittizio:concorso-trasferta"
"""

TESTO = ALIQUOTA + DIVISORI + REGOLE


@pytest.fixture
def cassa():
    return Corpus.da_toml(TESTO)


def assumi(registro, dal=date(2020, 1, 1), al=None, mensile="1000.00"):
    registro.registra_codice(R, "tipo_impiego", "1", dal, al)
    registro.registra_fatto(R, "mensile", mensile, dal, al)


def paga(registro, orologio, righe, giorno):
    """Esito e data di pagamento, nell'ordine di un mandato con valuta."""
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(R, esito.id, giorno)
    return esito


def del_mese(registro, corpus, mese, istituti=("stipendio",)):
    return [riga for riga in calcola(registro, corpus, R, mese) if riga.istituto in istituti]


def valori(periodo):
    return {riga.istituto: riga.valore for riga in (*periodo.basi, *periodo.contributi)}


def test_la_base_somma_cio_che_e_pagato_nel_mese_e_non_le_frazioni(registro, cassa, orologio):
    assumi(registro, dal=date(2026, 8, 24))
    righe = del_mese(registro, cassa, AGOSTO) + del_mese(registro, cassa, SETTEMBRE)
    paga(registro, orologio, righe, date(2026, 9, 27))

    assert all(not p.basi and not p.contributi for p in calcola_denuncia(registro, cassa, R, AGOSTO).periodi)
    periodo, = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi
    assert periodo.periodo == SETTEMBRE.periodo
    assert periodo.in_servizio
    assert valori(periodo) == {
        "base.pens": Decimal("1269.23"),
        "contributo": Decimal("126.92"),
        "quota_lavoratore": Decimal("31.73"),
    }


def test_il_contributo_di_cassa_non_compare_nel_calcolo_per_competenza(registro, cassa):
    assumi(registro)
    assert {riga.istituto for riga in calcola(registro, cassa, R, SETTEMBRE)} == {"stipendio"}


def test_senza_data_di_pagamento_l_importo_non_entra_e_viene_segnalato(registro, cassa, orologio):
    assumi(registro)
    orologio.vai(9, 27)
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 9, 27), del_mese(registro, cassa, SETTEMBRE))
    denuncia = calcola_denuncia(registro, cassa, R, SETTEMBRE)
    assert not denuncia.periodi[0].basi
    assert denuncia.esiti_senza_data == (esito.id,)

    orologio.avanza()
    registro.registra_pagamento(R, esito.id, date(2026, 9, 27))
    denuncia = calcola_denuncia(registro, cassa, R, SETTEMBRE)
    assert denuncia.periodi[0].base("pens").valore == Decimal("1000.00")
    assert denuncia.esiti_senza_data == ()


def test_calcolato_ma_non_pagato_non_entra(registro, cassa):
    assumi(registro)
    assert not calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi[0].basi


def test_l_arretrato_sta_nel_mese_in_cui_e_pagato_e_il_mese_originario_non_cambia(registro, cassa, orologio):
    assumi(registro)
    paga(registro, orologio, del_mese(registro, cassa, Mese(2026, 2)), date(2026, 2, 27))
    paga(registro, orologio, del_mese(registro, cassa, Mese(2026, 3)), date(2026, 3, 27))

    orologio.vai(3, 28)
    registro.registra_fatto(R, "mensile", "1100.00", date(2026, 2, 1))
    voci = differenze(registro, cassa, R, Mese(2026, 2), TipoEsito.PAGATO)
    paga(registro, orologio, [voce.importo() for voce in voci], date(2026, 4, 27))

    assert calcola_denuncia(registro, cassa, R, Mese(2026, 2)).periodi[0].base("pens").valore == Decimal("1000.00")
    assert calcola_denuncia(registro, cassa, R, Mese(2026, 3)).periodi[0].base("pens").valore == Decimal("1000.00")
    assert calcola_denuncia(registro, cassa, R, Mese(2026, 4)).periodi[0].base("pens").valore == Decimal("100.00")


def test_stesso_periodo_e_istituto_pagati_due_volte_restano_entrambi_tracciati(registro, cassa, orologio):
    assumi(registro)
    paga(registro, orologio, del_mese(registro, cassa, Mese(2026, 2)), date(2026, 2, 10))
    orologio.avanza()
    registro.registra_fatto(R, "mensile", "1100.00", date(2026, 2, 1))
    voci = differenze(registro, cassa, R, Mese(2026, 2), TipoEsito.PAGATO)
    paga(registro, orologio, [voce.importo() for voce in voci], date(2026, 2, 27))

    base = calcola_denuncia(registro, cassa, R, Mese(2026, 2)).periodi[0].base("pens")
    assert base.valore == Decimal("1100.00")
    assert [riga.valore for riga in base.derivazione.importi] == [Decimal("1000.00"), Decimal("100.00")]


def test_la_correzione_della_valuta_sposta_l_importo_e_resta_la_storia(registro, cassa, orologio):
    assumi(registro)
    esito = paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE), date(2026, 9, 30))
    prima = orologio.ora

    orologio.vai(10, 2)
    registro.registra_pagamento(R, esito.id, date(2026, 10, 1))

    assert not calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi[0].basi
    assert calcola_denuncia(registro, cassa, R, Mese(2026, 10)).periodi[0].base("pens").valore == Decimal("1000.00")
    assert calcola_denuncia(registro, cassa, R, SETTEMBRE, prima).periodi[0].base("pens").valore == Decimal("1000.00")


def test_data_di_pagamento_annullata_riporta_l_esito_tra_quelli_senza_data(registro, cassa, orologio):
    assumi(registro)
    esito = paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE), date(2026, 9, 27))
    fatto = registro.pagamenti(R, orologio.ora)[esito.id]
    orologio.avanza()
    registro.annulla_fatto(fatto.id, "valuta inserita per errore")
    assert calcola_denuncia(registro, cassa, R, SETTEMBRE).esiti_senza_data == (esito.id,)


def test_pagamenti_entro_il_12_gennaio_nell_e0_di_gennaio(registro, cassa, orologio):
    assumi(registro)
    paga(registro, orologio, del_mese(registro, cassa, Mese(2026, 12)), date(2027, 1, 12))
    assert not calcola_denuncia(registro, cassa, R, Mese(2026, 12)).periodi[0].basi
    assert calcola_denuncia(registro, cassa, R, Mese(2027, 1)).periodi[0].base("pens").valore == Decimal("1000.00")


def test_la_tredicesima_concorre_per_intero_nel_mese_in_cui_e_pagata(registro, cassa, orologio):
    assumi(registro)
    righe = del_mese(registro, cassa, Mese(2026, 12)) + list(calcola_annuale(registro, cassa, R, 2026))
    paga(registro, orologio, righe, date(2026, 12, 15))
    assert calcola_denuncia(registro, cassa, R, Mese(2026, 12)).periodi[0].base("pens").valore == Decimal("2000.00")


def test_i_contributi_nell_esito_non_chiedono_dichiarazione_di_concorso(registro, cassa, orologio):
    assumi(registro)
    esito = paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE), date(2026, 9, 27))
    contributi = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi[0].contributi
    orologio.avanza()
    secondo = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 9, 27), contributi)
    registro.registra_pagamento(R, secondo.id, date(2026, 9, 27))
    assert esito.id != secondo.id
    assert calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi[0].base("pens").valore == Decimal("1000.00")


# Aliquota e regola alla data di pagamento

def corpus_con_aliquote(dal="2026-06-15"):
    return Corpus.da_toml(
        TESTO.replace(
            'riferimento = "fittizio:aliquota"\n',
            f'riferimento = "fittizio:aliquota"\n[[parametro.vigenza]]\ndal = {dal}\n'
            'valore = "0.20"\nriferimento = "fittizio:aliquota-nuova"\n',
            1,
        )
    )


def test_l_aliquota_e_quella_vigente_al_pagamento_non_alla_competenza(registro, orologio):
    corpus = corpus_con_aliquote()
    assumi(registro)
    paga(registro, orologio, del_mese(registro, corpus, Mese(2026, 5)), date(2026, 6, 20))
    periodo = calcola_denuncia(registro, corpus, R, Mese(2026, 6)).periodi[0]
    contributo = next(riga for riga in periodo.contributi if riga.istituto == "contributo")
    assert contributo.valore == Decimal("200.00")
    assert contributo.derivazione.parametri[0].riferimento == "fittizio:aliquota-nuova"


def test_competenza_nuova_pagata_prima_del_cambio_usa_l_aliquota_precedente(registro, orologio):
    corpus = corpus_con_aliquote("2026-07-01")
    assumi(registro)
    paga(registro, orologio, del_mese(registro, corpus, Mese(2026, 7)), date(2026, 6, 25))
    assert valori(calcola_denuncia(registro, corpus, R, Mese(2026, 6)).periodi[0])["contributo"] == Decimal("100.00")


def test_due_pagamenti_a_cavallo_del_cambio_di_aliquota_fermano_il_calcolo(registro, orologio):
    corpus = corpus_con_aliquote()
    assumi(registro)
    paga(registro, orologio, del_mese(registro, corpus, Mese(2026, 4)), date(2026, 6, 10))
    paga(registro, orologio, del_mese(registro, corpus, Mese(2026, 5)), date(2026, 6, 20))
    with pytest.raises(ValiditaNonUniforme, match="aliquota"):
        calcola_denuncia(registro, corpus, R, Mese(2026, 6))


def test_regola_di_cassa_scelta_alla_data_di_pagamento(registro, orologio):
    testo = TESTO.replace(
        'formula = "arrotonda(base.pens * parametro.aliquota, 2)"\nmaturazione = "periodo"',
        'formula = "arrotonda(base.pens * parametro.aliquota, 2)"\nmaturazione = "periodo"\nal = 2026-05-31',
    )
    corpus = Corpus.da_toml(
        testo
        + """
[[regola]]
istituto = "contributo"
versione = 1
dal = 2026-06-01
riferimento = "fittizio:contributo-nuovo"
formula = "base.pens / 2"
maturazione = "periodo"
"""
    )
    assumi(registro)
    paga(registro, orologio, del_mese(registro, corpus, Mese(2026, 5)), date(2026, 6, 5))
    assert valori(calcola_denuncia(registro, corpus, R, Mese(2026, 6)).periodi[0])["contributo"] == Decimal("500.00")


def test_senza_regola_di_cassa_vigente_al_pagamento_il_calcolo_si_ferma(registro, orologio):
    corpus = Corpus.da_toml(
        TESTO.replace(
            'formula = "arrotonda(base.pens * parametro.aliquota, 2)"\nmaturazione = "periodo"',
            'formula = "arrotonda(base.pens * parametro.aliquota, 2)"\nmaturazione = "periodo"\nal = 2026-05-31',
        )
    )
    assumi(registro)
    paga(registro, orologio, del_mese(registro, corpus, Mese(2026, 5)), date(2026, 6, 5))
    with pytest.raises(ErroreCalcolo, match="contributo"):
        calcola_denuncia(registro, corpus, R, Mese(2026, 6))


# Dichiarazioni di concorso

def test_istituto_escluso_non_entra_ma_la_dichiarazione_resta_tracciata(registro, cassa, orologio):
    assumi(registro)
    registro.registra_fatto(R, "spesa", "80.00", date(2026, 9, 1), date(2026, 9, 30))
    righe = del_mese(registro, cassa, SETTEMBRE, ("stipendio", "rimborso"))
    paga(registro, orologio, righe, date(2026, 9, 27))
    base = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi[0].base("pens")
    assert base.valore == Decimal("1000.00")
    assert {riga.istituto for riga in base.derivazione.importi} == {"stipendio"}
    letti = {concorso.istituto: concorso for concorso in base.derivazione.concorsi}
    assert letti["rimborso"].misura == "escluso"
    assert letti["rimborso"].riferimento == "fittizio:concorso-rimborso"


def test_solo_importi_esclusi_nessuna_base_e_nessun_contributo(registro, cassa, orologio):
    registro.registra_codice(R, "tipo_impiego", "1", date(2020, 1, 1))
    registro.registra_fatto(R, "spesa", "80.00", date(2026, 9, 1), date(2026, 9, 30))
    paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE, ("rimborso",)), date(2026, 9, 27))
    periodo = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi[0]
    assert not periodo.basi
    assert not periodo.contributi


def test_concorso_parziale_ferma_il_calcolo_e_lo_nomina(registro, cassa, orologio):
    assumi(registro)
    registro.registra_fatto(R, "missione", "50.00", date(2026, 9, 1), date(2026, 9, 30))
    paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE, ("trasferta",)), date(2026, 9, 27))
    with pytest.raises(ConcorsoParziale, match="trasferta.*pens"):
        calcola_denuncia(registro, cassa, R, SETTEMBRE)


def test_concorso_assente_ferma_il_calcolo_e_lo_nomina(registro, orologio):
    corpus = Corpus.da_toml(
        TESTO.replace(
            '[[concorso]]\nistituto = "straordinario"\nbasi = ["pens"]\nmisura = "intero"\n'
            'dal = 2020-01-01\nriferimento = "fittizio:concorso-straordinario"\n',
            "",
        )
    )
    assumi(registro)
    registro.registra_fatto(R, "ore_pagate", "50.00", date(2026, 9, 1), date(2026, 9, 30))
    paga(registro, orologio, del_mese(registro, corpus, SETTEMBRE, ("straordinario",)), date(2026, 9, 27))
    with pytest.raises(ConcorsoMancante, match="straordinario.*pens"):
        calcola_denuncia(registro, corpus, R, SETTEMBRE)


def test_il_concorso_si_sceglie_alla_data_di_pagamento(registro, orologio):
    corpus = Corpus.da_toml(
        TESTO.replace(
            'dal = 2020-01-01\nriferimento = "fittizio:concorso-stipendio"',
            'dal = 2020-01-01\nal = 2026-12-31\nriferimento = "fittizio:concorso-stipendio"',
        )
    )
    assumi(registro)
    paga(registro, orologio, del_mese(registro, corpus, Mese(2026, 12)), date(2027, 1, 5))
    with pytest.raises(ConcorsoMancante, match="stipendio"):
        calcola_denuncia(registro, corpus, R, Mese(2027, 1))


def test_ogni_base_ha_le_proprie_dichiarazioni(registro, orologio):
    corpus = Corpus.da_toml(
        TESTO.replace('nome = "pens"\nriferimento = "fittizio:base-pens"\n',
                      'nome = "pens"\nriferimento = "fittizio:base-pens"\n\n'
                      '[[base]]\nnome = "credito"\nriferimento = "fittizio:base-credito"\n')
        + """
[[concorso]]
istituto = "stipendio"
basi = ["credito"]
misura = "escluso"
dal = 2020-01-01
riferimento = "fittizio:concorso-credito"
"""
    )
    assumi(registro)
    paga(registro, orologio, del_mese(registro, corpus, SETTEMBRE), date(2026, 9, 27))
    periodo = calcola_denuncia(registro, corpus, R, SETTEMBRE).periodi[0]
    assert periodo.base("pens").valore == Decimal("1000.00")
    assert periodo.base("credito") is None


def test_basi_multiple_nella_stessa_dichiarazione(registro, orologio):
    corpus = Corpus.da_toml(
        TESTO.replace('nome = "pens"\nriferimento = "fittizio:base-pens"\n',
                      'nome = "pens"\nriferimento = "fittizio:base-pens"\n\n'
                      '[[base]]\nnome = "credito"\nriferimento = "fittizio:base-credito"\n').replace(
            'istituto = "stipendio"\nbasi = ["pens"]', 'istituto = "stipendio"\nbasi = ["pens", "credito"]'
        )
    )
    assumi(registro)
    paga(registro, orologio, del_mese(registro, corpus, SETTEMBRE), date(2026, 9, 27))
    periodo = calcola_denuncia(registro, corpus, R, SETTEMBRE).periodi[0]
    assert periodo.base("credito").valore == Decimal("1000.00")


# Periodi dichiarati

def cambio_qualifica(registro):
    assumi(registro)
    registro.registra_codice(R, "qualifica", "A", date(2020, 1, 1), date(2026, 9, 14))
    registro.registra_codice(R, "qualifica", "B", date(2026, 9, 15))


def test_il_fisso_resta_sui_propri_giorni_e_il_resto_segue_il_pagamento(registro, cassa, orologio):
    cambio_qualifica(registro)
    registro.registra_fatto(R, "ore_pagate", "50.00", date(2026, 9, 20), date(2026, 9, 20))
    righe = del_mese(registro, cassa, SETTEMBRE, ("stipendio", "straordinario"))
    paga(registro, orologio, righe, date(2026, 9, 27))

    prima, dopo = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi
    assert prima.periodo == Periodo(date(2026, 9, 1), date(2026, 9, 14))
    assert dopo.periodo == Periodo(date(2026, 9, 15), date(2026, 9, 30))
    assert prima.base("pens").valore == Decimal("461.54")
    assert dopo.base("pens").valore == Decimal("538.46") + Decimal("50.00")
    assert prima.base("pens").periodo == prima.periodo
    assert valori(prima)["contributo"] == Decimal("46.15")
    assert valori(dopo)["contributo"] == Decimal("58.85")


def test_fisso_di_un_mese_precedente_nel_periodo_del_pagamento(registro, cassa, orologio):
    cambio_qualifica(registro)
    paga(registro, orologio, del_mese(registro, cassa, AGOSTO), date(2026, 9, 10))
    prima, dopo = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi
    assert prima.base("pens").valore == Decimal("1000.00")
    assert dopo.base("pens") is None


def test_pagamento_dopo_la_fine_del_servizio_nell_ultimo_periodo(registro, cassa, orologio):
    assumi(registro, al=date(2026, 9, 10))
    registro.registra_fatto(R, "ore_pagate", "50.00", date(2026, 9, 5), date(2026, 9, 5))
    righe = del_mese(registro, cassa, SETTEMBRE, ("straordinario",))
    paga(registro, orologio, righe, date(2026, 9, 27))
    periodo, = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi
    assert periodo.periodo == Periodo(date(2026, 9, 1), date(2026, 9, 10))
    assert periodo.in_servizio
    assert periodo.base("pens").valore == Decimal("50.00")


def test_pagamento_prima_dell_inizio_del_servizio_ferma_il_calcolo(registro, cassa, orologio):
    assumi(registro, dal=date(2026, 9, 20))
    registro.registra_fatto(R, "ore_pagate", "50.00", date(2026, 9, 20), date(2026, 9, 30))
    righe = del_mese(registro, cassa, SETTEMBRE, ("straordinario",))
    paga(registro, orologio, righe, date(2026, 9, 10))
    with pytest.raises(ErroreCalcolo, match="straordinario.*2026-09-10"):
        calcola_denuncia(registro, cassa, R, SETTEMBRE)


def test_senza_servizio_nel_mese_gli_importi_si_calcolano_fuori_servizio(registro, cassa, orologio):
    assumi(registro, al=date(2026, 6, 30))
    orologio.vai(7, 1)
    registro.registra_fatto(R, "mensile", "1100.00", date(2026, 6, 1), date(2026, 6, 30))
    voci = differenze(registro, cassa, R, Mese(2026, 6), TipoEsito.PAGATO)
    paga(registro, orologio, [voce.importo() for voce in voci], date(2026, 10, 27))

    periodo, = calcola_denuncia(registro, cassa, R, Mese(2026, 10)).periodi
    assert not periodo.in_servizio
    assert periodo.periodo == Mese(2026, 10).periodo
    assert periodo.base("pens").valore == Decimal("1100.00")


def test_senza_servizio_e_senza_pagamenti_nessun_periodo(registro, cassa):
    assumi(registro, al=date(2026, 6, 30))
    assert calcola_denuncia(registro, cassa, R, Mese(2026, 10)).periodi == ()


def test_aumento_di_importo_non_apre_un_periodo(registro, cassa, orologio):
    assumi(registro)
    registro.registra_fatto(R, "mensile", "1300.00", date(2026, 9, 15))
    paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE), date(2026, 9, 27))
    periodo, = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi
    assert len(periodo.base("pens").derivazione.importi) == 2


def test_lo_stesso_codice_registrato_di_nuovo_non_apre_un_periodo(registro, cassa):
    assumi(registro)
    registro.registra_codice(R, "qualifica", "A", date(2020, 1, 1))
    registro.registra_codice(R, "qualifica", "A", date(2026, 9, 15))
    assert len(calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi) == 1


def test_gli_altri_rapporti_non_entrano(registro, cassa, orologio):
    assumi(registro)
    registro.registra_codice("ALTRO", "tipo_impiego", "1", date(2020, 1, 1))
    registro.registra_fatto("ALTRO", "mensile", "500", date(2020, 1, 1))
    righe = list(calcola(registro, cassa, "ALTRO", SETTEMBRE))
    orologio.vai(9, 27)
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 9, 27), righe)
    registro.registra_pagamento("ALTRO", esito.id, date(2026, 9, 27))
    denuncia = calcola_denuncia(registro, cassa, R, SETTEMBRE)
    assert not denuncia.periodi[0].basi
    assert denuncia.esiti_senza_data == ()


# Tracciabilità

def test_spiegazione_arriva_a_pagamento_concorso_e_norma(registro, cassa, orologio):
    assumi(registro)
    paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE), date(2026, 9, 27))
    contributo = next(
        riga for riga in calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi[0].contributi
        if riga.istituto == "contributo"
    )
    testo = spiega(contributo)
    for atteso in (
        "fittizio:contributo",
        "fittizio:aliquota",
        "fittizio:base-pens",
        "fittizio:concorso-stipendio",
        "concorso stipendio -> pens: intero",
        "pagato il 2026-09-27",
        "data_pagamento",
    ):
        assert atteso in testo


def test_base_e_contributi_si_fissano_in_un_esito_dichiarato(registro, cassa, orologio):
    assumi(registro)
    paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE), date(2026, 9, 27))
    periodo = calcola_denuncia(registro, cassa, R, SETTEMBRE).periodi[0]
    orologio.avanza()
    esito = emetti_esito(registro, TipoEsito.DICHIARATO, date(2026, 10, 31), (*periodo.basi, *periodo.contributi))
    riletto = registro.esito(esito.id)
    assert riletto == esito
    base = next(riga for riga in riletto.righe if riga.istituto == "base.pens")
    assert base.derivazione.importi[0].data_pagamento == date(2026, 9, 27)
    assert base.derivazione.concorsi


def test_denuncia_riproducibile(registro, cassa, orologio):
    assumi(registro)
    paga(registro, orologio, del_mese(registro, cassa, SETTEMBRE), date(2026, 9, 27))
    istante = registro.adesso()
    assert calcola_denuncia(registro, cassa, R, SETTEMBRE, istante) == calcola_denuncia(registro, cassa, R, SETTEMBRE, istante)


# Controlli sul corpus

@pytest.mark.parametrize(
    ("vecchio", "nuovo", "messaggio"),
    [
        ('istituto = "stipendio"\nbasi = ["pens"]', 'istituto = "ignoto"\nbasi = ["pens"]', "ignoto"),
        ('istituto = "stipendio"\nbasi = ["pens"]', 'istituto = "stipendio"\nbasi = ["ignota"]', "ignota"),
        ('istituto = "stipendio"\nbasi = ["pens"]', 'istituto = "stipendio"\nbasi = []', "basi"),
        ('basi = ["pens"]\nmisura = "intero"', 'basi = ["pens"]\nmisura = "boh"', "misura"),
        ('riferimento = "fittizio:concorso-stipendio"', 'riferimento = "non valido"', "riferimento"),
        ('riferimento = "fittizio:base-pens"', 'riferimento = ""', "riferimento"),
        ('servizio = "tipo_impiego"\n', "", "servizio"),
        ("base.pens * parametro.aliquota", "base.ignota * parametro.aliquota", "ignota"),
        ('formula = "fatto.ore_pagate"', 'formula = "base.pens"', "periodo"),
        ("base.pens * parametro.aliquota", "base.pens * parametro.aliquota + importo.stipendio", "cassa"),
    ],
)
def test_corpus_incoerente_rifiutato(vecchio, nuovo, messaggio):
    assert vecchio in TESTO
    with pytest.raises(ErroreCorpus, match=messaggio):
        Corpus.da_toml(TESTO.replace(vecchio, nuovo, 1))


def test_concorsi_con_vigenze_sovrapposte_rifiutati():
    with pytest.raises(ErroreCorpus, match="sovrapposte"):
        Corpus.da_toml(
            TESTO
            + """
[[concorso]]
istituto = "stipendio"
basi = ["pens"]
misura = "escluso"
dal = 2026-01-01
riferimento = "fittizio:doppione"
"""
        )


def test_regole_dello_stesso_istituto_tutte_di_cassa_o_tutte_no():
    with pytest.raises(ErroreCorpus, match="cassa"):
        Corpus.da_toml(
            TESTO.replace(
                'formula = "arrotonda(base.pens * parametro.aliquota, 2)"\nmaturazione = "periodo"',
                'formula = "arrotonda(base.pens * parametro.aliquota, 2)"\nmaturazione = "periodo"\nal = 2026-05-31',
            )
            + """
[[regola]]
istituto = "contributo"
versione = 1
dal = 2026-06-01
riferimento = "fittizio:prova"
formula = "parametro.aliquota"
maturazione = "periodo"
"""
        )


def test_la_versione_del_corpus_dipende_da_basi_e_concorsi(cassa):
    assert Corpus.da_toml(TESTO.replace('misura = "escluso"', 'misura = "intero"')).versione != cassa.versione
    assert Corpus.da_toml(TESTO.replace("fittizio:base-pens", "fittizio:base-altra")).versione != cassa.versione


def test_corpus_senza_basi_non_produce_denuncia(registro, corpus):
    with pytest.raises(ErroreCorpus, match="base"):
        calcola_denuncia(registro, corpus, R, SETTEMBRE)
