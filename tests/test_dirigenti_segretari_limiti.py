"""Casi limite della PR A del ticket #73, scritti nella rilettura: condizione del fermo `manca`, fasce fuori elenco, fatti
del segretario su un rapporto che non e' di un segretario. Persone e rapporti di fantasia."""

from datetime import date

import pytest

from paghe import calcola
from paghe.errori import CasoNonModellato

from tests.test_dirigenti_segretari import ATTO, R, importi, reale, titolare  # noqa: F401
from paghe import Mese


def test_un_dipendente_del_comparto_senza_fascia_non_e_fermato(registro, reale):
    titolare(registro, "funzionari")
    assert "tabellare_funzionari" in importi(registro, reale, Mese(2026, 11))


def test_segretario_cessato_a_meta_mese_con_la_fascia_fino_alla_cessazione_non_e_fermato(registro, reale):
    titolare(registro, "segretario", al=date(2026, 11, 15))
    registro.registra_codice(R, "fascia_segretario", "B", date(2026, 1, 1), date(2026, 11, 15), atto=ATTO)
    assert "tabellare_segretario_b" in importi(registro, reale, Mese(2026, 11))


def test_una_fascia_fuori_elenco_non_lascia_il_segretario_senza_tabellare_in_silenzio(registro, reale):
    titolare(registro, "segretario")
    registro.registra_codice(R, "fascia_segretario", "D", date(2026, 1, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match="fascia_segretario"):
        calcola(registro, reale, R, Mese(2026, 11))


def test_una_fascia_su_un_rapporto_del_comparto_non_aggiunge_un_secondo_tabellare(registro, reale):
    titolare(registro, "funzionari")
    registro.registra_codice(R, "fascia_segretario", "B", date(2026, 1, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match="fascia_segretario"):
        calcola(registro, reale, R, Mese(2026, 11))


def test_la_posizione_del_segretario_su_un_dirigente_non_si_somma_in_silenzio(registro, reale):
    titolare(registro, "dirigente")
    registro.registra_fatto(R, "posizione_annua_segretario", "12000.00", date(2026, 1, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match="posizione_annua_segretario"):
        calcola(registro, reale, R, Mese(2026, 11))


def test_la_posizione_del_dirigente_su_un_segretario_ferma_il_calcolo(registro, reale):
    titolare(registro, "segretario")
    registro.registra_codice(R, "fascia_segretario", "B", date(2026, 1, 1), atto=ATTO)
    registro.registra_fatto(R, "posizione_annua_dirigente", "20000.00", date(2026, 1, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match="posizione_annua_dirigente"):
        calcola(registro, reale, R, Mese(2026, 11))
