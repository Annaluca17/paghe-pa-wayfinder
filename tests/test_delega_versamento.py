"""Esito versato della delega F24EP, con le ricevute e il versamento eseguito già nel nucleo (ADR 0023, 0025). Dati fittizi.

L'identificativo di versamento dell'evento è quello della delega: da una delega trasmessa nasce l'esito versato,
una sola volta, con la data reale dell'addebito.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese, TipoEsito
from paghe.delega import (
    annulla_delega,
    costruisci_delega,
    registra_versamento_delega,
    situazione_delega,
    trasmetti_delega,
)
from paghe.errori import ErroreRegistro, VistaFerma
from paghe.proposta import StatoDelega, registra_ricevuta_delega

from materiale_delega import ADATTATORE, corpus_delega, dati_ente, paga_a_mano, riga_a_mano

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def trasmessa(registro, corpus, orologio):
    """Febbraio: ritenuta 100,00, contributi 480,00 e credito 170E di 30,00; delega trasmessa il 10 marzo."""
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    righe = [
        riga_a_mano(corpus, VALUTA, i, v)
        for i, v in (("ritenuta_irpef", "100"), ("contributo_ente", "480"), ("credito_integrativo", "30"))
    ]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    orologio.vai(3, 10)
    return trasmetti_delega(registro, corpus, "DELEGA-1", ADATTATORE, FEB)


def versa(registro, chiave="ver-1", data=date(2026, 3, 16), delega="DELEGA-1", provenienza="addebito"):
    return registra_versamento_delega(registro, chiave, ADATTATORE, delega, data, provenienza)


def test_il_versamento_crea_l_esito_versato_con_le_righe_della_delega(registro, orologio, trasmessa):
    esito = versa(registro)
    assert esito.tipo is TipoEsito.VERSATO and esito.data == date(2026, 3, 16)
    assert sorted((r.istituto, r.valore) for r in esito.righe) == [
        ("contributo_ente", D("480")), ("credito_integrativo", D("30")), ("ritenuta_irpef", D("100")),
    ]
    assert registro.esiti(TipoEsito.VERSATO, orologio()) == [esito]


def test_l_identificativo_di_versamento_dell_evento_e_quello_della_delega(registro, orologio, trasmessa):
    esito = versa(registro)
    evento = registro.evento("ver-1")
    assert evento.contenuto["versamento"] == "DELEGA-1" and evento.contenuto["canale"] == "f24ep"
    assert evento.esito_id == esito.id and evento.adattatore == ADATTATORE


def test_l_esito_dichiarato_resta_com_era_dopo_il_versamento(registro, orologio, trasmessa):
    versa(registro)
    (dichiarato,) = registro.esiti(TipoEsito.DICHIARATO, orologio())
    assert dichiarato.id == trasmessa.esito_id and len(dichiarato.righe) == 3


def test_dopo_il_versamento_le_righe_non_entrano_in_nessuna_altra_delega(registro, corpus, orologio, trasmessa):
    versa(registro)
    assert costruisci_delega(registro, corpus, FEB).righe == ()
    with pytest.raises(VistaFerma, match="nessuna riga"):
        trasmetti_delega(registro, corpus, "DELEGA-2", ADATTATORE, FEB)


def test_il_versamento_ripetuto_non_crea_un_secondo_esito(registro, orologio, trasmessa):
    primo = versa(registro)
    assert versa(registro) == primo
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_un_secondo_addebito_con_un_altro_identificativo_e_un_errore(registro, orologio, trasmessa):
    versa(registro)
    with pytest.raises(ErroreRegistro, match="già"):
        versa(registro, chiave="ver-2")
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_la_regolarizzazione_e_registrata_e_non_crea_un_secondo_esito(registro, orologio, trasmessa):
    esito = versa(registro)
    orologio.avanza(3600)
    assert versa(registro, chiave="reg-1", data=date(2026, 3, 20), provenienza="regolarizzazione") == esito
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_una_delega_inesistente_non_si_versa(registro, orologio, trasmessa):
    with pytest.raises(ErroreRegistro, match="inesistente"):
        versa(registro, delega="DELEGA-9")


def test_una_delega_scartata_non_si_versa_e_la_nuova_delega_si(registro, corpus, orologio, trasmessa):
    registra_ricevuta_delega(registro, "r-1", ADATTATORE, "DELEGA-1", "controlli_formali", "negativo")
    with pytest.raises(ErroreRegistro, match="scartata"):
        versa(registro)
    assert registro.esiti(TipoEsito.VERSATO, orologio()) == []
    trasmetti_delega(registro, corpus, "DELEGA-2", ADATTATORE, FEB)
    esito = versa(registro, delega="DELEGA-2")
    assert len(esito.righe) == 3 and len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_una_delega_annullata_non_si_versa(registro, corpus, orologio, trasmessa):
    annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-1")
    with pytest.raises(ErroreRegistro, match="annullata"):
        versa(registro)


# Situazione della delega e versamento tardivo

def test_la_situazione_della_delega_trasmessa(registro, orologio, trasmessa):
    s = situazione_delega(registro, "DELEGA-1")
    assert (s.stato, s.versata_il, s.fermi) == (StatoDelega.TRASMESSA, None, ())


def test_la_situazione_segue_le_ricevute_e_il_versamento(registro, orologio, trasmessa):
    for numero, (fase, esito) in enumerate((("controlli_formali", "positivo"), ("controllo_crediti", "positivo"), ("addebito", "positivo"))):
        registra_ricevuta_delega(registro, f"r-{numero}", ADATTATORE, "DELEGA-1", fase, esito)
    versa(registro)
    s = situazione_delega(registro, "DELEGA-1")
    assert (s.stato, s.versata_il, s.fermi) == (StatoDelega.ADDEBITATA, date(2026, 3, 16), ())


def test_un_versamento_dopo_la_scadenza_si_segnala_e_ferma_quella_delega(registro, orologio, trasmessa):
    versa(registro, data=date(2026, 3, 17))  # la scadenza è il 16
    s = situazione_delega(registro, "DELEGA-1")
    (fermo,) = s.fermi
    assert fermo.caso == "versamento_tardivo" and "ravvedimento" in fermo.motivo
    assert "2026-03-17" in fermo.motivo and "2026-03-16" in fermo.motivo
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1  # il denaro è andato: l'esito nasce comunque


def test_un_versamento_alla_scadenza_non_e_tardivo(registro, orologio, trasmessa):
    versa(registro, data=date(2026, 3, 16))
    assert situazione_delega(registro, "DELEGA-1").fermi == ()
