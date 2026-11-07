"""Esiti con righe derivate (contributi, ritenute) e scritture atomiche del registro (ADR 0025). Dati fittizi."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, TipoEsito, calcola, differenze, emetti_esito
from paghe.errori import ErroreRegistro

from conftest import CORPUS_BASE

R = "RAPPORTO-1"
FEB = Mese(2026, 2)


CON_CONTRIBUTI = CORPUS_BASE + """
[periodo_dichiarato]
servizio = "compenso_mensile"

[[base]]
nome = "pens"
riferimento = "fittizio:base-pens"

[[regola]]
istituto = "contributo"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:contributo"
formula = "arrotonda(base.pens * parametro.aliquota, 2)"
maturazione = "periodo"

[[concorso]]
istituto = "compenso"
basi = ["pens"]
misura = "intero"
dal = 2026-01-01
riferimento = "fittizio:concorso-compenso"
"""


def compenso(registro, corpus):
    registro.registra_fatto(R, "compenso_mensile", "1000", date(2026, 1, 1))
    (riga,) = (r for r in calcola(registro, corpus, R, FEB) if r.istituto == "compenso")
    return riga


def derivata(riga, istituto, maturazione, valore, esiti=()):
    return replace(
        riga,
        istituto=istituto,
        valore=Decimal(valore),
        esiti_confrontati=tuple(esiti),
        derivazione=replace(riga.derivazione, istituto=istituto, maturazione=maturazione),
    )


# Due volte lo stesso importo: il contributo per differenza è un altro importo

def test_lo_stesso_importo_due_volte_nello_stesso_esito_e_rifiutato(registro, corpus):
    riga = compenso(registro, corpus)
    with pytest.raises(ErroreRegistro, match="due volte"):
        emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), [riga, riga])


def test_un_importo_e_la_sua_differenza_stanno_nello_stesso_esito(registro, corpus):
    """Due pagamenti dello stesso mese, versati insieme: i contributi per differenza hanno la stessa chiave."""
    riga = compenso(registro, corpus)
    primo = derivata(riga, "contributo", "periodo", "100")
    secondo = derivata(riga, "contributo", "periodo", "20", esiti=(1,))
    esito = emetti_esito(registro, TipoEsito.VERSATO, date(2026, 3, 16), [primo, secondo])
    assert [r.valore for r in esito.righe] == [Decimal("100"), Decimal("20")]


def test_due_differenze_dagli_stessi_esiti_sono_ancora_lo_stesso_importo(registro, corpus):
    riga = compenso(registro, corpus)
    uno = derivata(riga, "contributo", "periodo", "20", esiti=(1,))
    due = derivata(riga, "contributo", "periodo", "30", esiti=(1,))
    with pytest.raises(ErroreRegistro, match="due volte"):
        emetti_esito(registro, TipoEsito.VERSATO, date(2026, 3, 16), [uno, due])


# Le righe derivate non sono dovuto per competenza

def test_le_righe_derivate_di_un_esito_pagato_non_entrano_nelle_differenze(registro, orologio):
    """Il contributo nell'esito deriva dal pagato: `differenze` non lo confronta con il calcolo per competenza."""
    corpus = Corpus.da_toml(CON_CONTRIBUTI)
    riga = compenso(registro, corpus)
    righe = [riga, derivata(riga, "contributo", "periodo", "100")]
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), righe)
    registro.registra_pagamento(R, esito.id, date(2026, 2, 27))
    assert {d.istituto for d in differenze(registro, corpus, R, FEB, TipoEsito.PAGATO)} == {"ritenuta"}


# Scritture atomiche

def test_piu_scritture_atomiche_o_tutte_o_nessuna(registro, orologio):
    with pytest.raises(RuntimeError):
        with registro.atomico():
            registro.registra_fatto(R, "x", "1", date(2026, 1, 1))
            registro.registra_codice_ente("denominazione", "Ente di prova", date(2026, 1, 1))
            raise RuntimeError("guasto a metà")
    assert registro.fatti_noti(R, "x", orologio()) == []
    assert registro.fatti_ente_noti("denominazione", orologio()) == []


def test_le_scritture_atomiche_riuscite_restano(registro, orologio):
    with registro.atomico():
        registro.registra_fatto(R, "x", "1", date(2026, 1, 1))
        registro.registra_fatto(R, "y", "2", date(2026, 1, 1))
    assert len(registro.fatti_noti(R, "x", orologio())) == 1
    assert len(registro.fatti_noti(R, "y", orologio())) == 1


def test_dopo_un_annullamento_l_orologio_non_resta_avanti(registro, orologio):
    """Una scrittura annullata non lascia un «ultimo istante» che blocca l'orologio."""
    orologio.vai(6, 1)
    with pytest.raises(RuntimeError):
        with registro.atomico():
            registro.registra_fatto(R, "x", "1", date(2026, 1, 1))
            raise RuntimeError("guasto")
    orologio.vai(5, 1)
    registro.registra_fatto(R, "x", "1", date(2026, 1, 1))
