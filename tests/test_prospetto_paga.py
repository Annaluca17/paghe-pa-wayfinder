"""Prospetto paga (ticket #86, ADR 0030): vista di un rapporto in un pagamento eseguito, letta dal suo esito pagato.

Corpus reale piu' le dichiarazioni fittizie del mese di prova (composizione, regimi del prospetto). Persone e importi di
fantasia; codici fiscali con carattere di controllo valido.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Atto, Corpus, Mese, TipoEsito, calcola, emetti_esito
from paghe.errori import VistaFerma
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


def test_un_istituto_senza_dichiarazione_di_composizione_ferma_il_prospetto_e_si_nomina(registro, orologio):
    solo_reale = Corpus.da_toml(REALE, reale=True)
    dipendente(registro)
    esito = paga(registro, orologio, solo_reale, DIP)
    prospetto = prospetto_paga(registro, solo_reale, DIP, esito.id)
    assert not prospetto.consegnabile
    assert len(prospetto.fermi) == 2
    assert any("tabellare_funzionari" in fermo for fermo in prospetto.fermi)
    assert any("comparto_funzionari" in fermo for fermo in prospetto.fermi)


def test_un_rapporto_senza_righe_nel_pagamento_non_ha_prospetto(registro, corpus, orologio):
    dipendente(registro)
    sindaco(registro)
    esito = paga(registro, orologio, corpus, SINDACO)
    with pytest.raises(VistaFerma, match="R-DIP.*nessun prospetto"):
        prospetto_paga(registro, corpus, DIP, esito.id)


def test_un_esito_che_non_e_un_pagamento_eseguito_non_da_prospetto(registro, corpus, orologio):
    dipendente(registro)
    orologio.vai(11, 27)
    dichiarato = emetti_esito(registro, TipoEsito.DICHIARATO, PAGAMENTO, calcola(registro, corpus, DIP, NOVEMBRE))
    with pytest.raises(VistaFerma, match="nessun prospetto"):
        prospetto_paga(registro, corpus, DIP, dichiarato.id)


def collaboratore(registro):
    persona(registro, COCO)
    registro.registra_codice(COCO, "posizione_previdenziale", "gestione_separata", date(2026, 1, 1), atto=ATTO)
    registro.registra_fatto(COCO, "rata_collaborazione", "1000.00", PAGAMENTO, PAGAMENTO, atto=ATTO)


def test_senza_una_dichiarazione_del_regime_il_prospetto_non_spetta(registro, orologio):
    solo_reale = Corpus.da_toml(REALE, reale=True)
    collaboratore(registro)
    esito = paga(registro, orologio, solo_reale, COCO)
    with pytest.raises(VistaFerma, match="R-COCO.*non dichiara"):
        prospetto_paga(registro, solo_reale, COCO, esito.id)


def test_due_regimi_che_assegnano_lo_stesso_rapporto_fermano_la_vista(registro, orologio):
    doppio = Corpus.da_toml(
        REALE + FITTIZIO + """
[[output]]
vista = "prospetto_paga"
regime = "doppio"
istituti = ["indennita_funzione"]
posizione = "incarico"
dal = 2025-01-01
riferimento = "fittizio:prospetto-doppio"
""",
        reale=False,
    )
    sindaco(registro)
    esito = paga(registro, orologio, doppio, SINDACO)
    with pytest.raises(VistaFerma, match="R-SINDACO.*più regimi"):
        prospetto_paga(registro, doppio, SINDACO, esito.id)


def test_senza_posizione_il_prospetto_non_e_consegnabile_e_il_dato_si_nomina(registro, corpus, orologio):
    dipendente(registro, qualifica=None)
    esito = paga(registro, orologio, corpus, DIP)
    prospetto = prospetto_paga(registro, corpus, DIP, esito.id)
    assert prospetto.mancanti == ("posizione",)
    assert not prospetto.consegnabile


def test_senza_cognome_nome_o_codice_fiscale_il_prospetto_non_e_consegnabile(registro, corpus, orologio):
    dipendente(registro)
    registro.annulla_fatto(registro.fatti_persona_noti("P-R-DIP", "cognome", registro.adesso())[0].id, "prova")
    registro.annulla_fatto(registro.fatti_persona_noti("P-R-DIP", "codice_fiscale", registro.adesso())[0].id, "prova")
    esito = paga(registro, orologio, corpus, DIP)
    prospetto = prospetto_paga(registro, corpus, DIP, esito.id)
    assert prospetto.mancanti == ("codice_fiscale", "cognome")
    assert not prospetto.consegnabile


def test_senza_voci_sul_netto_il_prospetto_non_e_consegnabile(registro, orologio):
    corpus = Corpus.da_toml(
        REALE + FITTIZIO + """
[[output]]
vista = "prospetto_paga"
regime = "solo_oneri"
istituti = ["onere_art86"]
posizione = "carica"
dal = 2025-01-01
riferimento = "fittizio:prospetto-solo-oneri"
""",
        reale=False,
    )
    sindaco(registro)
    orologio.vai(11, 27)
    solo_onere = [i for i in calcola(registro, corpus, SINDACO, NOVEMBRE) if i.istituto == "onere_art86"]
    esito = emetti_esito(registro, TipoEsito.PAGATO, PAGAMENTO, solo_onere)
    registro.registra_pagamento(SINDACO, esito.id, PAGAMENTO)
    prospetto = prospetto_paga(registro, corpus, SINDACO, esito.id)
    assert prospetto.mancanti == ("voci",)


def test_il_codice_del_contratto_e_sempre_un_avviso_e_non_ferma_il_prospetto(registro, corpus, orologio):
    ente(registro)
    dipendente(registro)
    registro.registra_codice(DIP, "contratto", "RALN", date(2026, 1, 1))
    registro.registra_codice(DIP, "regime_fine_servizio", "3", date(2026, 1, 1))
    esito = paga(registro, orologio, corpus, DIP)
    prospetto = prospetto_paga(registro, corpus, DIP, esito.id)
    assert prospetto.avvisi == ("contratto_collettivo",)
    assert prospetto.consegnabile


def test_i_dati_dell_ente_e_il_tipo_di_fine_servizio_assenti_sono_avvisi_e_non_fermi(registro, corpus, orologio):
    dipendente(registro)
    esito = paga(registro, orologio, corpus, DIP)
    prospetto = prospetto_paga(registro, corpus, DIP, esito.id)
    assert prospetto.avvisi == ("contratto_collettivo", "ente_codice_fiscale", "ente_denominazione", "fine_servizio")
    assert prospetto.consegnabile


def test_il_tipo_di_fine_servizio_e_un_avviso_solo_dove_il_regime_lo_dichiara(registro, corpus, orologio):
    ente(registro)
    sindaco(registro)
    esito = paga(registro, orologio, corpus, SINDACO)
    assert prospetto_paga(registro, corpus, SINDACO, esito.id).avvisi == ("contratto_collettivo",)
