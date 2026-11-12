"""Il confronto col gestionale (prove/confronto) su file e cedolini fittizi: nessun dato reale.

Il PDF dei cedolini non e' coperto: servirebbe costruirne uno con pdfplumber e le sue coordinate.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese
from prove.confronto import irpef
from prove.confronto.calcolo import gira, motivo_di_esclusione
from prove.confronto.lettura import (
    Anagrafica, Cedolino, RigaCedolino, leggi_anagrafiche, leggi_imponibili_irpef, leggi_scritture_f24,
)

D = Decimal
CF_FITTIZIO = "RSSMRA80A01H501U"
MESE = Mese(2026, 10)
VALUTA = date(2026, 10, 27)


def _html(testata, righe) -> str:
    celle = lambda tag, valori: "<tr>" + "".join(f"<{tag}>{v}</{tag}>" for v in valori) + "</tr>"
    return "<html><body><table>" + celle("th", testata) + "".join(celle("td", r) for r in righe) + "</table></body></html>"


def _xls(percorso, testata, righe):
    percorso.write_text(_html(testata, righe), encoding="latin-1")
    return percorso


TESTATA_ANAGRAFICA = ["ente", "matr.", "assunto il", "cessato il", "nato il", "tipo p.t.", "% p.t.", "detr.lav.dip.", "tab.ritenute", "retr.anno-1"]


def _anagrafica(**campi) -> Anagrafica:
    base = {"assunto il": "01-03-2015", "cessato il": "", "nato il": "01-01-1980", "tipo p.t.": "", "% p.t.": "", "detr.lav.dip.": "Si", "tab.ritenute": "1", "retr.anno-1": "30000,00"}
    return Anagrafica("1", 1001, {**base, **campi})


def _cedolino(giorni="26.00", area="FUN") -> Cedolino:
    c = Cedolino(ente="1", matricola=1001, nominativo="ROSSI MARIO", codice_fiscale=CF_FITTIZIO, area=area, rapporto="TI")
    c.fisse = {"STIPENDIO BASE": D("2192.02")}
    c.righe = [RigaCedolino("304", "RETRIBUZIONE", giorni=D(giorni), competenza=D("2192.02"))]
    c.imponibile_irpef = D("2000.00")
    c.imposta_lorda = D("460.00")
    c.detrazioni_dettaglio = {"altre": D("100.00")}
    c.netto = D("1600.00")
    c.totale_competenze = D("2192.02")
    return c


# Lettura

def test_leggi_anagrafiche_trascrive_le_colonne(tmp_path):
    percorso = _xls(tmp_path / "anagrafe.xls", TESTATA_ANAGRAFICA + [""], [
        ["1", "1001", "01-03-2015", "", "01-01-1980", "", "", "Si", "1", "30000,00", "Tabella"],
        ["1", "1002", "01-09-2020", "31-10-2026", "15-05-1975", "O", "50", "Nessuna", "2", "0,00", ""],
        ["totale", "", "", "", "", "", "", "", "", "", ""],  # riga senza matricola: scartata
    ])
    prima, seconda = leggi_anagrafiche(percorso)
    assert (prima.ente, prima.matricola, prima.assunzione, prima.nascita, prima.cessazione) == ("1", 1001, date(2015, 3, 1), date(1980, 1, 1), None)
    assert seconda.cessazione == date(2026, 10, 31) and seconda["tipo p.t."] == "O" and seconda["% p.t."] == "50"
    assert prima["colonna_10"] == "Tabella"  # la colonna senza titolo e' nominata per posizione


def test_leggi_scritture_f24_salta_il_totale(tmp_path):
    percorso = tmp_path / "f24.csv"
    percorso.write_text(
        "ente;matr.;cod.;voce;c.ente;importo;trib.F24EP;rif.B\n"
        "1;1001;8118;CPDEL;X;123,45;S1;B1\n"
        "1;1001;8118;CPDEL;;50,00;S1;B1\n"
        "1;0;;TOTALE;;173,45;;\n",
        encoding="latin-1",
    )
    a_carico, a_carico_lavoratore = leggi_scritture_f24(percorso)
    assert (a_carico.matricola, a_carico.a_carico_ente, a_carico.importo) == (1001, True, D("123.45"))
    assert not a_carico_lavoratore.a_carico_ente


def _estrazione(tmp_path, righe):
    return _xls(tmp_path / "voci.xls", ["Matr.", "Anno", "Mese", "Voce", "Importo"], righe)


def test_leggi_imponibili_irpef_somma_la_voce_9001_dell_anno(tmp_path):
    percorso = _estrazione(tmp_path, [
        ["1001", "2026", "1", "9001-IMPONIBILE", "2.000,00"],
        ["1001", "2026", "1", "9001-ARRETRATI", "100,50"],  # stesso mese: si somma
        ["1001", "2026", "2", "9001", "2.000,00"],
        ["1001", "2026", "2", "9002", "999,00"],  # altra voce
        ["1001", "2025", "12", "9001", "1.500,00"],  # altro anno
        ["xx", "2026", "3", "9001", "1,00"],  # matricola non numerica
    ])
    assert leggi_imponibili_irpef(percorso, 2026) == {1001: {1: D("2100.50"), 2: D("2000.00")}}


# Esclusioni dal primo giro

def test_motivo_di_esclusione():
    assert motivo_di_esclusione(_cedolino(), _anagrafica(), MESE) == ""
    assert "segretario" in motivo_di_esclusione(_cedolino(area="SEG"), _anagrafica(), MESE)
    assert "cessazione" in motivo_di_esclusione(_cedolino(), _anagrafica(**{"cessato il": "31-10-2026"}), MESE)
    assert motivo_di_esclusione(_cedolino(), _anagrafica(**{"cessato il": "30-09-2026"}), MESE) == ""  # cessato prima del mese
    assert "part-time" in motivo_di_esclusione(_cedolino(), _anagrafica(**{"tipo p.t.": "O", "% p.t.": "50"}), MESE)
    assert "26" in motivo_di_esclusione(_cedolino(giorni="13.00"), _anagrafica(), MESE)


# Il giro sul nucleo

def _giro(pregressi=None):
    c = _cedolino()
    return gira([c], {c.matricola: _anagrafica()}, MESE, VALUTA, "gestionale", pregressi)


def test_gira_senza_pregressi_calcola_il_mese_isolato():
    giro = _giro()
    assert giro.esclusi == {} and set(giro.calcolati) == {1001}
    risultato = giro.calcolati[1001]
    assert risultato.fermo == ""
    assert risultato.netto is not None and risultato.valore("ritenuta_irpef") is not None
    assert giro.tabellari["funzionari"][1] == D("2192.02") * 12  # tabellare dei cedolini al posto di quello del corpus
    assert risultato.reddito_annuo() is not None


def test_gira_con_pregressi_il_reddito_annuo_include_il_pagato_prima():
    senza = _giro().calcolati[1001].reddito_annuo()
    pregressi = {1001: {m: D("2000.00") for m in range(1, 10)}}  # gennaio-settembre
    con = _giro(pregressi).calcolati[1001]
    assert con.fermo == ""
    # nove mesi pagati da 2.000 piu' ottobre e i due mesi che restano: il reddito non e' piu' il solo mese per 12
    assert con.reddito_annuo() is not None and con.reddito_annuo() != senza
    assert con.reddito_annuo() >= D("18000.00") + con.imponibile_fiscale()


def test_gira_esclude_chi_non_e_nel_primo_giro():
    c = _cedolino(giorni="13.00")
    giro = gira([c], {c.matricola: _anagrafica()}, MESE, VALUTA, "gestionale")
    assert 1001 in giro.esclusi and giro.calcolati == {}


# Scomposizione dell'IRPEF

def test_scomponi_ricostruisce_la_ritenuta_del_nucleo():
    c = _cedolino()
    giro = _giro()
    calcolato = giro.calcolati[1001]
    scomposta = irpef.scomponi(irpef.parametri(VALUTA), c, calcolato, _anagrafica(), 31)
    assert scomposta is not None and scomposta.matricola == 1001
    assert scomposta.ritenuta_prototipo == calcolato.valore("ritenuta_irpef")
    assert scomposta.quadra  # lorda - lavoro - ulteriore = ritenuta, al centesimo
    assert scomposta.reddito_prototipo == calcolato.reddito_annuo()
    assert scomposta.reddito_gestionale is not None  # la detrazione di lavoro del cedolino fissa un reddito annuo


def test_scomponi_senza_ritenuta_non_scompone():
    c = _cedolino()
    calcolato = _giro().calcolati[1001]
    calcolato.righe = [r for r in calcolato.righe if r.istituto != "ritenuta_irpef"]
    assert irpef.scomponi(irpef.parametri(VALUTA), c, calcolato, _anagrafica(), 31) is None
