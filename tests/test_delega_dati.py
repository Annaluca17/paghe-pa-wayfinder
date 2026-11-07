"""Dati dell'ente, data di versamento e avvisi della delega F24EP (ADR 0023). Dati fittizi.

Se manca un dato dell'ente o la data di versamento, è un dato mancante e l'invio resta fermo; se la data di
versamento cade dopo la scadenza il modello avvisa, non ferma.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.delega import costruisci_delega

from materiale_delega import corpus_delega, dati_ente, paga_a_mano, riga_a_mano

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal


@pytest.fixture
def corpus():
    return corpus_delega()


def con_pagamento(registro, corpus, orologio, istituti=("ritenuta_irpef", "contributo_ente"), valuta=VALUTA):
    righe = [riga_a_mano(corpus, valuta, i, "10") for i in istituti]
    paga_a_mano(registro, corpus, orologio, valuta, righe)
    return costruisci_delega(registro, corpus, Mese(valuta.year, valuta.month))


def mancanti(delega):
    return {(d.tipo, d.soggetto) for d in delega.dati_mancanti}


def avvisi(delega):
    return {a.tipo for a in delega.avvisi}


# Dati dell'ente

def test_con_tutti_i_dati_dell_ente_e_la_data_la_delega_e_pronta(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    d = con_pagamento(registro, corpus, orologio)
    assert d.pronta and d.dati_mancanti == () and d.fermi == ()
    assert (d.ente.codice_fiscale, d.ente.denominazione, d.ente.sigla_provincia) == ("00000000000", "ENTE DI PROVA", "RM")


@pytest.mark.parametrize("tipo", ["codice_fiscale", "denominazione", "email", "iban_tesoreria"])
def test_un_dato_dell_ente_mancante_ferma_l_invio(registro, corpus, orologio, tipo):
    dati_ente(registro, **{tipo: None})
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    d = con_pagamento(registro, corpus, orologio)
    assert mancanti(d) == {(tipo, "ente")} and not d.pronta
    assert [r.tributo for r in d.righe] == ["100E", "P201"]  # il calcolo e la vista restano


def test_la_sigla_di_provincia_serve_solo_con_una_riga_della_sezione_inpdap(registro, corpus, orologio):
    dati_ente(registro, sigla_provincia=None)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    con_p201 = con_pagamento(registro, corpus, orologio)
    assert mancanti(con_p201) == {("sigla_provincia", "ente")}


def test_senza_righe_inpdap_la_sigla_di_provincia_non_serve(registro, corpus, orologio):
    dati_ente(registro, sigla_provincia=None)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    d = con_pagamento(registro, corpus, orologio, istituti=("ritenuta_irpef",))
    assert d.dati_mancanti == () and d.pronta


def test_i_fatti_dell_ente_valgono_alla_data_di_versamento(registro, corpus, orologio):
    dati_ente(registro, dal=date(2026, 4, 1))  # validi solo da aprile
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    d = con_pagamento(registro, corpus, orologio)
    assert {tipo for tipo, _ in mancanti(d)} == {"codice_fiscale", "denominazione", "email", "iban_tesoreria", "sigla_provincia"}


def test_un_dato_dell_ente_corretto_dopo_vale_con_il_nuovo_fatto(registro, corpus, orologio):
    dati_ente(registro, email="sbagliata@ente.example")
    registro.registra_codice_ente("email", "paghe@ente.example", date(2026, 1, 1))
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    assert con_pagamento(registro, corpus, orologio).ente.email == "paghe@ente.example"


# Dati presenti ma fuori specifica

@pytest.mark.parametrize(
    "dato, valore",
    [
        ("codice_fiscale", "00000000001"),
        ("iban_tesoreria", "IT22X0200003245TEST00000001"),
        ("email", "senza-chiocciola"),
        ("denominazione", "E" * 56),
    ],
)
def test_un_dato_dell_ente_fuori_specifica_ferma_l_invio(registro, corpus, orologio, dato, valore):
    dati_ente(registro, **{dato: valore})
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    d = con_pagamento(registro, corpus, orologio)
    assert {f.caso for f in d.fermi} == {"dato_non_valido"} and not d.pronta


def test_una_sigla_di_provincia_non_valida_ferma_l_invio(registro, corpus, orologio):
    dati_ente(registro, sigla_provincia="roma")
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    d = con_pagamento(registro, corpus, orologio)
    assert {f.caso for f in d.fermi} == {"dato_non_valido"}


# Data di versamento

def test_senza_data_di_versamento_l_invio_e_fermo(registro, corpus, orologio):
    dati_ente(registro)
    d = con_pagamento(registro, corpus, orologio)
    assert mancanti(d) == {("data_versamento", "ente")} and d.data_versamento is None and not d.pronta


def test_una_data_di_versamento_dopo_la_scadenza_e_un_avviso_e_non_un_fermo(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 17))  # la scadenza è il 16
    d = con_pagamento(registro, corpus, orologio)
    assert avvisi(d) == {"versamento_dopo_la_scadenza"} and d.pronta
    avviso = next(iter(d.avvisi))
    assert "2026-03-17" in avviso.messaggio and "2026-03-16" in avviso.messaggio


@pytest.mark.parametrize("giorno", [date(2026, 3, 13), date(2026, 3, 16)])
def test_una_data_entro_la_scadenza_non_da_avvisi(registro, corpus, orologio, giorno):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, giorno)
    assert avvisi(con_pagamento(registro, corpus, orologio)) == set()


# Scadenza nella delega

def test_il_pagamento_di_luglio_ha_la_scadenza_del_20_agosto_e_l_avviso_di_prassi(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(Mese(2026, 7), date(2026, 8, 20))
    d = con_pagamento(registro, corpus, orologio, valuta=date(2026, 7, 24))
    assert d.scadenza.data == date(2026, 8, 20)
    assert avvisi(d) == {"scadenza_per_prassi"} and d.pronta


def test_il_16_di_domenica_la_scadenza_e_il_lunedi_e_versare_quel_giorno_non_da_avvisi(registro, corpus, orologio):
    """Aprile 2027: il 16 maggio è domenica, la scadenza è lunedì 17."""
    dati_ente(registro)
    registro.registra_data_versamento(Mese(2027, 4), date(2027, 5, 17))
    d = con_pagamento(registro, corpus, orologio, valuta=date(2027, 4, 23))
    assert d.scadenza.data == date(2027, 5, 17) and avvisi(d) == set()


def test_una_scadenza_non_calcolabile_ferma_l_invio_e_nomina_il_caso(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(Mese(2028, 12), date(2029, 1, 16))
    d = con_pagamento(registro, corpus, orologio, valuta=date(2028, 12, 20))
    assert d.scadenza is None
    (fermo,) = d.fermi
    assert fermo.caso == "scadenza_non_calcolabile" and "2029" in fermo.motivo
    assert not d.pronta
