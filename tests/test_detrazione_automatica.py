"""Detrazione automatica e giorni di servizio nella ritenuta e nel conguaglio (ADR 0019, ticket #93).

Valori e fonti fittizi. La regola di prova ha scaglioni 10% fino a 10000 e 20% oltre, la detrazione a richiesta di
1200 annui, e una detrazione automatica di 600 annui rapportata ai giorni di servizio sull'anno.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.errori import ErroreCorpus, ErroreFormula
from test_fiscale import (
    ALTRO,
    CF,
    P,
    R,
    TESTO,
    assumi,
    dichiara,
    paga,
    stipendio,
)

IMPOSTA_PROVA = "arrotonda(parametro.aliquota_1 * min(fisco.imponibile, parametro.limite_1 / fisco.periodi) + parametro.aliquota_2 * max(0, fisco.imponibile - parametro.limite_1 / fisco.periodi), 2)"
DETRAZIONE_PROVA = "arrotonda(parametro.detrazione_annua / fisco.periodi, 2)"
AUTOMATICA_PROVA = "arrotonda(parametro.detrazione_annua / 2 * fisco.giorni / fisco.giorni_anno / fisco.periodi, 2)"


def con_automatica(formula, imposta=None, detrazione=None):
    testo = TESTO
    if imposta is not None:
        testo = testo.replace(
            testo[testo.index("imposta = '''") : testo.index("detrazione = '''")], f"imposta = '''{imposta}'''\n"
        )
    marca = "detrazione_richiesta = \"lavoro_dipendente\"\n"
    assert marca in testo
    return testo.replace(marca, marca + f"detrazione_automatica = '''{formula}'''\n")


def test_la_regola_legge_la_detrazione_automatica():
    corpus = Corpus.da_toml(con_automatica(AUTOMATICA_PROVA))
    regola = corpus.regola_ritenuta(date(2026, 6, 1))
    assert regola.detrazione_automatica == AUTOMATICA_PROVA
    assert {"detrazione_annua"} <= regola.parametri


def test_senza_detrazione_automatica_vale_zero():
    regola = Corpus.da_toml(TESTO).regola_ritenuta(date(2026, 6, 1))
    assert regola.detrazione_automatica == "0"


@pytest.mark.parametrize(
    "formula",
    ["fatto.x", "importo.x", "base.x", "fisco.sconosciuto", "parametro.inesistente", "fisco.imponibile < 3"],
)
def test_la_detrazione_automatica_ha_gli_stessi_controlli_delle_altre_formule(formula):
    with pytest.raises((ErroreCorpus, ErroreFormula)):
        Corpus.da_toml(con_automatica(formula))


def test_giorni_e_giorni_anno_sono_ammessi_come_fisco():
    Corpus.da_toml(con_automatica("fisco.giorni / fisco.giorni_anno"))


def test_la_versione_del_corpus_cambia_con_la_detrazione_automatica():
    assert Corpus.da_toml(TESTO).versione != Corpus.da_toml(con_automatica(AUTOMATICA_PROVA)).versione
