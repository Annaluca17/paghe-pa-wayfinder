"""Rata del mese delle addizionali dell'anno prima (ticket #85, ADR 0029). Dati fittizi.

Dal 2026: regionale dovuta 240,00 e comunale dovuta 99,00 (vedi materiale_addizionali), nessun acconto trattenuto.
Dal mese dopo il conguaglio fino a novembre compreso, la rata e' il residuo diviso i mesi rimasti:
regionale 240 / 11 = 21,8181..., rata 21,82 (al centesimo) e i centesimi di differenza sull'ultima (21,80); comunale 99 / 11 = 9,00.
"""

from datetime import date
from decimal import Decimal

import pytest

from materiale_addizionali import anno_di_paghe, assumi_a, corpus_addizionali, paga, per_istituto

D = Decimal
REG, COM = "addizionale_regionale", "addizionale_comunale_saldo"


@pytest.fixture
def corpus():
    return corpus_addizionali()


@pytest.fixture
def dal_2027(registro, orologio, corpus):
    """Un anno 2026 completo, poi i pagamenti del 2027 uno alla volta con `paga_il(mese)`."""
    assumi_a(registro)
    anno_di_paghe(registro, orologio, corpus)
    return lambda mese, giorno=27: paga(registro, orologio, corpus, date(2027, mese, giorno))


def rate(fiscale):
    return per_istituto(fiscale.addizionali)


def test_gennaio_trattiene_un_undicesimo_del_residuo_di_ciascuna_addizionale(dal_2027):
    r = rate(dal_2027(1))
    assert (r[REG].valore, r[COM].valore) == (D("21.82"), D("9.00"))
    assert {(i.anno_imposta, i.derivazione.maturazione) for i in r.values()} == {(2026, "addizionale")}


def test_la_rata_dice_da_dove_viene(dal_2027):
    regionale = rate(dal_2027(1))[REG]
    assert regionale.derivazione.riferimento.startswith("fittizio:addizionali")
    assert [i.istituto for i in regionale.derivazione.importi] == ["addizionale_regionale_dovuta"]
    assert regionale.derivazione.importi[0].valore == D("240.00")
    assert {p.nome: p.valore for p in regionale.derivazione.parametri} == {"addizionale_mese_ultima_rata": D("11")}


def test_le_rate_restano_uguali_e_i_centesimi_finiscono_nell_ultima(dal_2027):
    regionali = [rate(dal_2027(mese))[REG].valore for mese in range(1, 12)]
    assert regionali[:-1] == [D("21.82")] * 10 and regionali[-1] == D("21.80")
    assert sum(regionali) == D("240.00")


def test_dopo_novembre_nulla(dal_2027):
    for mese in range(1, 12):
        dal_2027(mese)
    assert dal_2027(12).addizionali == ()


def test_un_mese_senza_pagamento_si_spalma_da_solo_sui_successivi(dal_2027):
    dal_2027(1)
    # nessun pagamento a febbraio: a marzo restano 240 - 21,82 = 218,18 da dividere per 9 mesi (marzo-novembre)
    assert rate(dal_2027(3))[REG].valore == D("24.24")


def test_una_sola_rata_per_persona_e_mese_sul_primo_pagamento(dal_2027):
    assert dal_2027(1, 15).addizionali != ()
    assert dal_2027(1, 27).addizionali == ()


def test_nessuna_rata_nel_mese_del_conguaglio_ne_prima(registro, orologio, corpus):
    assumi_a(registro)
    fiscali = anno_di_paghe(registro, orologio, corpus)
    assert all(f.addizionali == () for f in fiscali)  # nel 2026 non c'e' nulla da trattenere: dicembre, oltre novembre
