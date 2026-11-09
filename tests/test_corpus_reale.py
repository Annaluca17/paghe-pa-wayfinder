"""Corpus reale CPDEL del comparto Funzioni Locali (ticket #29, parte 2).

Gli importi attesi sono ricalcolati a mano dalle fonti del corpus: CCNL 28/10/2026 tab. B e C,
L. 296/2006, L. 662/1996, D.L. 384/1992, Circ. INPS 6/2026. Persone e rapporti sono di fantasia.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Corpus, Mese, TipoEsito, calcola, calcola_denuncia, differenze, emetti_esito, spiega
from paghe.errori import CasoNonModellato, ParametroMancante

CORPUS = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
R = "RAPPORTO-1"
CF = "RSSMRA80A01H501U"


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def assumi(registro, area, dal=date(2026, 1, 1), al=None):
    fatti = [
        registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1980, 1, 1)),
        registro.collega_rapporto(R, "PERSONA-1", dal),
        registro.registra_codice(R, "tipo_impiego", "1", dal, al),
        registro.registra_codice(R, "area", area, dal, al),
    ]
    return fatti


def stipendi(registro, corpus, *mesi):
    return [riga for mese in mesi for riga in calcola(registro, corpus, R, mese)]


def paga(registro, orologio, righe, giorno):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(R, esito.id, giorno)
    orologio.avanza()
    return esito


def importi(periodo):
    return {riga.istituto: riga.valore for riga in (*periodo.basi, *periodo.contributi)}


def test_il_corpus_reale_si_carica_senza_riferimenti_fittizi(reale):
    assert reale.reale
    assert "fittizio:" not in CORPUS.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("area", "tabellare", "comparto"),
    [
        ("funzionari", "2192.02", "36.33"),
        ("istruttori", "2019.63", "32.06"),
        ("operatori_esperti", "1796.60", "27.52"),
        ("operatori", "1724.21", "22.68"),
    ],
)
def test_tabellare_e_comparto_mensili_2026(registro, reale, area, tabellare, comparto):
    assumi(registro, area)
    assert {riga.istituto: riga.valore for riga in calcola(registro, reale, R, Mese(2026, 11))} == {
        f"tabellare_{area}": Decimal(tabellare),
        f"comparto_{area}": Decimal(comparto),
    }


def test_tabellare_2027(registro, reale):
    assumi(registro, "istruttori")
    righe = {riga.istituto: riga.valore for riga in calcola(registro, reale, R, Mese(2027, 1))}
    assert righe["tabellare_istruttori"] == Decimal("2055.86")


def test_comparto_oltre_giugno_2027_ferma_il_calcolo(registro, reale):
    assumi(registro, "istruttori")
    assert calcola(registro, reale, R, Mese(2027, 6))
    with pytest.raises(ParametroMancante, match="comparto"):
        calcola(registro, reale, R, Mese(2027, 7))


def test_denuncia_di_un_mese_intero(registro, reale, orologio):
    assumi(registro, "istruttori")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    assert importi(periodo) == {
        "base.cpdel": Decimal("2051.69"),
        "base.fondo_credito": Decimal("2051.69"),
        "base.tfs": Decimal("2019.63"),  # senza regime: base sì, contributo TFS no (ticket #33)
        "base.irap": Decimal("2051.69"),  # come la base CPDEL (ticket #81)
        "cpdel_totale": Decimal("669.88"),
        "cpdel_lavoratore": Decimal("181.57"),
        "cpdel_ente": Decimal("488.31"),
        "fondo_credito": Decimal("7.18"),
        "contributo_aggiuntivo": Decimal("0.00"),
        "irap_acconto": Decimal("174.39"),  # 8,5% a carico dell'ente
    }
    assert periodo.recuperi == ()


def test_assunzione_a_meta_agosto_pagata_a_settembre(registro, reale, orologio):
    assumi(registro, "funzionari", dal=date(2026, 8, 24))
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25))
    righe = {riga.istituto: riga.valore for riga in calcola(registro, reale, R, Mese(2026, 8))}
    assert righe == {"tabellare_funzionari": Decimal("590.16"), "comparto_funzionari": Decimal("9.78")}

    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 9)).periodi
    valori = importi(periodo)
    assert valori["base.cpdel"] == Decimal("2828.29")
    assert valori["cpdel_totale"] == Decimal("923.44")
    assert valori["cpdel_lavoratore"] == Decimal("250.30")
    assert valori["cpdel_ente"] == Decimal("673.14")
    assert valori["fondo_credito"] == Decimal("9.90")


def test_contributo_aggiuntivo_oltre_la_prima_fascia_mensile(registro, reale, orologio):
    assumi(registro, "operatori_esperti")
    mesi = (Mese(2026, 9), Mese(2026, 10), Mese(2026, 11))
    paga(registro, orologio, stipendi(registro, reale, *mesi), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    valori = importi(periodo)
    assert valori["base.cpdel"] == Decimal("5472.36")
    assert valori["contributo_aggiuntivo"] == Decimal("7.87")  # (5.472,36 - 4.685) x 1%
    assert valori["cpdel_totale"] == Decimal("1786.73")
    assert valori["cpdel_lavoratore"] == Decimal("484.30")
    assert valori["cpdel_ente"] == Decimal("1302.43")
    assert valori["fondo_credito"] == Decimal("19.15")

    aggiuntivo = next(riga for riga in periodo.contributi if riga.istituto == "contributo_aggiuntivo")
    testo = spiega(aggiuntivo)
    assert "urn:nir:stato:decreto.legge:1992-09-19;384~art3ter" in testo
    assert "prassi:inps:circolare:2026-01-30;6~par5" in testo


def test_dicembre_dopo_un_mese_oltre_fascia_chiede_il_conguaglio(registro, reale, orologio):
    assumi(registro, "operatori_esperti")
    mesi = (Mese(2026, 9), Mese(2026, 10), Mese(2026, 11))
    paga(registro, orologio, stipendi(registro, reale, *mesi), date(2026, 11, 27))
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 12)), date(2026, 12, 18))
    with pytest.raises(CasoNonModellato, match="conguaglio"):
        calcola_denuncia(registro, reale, R, Mese(2026, 12))


def test_prima_fascia_2027_non_ancora_nel_corpus(registro, reale, orologio):
    assumi(registro, "istruttori")
    paga(registro, orologio, stipendi(registro, reale, Mese(2027, 1)), date(2027, 1, 27))
    with pytest.raises(ParametroMancante, match="prima_fascia"):
        calcola_denuncia(registro, reale, R, Mese(2027, 1))


@pytest.mark.parametrize(
    ("area", "tabellare", "comparto"),
    [
        ("funzionari", "1096.01", "18.17"),
        ("istruttori", "1009.82", "16.03"),
        ("operatori_esperti", "898.30", "13.76"),
        ("operatori", "862.11", "11.34"),
    ],
)
def test_part_time_al_50_per_cento_riduce_competenze_fisse_e_periodiche(registro, reale, area, tabellare, comparto):
    """CCNL 16/11/2022 art. 62 c. 10, ora art. 55 c. 10 del CCNL 23/02/2026: proporzionali (ADR 0026, ticket #72)."""
    assumi(registro, area)
    registro.registra_fatto(R, "part_time", "50", date(2026, 11, 1))
    righe = calcola(registro, reale, R, Mese(2026, 11))
    assert {riga.istituto: riga.valore for riga in righe} == {
        f"tabellare_{area}": Decimal(tabellare),
        f"comparto_{area}": Decimal(comparto),
    }
    assert all(riga.derivazione.part_time.trattamento == "proporzionale" for riga in righe)


def test_recupero_su_cessato_per_cessazione_retroattiva(registro, reale, orologio):
    fatti = assumi(registro, "istruttori")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 10)), date(2026, 10, 27))

    orologio.vai(11, 3)
    for fatto in fatti[2:]:  # dopo il codice fiscale e il legame con la persona
        registro.annulla_fatto(fatto.id, "cessazione comunicata in ritardo")
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 1, 1), date(2026, 10, 15))
    registro.registra_codice(R, "area", "istruttori", date(2026, 1, 1), date(2026, 10, 15))
    registro.registra_codice(R, "cessazione", "1", date(2026, 10, 16))  # dal giorno dopo l'ultimo di servizio
    recupero = [voce.importo() for voce in differenze(registro, reale, R, Mese(2026, 10), TipoEsito.PAGATO)]
    assert sorted(riga.valore for riga in recupero) == [Decimal("-1009.81"), Decimal("-16.03")]
    paga(registro, orologio, recupero, date(2026, 11, 20))

    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    assert not periodo.in_servizio
    assert {caso.caso for caso in periodo.recuperi} == {"su cessato"}
    valori = importi(periodo)
    assert valori["base.cpdel"] == Decimal("-1025.84")
    assert valori["cpdel_totale"] == Decimal("-334.94")
    assert valori["cpdel_lavoratore"] == Decimal("-90.79")
    assert valori["cpdel_ente"] == Decimal("-244.15")
    assert valori["fondo_credito"] == Decimal("-3.59")
    assert valori["contributo_aggiuntivo"] == Decimal("0.00")


@pytest.mark.parametrize(
    ("istituto", "codice"),
    [
        ("tabellare_funzionari", "U.1.01.01.01.002"),
        ("cpdel_ente", "U.1.01.02.01.001"),
        ("irap_acconto", "U.1.02.01.01.001"),
    ],
)
def test_il_corpus_reale_classifica_le_spese_di_personale_con_l_origine_automatica(reale, istituto, codice):
    dichiarazione = reale.classificazione(istituto, date(2026, 3, 31))
    assert (dichiarazione.piano_dei_conti, dichiarazione.origine_impegno) == (codice, "automatico")


def test_il_corpus_reale_ha_la_scadenza_f24ep_2026_senza_proroga_e_nessuna_dal_2027(reale):
    regola = reale.regola_scadenza_f24ep(date(2026, 6, 1))
    assert regola is not None
    assert regola.giorno == 16
    assert regola.riferimento == "urn:nir:stato:decreto.legge:2008-11-29;185~art32ter-com1bis"
    assert regola.proroga is None
    assert reale.regola_scadenza_f24ep(date(2027, 1, 1)) is None


def test_la_scadenza_f24ep_2026_vale_fino_all_ultimo_giorno_dell_anno(reale):
    """Caso limite (#107): il 31/12/2026 la regola del 32-ter vale ancora, il giorno dopo non c'è regola."""
    assert reale.regola_scadenza_f24ep(date(2026, 12, 31)).giorno == 16
    assert reale.regola_scadenza_f24ep(date(2026, 1, 1)).giorno == 16


@pytest.mark.parametrize("posizione, causale", [("gestione_separata", "CXX"), ("pensionato", "C10"), ("altra_cassa", "C10")])
def test_il_corpus_reale_mappa_la_causale_della_gestione_separata_per_posizione(reale, posizione, causale):
    mappata = reale.mappatura_di_fatto(
        "f24ep.causale_gestione_separata", "causale", "posizione_previdenziale", posizione, date(2026, 11, 27)
    )
    assert mappata is not None and mappata.codice == causale


def test_il_corpus_reale_mappa_l_onere_art86_su_cxx(reale):
    assert reale.mappatura("onere_art86", "codice_tributo_f24ep", date(2026, 11, 27), None).codice == "CXX"
