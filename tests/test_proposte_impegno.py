"""Proposte di impegno e di accertamento da un atto registrato (ADR 0031). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus
from paghe.errori import ClassificazioneMancante, ErroreRegistro
from paghe.impegni import AttoPresupposto
from paghe.proposte_impegno import (
    conferma_proposta,
    emetti_proposta_accertamento,
    emetti_proposta_impegno,
    leggi_proposta,
    respingi_proposta,
)

from materiale_proposta import CORPUS_PROPOSTA

TIPO = "sottoscrizione_integrativo"
ATTO = AttoPresupposto(TIPO, "ente:ente_di_prova:contratto:2026-03-01;7")
DATA = date(2026, 3, 1)


@pytest.fixture
def corpus_atto():
    """Lo stipendio nasce da atto; il gettone e' automatico; il contributo dell'ente nasce da atto con entrata di riferimento."""
    testo = CORPUS_PROPOSTA.replace(
        'piano_dei_conti = "U.1.01.01.01.002"\norigine_impegno = "automatico"',
        f'piano_dei_conti = "U.1.01.01.01.002"\norigine_impegno = "{TIPO}"',
    ).replace(
        'piano_dei_conti = "U.1.01.02.01.001"\norigine_impegno = "automatico"',
        'piano_dei_conti = "E.3.05.99.99.999"\norigine_impegno = "accordo_rimborso"',
    )
    return Corpus.da_toml(testo)


def impegno_da(registro, corpus, chiave="PI-1", importo="5000", esercizio=2026, atto=ATTO):
    return emetti_proposta_impegno(
        registro, corpus, chiave, "adattatore-prova", "stipendio", atto, DATA, Decimal(importo), esercizio, "01", "02"
    )


def test_la_proposta_di_impegno_porta_classificazione_esercizio_atto_e_importo(registro, corpus_atto):
    proposta = impegno_da(registro, corpus_atto)
    letta = leggi_proposta(registro, "PI-1")
    assert letta == proposta
    assert (letta.verso, letta.istituto, letta.piano_dei_conti, letta.missione, letta.programma) == (
        "spesa", "stipendio", "U.1.01.01.01.002", "01", "02"
    )
    assert (letta.esercizio, letta.atto, letta.importo, letta.stato) == (2026, ATTO, Decimal("5000"), "inviata")


def test_lo_stesso_identificativo_con_lo_stesso_contenuto_non_ha_effetto(registro, corpus_atto, orologio):
    impegno_da(registro, corpus_atto)
    orologio.avanza()
    impegno_da(registro, corpus_atto)
    assert len(registro.eventi("proposta_impegno", registro.adesso())) == 1


def test_lo_stesso_identificativo_con_contenuto_diverso_e_un_errore(registro, corpus_atto, orologio):
    impegno_da(registro, corpus_atto)
    orologio.avanza()
    with pytest.raises(ErroreRegistro, match="contenuto diverso"):
        impegno_da(registro, corpus_atto, importo="6000")


def test_un_istituto_automatico_non_genera_proposte_di_impegno(registro, corpus_atto):
    with pytest.raises(ErroreRegistro, match="automatico"):
        emetti_proposta_impegno(registro, corpus_atto, "PI-G", "a", "gettone", ATTO, DATA, Decimal("10"), 2026, "01", "02")


def test_l_atto_deve_essere_del_tipo_che_l_origine_dell_istituto_dichiara(registro, corpus_atto):
    with pytest.raises(ErroreRegistro, match="origine"):
        impegno_da(registro, corpus_atto, atto=AttoPresupposto("altro_tipo", "ente:e:contratto:2026-03-01;1"))


def test_senza_classificazione_alla_data_dell_atto_la_proposta_non_si_emette(registro, corpus_atto):
    with pytest.raises(ClassificazioneMancante, match="stipendio"):
        emetti_proposta_impegno(
            registro, corpus_atto, "PI-X", "a", "stipendio", ATTO, date(2019, 1, 1), Decimal("10"), 2026, "01", "02"
        )


@pytest.mark.parametrize("importo", ["0", "-5"])
def test_l_importo_e_positivo(registro, corpus_atto, importo):
    with pytest.raises(ErroreRegistro, match="importo"):
        impegno_da(registro, corpus_atto, importo=importo)


def test_la_proposta_di_accertamento_ha_la_stessa_forma_con_verso_entrata(registro, corpus_atto):
    proposta = emetti_proposta_accertamento(
        registro, corpus_atto, "PA-1", "a", "contributo_ente", AttoPresupposto("accordo_rimborso", "ente:e:accordo:2026-03-01;2"),
        DATA, Decimal("800"), 2026, "01", "02",
    )
    assert (proposta.verso, proposta.piano_dei_conti, proposta.importo) == ("entrata", "E.3.05.99.99.999", Decimal("800"))


def test_il_verso_deve_accordarsi_al_codice_del_piano_dei_conti(registro, corpus_atto):
    with pytest.raises(ErroreRegistro, match="verso"):
        emetti_proposta_accertamento(registro, corpus_atto, "PA-2", "a", "stipendio", ATTO, DATA, Decimal("5"), 2026, "01", "02")


def test_la_ragioneria_conferma_la_proposta(registro, corpus_atto, orologio):
    impegno_da(registro, corpus_atto)
    orologio.avanza()
    conferma_proposta(registro, "PI-1")
    assert leggi_proposta(registro, "PI-1").stato == "confermata"


def test_la_ragioneria_respinge_con_un_motivo_obbligatorio(registro, corpus_atto, orologio):
    impegno_da(registro, corpus_atto)
    orologio.avanza()
    with pytest.raises(ErroreRegistro, match="motivo"):
        respingi_proposta(registro, "PI-1", "  ")
    respingi_proposta(registro, "PI-1", "importo non coperto")
    assert leggi_proposta(registro, "PI-1").stato == "respinta"
    assert leggi_proposta(registro, "PI-1").motivo == "importo non coperto"


def test_una_proposta_gia_decisa_non_si_decide_di_nuovo(registro, corpus_atto, orologio):
    impegno_da(registro, corpus_atto)
    orologio.avanza()
    conferma_proposta(registro, "PI-1")
    with pytest.raises(ErroreRegistro, match="inviata"):
        respingi_proposta(registro, "PI-1", "ci ripenso")


def test_una_proposta_inesistente_e_un_errore(registro):
    with pytest.raises(ErroreRegistro, match="inesistente"):
        leggi_proposta(registro, "NON-C-E")
