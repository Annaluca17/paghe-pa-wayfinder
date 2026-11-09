"""Somma esente e trattamento integrativo nella proposta e nella delega F24EP (ticket #95, ADR 0023). Dati fittizi.

Il riconosciuto e' una riga sul netto verso la persona e, per la delega, un credito del sostituto: 170E per il trattamento
integrativo e 175E per la somma esente, riferimento A il mese e B l'anno del pagamento. Il recupero e' una riga a debito
separata con lo stesso codice, riferimento A il mese del recupero.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.delega import costruisci_delega

from materiale_benefici import beneficio, composizione_benefici, parametri_benefici
from materiale_delega import dati_ente, paga_a_mano, riga_a_mano, toml_delega
from materiale_proposta import assumi as assumi_proposta, paga, per_istituto, stipendio

D = Decimal
FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
CHIAVE_100E = ("F", "100E", "", "", "0002", "2026")
CHIAVE_170E = ("F", "170E", "", "", "0002", "2026")
CHIAVE_175E = ("F", "175E", "", "", "0002", "2026")


def toml_con_benefici(limite_175e: bool = False) -> str:
    testo = toml_delega() + parametri_benefici() + beneficio() + composizione_benefici()
    return testo if limite_175e else testo.replace('limite_credito = "non_modellato"\n', "")


@pytest.fixture
def corpus():
    return Corpus.da_toml(toml_con_benefici())


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))


def delega_con(registro, corpus, orologio, voci):
    """`voci`: (istituto, valore) pagati il 27 febbraio con anno d'imposta 2026, e la delega del mese."""
    righe = [riga_a_mano(corpus, VALUTA, istituto, valore, anno_imposta=2026) for istituto, valore in voci]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    return costruisci_delega(registro, corpus, FEB)


def per_chiave(delega):
    return {(r.chiave, r.credito > 0): (r.debito, r.credito) for r in delega.righe}


def test_i_benefici_entrano_nella_proposta_sul_netto_della_persona(registro, orologio):
    corpus = Corpus.da_toml(toml_con_benefici())
    assumi_proposta(registro)
    orologio.vai(1, 20)
    versione = paga(registro, corpus, orologio, stipendio(registro, corpus, Mese(2026, 1), "1000"), date(2026, 1, 27), "p-1")
    righe = per_istituto(versione.righe)
    assert (righe["somma_esente"].importo.valore, righe["trattamento_integrativo"].importo.valore) == (D("50.00"), D("100.00"))
    # 1000 meno contributo del lavoratore 80,00 meno ritenuta 0 (sotto la franchigia), piu' i due benefici
    assert versione.netti[0].netto == D("1070.00")


def test_il_riconosciuto_e_un_credito_nella_delega_con_il_mese_e_l_anno_del_pagamento(registro, corpus, orologio, ente):
    d = delega_con(
        registro, corpus, orologio,
        [("ritenuta_irpef", "200"), ("trattamento_integrativo", "100"), ("somma_esente", "50")],
    )
    assert d.fermi == ()
    assert per_chiave(d)[(CHIAVE_170E, True)] == (D("0"), D("100"))
    assert per_chiave(d)[(CHIAVE_175E, True)] == (D("0"), D("50"))
    assert per_chiave(d)[(CHIAVE_100E, False)] == (D("200"), D("0"))
    assert d.saldo == D("50")


def test_il_recupero_e_una_riga_a_debito_separata_con_lo_stesso_codice(registro, corpus, orologio, ente):
    d = delega_con(
        registro, corpus, orologio,
        [("ritenuta_irpef", "200"), ("trattamento_integrativo", "100"), ("trattamento_integrativo_recupero", "137.50")],
    )
    assert d.fermi == ()
    assert per_chiave(d)[(CHIAVE_170E, False)] == (D("137.50"), D("0"))
    assert per_chiave(d)[(CHIAVE_170E, True)] == (D("0"), D("100"))
    assert d.totale_debito == D("337.50") and d.totale_credito == D("100")


def test_il_recupero_della_somma_esente_e_a_debito_su_175e(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("ritenuta_irpef", "200"), ("somma_esente_recupero", "55")])
    assert per_chiave(d)[(CHIAVE_175E, False)] == (D("55"), D("0"))


def test_il_credito_della_somma_esente_ferma_la_delega_se_il_limite_del_175e_non_e_modellato(registro, orologio, ente):
    corpus = Corpus.da_toml(toml_con_benefici(limite_175e=True))
    d = delega_con(registro, corpus, orologio, [("ritenuta_irpef", "200"), ("somma_esente", "50")])
    (fermo,) = d.fermi
    assert fermo.caso == "limite_credito" and "175E" in fermo.motivo
