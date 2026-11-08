"""Regimi del titolo, PR B del ticket #73: sindaco, mandato di amministratore (corpus reale).

Misura dell'indennita' di fantasia (input da atto, nessuna norma). Dimezzamento: art. 82 c. 1 TUEL. Quota forfettaria
dell'art. 86 c. 2: minimale 18.808,00 euro (Circ. INPS 14/2026) al 33,72% (Circ. INPS 8/2026), cioe' 6.342,06 euro annui.
Persone e rapporti di fantasia.
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
ATTO = Atto("ente:ente_di_prova:delibera:2026-01-09;1", date(2026, 1, 9))


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def mandato(registro, condizione="non_dipendente", posizione="gestione_separata", carica="sindaco", dal=date(2026, 1, 1)):
    """Un mandato di sindaco: carica, condizione lavorativa e posizione previdenziale come fatti datati."""
    registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1972, 10, 9))
    registro.collega_rapporto(R, "PERSONA-1", dal)
    for tipo, valore in (("carica", carica), ("condizione_lavorativa", condizione), ("posizione_previdenziale", posizione)):
        if valore is not None:
            registro.registra_codice(R, tipo, valore, dal, atto=ATTO)


def misura(registro, importo="3000.00", dal=date(2026, 1, 1)):
    return registro.registra_fatto(R, "misura_indennita_funzione", importo, dal, atto=ATTO)


def importi(registro, corpus, mese):
    return {riga.istituto: riga.valore for riga in calcola(registro, corpus, R, mese)}


def test_l_indennita_di_funzione_e_la_misura_mensile_da_atto_sul_mese_intero(registro, reale):
    mandato(registro)
    misura(registro)
    assert importi(registro, reale, Mese(2026, 11))["indennita_funzione"] == Decimal("3000.00")


def test_il_lavoratore_dipendente_senza_aspettativa_ha_l_indennita_dimezzata(registro, reale):
    mandato(registro, condizione="dipendente_senza_aspettativa")
    misura(registro)
    valori = importi(registro, reale, Mese(2026, 11))
    assert valori["indennita_funzione"] == Decimal("3000.00")  # l'importo pieno resta visibile
    assert valori["dimezzamento_indennita"] == Decimal("-1500.00")  # art. 82 c. 1 TUEL
    assert sum(valori.values()) == Decimal("1500.00")


def test_la_condizione_lavorativa_che_cambia_a_meta_mese_dimezza_solo_la_seconda_meta(registro, reale):
    mandato(registro, condizione=None)
    registro.registra_codice(R, "condizione_lavorativa", "non_dipendente", date(2026, 1, 1), date(2026, 11, 15), atto=ATTO)
    registro.registra_codice(R, "condizione_lavorativa", "dipendente_senza_aspettativa", date(2026, 11, 16), atto=ATTO)
    misura(registro)
    righe = calcola(registro, reale, R, Mese(2026, 11))
    # 15 giorni su 30 a ciascuna meta': 1.500,00 + 1.500,00 di indennita', meno la meta' della seconda frazione.
    assert [r.valore for r in righe if r.istituto == "indennita_funzione"] == [Decimal("1500.00"), Decimal("1500.00")]
    (dimezzamento,) = [r for r in righe if r.istituto == "dimezzamento_indennita"]
    assert dimezzamento.valore == Decimal("-750.00")
    assert dimezzamento.periodo.dal == date(2026, 11, 16)


def paga(registro, orologio, righe, giorno):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(R, esito.id, giorno)
    orologio.avanza()
    return esito


def test_l_indennita_non_entra_in_nessuna_base_previdenziale(registro, reale, orologio):
    mandato(registro, condizione="dipendente_senza_aspettativa")
    misura(registro)
    paga(registro, orologio, calcola(registro, reale, R, Mese(2026, 11)), date(2026, 11, 27))
    (periodo,) = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    # nessuna base previdenziale e quindi nessun contributo, nemmeno in gestione separata: resta solo la base IRAP (ticket #81)
    assert {base.istituto for base in periodo.basi} == {"base.irap"}
    assert {contributo.istituto for contributo in periodo.contributi} == {"irap_acconto"}


def test_senza_la_condizione_lavorativa_l_indennita_non_si_paga_piena_in_silenzio(registro, reale):
    mandato(registro, condizione=None)
    misura(registro)
    with pytest.raises(CasoNonModellato, match="condizione_lavorativa"):
        calcola(registro, reale, R, Mese(2026, 11))


def test_un_amministratore_in_aspettativa_ferma_il_calcolo_per_gli_oneri_del_comma_1(registro, reale):
    mandato(registro, condizione="dipendente_in_aspettativa")
    misura(registro)
    with pytest.raises(CasoNonModellato, match="aspettativa"):
        calcola(registro, reale, R, Mese(2026, 11))


@pytest.mark.parametrize("fatto", ["presenza_seduta", "rimborso_datore_lavoro", "indennita_fine_mandato", "fascia_popolazione", "inail_dovuta"])
def test_i_casi_non_modellati_del_mandato_fermano_il_calcolo_e_nominano_il_caso(registro, reale, fatto):
    mandato(registro)
    misura(registro)
    registro.registra_fatto(R, fatto, "1", date(2026, 11, 1), atto=ATTO)
    with pytest.raises(CasoNonModellato, match=fatto):
        calcola(registro, reale, R, Mese(2026, 11))


def test_una_carica_diversa_dal_sindaco_non_ha_un_regime_modellato(registro, reale):
    mandato(registro, carica="assessore")
    misura(registro)
    with pytest.raises(CasoNonModellato, match="carica"):
        calcola(registro, reale, R, Mese(2026, 11))


@pytest.mark.parametrize("posizione", [None, "pensionato", "altra_cassa"])
def test_una_posizione_diversa_dalla_gestione_separata_ferma_la_quota_verso_altre_casse(registro, reale, posizione):
    mandato(registro, posizione=posizione)
    misura(registro)
    with pytest.raises(CasoNonModellato, match="posizione_previdenziale"):
        calcola(registro, reale, R, Mese(2026, 11))


def test_all_amministratore_non_lavoratore_dipendente_spetta_la_quota_forfettaria_dell_art_86(registro, reale):
    mandato(registro)
    misura(registro)
    valori = importi(registro, reale, Mese(2026, 11))
    # 18.808,00 x 33,72% = 6.342,06 euro annui, un dodicesimo: 528,505 arrotondato a 528,51.
    assert valori["onere_art86"] == Decimal("528.51")


def test_al_lavoratore_dipendente_la_quota_dell_art_86_non_spetta_e_non_nasce_nessun_importo(registro, reale):
    mandato(registro, condizione="dipendente_senza_aspettativa")
    misura(registro)
    assert "onere_art86" not in importi(registro, reale, Mese(2026, 11))


def test_la_quota_a_meta_mese_e_proporzionale_ai_giorni_in_cui_il_diritto_vale(registro, reale):
    mandato(registro, condizione=None)
    registro.registra_codice(R, "condizione_lavorativa", "non_dipendente", date(2026, 1, 1), date(2026, 11, 15), atto=ATTO)
    registro.registra_codice(R, "condizione_lavorativa", "dipendente_senza_aspettativa", date(2026, 11, 16), atto=ATTO)
    misura(registro)
    (quota,) = [r for r in calcola(registro, reale, R, Mese(2026, 11)) if r.istituto == "onere_art86"]
    assert quota.valore == Decimal("264.26")  # 528,51 x 15/30
    assert quota.periodo.dal == date(2026, 11, 1) and quota.periodo.al == date(2026, 11, 15)


def test_la_quota_e_un_onere_dell_ente_non_e_reddito_ne_base(registro, reale, orologio):
    mandato(registro)
    misura(registro)
    righe = calcola(registro, reale, R, Mese(2026, 11))
    assert {r.derivazione.maturazione for r in righe if r.istituto == "onere_art86"} == {"onere"}
    paga(registro, orologio, righe, date(2026, 11, 27))
    (periodo,) = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    assert {base.istituto for base in periodo.basi} == {"base.irap"}  # l'onere non e' nella base, nemmeno in quella IRAP
    assert {base.istituto: base.valore for base in periodo.basi}["base.irap"] == Decimal("3000.00")
    assert {contributo.istituto for contributo in periodo.contributi} == {"irap_acconto"}
