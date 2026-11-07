"""Il rimborso 730 al lavoratore e' una riga sola: sul netto, verso il beneficiario, con canale accredito (ticket #71, ADR 0023).

La delega lo legge dalla natura della riga, qualunque sia il canale, e lo porta come credito del sostituto. Dati fittizi.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.delega import costruisci_delega

from materiale_delega import R, R2, corpus_delega, dati_ente, paga_a_mano, riga_a_mano

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal

CHIAVE_100E = ("F", "100E", "", "", "0002", "2026")
CHIAVE_150E_2025 = ("F", "150E", "", "", "", "2025")


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))


def test_il_rimborso_sul_netto_e_a_credito_nella_delega_con_l_anno_dei_redditi(registro, corpus, orologio, ente):
    righe = [
        riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100"),
        riga_a_mano(corpus, VALUTA, "rimborso_730_sul_netto", "40", anno_imposta=2025),
    ]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    d = costruisci_delega(registro, corpus, FEB)
    assert {r.chiave: (r.debito, r.credito) for r in d.righe} == {
        CHIAVE_100E: (D("100"), D("0")),
        CHIAVE_150E_2025: (D("0"), D("40")),
    }
    assert d.saldo == D("60") and d.pronta
