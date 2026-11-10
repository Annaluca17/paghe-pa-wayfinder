"""Casi limite della detrazione dell'art. 13 c. 5 (ticket #97), scritti in rilettura. Valori di fantasia."""

from decimal import Decimal
from types import SimpleNamespace

from test_detrazione_carica_elettiva import CARICA, ENTRAMBE, calcolo, reale  # noqa: F401

D = Decimal


def test_con_entrambi_i_redditi_senza_dichiarazione_nessuna_delle_due(reale):
    esito = calcolo(reale, "9000", ENTRAMBE, giorni=30, dichiarazione=None)
    assert (esito.detrazione, esito.art13, esito.dichiarata) == (D(0), "", False)


def test_oltre_50000_nessuna_detrazione_con_entrambi_i_redditi(reale):
    esito = calcolo(reale, "50000.01", ENTRAMBE)
    assert esito.detrazione == D(0)


def test_reddito_zero_la_detrazione_non_porta_l_imposta_sotto_zero(reale):
    esito = calcolo(reale, "0", CARICA)
    assert esito.detrazione == D("1265.00") and esito.dovuto == D(0)


def test_nel_mese_l_aumento_di_50_euro_segue_il_reddito_ragguagliato_all_anno(reale):
    # 1.416,66 x 12 = 16.999,92: dentro la fascia dei 50 euro; 1.416,67 x 12 = 17.000,04: fuori
    dentro = calcolo(reale, "1416.66", CARICA, periodi=12, giorni=1, giorni_anno=1)
    fuori = calcolo(reale, "1416.67", CARICA, periodi=12, giorni=1, giorni_anno=1)
    assert dentro.detrazione - fuori.detrazione > D("4")  # circa 50/12


def test_scelta_del_c_5_con_entrambi_vale_anche_se_meno_favorevole(reale):
    esito = calcolo(reale, "9000", ENTRAMBE, dichiarazione=SimpleNamespace(valore="scelta_art13_c5"))
    assert (esito.detrazione, esito.art13) == (D("1145.97"), "c. 5")
