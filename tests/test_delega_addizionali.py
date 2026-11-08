"""Addizionali nella delega F24EP (ticket #85, ADR 0029): 381E, 384E, 385E e crediti 160E/161E. Dati fittizi.

Codice regione e codice catastale vengono dal domicilio fiscale della persona al 1° gennaio dell'anno d'imposta della riga;
il riferimento B e' l'anno d'imposta dell'addizionale. Numeri del materiale: dovute 2026 regionale 240,00 e comunale 99,00,
rate di gennaio 2027 21,82 e 9,00; acconto 2027 in rate da 3,30.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto, Corpus, Mese, calcola
from paghe.delega import costruisci_delega

from materiale_addizionali import assumi_a, testo
from materiale_delega import MAPPATURE_DEL_CICLO, _codice, _mappatura, dati_ente, toml_scadenza
from materiale_proposta import P, R, paga as paga_proposta

D = Decimal
ATTO_CU = Atto("ente:ente_di_prova:cu:2026-03-16;1", date(2026, 3, 16))

CODICI = "".join(
    _codice(*voce)
    for voce in (
        ("100E", "F", "nessuno", "nessuno", "mese_pagamento", "anno_pagamento", "debito"),
        ("P201", "Q", "provincia", "facoltativo", "periodo_inizio", "periodo_fine", "debito"),
        ("381E", "R", "regione", "nessuno", "nessuno", "anno_imposta", "debito"),
        ("384E", "S", "catastale", "nessuno", "nessuno", "anno_imposta", "debito"),
        ("385E", "S", "catastale", "nessuno", "nessuno", "anno_imposta", "debito"),
        ("160E", "R", "regione", "nessuno", "nessuno", "anno_imposta", "debito_credito"),
        ("161E", "S", "catastale", "nessuno", "nessuno", "anno_imposta", "debito_credito"),
    )
)
MAPPATURE = "".join(
    _mappatura(istituto, codice)
    for istituto, codice in (
        ("addizionale_regionale", "381E"),
        ("addizionale_comunale_saldo", "384E"),
        ("addizionale_comunale_acconto", "385E"),
        ("addizionale_regionale_credito", "160E"),
        ("addizionale_comunale_credito", "161E"),
    )
)


@pytest.fixture
def corpus():
    return Corpus.da_toml(testo() + MAPPATURE_DEL_CICLO + MAPPATURE + CODICI + toml_scadenza())


def paga_il(registro, orologio, corpus, valuta, importo="1500"):
    registro.registra_fatto(R, "mensile", importo, valuta.replace(day=1), valuta.replace(day=28))
    righe = [r for r in calcola(registro, corpus, R, Mese(valuta.year, valuta.month)) if r.istituto == "stipendio"]
    return paga_proposta(registro, corpus, orologio, righe, valuta, f"pag-{valuta}")


def anno_2026(registro, orologio, corpus):
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    for mese in range(1, 13):
        paga_il(registro, orologio, corpus, date(2026, mese, 18))


def delega_di(registro, corpus, anno, mese):
    registro.registra_data_versamento(Mese(anno, mese), date(anno + (mese == 12), mese % 12 + 1, 16))
    return costruisci_delega(registro, corpus, Mese(anno, mese))


def riga(delega, tributo):
    (trovata,) = [r for r in delega.righe if r.tributo == tributo]
    return trovata


@pytest.fixture
def ente(registro):
    dati_ente(registro)


def test_la_rata_regionale_e_comunale_del_saldo_vanno_in_381E_e_384E_con_il_codice_del_domicilio(registro, orologio, corpus, ente):
    assumi_a(registro)
    anno_2026(registro, orologio, corpus)
    paga_il(registro, orologio, corpus, date(2027, 1, 18))
    d = delega_di(registro, corpus, 2027, 1)
    regionale, comunale = riga(d, "381E"), riga(d, "384E")
    assert (regionale.sezione, regionale.codice, regionale.rif_b, regionale.debito) == ("R", "98", "2026", D("21.82"))
    assert (comunale.sezione, comunale.codice, comunale.rif_b, comunale.debito) == ("S", "X001", "2026", D("9.00"))
    assert d.fermi == () and d.dati_mancanti == ()


def test_l_acconto_va_in_385E_con_l_anno_dell_acconto(registro, orologio, corpus, ente):
    assumi_a(registro)
    registro.registra_reddito_anno_precedente(P, 2025, "18000", ATTO_CU)
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    paga_il(registro, orologio, corpus, date(2026, 3, 18))
    d = delega_di(registro, corpus, 2026, 3)
    acconto = riga(d, "385E")
    assert (acconto.codice, acconto.rif_b, acconto.debito) == ("X001", "2026", D("3.30"))


def test_l_addizionale_a_credito_e_una_riga_161E_e_160E_si_compensa_con_i_debiti(registro, orologio, corpus, ente):
    assumi_a(registro)
    registro.registra_reddito_anno_precedente(P, 2025, "100000", ATTO_CU)
    anno_2026(registro, orologio, corpus)
    d = delega_di(registro, corpus, 2026, 12)
    credito = riga(d, "161E")
    assert (credito.sezione, credito.codice, credito.rif_b, credito.credito, credito.debito) == ("S", "X001", "2026", D("127.50"), D("0"))
    assert d.fermi == () and d.residui == ()


def test_senza_il_domicilio_fiscale_la_delega_lo_chiede_come_dato_mancante(registro, orologio, corpus, ente):
    assumi_a(registro)
    anno_2026(registro, orologio, corpus)
    paga_il(registro, orologio, corpus, date(2027, 1, 18))
    domicilio = registro.fatti_persona_noti(P, "domicilio_fiscale", registro.adesso())[0]
    registro.annulla_fatto(domicilio.id, "domicilio inserito per errore")
    d = delega_di(registro, corpus, 2027, 1)
    assert [m.tipo for m in d.dati_mancanti] == ["domicilio_fiscale"]
    assert [r.tributo for r in d.righe if r.tributo in ("381E", "384E")] == []
    assert not d.pronta
