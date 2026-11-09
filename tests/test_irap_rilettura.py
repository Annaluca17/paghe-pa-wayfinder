"""Rilettura del ticket #81: casi limite dell'acconto IRAP che i test della sessione non coprivano. Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.delega import costruisci_delega, trasmetti_delega

from controlli_f24ep import controlla
from materiale_delega import ADATTATORE, R, R2, corpus_delega, dati_ente, paga_a_mano, riga_a_mano
from test_irap import CORPUS, assumi, collabora, paga_il_mese, valori

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def test_un_esclusione_finita_prima_del_pagamento_non_toglie_nulla(registro, reale, orologio):
    assumi(registro)
    registro.registra_codice("RAPPORTO-1", "esclusione_base_irap", "cfl", date(2026, 1, 1), date(2026, 11, 15))
    paga_il_mese(registro, orologio, reale)
    v = valori(registro, reale)
    assert v["base.irap"] == D("2051.69")
    assert v["irap_acconto"] == D("174.39")


def test_un_cococo_escluso_non_ha_un_acconto_negativo(registro, reale, orologio):
    """Base zero: l'acconto non e' negativo."""
    registro.registra_codice("RAPPORTO-1", "esclusione_base_irap", "disabile", date(2026, 1, 1))
    collabora(registro, orologio, reale)
    v = valori(registro, reale)
    assert v.get("irap_acconto", D(0)) == D(0)
    assert v["gs_lavoratore"] == D("116.77")  # la previdenza non cambia


def test_un_acconto_zero_non_scrive_una_riga_380E(registro, orologio):
    corpus = corpus_delega()
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    righe = [
        riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100"),
        riga_a_mano(corpus, VALUTA, "irap_acconto", "0.00", rapporto=R2),
    ]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    d = costruisci_delega(registro, corpus, FEB)
    assert [r.tributo for r in d.righe] == ["100E"]


def test_il_file_con_due_380E_supera_i_controlli(registro, orologio):
    corpus = corpus_delega()
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    registro.registra_codice(R2, "sede_lavoro", "lombardia", date(2026, 1, 1))
    righe = [
        riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100"),
        riga_a_mano(corpus, VALUTA, "irap_acconto", "33.33", rapporto=R),
        riga_a_mano(corpus, VALUTA, "irap_acconto", "0.01", rapporto=R2),
    ]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    orologio.vai(3, 10)
    t = trasmetti_delega(registro, corpus, "DELEGA-1", ADATTATORE, FEB)
    assert controlla(t.file) == ([], [])
    testo = t.file.decode("latin-1")
    assert "R380E" in testo and testo.count("380E") == 2
