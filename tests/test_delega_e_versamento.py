"""Ricevute della delega, stato della delega ed evento di versamento eseguito (ADR 0025). Dati fittizi.

La delega non esiste ancora (ticket #54): l'evento porta un identificativo di versamento opaco.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese, TipoEsito, calcola, differenze
from paghe.errori import ErroreRegistro
from paghe.proposta import (
    StatoDelega,
    emetti_versione,
    registra_pagamento_eseguito,
    registra_ricevuta_delega,
    registra_versamento_eseguito,
    stato_delega,
    conferma_versione,
)

from materiale_proposta import R, R2, P2, assumi, corpus_p, paga, stipendio

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
ADATTATORE = "adattatore-prova"
V1 = "VERSAMENTO-1"


# Ricevute e stato della delega

def ricevuta(registro, chiave, fase, esito, versamento=V1):
    return registra_ricevuta_delega(registro, chiave, ADATTATORE, versamento, fase, esito)


def test_senza_ricevute_la_delega_e_trasmessa(registro):
    assert stato_delega(registro, V1) is StatoDelega.TRASMESSA


def test_i_controlli_formali_positivi_accettano_la_delega(registro, orologio):
    ricevuta(registro, "r-1", "controlli_formali", "positivo")
    assert stato_delega(registro, V1) is StatoDelega.ACCETTATA


def test_una_ricevuta_sospesa_sospende_la_delega_finche_non_e_sciolta(registro, orologio):
    ricevuta(registro, "r-1", "controlli_formali", "positivo")
    ricevuta(registro, "r-2", "controllo_crediti", "sospeso")
    assert stato_delega(registro, V1) is StatoDelega.SOSPESA
    ricevuta(registro, "r-3", "controllo_crediti", "positivo")
    assert stato_delega(registro, V1) is StatoDelega.ACCETTATA


def test_l_addebito_positivo_addebita_la_delega(registro, orologio):
    ricevuta(registro, "r-1", "controlli_formali", "positivo")
    ricevuta(registro, "r-2", "controllo_crediti", "positivo")
    ricevuta(registro, "r-3", "addebito", "positivo")
    assert stato_delega(registro, V1) is StatoDelega.ADDEBITATA


@pytest.mark.parametrize("fase", ["controlli_formali", "controllo_crediti", "addebito"])
def test_una_ricevuta_negativa_scarta_la_delega(registro, fase):
    ricevuta(registro, "r-1", "controlli_formali", "positivo")
    ricevuta(registro, "r-2", fase, "negativo")
    assert stato_delega(registro, V1) is StatoDelega.SCARTATA


def test_lo_stato_e_per_versamento(registro):
    ricevuta(registro, "r-1", "controlli_formali", "negativo", "VERSAMENTO-1")
    ricevuta(registro, "r-2", "controlli_formali", "positivo", "VERSAMENTO-2")
    assert stato_delega(registro, "VERSAMENTO-1") is StatoDelega.SCARTATA
    assert stato_delega(registro, "VERSAMENTO-2") is StatoDelega.ACCETTATA


def test_lo_stato_si_legge_a_un_istante(registro, orologio):
    ricevuta(registro, "r-1", "controlli_formali", "positivo")
    dopo_la_prima = orologio()
    orologio.avanza(3600)
    ricevuta(registro, "r-2", "addebito", "negativo")
    assert stato_delega(registro, V1, dopo_la_prima) is StatoDelega.ACCETTATA
    assert stato_delega(registro, V1, orologio()) is StatoDelega.SCARTATA


def test_la_ricevuta_ripetuta_con_lo_stesso_contenuto_non_ha_effetto(registro, orologio):
    primo = ricevuta(registro, "r-1", "controlli_formali", "positivo")
    secondo = registra_ricevuta_delega(registro, "r-1", "altro-adattatore", V1, "controlli_formali", "positivo")
    assert secondo == primo
    assert len(registro.eventi("ricevuta_delega", orologio())) == 1
    assert primo.adattatore == ADATTATORE


def test_la_ricevuta_con_lo_stesso_identificativo_e_contenuto_diverso_e_rifiutata(registro, orologio):
    ricevuta(registro, "r-1", "controlli_formali", "positivo")
    with pytest.raises(ErroreRegistro, match="contenuto diverso"):
        ricevuta(registro, "r-1", "controlli_formali", "negativo")
    assert stato_delega(registro, V1) is StatoDelega.ACCETTATA
    assert len(registro.eventi("ricevuta_delega", orologio())) == 1


@pytest.mark.parametrize(
    "fase, esito, versamento", [("trasmissione", "positivo", V1), ("addebito", "forse", V1), ("addebito", "positivo", " ")]
)
def test_una_ricevuta_incompleta_o_fuori_elenco_e_rifiutata(registro, fase, esito, versamento):
    with pytest.raises(ErroreRegistro):
        registra_ricevuta_delega(registro, "r-1", ADATTATORE, versamento, fase, esito)


# Versamento eseguito

def pagamento(registro, corpus, orologio, rapporti=(R,)):
    """Un pagamento eseguito: versione confermata ed esito pagato. Restituisce la versione."""
    for numero, rapporto in enumerate(rapporti):
        if numero:
            assumi(registro, rapporto, P2)
    assumi(registro)
    importi = []
    for rapporto, importo in zip(rapporti, ("1500", "500")):
        importi += stipendio(registro, corpus, FEB, importo, rapporto)
    return paga(registro, corpus, orologio, importi, VALUTA, "pag-1")


def righe_versate(versione, rapporto=R, istituti=("contributo_lavoratore", "contributo_ente", "ritenuta_irpef")):
    return [versione.riferimento(r) for r in versione.righe_del_rapporto(rapporto) if r.istituto in istituti]


def test_il_versamento_crea_l_esito_versato_con_le_righe_versate(registro, corpus_p, orologio):
    versione = pagamento(registro, corpus_p, orologio)
    orologio.avanza(3600)
    esito = registra_versamento_eseguito(
        registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe_versate(versione), "f24ep", "addebito"
    )
    assert esito.tipo is TipoEsito.VERSATO and esito.data == date(2026, 3, 16)
    assert {r.istituto: r.valore for r in esito.righe} == {
        "contributo_lavoratore": Decimal("120.00"),
        "contributo_ente": Decimal("360.00"),
        "ritenuta_irpef": Decimal("100.00"),
    }
    assert registro.esiti(TipoEsito.VERSATO, orologio()) == [esito]
    evento = registro.evento("ver-1")
    assert (evento.esito_id, evento.adattatore) == (esito.id, ADATTATORE)
    assert evento.contenuto["provenienza"] == "addebito" and evento.contenuto["canale"] == "f24ep"


def test_il_versamento_eseguito_ripetuto_non_crea_un_secondo_esito(registro, corpus_p, orologio):
    versione = pagamento(registro, corpus_p, orologio)
    righe = righe_versate(versione)
    primo = registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe, "f24ep", "addebito")
    orologio.avanza()
    secondo = registra_versamento_eseguito(registro, "ver-1", "altro", V1, date(2026, 3, 16), righe, "f24ep", "addebito")
    assert secondo == primo
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_lo_stesso_identificativo_con_contenuto_diverso_e_rifiutato(registro, corpus_p, orologio):
    versione = pagamento(registro, corpus_p, orologio)
    righe = righe_versate(versione)
    registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe, "f24ep", "addebito")
    with pytest.raises(ErroreRegistro, match="contenuto diverso"):
        registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 17), righe, "f24ep", "addebito")
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_la_regolarizzazione_dopo_l_addebito_e_registrata_e_non_crea_un_secondo_esito(registro, corpus_p, orologio):
    versione = pagamento(registro, corpus_p, orologio)
    righe = righe_versate(versione)
    esito = registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe, "f24ep", "addebito")
    orologio.avanza(3600)
    regolarizzato = registra_versamento_eseguito(
        registro, "reg-1", ADATTATORE, V1, date(2026, 3, 20), righe, "f24ep", "regolarizzazione"
    )
    assert regolarizzato == esito
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1
    evento = registro.evento("reg-1")
    assert evento.contenuto["provenienza"] == "regolarizzazione" and evento.esito_id == esito.id
    assert len(registro.eventi("versamento_eseguito", orologio())) == 2


def test_la_regolarizzazione_da_sola_vale_come_versamento_con_la_provenienza_che_lo_dice(registro, corpus_p, orologio):
    versione = pagamento(registro, corpus_p, orologio)
    esito = registra_versamento_eseguito(
        registro, "reg-1", ADATTATORE, V1, date(2026, 3, 20), righe_versate(versione), "f24ep", "regolarizzazione"
    )
    assert esito.tipo is TipoEsito.VERSATO and esito.data == date(2026, 3, 20)
    assert registro.evento("reg-1").contenuto["provenienza"] == "regolarizzazione"


def test_l_addebito_dopo_una_regolarizzazione_e_un_caso_non_modellato(registro, corpus_p, orologio):
    """L'esito è già nato con la data della regolarizzazione: il modello non lo corregge e non ne crea un secondo."""
    versione = pagamento(registro, corpus_p, orologio)
    righe = righe_versate(versione)
    registra_versamento_eseguito(registro, "reg-1", ADATTATORE, V1, date(2026, 3, 20), righe, "f24ep", "regolarizzazione")
    with pytest.raises(ErroreRegistro, match="caso non modellato"):
        registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe, "f24ep", "addebito")
    assert registro.evento("ver-1") is None
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_un_secondo_addebito_dello_stesso_versamento_e_un_errore(registro, corpus_p, orologio):
    versione = pagamento(registro, corpus_p, orologio)
    righe = righe_versate(versione)
    registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe, "f24ep", "addebito")
    with pytest.raises(ErroreRegistro, match="già"):
        registra_versamento_eseguito(registro, "ver-2", ADATTATORE, V1, date(2026, 3, 16), righe, "f24ep", "addebito")
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_una_riga_di_un_rapporto_non_pagato_non_si_versa(registro, corpus_p, orologio):
    assumi(registro)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    conferma_versione(registro, versione.id)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    with pytest.raises(ErroreRegistro, match="non risulta pagato"):
        registra_versamento_eseguito(
            registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe_versate(versione, R2), "f24ep", "addebito"
        )
    assert registro.esiti(TipoEsito.VERSATO, orologio()) == []


def test_una_riga_a_un_beneficiario_o_di_un_altro_canale_non_si_versa(registro, corpus_p, orologio):
    versione = pagamento(registro, corpus_p, orologio)
    stipendio_riga = versione.riferimento(next(r for r in versione.righe if r.istituto == "stipendio"))
    with pytest.raises(ErroreRegistro, match="versamento a un terzo"):
        registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), [stipendio_riga], "f24ep", "addebito")
    with pytest.raises(ErroreRegistro, match="versamento a un terzo"):
        registra_versamento_eseguito(
            registro, "ver-2", ADATTATORE, V1, date(2026, 3, 16), righe_versate(versione), "bonifico", "bonifico"
        )
    assert registro.esiti(TipoEsito.VERSATO, orologio()) == []


def test_una_riga_inesistente_e_un_errore(registro, corpus_p, orologio):
    versione = pagamento(registro, corpus_p, orologio)
    riga = righe_versate(versione)[0]
    inventata = type(riga)(riga.versione_id, riga.rapporto, "istituto_inventato", riga.periodo)
    with pytest.raises(ErroreRegistro, match="non è nella versione"):
        registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), [inventata], "f24ep", "addebito")


@pytest.mark.parametrize(
    "canale, provenienza", [("contanti", "addebito"), ("f24ep", "boh"), ("accredito", "addebito")]
)
def test_canale_e_provenienza_fuori_elenco_sono_rifiutati(registro, corpus_p, orologio, canale, provenienza):
    versione = pagamento(registro, corpus_p, orologio)
    with pytest.raises(ErroreRegistro):
        registra_versamento_eseguito(
            registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe_versate(versione), canale, provenienza
        )


def test_il_versamento_vuole_almeno_una_riga(registro, corpus_p, orologio):
    pagamento(registro, corpus_p, orologio)
    with pytest.raises(ErroreRegistro, match="almeno una riga"):
        registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), [], "f24ep", "addebito")


def test_un_versamento_puo_riunire_i_contributi_per_differenza_di_due_pagamenti_dello_stesso_mese(
    registro, corpus_p, orologio
):
    """Stessa chiave di importo in due esiti: nell'esito versato restano entrambe, non è «due volte lo stesso importo»."""
    assumi(registro)
    registro.registra_fatto(R, "mensile", "1000", FEB.primo_giorno, FEB.ultimo_giorno)
    primo = paga(registro, corpus_p, orologio, [r for r in calcola(registro, corpus_p, R, FEB) if r.istituto == "stipendio"], date(2026, 2, 20), "pag-1")
    registro.registra_fatto(R, "mensile", "1500", FEB.primo_giorno, FEB.ultimo_giorno)
    (arretrato,) = differenze(registro, corpus_p, R, FEB, TipoEsito.PAGATO)
    secondo = paga(registro, corpus_p, orologio, [arretrato.importo()], date(2026, 2, 27), "pag-2")
    righe = righe_versate(primo, istituti=("contributo_ente",)) + righe_versate(secondo, istituti=("contributo_ente",))
    esito = registra_versamento_eseguito(registro, "ver-1", ADATTATORE, V1, date(2026, 3, 16), righe, "f24ep", "addebito")
    assert sorted(r.valore for r in esito.righe) == [Decimal("120.00"), Decimal("240.00")]
    assert sum(r.valore for r in esito.righe) == Decimal("360.00")  # i contributi dell'intero mese sul 1500
