"""Domicilio fiscale della persona (ticket #85, ADR 0029): fatto datato con il comune e la regione. Dati fittizi."""

from datetime import date

import pytest

from paghe import Atto
from paghe.addizionali import domicilio_fiscale
from paghe.errori import ErroreRegistro

from materiale_proposta import P

ATTO = Atto("ente:ente_di_prova:comunicazione.domicilio:2025-12-10;1", date(2025, 12, 10))


def test_il_domicilio_vigente_al_1_gennaio_porta_il_codice_catastale_e_il_codice_regione(registro):
    registro.registra_domicilio_fiscale(P, "X001", "98", date(2025, 6, 1), atto=ATTO)
    domicilio = domicilio_fiscale(registro, P, date(2026, 1, 1), registro.adesso())
    assert (domicilio.comune, domicilio.regione) == ("X001", "98")
    assert domicilio.fatto.soggetto == "persona" and domicilio.fatto.atto == ATTO


def test_senza_domicilio_non_c_e_nulla_da_leggere(registro):
    assert domicilio_fiscale(registro, P, date(2026, 1, 1), registro.adesso()) is None


def test_conta_il_domicilio_al_1_gennaio_non_quello_di_dopo(registro, orologio):
    registro.registra_domicilio_fiscale(P, "X001", "98", date(2025, 6, 1), date(2026, 3, 31))
    orologio.avanza()
    registro.registra_domicilio_fiscale(P, "X002", "97", date(2026, 4, 1))
    assert domicilio_fiscale(registro, P, date(2026, 1, 1), registro.adesso()).comune == "X001"
    assert domicilio_fiscale(registro, P, date(2027, 1, 1), registro.adesso()).comune == "X002"


@pytest.mark.parametrize("comune, regione", [("", "98"), ("X001", " "), ("X001", "")])
def test_un_domicilio_senza_comune_o_senza_regione_e_rifiutato(registro, comune, regione):
    with pytest.raises(ErroreRegistro, match="Domicilio fiscale"):
        registro.registra_domicilio_fiscale(P, comune, regione, date(2026, 1, 1))
