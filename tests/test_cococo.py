"""Regimi del titolo, PR B del ticket #73: co.co.co. (corpus reale).

Gli importi attesi sono ricalcolati a mano dalle fonti: Circ. INPS 8/2026 (aliquote, ripartizione 2/3 e 1/3, massimale
122.295 euro). Compensi di fantasia (input da atto, nessuna norma). Persone e rapporti di fantasia.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Atto, Corpus, Mese, TipoEsito, calcola, calcola_denuncia, emetti_esito

CORPUS = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
R = "RAPPORTO-1"
CF = "RSSMRA80A01H501U"
ATTO = Atto("ente:ente_di_prova:determina:2026-01-09;1", date(2026, 1, 9))


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def collaboratore(registro, posizione="gestione_separata", dal=date(2026, 1, 1)):
    registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(R, "PERSONA-1", dal)
    if posizione is not None:
        registro.registra_codice(R, "posizione_previdenziale", posizione, dal, atto=ATTO)


def rata(registro, importo, giorno):
    return registro.registra_fatto(R, "rata_collaborazione", importo, giorno, giorno, atto=ATTO)


def importi(registro, corpus, mese):
    return {riga.istituto: riga.valore for riga in calcola(registro, corpus, R, mese)}


def test_la_rata_del_piano_matura_come_evento_nel_giorno_della_scadenza(registro, reale):
    collaboratore(registro)
    rata(registro, "1500.00", date(2026, 11, 30))
    (riga,) = calcola(registro, reale, R, Mese(2026, 11))
    assert (riga.istituto, riga.valore, riga.derivazione.maturazione) == ("compenso_collaborazione", Decimal("1500.00"), "evento")
    assert riga.periodo.dal == riga.periodo.al == date(2026, 11, 30)
