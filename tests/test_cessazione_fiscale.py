"""Conguaglio fiscale al pagamento finale della persona, alla cessazione (ticket #70, ADR 0019). Dati fittizi.

La fine del servizio è la fine del fatto di servizio del corpus (`tipo_impiego`). Un pagamento è finale se, alla sua valuta
prevista, nessun rapporto della persona ha più servizio nell'anno d'imposta. Il conguaglio è della persona.

Numeri sul corpus di materiale_proposta con la franchigia annua a 1200 (ragguagliata al mese 100), aliquota 20%:
  stipendio 1500: ritenuta (1500 - 100) * 0,20 = 280,00; imposta dell'anno (1500 - 1200) * 0,20 = 60,00;
  conguaglio = 60,00 - 280,00 = -220,00.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese, calcola
from paghe.proposta import emetti_versione

from materiale_proposta import CF, IBAN, P, R, corpus_proposta, per_istituto, stipendio


@pytest.fixture
def corpus_c():
    return corpus_proposta(franchigia="1200")


def assumi_fino_al(registro, rapporto, persona, al=None, dal=date(2026, 1, 1)):
    """Un rapporto con il servizio dal `dal` e, se c'è `al`, cessato in quella data."""
    if not registro.fatti_persona_noti(persona, "codice_fiscale", registro.adesso()):
        registro.registra_codice_persona(persona, "codice_fiscale", CF, date(1980, 1, 1))
        registro.registra_iban_persona(persona, IBAN, date(2026, 1, 1))
    registro.collega_rapporto(rapporto, persona, dal)
    registro.registra_codice(rapporto, "tipo_impiego", "1", dal, al)


def stipendio_fino_al(registro, corpus, mese, al, importo="1500", rapporto=R):
    """Lo stipendio del mese del rapporto cessato in `al`: il fatto mensile dura fino alla cessazione."""
    registro.registra_fatto(rapporto, "mensile", importo, mese.primo_giorno, al)
    return [riga for riga in calcola(registro, corpus, rapporto, mese) if riga.istituto == "stipendio"]


def test_il_pagamento_dopo_la_cessazione_porta_il_conguaglio_senza_il_fatto_dell_ente(registro, corpus_c, orologio):
    assumi_fino_al(registro, R, P, al=date(2026, 3, 14))
    importi = stipendio_fino_al(registro, corpus_c, Mese(2026, 3), date(2026, 3, 14))
    orologio.vai(3, 20)
    versione = emetti_versione(registro, corpus_c, date(2026, 3, 27), importi)
    righe = per_istituto(versione.righe)
    assert (righe["ritenuta_irpef"].importo.valore, righe["conguaglio_irpef"].importo.valore) == (
        Decimal("280.00"),
        Decimal("-220.00"),
    )
    assert [a.tipo for a in versione.avvisi if a.tipo == "proiezione_conguaglio"] == []
    assert versione.dati_mancanti == ()
