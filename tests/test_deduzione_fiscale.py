"""Contributi del lavoratore che riducono l'imponibile fiscale (ticket #70, art. 51 c. 2 lett. a TUIR). Dati fittizi.

Numeri scelti per tornare a mano, sul corpus di test_fiscale (scaglioni 10% fino a 10000, 20% fino a 30000, 30% oltre,
ragguagliati al mese; nessuna detrazione senza dichiarazione del sostituto).
Uno stipendio mensile di 1500 con un contributo del lavoratore di 120:
  imponibile fiscale = 1500 - 120 = 1380; scaglioni mensili 833,33 e 2500;
  ritenuta = 0,10 * 833,33 + 0,20 * (1380 - 833,33) = 83,33 + 109,33 = 192,67 (senza deduzione: 216,67).
"""

from datetime import date

import pytest

from paghe import Corpus
from paghe.errori import ErroreCorpus

from test_fiscale import TESTO

CONTRIBUTO = """
[[regola]]
istituto = "contributo_lavoratore"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:contributo-lavoratore"
formula = "arrotonda(base.pens * parametro.aliquota_1, 2)"
maturazione = "periodo"
"""

DEDUZIONE = """
[[deduzione_fiscale]]
istituto = "contributo_lavoratore"
dal = 2020-01-01
riferimento = "fittizio:deduzione-contributo-lavoratore"
"""


# Dichiarazione dell'istituto nel corpus

def test_l_istituto_dichiara_che_l_importo_riduce_l_imponibile_fiscale_con_date_e_riferimento():
    corpus = Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-12-31"))
    dichiarazione = corpus.deduzione_fiscale("contributo_lavoratore", date(2026, 6, 1))
    assert (dichiarazione.istituto, dichiarazione.riferimento) == (
        "contributo_lavoratore",
        "fittizio:deduzione-contributo-lavoratore",
    )
    assert corpus.deduzione_fiscale("contributo_lavoratore", date(2027, 1, 1)) is None
    assert corpus.deduzione_fiscale("stipendio", date(2026, 6, 1)) is None


def test_la_deduzione_di_un_istituto_ignoto_e_rifiutata():
    with pytest.raises(ErroreCorpus, match="istituto ignoto"):
        Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace('"contributo_lavoratore"', '"contributo_inesistente"'))


def test_due_deduzioni_dello_stesso_istituto_non_si_sovrappongono():
    seconda = DEDUZIONE.replace("2020-01-01", "2026-01-01").replace("deduzione-contributo-lavoratore", "deduzione-bis")
    with pytest.raises(ErroreCorpus, match="sovrappost"):
        Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-06-30") + seconda)
    adiacenti = DEDUZIONE.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2025-12-31") + seconda
    corpus = Corpus.da_toml(TESTO + CONTRIBUTO + adiacenti)
    assert corpus.deduzione_fiscale("contributo_lavoratore", date(2026, 1, 1)).riferimento == "fittizio:deduzione-bis"


def test_la_versione_del_corpus_cambia_con_la_deduzione_e_resta_senza():
    senza = Corpus.da_toml(TESTO + CONTRIBUTO)
    con = Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE)
    altra = Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace("deduzione-contributo-lavoratore", "deduzione-altra"))
    assert len({senza.versione, con.versione, altra.versione}) == 3


def test_la_deduzione_senza_riferimento_e_rifiutata():
    with pytest.raises(ErroreCorpus, match="riferimento normativo obbligatorio"):
        Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace('riferimento = "fittizio:deduzione-contributo-lavoratore"', 'riferimento = ""'))


def test_il_corpus_reale_rifiuta_il_riferimento_fittizio_della_deduzione():
    from test_fiscale import CORPUS_REALE

    reale = Corpus.carica(CORPUS_REALE, reale=True)
    testo = CORPUS_REALE.read_text(encoding="utf-8") + DEDUZIONE.replace('"contributo_lavoratore"', f'"{reale.istituti()[0]}"')
    with pytest.raises(ErroreCorpus, match="Deduzione fiscale.*fittizio"):
        Corpus.da_toml(testo, reale=True)
