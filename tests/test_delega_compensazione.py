"""Compensazione dei crediti del sostituto nella delega F24EP (ADR 0023). Dati fittizi.

Ordine scelto da Luca il 07/11/2026: prima contro le ritenute (100E), poi gli altri debiti nell'ordine delle
sezioni della delega. Il saldo di ogni modello non può essere negativo. Debiti di prova: 100E 100,00,
104E 50,00 e P201 480,00 (totale 630,00).
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.delega import costruisci_delega

from materiale_delega import R, R2, corpus_delega, dati_ente, paga_a_mano, riga_a_mano

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal

DEBITI = (("ritenuta_irpef", "100"), ("ritenuta_arretrati", "50"), ("contributo_ente", "480"))

CHIAVE_100E = ("F", "100E", "", "", "0002", "2026")
CHIAVE_104E = ("F", "104E", "", "", "0002", "2026")
CHIAVE_P201 = ("Q", "P201", "RM", "", "022026", "022026")
CHIAVE_150E = ("F", "150E", "", "", "", "2025")
CHIAVE_170E = ("F", "170E", "", "", "0002", "2026")


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))


def delega_con(registro, corpus, orologio, crediti=(), debiti=DEBITI):
    """Debiti e crediti `(istituto, valore[, anno d'imposta])` pagati il 27 febbraio, e la delega del mese."""
    righe = [riga_a_mano(corpus, VALUTA, i, v) for i, v in debiti]
    for voce in crediti:
        istituto, valore, *anno = voce
        righe.append(riga_a_mano(corpus, VALUTA, istituto, valore, anno_imposta=anno[0] if anno else None))
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    return costruisci_delega(registro, corpus, FEB)


def per_chiave(delega):
    return {r.chiave: (r.debito, r.credito) for r in delega.righe}


def assorbimenti(delega):
    return [(c.credito, c.debito, c.importo) for c in delega.compensazioni]


def test_un_credito_minore_delle_ritenute_si_compensa_tutto_contro_il_100e(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "30")])
    assert assorbimenti(d) == [(CHIAVE_170E, CHIAVE_100E, D("30"))]
    assert per_chiave(d)[CHIAVE_170E] == (D("0"), D("30"))
    assert d.saldo == D("600") and d.residui == ()


def test_i_debiti_restano_per_intero_e_il_credito_e_una_riga_a_credito(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "30")])
    assert per_chiave(d)[CHIAVE_100E] == (D("100"), D("0"))
    assert d.totale_debito == D("630") and d.totale_credito == D("30")


def test_il_credito_che_supera_le_ritenute_passa_agli_altri_debiti_nell_ordine_delle_sezioni(
    registro, corpus, orologio, ente
):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "300")])
    assert assorbimenti(d) == [
        (CHIAVE_170E, CHIAVE_100E, D("100")),
        (CHIAVE_170E, CHIAVE_104E, D("50")),
        (CHIAVE_170E, CHIAVE_P201, D("150")),
    ]
    assert d.saldo == D("330") and d.residui == ()


def test_la_ritenuta_100e_si_compensa_per_prima_anche_se_non_e_la_prima_riga(registro, corpus, orologio, ente):
    debiti = (("contributo_ente", "480"), ("ritenuta_arretrati", "50"), ("ritenuta_irpef", "100"))
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "120")], debiti)
    assert assorbimenti(d) == [(CHIAVE_170E, CHIAVE_100E, D("100")), (CHIAVE_170E, CHIAVE_104E, D("20"))]


def test_il_credito_maggiore_di_tutti_i_debiti_porta_il_saldo_a_zero_e_resta_visibile(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "1000")])
    assert d.saldo == D("0")
    assert per_chiave(d)[CHIAVE_170E] == (D("0"), D("630"))  # nella delega va solo ciò che è assorbito
    (residuo,) = d.residui
    assert (residuo.chiave, residuo.importo) == (CHIAVE_170E, D("370"))
    assert sum(o.valore for o in residuo.origine) == D("1000")  # la sua origine: le righe pagate del credito


def test_il_credito_uguale_ai_debiti_da_saldo_zero_senza_residuo(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "630")])
    assert d.saldo == D("0") and d.residui == () and d.pronta


def test_piu_crediti_si_compensano_uno_dopo_l_altro_e_il_residuo_e_di_quelli_non_assorbiti(
    registro, corpus, orologio, ente
):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "500"), ("rimborso_irpef_730", "400", 2025)])
    # Ordine dei crediti: sezione, codice, riferimenti (150E prima di 170E)
    assert assorbimenti(d) == [
        (CHIAVE_150E, CHIAVE_100E, D("100")),
        (CHIAVE_150E, CHIAVE_104E, D("50")),
        (CHIAVE_150E, CHIAVE_P201, D("250")),
        (CHIAVE_170E, CHIAVE_P201, D("230")),
    ]
    assert d.saldo == D("0")
    assert [(r.chiave, r.importo) for r in d.residui] == [(CHIAVE_170E, D("270"))]


def test_crediti_con_lo_stesso_codice_e_riferimenti_sono_una_riga_sola(registro, corpus, orologio, ente):
    righe = [riga_a_mano(corpus, VALUTA, i, v) for i, v in DEBITI]
    righe += [riga_a_mano(corpus, VALUTA, "credito_integrativo", v, rapporto=r) for v, r in (("20", R), ("15", R2))]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    d = costruisci_delega(registro, corpus, FEB)
    (credito,) = [r for r in d.righe if r.credito]
    assert credito.credito == D("35") and len(credito.origine) == 2


def test_un_credito_senza_debiti_non_si_porta_in_una_delega_e_nomina_il_caso(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "50")], debiti=())
    assert d.righe == () and not d.pronta
    (fermo,) = d.fermi
    assert fermo.caso == "solo_crediti" and "170E" in fermo.motivo


@pytest.mark.parametrize("credito", ["0.01", "99.99", "100", "100.01", "149.99", "150", "629.99", "630", "630.01", "5000"])
def test_il_saldo_non_e_mai_negativo(registro, corpus, orologio, ente, credito):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", credito)])
    assert d.saldo == max(D("630") - D(credito), D("0"))
    assert d.totale_credito + sum((r.importo for r in d.residui), D("0")) == D(credito)
    assert d.saldo >= 0


def test_le_compensazioni_sommano_il_credito_assorbito(registro, corpus, orologio, ente):
    d = delega_con(registro, corpus, orologio, [("credito_integrativo", "300")])
    assert sum(c.importo for c in d.compensazioni) == d.totale_credito == D("300")
