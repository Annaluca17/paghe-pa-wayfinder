"""Calendario dei festivi per anno e patrono della sede (ticket #106). Dati fittizi, codici di fantasia."""

from datetime import date, timedelta

import pytest

from paghe.calendario import e_lavorativo, pasqua
from paghe.corpus import CalendarioFestivi
from paghe.errori import ErroreCalcolo


@pytest.mark.parametrize(
    "anno, atteso",
    [(2024, date(2024, 3, 31)), (2025, date(2025, 4, 20)), (2026, date(2026, 4, 5)), (2027, date(2027, 3, 28))],
)
def test_la_pasqua_e_calcolata_non_scritta_a_mano(anno, atteso):
    assert pasqua(anno) == atteso


def calendario(anno, feste=("01-01", "10-04", "12-08", "12-25")):
    return CalendarioFestivi(anno, feste, True, "fittizio:festivi-prova")


def test_nel_2026_il_lunedi_dell_angelo_e_il_6_aprile_e_il_4_ottobre_c_e_anche_di_domenica():
    giorni = calendario(2026).giorni
    assert date(2026, 4, 6) in giorni
    assert date(2026, 10, 4) in giorni and date(2026, 10, 4).weekday() == 6


def test_nel_2027_il_lunedi_dell_angelo_e_il_29_marzo_e_il_4_ottobre_lunedi_non_e_lavorativo():
    c = calendario(2027)
    assert date(2027, 3, 29) in c.giorni
    assert date(2027, 10, 4).weekday() == 0
    assert not e_lavorativo(c, date(2027, 10, 4))
    assert e_lavorativo(c, date(2027, 10, 5))


def test_il_patrono_infrasettimanale_toglie_un_giorno_lavorativo():
    assert e_lavorativo(calendario(2026), date(2026, 6, 29))  # lunedì
    assert not e_lavorativo(calendario(2026), date(2026, 6, 29), "H501 06-29")


@pytest.mark.parametrize("patrono", ["H501 06-27", "H501 06-28", "H501 12-08", "H501 01-01"])
def test_il_patrono_di_sabato_domenica_o_su_festa_nazionale_non_toglie_altri_giorni(patrono):
    c = calendario(2026)
    con = [g for g in (date(2026, 6, 26) + timedelta(days=n) for n in range(5)) if e_lavorativo(c, g, patrono)]
    senza = [g for g in (date(2026, 6, 26) + timedelta(days=n) for n in range(5)) if e_lavorativo(c, g)]
    assert con == senza
    assert not e_lavorativo(c, date(2026, 12, 8), patrono)  # festa nazionale: già non lavorativa, nulla in più
    assert e_lavorativo(c, date(2026, 12, 9), patrono)


@pytest.mark.parametrize("valore", ["06-29", "H501", "H501 6-29", "h501 06-29", "H501 02-30", "H501 13-01"])
def test_un_patrono_malformato_e_un_errore_chiaro(valore):
    with pytest.raises(ErroreCalcolo, match="Patrono"):
        e_lavorativo(calendario(2026), date(2026, 6, 29), valore)


# Casi limite (rilettura): Pasqua agli estremi, patrono sul lunedì dell'Angelo, 29 febbraio in anno non bisestile.
@pytest.mark.parametrize("anno, atteso", [(2285, date(2285, 3, 22)), (2038, date(2038, 4, 25)), (2000, date(2000, 4, 23))])
def test_la_pasqua_agli_estremi_del_calendario_gregoriano(anno, atteso):
    assert pasqua(anno) == atteso


def test_un_patrono_sul_lunedi_dell_angelo_non_toglie_un_giorno_in_piu():
    cal = calendario(2026)
    aprile = [date(2026, 4, 1) + timedelta(days=n) for n in range(30)]
    senza = [g for g in aprile if e_lavorativo(cal, g)]
    con = [g for g in aprile if e_lavorativo(cal, g, "H501 04-06")]
    assert con == senza


def test_un_patrono_il_29_febbraio_e_valido_e_negli_anni_non_bisestili_non_cade_mai():
    cal = calendario(2027)
    febbraio = [date(2027, 2, 1) + timedelta(days=n) for n in range(28)]
    assert all(e_lavorativo(cal, g, "H501 02-29") == e_lavorativo(cal, g) for g in febbraio)
    assert not e_lavorativo(calendario(2028), date(2028, 2, 29), "H501 02-29")
