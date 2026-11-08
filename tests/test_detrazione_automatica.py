"""Detrazione automatica e giorni di servizio nella ritenuta e nel conguaglio (ADR 0019, ticket #93).

Valori e fonti fittizi, sul corpus di test_fiscale (detrazione a richiesta: 55,00 al mese su 1500 al mese). La detrazione
automatica di prova è di 600 annui, rapportata ai giorni di servizio sull'anno e al periodo.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.errori import ErroreCorpus, ErroreFormula
from test_fiscale import (
    ALTRO,
    DETRAZIONE,
    P,
    R,
    TESTO,
    assumi,
    dichiara,
    paga,
    stipendio,
)

IMPOSTA_PROVA = "arrotonda(parametro.aliquota_1 * min(fisco.imponibile, parametro.limite_1 / fisco.periodi) + parametro.aliquota_2 * max(0, fisco.imponibile - parametro.limite_1 / fisco.periodi), 2)"
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


# Ritenuta del mese: detrazione a richiesta e detrazione automatica separate

def corpus_prova(automatica=AUTOMATICA_PROVA):
    return Corpus.da_toml(con_automatica(automatica))


def imposta_di(imponibile, periodi):
    """Imposta di prova: 10% fino a limite_1 (10000) ragguagliato al periodo, 20% oltre."""
    limite = Decimal(10000) / periodi
    return (Decimal("0.1") * min(imponibile, limite) + Decimal("0.2") * max(Decimal(0), imponibile - limite)).quantize(
        Decimal("0.01")
    )


def test_la_detrazione_automatica_si_applica_senza_dichiarazione(registro, orologio):
    corpus = corpus_prova()
    assumi(registro)
    esito, fiscale = paga(registro, orologio, corpus, stipendio(registro, corpus, Mese(2026, 6)), date(2026, 6, 27))
    # automatica del mese: 600 * 1 / 1 / 12 = 50,00 (nella ritenuta del mese i giorni non pesano)
    assert fiscale.ritenuta.valore == imposta_di(Decimal(1500), 12) - Decimal("50.00")


def test_con_la_dichiarazione_si_sommano_le_due_detrazioni(registro, orologio):
    corpus = corpus_prova()
    assumi(registro)
    dichiara(registro, orologio)
    _, fiscale = paga(registro, orologio, corpus, stipendio(registro, corpus, Mese(2026, 6)), date(2026, 6, 27))
    assert fiscale.ritenuta.valore == imposta_di(Decimal(1500), 12) - Decimal("55.00") - Decimal("50.00")
    formula = fiscale.ritenuta.derivazione.formula
    assert DETRAZIONE in formula and AUTOMATICA_PROVA in formula


def test_la_derivazione_dice_quando_la_detrazione_a_richiesta_non_e_applicata(registro, orologio):
    corpus = corpus_prova()
    assumi(registro)
    _, fiscale = paga(registro, orologio, corpus, stipendio(registro, corpus, Mese(2026, 6)), date(2026, 6, 27))
    formula = fiscale.ritenuta.derivazione.formula
    assert "non applicata" in formula and AUTOMATICA_PROVA in formula


def test_le_detrazioni_non_portano_la_ritenuta_sotto_zero(registro, orologio):
    corpus = corpus_prova()
    assumi(registro)
    dichiara(registro, orologio)
    _, fiscale = paga(registro, orologio, corpus, stipendio(registro, corpus, Mese(2026, 6), "100"), date(2026, 6, 27))
    assert fiscale.ritenuta.valore == Decimal("0.00")
