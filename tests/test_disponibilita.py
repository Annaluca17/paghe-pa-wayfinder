"""Disponibilità residua di un impegno: la disponibilità meno le righe delle versioni vive (ADR 0031). Dati fittizi.

Lo stipendio di 1500 sul corpus di prova e' la riga della classificazione PIANO.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.errori import ErroreRegistro
from paghe.impegni import disponibilita_residua
from paghe.proposta import conferma_versione, emetti_versione, respingi_versione

from materiale_impegni import PIANO_ENTE, impegno
from materiale_proposta import R, R2, P2, assumi, corpus_p, stipendio

VALUTA = date(2026, 2, 27)
FEB = Mese(2026, 2)


def prepara(registro, corpus, disponibilita="10000"):
    assumi(registro)
    impegno(registro, "I-S", 1, 2026, disponibilita=disponibilita)
    impegno(registro, "I-E", 2, 2026, disponibilita="100000", piano=PIANO_ENTE)
    return stipendio(registro, corpus, FEB)


def residua(registro):
    return disponibilita_residua(registro, 2026, 1)


def test_senza_versioni_la_disponibilita_residua_e_quella_del_fatto(registro, corpus_p):
    prepara(registro, corpus_p)
    assert residua(registro) == Decimal("10000")


def test_una_versione_inviata_consuma_la_riga_abbinata(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p)
    orologio.vai(2, 20)
    emetti_versione(registro, corpus_p, VALUTA, importi)
    assert residua(registro) == Decimal("8500")


def test_una_versione_confermata_consuma_ancora(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    conferma_versione(registro, versione.id)
    assert residua(registro) == Decimal("8500")


def test_una_versione_respinta_libera_la_disponibilita(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    orologio.avanza()
    respingi_versione(registro, versione.id, "importo da rivedere")
    assert residua(registro) == Decimal("10000")


def test_una_versione_superata_libera_la_disponibilita(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    orologio.avanza()
    registro.registra_stato_versione(versione.id, "superata", "fatto cambiato")
    assert residua(registro) == Decimal("10000")


def test_due_versioni_vive_consumano_insieme(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p)
    assumi(registro, R2, P2)
    importi2 = stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    emetti_versione(registro, corpus_p, VALUTA, importi)
    orologio.avanza()
    emetti_versione(registro, corpus_p, VALUTA, importi2)
    assert residua(registro) == Decimal("8000")


def test_le_versioni_registrate_prima_della_data_della_disponibilita_non_contano(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p)
    orologio.vai(2, 20)
    emetti_versione(registro, corpus_p, VALUTA, importi)
    orologio.vai(3, 1)
    impegno(registro, "I-S2", 1, 2026, disponibilita="7000", data=date(2026, 3, 1))  # una disponibilita' nuova: il conto riparte
    assert residua(registro) == Decimal("7000")


def test_le_versioni_registrate_dalla_data_della_disponibilita_in_poi_contano(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p)
    orologio.vai(2, 20)
    impegno(registro, "I-S2", 1, 2026, disponibilita="7000", data=date(2026, 2, 20))  # stessa data della versione
    emetti_versione(registro, corpus_p, VALUTA, importi)
    assert residua(registro) == Decimal("5500")


def test_la_disponibilita_residua_si_legge_a_un_istante_passato(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p)
    orologio.vai(2, 20)
    prima = orologio()
    orologio.avanza()
    emetti_versione(registro, corpus_p, VALUTA, importi)
    assert disponibilita_residua(registro, 2026, 1, prima) == Decimal("10000")


def test_un_impegno_non_noto_e_un_errore(registro):
    with pytest.raises(ErroreRegistro, match="non noto"):
        disponibilita_residua(registro, 2026, 99)


def test_la_seconda_versione_trova_la_disponibilita_gia_consumata_dalla_prima(registro, corpus_p, orologio):
    importi = prepara(registro, corpus_p, disponibilita="2000")
    assumi(registro, R2, P2)
    importi2 = stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    emetti_versione(registro, corpus_p, VALUTA, importi)  # 1500 su 2000: restano 500
    orologio.avanza()
    seconda = emetti_versione(registro, corpus_p, VALUTA, importi2)  # 500: ci sta
    assert {r.impegno for r in seconda.righe_proposta if r.piano_dei_conti != PIANO_ENTE} == {(2026, 1)}
    orologio.avanza()
    assumi(registro, "RAPPORTO-3", "PERSONA-3")
    terzo = stipendio(registro, corpus_p, FEB, "100", "RAPPORTO-3")
    with pytest.raises(ErroreRegistro, match="Nessun rapporto"):
        emetti_versione(registro, corpus_p, VALUTA, terzo)  # 100 su 0 residui
