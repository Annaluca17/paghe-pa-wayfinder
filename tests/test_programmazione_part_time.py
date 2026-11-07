"""Programmazione del part-time: input da atto, un fatto per giorno (ADR 0026, ticket #72). Dati fittizi."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from paghe import Atto, Mese, Periodo
from paghe.errori import ErroreRegistro
from paghe.part_time import programmazione_del_mese, registra_programmazione

R = "RAPPORTO-1"
ATTO = Atto("fittizio:programmazione-2026", date(2026, 10, 20))
NOVEMBRE = Mese(2026, 11)


def settimana_corta(mese: Mese, ore="6"):
    """Lunedì-venerdì lavorativi con `ore`, sabato e domenica a riposo."""
    return {giorno: (Decimal(ore) if giorno.weekday() < 5 else Decimal(0)) for giorno in mese.giorni()}


def test_la_programmazione_del_mese_dice_per_ogni_giorno_se_si_lavora_e_per_quante_ore(registro):
    registra_programmazione(registro, R, settimana_corta(NOVEMBRE), ATTO)
    programmazione = programmazione_del_mese(registro, R, NOVEMBRE)
    assert programmazione.completa
    assert programmazione.ore[date(2026, 11, 2)] == Decimal("6")   # lunedì
    assert programmazione.ore[date(2026, 11, 1)] == Decimal("0")   # domenica
    assert programmazione.giorni_lavorativi == 21
    assert programmazione.ore_totali == Decimal("126")


def test_senza_programmazione_il_mese_non_e_coperto(registro):
    programmazione = programmazione_del_mese(registro, R, NOVEMBRE)
    assert not programmazione.completa
    assert not programmazione.ore


def test_un_mese_coperto_in_parte_non_e_completo_e_dice_quali_giorni_mancano(registro):
    parziale = {g: o for g, o in settimana_corta(NOVEMBRE).items() if g.day <= 20}
    registra_programmazione(registro, R, parziale, ATTO)
    programmazione = programmazione_del_mese(registro, R, NOVEMBRE)
    assert not programmazione.completa
    assert programmazione.mancanti == (Periodo(date(2026, 11, 21), date(2026, 11, 30)),)


def test_una_programmazione_annuale_copre_piu_mesi(registro):
    anno = {g: Decimal(6) for g in Periodo(date(2026, 1, 1), date(2026, 12, 31)).giorni()}
    registra_programmazione(registro, R, anno, ATTO)
    assert programmazione_del_mese(registro, R, Mese(2026, 2)).completa
    assert programmazione_del_mese(registro, R, Mese(2026, 12)).completa


def test_una_correzione_sostituisce_il_giorno(registro):
    registra_programmazione(registro, R, settimana_corta(NOVEMBRE), ATTO)
    registra_programmazione(registro, R, {date(2026, 11, 2): Decimal("3")}, Atto("fittizio:variazione", date(2026, 11, 1)))
    programmazione = programmazione_del_mese(registro, R, NOVEMBRE)
    assert programmazione.ore[date(2026, 11, 2)] == Decimal("3")
    assert programmazione.ore[date(2026, 11, 3)] == Decimal("6")


def test_la_programmazione_e_un_input_da_atto(registro):
    with pytest.raises(ErroreRegistro, match="atto"):
        registra_programmazione(registro, R, settimana_corta(NOVEMBRE), None)


@pytest.mark.parametrize("ore", ["-1", "25"])
def test_le_ore_di_un_giorno_stanno_fra_zero_e_ventiquattro(registro, ore):
    with pytest.raises(ErroreRegistro, match="ore"):
        registra_programmazione(registro, R, {date(2026, 11, 2): Decimal(ore)}, ATTO)
