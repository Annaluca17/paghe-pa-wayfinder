"""Prospetto paga (ticket #86, ADR 0030): vista di un rapporto in un pagamento eseguito, letta dal suo esito pagato.

Corpus reale piu' le dichiarazioni fittizie del mese di prova (composizione, regimi del prospetto). Persone e importi di
fantasia; codici fiscali con carattere di controllo valido.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Atto, Corpus, Mese, TipoEsito, calcola, emetti_esito
from paghe.prospetto_paga import prospetto_paga

RADICE = Path(__file__).resolve().parent.parent
REALE = (RADICE / "corpus" / "funzioni-locali-cpdel.toml").read_text(encoding="utf-8")
FITTIZIO = (RADICE / "prove" / "mese_di_prova" / "corpus_fittizio.toml").read_text(encoding="utf-8")
PAGAMENTO = date(2026, 11, 27)
NOVEMBRE = Mese(2026, 11)
ATTO = Atto("ente:ente_di_prova:determina:2026-01-09;1", date(2026, 1, 9))
DIP, SINDACO, COCO = "R-DIP", "R-SINDACO", "R-COCO"
CF = {DIP: "RSSMRA90A01H501W", SINDACO: "RSSMRA85T01H501M", COCO: "RSSMRA80A01H501U"}


@pytest.fixture(scope="module")
def corpus():
    return Corpus.da_toml(REALE + "\n" + FITTIZIO, reale=False)


def test_il_corpus_dichiara_per_regime_quale_fatto_da_la_posizione(corpus):
    dichiarazioni = corpus.outputs("prospetto_paga", PAGAMENTO)
    assert {d.regime: d.posizione for d in dichiarazioni} == {
        "dipendenti": "qualifica",
        "amministratori": "carica",
        "collaboratori": "incarico",
    }


def persona(registro, rapporto, cognome="PROVA", nome="NOME"):
    registro.registra_codice_persona(f"P-{rapporto}", "codice_fiscale", CF[rapporto], date(1980, 1, 1))
    registro.registra_codice_persona(f"P-{rapporto}", "cognome", cognome, date(1980, 1, 1))
    registro.registra_codice_persona(f"P-{rapporto}", "nome", nome, date(1980, 1, 1))
    registro.collega_rapporto(rapporto, f"P-{rapporto}", date(2026, 1, 1))


def dipendente(registro, qualifica="0FZEQF"):
    persona(registro, DIP)
    registro.registra_codice(DIP, "tipo_impiego", "1", date(2026, 1, 1))
    registro.registra_codice(DIP, "area", "funzionari", date(2026, 1, 1))
    if qualifica is not None:
        registro.registra_codice(DIP, "qualifica", qualifica, date(2026, 1, 1))


def paga(registro, orologio, corpus, rapporto, mese=NOVEMBRE, giorno=PAGAMENTO):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, calcola(registro, corpus, rapporto, mese))
    registro.registra_pagamento(rapporto, esito.id, giorno)
    orologio.avanza()
    return esito


def test_il_prospetto_porta_le_righe_sul_netto_con_periodo_e_segno_e_il_netto(registro, corpus, orologio):
    dipendente(registro)
    esito = paga(registro, orologio, corpus, DIP)
    prospetto = prospetto_paga(registro, corpus, DIP, esito.id)
    assert [(r.istituto, str(r.periodo), r.valore) for r in prospetto.righe_sul_netto] == [
        ("comparto_funzionari", "2026-11-01/2026-11-30", Decimal("36.33")),
        ("tabellare_funzionari", "2026-11-01/2026-11-30", Decimal("2192.02")),
    ]
    assert prospetto.netto == Decimal("2228.35")


def ente(registro):
    registro.registra_codice_ente("codice_fiscale", "01234567897", date(2026, 1, 1))
    registro.registra_codice_ente("denominazione", "ENTE DI PROVA", date(2026, 1, 1))


def test_l_intestazione_porta_ente_persona_posizione_fine_servizio_e_data_di_pagamento(registro, corpus, orologio):
    ente(registro)
    dipendente(registro)
    registro.registra_codice(DIP, "regime_fine_servizio", "3", date(2026, 1, 1))
    esito = paga(registro, orologio, corpus, DIP)
    prospetto = prospetto_paga(registro, corpus, DIP, esito.id)
    assert (prospetto.ente_codice_fiscale, prospetto.ente_denominazione) == ("01234567897", "ENTE DI PROVA")
    assert (prospetto.codice_fiscale, prospetto.cognome, prospetto.nome) == (CF[DIP], "PROVA", "NOME")
    assert (prospetto.posizione, prospetto.fine_servizio, prospetto.data_pagamento) == ("0FZEQF", "3", PAGAMENTO)


def sindaco(registro):
    persona(registro, SINDACO)
    for tipo, valore in (("carica", "sindaco"), ("condizione_lavorativa", "non_dipendente"), ("posizione_previdenziale", "gestione_separata")):
        registro.registra_codice(SINDACO, tipo, valore, date(2026, 1, 1), atto=ATTO)
    registro.registra_fatto(SINDACO, "misura_indennita_funzione", "3000.00", date(2026, 1, 1), atto=ATTO)


def test_le_righe_senza_effetto_sul_netto_stanno_a_parte_e_nessuna_riga_dell_esito_si_perde(registro, corpus, orologio):
    sindaco(registro)
    esito = paga(registro, orologio, corpus, SINDACO)
    prospetto = prospetto_paga(registro, corpus, SINDACO, esito.id)
    assert [(r.istituto, r.valore) for r in prospetto.righe_sul_netto] == [("indennita_funzione", Decimal("3000.00"))]
    assert [(r.istituto, r.valore) for r in prospetto.senza_effetto] == [("onere_art86", Decimal("528.51"))]
    assert prospetto.netto == Decimal("3000.00")
    assert len(prospetto.righe_sul_netto) + len(prospetto.senza_effetto) == len(esito.righe)
    assert prospetto.posizione == "sindaco"
