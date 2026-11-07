"""Evento di ritorno del pagamento eseguito: esito pagato, data di pagamento, valuta diversa (ADR 0025). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese, TipoEsito, attribuisci_reddito, calcola, calcola_denuncia, calcola_fiscale
from paghe.errori import CasoNonModellato, ErroreRegistro
from paghe.proposta import (
    AVVISO_ALTRO_MESE,
    AVVISO_ANNO_DIVERSO,
    StatoVersione,
    conferma_versione,
    controlla_superata,
    emetti_versione,
    registra_pagamento_eseguito,
    respingi_versione,
    stato_versione,
)

from materiale_proposta import P, P2, R, R2, assumi, corpus_p, per_istituto, stipendio

VALUTA = date(2026, 2, 27)
FEB = Mese(2026, 2)
ADATTATORE = "adattatore-prova"


def due_rapporti(registro, corpus, orologio):
    assumi(registro)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus, FEB) + stipendio(registro, corpus, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    conferma_versione(registro, versione.id)
    orologio.avanza()
    return versione, importi


def test_il_pagamento_crea_l_esito_pagato_con_le_righe_dei_soli_rapporti_pagati(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    risultato = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    esito = registro.esito(risultato.esito.id)
    assert esito.tipo is TipoEsito.PAGATO and esito.data == VALUTA
    assert {riga.rapporto for riga in esito.righe} == {R}
    # tutte le righe di composizione del rapporto, anche a carico ente, collegate agli stessi importi
    assert [r.istituto for r in esito.righe] == [r.istituto for r in versione.righe_del_rapporto(R)]
    assert "contributo_ente" in {riga.istituto for riga in esito.righe}
    assert list(esito.righe) == [r.importo for r in versione.righe_del_rapporto(R)]


def test_il_rapporto_non_pagato_non_ha_esito_e_riparte_con_una_nuova_versione(registro, corpus_p, orologio):
    versione, importi = due_rapporti(registro, corpus_p, orologio)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    assert registro.pagamenti(R2, orologio()) == {}
    orologio.avanza(3600)
    nuova = emetti_versione(registro, corpus_p, VALUTA, importi)
    assert nuova.rapporti == (R2,)
    assert [e.importo for e in nuova.esclusi] == [i for i in importi if i.rapporto == R]


def test_per_ogni_rapporto_pagato_c_e_il_fatto_data_di_pagamento(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    esito = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R, R2]).esito
    for rapporto in (R, R2):
        (fatto,) = registro.pagamenti(rapporto, orologio()).values()
        assert (fatto.valido_dal, fatto.valido_al, int(fatto.valore)) == (VALUTA, VALUTA, esito.id)


def test_c_e_un_collegamento_tra_esito_e_versione_e_l_adattatore_resta(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    esito = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R]).esito
    evento = registro.evento("pag-1")
    assert (evento.versione_id, evento.esito_id, evento.adattatore, evento.tipo) == (
        versione.id, esito.id, ADATTATORE, "pagamento_eseguito",
    )
    assert evento.contenuto == {"versione": versione.id, "valuta": "2026-02-27", "rapporti": [R]}


def test_lo_stesso_identificativo_con_lo_stesso_contenuto_non_ha_effetto(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    primo = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    orologio.avanza()
    secondo = registra_pagamento_eseguito(registro, corpus_p, "pag-1", "altro-adattatore", versione.id, VALUTA, [R])
    assert secondo.esito == primo.esito
    assert len(registro.esiti(TipoEsito.PAGATO, orologio())) == 1
    assert len(registro.pagamenti(R, orologio())) == 1
    assert len(registro.eventi("pagamento_eseguito", orologio())) == 1
    assert registro.evento("pag-1").adattatore == ADATTATORE


def test_lo_stesso_identificativo_con_contenuto_diverso_e_un_errore_e_non_crea_fatti(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    orologio.avanza()
    for valuta, rapporti in [(date(2026, 2, 28), [R]), (VALUTA, [R, R2])]:
        with pytest.raises(ErroreRegistro, match="contenuto diverso"):
            registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, valuta, rapporti)
    assert len(registro.esiti(TipoEsito.PAGATO, orologio())) == 1
    assert registro.pagamenti(R2, orologio()) == {}
    assert len(registro.eventi("pagamento_eseguito", orologio())) == 1


def test_un_secondo_evento_per_lo_stesso_rapporto_e_versione_con_altro_identificativo_e_un_errore(registro, corpus_p, orologio):
    """La valuta si corregge con un evento nuovo, ma non per un rapporto già pagato dalla stessa versione (ADR 0025)."""
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    with pytest.raises(ErroreRegistro, match="già pagati"):
        registra_pagamento_eseguito(registro, corpus_p, "pag-2", ADATTATORE, versione.id, date(2026, 2, 28), [R])
    assert len(registro.esiti(TipoEsito.PAGATO, orologio())) == 1


def test_un_secondo_evento_per_altri_rapporti_della_stessa_versione_e_ammesso(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    primo = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R]).esito
    secondo = registra_pagamento_eseguito(registro, corpus_p, "pag-2", ADATTATORE, versione.id, date(2026, 3, 2), [R2]).esito
    assert primo.id != secondo.id
    assert {r.rapporto for r in secondo.righe} == {R2}


def test_un_rapporto_che_la_versione_non_porta_e_un_errore(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    with pytest.raises(ErroreRegistro, match="non sono tra quelli"):
        registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, ["RAPPORTO-9"])
    with pytest.raises(ErroreRegistro, match="almeno un rapporto"):
        registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [])


def test_il_pagamento_vale_per_una_versione_confermata(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    inviata = emetti_versione(registro, corpus_p, VALUTA, importi)
    with pytest.raises(ErroreRegistro, match="confermata"):
        registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, inviata.id, VALUTA, [R])
    orologio.avanza()
    respinta = emetti_versione(registro, corpus_p, VALUTA, importi)
    respingi_versione(registro, respinta.id, "no")
    with pytest.raises(ErroreRegistro, match="confermata"):
        registra_pagamento_eseguito(registro, corpus_p, "pag-2", ADATTATORE, respinta.id, VALUTA, [R])
    assert registro.esiti(TipoEsito.PAGATO, orologio()) == []


def test_la_scrittura_e_atomica(registro, corpus_p, orologio, monkeypatch):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    vera = registro.registra_pagamento

    def guasta(rapporto, esito_id, data, atto=None):
        if rapporto == R2:
            raise RuntimeError("guasto a metà")
        return vera(rapporto, esito_id, data, atto)

    monkeypatch.setattr(registro, "registra_pagamento", guasta)
    with pytest.raises(RuntimeError):
        registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R, R2])
    assert registro.esiti(TipoEsito.PAGATO, orologio()) == []
    assert registro.pagamenti(R, orologio()) == {}
    assert registro.evento("pag-1") is None
    monkeypatch.undo()
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R, R2])
    assert len(registro.esiti(TipoEsito.PAGATO, orologio())) == 1


def test_l_evento_si_legge_a_un_istante(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    prima = orologio()
    orologio.avanza(3600)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    assert registro.eventi("pagamento_eseguito", prima) == []
    assert registro.esiti(TipoEsito.PAGATO, prima) == []
    assert len(registro.eventi("pagamento_eseguito", orologio())) == 1


# Valuta effettiva diversa dalla prevista

def test_nello_stesso_mese_non_ci_sono_conseguenze(registro, corpus_p, orologio):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    risultato = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, date(2026, 2, 20), [R])
    assert risultato.avvisi == ()
    (fatto,) = registro.pagamenti(R, orologio()).values()
    assert fatto.valido_dal == date(2026, 2, 20)
    assert calcola_denuncia(registro, corpus_p, R, FEB).periodi[0].base("pens").valore == Decimal("1500")


def test_in_un_altro_mese_dello_stesso_anno_gli_importi_entrano_nella_denuncia_del_mese_reale_con_un_avviso(
    registro, corpus_p, orologio
):
    versione, _ = due_rapporti(registro, corpus_p, orologio)
    risultato = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, date(2026, 3, 2), [R])
    (avviso,) = risultato.avvisi
    assert avviso.tipo == AVVISO_ALTRO_MESE and avviso.persona == P
    assert "pagamento successivo" in avviso.messaggio
    assert calcola_denuncia(registro, corpus_p, R, Mese(2026, 3)).periodi[0].base("pens").valore == Decimal("1500")
    assert calcola_denuncia(registro, corpus_p, R, FEB).periodi[0].base("pens") is None
    # l'esito resta com'era: ritenuta e contributi del mese previsto non si riscrivono
    assert {r.istituto for r in risultato.esito.righe} == {"stipendio", "contributo_lavoratore", "contributo_ente", "ritenuta_irpef"}


def test_in_un_altro_anno_d_imposta_l_esito_resta_e_il_calcolo_fiscale_della_persona_si_ferma(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 18), importi)
    conferma_versione(registro, versione.id)
    prima = orologio()
    orologio.avanza(3600)
    risultato = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, date(2027, 1, 20), [R])
    assert [a.tipo for a in risultato.avvisi] == [AVVISO_ANNO_DIVERSO]
    # le righe restano com'erano, con l'anno d'imposta della valuta prevista
    assert risultato.esito.data == date(2027, 1, 20)
    assert {r.anno_imposta for r in risultato.esito.righe if r.istituto == "stipendio"} == {2026}
    assert [r.valore for r in risultato.esito.righe] == [r.importo.valore for r in versione.righe]
    # il fermo si ricava dal registro: nessun altro dato da dichiarare
    nuovi = stipendio(registro, corpus_p, Mese(2027, 1))
    attribuiti = attribuisci_reddito(corpus_p, nuovi, date(2027, 2, 27))
    with pytest.raises(CasoNonModellato, match="anno d'imposta diverso dal previsto"):
        calcola_fiscale(registro, corpus_p, R, attribuiti, date(2027, 2, 27))
    # prima dell'evento il calcolo non era fermo
    calcola_fiscale(registro, corpus_p, R, attribuiti, date(2027, 2, 27), noto_al=prima)


def test_una_nuova_versione_per_quella_persona_ferma_il_rapporto_e_nomina_il_caso(registro, corpus_p, orologio):
    assumi(registro)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 18), importi)
    conferma_versione(registro, versione.id)
    orologio.avanza(3600)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, date(2027, 1, 20), [R])
    orologio.vai(1, 25, 2027)
    nuovi = stipendio(registro, corpus_p, Mese(2027, 1)) + stipendio(registro, corpus_p, Mese(2027, 1), "800", R2)
    nuova = emetti_versione(registro, corpus_p, date(2027, 2, 27), nuovi)
    assert nuova.rapporti == (R2,)
    (fermo,) = nuova.fermi
    assert fermo.rapporto == R and "anno d'imposta diverso" in fermo.motivo


def test_il_ritardo_oltre_il_12_gennaio_con_la_cassa_allargata_cambia_l_anno(registro, corpus_p, orologio):
    """Previsto il 10 gennaio (anno prima), pagato il 13: l'anno d'imposta è un altro."""
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(1, 5, 2027)
    versione = emetti_versione(registro, corpus_p, date(2027, 1, 10), importi)
    conferma_versione(registro, versione.id)
    risultato = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, date(2027, 1, 13), [R])
    assert [a.tipo for a in risultato.avvisi] == [AVVISO_ANNO_DIVERSO]


def test_lo_scivolamento_dentro_il_12_gennaio_non_cambia_l_anno(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(1, 5, 2027)
    versione = emetti_versione(registro, corpus_p, date(2027, 1, 10), importi)
    conferma_versione(registro, versione.id)
    risultato = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, date(2027, 1, 12), [R])
    assert risultato.avvisi == ()


def test_prima_dell_evento_il_fermo_non_c_e_e_dopo_l_annullamento_del_fatto_sparisce(registro, corpus_p, orologio):
    """Il fermo è un fatto della persona: si neutralizza come ogni fatto errato."""
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 18), importi)
    conferma_versione(registro, versione.id)
    orologio.avanza(3600)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, date(2027, 1, 20), [R])
    (fatto,) = registro.fatti_persona_noti(P, "anno_imposta_diverso", orologio())
    orologio.avanza()
    registro.annulla_fatto(fatto.id, "valuta registrata male")
    nuovi = stipendio(registro, corpus_p, Mese(2027, 1))
    attribuiti = attribuisci_reddito(corpus_p, nuovi, date(2027, 2, 27))
    calcola_fiscale(registro, corpus_p, R, attribuiti, date(2027, 2, 27))


# Versione superata: vince il denaro reale

def test_l_evento_su_una_versione_superata_crea_l_esito_dalle_righe_della_versione(registro, corpus_p, orologio):
    versione, importi = due_rapporti(registro, corpus_p, orologio)
    orologio.avanza(3600)
    registro.registra_fatto(R, "mensile", "1600", FEB.primo_giorno, FEB.ultimo_giorno)
    nuovi = [r for r in calcola(registro, corpus_p, R, FEB) if r.istituto == "stipendio"]
    assert controlla_superata(registro, corpus_p, versione.id, nuovi + [i for i in importi if i.rapporto == R2])
    orologio.avanza()
    risultato = registra_pagamento_eseguito(registro, corpus_p, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    stipendio_pagato = per_istituto(risultato.esito.righe)["stipendio"]
    assert stipendio_pagato.valore == Decimal("1500")  # le righe di quella versione, non il ricalcolo
    assert stato_versione(registro, versione.id) is StatoVersione.SUPERATA
    # la differenza col dovuto entra nel pagamento successivo
    from paghe import differenze

    (arretrato,) = (d for d in differenze(registro, corpus_p, R, FEB, TipoEsito.PAGATO) if d.istituto == "stipendio")
    assert arretrato.valore == Decimal("100")
