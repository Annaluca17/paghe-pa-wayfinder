"""Casi limite della somma sospesa 48-bis (ADR 0036): tetto, recuperi fiscali, altri titoli. Dati fittizi."""

from decimal import Decimal
from types import SimpleNamespace

from paghe.blocco_pagamenti import importo_sospeso, trattenute_per_il_tetto

from materiale_48bis import VALUTA, corpus_48bis


def _riga(natura, canale, sul_netto):
    return SimpleNamespace(natura=natura, canale=canale, sul_netto=Decimal(sul_netto))


def test_i_recuperi_fiscali_in_f24ep_non_contano_nel_tetto():
    righe = [
        _riga("retribuzione", "accredito", "3500"),
        _riga("trattenuta_terzi", "f24ep", "-400"),  # recupero del trattamento integrativo: va all'erario
        _riga("trattenuta_terzi", "bonifico", "-300"),  # cessione del quinto
    ]
    assert trattenute_per_il_tetto(righe) == Decimal("300")


def test_trattenute_che_arrivano_esattamente_alla_meta_lasciano_zero():
    regola = corpus_48bis().regola_somma_sospesa(VALUTA)
    assert importo_sospeso(regola, Decimal("3000"), Decimal("1500"), Decimal("5000")) == Decimal(0)


def test_per_un_altro_titolo_sopra_5000_si_sospende_un_quinto():
    regola = corpus_48bis().regola_somma_sospesa(VALUTA)
    assert importo_sospeso(regola, Decimal("6000.01"), Decimal(0), Decimal("10000")) == Decimal("1200.00")


def test_il_tetto_si_arrotonda_per_difetto_prima_di_togliere_le_trattenute():
    regola = corpus_48bis().regola_somma_sospesa(VALUTA)
    # meta' di 2600,01 = 1300,005 -> 1300,00; meno 1000 = 300; la fascia 1/7 (371,43) e il debito sono maggiori
    assert importo_sospeso(regola, Decimal("2600.01"), Decimal("1000"), Decimal("5000")) == Decimal("300.00")
