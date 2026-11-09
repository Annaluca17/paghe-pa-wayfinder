"""Somma esente e trattamento integrativo nel pagamento del mese (ticket #95, ADR 0019). Valori e fonti fittizi.

Vedi materiale_benefici per i numeri: stipendio di 1000 al mese, integrativo 100,00 e somma esente 50,00 al mese.
"""

from datetime import date
from decimal import Decimal

from paghe import Corpus, Mese, calcola, imponibile_fiscale

from materiale_benefici import (
    beneficio,
    corpus_benefici,
    del_beneficio,
    mese_pagato,
    paga_con_benefici,
    parametri_benefici,
)
from test_fiscale import ALTRO, P, R, TESTO, assumi, stipendio

D = Decimal


def test_somma_esente_e_trattamento_integrativo_di_un_mese_pieno(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    for numero in range(1, 6):
        _, fiscale = mese_pagato(registro, orologio, corpus, numero)
    # stimato 5000 in 151 giorni -> 12091,39: fascia del 5% su 1000 = 50,00; integrativo 1200 / 12 = 100,00
    assert del_beneficio(fiscale, "somma_esente").valore == D("50.00")
    integrativo = del_beneficio(fiscale, "trattamento_integrativo")
    assert integrativo.valore == D("100.00")
    assert integrativo.derivazione.maturazione == "beneficio"
    assert integrativo.anno_imposta == 2026


def test_la_derivazione_porta_formula_parametri_e_importi_letti(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    _, fiscale = mese_pagato(registro, orologio, corpus, 6)
    derivazione = del_beneficio(fiscale, "trattamento_integrativo").derivazione
    assert "parametro.ti_importo" in derivazione.formula  # la formula e' il testo del corpus
    assert {"ti_importo", "ti_soglia_1", "ti_riduzione"} <= {p.nome for p in derivazione.parametri}
    assert all(p.riferimento.startswith("fittizio:") for p in derivazione.parametri)
    assert [i.istituto for i in derivazione.importi] == ["stipendio"]
    assert "reddito annuo stimato" in derivazione.formula and "detrazione dell'art. 13 = 70.00" in derivazione.formula


def test_oltre_il_limite_la_somma_esente_e_zero(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    for numero in range(1, 4):
        _, fiscale = mese_pagato(registro, orologio, corpus, numero, "2000")  # 6000 in 90 giorni: 24333 euro l'anno
    assert del_beneficio(fiscale, "somma_esente").valore == D("0.00")
    assert del_beneficio(fiscale, "trattamento_integrativo").valore == D("0.00")


def test_i_benefici_non_sono_reddito_ne_cambiano_l_imponibile_e_la_ritenuta(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    mese_pagato(registro, orologio, corpus, 1)
    _, fiscale = mese_pagato(registro, orologio, corpus, 2)
    assert del_beneficio(fiscale, "somma_esente").valore > 0
    assert imponibile_fiscale(registro, P, 2026).valore == D("2000")
    # ritenuta come senza benefici: 116,67 (imposta del mese) meno nessuna detrazione senza dichiarazione
    assert fiscale.ritenuta.valore == D("116.67")


def test_tra_15000_e_28000_conta_la_differenza_tra_detrazioni_e_imposta_lorda(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    _, fiscale = mese_pagato(registro, orologio, corpus, 1, "1500")
    # imposta 216,67 oltre la detrazione 55,00: senza oneri comunicati nulla
    assert del_beneficio(fiscale, "trattamento_integrativo").valore == D("0.00")


def test_gli_oneri_comunicati_dalla_persona_si_sommano_alle_detrazioni_note(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    registro.registra_fatto_persona(P, "oneri_detraibili", "3000", date(2026, 1, 1))
    _, fiscale = mese_pagato(registro, orologio, corpus, 1, "1500")
    # 55,00 + 3000 / 12 - 216,67 = 88,33, sotto il tetto di 100,00 al mese
    integrativo = del_beneficio(fiscale, "trattamento_integrativo")
    assert integrativo.valore == D("88.33")
    assert [f.tipo for f in integrativo.derivazione.fatti] == ["oneri_detraibili"]


def test_il_secondo_pagamento_del_mese_porta_solo_la_differenza(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    assumi(registro, ALTRO)
    _, primo = mese_pagato(registro, orologio, corpus, 1, "700")
    # stimato 700 in 31 giorni: 8241,94 -> 7% di 700 = 49,00
    assert del_beneficio(primo, "somma_esente").valore == D("49.00")
    righe = stipendio(registro, corpus, Mese(2026, 1), "300", ALTRO)
    _, secondo = paga_con_benefici(registro, orologio, corpus, righe, date(2026, 1, 28), ALTRO)
    # reddito del mese 1000, stimato 11774,19 -> 5% di 1000 = 50,00 meno i 49,00 gia' riconosciuti
    assert del_beneficio(secondo, "somma_esente").valore == D("1.00")


def test_il_reddito_annuo_stimato_conta_i_giorni_di_servizio_dall_assunzione(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro, dal=date(2026, 7, 1))
    _, fiscale = mese_pagato(registro, orologio, corpus, 7)
    somma = del_beneficio(fiscale, "somma_esente")
    # 1000 in 31 giorni di servizio: 11774,19 -> fascia del 5%
    assert somma.valore == D("50.00")
    assert "11774.19" in somma.derivazione.formula and "31 giorni di servizio per 365" in somma.derivazione.formula


def test_la_carica_elettiva_non_ha_il_trattamento_integrativo(registro, orologio):
    testo = TESTO.replace('categorie = ["lavoro_dipendente"]', 'categorie = ["lavoro_dipendente", "carica_elettiva"]')
    corpus = Corpus.da_toml(testo + parametri_benefici() + beneficio())
    assumi(registro)
    registro.registra_fatto(R, "gettone", "800", date(2026, 3, 1), date(2026, 3, 31))
    righe = calcola(registro, corpus, R, Mese(2026, 3))
    _, fiscale = paga_con_benefici(registro, orologio, corpus, righe, date(2026, 3, 27))
    assert fiscale.benefici == ()
