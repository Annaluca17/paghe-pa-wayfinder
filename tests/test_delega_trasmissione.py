"""Trasmissione della delega F24EP: esito dichiarato immutabile, correzione, annullamento (ADR 0023). Dati fittizi.

La delega trasmessa è un esito dichiarato che non cambia più; una correzione è una nuova delega; l'annullamento
entro il termine è un fatto a sé. Termini dell'Allegato 2: saldo maggiore di zero, invio entro le 20:00 e
annullamento entro le 22:00 (ora italiana) del secondo giorno lavorativo prima della data di versamento; saldo zero,
fino alle 24:00 del giorno di versamento.
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from paghe import Mese, TipoEsito
from paghe.delega import (
    annulla_delega,
    costruisci_delega,
    delega_attiva,
    leggi_delega_trasmessa,
    termine_annullamento,
    termine_trasmissione,
    trasmetti_delega,
)
from paghe.errori import ErroreRegistro, VistaFerma
from paghe.proposta import registra_ricevuta_delega

from controlli_f24ep import controlla
from materiale_delega import ADATTATORE, corpus_delega, dati_ente, paga_a_mano, riga_a_mano

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def pronta(registro, corpus, orologio):
    """Pagamento di febbraio con ritenuta 100,00 e contributi 480,00; la delega scade e si versa il 16 marzo 2026."""
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    paga_a_mano(
        registro, corpus, orologio, VALUTA,
        [riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100"), riga_a_mano(corpus, VALUTA, "contributo_ente", "480")],
    )
    orologio.vai(3, 10)


def trasmetti(registro, corpus, delega_id="DELEGA-1"):
    return trasmetti_delega(registro, corpus, delega_id, ADATTATORE, FEB)


# Trasmissione ed esito dichiarato

def test_la_trasmissione_registra_l_esito_dichiarato_con_gli_importi_della_delega(registro, corpus, orologio, pronta):
    t = trasmetti(registro, corpus)
    (esito,) = registro.esiti(TipoEsito.DICHIARATO, orologio())
    assert esito.id == t.esito_id and esito.data == date(2026, 3, 10)
    assert sorted((r.istituto, r.valore) for r in esito.righe) == [
        ("contributo_ente", D("480")), ("ritenuta_irpef", D("100")),
    ]


def test_la_delega_trasmessa_si_rilegge_dal_registro_con_righe_scadenza_e_saldo(registro, corpus, orologio, pronta):
    t = trasmetti(registro, corpus)
    letta = leggi_delega_trasmessa(registro, "DELEGA-1")
    assert letta == t
    assert [(r.tributo, r.debito) for r in letta.righe] == [("100E", D("100")), ("P201", D("480"))]
    assert (letta.scadenza, letta.data_versamento, letta.saldo) == (date(2026, 3, 16), date(2026, 3, 16), D("580"))
    assert letta.mese_pagamento == FEB and letta.ente.denominazione == "ENTE DI PROVA"


def test_il_file_telematico_supera_i_controlli_ed_e_quello_della_delega(registro, corpus, orologio, pronta):
    t = trasmetti(registro, corpus)
    assert controlla(t.file) == ([], [])
    righe = [r.decode("latin-1") for r in t.file.split(b"\r\n") if r]
    assert righe[1][1872:1887].rstrip() == "580,00" and righe[1][1887:1897] == "16-03-2026"
    assert righe[2][122:130].strip() == "F100E"  # tipo riga e codice tributo della prima riga


def test_il_file_si_rigenera_uguale_dal_registro(registro, corpus, orologio, pronta):
    t = trasmetti(registro, corpus)
    assert leggi_delega_trasmessa(registro, "DELEGA-1").file == t.file


def test_la_delega_trasmessa_non_cambia_se_poi_cambiano_i_fatti_sull_ente(registro, corpus, orologio, pronta):
    t = trasmetti(registro, corpus)
    registro.registra_codice_ente("email", "altra@ente.example", date(2026, 1, 1))
    registro.registra_codice_ente("denominazione", "ALTRO ENTE", date(2026, 1, 1))
    letta = leggi_delega_trasmessa(registro, "DELEGA-1")
    assert letta.ente.email == "paghe@ente.example" and letta.file == t.file


def test_la_stessa_trasmissione_ripetuta_non_ha_effetto(registro, corpus, orologio, pronta):
    primo = trasmetti(registro, corpus)
    orologio.avanza(60)
    secondo = trasmetti(registro, corpus)
    assert secondo == primo
    assert len(registro.esiti(TipoEsito.DICHIARATO, orologio())) == 1
    assert len(registro.eventi("delega_trasmessa", orologio())) == 1


def test_lo_stesso_identificativo_con_un_contenuto_diverso_e_rifiutato(registro, corpus, orologio, pronta):
    trasmetti(registro, corpus)
    registro.registra_codice_ente("email", "altra@ente.example", date(2026, 1, 1))
    with pytest.raises(ErroreRegistro, match="contenuto diverso"):
        trasmetti(registro, corpus)
    assert len(registro.esiti(TipoEsito.DICHIARATO, orologio())) == 1


def test_una_delega_con_dati_mancanti_non_si_trasmette_e_non_scrive_nulla(registro, corpus, orologio):
    dati_ente(registro, email=None)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    paga_a_mano(registro, corpus, orologio, VALUTA, [riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100")])
    with pytest.raises(VistaFerma, match="email"):
        trasmetti(registro, corpus)
    assert registro.esiti(TipoEsito.DICHIARATO, orologio()) == [] and registro.eventi("delega_trasmessa", orologio()) == []


def test_una_delega_con_un_fermo_non_si_trasmette_nominando_il_caso(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    paga_a_mano(
        registro, corpus, orologio, VALUTA,
        [riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100"), riga_a_mano(corpus, VALUTA, "debito_senza_codice", "10")],
    )
    with pytest.raises(VistaFerma, match="debito_senza_codice"):
        trasmetti(registro, corpus)
    assert registro.esiti(TipoEsito.DICHIARATO, orologio()) == []


def test_senza_righe_non_c_e_nulla_da_trasmettere(registro, corpus, orologio):
    dati_ente(registro)
    with pytest.raises(VistaFerma, match="nessuna riga"):
        trasmetti(registro, corpus)


def test_l_identificativo_della_delega_e_obbligatorio(registro, corpus, orologio, pronta):
    with pytest.raises(ErroreRegistro, match="identificativo"):
        trasmetti(registro, corpus, " ")


# Lo stesso importo in due deleghe

def test_le_righe_di_una_delega_trasmessa_non_entrano_in_un_altra(registro, corpus, orologio, pronta):
    trasmetti(registro, corpus)
    d = costruisci_delega(registro, corpus, FEB)
    assert d.righe == () and d.altre_deleghe == ("DELEGA-1",)
    with pytest.raises(VistaFerma, match="nessuna riga"):
        trasmetti(registro, corpus, "DELEGA-2")


def test_una_delega_scartata_libera_le_righe_per_una_nuova_delega(registro, corpus, orologio, pronta):
    prima = trasmetti(registro, corpus)
    registra_ricevuta_delega(registro, "r-1", ADATTATORE, "DELEGA-1", "controlli_formali", "negativo")
    assert not delega_attiva(registro, "DELEGA-1")
    nuova = trasmetti(registro, corpus, "DELEGA-2")
    assert nuova.righe == prima.righe and nuova.esito_id != prima.esito_id
    assert len(registro.esiti(TipoEsito.DICHIARATO, orologio())) == 2  # l'esito della prima resta com'era
    assert leggi_delega_trasmessa(registro, "DELEGA-1") == prima


def test_una_delega_con_ricevute_positive_resta_attiva_e_tiene_le_sue_righe(registro, corpus, orologio, pronta):
    trasmetti(registro, corpus)
    registra_ricevuta_delega(registro, "r-1", ADATTATORE, "DELEGA-1", "controlli_formali", "positivo")
    assert delega_attiva(registro, "DELEGA-1")
    assert costruisci_delega(registro, corpus, FEB).righe == ()


# Annullamento

def test_l_annullamento_entro_il_termine_e_un_fatto_a_se_e_libera_le_righe(registro, corpus, orologio, pronta):
    trasmetti(registro, corpus)
    evento = annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-1")
    assert evento.tipo == "delega_annullata" and evento.contenuto == {"delega": "DELEGA-1"}
    assert not delega_attiva(registro, "DELEGA-1")
    assert len(costruisci_delega(registro, corpus, FEB).righe) == 2
    assert len(registro.esiti(TipoEsito.DICHIARATO, orologio())) == 1  # l'esito dichiarato non si tocca


def test_l_annullamento_ripetuto_non_ha_effetto(registro, corpus, orologio, pronta):
    trasmetti(registro, corpus)
    primo = annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-1")
    assert annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-1") == primo
    assert len(registro.eventi("delega_annullata", orologio())) == 1


def test_non_si_annulla_una_delega_inesistente_o_gia_annullata(registro, corpus, orologio, pronta):
    with pytest.raises(ErroreRegistro, match="inesistente"):
        annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-9")
    trasmetti(registro, corpus)
    annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-1")
    with pytest.raises(ErroreRegistro, match="già annullata"):
        annulla_delega(registro, corpus, "ann-2", ADATTATORE, "DELEGA-1")


def test_l_annullamento_dopo_il_termine_e_rifiutato(registro, corpus, orologio, pronta):
    trasmetti(registro, corpus)
    orologio.ora = datetime(2026, 3, 12, 21, 30, tzinfo=UTC)  # le 22:30 italiane del giovedì 12
    with pytest.raises(ErroreRegistro, match="termine"):
        annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-1")
    assert delega_attiva(registro, "DELEGA-1")


def test_l_annullamento_poco_prima_del_termine_e_ammesso(registro, corpus, orologio, pronta):
    trasmetti(registro, corpus)
    orologio.ora = datetime(2026, 3, 12, 20, 59, tzinfo=UTC)  # le 21:59 italiane
    annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-1")
    assert not delega_attiva(registro, "DELEGA-1")


# Termini dell'Allegato 2

def italiane(anno, mese, giorno, ora, minuto=0):
    """Un istante dato in ora italiana, per il confronto: marzo 2026 è ora solare (UTC+1)."""
    return datetime(anno, mese, giorno, tzinfo=UTC) + timedelta(hours=ora - 1, minutes=minuto)


def test_il_termine_di_trasmissione_e_alle_20_del_secondo_giorno_lavorativo_prima(corpus):
    # versamento lunedì 16 marzo 2026: giovedì 12 marzo (venerdì 13 è il giorno prima, giovedì il secondo prima)
    assert termine_trasmissione(corpus, date(2026, 3, 16), D("580")) == italiane(2026, 3, 12, 20)


def test_il_termine_di_annullamento_e_alle_22(corpus):
    assert termine_annullamento(corpus, date(2026, 3, 16), D("580")) == italiane(2026, 3, 12, 22)


def test_con_saldo_zero_i_termini_sono_la_mezzanotte_del_giorno_di_versamento(corpus):
    assert termine_trasmissione(corpus, date(2026, 3, 16), D("0")) == italiane(2026, 3, 17, 0)
    assert termine_annullamento(corpus, date(2026, 3, 16), D("0")) == italiane(2026, 3, 17, 0)


def test_i_giorni_festivi_non_sono_lavorativi_per_i_termini(corpus):
    # versamento martedì 28 aprile 2026: lunedì 27 è il 1° e venerdì 24 il 2° giorno prima (25 e 26 sono sabato e domenica)
    assert termine_trasmissione(corpus, date(2026, 4, 28), D("1")) == datetime(2026, 4, 24, 18, 0, tzinfo=UTC)  # 20:00 ora legale
    # versamento lunedì 4 maggio: venerdì 1 maggio è festivo, quindi giovedì 30 aprile è il 1° e mercoledì 29 il 2° giorno prima
    assert termine_trasmissione(corpus, date(2026, 5, 4), D("1")) == datetime(2026, 4, 29, 18, 0, tzinfo=UTC)


def test_il_termine_usa_l_ora_legale_d_estate(corpus):
    assert termine_trasmissione(corpus, date(2026, 8, 20), D("1")) == datetime(2026, 8, 18, 18, 0, tzinfo=UTC)


def test_una_trasmissione_dopo_il_termine_da_un_avviso(registro, corpus, orologio, pronta):
    orologio.ora = datetime(2026, 3, 12, 19, 30, tzinfo=UTC)  # le 20:30 italiane del giovedì 12: oltre le 20
    t = trasmetti(registro, corpus)
    assert [a.tipo for a in t.avvisi] == ["trasmissione_oltre_il_termine"]


def test_una_trasmissione_nei_termini_non_da_avvisi(registro, corpus, orologio, pronta):
    assert trasmetti(registro, corpus).avvisi == ()
