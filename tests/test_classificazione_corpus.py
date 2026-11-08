"""Dichiarazione di classificazione per istituto nel corpus (ADR 0031). Valori e fonti fittizi."""

from datetime import date

import pytest

from paghe import Corpus
from paghe.errori import ErroreCorpus

from conftest import CORPUS_BASE

CLASSIFICAZIONE = """
[[classificazione]]
istituto = "compenso"
dal = 2020-01-01
riferimento = "fittizio:class-compenso"
piano_dei_conti = "U.1.01.01.01.002"
origine_impegno = "automatico"
"""


def corpus(extra: str = "", reale: bool = False) -> Corpus:
    return Corpus.da_toml(CORPUS_BASE + extra, reale=reale)


def test_la_dichiarazione_dice_piano_dei_conti_e_origine_dell_impegno():
    d = corpus(CLASSIFICAZIONE).classificazione("compenso", date(2026, 5, 1))
    assert (d.piano_dei_conti, d.origine_impegno) == ("U.1.01.01.01.002", "automatico")
    assert d.riferimento == "fittizio:class-compenso"


def test_una_classificazione_assente_e_none():
    assert corpus().classificazione("compenso", date(2026, 5, 1)) is None


def test_la_dichiarazione_vale_nelle_sue_date():
    c = corpus(CLASSIFICAZIONE.replace("dal = 2020-01-01", "dal = 2026-03-01\nal = 2026-06-30"))
    assert c.classificazione("compenso", date(2026, 2, 28)) is None
    assert c.classificazione("compenso", date(2026, 3, 1)) is not None
    assert c.classificazione("compenso", date(2026, 6, 30)) is not None
    assert c.classificazione("compenso", date(2026, 7, 1)) is None


@pytest.mark.parametrize("codice", ["U.1.01.01.01.02", "X.1.01.01.01.002", "U.1.01.01.01.002 ", "u.1.01.01.01.002", "1.01.01.01.002"])
def test_il_codice_di_v_livello_ha_il_formato_del_piano_dei_conti(codice):
    with pytest.raises(ErroreCorpus, match="piano dei conti"):
        corpus(CLASSIFICAZIONE.replace("U.1.01.01.01.002", codice))


def test_il_codice_di_entrata_e_ammesso():
    assert corpus(CLASSIFICAZIONE.replace("U.1.01.01.01.002", "E.9.01.02.01.001")).classificazione("compenso", date(2026, 5, 1))


@pytest.mark.parametrize("origine", ["", "  ", " automatico"])
def test_l_origine_dell_impegno_e_automatico_o_il_nome_di_un_tipo_di_atto(origine):
    with pytest.raises(ErroreCorpus, match="origine"):
        corpus(CLASSIFICAZIONE.replace('"automatico"', f'"{origine}"'))


def test_l_origine_puo_essere_un_tipo_di_atto():
    c = corpus(CLASSIFICAZIONE.replace('"automatico"', '"sottoscrizione_integrativo"'))
    assert c.classificazione("compenso", date(2026, 5, 1)).origine_impegno == "sottoscrizione_integrativo"


def test_l_istituto_deve_essere_noto():
    with pytest.raises(ErroreCorpus, match="istituto"):
        corpus(CLASSIFICAZIONE.replace('"compenso"', '"sconosciuto"'))


def test_due_dichiarazioni_dello_stesso_istituto_non_si_sovrappongono():
    with pytest.raises(ErroreCorpus, match="sovrapposte"):
        corpus(CLASSIFICAZIONE + CLASSIFICAZIONE)


def test_due_dichiarazioni_in_date_diverse_si_alternano():
    prima = CLASSIFICAZIONE.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-12-31")
    dopo = CLASSIFICAZIONE.replace("dal = 2020-01-01", "dal = 2027-01-01").replace("U.1.01.01.01.002", "U.1.01.01.01.006")
    c = corpus(prima + dopo)
    assert c.classificazione("compenso", date(2026, 12, 31)).piano_dei_conti == "U.1.01.01.01.002"
    assert c.classificazione("compenso", date(2027, 1, 1)).piano_dei_conti == "U.1.01.01.01.006"


def test_il_corpus_reale_rifiuta_il_riferimento_fittizio_della_classificazione():
    with pytest.raises(ErroreCorpus, match="fittizio"):
        corpus(CLASSIFICAZIONE, reale=True)


def test_la_classificazione_entra_nell_impronta_solo_se_presente():
    base = corpus().versione
    assert base == "51a715efce086279"
    con = corpus(CLASSIFICAZIONE).versione
    assert con != base
    assert corpus(CLASSIFICAZIONE).versione == con
    assert corpus(CLASSIFICAZIONE.replace("U.1.01.01.01.002", "U.1.01.01.01.006")).versione != con
    assert corpus(CLASSIFICAZIONE.replace('"automatico"', '"atto"')).versione != con
