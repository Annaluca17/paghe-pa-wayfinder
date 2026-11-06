from datetime import date
from decimal import Decimal

import pytest

from conftest import CORPUS_BASE
from paghe import Corpus, Mese
from paghe.errori import ErroreCorpus, ErroreFormula, ParametroMancante, ValiditaNonUniforme
from paghe.formula import riferimenti, valuta


def valori(origine, nome):
    return {"a": Decimal("10"), "b": Decimal("3")}[nome]


@pytest.mark.parametrize(
    ("formula", "atteso"),
    [
        ("fatto.a + importo.b", "13"),
        ("-fatto.a * 2", "-20"),
        ("min(fatto.a, importo.b)", "3"),
        ("max(fatto.a, importo.b, 20)", "20"),
        ("arrotonda(fatto.a / importo.b, 2)", "3.33"),
    ],
)
def test_formula_valutata(formula, atteso):
    assert valuta(formula, valori) == Decimal(atteso)


def test_arrotondamento_solo_se_dichiarato_e_mezzo_in_su():
    assert valuta("arrotonda(fatto.a, 0)", lambda *_: Decimal("2.5")) == Decimal("3")
    assert valuta("fatto.a / importo.b", valori) != Decimal("3.33")


@pytest.mark.parametrize(
    "formula",
    [
        "__import__('os').system('x')",
        "open('x')",
        "fatto.a.__class__",
        "fatto.a ** 2",
        "(lambda: 1)()",
        "altro.a",
        "fatto.a if fatto.a else 1",
        "fatto.a * 0.1",
        "True",
        "arrotonda(fatto.a, -1)",
        "arrotonda(fatto.a, importo.b)",
        "",
        "1 +",
    ],
)
def test_formula_rifiutata(formula):
    with pytest.raises(ErroreFormula):
        riferimenti(formula)


def test_divisione_per_zero_non_produce_importo():
    with pytest.raises(ErroreFormula):
        valuta("fatto.a / 0", valori)


def test_riferimenti_dichiarati():
    letti = riferimenti("fatto.x + parametro.y * importo.z")
    assert (letti.fatti, letti.parametri, letti.importi) == ({"x"}, {"y"}, {"z"})


def test_riferimento_obbligatorio_su_regola_e_parametro():
    with pytest.raises(ErroreCorpus, match="riferimento"):
        Corpus.da_toml(CORPUS_BASE.replace('riferimento = "fittizio:art-1"', 'riferimento = " "'))
    with pytest.raises(ErroreCorpus, match="riferimento"):
        Corpus.da_toml(CORPUS_BASE.replace('riferimento = "fittizio:fonte-aliquota"', 'riferimento = ""'))
    with pytest.raises(ErroreCorpus):
        Corpus.da_toml(CORPUS_BASE.replace('riferimento = "fittizio:art-1"\n', ""))


def regola(istituto, formula, dal="2026-01-01", extra=""):
    return f"""
[[regola]]
istituto = "{istituto}"
versione = 1
dal = {dal}
riferimento = "fittizio:prova"
formula = "{formula}"
{extra}
"""


def test_cicli_rifiutati():
    with pytest.raises(ErroreCorpus, match="Ciclo"):
        Corpus.da_toml(regola("a", "importo.b") + regola("b", "importo.c") + regola("c", "importo.a"))
    with pytest.raises(ErroreCorpus, match="Ciclo"):
        Corpus.da_toml(regola("a", "importo.a"))


def test_riferimenti_ignoti_rifiutati():
    with pytest.raises(ErroreCorpus, match="parametri ignoti"):
        Corpus.da_toml(regola("a", "parametro.ignoto"))
    with pytest.raises(ErroreCorpus, match="importi senza regola"):
        Corpus.da_toml(regola("a", "importo.ignoto"))


def test_vigenze_sovrapposte_rifiutate():
    testo = regola("a", "fatto.x") + regola("a", "fatto.x", dal="2026-06-01")
    with pytest.raises(ErroreCorpus, match="sovrapposte"):
        Corpus.da_toml(testo)


@pytest.mark.parametrize("valore", ["0.1", '"abc"', '"NaN"', '"Infinity"'])
def test_valore_parametro_non_ammesso(valore):
    with pytest.raises(ErroreCorpus):
        Corpus.da_toml(CORPUS_BASE.replace('valore = "0.10"', f"valore = {valore}"))


def test_versione_corpus_deterministica_e_sensibile_al_contenuto(corpus):
    assert Corpus.da_toml(CORPUS_BASE).versione == corpus.versione
    variato = Corpus.da_toml(CORPUS_BASE.replace('"0.10"', '"0.11"'))
    assert variato.versione != corpus.versione


def test_parametro_vigenza_per_mese():
    parametri = """
[[parametro]]
nome = "p"
[[parametro.vigenza]]
dal = 2026-01-01
valore = "1"
riferimento = "fittizio:a"
[[parametro.vigenza]]
dal = 2026-03-01
valore = "2"
riferimento = "fittizio:b"
[[parametro.vigenza]]
dal = 2026-05-15
valore = "3"
riferimento = "fittizio:c"
"""
    p = Corpus.da_toml(parametri).parametro("p")
    assert p.vigenza_per(Mese(2026, 2)).valore == 1
    assert p.vigenza_per(Mese(2026, 3)).riferimento == "fittizio:b"
    with pytest.raises(ParametroMancante):
        p.vigenza_per(Mese(2025, 12))
    with pytest.raises(ValiditaNonUniforme):
        p.vigenza_per(Mese(2026, 5))


def test_regola_che_cambia_dentro_il_mese_non_si_applica():
    testo = regola("a", "fatto.x", extra="al = 2026-03-15") + regola("a", "fatto.y", dal="2026-03-16")
    corpus = Corpus.da_toml(testo)
    assert corpus.regola_per("a", Mese(2026, 2)).dal == date(2026, 1, 1)
    assert corpus.regola_per("a", Mese(2025, 12)) is None
    with pytest.raises(ValiditaNonUniforme):
        corpus.regola_per("a", Mese(2026, 3))
