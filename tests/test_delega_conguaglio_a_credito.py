"""Conguaglio a credito nella delega F24EP (ticket #71, ADR 0023). Dati fittizi.

I conguagli negativi (ritenuta con segno meno nella composizione) riducono la riga 100E della stessa delega, sommati
con le ritenute dello stesso codice e degli stessi riferimenti. Se il totale resta positivo o zero si versa al netto;
se diventa negativo la delega si ferma e nomina il caso. Nessuna riga a debito negativa arriva al serializzatore.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.delega import costruisci_delega, trasmetti_delega
from paghe.errori import VistaFerma

from materiale_delega import ADATTATORE, R, R2, corpus_delega, dati_ente, paga_a_mano, riga_a_mano

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal
CHIAVE_100E = ("F", "100E", "", "", "0002", "2026")


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))


def delega_con(registro, corpus, orologio, voci):
    """`voci`: (istituto, valore, rapporto) pagati il 27 febbraio, e la delega del mese."""
    paga_a_mano(registro, corpus, orologio, VALUTA, [riga_a_mano(corpus, VALUTA, i, v, rapporto=r) for i, v, r in voci])
    return costruisci_delega(registro, corpus, FEB)


def test_il_conguaglio_a_credito_riduce_la_ritenuta_100e_della_stessa_delega(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("ritenuta_irpef", "100", R), ("conguaglio_irpef", "-30", R)])
    (riga,) = d.righe
    assert (riga.chiave, riga.debito, riga.credito) == (CHIAVE_100E, D("70"), D("0"))
    assert d.pronta and d.fermi == ()


def test_i_conguagli_di_piu_persone_si_sommano_con_le_ritenute_dello_stesso_codice(registro, corpus, orologio, ente):
    voci = [
        ("ritenuta_irpef", "100", R), ("conguaglio_irpef", "-30", R),
        ("ritenuta_irpef", "50", R2), ("conguaglio_irpef", "-20", R2),
    ]
    (riga,) = delega_con(registro, corpus, orologio, voci).righe
    assert riga.debito == D("100")


def test_un_conguaglio_a_credito_che_supera_le_ritenute_ferma_la_delega_e_nomina_il_caso(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("ritenuta_irpef", "100", R), ("conguaglio_irpef", "-300", R)])
    assert not d.pronta
    (fermo,) = d.fermi
    assert fermo.caso == "debito_negativo"
    assert "100E" in fermo.motivo and "-200" in fermo.motivo


def test_la_delega_con_un_debito_negativo_non_si_trasmette_e_non_arriva_al_serializzatore(registro, corpus, orologio, ente):
    delega_con(registro, corpus, orologio, [("ritenuta_irpef", "100", R), ("conguaglio_irpef", "-300", R)])
    with pytest.raises(VistaFerma, match="debito negativo|100E"):
        trasmetti_delega(registro, corpus, "DELEGA-1", ADATTATORE, FEB)
    assert registro.evento("delega:DELEGA-1") is None
