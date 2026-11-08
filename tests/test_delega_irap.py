"""Acconto IRAP nella delega F24EP: 380E per regione della sede di lavoro (ADR 0028, ticket #81). Dati fittizi.

Pagamento del 27 febbraio 2026: riferimento A `0002`, riferimento B `2026`, scadenza il 16 marzo 2026.
Codici regione della tabella dei test: Lazio 08, Lombardia 10 (ris. AdE 367/E/2007 per il formato).
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.delega import costruisci_delega

from materiale_delega import R, R2, corpus_delega, dati_ente, paga_a_mano, riga_a_mano

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))


def sede(registro, rapporto, regione, dal=date(2026, 1, 1), al=None):
    registro.registra_codice(rapporto, "sede_lavoro", regione, dal, al)


def delega_irap(registro, corpus, orologio, **per_rapporto):
    """Un acconto IRAP per rapporto, pagato alla VALUTA: `R=...` come {rapporto: importo}."""
    righe = [riga_a_mano(corpus, VALUTA, "irap_acconto", importo, rapporto=rapporto) for rapporto, importo in per_rapporto.items()]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    return costruisci_delega(registro, corpus, FEB)


def test_senza_sede_l_acconto_va_nella_regione_dell_ente_con_il_suo_codice(registro, corpus, orologio, ente):
    d = delega_irap(registro, corpus, orologio, **{R: "174.39"})
    (riga,) = d.righe
    assert (riga.sezione, riga.tributo, riga.codice, riga.estremi, riga.rif_a, riga.rif_b) == ("R", "380E", "08", "", "0002", "2026")
    assert (riga.debito, riga.credito) == (D("174.39"), D(0))
    assert d.fermi == () and d.dati_mancanti == ()


def test_due_rapporti_in_due_regioni_nello_stesso_mese_danno_due_righe_380E(registro, corpus, orologio, ente):
    sede(registro, R2, "lombardia")
    d = delega_irap(registro, corpus, orologio, **{R: "100.00", R2: "60.50"})
    assert [(r.tributo, r.codice, r.debito) for r in d.righe] == [("380E", "08", D("100.00")), ("380E", "10", D("60.50"))]
    assert d.fermi == ()


def test_due_rapporti_nella_stessa_regione_sono_una_riga_sola(registro, corpus, orologio, ente):
    sede(registro, R, "lazio")
    d = delega_irap(registro, corpus, orologio, **{R: "100.00", R2: "60.50"})  # R2 senza sede: regione dell'ente, Lazio
    assert [(r.codice, r.debito) for r in d.righe] == [("08", D("160.50"))]


def test_la_sede_del_rapporto_vince_sulla_regione_dell_ente(registro, corpus, orologio, ente):
    sede(registro, R, "lombardia")
    d = delega_irap(registro, corpus, orologio, **{R: "100.00"})
    assert [(r.codice, r.debito) for r in d.righe] == [("10", D("100.00"))]


def test_la_sede_conta_alla_data_di_pagamento(registro, corpus, orologio, ente):
    sede(registro, R, "lombardia", dal=date(2026, 1, 1), al=date(2026, 2, 10))
    sede(registro, R, "lazio", dal=date(2026, 2, 11))
    d = delega_irap(registro, corpus, orologio, **{R: "100.00"})  # pagato il 27 febbraio
    assert [r.codice for r in d.righe] == ["08"]


def test_senza_sede_e_senza_regione_dell_ente_manca_un_dato_e_la_riga_non_c_e(registro, corpus, orologio):
    dati_ente(registro, regione=None)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    d = delega_irap(registro, corpus, orologio, **{R: "100.00"})
    assert d.righe == () and d.fermi == ()
    (mancante,) = d.dati_mancanti
    assert (mancante.tipo, mancante.soggetto) == ("regione", "ente")
    assert not d.pronta


def test_una_sede_basta_anche_senza_la_regione_dell_ente(registro, corpus, orologio):
    dati_ente(registro, regione=None)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    sede(registro, R, "lombardia")
    d = delega_irap(registro, corpus, orologio, **{R: "100.00"})
    assert [r.codice for r in d.righe] == ["10"] and d.dati_mancanti == ()


def test_una_regione_senza_codice_nel_corpus_ferma_l_invio_e_la_nomina(registro, corpus, orologio, ente):
    sede(registro, R, "atlantide")
    d = delega_irap(registro, corpus, orologio, **{R: "100.00"})
    (fermo,) = d.fermi
    assert fermo.caso == "regione_non_mappata" and "atlantide" in fermo.motivo
    assert d.righe == ()


def tipi_avvisi(delega):
    return [a.tipo for a in delega.avvisi]


def test_un_cambio_di_sede_da_meno_di_tre_mesi_da_un_avviso_e_non_un_fermo(registro, corpus, orologio, ente):
    sede(registro, R, "lombardia", dal=date(2025, 6, 1), al=date(2026, 1, 31))
    sede(registro, R, "lazio", dal=date(2026, 2, 1))
    d = delega_irap(registro, corpus, orologio, **{R: "100.00"})
    assert d.fermi == () and [r.codice for r in d.righe] == ["08"]
    (avviso,) = [a for a in d.avvisi if a.tipo == "cambio_sede_recente"]
    assert R in avviso.messaggio and "lombardia" in avviso.messaggio and "lazio" in avviso.messaggio


def test_un_cambio_di_sede_da_almeno_tre_mesi_non_da_avvisi(registro, corpus, orologio, ente):
    sede(registro, R, "lombardia", dal=date(2025, 6, 1), al=date(2025, 10, 31))
    sede(registro, R, "lazio", dal=date(2025, 11, 1))  # da tre mesi e 26 giorni al pagamento del 27 febbraio
    d = delega_irap(registro, corpus, orologio, **{R: "100.00"})
    assert "cambio_sede_recente" not in tipi_avvisi(d)


def test_una_sede_sola_o_la_stessa_regione_non_da_avvisi(registro, corpus, orologio, ente):
    sede(registro, R, "lazio", dal=date(2025, 6, 1), al=date(2026, 1, 31))
    sede(registro, R, "lazio", dal=date(2026, 2, 1))  # nuova sede, stessa regione
    sede(registro, R2, "lombardia", dal=date(2026, 2, 1))  # prima sede registrata: non e' un cambio
    d = delega_irap(registro, corpus, orologio, **{R: "100.00", R2: "50.00"})
    assert "cambio_sede_recente" not in tipi_avvisi(d)
