"""Acconto IRAP, ticket #81 (ADR 0028): base per titolo sul corpus reale, importi ricalcolati a mano.

Aliquota 8,5% (art. 16 c. 2 D.Lgs. 446/1997). Persone, rapporti e importi di fantasia.
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
D = Decimal


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def assumi(registro, area="istruttori", dal=date(2026, 1, 1)):
    registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(R, "PERSONA-1", dal)
    registro.registra_codice(R, "tipo_impiego", "1", dal)
    registro.registra_codice(R, "area", area, dal)


def paga(registro, orologio, righe, giorno):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(R, esito.id, giorno)
    orologio.avanza()


def paga_il_mese(registro, orologio, reale, mese=Mese(2026, 11), giorno=date(2026, 11, 27)):
    paga(registro, orologio, calcola(registro, reale, R, mese), giorno)


def valori(registro, reale, mese=Mese(2026, 11)):
    (periodo,) = calcola_denuncia(registro, reale, R, mese).periodi
    return {riga.istituto: riga.valore for riga in (*periodo.basi, *periodo.contributi)}


def test_un_dipendente_ha_l_acconto_all_8_5_sull_imponibile_previdenziale_del_pagamento(registro, reale, orologio):
    assumi(registro)
    paga_il_mese(registro, orologio, reale)
    v = valori(registro, reale)
    assert v["base.irap"] == D("2051.69")
    assert v["irap_acconto"] == D("174.39")  # 2.051,69 x 8,5% = 174,393..., al centesimo


def collabora(registro, orologio, reale, importo="1000.00", posizione="gestione_separata"):
    registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(R, "PERSONA-1", date(2026, 1, 1))
    registro.registra_codice(R, "posizione_previdenziale", posizione, date(2026, 1, 1), atto=ATTO)
    registro.registra_fatto(R, "rata_collaborazione", importo, date(2026, 11, 30), date(2026, 11, 30), atto=ATTO)
    paga_il_mese(registro, orologio, reale, giorno=date(2026, 11, 30))


def test_un_cococo_ha_la_base_al_netto_della_quota_di_gestione_separata_a_carico_del_collaboratore(registro, reale, orologio):
    collabora(registro, orologio, reale)
    v = valori(registro, reale)
    assert v["gs_lavoratore"] == D("116.77")
    # (1.000,00 - 116,77) x 8,5% = 75,07455: scelta di Luca, fonte non leggibile, da verificare (ADR 0028)
    assert v["irap_acconto"] == D("75.07")


def mandato(registro, orologio, reale, condizione="non_dipendente", misura="3000.00"):
    registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1972, 10, 9))
    registro.collega_rapporto(R, "PERSONA-1", date(2026, 1, 1))
    for tipo, valore in (("carica", "sindaco"), ("condizione_lavorativa", condizione), ("posizione_previdenziale", "gestione_separata")):
        registro.registra_codice(R, tipo, valore, date(2026, 1, 1), atto=ATTO)
    registro.registra_fatto(R, "misura_indennita_funzione", misura, date(2026, 1, 1), atto=ATTO)
    paga_il_mese(registro, orologio, reale, giorno=date(2026, 11, 30))


def test_un_amministratore_ha_la_base_sull_indennita_di_funzione_e_fuori_l_onere_dell_art_86(registro, reale, orologio):
    mandato(registro, orologio, reale)
    v = valori(registro, reale)
    assert v["base.irap"] == D("3000.00")
    assert v["irap_acconto"] == D("255.00")  # 3.000,00 x 8,5%; la quota art. 86 e' un onere dell'ente, non entra


def test_l_indennita_dimezzata_entra_nella_base_per_l_importo_pagato(registro, reale, orologio):
    mandato(registro, orologio, reale, condizione="dipendente_senza_aspettativa")
    v = valori(registro, reale)
    assert v["base.irap"] == D("1500.00")  # 3.000,00 meno il dimezzamento di 1.500,00 (art. 82 c. 1 TUEL)
    assert v["irap_acconto"] == D("127.50")
