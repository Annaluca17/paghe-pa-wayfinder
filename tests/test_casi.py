"""Corpus reale, regole sul mese, fermi e casi di recupero (ticket #29, parte 2).

Meccanismi del motore provati con un corpus fittizio: valori e fonti non sono norme.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, Periodo, TipoEsito, calcola, calcola_denuncia, differenze, emetti_esito
from paghe.errori import CasoNonModellato, ErroreCalcolo, ErroreCorpus, FattoMancante, ParametroMancante
from paghe.riferimento import motivo_rifiuto

R = "RAPPORTO-1"
ALTRO = "RAPPORTO-2"
CF = "RSSMRA80A01H501U"

PARAMETRI = """
[[parametro]]
nome = "aliquota"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "0.10"
riferimento = "fittizio:aliquota"

[[parametro]]
nome = "soglia"
[[parametro.vigenza]]
dal = 2026-01-01
al = 2026-12-31
valore = "1500"
riferimento = "fittizio:soglia-2026"

[[parametro]]
nome = "aliquota_aggiuntiva"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "0.01"
riferimento = "fittizio:aggiuntiva"

[[parametro]]
nome = "massimale"
[[parametro.vigenza]]
dal = 2026-01-01
al = 2026-12-31
valore = "4500"
riferimento = "fittizio:massimale-2026"

[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "26"
riferimento = "fittizio:d"

[[parametro]]
nome = "mensile_alto"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "1200"
riferimento = "fittizio:tabella-alto"

[[parametro]]
nome = "mensile_basso"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "1000"
riferimento = "fittizio:tabella-basso"
"""

REGOLE = """
[periodo_dichiarato]
servizio = "tipo_impiego"
cessazione = "cessazione"
sospensione = "sospensione"
fatti = ["qualifica"]

[denuncia]
persona = "codice_fiscale"
massimale = { base = "pens", parametro = "massimale" }
conguaglio_annuo = ["aggiuntivo"]

[[fermo]]
fatto = "regime_fine_servizio"
caso = "contribuzione TFS e TFR"
ambito = "denuncia"
riferimento = "fittizio:fermo-tfs"

[[fermo]]
fatto = "part_time"
caso = "part-time"
ambito = "calcolo"
riferimento = "fittizio:fermo-part-time"

[[base]]
nome = "pens"
riferimento = "fittizio:base-pens"

[[regola]]
istituto = "stipendio_alto"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio-alto"
formula = "parametro.mensile_alto"
maturazione = "giorni"
applica_se = "area=alta"
conteggio = "lun_sab"
divisore = "d"
decimali = 2

[[regola]]
istituto = "stipendio_basso"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio-basso"
formula = "parametro.mensile_basso"
maturazione = "giorni"
applica_se = "area=bassa"
conteggio = "lun_sab"
divisore = "d"
decimali = 2

[[regola]]
istituto = "una_tantum"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:una-tantum"
formula = "fatto.una_tantum"
maturazione = "evento"
applica_se = "una_tantum"

[[regola]]
istituto = "contributo"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:contributo"
formula = "arrotonda(base.pens * parametro.aliquota, 2)"
maturazione = "periodo"

[[regola]]
istituto = "aggiuntivo"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:aggiuntivo"
formula = "arrotonda(max(base.pens - parametro.soglia, 0) * parametro.aliquota_aggiuntiva, 2)"
maturazione = "mese"

[[concorso]]
istituto = "stipendio_alto"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-alto"

[[concorso]]
istituto = "stipendio_basso"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-basso"

[[concorso]]
istituto = "una_tantum"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-una-tantum"
"""

TESTO = PARAMETRI + REGOLE


@pytest.fixture
def casi():
    return Corpus.da_toml(TESTO)


def assumi(registro, rapporto=R, dal=date(2026, 1, 1), al=None, area="bassa", cf=CF, persona="PERSONA-1"):
    registro.registra_codice_persona(persona, "codice_fiscale", cf, date(1980, 1, 1))
    registro.collega_rapporto(rapporto, persona, dal)
    registro.registra_codice(rapporto, "tipo_impiego", "1", dal, al)
    registro.registra_codice(rapporto, "area", area, dal, al)


def stipendi(registro, corpus, *mesi, rapporto=R):
    return [riga for mese in mesi for riga in calcola(registro, corpus, rapporto, mese)]


def paga(registro, orologio, righe, giorno, rapporto=R):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(rapporto, esito.id, giorno)
    orologio.avanza()
    return esito


def cessa(registro, giorno, rapporto=R):
    """Cessazione: valida dal giorno dopo l'ultimo giorno di servizio (ticket #43)."""
    registro.registra_codice(rapporto, "cessazione", "1", giorno)


def sospendi(registro, giorno, rapporto=R):
    """Sospensione: valida dal giorno dopo l'ultimo giorno di servizio (ticket #43)."""
    registro.registra_codice(rapporto, "sospensione", "1", giorno)


def contributi(periodo):
    return {riga.istituto: riga.valore for riga in periodo.contributi}


# Rifiuto dei riferimenti fittizi nel corpus reale (ADR 0003)

def test_il_corpus_reale_rifiuta_i_riferimenti_fittizi():
    with pytest.raises(ErroreCorpus, match="fittizio"):
        Corpus.da_toml(TESTO, reale=True)


def test_il_corpus_fittizio_resta_ammesso_fuori_dal_corpus_reale(casi):
    assert not casi.reale


@pytest.mark.parametrize(
    "riferimento",
    [
        "prassi:inpdap:nota.operativa:2007-01-23;2",
        "urn:nir:stato:decreto.legge:1992-09-19;384~art3ter",
        "prassi:inps:circolare:2014-01-16;6~par19",
    ],
)
def test_riferimenti_delle_fonti_cpdel_ammessi(riferimento):
    assert motivo_rifiuto(riferimento) is None


# Parametri con fine vigenza e regole condizionate da un codice

def test_un_parametro_con_fine_vigenza_non_vale_oltre(registro, casi, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 12)), date(2027, 1, 12))
    with pytest.raises(ParametroMancante, match="soglia"):
        calcola_denuncia(registro, casi, R, Mese(2027, 1))


def test_la_fine_vigenza_e_ammessa_solo_sull_ultima_vigenza():
    testo = PARAMETRI.replace(
        'riferimento = "fittizio:soglia-2026"\n',
        'riferimento = "fittizio:soglia-2026"\n[[parametro.vigenza]]\ndal = 2027-01-01\nvalore = "1600"\n'
        'riferimento = "fittizio:soglia-2027"\n',
    )
    with pytest.raises(ErroreCorpus, match="soglia"):
        Corpus.da_toml(testo + REGOLE)


def test_la_regola_si_applica_solo_al_codice_indicato(registro, casi):
    assumi(registro, area="alta")
    assert {riga.istituto: riga.valore for riga in calcola(registro, casi, R, Mese(2026, 11))} == {
        "stipendio_alto": Decimal("1200.00")
    }


def test_il_cambio_di_codice_divide_il_mese_tra_le_regole(registro, casi):
    assumi(registro, area="alta", al=date(2026, 11, 15))
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 11, 16))
    registro.registra_codice(R, "area", "bassa", date(2026, 11, 16))
    righe = {riga.istituto: riga for riga in calcola(registro, casi, R, Mese(2026, 11))}
    assert righe["stipendio_alto"].periodo == Periodo(date(2026, 11, 1), date(2026, 11, 15))
    assert righe["stipendio_alto"].valore == Decimal("553.85")  # 1200 x 12/26
    assert righe["stipendio_basso"].periodo == Periodo(date(2026, 11, 16), date(2026, 11, 30))


def test_condizione_su_un_fatto_numerico_rifiutata(registro, casi):
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 1, 1))
    registro.registra_fatto(R, "area", "1", date(2026, 1, 1))
    with pytest.raises(ErroreCalcolo, match="area"):
        calcola(registro, casi, R, Mese(2026, 11))


# Regola sul mese: totale del mese, esposta sull'ultimo periodo (nota di prassi 2)

def test_la_regola_sul_mese_legge_il_totale_e_sta_sull_ultimo_periodo(registro, casi, orologio):
    assumi(registro)
    registro.registra_codice(R, "qualifica", "A", date(2026, 1, 1), date(2026, 11, 15))
    registro.registra_codice(R, "qualifica", "B", date(2026, 11, 16))
    righe = stipendi(registro, casi, Mese(2026, 9), Mese(2026, 10), Mese(2026, 11))
    paga(registro, orologio, righe, date(2026, 11, 27))

    primo, ultimo = calcola_denuncia(registro, casi, R, Mese(2026, 11)).periodi
    assert "aggiuntivo" not in contributi(primo)
    aggiuntivo = next(riga for riga in ultimo.contributi if riga.istituto == "aggiuntivo")
    assert aggiuntivo.valore == Decimal("15.00")  # (3.000 - 1.500) x 1%
    assert aggiuntivo.periodo == ultimo.periodo
    letta, = aggiuntivo.derivazione.importi
    assert letta.valore == Decimal("3000.00")
    assert letta.periodo == Mese(2026, 11).periodo


def test_sotto_soglia_la_regola_sul_mese_vale_zero(registro, casi, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, casi, R, Mese(2026, 11)).periodi
    assert contributi(periodo) == {"contributo": Decimal("100.00"), "aggiuntivo": Decimal("0.00")}


def test_la_regola_sul_mese_deve_leggere_una_base():
    testo = TESTO.replace(
        'formula = "arrotonda(max(base.pens - parametro.soglia, 0) * parametro.aliquota_aggiuntiva, 2)"',
        'formula = "parametro.soglia"',
    )
    with pytest.raises(ErroreCorpus, match="aggiuntivo"):
        Corpus.da_toml(testo)


def test_una_regola_sul_periodo_non_legge_una_regola_sul_mese():
    testo = TESTO + """
[[regola]]
istituto = "derivato"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:derivato"
formula = "importo.aggiuntivo * 2"
maturazione = "periodo"
"""
    with pytest.raises(ErroreCorpus, match="derivato"):
        Corpus.da_toml(testo)


# Fermi dichiarati nel corpus

def test_un_fermo_della_denuncia_lascia_il_calcolo_e_ferma_la_denuncia(registro, casi, orologio):
    assumi(registro)
    registro.registra_codice(R, "regime_fine_servizio", "X", date(2026, 1, 1))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    with pytest.raises(CasoNonModellato, match="contribuzione TFS e TFR"):
        calcola_denuncia(registro, casi, R, Mese(2026, 11))


def test_un_fermo_del_calcolo_ferma_anche_il_calcolo(registro, casi):
    assumi(registro)
    registro.registra_fatto(R, "part_time", "50", date(2026, 11, 10))
    assert calcola(registro, casi, R, Mese(2026, 10))
    with pytest.raises(CasoNonModellato, match="part-time"):
        calcola(registro, casi, R, Mese(2026, 11))


def test_fermo_con_ambito_ignoto_rifiutato():
    with pytest.raises(ErroreCorpus, match="ambito"):
        Corpus.da_toml(TESTO.replace('ambito = "calcolo"', 'ambito = "sempre"'))


# Persona, più rapporti, massimale e conguaglio (ADR 0005)

def test_senza_codice_fiscale_la_denuncia_si_ferma(registro, casi, orologio):
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 1, 1))
    registro.registra_codice(R, "area", "bassa", date(2026, 1, 1))
    registro.collega_rapporto(R, "PERSONA-1", date(2026, 1, 1))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    with pytest.raises(FattoMancante, match="codice_fiscale"):
        calcola_denuncia(registro, casi, R, Mese(2026, 11))


def test_piu_rapporti_della_stessa_persona_nello_stesso_anno_fermano_la_denuncia(registro, casi, orologio):
    assumi(registro)
    assumi(registro, rapporto=ALTRO, dal=date(2026, 3, 1), al=date(2026, 4, 30))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    with pytest.raises(CasoNonModellato, match="più rapporti"):
        calcola_denuncia(registro, casi, R, Mese(2026, 11))


def test_un_rapporto_di_un_altro_anno_non_ferma(registro, casi, orologio):
    assumi(registro)
    assumi(registro, rapporto=ALTRO, dal=date(2025, 3, 1), al=date(2025, 4, 30))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    assert calcola_denuncia(registro, casi, R, Mese(2026, 11)).periodi


def test_un_altra_persona_non_ferma(registro, casi, orologio):
    assumi(registro)
    assumi(registro, rapporto=ALTRO, cf="BNCLRA85M41F205C", persona="PERSONA-2")
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    assert calcola_denuncia(registro, casi, R, Mese(2026, 11)).periodi


def test_senza_legame_con_la_persona_la_denuncia_si_ferma(registro, casi, orologio):
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 1, 1))
    registro.registra_codice(R, "area", "bassa", date(2026, 1, 1))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    with pytest.raises(FattoMancante, match="persona"):
        calcola_denuncia(registro, casi, R, Mese(2026, 11))


def test_il_superamento_del_massimale_nell_anno_ferma_la_denuncia(registro, casi, orologio):
    assumi(registro)
    for mese in range(1, 5):
        paga(registro, orologio, stipendi(registro, casi, Mese(2026, mese)), date(2026, mese, 27))
    assert calcola_denuncia(registro, casi, R, Mese(2026, 4)).periodi
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 5)), date(2026, 5, 27))
    with pytest.raises(CasoNonModellato, match="massimale"):
        calcola_denuncia(registro, casi, R, Mese(2026, 5))


def test_conguaglio_annuo_a_dicembre_se_nell_anno_la_regola_sul_mese_e_scattata(registro, casi, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 9), Mese(2026, 10)), date(2026, 10, 27))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 12)), date(2026, 12, 18))
    with pytest.raises(CasoNonModellato, match="conguaglio"):
        calcola_denuncia(registro, casi, R, Mese(2026, 12))


def test_a_dicembre_senza_regola_sul_mese_scattata_nessun_conguaglio(registro, casi, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 12)), date(2026, 12, 18))
    assert calcola_denuncia(registro, casi, R, Mese(2026, 12)).periodi


def test_conguaglio_annuo_anche_nel_mese_di_cessazione(registro, casi, orologio):
    assumi(registro, al=date(2026, 6, 15))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 3), Mese(2026, 4)), date(2026, 4, 27))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 6)), date(2026, 6, 26))
    with pytest.raises(CasoNonModellato, match="conguaglio"):
        calcola_denuncia(registro, casi, R, Mese(2026, 6))


# Recuperi (ADR 0005, nota di prassi 2)

def test_recupero_in_servizio_detratto_dalla_denuncia_del_mese(registro, casi, orologio):
    assumi(registro)
    registro.registra_fatto(R, "una_tantum", "300", date(2026, 10, 5), date(2026, 10, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 10)), date(2026, 10, 27))
    orologio.vai(11, 2)
    registro.registra_fatto(R, "una_tantum", "100", date(2026, 10, 5), date(2026, 10, 5))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 10), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero + stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))

    periodo, = calcola_denuncia(registro, casi, R, Mese(2026, 11)).periodi
    assert periodo.base("pens").valore == Decimal("800.00")
    assert contributi(periodo)["contributo"] == Decimal("80.00")
    caso, = periodo.recuperi
    assert caso.caso == "in servizio"
    assert caso.importo.valore == Decimal("-200")


def test_recupero_su_cessato_in_un_periodo_fuori_servizio(registro, casi, orologio):
    assumi(registro, al=date(2026, 9, 30))
    cessa(registro, date(2026, 10, 1))
    registro.registra_fatto(R, "una_tantum", "300", date(2026, 9, 5), date(2026, 9, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 9)), date(2026, 9, 25))
    orologio.vai(11, 2)
    registro.registra_fatto(R, "una_tantum", "100", date(2026, 9, 5), date(2026, 9, 5))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 9), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 11, 20))

    periodo, = calcola_denuncia(registro, casi, R, Mese(2026, 11)).periodi
    assert not periodo.in_servizio
    assert periodo.base("pens").valore == Decimal("-200")
    assert contributi(periodo)["contributo"] == Decimal("-20.00")
    caso, = periodo.recuperi
    assert caso.caso == "su cessato"


def test_recupero_dopo_la_fine_del_servizio_senza_cessazione_ne_sospensione_ferma_e_nomina_il_caso(registro, casi, orologio):
    assumi(registro, al=date(2026, 9, 30))
    registro.registra_fatto(R, "una_tantum", "300", date(2026, 9, 5), date(2026, 9, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 9)), date(2026, 9, 25))
    orologio.vai(11, 2)
    registro.registra_fatto(R, "una_tantum", "100", date(2026, 9, 5), date(2026, 9, 5))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 9), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 11, 20))
    with pytest.raises(CasoNonModellato, match="finisce il 2026-09-30 senza cessazione né sospensione"):
        calcola_denuncia(registro, casi, R, Mese(2026, 11))


def test_il_recupero_ha_la_data_del_pagamento_in_cui_la_trattenuta_e_operata(registro, casi, orologio):
    assumi(registro)
    registro.registra_fatto(R, "una_tantum", "300", date(2026, 10, 5), date(2026, 10, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 10)), date(2026, 10, 27))
    orologio.vai(11, 2)
    registro.registra_fatto(R, "una_tantum", "100", date(2026, 10, 5), date(2026, 10, 5))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 10), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero + stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))

    caso, = calcola_denuncia(registro, casi, R, Mese(2026, 11)).periodi[0].recuperi
    assert caso.importo.data_pagamento == date(2026, 11, 27)
    assert caso.importo.periodo.dal == date(2026, 10, 5)  # la competenza resta quella d'origine
    assert calcola_denuncia(registro, casi, R, Mese(2026, 10)).periodi[0].base("pens").valore == Decimal("1300.00")


def recupero_oltre_capienza(registro, casi, orologio):
    """Ottobre pagato 300 di una tantum, poi azzerato: a novembre si recupera -300 senza stipendio da cui detrarlo."""
    assumi(registro)
    registro.registra_fatto(R, "una_tantum", "300", date(2026, 10, 5), date(2026, 10, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 10)), date(2026, 10, 27))
    orologio.vai(11, 2)
    registro.registra_fatto(R, "una_tantum", "0", date(2026, 10, 5), date(2026, 10, 5))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 10), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 11, 10))


def test_recupero_oltre_capienza_in_servizio_ferma_la_base_a_zero_e_mostra_il_residuo(registro, casi, orologio):
    recupero_oltre_capienza(registro, casi, orologio)
    denuncia = calcola_denuncia(registro, casi, R, Mese(2026, 11))
    periodo, = denuncia.periodi
    assert periodo.base("pens").valore == Decimal("0")
    assert contributi(periodo)["contributo"] == Decimal("0.00")
    residuo, = denuncia.riporti
    assert residuo.istituto == "riporto.pens"
    assert residuo.valore == Decimal("-300")


def test_il_residuo_si_detrae_dal_mese_dopo_con_la_derivazione_fino_al_recupero_d_origine(registro, casi, orologio):
    recupero_oltre_capienza(registro, casi, orologio)
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 12)), date(2026, 12, 18))
    denuncia = calcola_denuncia(registro, casi, R, Mese(2026, 12))
    periodo, = denuncia.periodi
    assert periodo.base("pens").valore == Decimal("700.00")
    assert denuncia.riporti == ()
    detratto, = [riga for riga in periodo.base("pens").derivazione.importi if riga.istituto == "riporto.pens"]
    assert detratto.valore == Decimal("-300")
    entrante, = detratto.derivazione.importi
    origine, = entrante.derivazione.importi
    assert (origine.istituto, origine.valore, origine.data_pagamento) == ("una_tantum", Decimal("-300"), date(2026, 11, 10))


def test_il_residuo_che_non_entra_nemmeno_nel_mese_dopo_continua(registro, casi, orologio):
    assumi(registro)
    registro.registra_fatto(R, "una_tantum", "1500", date(2026, 8, 5), date(2026, 8, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 8)), date(2026, 8, 27))
    orologio.vai(9, 2)
    registro.registra_fatto(R, "una_tantum", "0", date(2026, 8, 5), date(2026, 8, 5))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 8), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 9, 10))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 10)), date(2026, 10, 27))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))

    ottobre = calcola_denuncia(registro, casi, R, Mese(2026, 10))
    assert ottobre.periodi[0].base("pens").valore == Decimal("0")
    residuo, = ottobre.riporti
    assert residuo.valore == Decimal("-500.00")
    novembre = calcola_denuncia(registro, casi, R, Mese(2026, 11))
    assert novembre.periodi[0].base("pens").valore == Decimal("500.00")
    assert novembre.riporti == ()


def sospeso_con_recupero(registro, casi, orologio):
    """Servizio fino al 30/09, sospensione dal 01/10; a novembre da sospeso si recupera -200 sul pagato di settembre."""
    assumi(registro, al=date(2026, 9, 30))
    sospendi(registro, date(2026, 10, 1))
    registro.registra_fatto(R, "una_tantum", "300", date(2026, 9, 5), date(2026, 9, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 9)), date(2026, 9, 25))
    orologio.vai(11, 2)
    registro.registra_fatto(R, "una_tantum", "100", date(2026, 9, 5), date(2026, 9, 5))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 9), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 11, 20))


def rientra(registro, giorno, al=None):
    """Il rientro e' un nuovo fatto di servizio."""
    registro.registra_codice(R, "tipo_impiego", "1", giorno, al)
    registro.registra_codice(R, "area", "bassa", giorno, al)


def test_recupero_pagato_da_sospeso_non_entra_nella_denuncia_e_aspetta_il_rientro(registro, casi, orologio):
    sospeso_con_recupero(registro, casi, orologio)
    denuncia = calcola_denuncia(registro, casi, R, Mese(2026, 11))
    assert denuncia.periodi == ()
    residuo, = denuncia.riporti
    assert (residuo.istituto, residuo.valore) == ("riporto.pens", Decimal("-200"))


def test_recupero_da_sospeso_si_detrae_dal_primo_periodo_dopo_il_rientro(registro, casi, orologio):
    sospeso_con_recupero(registro, casi, orologio)
    rientra(registro, date(2026, 12, 1))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 12)), date(2026, 12, 18))
    denuncia = calcola_denuncia(registro, casi, R, Mese(2026, 12))
    periodo, = denuncia.periodi
    assert periodo.base("pens").valore == Decimal("800.00")
    assert denuncia.riporti == ()


def test_riporto_aperto_alla_sospensione_aspetta_il_rientro(registro, casi, orologio):
    assumi(registro, al=date(2026, 9, 30))
    registro.registra_fatto(R, "una_tantum", "300", date(2026, 9, 5), date(2026, 9, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 9)), date(2026, 9, 25))
    orologio.vai(10, 2)
    registro.registra_fatto(R, "una_tantum", "0", date(2026, 9, 5), date(2026, 9, 5))
    # Il recupero e' pagato da sospeso solo dopo: qui il servizio finisce con un riporto gia' aperto.
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 10, 1), date(2026, 10, 31))
    registro.registra_codice(R, "area", "bassa", date(2026, 10, 1), date(2026, 10, 31))
    sospendi(registro, date(2026, 11, 1))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 9), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 10, 10))
    ottobre = calcola_denuncia(registro, casi, R, Mese(2026, 10))
    assert ottobre.periodi[0].base("pens").valore == Decimal("0")
    assert ottobre.riporti[0].valore == Decimal("-300")
    rientra(registro, date(2026, 12, 1))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 12)), date(2026, 12, 18))
    assert calcola_denuncia(registro, casi, R, Mese(2026, 11)).riporti[0].valore == Decimal("-300")
    dicembre = calcola_denuncia(registro, casi, R, Mese(2026, 12))
    assert dicembre.periodi[0].base("pens").valore == Decimal("700.00")


def test_riporto_ancora_aperto_alla_cessazione_ferma_e_nomina_il_caso(registro, casi, orologio):
    assumi(registro, al=date(2026, 9, 30))
    cessa(registro, date(2026, 10, 1))
    registro.registra_fatto(R, "una_tantum", "300", date(2026, 8, 5), date(2026, 8, 5))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 8)), date(2026, 8, 27))
    orologio.vai(9, 2)
    registro.registra_fatto(R, "una_tantum", "0", date(2026, 8, 5), date(2026, 8, 5))
    recupero = [voce.importo() for voce in differenze(registro, casi, R, Mese(2026, 8), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 9, 10))
    with pytest.raises(CasoNonModellato, match="riporto del recupero ancora aperto alla cessazione.*riporto.pens"):
        calcola_denuncia(registro, casi, R, Mese(2026, 9))


def test_riporto_aperto_alla_cessazione_dopo_una_sospensione_ferma(registro, casi, orologio):
    sospeso_con_recupero(registro, casi, orologio)
    rientra(registro, date(2026, 12, 1), date(2026, 12, 31))
    cessa(registro, date(2027, 1, 1))
    with pytest.raises(CasoNonModellato, match="riporto del recupero ancora aperto alla cessazione"):
        calcola_denuncia(registro, casi, R, Mese(2026, 12))


def test_recupero_fuori_servizio_senza_servizio_precedente_ferma(registro, casi, orologio):
    assumi(registro, dal=date(2026, 12, 1))
    registro.registra_fatto(R, "una_tantum", "-50", date(2026, 12, 1), date(2026, 12, 1))
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 12)), date(2026, 11, 30))
    with pytest.raises(CasoNonModellato, match="senza servizio precedente"):
        calcola_denuncia(registro, casi, R, Mese(2026, 11))


def test_senza_recuperi_nessun_caso(registro, casi, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, casi, Mese(2026, 11)), date(2026, 11, 27))
    assert calcola_denuncia(registro, casi, R, Mese(2026, 11)).periodi[0].recuperi == ()
