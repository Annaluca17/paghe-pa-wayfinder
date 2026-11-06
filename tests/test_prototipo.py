"""Prototipo dimostrativo da buttare (ticket #37): la pagina HTML dal fatto alla ListaPosPA.

Persone e codici fiscali sono di fantasia. Gli importi attesi sono quelli ricalcolati a mano in
test_corpus_reale.py, test_fine_servizio.py e test_lista_pos_pa.py, scritti come li legge una
persona (punto per le migliaia, virgola per i decimali); nell'XML con la sola virgola.
"""

import re
import subprocess
import sys

import pytest

from paghe.prototipo import genera


@pytest.fixture(scope="module")
def pagina(tmp_path_factory):
    percorso = genera(tmp_path_factory.mktemp("prototipo"))
    return percorso.read_text(encoding="utf-8")


def sezione(pagina, nome):
    trovata = re.search(rf'<section id="{nome}".*?</section>', pagina, re.S)
    assert trovata, f"sezione {nome} assente"
    return trovata.group(0)


def test_la_pagina_e_un_file_html_autonomo(pagina):
    assert pagina.startswith("<!doctype html>")
    assert "PROTOTIPO" in pagina
    assert "<script src" not in pagina and "<link" not in pagina  # nessuna risorsa esterna


def test_mese_intero(pagina):
    s = sezione(pagina, "mese-intero")
    assert "RSSMRA80A01H501U" in s
    for atteso in ("2.019,63", "32,06", "2.051,69", "669,88", "181,57", "488,31", "7,18", "1.615,70", "98,56"):
        assert atteso in s, atteso
    assert "E0" in s
    assert "&lt;ImponibileTFS&gt;1615,70&lt;/ImponibileTFS&gt;" in s
    assert "Trasmissibile" in s


def test_assunzione_a_meta_mese_pagata_il_mese_dopo(pagina):
    s = sezione(pagina, "assunzione")
    # Agosto per competenza: 7 giorni lun-sab su 26 (nota di prassi 1).
    assert "590,16" in s and "9,78" in s
    # Settembre per cassa: agosto e settembre insieme.
    for atteso in ("2.828,29", "923,44", "250,30", "673,14", "9,90", "2.225,74", "135,77", "2.782,18", "2.192,02"):
        assert atteso in s, atteso
    assert "V1 causale 5" in s
    assert "&lt;RetribTeoricaTabellareTFR&gt;2192,02&lt;/RetribTeoricaTabellareTFR&gt;" in s


def test_arretrato_oltre_la_prima_fascia(pagina):
    s = sezione(pagina, "arretrato")
    # Settembre, ottobre e novembre pagati a novembre: (5.472,36 - 4.685) x 1% = 7,87.
    for atteso in ("5.472,36", "7,87", "1.786,73", "484,30", "1.302,43", "19,15", "4.685,00"):
        assert atteso in s, atteso
    assert "&lt;Contrib1PerCento&gt;7,87&lt;/Contrib1PerCento&gt;" in s
    # Il mese dopo il conguaglio annuo non è modellato: un caso nominato, non un errore grezzo.
    assert "Caso non modellato" in s
    assert "conguaglio annuo" in s
    assert "Traceback" not in s and "CasoNonModellato" not in s


def test_recupero_su_cessato_mostra_il_quadro_fermo(pagina):
    s = sezione(pagina, "recupero")
    # Cessazione al 15/10 comunicata dopo il pagamento di ottobre intero: si recupera la seconda metà.
    for atteso in ("-1.009,81", "-16,03", "-1.025,84", "-334,94", "-90,79", "-244,15", "-3,59"):
        assert atteso in s, atteso
    assert "su cessato" in s
    assert "Quadro fermo: V1 causale 7, codice motivo 7" in s
    assert "Non trasmissibile" in s
    assert "Annullato" in s  # i fatti errati non si cancellano: si annullano con un motivo


def test_la_spiegazione_arriva_alla_norma_e_segnala_la_prassi(pagina):
    arretrato = sezione(pagina, "arretrato")
    assert "D.L. 19/09/1992 n. 384, art. 3ter" in arretrato
    assert "Circolare INPS 30/01/2026 n. 6, § 5" in arretrato
    assert "Nota di prassi 2 del 06/11/2026" in arretrato
    assert "SOLO PRASSI" in pagina


def test_il_comando_scrive_la_pagina(tmp_path):
    esito = subprocess.run(
        [sys.executable, "-m", "paghe.prototipo", str(tmp_path / "uscita")], capture_output=True, text=True, check=False
    )
    assert esito.returncode == 0, esito.stderr
    assert (tmp_path / "uscita" / "index.html").is_file()
