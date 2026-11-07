"""Vista della delega F24EP dalle righe di composizione degli esiti pagati (ADR 0023). Dati fittizi.

Numeri a mano: stipendio di 1500, ritenuta 100,00, contributo del lavoratore 120,00 e dell'ente 360,00,
che vanno entrambi in P201 per 480,00. Pagamento del 27 febbraio 2026: scadenza il 16 marzo 2026 (lunedì).
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.delega import costruisci_delega

from materiale_delega import (
    R, R2, corpus_delega, dati_ente, paga_a_mano, riga_a_mano,
)
from materiale_proposta import P2, assumi, paga, stipendio

FEB = Mese(2026, 2)
MAR = Mese(2026, 3)
VALUTA = date(2026, 2, 27)
D = Decimal


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))


def pagamento_con_stipendio(registro, corpus, orologio, chiave="pag-1"):
    assumi(registro)
    return paga(registro, corpus, orologio, stipendio(registro, corpus, FEB), VALUTA, chiave)


def delega(registro, corpus, mese=FEB):
    return costruisci_delega(registro, corpus, mese)


def per_codice(d):
    return {(r.sezione, r.tributo, r.codice, r.estremi, r.rif_a, r.rif_b): (r.debito, r.credito) for r in d.righe}


def test_la_delega_somma_per_codice_e_riferimenti_le_righe_del_pagamento(registro, corpus, orologio, ente):
    pagamento_con_stipendio(registro, corpus, orologio)
    d = delega(registro, corpus)
    assert per_codice(d) == {
        ("F", "100E", "", "", "0002", "2026"): (D("100.00"), D("0")),
        ("Q", "P201", "RM", "", "022026", "022026"): (D("480.00"), D("0")),
    }
    assert d.saldo == D("580.00") and d.pronta
    assert d.fermi == () and d.dati_mancanti == ()


def test_la_scadenza_e_la_regola_applicata_al_mese_del_pagamento(registro, corpus, orologio, ente):
    pagamento_con_stipendio(registro, corpus, orologio)
    d = delega(registro, corpus)
    assert d.scadenza.data == date(2026, 3, 16) and d.data_versamento == date(2026, 3, 16)
    assert d.mese_pagamento == FEB


def test_ogni_riga_conserva_il_legame_con_gli_importi_che_la_compongono(registro, corpus, orologio, ente):
    versione = pagamento_con_stipendio(registro, corpus, orologio)
    d = delega(registro, corpus)
    p201 = next(r for r in d.righe if r.tributo == "P201")
    attesi = {
        versione.riferimento(r): r.importo.valore
        for r in versione.righe
        if r.istituto in ("contributo_lavoratore", "contributo_ente")
    }
    assert {o.riferimento: o.valore for o in p201.origine} == attesi
    assert sorted(attesi.values()) == [D("120.00"), D("360.00")]
    assert sum(o.valore for o in p201.origine) == p201.debito


def test_le_righe_sono_nell_ordine_delle_sezioni_della_delega(registro, corpus, orologio, ente):
    pagamento_con_stipendio(registro, corpus, orologio)
    assert [r.sezione for r in delega(registro, corpus).righe] == ["F", "Q"]


def test_un_rapporto_non_pagato_non_entra_mai_nella_delega(registro, corpus, orologio, ente):
    from paghe.proposta import conferma_versione, emetti_versione, registra_pagamento_eseguito

    assumi(registro)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus, FEB) + stipendio(registro, corpus, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    conferma_versione(registro, versione.id)
    registra_pagamento_eseguito(registro, corpus, "pag-1", "adattatore-prova", versione.id, VALUTA, [R])
    d = delega(registro, corpus)
    assert per_codice(d)[("F", "100E", "", "", "0002", "2026")] == (D("100.00"), D("0"))
    assert {o.riferimento.rapporto for r in d.righe for o in r.origine} == {R}


def test_senza_pagamenti_nel_mese_la_delega_e_vuota_e_non_e_pronta(registro, corpus, orologio, ente):
    pagamento_con_stipendio(registro, corpus, orologio)
    d = delega(registro, corpus, MAR)
    assert d.righe == () and not d.pronta and d.sorgenti == ()


def test_entrano_solo_le_righe_con_canale_f24ep(registro, corpus, orologio, ente):
    righe = [riga_a_mano(corpus, VALUTA, i, "50") for i in ("ritenuta_arretrati", "pignoramento")]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    d = delega(registro, corpus)
    assert per_codice(d) == {("F", "104E", "", "", "0002", "2026"): (D("50"), D("0"))}


def test_importi_con_lo_stesso_codice_e_gli_stessi_riferimenti_si_sommano_e_restano_legati(
    registro, corpus, orologio, ente
):
    righe = [riga_a_mano(corpus, VALUTA, "ritenuta_arretrati", v, rapporto=r) for v, r in (("50", R), ("30", R2))]
    versione = paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    d = delega(registro, corpus)
    (riga,) = d.righe
    assert riga.debito == D("80")
    assert {o.riferimento: o.valore for o in riga.origine} == {
        versione.riferimento(r): r.importo.valore for r in versione.righe
    }


def test_riferimenti_diversi_restano_righe_distinte(registro, corpus, orologio, ente):
    from paghe import Periodo

    gennaio = Periodo(date(2026, 1, 1), date(2026, 1, 31))
    righe = [
        riga_a_mano(corpus, VALUTA, "contributo_ente", "10"),
        riga_a_mano(corpus, VALUTA, "contributo_ente", "7", rapporto=R2, periodo=gennaio),
    ]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    assert per_codice(delega(registro, corpus)) == {
        ("Q", "P201", "RM", "", "022026", "022026"): (D("10"), D("0")),
        ("Q", "P201", "RM", "", "012026", "012026"): (D("7"), D("0")),
    }


def test_i_riferimenti_seguono_il_catalogo_per_anno_d_imposta_e_per_mese_di_pagamento(registro, corpus, orologio, ente):
    righe = [
        riga_a_mano(corpus, VALUTA, "rimborso_irpef_730", "40", anno_imposta=2025),
        riga_a_mano(corpus, VALUTA, "credito_integrativo", "20"),
        riga_a_mano(corpus, VALUTA, "ritenuta_arretrati", "500"),
    ]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    assert per_codice(delega(registro, corpus)) == {
        ("F", "104E", "", "", "0002", "2026"): (D("500"), D("0")),
        ("F", "150E", "", "", "", "2025"): (D("0"), D("40")),
        ("F", "170E", "", "", "0002", "2026"): (D("0"), D("20")),
    }
