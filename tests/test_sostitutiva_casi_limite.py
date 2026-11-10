"""Casi limite della sostitutiva sull'accessorio (ticket #96, ADR 0035). Valori e fonti fittizi, numeri di materiale_sostitutiva."""

from datetime import date
from decimal import Decimal

from materiale_sostitutiva import BASE, IMPOSTA, corpus_sostitutiva, della_sostitutiva, mese_con_premio
from paghe import Atto
from test_fiscale import P, assumi

D = Decimal


def test_al_conguaglio_spetta_l_accessorio_di_prima_della_rinuncia_anche_se_il_mese_era_sopra_il_limite(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    # gennaio: (6000 + 500) * 365 / 31 = 76532,26, sopra i 50000: niente sostitutiva nel mese
    _, gennaio = mese_con_premio(registro, orologio, corpus, 1, stipendio="6000", premio="500")
    assert gennaio.sostitutiva == ()
    registro.registra_rinuncia_sostitutiva(P, date(2026, 2, 1), None, Atto("ente:c_x000:modulo:2026-01-30;1", date(2026, 1, 30)))
    # febbraio: 1000 di premio dopo la rinuncia, in tassazione ordinaria
    _, febbraio = mese_con_premio(registro, orologio, corpus, 2, premio="1000")
    assert febbraio.sostitutiva == ()
    for numero in range(3, 12):
        mese_con_premio(registro, orologio, corpus, numero)
    _, dicembre = mese_con_premio(registro, orologio, corpus, 12, ultimo=True)
    # reddito vero 18500, sotto il limite: spettano i 500 di gennaio, non i 1000 di febbraio (tetto 800 non raggiunto)
    assert della_sostitutiva(dicembre, BASE).valore == D("500.00")
    assert della_sostitutiva(dicembre, IMPOSTA).valore == D("75.00")


def test_l_imponibile_sostitutivo_non_muove_denaro():
    import pytest

    from paghe.corpus import DichiarazioneComposizione
    from paghe.errori import ErroreCorpus

    DichiarazioneComposizione("q", date(2026, 1, 1), "fittizio:q", natura="imponibile_sostitutivo", effetto="nessuno")
    with pytest.raises(ErroreCorpus):
        DichiarazioneComposizione("q", date(2026, 1, 1), "fittizio:q", natura="imponibile_sostitutivo", effetto="meno")
    with pytest.raises(ErroreCorpus):
        DichiarazioneComposizione(
            "q", date(2026, 1, 1), "fittizio:q", natura="imponibile_sostitutivo", effetto="nessuno", canale="f24ep"
        )
