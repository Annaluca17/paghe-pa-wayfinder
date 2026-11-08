"""Acconto IRAP, ticket #81 (ADR 0028): base per titolo sul corpus reale, importi ricalcolati a mano.

Aliquota 8,5% (art. 16 c. 2 D.Lgs. 446/1997). Persone, rapporti e importi di fantasia.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Atto, Corpus, Mese, TipoEsito, calcola, calcola_denuncia, emetti_esito
from paghe.errori import CasoNonModellato

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


def esclusione(registro, motivo="disabile", dal=date(2026, 11, 1), al=None):
    registro.registra_codice(R, "esclusione_base_irap", motivo, dal, al, atto=ATTO)


@pytest.mark.parametrize("motivo", ["disabile", "apprendista", "cfl"])
def test_una_persona_esclusa_per_tutto_il_mese_non_ha_ne_base_ne_acconto(registro, reale, orologio, motivo):
    assumi(registro)
    esclusione(registro, motivo)
    paga_il_mese(registro, orologio, reale)
    v = valori(registro, reale)
    assert "base.irap" not in v and "irap_acconto" not in v
    assert v["base.cpdel"] == D("2051.69")  # l'esclusione e' solo dell'IRAP, la previdenza non cambia


def test_l_esclusione_vale_per_i_pagamenti_dopo_la_sua_decorrenza(registro, reale, orologio):
    assumi(registro)
    esclusione(registro, dal=date(2026, 11, 20))
    paga(registro, orologio, calcola(registro, reale, R, Mese(2026, 11)), date(2026, 11, 10))
    (periodo,) = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    assert periodo.base("irap").valore == D("2051.69")  # pagato il 10 novembre: la persona non era ancora esclusa


def test_un_motivo_di_esclusione_non_ammesso_ferma_il_calcolo_e_lo_nomina(registro, reale, orologio):
    assumi(registro)
    esclusione(registro, "motivo_inventato")
    paga_il_mese(registro, orologio, reale)
    with pytest.raises(CasoNonModellato, match="motivo_inventato"):
        calcola_denuncia(registro, reale, R, Mese(2026, 11))


def test_una_regola_regionale_datata_puo_ridurre_l_aliquota_senza_toccare_il_codice(registro, orologio):
    """L'8,5% e' un parametro datato (art. 16 c. 3: le Regioni possono ridurre, non aumentare): un corpus di prova
    lo sostituisce da luglio con un'aliquota regionale fittizia del 7,00%."""
    testo = CORPUS.read_text(encoding="utf-8")
    nazionale = 'valore = "8.50"\nriferimento = "urn:nir:stato:decreto.legislativo:1997-12-15;446~art16-com2"'
    assert nazionale in testo.replace("\r\n", "\n")
    regionale = nazionale + '''

[[parametro.vigenza]]
dal = 2026-07-01
valore = "7.00"
riferimento = "fittizio:legge-regionale-aliquota-irap"'''
    corpus = Corpus.da_toml(testo.replace("\r\n", "\n").replace(nazionale, regionale))
    assumi(registro)
    paga_il_mese(registro, orologio, corpus)
    assert valori(registro, corpus)["irap_acconto"] == D("143.62")  # 2.051,69 x 7,00% = 143,6183, al centesimo


def test_il_corpus_reale_mappa_ogni_regione_al_suo_codice_f24ep(reale):
    def codice(nome):
        voce = reale.mappatura_di_fatto("f24ep.codice_regione", "codice_regione", "sede_lavoro", nome, date(2026, 2, 27))
        return voce.codice if voce else None

    assert codice("lazio") == "08"  # l'esempio ufficiale della tabella AdE (ricerca irap-scadenza-riparto)
    regioni = [
        "abruzzo", "basilicata", "provincia_autonoma_bolzano", "calabria", "campania", "emilia_romagna",
        "friuli_venezia_giulia", "lazio", "liguria", "lombardia", "marche", "molise", "piemonte", "puglia", "sardegna",
        "sicilia", "toscana", "provincia_autonoma_trento", "umbria", "valle_d_aosta", "veneto",
    ]
    assert [codice(nome) for nome in regioni] == [f"{numero:02d}" for numero in range(1, 22)]
    assert codice("atlantide") is None
