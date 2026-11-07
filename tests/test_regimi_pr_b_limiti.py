"""Casi limite della PR B del ticket #73, scritti nella rilettura: massimale nel mese stesso e al cambio d'anno.
Persone e rapporti di fantasia."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese, calcola
from paghe.errori import ParametroMancante

from tests.test_cococo import R, collaboratore, gestione_separata, paga, rata, reale  # noqa: F401


def test_una_sola_rata_oltre_il_massimale_ha_la_base_al_massimale_nel_mese_stesso(registro, reale, orologio):
    collaboratore(registro)
    rata(registro, "130000.00", date(2026, 1, 30))
    paga(registro, orologio, calcola(registro, reale, R, Mese(2026, 1)), date(2026, 1, 30))
    assert gestione_separata(registro, reale, Mese(2026, 1))["base.gestione_separata"] == Decimal("122295.00")


def test_senza_il_massimale_dell_anno_nuovo_la_base_si_ferma_invece_di_riusare_quello_vecchio(registro, reale, orologio):
    collaboratore(registro)
    rata(registro, "130000.00", date(2026, 12, 30))
    paga(registro, orologio, calcola(registro, reale, R, Mese(2026, 12)), date(2026, 12, 30))
    rata(registro, "1000.00", date(2027, 1, 29))
    paga(registro, orologio, calcola(registro, reale, R, Mese(2027, 1)), date(2027, 1, 29))
    with pytest.raises(ParametroMancante, match="massimale_annuo_gs"):
        gestione_separata(registro, reale, Mese(2027, 1))


def test_due_rate_nello_stesso_mese_che_passano_il_massimale(registro, reale, orologio):
    collaboratore(registro)
    rata(registro, "120000.00", date(2026, 3, 10))
    rata(registro, "5000.00", date(2026, 3, 30))
    paga(registro, orologio, calcola(registro, reale, R, Mese(2026, 3)), date(2026, 3, 30))
    assert gestione_separata(registro, reale, Mese(2026, 3))["base.gestione_separata"] == Decimal("122295.00")
