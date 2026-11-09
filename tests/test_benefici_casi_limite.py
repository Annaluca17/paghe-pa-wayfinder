"""Casi limite di somma esente e recuperi (ticket #95, rilettura). Valori e fonti fittizi, numeri di materiale_benefici.

Somma esente: 7% fino a 8500, 5% fino a 15000, 4% fino a 20000. La percentuale si sceglie sul reddito di lavoro
dipendente rapportato all'intero anno, il limite dei 20000 resta sul reddito vero (L. 207/2024 art. 1 c. 4-5).
"""

from datetime import date
from decimal import Decimal

from materiale_benefici import assumi_fino_al, corpus_benefici, del_beneficio, mese_pagato

D = Decimal
LUGLIO = date(2026, 7, 1)
OLTRE = date(2027, 12, 31)


def da_luglio(registro, orologio, corpus, importo):
    """Assunta il 1° luglio: cinque mesi pagati, poi dicembre con il conguaglio."""
    assumi_fino_al(registro, OLTRE, dal=LUGLIO)
    for numero in range(7, 12):
        mese_pagato(registro, orologio, corpus, numero, importo)
    return mese_pagato(registro, orologio, corpus, 12, importo, ultimo=True)


def test_al_conguaglio_la_percentuale_si_sceglie_sul_reddito_rapportato_all_anno(registro, orologio):
    _, fiscale = da_luglio(registro, orologio, corpus_benefici(), "1500")
    # reddito vero 9000, rapportato all'anno 9000 * 365 / 184 = 17853,26: 4%, non il 5% del reddito vero
    somma = del_beneficio(fiscale, "somma_esente")
    assert "spettante dell'anno = 360.00" in somma.derivazione.formula
    assert somma.valore == D("60.00")  # 4% di 9000 meno i 5 mesi gia' riconosciuti (4% di 1500 = 60,00 al mese)


def test_il_limite_dei_20000_resta_sul_reddito_vero_anche_se_quello_rapportato_lo_supera(registro, orologio):
    _, fiscale = da_luglio(registro, orologio, corpus_benefici(), "2000")
    # nei mesi lo stimato e' circa 23500: niente somma esente; reddito vero 12000, sotto i 20000: spetta il 4%
    somma = del_beneficio(fiscale, "somma_esente")
    assert "spettante dell'anno = 480.00" in somma.derivazione.formula
    assert somma.valore == D("480.00")


def test_un_recupero_pari_alla_soglia_e_in_unica_soluzione(registro, orologio):
    corpus = corpus_benefici(parametri={"recupero_soglia": "550"})
    assumi_fino_al(registro, OLTRE)
    for numero in range(1, 12):
        mese_pagato(registro, orologio, corpus, numero)
    _, fiscale = mese_pagato(registro, orologio, corpus, 12, "30000", ultimo=True)
    somma = del_beneficio(fiscale, "somma_esente_recupero")
    assert somma.valore == D("550.00") and "unica soluzione" in somma.derivazione.formula
