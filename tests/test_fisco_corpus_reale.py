"""Formule fiscali del corpus reale sui punti notevoli (ticket #93): salti di fascia, soglie, rapporto ai giorni."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Corpus
from paghe.fisco import _calcola

CORPUS_REALE = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
D = Decimal


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS_REALE, reale=True)


def calcolo(reale, imponibile, periodi=1, giorno=date(2026, 6, 1), giorni=365, giorni_anno=365, dichiarazione=True):
    regola = reale.regola_ritenuta(giorno)
    fatto = object() if dichiarazione else None
    return _calcola(reale, regola, D(imponibile), periodi, giorno, fatto, giorni, giorni_anno)


@pytest.mark.parametrize("anno", [2026, 2027])
@pytest.mark.parametrize(
    ("reddito", "imposta"),
    [
        ("28000", "6440.00"),
        ("28001", "6440.33"),
        ("50000", "13700.00"),
        ("50001", "13700.43"),
        ("60000", "18000.00"),
    ],
)
def test_imposta_a_scaglioni(reale, anno, reddito, imposta):
    assert calcolo(reale, reddito, giorno=date(anno, 6, 1)).imposta == D(imposta)


@pytest.mark.parametrize(
    ("reddito", "detrazione"),
    [
        ("15000", "1955.00"),  # la fascia a) arriva fino a 15.000 compresi
        ("15000.01", "3100.00"),  # sopra, il salto a 3.100
        ("25000", "2184.62"),  # fascia b), senza l'aumento di 65 (non superato)
        ("25000.01", "2249.62"),  # oltre 25.000 l'aumento di 65
        ("28000", "1975.00"),  # fine della fascia b) con l'aumento
        ("28000.01", "1975.00"),  # inizio della fascia c): 1910 x 21.999,99/22.000 = 1909,99; con 65 = 1974,99
        ("35000", "1367.27"),  # ultimo con l'aumento
        ("35000.01", "1302.27"),  # senza l'aumento
        ("50000", "0.00"),
        ("50000.01", "0.00"),
    ],
)
def test_detrazione_dell_art_13(reale, reddito, detrazione):
    atteso = D(detrazione)
    effettivo = calcolo(reale, reddito).detrazione
    assert abs(effettivo - atteso) <= D("0.01")
    assert effettivo >= 0


@pytest.mark.parametrize(
    ("reddito", "ulteriore"),
    [
        ("20000", "0.00"),
        ("20000.01", "1000.00"),
        ("32000", "1000.00"),
        ("36000", "500.00"),
        ("40000", "0.00"),
        ("40000.01", "0.00"),
    ],
)
def test_ulteriore_detrazione_automatica(reale, reddito, ulteriore):
    assert calcolo(reale, reddito, dichiarazione=False).detrazione_automatica == D(ulteriore)


def test_la_ritenuta_del_mese_ragguaglia_scaglioni_e_detrazioni_a_un_dodicesimo(reale):
    # 2.000 al mese: reddito annuo 24.000, imposta 5.520 / 12, art. 13 b) 1.910 + 1.190 x 4.000 / 13.000 = 2.276,15 / 12
    c = calcolo(reale, "2000", periodi=12, giorni=1, giorni_anno=1)
    assert (c.imposta, c.detrazione, c.detrazione_automatica) == (D("460.00"), D("189.68"), D("83.33"))
    assert c.dovuto == D("460.00") - D("189.68") - D("83.33")


def test_senza_dichiarazione_resta_solo_la_detrazione_automatica(reale):
    c = calcolo(reale, "2000", periodi=12, giorni=1, giorni_anno=1, dichiarazione=False)
    assert (c.detrazione, c.dovuto) == (D("0"), D("460.00") - D("83.33"))


def test_il_conguaglio_rapporta_la_detrazione_ai_giorni_e_il_minimo_di_690_vale_dopo_il_rapporto(reale):
    assert calcolo(reale, "9000", giorni=184).detrazione == D("985.53")  # 1.955 x 184 / 365
    assert calcolo(reale, "9000", giorni=30).detrazione == D("690.00")  # 160,68 sale al minimo
    assert calcolo(reale, "9000", giorni=366, giorni_anno=366).detrazione == D("1955.00")


def test_il_minimo_di_690_non_vale_oltre_15000(reale):
    assert calcolo(reale, "16000", giorni=30).detrazione < D("690")


def test_l_ulteriore_detrazione_e_rapportata_ai_giorni(reale):
    assert calcolo(reale, "25000", giorni=184, dichiarazione=False).detrazione_automatica == D("504.11")  # 1.000 x 184 / 365


def test_il_reale_ha_due_versioni_di_ritenuta_e_conguaglio(reale):
    assert reale.regola_ritenuta(date(2026, 12, 31)).versione == 1
    assert reale.regola_ritenuta(date(2027, 1, 1)).versione == 2
    assert reale.regola_conguaglio(date(2026, 12, 31)).versione == 1
    assert reale.regola_conguaglio(date(2027, 1, 1)).versione == 2
    assert reale.regola_ritenuta(date(2025, 12, 31)) is None
