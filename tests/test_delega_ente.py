"""Fatti sull'ente per la delega F24EP: data di versamento e credito riportato (ADR 0023, ticket #54). Dati fittizi."""

from datetime import date

import pytest

from paghe import Mese
from paghe.errori import ErroreRegistro

MARZO = Mese(2026, 3)


def test_senza_fatto_la_data_di_versamento_manca(registro, orologio):
    assert registro.data_versamento_scelta(MARZO, orologio()) is None


def test_la_data_di_versamento_e_un_fatto_dell_ente_per_mese_di_pagamento(registro, orologio):
    fatto = registro.registra_data_versamento(MARZO, date(2026, 4, 14))
    assert fatto.soggetto == "ente"
    assert registro.data_versamento_scelta(MARZO, orologio()) == date(2026, 4, 14)
    assert registro.data_versamento_scelta(Mese(2026, 4), orologio()) is None


def test_una_nuova_scelta_corregge_la_precedente_e_si_legge_a_un_istante(registro, orologio):
    registro.registra_data_versamento(MARZO, date(2026, 4, 14))
    prima = orologio()
    orologio.avanza(3600)
    registro.registra_data_versamento(MARZO, date(2026, 4, 15))
    assert registro.data_versamento_scelta(MARZO, orologio()) == date(2026, 4, 15)
    assert registro.data_versamento_scelta(MARZO, prima) == date(2026, 4, 14)


def test_una_scelta_annullata_non_vale(registro, orologio):
    registro.registra_data_versamento(MARZO, date(2026, 4, 14))
    sbagliata = registro.registra_data_versamento(MARZO, date(2026, 4, 30))
    registro.annulla_fatto(sbagliata.id, "scelta per errore")
    assert registro.data_versamento_scelta(MARZO, orologio()) == date(2026, 4, 14)


def test_la_data_di_versamento_non_precede_il_mese_di_pagamento(registro):
    with pytest.raises(ErroreRegistro, match="mese di pagamento"):
        registro.registra_data_versamento(MARZO, date(2026, 2, 28))


def test_il_credito_riportato_e_un_fatto_categoriale_dell_ente(registro, orologio):
    fatto = registro.registra_codice_ente("credito_riportato", "{}", date(2026, 4, 17))
    assert fatto.soggetto == "ente" and fatto.categoriale
    assert registro.vigente_ente("credito_riportato", date(2026, 6, 1), orologio()) == fatto
