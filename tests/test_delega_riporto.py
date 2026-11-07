"""Credito non assorbito: resta visibile e passa alla scadenza successiva come fatto sull'ente con la sua origine (ADR 0023).

Febbraio: debiti 630,00 (100E 100, 104E 50, P201 480) e credito 170E di 1000,00; assorbiti 630, residuo 370,00.
Marzo: ritenuta di 200,00, il riporto ne assorbe 200 e ne restano 170. Aprile: ritenuta di 100,00, restano 70.
Dati fittizi.
"""

import json
from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from paghe.delega import (
    annulla_delega,
    costruisci_delega,
    crediti_riportati,
    leggi_delega_trasmessa,
    trasmetti_delega,
)
from paghe.proposta import registra_ricevuta_delega

from materiale_delega import ADATTATORE, corpus_delega, dati_ente, paga_a_mano, riga_a_mano

FEB, MAR, APR = Mese(2026, 2), Mese(2026, 3), Mese(2026, 4)
D = Decimal
CHIAVE_170E_FEB = ("F", "170E", "", "", "0002", "2026")


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def febbraio(registro, corpus, orologio):
    """Febbraio pagato e la sua delega trasmessa, con un residuo di credito di 370,00."""
    dati_ente(registro)
    for mese, versamento in ((FEB, date(2026, 3, 16)), (MAR, date(2026, 4, 16)), (APR, date(2026, 5, 15))):
        registro.registra_data_versamento(mese, versamento)
    valuta = date(2026, 2, 27)
    righe = [
        riga_a_mano(corpus, valuta, i, v)
        for i, v in (("ritenuta_irpef", "100"), ("ritenuta_arretrati", "50"), ("contributo_ente", "480"), ("credito_integrativo", "1000"))
    ]
    paga_a_mano(registro, corpus, orologio, valuta, righe, "pag-feb")
    orologio.vai(3, 10)
    return trasmetti_delega(registro, corpus, "DELEGA-FEB", ADATTATORE, FEB)


def paga_mese(registro, corpus, orologio, valuta, ritenuta, chiave):
    paga_a_mano(registro, corpus, orologio, valuta, [riga_a_mano(corpus, valuta, "ritenuta_irpef", ritenuta)], chiave)
    orologio.avanza(3600)


def test_la_vista_mostra_il_residuo_senza_scrivere_nessun_fatto(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    valuta = date(2026, 2, 27)
    righe = [riga_a_mano(corpus, valuta, i, v) for i, v in (("ritenuta_irpef", "100"), ("credito_integrativo", "1000"))]
    paga_a_mano(registro, corpus, orologio, valuta, righe)
    d = costruisci_delega(registro, corpus, FEB)
    assert [(r.chiave, r.importo) for r in d.residui] == [(CHIAVE_170E_FEB, D("900"))]
    assert crediti_riportati(registro, orologio()) == ()


def test_la_trasmissione_registra_il_residuo_come_fatto_sull_ente_con_la_sua_origine(registro, corpus, orologio, febbraio):
    (riporto,) = crediti_riportati(registro, orologio())
    assert (riporto.chiave, riporto.importo) == (CHIAVE_170E_FEB, D("370"))
    assert (riporto.delega, riporto.scadenza) == ("DELEGA-FEB", date(2026, 3, 16))
    assert sum(o.valore for o in riporto.origine) == D("1000") and riporto.origine[0].riferimento is not None
    fatto = registro.fatti_ente_noti("credito_riportato", orologio())[0]
    assert fatto.id == riporto.fatto_id and fatto.valido_dal == date(2026, 3, 17) and fatto.soggetto == "ente"
    assert json.loads(fatto.valore)["delega"] == "DELEGA-FEB"


def test_la_delega_trasmessa_dice_quali_riporti_ha_usato(registro, corpus, orologio, febbraio):
    assert febbraio.riporti_usati == ()
    assert [(r.chiave, r.importo) for r in febbraio.residui] == [(CHIAVE_170E_FEB, D("370"))]


def test_il_credito_riportato_entra_nella_delega_della_scadenza_successiva(registro, corpus, orologio, febbraio):
    (riporto,) = crediti_riportati(registro, orologio())
    paga_mese(registro, corpus, orologio, date(2026, 3, 27), "200", "pag-mar")
    d = costruisci_delega(registro, corpus, MAR)
    (credito,) = [r for r in d.righe if r.credito]
    assert (credito.chiave, credito.credito) == (CHIAVE_170E_FEB, D("200"))
    assert [(o.riporto, o.valore, o.riferimento) for o in credito.origine] == [(riporto.fatto_id, D("370"), None)]
    assert d.saldo == D("0") and d.riporti_usati == (riporto.fatto_id,)
    assert [(r.chiave, r.importo) for r in d.residui] == [(CHIAVE_170E_FEB, D("170"))]


def test_il_riporto_non_entra_nella_delega_che_l_ha_generato(registro, corpus, orologio, febbraio):
    d = costruisci_delega(registro, corpus, FEB, ignorando_delega="DELEGA-FEB")
    assert d.riporti_usati == () and [r.credito for r in d.righe if r.credito] == [D("630")]


def test_il_residuo_si_porta_di_scadenza_in_scadenza_con_la_catena_delle_origini(registro, corpus, orologio, febbraio):
    paga_mese(registro, corpus, orologio, date(2026, 3, 27), "200", "pag-mar")
    trasmetti_delega(registro, corpus, "DELEGA-MAR", ADATTATORE, MAR)
    paga_mese(registro, corpus, orologio, date(2026, 4, 27), "100", "pag-apr")
    d = costruisci_delega(registro, corpus, APR)
    (credito,) = [r for r in d.righe if r.credito]
    assert credito.credito == D("100")
    assert [(r.chiave, r.importo) for r in d.residui] == [(CHIAVE_170E_FEB, D("70"))]
    riporti = crediti_riportati(registro, orologio())
    assert [(r.delega, r.importo) for r in riporti] == [("DELEGA-FEB", D("370")), ("DELEGA-MAR", D("170"))]
    # il riporto di marzo è quello che aprile usa: quello di febbraio l'ha già usato marzo
    assert d.riporti_usati == (riporti[1].fatto_id,)
    assert riporti[1].origine[0].riporto == riporti[0].fatto_id  # la catena arriva fino alle righe pagate


def test_un_riporto_usato_da_una_delega_attiva_non_si_usa_due_volte(registro, corpus, orologio, febbraio):
    paga_mese(registro, corpus, orologio, date(2026, 3, 27), "200", "pag-mar")
    trasmetti_delega(registro, corpus, "DELEGA-MAR", ADATTATORE, MAR)
    assert leggi_delega_trasmessa(registro, "DELEGA-MAR").riporti_usati == (crediti_riportati(registro, orologio())[0].fatto_id,)
    paga_mese(registro, corpus, orologio, date(2026, 4, 27), "100", "pag-apr")
    assert costruisci_delega(registro, corpus, APR).totale_credito == D("100")  # solo i 170 di marzo, 100 assorbiti


def test_se_la_delega_di_origine_e_scartata_il_suo_riporto_non_vale(registro, corpus, orologio, febbraio):
    registra_ricevuta_delega(registro, "r-1", ADATTATORE, "DELEGA-FEB", "controllo_crediti", "negativo")
    paga_mese(registro, corpus, orologio, date(2026, 3, 27), "200", "pag-mar")
    d = costruisci_delega(registro, corpus, MAR)
    assert d.riporti_usati == () and d.totale_credito == D("0")
    assert crediti_riportati(registro, orologio()) == ()


def test_se_la_delega_di_origine_e_annullata_il_suo_riporto_non_vale(registro, corpus, orologio, febbraio):
    annulla_delega(registro, corpus, "ann-1", ADATTATORE, "DELEGA-FEB")
    paga_mese(registro, corpus, orologio, date(2026, 3, 27), "200", "pag-mar")
    assert costruisci_delega(registro, corpus, MAR).riporti_usati == ()


def test_se_la_delega_che_usa_il_riporto_e_scartata_il_riporto_torna_disponibile(registro, corpus, orologio, febbraio):
    paga_mese(registro, corpus, orologio, date(2026, 3, 27), "200", "pag-mar")
    trasmetti_delega(registro, corpus, "DELEGA-MAR", ADATTATORE, MAR)
    registra_ricevuta_delega(registro, "r-2", ADATTATORE, "DELEGA-MAR", "addebito", "negativo")
    nuova = trasmetti_delega(registro, corpus, "DELEGA-MAR-2", ADATTATORE, MAR)
    assert nuova.riporti_usati == (crediti_riportati(registro, orologio())[0].fatto_id,)
    assert nuova.totale_credito == D("200")


def test_il_riporto_si_somma_a_un_credito_nuovo_con_lo_stesso_codice_e_riferimenti(registro, corpus, orologio):
    """Rimborso 730 dell'anno d'imposta 2025 (150E): febbraio ne riporta 200,00, marzo ne aggiunge 50,00."""
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    registro.registra_data_versamento(MAR, date(2026, 4, 16))
    feb, mar = date(2026, 2, 27), date(2026, 3, 27)
    paga_a_mano(
        registro, corpus, orologio, feb,
        [riga_a_mano(corpus, feb, "ritenuta_irpef", "100"), riga_a_mano(corpus, feb, "rimborso_irpef_730", "300", anno_imposta=2025)],
        "pag-feb",
    )
    orologio.vai(3, 10)
    trasmetti_delega(registro, corpus, "DELEGA-FEB", ADATTATORE, FEB)
    paga_a_mano(
        registro, corpus, orologio, mar,
        [riga_a_mano(corpus, mar, "ritenuta_irpef", "200"), riga_a_mano(corpus, mar, "rimborso_irpef_730", "50", anno_imposta=2025)],
        "pag-mar",
    )
    d = costruisci_delega(registro, corpus, MAR)
    (credito,) = [r for r in d.righe if r.credito]
    assert (credito.chiave, credito.credito) == (("F", "150E", "", "", "", "2025"), D("200"))
    assert sorted((o.valore, o.riporto is not None, o.riferimento is not None) for o in credito.origine) == [
        (D("50"), False, True), (D("200"), True, False),
    ]
    assert [r.importo for r in d.residui] == [D("50")]


def test_un_riporto_senza_debiti_nella_scadenza_ferma_l_invio_nominando_il_caso(registro, corpus, orologio, febbraio):
    valuta = date(2026, 3, 27)
    paga_a_mano(registro, corpus, orologio, valuta, [riga_a_mano(corpus, valuta, "pignoramento", "10")], "pag-mar")
    d = costruisci_delega(registro, corpus, MAR)
    assert d.righe == () and {f.caso for f in d.fermi} == {"solo_crediti"}
