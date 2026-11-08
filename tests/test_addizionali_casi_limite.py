"""Casi limite delle addizionali, dalla rilettura del ticket #85 (ADR 0029). Dati fittizi (vedi materiale_addizionali)."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import conguaglio_per_differenza
from paghe.errori import CasoNonModellato

from materiale_addizionali import anno_di_paghe, assumi_a, corpus_addizionali, domicilio, paga, per_istituto
from materiale_proposta import R

D = Decimal
REG, COM, ACC = "addizionale_regionale", "addizionale_comunale_saldo", "addizionale_comunale_acconto"


@pytest.fixture
def corpus():
    return corpus_addizionali()


def test_le_rate_del_saldo_chiudono_esattamente_a_novembre(registro, orologio, corpus):
    assumi_a(registro)
    anno_di_paghe(registro, orologio, corpus)
    rate = [per_istituto(paga(registro, orologio, corpus, date(2027, mese, 27)).addizionali) for mese in range(1, 13)]
    regionali = [r[REG].valore for r in rate if REG in r]
    assert len(regionali) == 11 and REG not in rate[11]
    assert sum(regionali) == D("240.00")
    assert max(regionali) - min(regionali) <= D("0.05")


def test_con_il_domicilio_cambiato_al_primo_gennaio_l_acconto_va_al_comune_nuovo_con_le_sue_aliquote_dell_anno_prima(
    registro, orologio, corpus
):
    """Il saldo 2026 resta del comune X001 (99,00); l'acconto 2027 è del comune del 1° gennaio 2027, X002, con aliquota e
    soglia 2026 di X002: 0,6% su 18000 = 108,00; 30% = 32,40; in nove rate 3,60."""
    assumi_a(registro)
    anno_di_paghe(registro, orologio, corpus)
    domicilio(registro, "X002", "97", dal=date(2027, 1, 1))
    for mese in (1, 2):
        paga(registro, orologio, corpus, date(2027, mese, 27))
    marzo = per_istituto(paga(registro, orologio, corpus, date(2027, 3, 27)).addizionali)
    assert marzo[COM].valore == D("9.00")
    assert marzo[ACC].valore == D("3.60")


def test_un_domicilio_corretto_dopo_il_conguaglio_ferma_il_conguaglio_per_differenza(registro, orologio, corpus):
    """L'IRPEF non cambia, ma le addizionali sì: il conguaglio per differenza non le ricalcola ancora, quindi si ferma."""
    assumi_a(registro)
    anno_di_paghe(registro, orologio, corpus)
    domicilio(registro, "X002", "97", dal=date(2025, 6, 1))
    with pytest.raises(CasoNonModellato, match="addizional"):
        conguaglio_per_differenza(registro, corpus, R, 2026, date(2027, 2, 26))
