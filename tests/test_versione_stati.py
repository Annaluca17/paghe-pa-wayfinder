"""Stati della versione di proposta: inviata, confermata, respinta, superata (ADR 0013, 0025). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese, calcola
from paghe.errori import ErroreRegistro
from paghe.proposta import (
    StatoVersione,
    conferma_versione,
    controlla_superata,
    emetti_versione,
    registra_pagamento_eseguito,
    respingi_versione,
    stato_versione,
)

from materiale_proposta import R, assumi, corpus_p, stipendio

VALUTA = date(2026, 2, 27)
FEB = Mese(2026, 2)


def emessa(registro, corpus, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus, FEB)
    orologio.vai(2, 20)
    return emetti_versione(registro, corpus, VALUTA, importi), importi


def ricalcola(registro, corpus):
    return [r for r in calcola(registro, corpus, R, FEB) if r.istituto == "stipendio"]


def cambia_lo_stipendio(registro, orologio, nuovo="1600"):
    orologio.avanza(3600)
    registro.registra_fatto(R, "mensile", nuovo, FEB.primo_giorno, FEB.ultimo_giorno)


def test_una_versione_emessa_e_inviata(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    assert stato_versione(registro, versione.id) is StatoVersione.INVIATA


def test_la_ragioneria_conferma(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    orologio.avanza()
    conferma_versione(registro, versione.id)
    assert stato_versione(registro, versione.id) is StatoVersione.CONFERMATA


def test_la_ragioneria_respinge_con_un_motivo(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    orologio.avanza()
    respingi_versione(registro, versione.id, "impegno non capiente")
    assert stato_versione(registro, versione.id) is StatoVersione.RESPINTA
    assert registro.stati_versione(versione.id, orologio())[-1][1] == "impegno non capiente"


def test_il_rifiuto_vuole_il_motivo(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    with pytest.raises(ErroreRegistro, match="motivo"):
        respingi_versione(registro, versione.id, "  ")
    assert stato_versione(registro, versione.id) is StatoVersione.INVIATA


def test_una_versione_respinta_o_confermata_non_si_conferma_di_nuovo(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    orologio.avanza()
    conferma_versione(registro, versione.id)
    with pytest.raises(ErroreRegistro, match="non si conferma"):
        conferma_versione(registro, versione.id)
    with pytest.raises(ErroreRegistro, match="non si respinge"):
        respingi_versione(registro, versione.id, "tardi")


def test_gli_stati_sono_eventi_e_la_storia_resta(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    orologio.avanza()
    conferma_versione(registro, versione.id)
    assert [stato for stato, _, _ in registro.stati_versione(versione.id, orologio())] == ["inviata", "confermata"]


def test_lo_stato_si_legge_a_un_istante(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    emissione = orologio()
    orologio.avanza(3600)
    conferma_versione(registro, versione.id)
    assert stato_versione(registro, versione.id, emissione) is StatoVersione.INVIATA
    assert stato_versione(registro, versione.id, orologio()) is StatoVersione.CONFERMATA


def test_lo_stato_prima_dell_emissione_non_e_noto(registro, corpus_p, orologio):
    assumi(registro)
    prima = orologio()
    versione, _ = emessa(registro, corpus_p, orologio)
    with pytest.raises(ErroreRegistro, match="non ancora nota"):
        stato_versione(registro, versione.id, prima)


def test_una_versione_inesistente_non_ha_stato(registro):
    with pytest.raises(ErroreRegistro, match="inesistente"):
        stato_versione(registro, 99)


# Versione superata

def test_se_nulla_cambia_la_versione_non_e_superata(registro, corpus_p, orologio):
    versione, importi = emessa(registro, corpus_p, orologio)
    orologio.avanza(3600)
    assert not controlla_superata(registro, corpus_p, versione.id, ricalcola(registro, corpus_p))
    assert stato_versione(registro, versione.id) is StatoVersione.INVIATA


def test_un_fatto_che_cambia_dopo_l_invio_rende_superata_la_versione(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    cambia_lo_stipendio(registro, orologio)
    assert controlla_superata(registro, corpus_p, versione.id, ricalcola(registro, corpus_p))
    assert stato_versione(registro, versione.id) is StatoVersione.SUPERATA


def test_vale_anche_per_una_versione_gia_confermata(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    orologio.avanza()
    conferma_versione(registro, versione.id)
    cambia_lo_stipendio(registro, orologio)
    assert controlla_superata(registro, corpus_p, versione.id, ricalcola(registro, corpus_p))
    assert [s for s, _, _ in registro.stati_versione(versione.id, orologio())] == ["inviata", "confermata", "superata"]


def test_un_fatto_dell_ente_dopo_l_invio_rende_superata_la_versione(registro, corpus_p, orologio):
    """Il fatto sull'ultimo pagamento porta il conguaglio che la versione già inviata non aveva."""
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 18), importi)
    orologio.avanza(3600)
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    assert controlla_superata(registro, corpus_p, versione.id, importi)


def test_il_ricalcolo_e_a_un_istante_dato(registro, corpus_p, orologio):
    versione, importi = emessa(registro, corpus_p, orologio)
    prima = orologio()
    cambia_lo_stipendio(registro, orologio)
    assert not controlla_superata(registro, corpus_p, versione.id, importi, noto_al=prima)
    assert stato_versione(registro, versione.id) is StatoVersione.INVIATA
    assert controlla_superata(registro, corpus_p, versione.id, ricalcola(registro, corpus_p))


def test_il_controllo_ripetuto_non_aggiunge_stati(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    cambia_lo_stipendio(registro, orologio)
    nuovi = ricalcola(registro, corpus_p)
    assert controlla_superata(registro, corpus_p, versione.id, nuovi)
    assert controlla_superata(registro, corpus_p, versione.id, nuovi)
    assert len(registro.stati_versione(versione.id, orologio())) == 2


def test_dopo_l_evento_di_pagamento_la_versione_non_e_piu_da_superare(registro, corpus_p, orologio):
    versione, _ = emessa(registro, corpus_p, orologio)
    orologio.avanza()
    conferma_versione(registro, versione.id)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", "adattatore-prova", versione.id, VALUTA, versione.rapporti)
    cambia_lo_stipendio(registro, orologio)
    assert not controlla_superata(registro, corpus_p, versione.id, ricalcola(registro, corpus_p))
    assert stato_versione(registro, versione.id) is StatoVersione.CONFERMATA


def test_una_versione_respinta_non_si_ricalcola(registro, corpus_p, orologio):
    versione, importi = emessa(registro, corpus_p, orologio)
    orologio.avanza()
    respingi_versione(registro, versione.id, "no")
    with pytest.raises(ErroreRegistro, match="respinta"):
        controlla_superata(registro, corpus_p, versione.id, importi)


def test_la_versione_piu_recente_si_ricalcola_sul_nuovo_esito(registro, corpus_p, orologio):
    """Pagata la prima versione, la seconda, emessa prima dell'esito, non porta più gli stessi importi."""
    versione1, importi = emessa(registro, corpus_p, orologio)
    orologio.avanza()
    versione2 = emetti_versione(registro, corpus_p, VALUTA, importi)
    conferma_versione(registro, versione1.id)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", "adattatore-prova", versione1.id, VALUTA, versione1.rapporti)
    orologio.avanza(3600)
    assert controlla_superata(registro, corpus_p, versione2.id, importi)
    assert stato_versione(registro, versione2.id) is StatoVersione.SUPERATA
