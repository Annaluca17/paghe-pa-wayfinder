"""se(condizione, allora, altrimenti): un solo confronto, mai fuori da se (ADR 0002, ticket #93)."""

from decimal import Decimal

import pytest

from paghe.errori import ErroreFormula
from paghe.formula import riferimenti, valuta


def letti(origine, nome):
    return {"r": Decimal("15000"), "s": Decimal("10")}[nome]


@pytest.mark.parametrize(
    ("formula", "atteso"),
    [
        ("se(fatto.r <= 15000, 1955, 3100)", "1955"),
        ("se(fatto.r < 15000, 1955, 3100)", "3100"),
        ("se(fatto.r > 15000, 1, 2)", "2"),
        ("se(fatto.r >= 15000, 1, 2)", "1"),
        ("se(fatto.r > fatto.s * 1000, 1 + 1, 7)", "2"),
        ("se(fatto.s < 20, se(fatto.s < 5, 1, 2), 3)", "2"),
        ("1 + se(fatto.s < 20, 4, 5)", "5"),
    ],
)
def test_se_sceglie_il_ramo_dal_confronto(formula, atteso):
    assert valuta(formula, letti) == Decimal(atteso)


def test_se_valuta_solo_il_ramo_scelto():
    # Il ramo non scelto dividerebbe per zero: non deve essere valutato.
    assert valuta("se(fatto.s > 0, 1, 1 / 0)", letti) == Decimal("1")


def test_se_dichiara_i_riferimenti_di_tutti_i_suoi_argomenti():
    trovati = riferimenti("se(fatto.a < parametro.p, importo.x, base.y)")
    assert (trovati.fatti, trovati.parametri, trovati.importi, trovati.basi) == ({"a"}, {"p"}, {"x"}, {"y"})


@pytest.mark.parametrize(
    "formula",
    [
        "fatto.r < 3",
        "1 + (fatto.r < 3)",
        "min(fatto.r < 3, 1)",
        "se(fatto.r, 1, 2)",
        "se(fatto.r == 3, 1, 2)",
        "se(fatto.r != 3, 1, 2)",
        "se(1 < fatto.r < 3, 1, 2)",
        "se(fatto.r < 3, 1)",
        "se(fatto.r < 3, 1, 2, 3)",
        "se(fatto.r < 3, 1, 2.5)",
        "se(fatto.r < 3 and fatto.s < 3, 1, 2)",
        "se(fatto.r in 3, 1, 2)",
    ],
)
def test_se_e_confronti_fuori_posto_rifiutati(formula):
    with pytest.raises(ErroreFormula):
        riferimenti(formula)


@pytest.mark.parametrize(
    ("formula", "atteso"),
    [
        ("tronca(3000 / 13000, 4)", "0.2307"),  # 0,230769...: si prendono le prime quattro cifre, senza arrotondare
        ("tronca(21999 / 22000, 4)", "0.9999"),
        ("tronca(1 / 2, 4)", "0.5000"),
        ("tronca(fatto.r, 0)", "15000"),
    ],
)
def test_tronca_prende_le_prime_cifre_decimali(formula, atteso):
    assert valuta(formula, letti) == Decimal(atteso)


def test_tronca_vuole_decimali_interi_non_negativi():
    with pytest.raises(ErroreFormula):
        valuta("tronca(fatto.r, -1)", letti)
