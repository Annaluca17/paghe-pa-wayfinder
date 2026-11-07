"""`anche_se`: altre condizioni `tipo=codice` che devono valere insieme ad `applica_se` (ticket #73). Dati fittizi."""

from datetime import date

import pytest

from paghe import Corpus, Mese, calcola
from paghe.errori import ErroreCorpus

from conftest import CORPUS_BASE

REGOLA = """
[[regola]]
istituto = "quota"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:quota"
formula = "parametro.aliquota"
maturazione = "evento"
applica_se = "carica=sindaco"
anche_se = {anche_se}
"""


def corpus(anche_se='["condizione=libera", "cassa=speciale"]'):
    return Corpus.da_toml(CORPUS_BASE + REGOLA.format(anche_se=anche_se))


@pytest.mark.parametrize("scritto", ['["senza_uguale"]', '["=codice"]', '["tipo="]', '[" tipo=codice"]'])
def test_una_condizione_aggiuntiva_malformata_e_rifiutata(scritto):
    with pytest.raises(ErroreCorpus, match="anche_se"):
        corpus(scritto)


def test_anche_se_senza_applica_se_e_rifiutata():
    testo = CORPUS_BASE + REGOLA.format(anche_se='["a=b"]').replace('applica_se = "carica=sindaco"\n', "")
    with pytest.raises(ErroreCorpus, match="anche_se richiede applica_se"):
        Corpus.da_toml(testo)


def test_la_regola_si_applica_solo_se_valgono_tutte_le_condizioni(registro):
    c = corpus()
    registro.collega_rapporto("R", "P", date(2026, 1, 1))
    registro.registra_codice("R", "carica", "sindaco", date(2026, 1, 1))
    registro.registra_codice("R", "condizione", "libera", date(2026, 1, 1))
    assert not [i for i in calcola(registro, c, "R", Mese(2026, 3)) if i.istituto == "quota"]
    registro.registra_codice("R", "cassa", "speciale", date(2026, 1, 1))
    (riga,) = [i for i in calcola(registro, c, "R", Mese(2026, 3)) if i.istituto == "quota"]
    assert {f.tipo for f in riga.derivazione.fatti} == {"carica", "condizione", "cassa"}


def test_la_versione_del_corpus_cambia_con_le_condizioni_aggiuntive():
    assert corpus().versione != corpus('["condizione=libera"]').versione
