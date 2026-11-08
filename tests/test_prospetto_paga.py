"""Prospetto paga (ticket #86, ADR 0030): vista di un rapporto in un pagamento eseguito, letta dal suo esito pagato.

Corpus reale piu' le dichiarazioni fittizie del mese di prova (composizione, regimi del prospetto). Persone e importi di
fantasia; codici fiscali con carattere di controllo valido.
"""

from datetime import date
from pathlib import Path

import pytest

from paghe import Corpus

RADICE = Path(__file__).resolve().parent.parent
REALE = (RADICE / "corpus" / "funzioni-locali-cpdel.toml").read_text(encoding="utf-8")
FITTIZIO = (RADICE / "prove" / "mese_di_prova" / "corpus_fittizio.toml").read_text(encoding="utf-8")
PAGAMENTO = date(2026, 11, 27)


@pytest.fixture(scope="module")
def corpus():
    return Corpus.da_toml(REALE + "\n" + FITTIZIO, reale=False)


def test_il_corpus_dichiara_per_regime_quale_fatto_da_la_posizione(corpus):
    dichiarazioni = corpus.outputs("prospetto_paga", PAGAMENTO)
    assert {d.regime: d.posizione for d in dichiarazioni} == {
        "dipendenti": "qualifica",
        "amministratori": "carica",
        "collaboratori": "incarico",
    }
