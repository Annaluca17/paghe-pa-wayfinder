"""Condizione di proposta: un fatto che il corpus richiede perche' l'importo entri in una versione (ticket #73, ADR 0015).

Dati esclusivamente fittizi. Il caso e' l'attestazione della prestazione di una rata di collaborazione."""

from datetime import date

import pytest

from paghe import Corpus, Mese
from paghe.errori import ErroreCorpus
from paghe.proposta import emetti_versione

from materiale_proposta import CORPUS_PROPOSTA, P, P2, R, R2, assumi, stipendio

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
CONDIZIONE = """
[[condizione_di_proposta]]
istituto = "stipendio"
fatto = "attestazione_prestazione"
dal = 2020-01-01
riferimento = "fittizio:attestazione-stipendio"
"""


@pytest.fixture
def corpus_c():
    return Corpus.da_toml(CORPUS_PROPOSTA + CONDIZIONE)


def test_un_importo_senza_il_fatto_richiesto_resta_calcolato_ma_fuori_dalla_versione(registro, corpus_c, orologio):
    assumi(registro, R, P)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus_c, FEB, rapporto=R) + stipendio(registro, corpus_c, FEB, rapporto=R2)
    registro.registra_codice(R2, "attestazione_prestazione", "si", FEB.primo_giorno, FEB.ultimo_giorno)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_c, VALUTA, importi)
    assert versione.rapporti == (R2,)
    (escluso,) = versione.esclusi
    assert (escluso.importo.rapporto, escluso.importo.istituto) == (R, "stipendio")
    assert "attestazione_prestazione" in escluso.motivo


def test_una_condizione_su_un_istituto_senza_regola_e_rifiutata():
    with pytest.raises(ErroreCorpus, match="istituto senza regola"):
        Corpus.da_toml(CORPUS_PROPOSTA + CONDIZIONE.replace('"stipendio"', '"inesistente"'))


def test_il_fatto_deve_coprire_tutto_il_periodo_dell_importo(registro, corpus_c, orologio):
    assumi(registro, R, P)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus_c, FEB, rapporto=R) + stipendio(registro, corpus_c, FEB, rapporto=R2)
    registro.registra_codice(R, "attestazione_prestazione", "si", FEB.primo_giorno, date(2026, 2, 14))
    registro.registra_codice(R2, "attestazione_prestazione", "si", FEB.primo_giorno, FEB.ultimo_giorno)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_c, VALUTA, importi)
    assert versione.rapporti == (R2,)
    assert [e.importo.rapporto for e in versione.esclusi] == [R]


def test_senza_condizione_dichiarata_l_importo_entra_come_prima(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_PROPOSTA)
    assumi(registro, R, P)
    importi = stipendio(registro, corpus, FEB)
    orologio.vai(2, 20)
    assert emetti_versione(registro, corpus, VALUTA, importi).rapporti == (R,)
