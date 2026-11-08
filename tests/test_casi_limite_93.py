"""Casi limite del fisco reale (rilettura del ticket #93): scaglione a cavallo nel mese, detrazioni a zero, incapienza."""

from datetime import date
from decimal import Decimal

from paghe import Mese
from paghe.fisco import _calcola
from paghe.modello import Atto
from test_fiscale import P, assumi, fisco, paga, stipendio  # noqa: F401 (fixture)
from test_fisco_corpus_reale import calcolo, reale  # noqa: F401 (fixture)

D = Decimal


def test_un_mese_a_cavallo_del_primo_scaglione_tassa_al_33_solo_l_eccedenza(reale):
    # 2.333,34 al mese: reddito annuo 28.000,08; solo 0,08 annui vanno al 33%
    c = calcolo(reale, "2333.34", periodi=12, giorni=1, giorni_anno=1)
    assert c.imposta == ((D("6440") + D("0.08") * D("0.33")) / 12).quantize(D("0.01"))


def test_sopra_50000_ogni_detrazione_e_zero_e_resta_l_imposta(reale):
    c = calcolo(reale, "50000.01")
    assert (c.detrazione, c.detrazione_automatica) == (0, 0)
    assert c.dovuto == c.imposta == D("13700.00")


def test_sopra_50000_anche_nel_mese_le_detrazioni_sono_zero(reale):
    c = calcolo(reale, "4200", periodi=12, giorni=1, giorni_anno=1)  # 50.400 annui
    assert (c.detrazione, c.detrazione_automatica) == (0, 0)


def test_conguaglio_oltre_la_capienza_del_pagamento_resta_intero(registro, orologio, fisco):
    """La dichiarazione vale fino a novembre: il conguaglio toglie tutta la detrazione dell'anno su un dicembre che non
    la contiene. Il modello non limita ancora il conguaglio alla capienza né lo differisce (#99): lo prova intero."""
    assumi(registro)
    registro.registra_dichiarazione_sostituito(
        P, "lavoro_dipendente", date(2026, 1, 1), date(2026, 11, 30), Atto("ente:c_x000:modulo:2026-01-10;1", date(2026, 1, 10))
    )
    operate = D(0)
    for mese in range(1, 12):
        _, f = paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, mese), "300"), date(2026, mese, 27))
        operate += f.ritenuta.valore
    _, f = paga(registro, orologio, fisco, stipendio(registro, fisco, Mese(2026, 12), "300"), date(2026, 12, 18), ultimo=True)
    trattenuto = f.ritenuta.valore + f.conguaglio.valore
    assert f.conguaglio.valore > 0
    assert trattenuto > D("300")  # più del lordo del pagamento: incapienza
    regola = fisco.regola_ritenuta(date(2026, 12, 18))
    senza_detrazione = _calcola(fisco, regola, D("3600"), 1, date(2026, 12, 18), None)
    assert operate + trattenuto == senza_detrazione.dovuto  # l'anno chiude senza detrazione, come vuole la dichiarazione
