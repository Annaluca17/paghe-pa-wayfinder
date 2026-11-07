"""Lista collaboratori (ticket #73, PR B): vista della denuncia di chi e' in gestione separata, separata dalla ListaPosPA.

Corpus reale. Importi e persone di fantasia; codici fiscali con carattere di controllo valido.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Atto, Corpus, Mese, TipoEsito, calcola, emetti_esito
from paghe.denuncia import rapporti_della_vista
from paghe.lista_collaboratori import lista_collaboratori

CORPUS = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
ATTO = Atto("ente:ente_di_prova:determina:2026-01-09;1", date(2026, 1, 9))
COCO, SINDACO, DIPENDENTE = "R-COCO", "R-SINDACO", "R-DIP"
CF = {COCO: "RSSMRA80A01H501U", SINDACO: "RSSMRA85T01H501M", DIPENDENTE: "RSSMRA90A01H501W"}
NOVEMBRE = Mese(2026, 11)


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def persona(registro, rapporto, cognome="PROVA", nome="NOME"):
    registro.registra_codice_persona(f"P-{rapporto}", "codice_fiscale", CF[rapporto], date(1980, 1, 1))
    registro.registra_codice_persona(f"P-{rapporto}", "cognome", cognome, date(1980, 1, 1))
    registro.registra_codice_persona(f"P-{rapporto}", "nome", nome, date(1980, 1, 1))
    registro.collega_rapporto(rapporto, f"P-{rapporto}", date(2026, 1, 1))


def collaboratore(registro, posizione="gestione_separata", importo="1000.00", giorno=date(2026, 11, 30)):
    persona(registro, COCO)
    registro.registra_codice(COCO, "posizione_previdenziale", posizione, date(2026, 1, 1), atto=ATTO)
    registro.registra_fatto(COCO, "rata_collaborazione", importo, giorno, giorno, atto=ATTO)


def sindaco(registro):
    persona(registro, SINDACO)
    for tipo, valore in (("carica", "sindaco"), ("condizione_lavorativa", "non_dipendente"), ("posizione_previdenziale", "gestione_separata")):
        registro.registra_codice(SINDACO, tipo, valore, date(2026, 1, 1), atto=ATTO)
    registro.registra_fatto(SINDACO, "misura_indennita_funzione", "3000.00", date(2026, 1, 1), atto=ATTO)


def dipendente(registro):
    persona(registro, DIPENDENTE)
    registro.registra_codice(DIPENDENTE, "tipo_impiego", "1", date(2026, 1, 1))
    registro.registra_codice(DIPENDENTE, "area", "funzionari", date(2026, 1, 1))


def paga(registro, orologio, corpus, rapporti, mese=NOVEMBRE, giorno=date(2026, 11, 27)):
    for rapporto in rapporti:
        orologio.vai(giorno.month, giorno.day, giorno.year)
        esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, calcola(registro, corpus, rapporto, mese))
        registro.registra_pagamento(rapporto, esito.id, giorno)
        orologio.avanza()


def test_ogni_vista_prende_solo_i_rapporti_che_il_regime_le_assegna(registro, reale, orologio):
    collaboratore(registro)
    sindaco(registro)
    dipendente(registro)
    paga(registro, orologio, reale, (COCO, SINDACO, DIPENDENTE))
    rapporti = (COCO, SINDACO, DIPENDENTE)
    assert rapporti_della_vista(registro, reale, "lista_collaboratori", NOVEMBRE, rapporti) == (COCO, SINDACO)
    assert rapporti_della_vista(registro, reale, "lista_pos_pa", NOVEMBRE, rapporti) == (DIPENDENTE,)


def test_la_lista_del_collaboratore_porta_imponibile_contributo_e_quote_nel_mese_di_erogazione(registro, reale, orologio):
    collaboratore(registro)
    paga(registro, orologio, reale, (COCO,))
    lista = lista_collaboratori(registro, reale, COCO, NOVEMBRE)
    assert lista.mese_erogazione == NOVEMBRE
    assert (lista.collaboratore.codice_fiscale, lista.collaboratore.cognome, lista.collaboratore.nome) == (CF[COCO], "PROVA", "NOME")
    (riga,) = lista.righe
    assert (riga.imponibile, riga.contributo, riga.quota_collaboratore, riga.quota_ente) == (
        Decimal("1000.00"), Decimal("350.30"), Decimal("116.77"), Decimal("233.53"),
    )
    assert not riga.forfettaria


def test_senza_i_codici_del_tracciato_la_lista_e_una_bozza_non_trasmissibile(registro, reale, orologio):
    collaboratore(registro)
    paga(registro, orologio, reale, (COCO,))
    lista = lista_collaboratori(registro, reale, COCO, NOVEMBRE)
    assert not lista.trasmissibile
    assert any("tracciato" in motivo for motivo in lista.bozza)
    assert not any("cassa allargata" in motivo for motivo in lista.bozza)  # pagata e attribuita nello stesso anno


def test_la_quota_forfettaria_del_sindaco_e_una_riga_senza_imponibile_a_carico_dell_ente(registro, reale, orologio):
    sindaco(registro)
    paga(registro, orologio, reale, (SINDACO,))
    (riga,) = lista_collaboratori(registro, reale, SINDACO, NOVEMBRE).righe
    assert riga.forfettaria and riga.imponibile is None and riga.quota_collaboratore is None
    assert (riga.contributo, riga.quota_ente) == (Decimal("528.51"), Decimal("528.51"))


def test_l_indennita_del_sindaco_non_e_nella_lista_tra_i_contributi(registro, reale, orologio):
    sindaco(registro)
    paga(registro, orologio, reale, (SINDACO,))
    lista = lista_collaboratori(registro, reale, SINDACO, NOVEMBRE)
    assert [i.istituto for riga in lista.righe for i in riga.importi] == ["onere_art86"]


def test_una_somma_pagata_entro_il_12_gennaio_e_attribuita_all_anno_prima_resta_bozza_per_la_cassa_allargata(registro, reale, orologio):
    """Il corpus reale non ha categorie di reddito: l'attribuzione all'anno prima la porta l'esito pagato, come in produzione."""
    collaboratore(registro, importo="1000.00", giorno=date(2026, 1, 5))
    gennaio = Mese(2026, 1)
    giorno = date(2026, 1, 8)
    orologio.vai(1, 8)
    attribuiti = [replace(riga, anno_imposta=2025, categoria_reddito="collaborazione") for riga in calcola(registro, reale, COCO, gennaio)]
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, attribuiti)
    registro.registra_pagamento(COCO, esito.id, giorno)
    lista = lista_collaboratori(registro, reale, COCO, gennaio)
    assert any("cassa allargata" in motivo and "2025" in motivo for motivo in lista.bozza)
