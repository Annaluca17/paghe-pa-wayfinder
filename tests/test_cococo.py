"""Regimi del titolo, PR B del ticket #73: co.co.co. (corpus reale).

Gli importi attesi sono ricalcolati a mano dalle fonti: Circ. INPS 8/2026 (aliquote, ripartizione 2/3 e 1/3, massimale
122.295 euro). Compensi di fantasia (input da atto, nessuna norma). Persone e rapporti di fantasia.
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


def collaboratore(registro, posizione="gestione_separata", dal=date(2026, 1, 1)):
    registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(R, "PERSONA-1", dal)
    if posizione is not None:
        registro.registra_codice(R, "posizione_previdenziale", posizione, dal, atto=ATTO)


def rata(registro, importo, giorno):
    return registro.registra_fatto(R, "rata_collaborazione", importo, giorno, giorno, atto=ATTO)


def importi(registro, corpus, mese):
    return {riga.istituto: riga.valore for riga in calcola(registro, corpus, R, mese)}


def test_la_rata_del_piano_matura_come_evento_nel_giorno_della_scadenza(registro, reale):
    collaboratore(registro)
    rata(registro, "1500.00", date(2026, 11, 30))
    (riga,) = calcola(registro, reale, R, Mese(2026, 11))
    assert (riga.istituto, riga.valore, riga.derivazione.maturazione) == ("compenso_collaborazione", Decimal("1500.00"), "evento")
    assert riga.periodo.dal == riga.periodo.al == date(2026, 11, 30)


def test_l_attestazione_della_prestazione_e_la_condizione_di_proposta_della_rata(reale):
    condizione = reale.condizione_di_proposta("compenso_collaborazione", date(2026, 11, 27))
    assert condizione is not None and condizione.fatto == "attestazione_prestazione"
    assert reale.condizione_di_proposta("tabellare_funzionari", date(2026, 11, 27)) is None


def paga(registro, orologio, righe, giorno):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(R, esito.id, giorno)
    orologio.avanza()
    return esito


def gestione_separata(registro, corpus, mese):
    (periodo,) = calcola_denuncia(registro, corpus, R, mese).periodi
    return {riga.istituto: riga.valore for riga in (*periodo.basi, *periodo.contributi)}


def paga_la_rata(registro, orologio, reale, importo, posizione="gestione_separata"):
    collaboratore(registro, posizione)
    rata(registro, importo, date(2026, 11, 30))
    paga(registro, orologio, calcola(registro, reale, R, Mese(2026, 11)), date(2026, 11, 30))
    return gestione_separata(registro, reale, Mese(2026, 11))


def test_senza_altra_cassa_la_gestione_separata_e_al_3503_con_un_terzo_al_collaboratore(registro, reale, orologio):
    valori = paga_la_rata(registro, orologio, reale, "1000.00")
    assert valori["base.gestione_separata"] == Decimal("1000.00")
    assert valori["gs_totale"] == Decimal("350.30")  # 33,00 IVS + 0,72 aggiuntive + 1,31 DIS-COLL
    assert valori["gs_lavoratore"] == Decimal("116.77")  # un terzo, arrotondato
    assert valori["gs_ente"] == Decimal("233.53")  # per differenza: 350,30 - 116,77
    assert valori["gs_lavoratore"] + valori["gs_ente"] == valori["gs_totale"]


@pytest.mark.parametrize("posizione", ["pensionato", "altra_cassa"])
def test_pensionato_o_con_altra_cassa_ha_l_ivs_al_24_piu_le_aggiuntive(registro, reale, orologio, posizione):
    valori = paga_la_rata(registro, orologio, reale, "1000.00", posizione)
    assert valori["gs_totale"] == Decimal("247.20")  # 24,00 IVS + 0,72 aggiuntive, senza DIS-COLL (da verificare)
    assert valori["gs_lavoratore"] == Decimal("82.40")
    assert valori["gs_ente"] == Decimal("164.80")


@pytest.mark.parametrize("fatto", ["cumulo_altri_committenti", "inail_dovuta", "irap_dovuta"])
def test_cumulo_inail_e_irap_fermano_il_calcolo_e_nominano_il_caso(registro, reale, fatto):
    collaboratore(registro)
    rata(registro, "1000.00", date(2026, 11, 30))
    registro.registra_fatto(R, fatto, "1", date(2026, 11, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match=fatto):
        calcola(registro, reale, R, Mese(2026, 11))
