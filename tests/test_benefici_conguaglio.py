"""Somma esente e trattamento integrativo al conguaglio: spettante dell'anno, differenza, recupero a rate (ticket #95).

Valori e fonti fittizi, numeri di materiale_benefici. Undici mesi di 1000 (somma esente 50,00 e integrativo 100,00 al mese:
550,00 e 1100,00 riconosciuti), poi a dicembre un pagamento di 30000: il reddito dell'anno e' 41000, sopra il limite
della somma esente e dell'integrativo, e senza ulteriore detrazione. Spettante zero: da recuperare 550,00 e 1100,00.
"""

from datetime import date
from decimal import Decimal

from paghe import Mese

from materiale_benefici import assumi_fino_al, corpus_benefici, del_beneficio, mese_pagato, paga_con_benefici
from test_fiscale import assumi, stipendio

D = Decimal


def anno_con_premio(registro, orologio, corpus, premio="30000"):
    """Undici mesi di 1000 e il pagamento di dicembre, con il conguaglio."""
    for numero in range(1, 12):
        mese_pagato(registro, orologio, corpus, numero)
    return mese_pagato(registro, orologio, corpus, 12, premio, ultimo=True)


def test_senza_differenza_il_conguaglio_non_cambia_il_riconosciuto(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    _, fiscale = anno_con_premio(registro, orologio, corpus, "1000")
    # spettante: 5% di 12000 = 600,00 e 1200,00; gia' riconosciuti 550,00 e 1100,00: restano 50,00 e 100,00
    assert del_beneficio(fiscale, "somma_esente").valore == D("50.00")
    assert del_beneficio(fiscale, "trattamento_integrativo").valore == D("100.00")
    assert [i.istituto for i in fiscale.benefici if i.istituto.endswith("_recupero")] == []


def test_il_reddito_vero_alza_il_riconosciuto_e_la_differenza_si_paga_nel_conguaglio(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    mese_pagato(registro, orologio, corpus, 1, "700")  # stimato 8241,94: 7% = 49,00; integrativo zero (imposta sotto detrazione)
    for numero in range(2, 12):
        mese_pagato(registro, orologio, corpus, numero)
    _, fiscale = mese_pagato(registro, orologio, corpus, 12, ultimo=True)
    # reddito vero 11700: somma esente 5% = 585,00, riconosciuti 49 + 500 = 549,00; integrativo 1200,00 contro 1000,00
    somma = del_beneficio(fiscale, "somma_esente")
    assert somma.valore == D("36.00") and "spettante dell'anno = 585.00" in somma.derivazione.formula
    assert del_beneficio(fiscale, "trattamento_integrativo").valore == D("200.00")


def test_il_riconosciuto_in_piu_e_un_recupero_a_rate_oltre_la_soglia(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    esito, fiscale = anno_con_premio(registro, orologio, corpus)
    assert del_beneficio(fiscale, "somma_esente").valore == D("0.00")
    assert [i.istituto for i in fiscale.benefici if i.istituto.endswith("_recupero")] == []
    decisioni = [i for i in fiscale.conguaglio.derivazione.importi if i.derivazione.maturazione == "da_recuperare"]
    assert {(i.istituto, i.valore) for i in decisioni} == {
        ("somma_esente_recupero", D("550.00")),
        ("trattamento_integrativo_recupero", D("1100.00")),
    }
    assert "10 rate" in next(i for i in decisioni if i.istituto == "somma_esente_recupero").derivazione.formula


def test_le_rate_partono_dal_pagamento_dopo_il_conguaglio_con_la_derivazione_che_risale_al_conguaglio(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    anno_con_premio(registro, orologio, corpus)
    _, fiscale = mese_pagato(registro, orologio, corpus, 1, anno=2027)
    ti = del_beneficio(fiscale, "trattamento_integrativo_recupero")
    se = del_beneficio(fiscale, "somma_esente_recupero")
    assert (ti.valore, se.valore) == (D("137.50"), D("55.00"))  # 1100 / 8 e 550 / 10
    assert ti.anno_imposta == 2026
    assert ti.derivazione.importi[0].derivazione.maturazione == "conguaglio"
    assert "rate rimaste (8 di 8)" in ti.derivazione.formula


def test_il_recupero_a_rate_finisce_dopo_otto_e_dieci_rate(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    anno_con_premio(registro, orologio, corpus)
    totale = {"trattamento_integrativo_recupero": D(0), "somma_esente_recupero": D(0)}
    for numero in range(1, 13):
        _, fiscale = mese_pagato(registro, orologio, corpus, numero, anno=2027)
        for importo in fiscale.benefici:
            if importo.istituto in totale:
                totale[importo.istituto] += importo.valore
    assert totale == {"trattamento_integrativo_recupero": D("1100.00"), "somma_esente_recupero": D("550.00")}
    assert [i.istituto for i in fiscale.benefici if i.istituto.endswith("_recupero")] == []


def test_una_rata_sola_al_mese_anche_con_due_pagamenti(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    assumi(registro, "RAPPORTO-2")
    anno_con_premio(registro, orologio, corpus)
    mese_pagato(registro, orologio, corpus, 1, anno=2027)
    righe = stipendio(registro, corpus, Mese(2027, 1), "100", "RAPPORTO-2")
    _, secondo = paga_con_benefici(registro, orologio, corpus, righe, date(2027, 1, 28), "RAPPORTO-2")
    assert [i for i in secondo.benefici if i.istituto.endswith("_recupero")] == []


def test_fino_alla_soglia_il_recupero_e_in_unica_soluzione(registro, orologio):
    corpus = corpus_benefici(parametri={"recupero_soglia": "600"})
    assumi(registro)
    _, fiscale = anno_con_premio(registro, orologio, corpus)
    somma = del_beneficio(fiscale, "somma_esente_recupero")
    assert somma.valore == D("550.00") and somma.anno_imposta == 2026
    assert "unica soluzione" in somma.derivazione.formula
    # l'integrativo (1100,00) supera la soglia di 600,00: ha le sue rate, la soglia e' per beneficio
    assert [i.istituto for i in fiscale.benefici if i.istituto == "trattamento_integrativo_recupero"] == []


# Pagamento finale: il recupero e' sempre in unica soluzione

def test_alla_cessazione_il_recupero_e_in_unica_soluzione_qualunque_sia_l_importo(registro, orologio):
    corpus = corpus_benefici()
    assumi_fino_al(registro, date(2026, 12, 20))
    for numero in range(1, 12):
        mese_pagato(registro, orologio, corpus, numero)
    _, fiscale = mese_pagato(registro, orologio, corpus, 12, "30000", ultimo=True)
    assert del_beneficio(fiscale, "somma_esente_recupero").valore == D("550.00")
    assert del_beneficio(fiscale, "trattamento_integrativo_recupero").valore == D("1100.00")
    assert "alla cessazione" in del_beneficio(fiscale, "somma_esente_recupero").derivazione.formula
    assert [i for i in fiscale.conguaglio.derivazione.importi if i.derivazione.maturazione == "da_recuperare"] == []


def test_alla_cessazione_il_residuo_delle_rate_in_corso_si_trattiene_tutto(registro, orologio):
    corpus = corpus_benefici()
    assumi_fino_al(registro, date(2027, 3, 20))
    for numero in range(1, 12):
        mese_pagato(registro, orologio, corpus, numero)
    mese_pagato(registro, orologio, corpus, 12, "30000", ultimo=True)
    mese_pagato(registro, orologio, corpus, 1, anno=2027)
    mese_pagato(registro, orologio, corpus, 2, anno=2027)
    _, fiscale = mese_pagato(registro, orologio, corpus, 3, anno=2027, ultimo=True)
    residui = {i.istituto: i for i in fiscale.benefici if i.istituto.endswith("_recupero") and i.anno_imposta == 2026}
    # due rate gia' trattenute: 1100 - 2 * 137,50 e 550 - 2 * 55,00
    assert residui["trattamento_integrativo_recupero"].valore == D("825.00")
    assert residui["somma_esente_recupero"].valore == D("440.00")
    assert "alla cessazione" in residui["somma_esente_recupero"].derivazione.formula


# Soglia cumulata: il recupero della somma esente si confronta con la soglia al netto dell'ulteriore detrazione in piu'

def test_la_soglia_della_somma_esente_si_guarda_al_netto_dell_ulteriore_detrazione(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    _, fiscale = anno_con_premio(registro, orologio, corpus, "25000")
    # reddito 36000: ulteriore detrazione 1000 * (40000 - 36000) / 8000 = 500,00 mai applicata nelle ritenute dei mesi;
    # da recuperare 550,00, netto 50,00 sotto la soglia di 60: unica soluzione per intero
    somma = del_beneficio(fiscale, "somma_esente_recupero")
    assert somma.valore == D("550.00")
    assert "ulteriore detrazione spettante in più 500.00" in somma.derivazione.formula


def test_un_ulteriore_detrazione_oltre_il_recupero_lo_porta_sotto_la_soglia(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    _, fiscale = anno_con_premio(registro, orologio, corpus, "24000")
    # reddito 35000: ulteriore detrazione 625,00 sopra i 550,00 da recuperare: netto negativo, sotto la soglia. Con un
    # reddito oltre 40000 l'ulteriore detrazione e' zero e il recupero va a rate (vedi sopra)
    assert del_beneficio(fiscale, "somma_esente_recupero").valore == D("550.00")
