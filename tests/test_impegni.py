"""Fatto contabile dell'impegno, disponibilità e abbinamento (ADR 0031). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe.errori import ErroreRegistro
from paghe.impegni import AttoPresupposto, impegni_noti

from materiale_impegni import PIANO, impegno

# Fatto contabile

def test_il_fatto_contabile_porta_numero_esercizio_classificazione_atto_e_disponibilita(registro):
    atto = AttoPresupposto("sottoscrizione_integrativo", "ente:ente_di_prova:contratto:2026-03-01;7")
    impegno(registro, numero=12, esercizio=2026, disponibilita="5000.50", data=date(2026, 3, 1), atto=atto)
    noto = impegni_noti(registro, registro.adesso())[(2026, 12)]
    assert (noto.numero, noto.esercizio, noto.piano_dei_conti, noto.missione, noto.programma) == (12, 2026, PIANO, "01", "02")
    assert (noto.atto, noto.disponibilita, noto.data) == (atto, Decimal("5000.50"), date(2026, 3, 1))


def test_l_impegno_automatico_non_ha_atto(registro):
    impegno(registro)
    assert impegni_noti(registro, registro.adesso())[(2026, 1)].atto is None


def test_lo_stesso_identificativo_con_lo_stesso_contenuto_non_ha_effetto(registro, orologio):
    impegno(registro)
    orologio.avanza()
    impegno(registro)
    assert len(registro.eventi("fatto_contabile_impegno", registro.adesso())) == 1


def test_lo_stesso_identificativo_con_contenuto_diverso_e_un_errore_e_non_cambia_nulla(registro, orologio):
    impegno(registro, disponibilita="10000")
    orologio.avanza()
    with pytest.raises(ErroreRegistro, match="contenuto diverso"):
        impegno(registro, disponibilita="9000")
    assert impegni_noti(registro, registro.adesso())[(2026, 1)].disponibilita == Decimal("10000")


def test_per_lo_stesso_impegno_vale_la_disponibilita_con_la_data_piu_recente(registro, orologio):
    impegno(registro, chiave="IMP-1-A", disponibilita="10000", data=date(2026, 1, 1))
    impegno(registro, chiave="IMP-1-C", disponibilita="7000", data=date(2026, 6, 1))
    impegno(registro, chiave="IMP-1-B", disponibilita="9000", data=date(2026, 3, 1))  # arriva dopo ma e' piu' vecchia
    noto = impegni_noti(registro, registro.adesso())[(2026, 1)]
    assert (noto.disponibilita, noto.data) == (Decimal("7000"), date(2026, 6, 1))


def test_lo_stesso_numero_in_esercizi_diversi_e_un_altro_impegno(registro):
    impegno(registro, chiave="IMP-A", numero=1, esercizio=2025)
    impegno(registro, chiave="IMP-B", numero=1, esercizio=2026)
    assert set(impegni_noti(registro, registro.adesso())) == {(2025, 1), (2026, 1)}


def test_la_conoscenza_dell_impegno_dipende_dall_istante(registro, orologio):
    prima = orologio()
    orologio.avanza()
    impegno(registro)
    assert impegni_noti(registro, prima) == {}


@pytest.mark.parametrize(
    ("campo", "valore"),
    [
        ("disponibilita", "-1"),
        ("disponibilita", "abc"),
        ("disponibilita", 1.5),
        ("piano", "U.1.01"),
        ("numero", 0),
        ("missione", "1"),
        ("programma", "AB"),
    ],
)
def test_un_fatto_contabile_non_valido_e_rifiutato(registro, campo, valore):
    with pytest.raises(ErroreRegistro):
        impegno(registro, **{campo: valore})
    assert impegni_noti(registro, registro.adesso()) == {}
