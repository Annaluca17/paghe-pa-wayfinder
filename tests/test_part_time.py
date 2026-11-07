"""Part-time: trattamento dichiarato dall'istituto, calcolo mensilizzato, programmazione (ADR 0026, ticket #72).

Valori e fonti fittizi: nessun valore qui è una norma.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, Periodo, calcola
from paghe.errori import CasoNonModellato, ErroreCorpus, FattoMancante

R = "RAPPORTO-1"
NOVEMBRE = Mese(2026, 11)

BASE = """
[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "26"
riferimento = "fittizio:d"

[[regola]]
istituto = "stipendio"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio"
formula = "fatto.mensile"
maturazione = "giorni"
applica_se = "mensile"
conteggio = "lun_sab"
divisore = "d"
decimali = 2
"""


def dichiarazione(trattamento="proporzionale", istituto="stipendio", dal="2020-01-01", extra=""):
    return f"""
[[part_time]]
istituto = "{istituto}"
trattamento = "{trattamento}"
dal = {dal}
riferimento = "fittizio:part-time-{istituto}"
{extra}
"""


def corpus_con(*dichiarazioni, base=BASE):
    return Corpus.da_toml(base + "".join(dichiarazioni))


def test_un_istituto_dichiara_il_trattamento_nel_part_time():
    corpus = corpus_con(dichiarazione("proporzionale"))
    voce = corpus.trattamento_part_time("stipendio", date(2026, 11, 1))
    assert voce.trattamento == "proporzionale"
    assert voce.riferimento == "fittizio:part-time-stipendio"
    assert corpus.trattamento_part_time("altro", date(2026, 11, 1)) is None
