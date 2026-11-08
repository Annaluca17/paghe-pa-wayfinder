"""Conferma con cambio di abbinamento: la Ragioneria sceglie un altro impegno noto della stessa classificazione (ADR 0031).

Dati fittizi. Lo stipendio di 1500 sul corpus di prova e' la riga della classificazione PIANO.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.errori import ErroreRegistro
from paghe.impegni import abbinamenti_confermati, disponibilita_residua
from paghe.proposta import StatoVersione, conferma_versione, emetti_versione, stato_versione

from materiale_impegni import PIANO, PIANO_ENTE, impegno
from materiale_proposta import assumi_senza_impegni, corpus_p, stipendio

VALUTA = date(2026, 2, 27)
FEB = Mese(2026, 2)


@pytest.fixture
def versione(registro, corpus_p, orologio):
    """Una versione inviata, abbinata all'impegno 2026/1 (il numero piu' basso); il 2026/2 e' un'alternativa."""
    assumi_senza_impegni(registro)
    impegno(registro, "I-1", 1, 2026, disponibilita="10000")
    impegno(registro, "I-2", 2, 2026, disponibilita="10000")
    impegno(registro, "I-E", 3, 2026, disponibilita="100000", piano=PIANO_ENTE)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    inviata = emetti_versione(registro, corpus_p, VALUTA, importi)
    orologio.avanza()
    return inviata


def riga_stipendio(versione):
    return next(r for r in versione.righe_proposta if r.piano_dei_conti == PIANO)


def test_senza_abbinamenti_la_conferma_e_quella_di_prima(registro, versione):
    assert conferma_versione(registro, versione.id) == ()
    assert stato_versione(registro, versione.id) is StatoVersione.CONFERMATA
    assert abbinamenti_confermati(registro, versione.id) == ()


def test_la_ragioneria_sceglie_un_altro_impegno_e_la_traccia_resta_nel_registro(registro, versione):
    riga = riga_stipendio(versione)
    assert conferma_versione(registro, versione.id, {riga.chiave: (2026, 2)}) == ()
    (cambio,) = abbinamenti_confermati(registro, versione.id)
    assert (cambio.riga, cambio.proposto, cambio.scelto) == (riga.chiave, (2026, 1), (2026, 2))
    assert not cambio.incapiente


def test_la_disponibilita_successiva_si_conta_sull_impegno_scelto(registro, versione):
    assert disponibilita_residua(registro, 2026, 1) == Decimal("8500")
    conferma_versione(registro, versione.id, {riga_stipendio(versione).chiave: (2026, 2)})
    assert disponibilita_residua(registro, 2026, 1) == Decimal("10000")
    assert disponibilita_residua(registro, 2026, 2) == Decimal("8500")


def test_un_impegno_non_noto_rifiuta_la_conferma_e_non_la_registra(registro, versione):
    with pytest.raises(ErroreRegistro, match="non noto"):
        conferma_versione(registro, versione.id, {riga_stipendio(versione).chiave: (2026, 99)})
    assert stato_versione(registro, versione.id) is StatoVersione.INVIATA
    assert abbinamenti_confermati(registro, versione.id) == ()


def test_un_impegno_di_un_altra_classificazione_rifiuta_la_conferma(registro, versione):
    with pytest.raises(ErroreRegistro, match="classificazione"):
        conferma_versione(registro, versione.id, {riga_stipendio(versione).chiave: (2026, 3)})  # e' del contributo ente
    assert stato_versione(registro, versione.id) is StatoVersione.INVIATA


def test_una_riga_che_non_e_della_versione_rifiuta_la_conferma(registro, versione):
    with pytest.raises(ErroreRegistro, match="non è una riga"):
        conferma_versione(registro, versione.id, {(PIANO, "09", "09", (2026, 1)): (2026, 2)})
    assert stato_versione(registro, versione.id) is StatoVersione.INVIATA


def test_un_impegno_incapiente_conferma_con_un_avviso_e_lo_registra(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-1", 1, 2026)
    impegno(registro, "I-2", 2, 2026, disponibilita="1000")
    impegno(registro, "I-E", 3, 2026, disponibilita="100000", piano=PIANO_ENTE)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    inviata = emetti_versione(registro, corpus_p, VALUTA, importi)
    avvisi = conferma_versione(registro, inviata.id, {riga_stipendio(inviata).chiave: (2026, 2)})
    assert [a.tipo for a in avvisi] == ["impegno_incapiente"]
    assert "2026/2" in avvisi[0].messaggio and "500" in avvisi[0].messaggio  # 1500 su 1000
    assert stato_versione(registro, inviata.id) is StatoVersione.CONFERMATA
    assert abbinamenti_confermati(registro, inviata.id)[0].incapiente


def test_scegliere_l_impegno_proposto_non_e_un_cambio(registro, versione):
    conferma_versione(registro, versione.id, {riga_stipendio(versione).chiave: (2026, 1)})
    assert abbinamenti_confermati(registro, versione.id) == ()
    assert stato_versione(registro, versione.id) is StatoVersione.CONFERMATA


def test_una_versione_gia_confermata_non_si_riconferma(registro, versione):
    conferma_versione(registro, versione.id)
    with pytest.raises(ErroreRegistro, match="non si conferma"):
        conferma_versione(registro, versione.id, {riga_stipendio(versione).chiave: (2026, 2)})
