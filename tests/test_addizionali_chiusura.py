"""Saldo al netto dell'acconto, addizionale a credito e cessazione (ticket #85, ADR 0029). Dati fittizi.

Con la CU 2025 di 18000 l'acconto 2026 del comune X001 e' il 30% di 99,00 = 29,70, in nove rate da 3,30 (marzo-novembre 2026).
Il saldo comunale 2026 e' 99,00 - 29,70 = 69,30, cioe' 6,30 per undici mesi.
Con la CU 2025 di 100000 l'acconto e' il 30% di (75,00 + 85000 x 0,8% = 755,00) = 226,50, oltre i 99,00 dovuti: a credito 127,50.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto

from materiale_addizionali import anno_di_paghe, assumi_a, assumi_fino_al, corpus_addizionali, paga, per_istituto
from materiale_proposta import P

D = Decimal
ATTO_CU = Atto("ente:ente_di_prova:cu:2026-03-16;1", date(2026, 3, 16))
SALDO, REG, CREDITO, REG_CREDITO = (
    "addizionale_comunale_saldo", "addizionale_regionale", "addizionale_comunale_credito", "addizionale_regionale_credito",
)


@pytest.fixture
def corpus():
    return corpus_addizionali()


def anno_con_acconto(registro, orologio, corpus, cu):
    assumi_a(registro)
    registro.registra_reddito_anno_precedente(P, 2025, cu, ATTO_CU)
    return anno_di_paghe(registro, orologio, corpus)


def test_l_acconto_trattenuto_nell_anno_riduce_il_saldo_comunale(registro, orologio, corpus):
    fiscali = anno_con_acconto(registro, orologio, corpus, "18000")
    acconti = [per_istituto(f.addizionali)["addizionale_comunale_acconto"].valore for f in fiscali[2:11]]
    assert acconti == [D("3.30")] * 9
    assert fiscali[-1].addizionali == ()  # nessun credito: l'acconto e' sotto l'addizionale dovuta
    rate = per_istituto(paga(registro, orologio, corpus, date(2027, 1, 27)).addizionali)
    assert rate[SALDO].valore == D("6.30") and rate[REG].valore == D("21.82")  # (99,00 - 29,70) / 11


def test_l_acconto_oltre_l_addizionale_dovuta_si_restituisce_nel_pagamento_del_conguaglio(registro, orologio, corpus):
    fiscali = anno_con_acconto(registro, orologio, corpus, "100000")
    credito = per_istituto(fiscali[-1].addizionali)[CREDITO]
    assert (credito.valore, credito.anno_imposta, credito.derivazione.maturazione) == (D("127.50"), 2026, "addizionale")
    dovuta, *acconti = credito.derivazione.importi
    assert (dovuta.istituto, dovuta.valore) == ("addizionale_comunale_dovuta", D("99.00"))
    assert {i.istituto for i in acconti} == {"addizionale_comunale_acconto"} and sum(i.valore for i in acconti) == D("226.50")
    assert REG_CREDITO not in per_istituto(fiscali[-1].addizionali)


def test_dopo_la_restituzione_non_resta_nulla_da_trattenere_del_saldo_comunale(registro, orologio, corpus):
    anno_con_acconto(registro, orologio, corpus, "100000")
    rate = per_istituto(paga(registro, orologio, corpus, date(2027, 1, 27)).addizionali)
    assert SALDO not in rate and rate[REG].valore == D("21.82")


def test_alla_cessazione_il_residuo_e_le_addizionali_dell_anno_si_trattengono_in_unica_soluzione(registro, orologio, corpus):
    assumi_fino_al(registro, date(2027, 3, 27))
    anno_di_paghe(registro, orologio, corpus)
    paga(registro, orologio, corpus, date(2027, 1, 27), "6000")
    paga(registro, orologio, corpus, date(2027, 2, 27), "6000")
    finale = paga(registro, orologio, corpus, date(2027, 3, 27), "6000", ultimo=True, fino_al=date(2027, 3, 27))
    trattenute = {(i.istituto, i.anno_imposta): i.valore for i in finale.addizionali}
    assert trattenute == {
        (REG, 2026): D("196.36"),  # 240,00 - 2 x 21,82
        (SALDO, 2026): D("81.00"),  # 99,00 - 2 x 9,00
        (REG, 2027): D("240.00"),  # 18000 di reddito 2027 in tre mesi: 180,00 + 60,00
        (SALDO, 2027): D("99.00"),
    }
    assert finale.avvisi_di("acconto_senza_base") == ()  # alla cessazione non c'e' acconto
