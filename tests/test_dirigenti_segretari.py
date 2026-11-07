"""Regimi del titolo, PR A del ticket #73: dirigente e segretario (corpus reale).

Gli importi attesi sono ricalcolati a mano dalle fonti: tabellari del CCNL Area Funzioni Locali 23/02/2026 (art. 22 per
il dirigente, art. 35 c. 3 per il segretario), 13 mensilita'; posizione annua di fantasia (input da atto, nessuna norma).
Persone e rapporti sono di fantasia.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Atto, Corpus, Mese, TipoEsito, calcola, calcola_denuncia, emetti_esito
from paghe.errori import CasoNonModellato

CORPUS = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
R = "RAPPORTO-1"
CF = "RSSMRA80A01H501U"
ATTO = Atto("ente:ente_di_prova:determina:2026-01-09;1", date(2026, 1, 9))


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def titolare(registro, area, dal=date(2026, 1, 1), al=None):
    registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(R, "PERSONA-1", dal)
    registro.registra_codice(R, "tipo_impiego", "1", dal, al)
    registro.registra_codice(R, "area", area, dal, al)


def importi(registro, corpus, mese):
    return {riga.istituto: riga.valore for riga in calcola(registro, corpus, R, mese)}


def test_dirigente_a_tempo_pieno_ha_il_tabellare_mensile_su_13_mensilita(registro, reale):
    titolare(registro, "dirigente")
    assert importi(registro, reale, Mese(2026, 11))["tabellare_dirigenti"] == Decimal("3846.60")  # 50.005,77 / 13


def posizione_dirigente(registro, annua, dal=date(2026, 1, 1)):
    return registro.registra_fatto(R, "posizione_annua_dirigente", annua, dal, atto=ATTO)


def test_la_posizione_del_dirigente_e_l_annuo_deliberato_su_13_mensilita(registro, reale):
    titolare(registro, "dirigente")
    posizione_dirigente(registro, "20000.00")
    valori = importi(registro, reale, Mese(2026, 11))
    assert valori["tabellare_dirigenti"] == Decimal("3846.60")
    assert valori["posizione_dirigenti"] == Decimal("1538.46")  # 20.000 / 13


def test_senza_posizione_deliberata_il_dirigente_ha_solo_il_tabellare(registro, reale):
    titolare(registro, "dirigente")
    assert set(importi(registro, reale, Mese(2026, 11))) == {"tabellare_dirigenti"}


def paga(registro, orologio, righe, giorno):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(R, esito.id, giorno)
    orologio.avanza()
    return esito


def basi_e_contributi(registro, corpus, mese):
    periodo, = calcola_denuncia(registro, corpus, R, mese).periodi
    return {riga.istituto: riga.valore for riga in (*periodo.basi, *periodo.contributi)}


def test_cpdel_fondo_credito_e_tfr_del_dirigente_sono_sul_tabellare_e_sulla_posizione(registro, reale, orologio):
    titolare(registro, "dirigente")
    registro.registra_codice(R, "regime_fine_servizio", "1", date(2026, 1, 1))
    posizione_dirigente(registro, "20000.00")
    righe = calcola(registro, reale, R, Mese(2026, 11))
    assert {riga.istituto: riga.valore for riga in righe}["riduzione_tfr"] == Decimal("-107.70")  # 2,50% di 4.308,05
    paga(registro, orologio, righe, date(2026, 11, 27))
    valori = basi_e_contributi(registro, reale, Mese(2026, 11))
    assert valori["base.cpdel"] == valori["base.fondo_credito"] == valori["base.tfs"] == Decimal("5385.06")  # 3.846,60 + 1.538,46
    assert valori["cpdel_totale"] == Decimal("1758.22")  # 32,65%
    assert valori["cpdel_lavoratore"] == Decimal("476.58")  # 8,85%
    assert valori["fondo_credito"] == Decimal("18.85")  # 0,35%
    assert valori["imponibile_tfr"] == Decimal("4308.05")  # 80%
    assert valori["contributo_tfr"] == Decimal("262.79")  # 6,10%


def test_dirigente_assunto_a_meta_mese_ha_il_divisore_del_mese_parziale_come_il_comparto(registro, reale):
    titolare(registro, "dirigente", dal=date(2026, 11, 16))
    posizione_dirigente(registro, "20000.00", dal=date(2026, 11, 16))
    valori = importi(registro, reale, Mese(2026, 11))
    # Dal 16 al 30 novembre i giorni lun-sab sono 13 su un divisore di 26.
    assert valori["tabellare_dirigenti"] == Decimal("1923.30")
    assert valori["posizione_dirigenti"] == Decimal("769.23")


@pytest.mark.parametrize("fatto", ["retribuzione_risultato", "interim"])
def test_risultato_e_interim_del_dirigente_fermano_il_calcolo_e_nominano_il_caso(registro, reale, fatto):
    titolare(registro, "dirigente")
    registro.registra_fatto(R, fatto, "1000.00", date(2026, 11, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match=fatto):
        calcola(registro, reale, R, Mese(2026, 11))


def test_la_tredicesima_del_dirigente_non_e_un_importo_a_parte_come_nel_comparto(registro, reale):
    """Il tabellare e' gia' annuo / 13 e la tredicesima non e' modellata nel comparto (ADR 0004): dicembre non porta altro."""
    titolare(registro, "dirigente")
    posizione_dirigente(registro, "20000.00")
    novembre, dicembre = importi(registro, reale, Mese(2026, 11)), importi(registro, reale, Mese(2026, 12))
    assert dicembre == novembre
    assert not [istituto for istituto in dicembre if "tredicesima" in istituto]


def segretario(registro, fascia, dal=date(2026, 1, 1), dal_fascia=None):
    titolare(registro, "segretario", dal)
    registro.registra_codice(R, "fascia_segretario", fascia, dal_fascia or dal, atto=ATTO)


@pytest.mark.parametrize(("fascia", "atteso"), [("A", "3846.60"), ("B", "3846.60"), ("C", "3077.28")])
def test_il_tabellare_del_segretario_dipende_dalla_fascia(registro, reale, fascia, atteso):
    segretario(registro, fascia)
    (tabellare,) = [v for i, v in importi(registro, reale, Mese(2026, 11)).items() if i.startswith("tabellare_segretario")]
    assert tabellare == Decimal(atteso)  # 50.005,77 / 13 per A e B; 40.004,59 / 13 per C


def test_il_cambio_di_fascia_a_meta_mese_divide_il_tabellare_tra_le_due_fasce(registro, reale):
    titolare(registro, "segretario")
    registro.registra_codice(R, "fascia_segretario", "B", date(2026, 1, 1), date(2026, 11, 15), atto=ATTO)
    registro.registra_codice(R, "fascia_segretario", "C", date(2026, 11, 16), atto=ATTO)
    valori = importi(registro, reale, Mese(2026, 11))
    # Giorni lun-sab su 26: 12 dal 1 al 15 novembre, 13 dal 16 al 30.
    assert valori["tabellare_segretario_b"] == Decimal("1775.35")  # 3.846,60 x 12/26
    assert valori["tabellare_segretario_c"] == Decimal("1538.64")  # 3.077,28 x 13/26
    assert "tabellare_segretario_a" not in valori


def test_segretario_senza_fascia_ferma_il_calcolo_invece_di_scegliere_un_tabellare(registro, reale):
    titolare(registro, "segretario")
    with pytest.raises(CasoNonModellato, match="fascia_segretario"):
        calcola(registro, reale, R, Mese(2026, 11))


def test_segretario_senza_fascia_in_un_solo_giorno_del_mese_ferma_il_calcolo(registro, reale):
    segretario(registro, "B", dal_fascia=date(2026, 11, 10))
    with pytest.raises(CasoNonModellato, match="fascia_segretario"):
        calcola(registro, reale, R, Mese(2026, 11))


FERMO_MANCA = """
[[fermo]]
fatto = "fascia"
caso = "senza fascia"
ambito = "calcolo"
riferimento = "fittizio:fermo-fascia"
{altro}
"""


def test_un_fermo_manca_chiede_la_condizione_e_non_si_combina_con_il_codice():
    from paghe.errori import ErroreCorpus

    with pytest.raises(ErroreCorpus, match="`manca` e `se`"):
        Corpus.da_toml(FERMO_MANCA.format(altro="manca = true"))
    with pytest.raises(ErroreCorpus, match="`manca` e `se`"):
        Corpus.da_toml(FERMO_MANCA.format(altro='se = "area=x"'))
    with pytest.raises(ErroreCorpus, match="non si combina"):
        Corpus.da_toml(FERMO_MANCA.format(altro='manca = true\nse = "area=x"\ncodice = "A"'))


def posizione_segretario(registro, annua, dal=date(2026, 1, 1)):
    return registro.registra_fatto(R, "posizione_annua_segretario", annua, dal, atto=ATTO)


def test_la_posizione_del_segretario_e_l_annuo_deliberato_su_13_mensilita(registro, reale):
    segretario(registro, "B")
    posizione_segretario(registro, "12000.00")
    valori = importi(registro, reale, Mese(2026, 11))
    assert valori["tabellare_segretario_b"] == Decimal("3846.60")
    assert valori["posizione_segretario"] == Decimal("923.08")  # 12.000 / 13


def test_la_convenzione_di_segreteria_ferma_il_calcolo(registro, reale):
    segretario(registro, "B")
    registro.registra_fatto(R, "convenzione_segreteria", "1", date(2026, 11, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match="convenzione_segreteria"):
        calcola(registro, reale, R, Mese(2026, 11))


@pytest.mark.parametrize("fatto", ["scavalco", "galleggiamento", "retribuzione_risultato", "diritti_rogito"])
def test_gli_altri_casi_del_segretario_fermano_il_calcolo_e_nominano_il_fatto(registro, reale, fatto):
    segretario(registro, "B")
    registro.registra_fatto(R, fatto, "1000.00", date(2026, 11, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match=fatto):
        calcola(registro, reale, R, Mese(2026, 11))
