"""Scelta del dipendente sulle misure del cuneo fiscale (ticket #125, ADR 0040). Valori e fonti fittizi.

Tre valori: «nel_mese» (predefinito), «solo_conguaglio», «nessuna». Valgono per somma esente, ulteriore detrazione e
trattamento integrativo. Mese per mese conta la scelta in vigore nel mese di pagamento; al conguaglio quella in vigore
alla data del conguaglio, per tutto l'anno. Numeri di materiale_benefici: stipendio di 1000 al mese, somma esente 50,00
e integrativo 100,00 al mese; con stipendio di 2000 l'ulteriore detrazione di prova vale 1000 l'anno (83,33 al mese).
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto, Registro
from paghe.registro import ErroreRegistro

from materiale_benefici import assumi_fino_al, corpus_benefici, del_beneficio, mese_pagato
from test_fiscale import P, assumi

D = Decimal
ATTO = Atto("ente:c_x000:modulo:2026-01-10;1", date(2026, 1, 10))
ISTITUTI = ("somma_esente", "trattamento_integrativo")


def scegli(registro, scelta, dal=date(2026, 1, 1), al=None):
    return registro.registra_scelta_cuneo(P, scelta, dal, al, ATTO)


def istituti(fiscale, suffisso=""):
    """Gli importi dei benefici (o dei recuperi) del pagamento, senza le righe a zero del conguaglio."""
    return {
        i.istituto: i
        for i in fiscale.benefici
        if i.valore and i.istituto.endswith("_recupero") == bool(suffisso)
    }


def anno_intero(registro, orologio, corpus, importo="1000"):
    """Dodici mesi pagati, l'ultimo con il conguaglio; ritorna i dodici esiti fiscali."""
    return [mese_pagato(registro, orologio, corpus, n, importo, ultimo=(n == 12))[1] for n in range(1, 13)]


def totale_imposta(fiscali):
    return sum((f.ritenuta.valore + (f.conguaglio.valore if f.conguaglio else 0) for f in fiscali), D(0))


# Il dato nel registro

def test_senza_il_dato_la_scelta_e_nel_mese(registro, orologio):
    assumi(registro)
    _, fiscale = mese_pagato(registro, orologio, corpus_benefici(), 1)
    assert del_beneficio(fiscale, "somma_esente").valore == D("50.00")


def test_il_dato_vuole_un_valore_noto_e_il_documento_di_origine(registro):
    with pytest.raises(ErroreRegistro):
        registro.registra_scelta_cuneo(P, "forse", date(2026, 1, 1), None, ATTO)
    with pytest.raises(ErroreRegistro):
        registro.registra_scelta_cuneo(P, "nessuna", date(2026, 1, 1), None, None)


def test_nel_mese_scelto_espressamente_come_senza_dato(registro, orologio):
    assumi(registro)
    scegli(registro, "nel_mese")
    _, fiscale = mese_pagato(registro, orologio, corpus_benefici(), 1)
    assert del_beneficio(fiscale, "somma_esente").valore == D("50.00")
    assert del_beneficio(fiscale, "trattamento_integrativo").valore == D("100.00")


# Solo a conguaglio

def test_solo_a_conguaglio_nei_mesi_non_si_da_nulla_e_a_dicembre_tutto_lo_spettante(registro, orologio):
    assumi(registro)
    scegli(registro, "solo_conguaglio")
    fiscali = anno_intero(registro, orologio, corpus_benefici())
    assert all(istituti(f) == {} for f in fiscali[:-1])
    finale = istituti(fiscali[-1])
    # reddito vero 12000: 5% = 600,00 e integrativo 1200,00, nessun gia' riconosciuto
    assert finale["somma_esente"].valore == D("600.00")
    assert finale["trattamento_integrativo"].valore == D("1200.00")


def anno_con_scelta(orologio, scelta, importo="2000"):
    """Un anno intero in un registro nuovo con la scelta data (nessuna se `nel_mese`)."""
    r = Registro(orologio=orologio)
    try:
        assumi(r)
        if scelta != "nel_mese":
            scegli(r, scelta)
        fiscali = anno_intero(r, orologio, corpus_benefici(), importo)
    finally:
        r.chiudi()
        orologio.vai(1, 1, 2026)
    return fiscali


def test_solo_a_conguaglio_l_ulteriore_detrazione_non_riduce_le_ritenute_dei_mesi(registro, orologio):
    nel_mese = anno_con_scelta(orologio, "nel_mese")
    solo = anno_con_scelta(orologio, "solo_conguaglio")
    # reddito 24000: ulteriore detrazione di prova 83,33 al mese
    assert solo[0].ritenuta.valore - nel_mese[0].ritenuta.valore == D("83.33")


def test_l_ulteriore_detrazione_a_conguaglio_pareggia_l_anno_con_nel_mese(registro, orologio):
    # Il totale dell'imposta dell'anno e' lo stesso con «nel mese» e con «solo a conguaglio»: cambia solo quando si da.
    assert totale_imposta(anno_con_scelta(orologio, "nel_mese")) == totale_imposta(anno_con_scelta(orologio, "solo_conguaglio"))


# Nessuna

def test_nessuna_non_da_mai_somma_ne_integrativo_ne_a_conguaglio(registro, orologio):
    assumi(registro)
    scegli(registro, "nessuna")
    fiscali = anno_intero(registro, orologio, corpus_benefici())
    assert all(istituti(f) == {} and istituti(f, "_recupero") == {} for f in fiscali)


def test_nessuna_l_ulteriore_detrazione_non_si_da_nemmeno_a_conguaglio(registro, orologio):
    nel_mese = totale_imposta(anno_con_scelta(orologio, "nel_mese"))
    nessuna = totale_imposta(anno_con_scelta(orologio, "nessuna"))
    # reddito 24000: ulteriore detrazione di prova 1000 l'anno, mai data
    assert nessuna - nel_mese == D("1000.00")


def test_nessuna_a_dicembre_recupera_tutto_il_gia_dato(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    for numero in range(1, 12):
        mese_pagato(registro, orologio, corpus, numero)
    scegli(registro, "nessuna", date(2026, 12, 1))
    _, fiscale = mese_pagato(registro, orologio, corpus, 12, ultimo=True)
    assert istituti(fiscale) == {}
    # gia' dato 550,00 e 1100,00, sopra la soglia di 60: la decisione e' tutto il gia' dato, a rate; la prima nel conguaglio
    decisioni = {
        i.istituto: i.valore for i in fiscale.conguaglio.derivazione.importi if i.derivazione.maturazione == "da_recuperare"
    }
    assert decisioni == {"somma_esente_recupero": D("550.00"), "trattamento_integrativo_recupero": D("1100.00")}
    assert {k: i.valore for k, i in istituti(fiscale, "_recupero").items()} == {
        "somma_esente_recupero": D("55.00"),
        "trattamento_integrativo_recupero": D("137.50"),
    }


# Cambio di scelta a meta' anno

def test_dal_mese_alla_sola_conguaglio_a_meta_anno_il_conguaglio_da_il_resto(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    scegli(registro, "nel_mese", date(2026, 1, 1), date(2026, 6, 30))
    scegli(registro, "solo_conguaglio", date(2026, 7, 1))
    fiscali = anno_intero(registro, orologio, corpus)
    assert all(del_beneficio(f, "somma_esente").valore == D("50.00") for f in fiscali[:6])
    assert all(istituti(f) == {} for f in fiscali[6:11])
    # spettante 600,00 e 1200,00, gia' dati 300,00 e 600,00 nei primi sei mesi
    finale = istituti(fiscali[-1])
    assert finale["somma_esente"].valore == D("300.00")
    assert finale["trattamento_integrativo"].valore == D("600.00")


def test_dal_mese_a_nessuna_a_meta_anno_il_conguaglio_recupera_quanto_dato(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    scegli(registro, "nel_mese", date(2026, 1, 1), date(2026, 6, 30))
    scegli(registro, "nessuna", date(2026, 7, 1))
    fiscali = anno_intero(registro, orologio, corpus)
    assert all(istituti(f) == {} for f in fiscali[6:])
    # dati 300,00 e 600,00: sopra la soglia, a rate (dieci e otto), la prima nel conguaglio
    recuperi = {k: i.valore for k, i in istituti(fiscali[-1], "_recupero").items()}
    assert recuperi == {"somma_esente_recupero": D("30.00"), "trattamento_integrativo_recupero": D("75.00")}


def test_a_conguaglio_vale_la_scelta_in_vigore_alla_sua_data_per_tutto_l_anno(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    scegli(registro, "nessuna", date(2026, 1, 1), date(2026, 11, 30))
    scegli(registro, "nel_mese", date(2026, 12, 1))
    fiscali = anno_intero(registro, orologio, corpus)
    assert all(istituti(f) == {} for f in fiscali[:11])
    # a dicembre «nel mese» e' in vigore: spettante dell'anno intero 600,00 e 1200,00, nulla gia' dato
    finale = istituti(fiscali[-1])
    assert finale["somma_esente"].valore == D("600.00")
    assert finale["trattamento_integrativo"].valore == D("1200.00")


# Cessazione

def test_cessazione_con_solo_a_conguaglio_il_conguaglio_di_fine_rapporto_da_lo_spettante(registro, orologio):
    corpus = corpus_benefici()
    assumi_fino_al(registro, date(2026, 6, 20))
    scegli(registro, "solo_conguaglio")
    for numero in range(1, 6):
        _, fiscale = mese_pagato(registro, orologio, corpus, numero)
        assert istituti(fiscale) == {}
    _, fiscale = mese_pagato(registro, orologio, corpus, 6, ultimo=True)
    finale = istituti(fiscale)
    # reddito vero 7000 (cinque mesi e il pagamento finale con il rateo della tredicesima), rapportato all'anno 14941,52: 5%
    assert finale["somma_esente"].valore == D("350.00")
    assert "scelta" not in finale["somma_esente"].derivazione.formula


def test_cessazione_con_nessuna_recupera_in_unica_soluzione_il_gia_dato(registro, orologio):
    corpus = corpus_benefici()
    assumi_fino_al(registro, date(2026, 6, 20))
    for numero in range(1, 6):
        mese_pagato(registro, orologio, corpus, numero)
    scegli(registro, "nessuna", date(2026, 6, 1))
    _, fiscale = mese_pagato(registro, orologio, corpus, 6, ultimo=True)
    recuperi = istituti(fiscale, "_recupero")
    assert recuperi["somma_esente_recupero"].valore == D("250.00")
    assert recuperi["trattamento_integrativo_recupero"].valore == D("500.00")
    assert "alla cessazione" in recuperi["somma_esente_recupero"].derivazione.formula
    assert istituti(fiscale) == {}


# Tracciabilita'

def test_il_dato_della_scelta_e_nei_fatti_della_derivazione(registro, orologio):
    corpus = corpus_benefici()
    assumi(registro)
    scelta = scegli(registro, "solo_conguaglio")
    fiscali = anno_intero(registro, orologio, corpus)
    assert scelta.id in {f.id for f in fiscali[0].ritenuta.derivazione.fatti}
    assert scelta.id in {f.id for f in istituti(fiscali[-1])["somma_esente"].derivazione.fatti}
