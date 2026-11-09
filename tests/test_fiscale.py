"""Ritenuta del pagamento, imponibile fiscale per persona e conguaglio (ADR 0019). Valori e fonti fittizi.

I numeri sono scelti per tornare a mano. Scaglioni annui: 10% fino a 10000, 20% fino a 30000, 30% oltre.
Detrazione annua: 1200, ridotta in proporzione fino a 40000 di reddito. Periodo di paga: il mese.

Un pagamento mensile di 1500 senza detrazione:
  scaglioni ragguagliati (diviso 12): 833,33 e 2500; imposta 0,10 * 833,33 + 0,20 * (1500 - 833,33) = 216,67.
Con la detrazione, 1200 * (40000 - 1500 * 12) / 40000 / 12 = 55,00; ritenuta 161,67.
Su dodici pagamenti di 1500 il reddito è 18000: imposta annua 2600, detrazione annua 660, dovuto 1940,00.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import (
    Atto,
    Corpus,
    Mese,
    Periodo,
    TipoEsito,
    attribuisci_reddito,
    calcola,
    calcola_denuncia,
    calcola_fiscale,
    conguaglio_per_differenza,
    differenze,
    emetti_esito,
    imponibile_fiscale,
    proiezione_conguaglio,
    spiega,
)
from paghe.errori import (
    CasoNonModellato,
    ErroreCalcolo,
    ErroreCorpus,
    ErroreRegistro,
    FattoMancante,
    RedditoMancante,
)

CORPUS_REALE = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
CF = "RSSMRA80A01H501U"
P = "PERSONA-1"
R = "RAPPORTO-1"
ALTRO = "RAPPORTO-2"

IMPOSTA = """arrotonda(
    parametro.aliquota_1 * min(fisco.imponibile, parametro.limite_1 / fisco.periodi)
    + parametro.aliquota_2 * max(0, min(fisco.imponibile, parametro.limite_2 / fisco.periodi) - parametro.limite_1 / fisco.periodi)
    + parametro.aliquota_3 * max(0, fisco.imponibile - parametro.limite_2 / fisco.periodi), 2)"""

DETRAZIONE = """arrotonda(
    parametro.detrazione_annua * max(0, parametro.limite_detrazione - fisco.imponibile * fisco.periodi)
    / parametro.limite_detrazione / fisco.periodi, 2)"""


def _parametri() -> str:
    voci = {
        "limite_1": "10000",
        "limite_2": "30000",
        "aliquota_1": "0.10",
        "aliquota_2": "0.20",
        "aliquota_3": "0.30",
        "detrazione_annua": "1200",
        "limite_detrazione": "40000",
    }
    return "".join(
        f'''
[[parametro]]
nome = "{nome}"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "{valore}"
riferimento = "fittizio:{nome.replace('_', '-')}"
'''
        for nome, valore in voci.items()
    )


FISCALE = f"""
[[categoria_reddito]]
nome = "lavoro_dipendente"
[[categoria_reddito.cassa_allargata]]
dal = 2020-01-01
vale = true
riferimento = "fittizio:cassa-lavoro"

[[categoria_reddito]]
nome = "carica_elettiva"
[[categoria_reddito.cassa_allargata]]
dal = 2020-01-01
vale = false
riferimento = "fittizio:cassa-carica"

[[reddito]]
istituto = "stipendio"
categoria = "lavoro_dipendente"
dal = 2020-01-01
riferimento = "fittizio:reddito-stipendio"

[[reddito]]
istituto = "gettone"
categoria = "carica_elettiva"
dal = 2020-01-01
riferimento = "fittizio:reddito-gettone"

[[ritenuta]]
istituto = "ritenuta_irpef"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:ritenuta"
categorie = ["lavoro_dipendente"]
detrazione_richiesta = "lavoro_dipendente"
imposta = '''{IMPOSTA}'''
detrazione = '''{DETRAZIONE}'''

[[conguaglio]]
istituto = "conguaglio_irpef"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:conguaglio"
"""

REGOLE = """
[periodo_dichiarato]
servizio = "tipo_impiego"

[[base]]
nome = "pens"
riferimento = "fittizio:base-pens"

[[regola]]
istituto = "stipendio"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio"
formula = "fatto.mensile"
maturazione = "evento"
applica_se = "mensile"

[[regola]]
istituto = "gettone"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:gettone"
formula = "fatto.gettone"
maturazione = "evento"
applica_se = "gettone"

[[concorso]]
istituto = "stipendio"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-stipendio"

[[concorso]]
istituto = "gettone"
basi = ["pens"]
misura = "escluso"
dal = 2020-01-01
riferimento = "fittizio:concorso-gettone"
"""

TESTO = _parametri() + REGOLE + FISCALE


@pytest.fixture
def fisco():
    return Corpus.da_toml(TESTO)


def assumi(registro, rapporto=R, persona=P, dal=date(2026, 1, 1)):
    if not registro.fatti_persona_noti(persona, "codice_fiscale", registro.adesso()):
        registro.registra_codice_persona(persona, "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(rapporto, persona, dal)
    registro.registra_codice(rapporto, "tipo_impiego", "1", dal)


def dichiara(registro, orologio, dal=date(2026, 1, 1), persona=P, quando=None):
    if quando:
        orologio.vai(quando.month, quando.day, quando.year)
    return registro.registra_dichiarazione_sostituito(
        persona, "lavoro_dipendente", dal, None, Atto("ente:c_x000:modulo:2026-01-10;1", date(2026, 1, 10))
    )


def stipendio(registro, corpus, mese, importo="1500", rapporto=R):
    registro.registra_fatto(rapporto, "mensile", importo, mese.primo_giorno, mese.ultimo_giorno)
    return calcola(registro, corpus, rapporto, mese)


def paga(registro, orologio, corpus, righe, giorno, rapporto=R, ultimo=False):
    """Un pagamento: attribuzione, ritenuta ed eventuale conguaglio, poi l'esito pagato con la sua data."""
    orologio.vai(giorno.month, giorno.day, giorno.year)
    attribuite = attribuisci_reddito(corpus, righe, giorno)
    fiscale = calcola_fiscale(registro, corpus, rapporto, attribuite, giorno, ultimo_dell_anno=ultimo)
    contenuto = [*attribuite, fiscale.ritenuta, *([fiscale.conguaglio] if fiscale.conguaglio else [])]
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, contenuto)
    registro.registra_pagamento(rapporto, esito.id, giorno)
    orologio.avanza()
    return esito, fiscale


def anno_di_paghe(registro, orologio, corpus, fino_a=12, rapporto=R):
    """Pagamenti di 1500 il 27 di ogni mese del 2026; l'ultimo porta il conguaglio."""
    risultati = []
    for numero in range(1, fino_a + 1):
        mese = Mese(2026, numero)
        orologio.vai(numero, 1)
        righe = stipendio(registro, corpus, mese, rapporto=rapporto)
        risultati.append(paga(registro, orologio, corpus, righe, date(2026, numero, 27), rapporto, ultimo=numero == 12))
    return risultati


# Anno d'imposta e categoria di reddito dichiarate dall'istituto

def test_l_istituto_dichiara_la_categoria_e_l_anno_e_la_data_di_pagamento(registro, fisco, orologio):
    assumi(registro)
    righe = stipendio(registro, fisco, Mese(2026, 6))
    (riga,) = attribuisci_reddito(fisco, righe, date(2026, 6, 27))
    assert (riga.categoria_reddito, riga.anno_imposta) == ("lavoro_dipendente", 2026)


def test_con_la_cassa_allargata_il_pagamento_entro_il_12_gennaio_va_all_anno_prima(registro, fisco, orologio):
    assumi(registro)
    righe = stipendio(registro, fisco, Mese(2026, 12))
    (primo,) = attribuisci_reddito(fisco, righe, date(2027, 1, 1))
    (ultimo,) = attribuisci_reddito(fisco, righe, date(2027, 1, 12))
    assert primo.anno_imposta == ultimo.anno_imposta == 2026


def test_il_pagamento_dopo_il_12_gennaio_va_all_anno_del_pagamento(registro, fisco, orologio):
    assumi(registro)
    righe = stipendio(registro, fisco, Mese(2027, 1))
    (riga,) = attribuisci_reddito(fisco, righe, date(2027, 1, 13))
    assert riga.anno_imposta == 2027


def test_senza_cassa_allargata_l_anno_e_quello_del_pagamento(registro, fisco, orologio):
    assumi(registro)
    registro.registra_fatto(R, "gettone", "100", date(2027, 1, 1), date(2027, 1, 31))
    righe = calcola(registro, fisco, R, Mese(2027, 1))
    (riga,) = attribuisci_reddito(fisco, righe, date(2027, 1, 10))
    assert (riga.categoria_reddito, riga.anno_imposta) == ("carica_elettiva", 2027)


def test_un_istituto_senza_categoria_ferma_il_calcolo(registro, orologio):
    blocco = (
        '[[reddito]]\nistituto = "stipendio"\ncategoria = "lavoro_dipendente"\n'
        'dal = 2020-01-01\nriferimento = "fittizio:reddito-stipendio"\n'
    )
    assert blocco in TESTO
    corpus = Corpus.da_toml(TESTO.replace(blocco, ""))
    assumi(registro)
    righe = stipendio(registro, corpus, Mese(2026, 6))
    with pytest.raises(RedditoMancante, match="stipendio"):
        attribuisci_reddito(corpus, righe, date(2026, 6, 27))


def test_senza_dichiarazione_della_cassa_allargata_alla_data_il_calcolo_si_ferma(registro, fisco, orologio):
    assumi(registro)
    corpus = Corpus.da_toml(TESTO.replace("dal = 2020-01-01\nvale = true", "dal = 2026-01-01\nvale = true"))
    righe = stipendio(registro, corpus, Mese(2025, 6))
    with pytest.raises(RedditoMancante, match="cassa allargata"):
        attribuisci_reddito(corpus, righe, date(2025, 6, 27))


def test_un_pagamento_di_competenza_di_un_altro_anno_senza_causa_ferma_il_calcolo(registro, fisco, orologio):
    """La causa del pagamento tardivo e la tassazione separata non sono in questa fetta (ADR 0018)."""
    assumi(registro)
    righe = stipendio(registro, fisco, Mese(2026, 12))
    with pytest.raises(CasoNonModellato, match="causa del pagamento tardivo"):
        attribuisci_reddito(fisco, righe, date(2027, 1, 13))


def test_l_anno_e_la_categoria_restano_congelati_nell_esito(registro, fisco, orologio):
    assumi(registro)
    esito, _ = paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 6)), date(2026, 6, 27))
    letto = registro.esito(esito.id)
    stipendi = [riga for riga in letto.righe if riga.istituto == "stipendio"]
    assert [(riga.anno_imposta, riga.categoria_reddito) for riga in stipendi] == [(2026, "lavoro_dipendente")]


# Imponibile fiscale per persona e anno d'imposta

def test_l_imponibile_fiscale_somma_gli_esiti_pagati_di_tutti_i_rapporti_della_persona(registro, fisco, orologio):
    assumi(registro)
    assumi(registro, rapporto=ALTRO)
    paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 3)), date(2026, 3, 27))
    paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 4), "500", ALTRO), date(2026, 4, 27), ALTRO)
    base = imponibile_fiscale(registro, P, 2026)
    assert base.valore == Decimal("2000")
    assert {riga.rapporto for riga in base.righe} == {R, ALTRO}


def test_l_imponibile_fiscale_e_per_anno_e_per_persona(registro, fisco, orologio):
    assumi(registro)
    assumi(registro, rapporto=ALTRO, persona="PERSONA-2")
    paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 3)), date(2026, 3, 27))
    paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 4), "700", ALTRO), date(2026, 4, 27), ALTRO)
    orologio.vai(1, 5, 2027)
    paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2027, 1), "900"), date(2027, 1, 27))
    assert imponibile_fiscale(registro, P, 2026).valore == Decimal("1500")
    assert imponibile_fiscale(registro, P, 2027).valore == Decimal("900")
    assert imponibile_fiscale(registro, "PERSONA-2", 2026).valore == Decimal("700")


def test_l_imponibile_fiscale_senza_esiti_e_zero(registro):
    assert imponibile_fiscale(registro, P, 2026).valore == Decimal(0)


def test_un_esito_pagato_senza_anno_d_imposta_ferma_l_imponibile(registro, fisco, orologio):
    assumi(registro)
    righe = stipendio(registro, fisco, Mese(2026, 3))
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 3, 27), righe)
    registro.registra_pagamento(R, esito.id, date(2026, 3, 27))
    with pytest.raises(RedditoMancante, match="anno d'imposta"):
        imponibile_fiscale(registro, P, 2026)


# Ritenuta del pagamento

def test_la_ritenuta_ragguaglia_gli_scaglioni_al_periodo_di_paga(registro, fisco, orologio):
    assumi(registro)
    _, fiscale = paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 6)), date(2026, 6, 27))
    assert fiscale.ritenuta.valore == Decimal("216.67")


def test_con_la_dichiarazione_le_detrazioni_sono_rapportate_al_periodo(registro, fisco, orologio):
    assumi(registro)
    dichiara(registro, orologio)
    _, fiscale = paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 6)), date(2026, 6, 27))
    assert fiscale.ritenuta.valore == Decimal("161.67")
    assert [fatto.tipo for fatto in fiscale.ritenuta.derivazione.fatti] == ["dichiarazione_sostituito"]
    assert not fiscale.avvisi_di("senza_dichiarazione_sostituito")


def test_senza_dichiarazione_nessuna_detrazione_una_segnalazione_e_nessun_fermo(registro, fisco, orologio):
    assumi(registro)
    _, fiscale = paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 6)), date(2026, 6, 27))
    (avviso,) = fiscale.avvisi_di("senza_dichiarazione_sostituito")
    assert avviso.persona == P
    assert fiscale.ritenuta.derivazione.fatti == ()


def test_una_dichiarazione_scaduta_non_da_detrazioni(registro, fisco, orologio):
    assumi(registro)
    registro.registra_dichiarazione_sostituito(
        P, "lavoro_dipendente", date(2026, 1, 1), date(2026, 5, 31), Atto("ente:c_x000:modulo:2026-01-10;1", date(2026, 1, 10))
    )
    _, fiscale = paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 6)), date(2026, 6, 27))
    assert fiscale.ritenuta.valore == Decimal("216.67")
    assert fiscale.avvisi_di("senza_dichiarazione_sostituito")


def test_la_dichiarazione_vuole_il_documento_di_origine(registro):
    with pytest.raises(ErroreRegistro, match="documento"):
        registro.registra_dichiarazione_sostituito(P, "lavoro_dipendente", date(2026, 1, 1), None, None)


def test_la_ritenuta_e_un_importo_sul_rapporto_con_derivazione_fino_al_cumulo(registro, fisco, orologio):
    assumi(registro)
    assumi(registro, rapporto=ALTRO)
    paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 3)), date(2026, 3, 20))
    _, fiscale = paga(
        registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 3), "500", ALTRO), date(2026, 3, 27), ALTRO
    )
    ritenuta = fiscale.ritenuta
    assert (ritenuta.rapporto, ritenuta.istituto) == (ALTRO, "ritenuta_irpef")
    assert ritenuta.derivazione.maturazione == "ritenuta"
    assert {riga.rapporto for riga in ritenuta.derivazione.importi} == {R, ALTRO}
    testo = spiega(ritenuta)
    assert "ritenuta_irpef" in testo and "stipendio" in testo and f"rapporto {R}" in testo
    assert {p.nome for p in ritenuta.derivazione.parametri} >= {"aliquota_1", "limite_1", "limite_2"}


def test_due_rapporti_della_stessa_persona_nello_stesso_periodo_hanno_gli_scaglioni_una_volta(registro, fisco, orologio):
    """Primo pagamento 1500: 216,67. Secondo di 500 nello stesso mese: su 2000 l'imposta è 316,67, meno 216,67."""
    assumi(registro)
    assumi(registro, rapporto=ALTRO)
    _, primo = paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 3)), date(2026, 3, 20))
    _, secondo = paga(
        registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 3), "500", ALTRO), date(2026, 3, 27), ALTRO
    )
    assert primo.ritenuta.valore == Decimal("216.67")
    assert secondo.ritenuta.valore == Decimal("100.00")


def test_pagamenti_di_mesi_diversi_hanno_ciascuno_la_propria_ritenuta(registro, fisco, orologio):
    assumi(registro)
    (_, uno), (_, due) = anno_di_paghe(registro, orologio, fisco, fino_a=2)
    assert uno.ritenuta.valore == due.ritenuta.valore == Decimal("216.67")


def test_un_rapporto_senza_persona_ferma_la_ritenuta(registro, fisco, orologio):
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 1, 1))
    righe = attribuisci_reddito(fisco, stipendio(registro, fisco, Mese(2026, 6)), date(2026, 6, 27))
    with pytest.raises(FattoMancante, match="persona"):
        calcola_fiscale(registro, fisco, R, righe, date(2026, 6, 27))


def test_una_categoria_che_la_regola_non_copre_ferma_la_ritenuta(registro, fisco, orologio):
    assumi(registro)
    registro.registra_fatto(R, "gettone", "100", date(2026, 6, 1), date(2026, 6, 30))
    righe = attribuisci_reddito(fisco, calcola(registro, fisco, R, Mese(2026, 6)), date(2026, 6, 27))
    with pytest.raises(CasoNonModellato, match="carica_elettiva"):
        calcola_fiscale(registro, fisco, R, righe, date(2026, 6, 27))


def test_le_righe_di_un_altra_persona_non_si_pagano_con_questo_rapporto(registro, fisco, orologio):
    assumi(registro)
    assumi(registro, rapporto=ALTRO, persona="PERSONA-2")
    righe = attribuisci_reddito(fisco, stipendio(registro, fisco, Mese(2026, 6), rapporto=ALTRO), date(2026, 6, 27))
    with pytest.raises(ErroreCalcolo, match="altra persona"):
        calcola_fiscale(registro, fisco, R, righe, date(2026, 6, 27))


def test_righe_senza_anno_d_imposta_fermano_la_ritenuta(registro, fisco, orologio):
    assumi(registro)
    with pytest.raises(RedditoMancante):
        calcola_fiscale(registro, fisco, R, stipendio(registro, fisco, Mese(2026, 6)), date(2026, 6, 27))


def test_i_parametri_si_scelgono_all_anno_d_imposta(registro, orologio):
    """Un pagamento del 10 gennaio 2027, attribuito al 2026, usa i parametri del 2026."""
    nuovo = TESTO.replace(
        '[[parametro.vigenza]]\ndal = 2020-01-01\nvalore = "0.10"\nriferimento = "fittizio:aliquota-1"',
        '[[parametro.vigenza]]\ndal = 2020-01-01\nvalore = "0.10"\nriferimento = "fittizio:aliquota-1"\n'
        '[[parametro.vigenza]]\ndal = 2027-01-01\nvalore = "0.50"\nriferimento = "fittizio:aliquota-1-nuova"',
    )
    corpus = Corpus.da_toml(nuovo)
    assumi(registro)
    orologio.vai(12, 1)
    righe = stipendio(registro, corpus, Mese(2026, 12))
    _, fiscale = paga(registro, orologio, corpus, righe, date(2027, 1, 10))
    assert fiscale.ritenuta.valore == Decimal("216.67")


# Conguaglio sull'ultimo pagamento attribuito all'anno

def test_il_conguaglio_si_fa_sull_ultimo_pagamento_dell_anno(registro, fisco, orologio):
    assumi(registro)
    dichiara(registro, orologio)
    esiti = anno_di_paghe(registro, orologio, fisco)
    ritenute = [fiscale.ritenuta.valore for _, fiscale in esiti]
    assert ritenute == [Decimal("161.67")] * 12
    assert all(fiscale.conguaglio is None for _, fiscale in esiti[:-1])
    conguaglio = esiti[-1][1].conguaglio
    # dovuto 1940,00; ritenute operate 12 * 161,67 = 1940,04
    assert conguaglio.valore == Decimal("-0.04")
    assert (conguaglio.istituto, conguaglio.anno_imposta) == ("conguaglio_irpef", 2026)
    assert conguaglio.derivazione.maturazione == "conguaglio"


def test_il_conguaglio_deriva_dall_imponibile_fiscale_e_dalle_ritenute_operate(registro, fisco, orologio):
    assumi(registro)
    dichiara(registro, orologio)
    esiti = anno_di_paghe(registro, orologio, fisco)
    conguaglio = esiti[-1][1].conguaglio
    istituti = [riga.istituto for riga in conguaglio.derivazione.importi]
    assert istituti.count("stipendio") == 12 and istituti.count("ritenuta_irpef") == 12
    assert "conguaglio_irpef" in spiega(conguaglio)


def test_il_conguaglio_riconosce_la_detrazione_dichiarata_dopo_i_primi_pagamenti(registro, fisco, orologio):
    """Sei ritenute senza detrazione (6 * 216,67) e sei con (6 * 161,67): 2270,04 contro un dovuto di 1940,00."""
    assumi(registro)
    for numero in range(1, 7):
        orologio.vai(numero, 1)
        paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, numero)), date(2026, numero, 27))
    dichiara(registro, orologio, dal=date(2026, 7, 1), quando=date(2026, 7, 2))
    for numero in range(7, 13):
        orologio.vai(numero, 1) if numero > 7 else None
        paga(
            registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, numero)), date(2026, numero, 27),
            ultimo=numero == 12,
        )
    conguaglio = registro.esiti(TipoEsito.PAGATO, registro.adesso())[-1].righe
    (valore,) = [riga.valore for riga in conguaglio if riga.istituto == "conguaglio_irpef"]
    assert valore == Decimal("-330.04")


def test_un_pagamento_che_non_e_l_ultimo_non_puo_portare_il_conguaglio(registro, fisco, orologio):
    assumi(registro)
    orologio.vai(12, 1)
    paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 12)), date(2026, 12, 27))
    orologio.vai(12, 28)
    righe = attribuisci_reddito(fisco, stipendio(registro, fisco, Mese(2026, 11)), date(2026, 12, 20))
    with pytest.raises(ErroreCalcolo, match="non è l'ultimo"):
        calcola_fiscale(registro, fisco, R, righe, date(2026, 12, 20), ultimo_dell_anno=True)


def test_il_conguaglio_dell_anno_prima_su_un_pagamento_di_gennaio_con_la_cassa_allargata(registro, fisco, orologio):
    assumi(registro)
    esiti = anno_di_paghe(registro, orologio, fisco, fino_a=11)
    orologio.vai(12, 1)
    righe = stipendio(registro, fisco, Mese(2026, 12))
    _, fiscale = paga(registro, orologio, fisco, righe, date(2027, 1, 10), ultimo=True)
    assert fiscale.conguaglio.anno_imposta == 2026
    assert fiscale.ritenuta.anno_imposta == 2026
    assert len(esiti) == 11


# Conguaglio per differenza

def _anno_chiuso_senza_detrazione(registro, orologio, corpus):
    assumi(registro)
    return anno_di_paghe(registro, orologio, corpus)


def test_senza_fatti_nuovi_non_c_e_differenza(registro, fisco, orologio):
    _anno_chiuso_senza_detrazione(registro, orologio, fisco)
    orologio.vai(2, 10, 2027)
    assert conguaglio_per_differenza(registro, fisco, R, 2026, date(2027, 2, 26)) is None


def test_un_fatto_nuovo_cambia_il_dovuto_e_il_conguaglio_per_differenza_lo_regola(registro, fisco, orologio):
    """Dodici ritenute senza detrazione: 12 * 216,67 = 2600,04. Conguaglio di dicembre: 2600,00 - 2600,04 = -0,04.
    La dichiarazione arriva dopo: il dovuto scende a 1940,00 e la differenza è 1940,00 - 2600,00 = -660,00."""
    _anno_chiuso_senza_detrazione(registro, orologio, fisco)
    chiuso = registro.esiti(TipoEsito.PAGATO, registro.adesso())
    dichiara(registro, orologio, quando=date(2027, 2, 5))
    differenza = conguaglio_per_differenza(registro, fisco, R, 2026, date(2027, 2, 26))
    assert differenza.valore == Decimal("-660.00")
    assert (differenza.anno_imposta, differenza.istituto) == (2026, "conguaglio_irpef")
    assert [fatto.tipo for fatto in differenza.derivazione.fatti] == ["dichiarazione_sostituito"]
    assert registro.esiti(TipoEsito.PAGATO, registro.adesso()) == chiuso


def test_il_conguaglio_per_differenza_si_fissa_in_un_pagamento_e_poi_non_ce_ne_e_un_altro(registro, fisco, orologio):
    _anno_chiuso_senza_detrazione(registro, orologio, fisco)
    dichiara(registro, orologio, quando=date(2027, 2, 5))
    orologio.vai(2, 26, 2027)
    differenza = conguaglio_per_differenza(registro, fisco, R, 2026, date(2027, 2, 26))
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2027, 2, 26), [differenza])
    registro.registra_pagamento(R, esito.id, date(2027, 2, 26))
    assert conguaglio_per_differenza(registro, fisco, R, 2026, date(2027, 2, 27)) is None


def test_dopo_il_28_febbraio_il_conguaglio_per_differenza_chiede_la_cessazione(registro, fisco, orologio):
    _anno_chiuso_senza_detrazione(registro, orologio, fisco)
    dichiara(registro, orologio, quando=date(2027, 3, 1))
    with pytest.raises(CasoNonModellato, match="28 febbraio"):
        conguaglio_per_differenza(registro, fisco, R, 2026, date(2027, 3, 5))


def test_il_conguaglio_per_differenza_puo_stare_nello_stesso_pagamento_di_uno_stipendio_dell_anno_dopo(
    registro, fisco, orologio
):
    _anno_chiuso_senza_detrazione(registro, orologio, fisco)
    dichiara(registro, orologio, quando=date(2027, 2, 5))
    orologio.vai(2, 20, 2027)
    righe = stipendio(registro, fisco, Mese(2027, 2))
    attribuite = attribuisci_reddito(fisco, righe, date(2027, 2, 26))
    fiscale = calcola_fiscale(registro, fisco, R, attribuite, date(2027, 2, 26))
    differenza = conguaglio_per_differenza(registro, fisco, R, 2026, date(2027, 2, 26))
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2027, 2, 26), [*attribuite, fiscale.ritenuta, differenza])
    assert {riga.anno_imposta for riga in esito.righe if riga.istituto != "stipendio"} == {2026, 2027}
    assert fiscale.ritenuta.anno_imposta == 2027


# Proiezione del conguaglio come avviso

def test_la_proiezione_del_conguaglio_e_un_avviso_che_non_cambia_la_ritenuta(registro, fisco, orologio):
    """Dopo tre pagamenti (reddito 4500): imposta 450, detrazione 1065, dovuto 0; ritenute operate 3 * 161,67."""
    assumi(registro)
    dichiara(registro, orologio)
    anno_di_paghe(registro, orologio, fisco, fino_a=2)
    orologio.vai(3, 1)
    righe = attribuisci_reddito(fisco, stipendio(registro, fisco, Mese(2026, 3)), date(2026, 3, 27))
    fiscale = calcola_fiscale(registro, fisco, R, righe, date(2026, 3, 27))
    (avviso,) = fiscale.avvisi_di("proiezione_conguaglio")
    assert (avviso.persona, avviso.anno, avviso.valore) == (P, 2026, Decimal("-485.01"))
    assert fiscale.ritenuta.valore == Decimal("161.67")
    assert fiscale.conguaglio is None


def test_la_proiezione_sa_anche_stare_da_sola(registro, fisco, orologio):
    assumi(registro)
    dichiara(registro, orologio)
    anno_di_paghe(registro, orologio, fisco, fino_a=3)
    avviso = proiezione_conguaglio(registro, fisco, P, 2026, date(2026, 3, 27))
    assert avviso.valore == Decimal("-485.01")


# Il resto del modello non cambia

def test_la_denuncia_non_conta_ritenuta_e_conguaglio_nelle_basi(registro, fisco, orologio):
    assumi(registro)
    dichiara(registro, orologio)
    esiti = anno_di_paghe(registro, orologio, fisco)
    denuncia = calcola_denuncia(registro, fisco, R, Mese(2026, 12))
    (periodo,) = denuncia.periodi
    assert periodo.base("pens").valore == Decimal("1500")
    assert esiti[-1][1].conguaglio is not None


def test_le_differenze_per_competenza_non_vedono_ritenuta_e_conguaglio(registro, fisco, orologio):
    assumi(registro)
    anno_di_paghe(registro, orologio, fisco)
    assert differenze(registro, fisco, R, Mese(2026, 12), TipoEsito.PAGATO) == ()


def test_l_esito_conserva_anno_e_categoria_dopo_la_lettura(registro, fisco, orologio):
    assumi(registro)
    esiti = anno_di_paghe(registro, orologio, fisco, fino_a=1)
    letto = registro.esito(esiti[0][0].id)
    assert letto.righe == esiti[0][0].righe
    assert {riga.anno_imposta for riga in letto.righe} == {2026}


# Il corpus dichiara le regole fiscali con fonte

def test_il_corpus_senza_fiscale_resta_valido():
    assert Corpus.da_toml(_parametri() + REGOLE).versione


def test_la_versione_del_corpus_cambia_con_la_regola_fiscale():
    altro = TESTO.replace('versione = 1\ndal = 2020-01-01\nriferimento = "fittizio:ritenuta"',
                          'versione = 2\ndal = 2020-01-01\nriferimento = "fittizio:ritenuta"')
    assert Corpus.da_toml(altro).versione != Corpus.da_toml(TESTO).versione


@pytest.mark.parametrize(
    "da, a, messaggio",
    [
        ('categoria = "lavoro_dipendente"\ndal = 2020-01-01\nriferimento = "fittizio:reddito-stipendio"',
         'categoria = "ignota"\ndal = 2020-01-01\nriferimento = "fittizio:reddito-stipendio"', "categoria"),
        ('istituto = "stipendio"\ncategoria', 'istituto = "senza_regola"\ncategoria', "regola"),
        ('categorie = ["lavoro_dipendente"]', 'categorie = ["ignota"]', "categoria"),
        ("parametro.aliquota_1 *", "parametro.inventata *", "parametri ignoti"),
        ("parametro.aliquota_1 *", "fatto.inventato *", "fatti"),
        ("fisco.imponibile, parametro.limite_1", "fisco.inventato, parametro.limite_1", "fisco"),
        ('riferimento = "fittizio:ritenuta"', 'riferimento = ""', "riferimento"),
        ('riferimento = "fittizio:cassa-lavoro"', 'riferimento = ""', "riferimento"),
        ('riferimento = "fittizio:conguaglio"', 'riferimento = ""', "riferimento"),
    ],
)
def test_il_corpus_rifiuta_dichiarazioni_fiscali_incomplete(da, a, messaggio):
    assert da in TESTO
    with pytest.raises(ErroreCorpus, match=messaggio):
        Corpus.da_toml(TESTO.replace(da, a, 1))


def test_una_regola_normale_non_legge_il_fisco():
    testo = REGOLE.replace('formula = "fatto.mensile"', 'formula = "fisco.imponibile"') + _parametri()
    with pytest.raises(ErroreCorpus, match="fisco"):
        Corpus.da_toml(testo)


def test_il_corpus_reale_rifiuta_i_riferimenti_fittizi_anche_nel_fiscale():
    with pytest.raises(ErroreCorpus, match="fittizio"):
        Corpus.da_toml(TESTO, reale=True)


def test_due_categorie_con_lo_stesso_nome_sono_rifiutate():
    doppio = TESTO + '\n[[categoria_reddito]]\nnome = "carica_elettiva"\n' + (
        '[[categoria_reddito.cassa_allargata]]\ndal = 2020-01-01\nvale = true\nriferimento = "fittizio:x"\n')
    with pytest.raises(ErroreCorpus, match="stesso nome"):
        Corpus.da_toml(doppio)


# Pagamento fisiologico (ticket #61, CONTEXT.md, ADR 0018)

FISIOLOGICO = """
[[pagamento_fisiologico]]
istituto = "stipendio"
dal = 2020-01-01
riferimento = "fittizio:fisiologico-stipendio"
"""


def test_l_istituto_dichiara_il_pagamento_fisiologico_con_date_e_riferimento():
    corpus = Corpus.da_toml(TESTO + FISIOLOGICO.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-12-31"))
    dichiarazione = corpus.pagamento_fisiologico("stipendio", date(2026, 6, 1))
    assert (dichiarazione.istituto, dichiarazione.riferimento) == ("stipendio", "fittizio:fisiologico-stipendio")
    assert corpus.pagamento_fisiologico("stipendio", date(2027, 1, 13)) is None
    assert corpus.pagamento_fisiologico("gettone", date(2026, 6, 1)) is None


def test_il_pagamento_fisiologico_di_un_istituto_ignoto_e_rifiutato():
    with pytest.raises(ErroreCorpus, match="istituto ignoto"):
        Corpus.da_toml(TESTO + FISIOLOGICO.replace('"stipendio"', '"premio_inesistente"'))


def test_due_dichiarazioni_fisiologiche_dello_stesso_istituto_non_si_sovrappongono():
    seconda = FISIOLOGICO.replace("2020-01-01", "2026-01-01").replace("fisiologico-stipendio", "fisiologico-bis")
    with pytest.raises(ErroreCorpus, match="sovrappost"):
        Corpus.da_toml(TESTO + FISIOLOGICO.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-06-30") + seconda)
    adiacenti = FISIOLOGICO.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2025-12-31") + seconda
    assert Corpus.da_toml(TESTO + adiacenti).pagamento_fisiologico("stipendio", date(2026, 1, 1)).riferimento == "fittizio:fisiologico-bis"


def test_il_pagamento_fisiologico_senza_riferimento_e_rifiutato():
    senza = FISIOLOGICO.replace('riferimento = "fittizio:fisiologico-stipendio"', 'riferimento = ""')
    with pytest.raises(ErroreCorpus, match="riferimento normativo obbligatorio"):
        Corpus.da_toml(TESTO + senza)


def test_il_corpus_reale_rifiuta_il_riferimento_fittizio_del_pagamento_fisiologico():
    """Anche con tutto il resto reale: l'unico riferimento fittizio è quello della dichiarazione."""
    reale = Corpus.carica(CORPUS_REALE, reale=True)
    assert reale.versione
    testo = CORPUS_REALE.read_text(encoding="utf-8") + FISIOLOGICO.replace('"stipendio"', f'"{reale.istituti()[0]}"')
    with pytest.raises(ErroreCorpus, match="Pagamento fisiologico.*fittizio"):
        Corpus.da_toml(testo, reale=True)


def test_la_versione_del_corpus_cambia_con_la_dichiarazione_fisiologica():
    senza = Corpus.da_toml(TESTO)
    con = Corpus.da_toml(TESTO + FISIOLOGICO)
    altra = Corpus.da_toml(TESTO + FISIOLOGICO.replace("fisiologico-stipendio", "fisiologico-altro"))
    assert len({senza.versione, con.versione, altra.versione}) == 3


def test_la_versione_dei_corpus_senza_dichiarazione_fisiologica_non_cambia():
    """Valori letti prima della modifica: l'impronta tiene conto della dichiarazione solo se c'è."""
    assert Corpus.da_toml(TESTO).versione == "e41b25349377cf4c"
    assert Corpus.carica(CORPUS_REALE, reale=True).versione == "aa2acea7b7a9dfdf"


@pytest.fixture
def fisiologico():
    return Corpus.da_toml(TESTO + FISIOLOGICO)


def test_il_pagamento_fisiologico_dell_anno_prima_e_attribuito_all_anno_d_imposta_del_pagamento(registro, fisiologico):
    assumi(registro)
    righe = stipendio(registro, fisiologico, Mese(2026, 12))
    (riga,) = attribuisci_reddito(fisiologico, righe, date(2027, 1, 13))
    assert (riga.categoria_reddito, riga.anno_imposta) == ("lavoro_dipendente", 2027)
    assert riga.periodo == Periodo(date(2026, 12, 1), date(2026, 12, 31))


def test_senza_dichiarazione_dell_istituto_il_fermo_nomina_il_caso(registro, fisco):
    assumi(registro)
    righe = stipendio(registro, fisco, Mese(2026, 12))
    with pytest.raises(CasoNonModellato, match="non dichiara il pagamento fisiologico") as errore:
        attribuisci_reddito(fisco, righe, date(2027, 1, 13))
    assert "causa del pagamento tardivo" in str(errore.value)


def test_una_dichiarazione_scaduta_prima_della_data_di_pagamento_non_vale(registro):
    corpus = Corpus.da_toml(TESTO + FISIOLOGICO.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2027-01-12"))
    assumi(registro)
    righe = stipendio(registro, corpus, Mese(2026, 12))
    with pytest.raises(CasoNonModellato, match="non dichiara il pagamento fisiologico"):
        attribuisci_reddito(corpus, righe, date(2027, 1, 13))
    (riga,) = attribuisci_reddito(corpus, righe, date(2027, 1, 12))
    assert riga.anno_imposta == 2026  # dentro la cassa allargata: già dell'anno di competenza


def test_una_competenza_di_due_anni_prima_ferma_anche_con_la_dichiarazione(registro, fisiologico):
    assumi(registro)
    righe = stipendio(registro, fisiologico, Mese(2025, 12))
    with pytest.raises(CasoNonModellato, match="due o più anni prima"):
        attribuisci_reddito(fisiologico, righe, date(2027, 1, 13))


def test_una_competenza_a_cavallo_di_due_anni_ferma_anche_con_la_dichiarazione(registro, fisiologico):
    assumi(registro)
    (riga,) = stipendio(registro, fisiologico, Mese(2026, 12))
    cavallo = replace(riga, periodo=Periodo(date(2026, 12, 15), date(2027, 1, 14)))
    with pytest.raises(CasoNonModellato, match="a cavallo di due anni"):
        attribuisci_reddito(fisiologico, [cavallo], date(2027, 1, 20))


def test_il_pagamento_fisiologico_entra_nell_imponibile_nella_ritenuta_e_nel_conguaglio_dell_anno_del_pagamento(
    registro, orologio, fisiologico
):
    """Stipendio di dicembre 2026 di 1500 pagato il 13/01/2027: è reddito 2027, non 2026."""
    assumi(registro)
    righe = stipendio(registro, fisiologico, Mese(2026, 12))
    esito, fiscale = paga(registro, orologio, fisiologico, righe, date(2027, 1, 13), ultimo=True)
    assert imponibile_fiscale(registro, P, 2027).valore == Decimal("1500")
    assert imponibile_fiscale(registro, P, 2026).valore == Decimal(0)
    assert fiscale.ritenuta.valore == Decimal("216.67")  # 0,10 * 833,33 + 0,20 * (1500 - 833,33)
    assert fiscale.ritenuta.anno_imposta == 2027
    assert fiscale.conguaglio.valore == Decimal("-66.67")  # imposta annua 0,10 * 1500 = 150, meno 216,67 operati
    assert fiscale.conguaglio.anno_imposta == 2027


def test_la_performance_di_dicembre_pagata_il_10_gennaio_con_la_cassa_allargata_e_gia_dell_anno_di_competenza(
    registro, fisco, fisiologico
):
    """Non serve nessuna dichiarazione: l'anno d'imposta è il 2026, quello della competenza."""
    assumi(registro)
    for corpus in (fisco, fisiologico):
        righe = stipendio(registro, corpus, Mese(2026, 12))
        (riga,) = attribuisci_reddito(corpus, righe, date(2027, 1, 10))
        assert riga.anno_imposta == 2026


def test_una_competenza_posteriore_all_anno_d_imposta_ferma_il_calcolo(registro, fisiologico):
    assumi(registro)
    righe = stipendio(registro, fisiologico, Mese(2027, 1))
    with pytest.raises(CasoNonModellato, match="posteriore all'anno d'imposta"):
        attribuisci_reddito(fisiologico, righe, date(2026, 12, 20))
