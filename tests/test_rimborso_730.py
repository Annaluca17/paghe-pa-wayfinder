"""Il rimborso da 730-4 come importo del rapporto della persona (ticket #71). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Periodo
from paghe.errori import ParametroMancante
from paghe.esito_730_4 import rimborso_730_4

from materiale_proposta import P, R, assumi
from materiale_rimborso import ATTO_730_4, LUGLIO, corpus_rimborso

D = Decimal


@pytest.fixture
def corpus():
    return corpus_rimborso()


def test_il_rimborso_e_un_importo_del_rapporto_con_l_anno_dei_redditi_dichiarati(registro, corpus):
    assumi(registro)
    fatto = registro.registra_esito_730_4(P, D("150.00"), 2025, date(2026, 6, 20), ATTO_730_4)
    importo = rimborso_730_4(registro, corpus, R, LUGLIO)
    assert (importo.rapporto, importo.istituto, importo.valore, importo.anno_imposta) == (R, "rimborso_730_4", D("150.00"), 2025)
    assert importo.periodo == Periodo(date(2025, 1, 1), date(2025, 12, 31))
    assert importo.derivazione.fatti == (fatto,)
    assert [(p.nome, p.valore) for p in importo.derivazione.parametri] == [("rimborso_730_primo_mese", D("7"))]
