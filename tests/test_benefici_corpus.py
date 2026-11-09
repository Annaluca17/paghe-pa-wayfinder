"""Regola dei benefici della persona nel corpus (ticket #95, ADR 0019). Valori e fonti fittizi."""

from datetime import date

import pytest

from paghe import Corpus
from paghe.errori import ErroreCorpus, ErroreFormula

from materiale_benefici import TESTO_BENEFICI, beneficio, corpus_benefici, parametri_benefici
from test_fiscale import TESTO


def test_la_regola_dei_benefici_si_legge_dal_corpus():
    regola = corpus_benefici().regola_benefici(date(2026, 6, 1))
    assert regola.istituto_somma_esente == "somma_esente"
    assert regola.categorie_trattamento_integrativo == ("lavoro_dipendente",)
    assert {"se_soglia_1", "ti_importo", "recupero_soglia", "recupero_rate_ti"} <= set(regola.parametri)


def test_senza_la_regola_il_corpus_non_calcola_i_benefici():
    assert Corpus.da_toml(TESTO).regola_benefici(date(2026, 6, 1)) is None


def test_la_versione_del_corpus_cambia_con_i_benefici():
    assert Corpus.da_toml(TESTO).versione != Corpus.da_toml(TESTO_BENEFICI).versione


@pytest.mark.parametrize("formula", ["fatto.x", "importo.x", "base.x", "fisco.sconosciuto", "parametro.inesistente"])
def test_le_formule_dei_benefici_hanno_i_controlli_delle_altre_formule(formula):
    with pytest.raises((ErroreCorpus, ErroreFormula)):
        Corpus.da_toml(TESTO + parametri_benefici() + beneficio(somma=formula))


def test_una_categoria_ignota_ferma_il_corpus():
    with pytest.raises(ErroreCorpus, match="categoria ignota"):
        Corpus.da_toml(TESTO + parametri_benefici() + beneficio(categorie_ti='["inesistente"]'))


def test_i_benefici_vogliono_la_ritenuta_di_cui_leggono_imposta_e_detrazione():
    senza_ritenuta = TESTO[: TESTO.index("[[ritenuta]]")]
    with pytest.raises(ErroreCorpus, match="ritenuta"):
        Corpus.da_toml(senza_ritenuta + parametri_benefici() + beneficio())
