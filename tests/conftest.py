"""Dati esclusivamente fittizi: nessun valore qui è una norma reale."""

from datetime import UTC, datetime, timedelta

import pytest

from paghe import Corpus, Registro

CORPUS_BASE = """
[[parametro]]
nome = "aliquota"
[[parametro.vigenza]]
dal = 2026-01-01
valore = "0.10"
riferimento = "fittizio:fonte-aliquota"

[[regola]]
istituto = "compenso"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:art-1"
formula = "fatto.compenso_mensile"

[[regola]]
istituto = "ritenuta"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:art-2"
formula = "arrotonda(importo.compenso * parametro.aliquota, 2)"
"""


class Orologio:
    def __init__(self):
        self.ora = datetime(2026, 1, 1, 9, 0, tzinfo=UTC)

    def __call__(self):
        return self.ora

    def vai(self, mese, giorno, anno=2026):
        self.ora = datetime(anno, mese, giorno, 9, 0, tzinfo=UTC)
        return self.ora

    def avanza(self, secondi=1):
        self.ora += timedelta(seconds=secondi)
        return self.ora


@pytest.fixture
def orologio():
    return Orologio()


@pytest.fixture
def registro(orologio):
    r = Registro(orologio=orologio)
    yield r
    r.chiudi()


@pytest.fixture
def corpus():
    return Corpus.da_toml(CORPUS_BASE)
