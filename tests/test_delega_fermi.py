"""Controllo di completezza della delega F24EP: ciò che ferma l'invio e non il calcolo (ADR 0023, 0022). Dati fittizi.

Una riga che non si può portare resta fuori dalla vista e nomina il caso; le altre righe valide restano.
"""

from calendar import monthrange
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, Periodo
from paghe.delega import costruisci_delega

from materiale_delega import R, R2, corpus_delega, dati_ente, paga_a_mano, riga_a_mano, toml_delega

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal


@pytest.fixture
def corpus():
    return corpus_delega()


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))


def delega_di(registro, corpus, orologio, **istituti_e_valori):
    righe = [riga_a_mano(corpus, VALUTA, istituto, valore) for istituto, valore in istituti_e_valori.items()]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    return costruisci_delega(registro, corpus, FEB)


def casi(delega):
    return {(f.caso, f.motivo) for f in delega.fermi}


def test_un_importo_senza_mappatura_ferma_l_invio_e_nomina_l_istituto(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", debito_senza_codice="10")
    (fermo,) = d.fermi
    assert fermo.caso == "mappatura_mancante" and "debito_senza_codice" in fermo.motivo
    assert not d.pronta


def test_le_altre_righe_valide_restano_nella_vista(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", debito_senza_codice="10")
    assert [(r.tributo, r.debito) for r in d.righe] == [("104E", D("50"))]


def test_anche_un_credito_senza_mappatura_ferma_l_invio(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", credito_senza_codice="10")
    (fermo,) = d.fermi
    assert fermo.caso == "mappatura_mancante" and "credito_senza_codice" in fermo.motivo


def test_la_mappatura_e_quella_vigente_alla_data_di_pagamento(registro, orologio, ente):
    scaduta = toml_delega().replace(
        'codice = "100E"\ndal = 2020-01-01', 'codice = "100E"\ndal = 2020-01-01\nal = 2025-12-31'
    )
    corpus = Corpus.da_toml(scaduta)
    d = delega_di(registro, corpus, orologio, credito_su_codice_a_debito="10")
    assert {f.caso for f in d.fermi} == {"mappatura_mancante"}


def test_un_codice_fuori_dal_catalogo_ferma_l_invio_e_nomina_istituto_e_codice(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", debito_codice_ignoto="10")
    (fermo,) = d.fermi
    assert fermo.caso == "codice_fuori_catalogo" and "debito_codice_ignoto" in fermo.motivo and "999E" in fermo.motivo
    assert [r.tributo for r in d.righe] == ["104E"]


def test_le_righe_irap_fermano_l_invio_nominando_scadenza_e_riparto_per_regione(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", irap_acconto="40")
    (fermo,) = d.fermi
    assert fermo.caso == "irap" and "irap_acconto" in fermo.motivo
    assert "scadenza" in fermo.motivo and "riparto per regione" in fermo.motivo
    assert [r.tributo for r in d.righe] == ["104E"]  # il resto della delega non cambia


def test_un_codice_che_vuole_il_comune_o_la_regione_ferma_l_invio_nominando_il_caso(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", addizionale_comunale="10")
    (fermo,) = d.fermi
    assert fermo.caso == "codice_non_modellato" and "addizionale_comunale" in fermo.motivo
    assert "catastale" in fermo.motivo


def test_un_credito_su_un_codice_solo_a_debito_ferma_l_invio(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", credito_su_codice_a_debito="10")
    (fermo,) = d.fermi
    assert fermo.caso == "credito_su_codice_a_debito" and "credito_su_codice_a_debito" in fermo.motivo
    assert "100E" in fermo.motivo


def test_un_credito_con_un_limite_non_modellato_ferma_l_invio_nominando_il_codice(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", credito_somma_175="10")
    (fermo,) = d.fermi
    assert fermo.caso == "limite_credito" and "175E" in fermo.motivo and "credito_somma_175" in fermo.motivo


def test_un_credito_per_anno_d_imposta_senza_l_anno_ferma_l_invio(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", rimborso_irpef_730="10")  # senza anno d'imposta
    (fermo,) = d.fermi
    assert fermo.caso == "anno_imposta_mancante" and "rimborso_irpef_730" in fermo.motivo


def test_piu_fermi_diversi_sono_tutti_nominati(registro, corpus, orologio, ente):
    d = delega_di(registro, corpus, orologio, ritenuta_arretrati="50", debito_senza_codice="1", irap_acconto="2")
    assert {f.caso for f in d.fermi} == {"mappatura_mancante", "irap"}


def test_lo_stesso_istituto_in_piu_righe_e_nominato_una_volta(registro, corpus, orologio, ente):
    righe = [riga_a_mano(corpus, VALUTA, "debito_senza_codice", v, rapporto=r) for v, r in (("1", R), ("2", R2))]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    assert len(costruisci_delega(registro, corpus, FEB).fermi) == 1


def test_piu_di_22_righe_in_un_modulo_fermano_l_invio(registro, corpus, orologio, ente):
    """Più moduli richiedono di dividere i crediti tra le pagine: il caso non è modellato."""
    righe = []
    for numero in range(23):
        anno, mese = divmod(2024 * 12 + 3 + numero, 12)
        periodo = Periodo(date(anno, mese + 1, 1), date(anno, mese + 1, monthrange(anno, mese + 1)[1]))
        righe.append(riga_a_mano(corpus, VALUTA, "contributo_ente", "1", periodo=periodo))
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    d = costruisci_delega(registro, corpus, FEB)
    assert len(d.righe) == 23
    assert {f.caso for f in d.fermi} == {"piu_di_22_righe"}
    assert not d.pronta
