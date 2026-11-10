"""Dichiarazione dell'istituto accessorio e regola della sostitutiva nel corpus (ticket #96, ADR 0035). Valori e fonti fittizi."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Corpus
from paghe.errori import ErroreCorpus
from paghe.sostitutiva import netto_accessorio, scomputo

from materiale_sostitutiva import ACCESSORIO, PREMIO, TESTO_SOSTITUTIVA, corpus_sostitutiva, parametri_sostitutiva, sostitutiva
from test_fiscale import TESTO

D = Decimal
CORPUS_REALE = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"


def test_l_istituto_dichiara_di_essere_accessorio_con_date_e_riferimento():
    corpus = corpus_sostitutiva()
    assert corpus.accessorio("premio", date(2026, 6, 1)).riferimento == "fittizio:accessorio-premio"
    assert corpus.accessorio("stipendio", date(2026, 6, 1)) is None


def test_la_dichiarazione_ha_una_vigenza():
    chiusa = ACCESSORIO.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2025-12-31")
    corpus = corpus_sostitutiva(accessorio=chiusa)
    assert corpus.accessorio("premio", date(2026, 1, 1)) is None


def test_la_regola_e_datata_e_fuori_dal_2026_non_c_e():
    corpus = corpus_sostitutiva()
    regola = corpus.regola_sostitutiva(date(2026, 6, 1))
    assert (regola.istituto, regola.istituto_base) == ("sostitutiva_accessorio", "sostitutiva_accessorio_base")
    assert corpus.regola_sostitutiva(date(2027, 1, 1)) is None


def test_la_versione_del_corpus_cambia_con_la_sostitutiva_e_resta_senza():
    senza = Corpus.da_toml(TESTO + PREMIO)
    assert senza.versione != Corpus.da_toml(TESTO_SOSTITUTIVA).versione
    assert senza.regola_sostitutiva(date(2026, 6, 1)) is None


def test_un_istituto_accessorio_ignoto_ferma_il_corpus():
    with pytest.raises(ErroreCorpus, match="istituto ignoto"):
        Corpus.da_toml(TESTO + PREMIO + ACCESSORIO.replace('"premio"', '"inesistente"'))


def test_due_dichiarazioni_dello_stesso_istituto_non_si_sovrappongono():
    with pytest.raises(ErroreCorpus, match="sovrappost"):
        Corpus.da_toml(TESTO + PREMIO + ACCESSORIO + ACCESSORIO)


def test_un_parametro_ignoto_ferma_il_corpus():
    with pytest.raises(ErroreCorpus, match="parametri ignoti"):
        Corpus.da_toml(TESTO + PREMIO + parametri_sostitutiva() + sostitutiva().replace('"sost_tetto"', '"inesistente"'))


def test_l_imposta_e_la_quota_sono_istituti_diversi():
    with pytest.raises(ErroreCorpus, match="istituti diversi"):
        Corpus.da_toml(
            TESTO + PREMIO + parametri_sostitutiva() + sostitutiva().replace("sostitutiva_accessorio_base", "sostitutiva_accessorio")
        )


def test_la_regola_senza_riferimento_e_rifiutata():
    with pytest.raises(ErroreCorpus, match="riferimento normativo obbligatorio"):
        Corpus.da_toml(
            TESTO + PREMIO + parametri_sostitutiva() + sostitutiva().replace('riferimento = "fittizio:sostitutiva"', 'riferimento = ""')
        )


def test_nel_corpus_reale_la_regola_ha_i_valori_della_legge_e_nessun_istituto_e_accessorio():
    reale = Corpus.carica(CORPUS_REALE, reale=True)
    regola = reale.regola_sostitutiva(date(2026, 6, 1))
    valori = {nome: reale.parametro(nome).vigenza_per(__import__("paghe").Periodo(date(2026, 6, 1), date(2026, 6, 1))).valore
              for nome in regola.parametri}
    assert valori == {
        "sostitutiva_accessorio_aliquota": D("0.15"),
        "sostitutiva_accessorio_tetto": D("800"),
        "sostitutiva_accessorio_limite": D("50000"),
    }
    assert "art1-com237" in regola.riferimento and "4-E" in regola.riferimento
    assert reale.regola_sostitutiva(date(2027, 1, 1)) is None
    assert reale.fiscale.accessori == ()
    assert reale.composizione("sostitutiva_accessorio", date(2026, 6, 1)).canale == "f24ep"
    assert reale.composizione("sostitutiva_accessorio_base", date(2026, 6, 1)).natura == "imponibile_sostitutivo"


# Funzioni pure

def test_il_netto_dell_accessorio_toglie_i_contributi_in_proporzione_al_reddito_del_pagamento():
    # 500 di accessorio su 2000 di reddito, contributi 160: 500 - 160 * 500 / 2000 = 460,00
    assert netto_accessorio(D("500"), D("2000"), D("160")) == D("460.00")
    assert netto_accessorio(D("500"), D("500"), D("0")) == D("500.00")
    assert netto_accessorio(D("0"), D("0"), D("0")) == D("0")


def test_lo_scomputo_e_l_imposta_trattenuta_oltre_quella_che_spetta_sulla_quota_rimasta():
    assert scomputo(D("0.15"), D("0"), D("15.00")) == D("15.00")
    assert scomputo(D("0.15"), D("100"), D("15.00")) == D("0")
    assert scomputo(D("0.15"), D("200"), D("15.00")) == D("0")
