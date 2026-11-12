"""Malattia del comparto (ADR 0042, ticket #130).

Due gruppi: le regole pure sugli episodi (stati dei giorni), con il corpus reale per i parametri; il calcolo del mese e
della tredicesima con il corpus reale. Persone e rapporti sono di fantasia.
"""

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Corpus, Mese, Periodo, calcola, calcola_annuale
from paghe.errori import CasoNonModellato
from paghe.malattia import INFORTUNIO, ORDINARIA, RICOVERO, SALVAVITA, registra_malattia, stati_del_periodo

CORPUS_REALE = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
R = "RAPPORTO-1"


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS_REALE, reale=True)


def assumi(registro, area="istruttori", regime="3"):
    dal = date(2019, 1, 1)
    registro.registra_codice(R, "tipo_impiego", "1", dal, None)
    registro.registra_codice(R, "area", area, dal, None)
    registro.registra_codice(R, "regime_fine_servizio", regime, dal, None)


def somma(importi, istituto):
    return sum((i.valore for i in importi if i.istituto == istituto), Decimal(0))


def stati(registro, reale, dal, al):
    return stati_del_periodo(registro, reale, R, Periodo(dal, al))


# --- Episodi e decurtazione dei primi 10 giorni ---


def test_un_episodio_di_un_giorno_e_decurtato(registro, reale):
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 10))
    s = stati(registro, reale, date(2026, 3, 1), date(2026, 3, 31))
    assert list(s) == [date(2026, 3, 10)]
    assert s[date(2026, 3, 10)].decurtazione is True
    assert s[date(2026, 3, 10)].percentuale == Decimal(100)


def test_un_episodio_di_15_giorni_e_decurtato_solo_nei_primi_10(registro, reale):
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 24))
    s = stati(registro, reale, date(2026, 3, 1), date(2026, 3, 31))
    assert [g.day for g, x in s.items() if x.decurtazione] == list(range(10, 20))
    assert [g.day for g, x in s.items() if not x.decurtazione] == list(range(20, 25))


def test_i_dieci_giorni_non_sono_un_tetto_annuale(registro, reale):
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 14))
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 20), date(2026, 3, 22))
    s = stati(registro, reale, date(2026, 3, 1), date(2026, 3, 31))
    assert all(x.decurtazione for x in s.values()) and len(s) == 8


def test_certificati_continui_sono_un_solo_episodio(registro, reale):
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 14))
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 15), date(2026, 3, 24))
    s = stati(registro, reale, date(2026, 3, 1), date(2026, 3, 31))
    assert [g.day for g, x in s.items() if x.decurtazione] == list(range(10, 20))


def test_un_fine_settimana_tra_due_certificati_non_spezza_l_episodio(registro, reale):
    # venerdì 13 marzo 2026 e lunedì 16: sabato e domenica non sono lavorati
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 9), date(2026, 3, 13))
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 16), date(2026, 3, 20))
    s = stati(registro, reale, date(2026, 3, 1), date(2026, 3, 31))
    assert date(2026, 3, 14) in s and date(2026, 3, 15) in s  # i giorni in mezzo sono dell'episodio
    assert [g.day for g, x in s.items() if x.decurtazione] == list(range(9, 19))
    assert s[date(2026, 3, 19)].decurtazione is False


def test_un_giorno_lavorato_in_mezzo_apre_un_nuovo_episodio(registro, reale):
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 9), date(2026, 3, 13))
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 17), date(2026, 3, 21))  # martedì: 16 lavorato
    s = stati(registro, reale, date(2026, 3, 1), date(2026, 3, 31))
    assert date(2026, 3, 16) not in s
    assert all(x.decurtazione for x in s.values())  # due episodi, ciascuno sotto i 10 giorni


def test_il_ricovero_non_e_decurtato(registro, reale):
    registra_malattia(registro, R, RICOVERO, date(2026, 3, 10), date(2026, 3, 24))
    s = stati(registro, reale, date(2026, 3, 1), date(2026, 3, 31))
    assert not any(x.decurtazione for x in s.values())


def test_salvavita_e_infortunio_non_sono_decurtati_e_non_contano_per_il_comporto(registro, reale):
    registra_malattia(registro, R, SALVAVITA, date(2026, 3, 2), date(2026, 3, 6))
    registra_malattia(registro, R, INFORTUNIO, date(2026, 3, 9), date(2026, 3, 13))
    s = stati(registro, reale, date(2026, 3, 1), date(2026, 3, 31))
    assert not any(x.decurtazione for x in s.values())
    assert all(x.giorni_comporto == 0 and x.percentuale == Decimal(100) for x in s.values())


# --- Periodi 100 / 90 / 50 / non retribuito sui tre anni ---


def _giorno_n(inizio, n):
    return inizio + timedelta(days=n - 1)


def test_il_comporto_passa_al_90_al_271_giorno(registro, reale):
    inizio = date(2025, 1, 1)
    registra_malattia(registro, R, RICOVERO, inizio, _giorno_n(inizio, 600))
    s = stati_del_periodo(registro, reale, R, Periodo(inizio, _giorno_n(inizio, 600)))
    assert s[_giorno_n(inizio, 270)].percentuale == Decimal(100)
    assert s[_giorno_n(inizio, 271)].percentuale == Decimal(90)
    assert s[_giorno_n(inizio, 360)].percentuale == Decimal(90)
    assert s[_giorno_n(inizio, 361)].percentuale == Decimal(50)
    assert s[_giorno_n(inizio, 540)].percentuale == Decimal(50)
    assert s[_giorno_n(inizio, 541)].percentuale == Decimal(0)


def test_il_comporto_somma_gli_episodi_dei_tre_anni_e_dimentica_i_piu_vecchi(registro, reale):
    registra_malattia(registro, R, RICOVERO, date(2022, 1, 1), date(2022, 12, 31))  # 365 giorni, fuori dai tre anni
    registra_malattia(registro, R, RICOVERO, date(2025, 1, 1), date(2025, 9, 27))  # 270 giorni
    registra_malattia(registro, R, ORDINARIA, date(2026, 1, 12), date(2026, 1, 12))
    s = stati(registro, reale, date(2026, 1, 1), date(2026, 1, 31))
    assert s[date(2026, 1, 12)].giorni_comporto == 271 and s[date(2026, 1, 12)].percentuale == Decimal(90)


# --- Calcolo del mese ---


def test_il_comparto_si_toglie_nei_dieci_giorni_il_tabellare_resta(registro, reale):
    assumi(registro)
    base = calcola(registro, reale, R, Mese(2026, 3))
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 24))
    con = calcola(registro, reale, R, Mese(2026, 3))
    assert somma(con, "tabellare_istruttori") == somma(base, "tabellare_istruttori")
    comparto = somma(base, "comparto_istruttori")
    # dal 10 al 19 marzo, senza la domenica 15: 9 giorni su 26
    atteso = comparto - (comparto * 9 / 26).quantize(Decimal("0.01"))
    assert abs(somma(con, "comparto_istruttori") - atteso) <= Decimal("0.01")


def test_l_episodio_di_un_giorno_toglie_un_ventiseiesimo(registro, reale):
    assumi(registro)
    base = calcola(registro, reale, R, Mese(2026, 3))
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 10))
    con = calcola(registro, reale, R, Mese(2026, 3))
    comparto = somma(base, "comparto_istruttori")
    atteso = comparto - (comparto / 26).quantize(Decimal("0.01"))
    assert abs(somma(con, "comparto_istruttori") - atteso) <= Decimal("0.01")


def test_il_ricovero_non_toglie_nulla(registro, reale):
    assumi(registro)
    base = calcola(registro, reale, R, Mese(2026, 3))
    registra_malattia(registro, R, RICOVERO, date(2026, 3, 10), date(2026, 3, 24))
    con = calcola(registro, reale, R, Mese(2026, 3))
    assert somma(con, "comparto_istruttori") == somma(base, "comparto_istruttori")
    assert somma(con, "tabellare_istruttori") == somma(base, "tabellare_istruttori")


def test_al_90_per_cento_si_riduce_anche_il_tabellare(registro, reale):
    assumi(registro)
    registra_malattia(registro, R, RICOVERO, date(2025, 1, 1), date(2025, 9, 27))  # 270 giorni a 100
    base = calcola(registro, reale, R, Mese(2026, 3))
    registra_malattia(registro, R, RICOVERO, date(2026, 3, 1), date(2026, 3, 31))  # tutto il mese al 90
    con = calcola(registro, reale, R, Mese(2026, 3))
    tabellare = somma(base, "tabellare_istruttori")
    assert somma(con, "tabellare_istruttori") == (tabellare * Decimal("0.9")).quantize(Decimal("0.01"))


def test_i_contributi_restano_sull_intero(registro, reale):
    assumi(registro)
    base = calcola(registro, reale, R, Mese(2026, 3))
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 24))
    con = calcola(registro, reale, R, Mese(2026, 3))
    for istituto in ("cpdel_totale", "fondo_credito", "imponibile_tfs", "tfs_totale"):
        assert somma(con, istituto) == somma(base, istituto), istituto


def test_un_istituto_senza_dichiarazione_ferma_il_calcolo(registro, reale):
    registro.registra_codice(R, "tipo_impiego", "1", date(2019, 1, 1), None)
    registro.registra_codice(R, "fascia_segretario", "A", date(2019, 1, 1), None)
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 12))
    with pytest.raises(CasoNonModellato, match="malattia"):
        calcola(registro, reale, R, Mese(2026, 3))


# --- Tredicesima ---


def test_la_tredicesima_si_riduce_nei_periodi_al_90_e_al_50(registro, reale):
    assumi(registro)
    piena = somma(calcola_annuale(registro, reale, R, 2026), "tredicesima_istruttori")
    registra_malattia(registro, R, RICOVERO, date(2025, 1, 1), date(2025, 9, 27))
    # 31 giorni al 90% a gennaio 2026
    registra_malattia(registro, R, RICOVERO, date(2026, 1, 1), date(2026, 1, 31))
    ridotta = somma(calcola_annuale(registro, reale, R, 2026), "tredicesima_istruttori")
    atteso = (piena * (Decimal(365 - 31) + Decimal(31) * Decimal("0.9")) / 365).quantize(Decimal("0.01"))
    assert abs(ridotta - atteso) <= Decimal("0.01")


def test_la_decurtazione_dei_dieci_giorni_non_tocca_la_tredicesima(registro, reale):
    assumi(registro)
    piena = somma(calcola_annuale(registro, reale, R, 2026), "tredicesima_istruttori")
    registra_malattia(registro, R, ORDINARIA, date(2026, 3, 10), date(2026, 3, 24))
    assert somma(calcola_annuale(registro, reale, R, 2026), "tredicesima_istruttori") == piena
