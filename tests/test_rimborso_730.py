"""Il rimborso da 730-4 come importo del rapporto della persona (ticket #71). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Periodo
from paghe.errori import CasoNonModellato, ParametroMancante
from paghe.esito_730_4 import rimborso_730_4

from materiale_proposta import P, R, R2, assumi
from materiale_rimborso import ATTO_730_4, ATTO_RETTIFICA, LUGLIO, corpus_rimborso

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


def test_prima_del_primo_mese_utile_non_c_e_rimborso(registro, corpus):
    assumi(registro)
    registro.registra_esito_730_4(P, D("150.00"), 2025, date(2026, 6, 20), ATTO_730_4)
    assert rimborso_730_4(registro, corpus, R, date(2026, 6, 26)) is None
    assert rimborso_730_4(registro, corpus, R, date(2026, 7, 1)) is not None


def test_senza_il_parametro_del_primo_mese_il_rimborso_non_si_calcola_e_lo_dice(registro):
    assumi(registro)
    registro.registra_esito_730_4(P, D("150.00"), 2025, date(2026, 6, 20), ATTO_730_4)
    with pytest.raises(ParametroMancante, match="rimborso_730_primo_mese"):
        rimborso_730_4(registro, corpus_rimborso(con_parametro=False), R, LUGLIO)


def test_senza_esito_730_4_o_senza_persona_non_c_e_rimborso(registro, corpus):
    assert rimborso_730_4(registro, corpus, R, LUGLIO) is None  # rapporto senza persona
    assumi(registro)
    assert rimborso_730_4(registro, corpus, R, LUGLIO) is None  # persona senza esito


def test_il_rettificativo_da_un_importo_con_la_stessa_chiave_ma_il_nuovo_valore(registro, corpus, orologio):
    assumi(registro)
    registro.registra_esito_730_4(P, D("150.00"), 2025, date(2026, 6, 20), ATTO_730_4)
    primo = rimborso_730_4(registro, corpus, R, LUGLIO)
    orologio.avanza()
    registro.registra_esito_730_4(P, D("120.00"), 2025, date(2026, 7, 10), ATTO_RETTIFICA)
    secondo = rimborso_730_4(registro, corpus, R, LUGLIO)
    assert (secondo.valore, secondo.chiave) == (D("120.00"), primo.chiave)


def test_una_persona_con_piu_rapporti_ferma_il_rimborso_e_nomina_il_caso(registro, corpus):
    assumi(registro)
    assumi(registro, R2, P)
    registro.registra_esito_730_4(P, D("150.00"), 2025, date(2026, 6, 20), ATTO_730_4)
    with pytest.raises(CasoNonModellato, match="più rapporti"):
        rimborso_730_4(registro, corpus, R, LUGLIO)
