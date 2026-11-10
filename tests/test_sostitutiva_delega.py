"""Sostitutiva sull'accessorio nella proposta e nella delega F24EP (ticket #96, ADR 0023 e 0035). Dati fittizi.

L'imposta e' una trattenuta sul netto e una riga a debito 179E (ris. AdE 4/E/2026), riferimento A il mese e B l'anno del
pagamento. La quota a sostitutiva e' un totale intermedio: non entra nel netto ne' nella delega.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.delega import costruisci_delega

from materiale_delega import dati_ente, paga_a_mano, riga_a_mano, toml_delega
from materiale_sostitutiva import CODICE_179E, COMPOSIZIONE_SOSTITUTIVA, parametri_sostitutiva, sostitutiva

D = Decimal
FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
CHIAVE_100E = ("F", "100E", "", "", "0002", "2026")
CHIAVE_179E = ("F", "179E", "", "", "0002", "2026")


@pytest.fixture
def corpus():
    return Corpus.da_toml(toml_delega() + parametri_sostitutiva() + sostitutiva() + COMPOSIZIONE_SOSTITUTIVA + CODICE_179E)


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))


def delega_con(registro, corpus, orologio, voci):
    righe = [riga_a_mano(corpus, VALUTA, istituto, valore, anno_imposta=2026) for istituto, valore in voci]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    return costruisci_delega(registro, corpus, FEB)


def test_l_imposta_e_una_riga_a_debito_179e_con_il_mese_e_l_anno_del_pagamento(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("ritenuta_irpef", "200"), ("sostitutiva_accessorio", "75")])
    assert d.fermi == ()
    per_chiave = {r.chiave: (r.debito, r.credito) for r in d.righe}
    assert per_chiave[CHIAVE_179E] == (D("75"), D("0"))
    assert per_chiave[CHIAVE_100E] == (D("200"), D("0"))
    assert d.totale_debito == D("275") and d.totale_credito == D("0")
