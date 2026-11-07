"""Il ciclo della delega dal calcolo al versamento e i casi limite (ADR 0023). Dati fittizi.

Stipendio di 1500 a febbraio 2026, pagato il 27: ritenuta 100,00, contributi 480,00 (lavoratore 120 e ente 360).
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, TipoEsito
from paghe.delega import (
    costruisci_delega,
    registra_versamento_delega,
    situazione_delega,
    trasmetti_delega,
)
from paghe.errori import VistaFerma
from paghe.proposta import StatoDelega, conferma_versione, emetti_versione, registra_pagamento_eseguito, registra_ricevuta_delega

from controlli_f24ep import controlla
from materiale_delega import (
    ADATTATORE, R, R2, corpus_delega, dati_ente, paga_a_mano, riga_a_mano, toml_delega,
)
from materiale_proposta import P2, assumi, paga, stipendio

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
D = Decimal


@pytest.fixture
def corpus():
    return corpus_delega()


def test_il_ciclo_dal_calcolo_alla_delega_versata(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    assumi(registro)
    paga(registro, corpus, orologio, stipendio(registro, corpus, FEB), VALUTA, "pag-1")
    orologio.vai(3, 10)
    t = trasmetti_delega(registro, corpus, "DELEGA-FEB", ADATTATORE, FEB)
    assert [(r.tributo, r.debito) for r in t.righe] == [("100E", D("100.00")), ("P201", D("480.00"))]
    assert controlla(t.file) == ([], [])
    for numero, fase in enumerate(("controlli_formali", "controllo_crediti", "addebito")):
        registra_ricevuta_delega(registro, f"r-{numero}", ADATTATORE, "DELEGA-FEB", fase, "positivo")
    orologio.vai(3, 16)
    esito = registra_versamento_delega(registro, "ver-1", ADATTATORE, "DELEGA-FEB", date(2026, 3, 16))
    assert esito.tipo is TipoEsito.VERSATO and sum(r.valore for r in esito.righe) == D("580.00")
    s = situazione_delega(registro, "DELEGA-FEB")
    assert (s.stato, s.versata_il, s.fermi) == (StatoDelega.ADDEBITATA, date(2026, 3, 16), ())
    assert costruisci_delega(registro, corpus, FEB).righe == ()


def test_un_rapporto_fermo_o_non_pagato_non_entra_nella_delega(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    assumi(registro)
    assumi(registro, R2, P2)
    assumi(registro, "RAPPORTO-3", P2)  # due rapporti della stessa persona: caso non modellato, entrambi fermi
    importi = (
        stipendio(registro, corpus, FEB)
        + stipendio(registro, corpus, FEB, "500", R2)
        + stipendio(registro, corpus, FEB, "300", "RAPPORTO-3")
    )
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert versione.rapporti == (R,) and {f.rapporto for f in versione.fermi} == {R2, "RAPPORTO-3"}
    conferma_versione(registro, versione.id)
    registra_pagamento_eseguito(registro, corpus, "pag-1", ADATTATORE, versione.id, VALUTA, [R])
    d = costruisci_delega(registro, corpus, FEB)
    assert {o.riferimento.rapporto for r in d.righe for o in r.origine} == {R}
    assert d.saldo == D("580.00")


def test_una_riga_senza_mappatura_con_altre_valide_ferma_l_invio_e_non_la_vista(registro, orologio):
    senza = Corpus.da_toml(
        toml_delega().replace(
            '[[mappatura]]\nistituto = "contributo_ente"\nsistema = "codice_tributo_f24ep"\ncodice = "P201"\ndal = 2020-01-01\n'
            'riferimento = "fittizio:mappatura-contributo-ente"\n',
            "",
        )
    )
    assert senza.mappatura("contributo_ente", "codice_tributo_f24ep", VALUTA) is None
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    assumi(registro)
    paga(registro, senza, orologio, stipendio(registro, senza, FEB), VALUTA, "pag-1")
    d = costruisci_delega(registro, senza, FEB)
    assert [(r.tributo, r.debito) for r in d.righe] == [("100E", D("100.00")), ("P201", D("120.00"))]
    (fermo,) = d.fermi
    assert fermo.caso == "mappatura_mancante" and "contributo_ente" in fermo.motivo
    with pytest.raises(VistaFerma, match="contributo_ente"):
        trasmetti_delega(registro, senza, "DELEGA-FEB", ADATTATORE, FEB)
    assert registro.esiti(TipoEsito.DICHIARATO, orologio()) == []


def test_saldo_zero_si_trasmette_con_il_saldo_totale_a_zero_e_si_versa(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    righe = [riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100"), riga_a_mano(corpus, VALUTA, "credito_integrativo", "100")]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    orologio.vai(3, 10)
    t = trasmetti_delega(registro, corpus, "DELEGA-0", ADATTATORE, FEB)
    assert t.saldo == D("0") and t.residui == ()
    assert controlla(t.file) == ([], [])
    assert [r.decode("latin-1") for r in t.file.split(b"\r\n") if r][1][1872:1887].rstrip() == "0,00"
    assert registra_versamento_delega(registro, "ver-0", ADATTATORE, "DELEGA-0", date(2026, 3, 16)).tipo is TipoEsito.VERSATO


def test_il_credito_maggiore_di_tutti_i_debiti_si_trasmette_e_il_residuo_resta(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    righe = [riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100"), riga_a_mano(corpus, VALUTA, "credito_integrativo", "250")]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    t = trasmetti_delega(registro, corpus, "DELEGA-1", ADATTATORE, FEB)
    assert (t.saldo, t.totale_credito) == (D("0"), D("100"))
    assert [r.importo for r in t.residui] == [D("150")]
    assert controlla(t.file) == ([], [])


def test_il_pagamento_di_luglio_porta_il_20_agosto_nel_file(registro, corpus, orologio):
    dati_ente(registro)
    luglio = Mese(2026, 7)
    registro.registra_data_versamento(luglio, date(2026, 8, 20))
    valuta = date(2026, 7, 24)
    paga_a_mano(registro, corpus, orologio, valuta, [riga_a_mano(corpus, valuta, "ritenuta_irpef", "100")])
    orologio.vai(8, 10)
    t = trasmetti_delega(registro, corpus, "DELEGA-LUG", ADATTATORE, luglio)
    assert t.scadenza == date(2026, 8, 20) and "scadenza_per_prassi" in {a.tipo for a in t.avvisi}
    assert [r.decode("latin-1") for r in t.file.split(b"\r\n") if r][1][1887:1897] == "20-08-2026"
    assert (t.righe[0].rif_a, t.righe[0].rif_b) == ("0007", "2026")


def test_il_pagamento_di_dicembre_scade_a_gennaio_con_la_regola_del_2027(registro, corpus, orologio):
    dati_ente(registro)
    dicembre = Mese(2026, 12)
    registro.registra_data_versamento(dicembre, date(2027, 1, 18))  # il 16 gennaio 2027 è sabato
    valuta = date(2026, 12, 23)
    paga_a_mano(registro, corpus, orologio, valuta, [riga_a_mano(corpus, valuta, "ritenuta_irpef", "100")])
    d = costruisci_delega(registro, corpus, dicembre)
    assert d.scadenza.data == date(2027, 1, 18) and d.scadenza.riferimento == "fittizio:scadenza-2027"
    assert d.pronta and (d.righe[0].rif_a, d.righe[0].rif_b) == ("0012", "2026")


def test_la_vista_si_puo_rileggere_a_un_istante_passato(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    paga_a_mano(registro, corpus, orologio, VALUTA, [riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100")])
    prima = orologio()
    orologio.vai(3, 10)
    trasmetti_delega(registro, corpus, "DELEGA-1", ADATTATORE, FEB)
    assert costruisci_delega(registro, corpus, FEB).righe == ()
    assert [r.debito for r in costruisci_delega(registro, corpus, FEB, noto_al=prima).righe] == [D("100")]


def test_la_correzione_e_una_nuova_delega_dopo_lo_scarto(registro, corpus, orologio):
    """La prima delega parte con una data sbagliata ed è scartata; la nuova ha un'altra data e le stesse righe."""
    dati_ente(registro)
    registro.registra_data_versamento(FEB, date(2026, 3, 13))
    paga_a_mano(registro, corpus, orologio, VALUTA, [riga_a_mano(corpus, VALUTA, "ritenuta_irpef", "100")])
    orologio.vai(3, 10)
    prima = trasmetti_delega(registro, corpus, "DELEGA-1", ADATTATORE, FEB)
    registra_ricevuta_delega(registro, "r-1", ADATTATORE, "DELEGA-1", "controlli_formali", "negativo")
    registro.registra_data_versamento(FEB, date(2026, 3, 16))
    nuova = trasmetti_delega(registro, corpus, "DELEGA-2", ADATTATORE, FEB)
    assert (prima.data_versamento, nuova.data_versamento) == (date(2026, 3, 13), date(2026, 3, 16))
    assert nuova.righe == prima.righe and nuova.file != prima.file
    assert situazione_delega(registro, "DELEGA-1").stato is StatoDelega.SCARTATA
    assert len(registro.esiti(TipoEsito.DICHIARATO, orologio())) == 2
