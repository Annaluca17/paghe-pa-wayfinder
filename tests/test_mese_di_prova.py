"""Il mese di prova (ticket #68): un mese intero di un ente fittizio, dai fatti ai file.

Il test fa girare il percorso e confronta il resoconto con quello fissato in `prove/mese_di_prova/resoconto-atteso.md`:
quando un ticket sposta piu' avanti il punto in cui il mese si ferma, il resoconto cambia e il test lo mostra.
Dopo un cambio voluto: `python -m prove.mese_di_prova --aggiorna-atteso` e il diff del file dice cosa si e' sbloccato.
Dati esclusivamente fittizi.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from paghe import Corpus
from paghe.errori import ErroreCorpus

from controlli_f24ep import controlla
from prove.mese_di_prova import scenario as S
from prove.mese_di_prova.codici import carattere_di_controllo, codice_fiscale
from prove.mese_di_prova.percorso import CORPUS_FITTIZIO, CORPUS_REALE, RADICE, esegui
from prove.mese_di_prova.resoconto import cause_ordinate, scrivi

ATTESO = RADICE / "prove" / "mese_di_prova" / "resoconto-atteso.md"



@pytest.fixture(scope="module")
def uscita(tmp_path_factory):
    return tmp_path_factory.mktemp("uscita")


@pytest.fixture(scope="module")
def esecuzione(uscita):
    return esegui(uscita)


@pytest.fixture(scope="module")
def resoconto(esecuzione):
    return scrivi(esecuzione)


def test_il_resoconto_e_quello_atteso(resoconto):
    atteso = ATTESO.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert resoconto == atteso, (
        "Il resoconto del mese di prova e' cambiato. Se e' voluto: python -m prove.mese_di_prova --aggiorna-atteso, "
        "e il diff di prove/mese_di_prova/resoconto-atteso.md dice cosa si e' sbloccato."
    )


def test_il_resoconto_e_deterministico(resoconto):
    """Nessun istante reale, nessun percorso assoluto, nessun separatore di Windows."""
    assert str(RADICE) not in resoconto
    assert not re.search(r"\b\d{2}:\d{2}(:\d{2})?\b", resoconto)
    assert not re.search(r"[A-Za-z]:\\|/Users/|/home/", resoconto)
    assert "tmp" not in resoconto.lower()


def test_il_percorso_di_marzo(esecuzione, uscita):
    arrivi = {r: a for (m, r), a in esecuzione.arrivi.items() if m == "2026-03"}
    # La causale della gestione separata e' ASSUNTA nel corpus fittizio (ZGS1, di fantasia: C10 o CXX da verificare), cosi' la
    # delega con le righe di R10 e R11 non ferma tutto il mese (ticket #73).
    assert [r for r, a in arrivi.items() if a == "completo"] == ["R01", "R02", "R03", "R05", "R06", "R07"]
    assert not [r for r, a in arrivi.items() if a == "delega"]
    # R04, a tempo parziale al 60% (verticale), supera il calcolo e arriva alla ListaPosPA, ma e' una bozza (ticket #72).
    assert arrivi["R04"] == "lista_pos_pa"
    # Dirigente e segretario (ticket #73) superano calcolo, denuncia e pagamento: alla ListaPosPA mancano contratto e qualifica,
    # di cui non si inventano i codici.
    assert {arrivi[r] for r in ("R08", "R09")} == {"lista_pos_pa"}
    # Sindaco e co.co.co. (ticket #73) arrivano alla lista collaboratori, una bozza: i codici del tracciato non sono dichiarati.
    assert {arrivi[r] for r in ("R10", "R11")} == {"lista_collaboratori"}
    f24ep = (uscita / "f24ep-2026-03.txt").read_bytes()
    assert controlla(f24ep) == ([], [])
    assert b"ZGS1" in f24ep


def test_i_fermi_del_mese_nominano_il_caso_e_il_rapporto(esecuzione):
    per_causa = {g["causa"]: g for g in cause_ordinate(esecuzione)}
    assert not [causa for causa in per_causa if "regime del titolo" in causa]  # ogni titolo ha il suo regime nel corpus
    (tracciato,) = [g for causa, g in per_causa.items() if causa.startswith("tracciato della lista collaboratori")]
    assert tracciato["bloccati"] == {"R10", "R11"}  # codici del tracciato non letti: bozza, non inventati
    (attestazione,) = [g for causa, g in per_causa.items() if "attestazione_prestazione" in causa]
    assert attestazione["bloccati"] == {"R11"}  # la rata di dicembre non e' attestata: calcolata, ma fuori dalla versione
    assert not [causa for causa in per_causa if causa.startswith("mappatura_mancante")]
    for dato in ("contratto", "qualifica"):
        assert per_causa[f"dato mancante {dato}"]["bloccati"] == {"R08", "R09"}  # codici del tracciato non letti
    assert "part-time, riproporzionamento non modellato" not in per_causa
    assert per_causa["bozza non trasmissibile"]["bloccati"] == {"R04", "R12"}  # ListaPosPA del part-time verticale
    # Con il fisco reale (ticket #93) i conguagli a credito non superano piu' le ritenute della delega: niente debito negativo.
    assert not [causa for causa in per_causa if "150E" in causa or causa.startswith("debito_negativo")]


def test_il_rimborso_730_di_r07_e_sul_netto_e_credito_nella_delega_di_dicembre(esecuzione, resoconto):
    """Un esito 730-4 vero, la dichiarazione sul netto verso il beneficiario: nessun difetto del rimborso o del debito negativo."""
    assert esecuzione.difetti == []
    assert "netto R07: 2102.50" in resoconto  # 1952.50 prima del rimborso, piu' 150.00
    assert "R07: rimborso del 730-4: 150.00, anno dei redditi dichiarati 2025" in resoconto
    assert "riga F 150E: debito 0.00, credito 150.00" in resoconto  # la riga a credito e' nella delega trasmessa
    assert "esito 730-4" in resoconto and "rimborso_irpef_730" not in resoconto


def test_l_elenco_delle_cause_e_ordinato_per_rapporti_e_poi_per_passi(esecuzione):
    cause = cause_ordinate(esecuzione)
    chiavi = [(-len(g["bloccati"]), -g["passi"]) for g in cause]
    assert chiavi == sorted(chiavi)


def test_il_conteggio_dei_passaggi_distingue_avvio_e_ricorrenti(esecuzione):
    categorie = {p.categoria for p in esecuzione.passaggi}
    assert categorie == {"avvio", "ricorrente", "conferma", "scelta", "evento", "comando"}
    marzo = [p for p in esecuzione.passaggi if p.quando == "2026-03" and p.categoria == "ricorrente"]
    assert len(marzo) == 17  # performance, progressione (area e qualifica), cessazione (6 annullamenti, 6 fatti, codice), attestazione di R11
    assert all(p.categoria != "ricorrente" for p in esecuzione.passaggi if p.quando == "avvio")


def test_i_file_prodotti_sono_validi(esecuzione, uscita):
    assert sorted(esecuzione.file_prodotti) == ["f24ep-2026-03.txt", "f24ep-2026-12.txt", "lista-pos-pa-2026-03.xml"]
    radice = ET.parse(uscita / "lista-pos-pa-2026-03.xml").getroot()
    assert radice.tag == "DenunceMensili"
    assert len(radice.findall(".//D0_DenunciaIndividuale")) == 6


# Scenario e corpus fittizio

def test_i_codici_fiscali_hanno_il_carattere_di_controllo_valido():
    assert carattere_di_controllo("RSSMRA80A01H501") == "U"  # il codice di prova dei test esistenti
    assert codice_fiscale("ROSSI", "MARIO", 1980, 1, 1) == "RSSMRA80A01H501U"
    codici = [r.cf for r in S.RAPPORTI]
    assert len(set(codici)) == len(codici)
    for cf in codici:
        assert re.fullmatch(r"[A-Z]{6}\d{2}[A-EHLMPR-T]\d{2}[A-Z]\d{3}[A-Z]", cf)
        assert cf[15] == carattere_di_controllo(cf[:15])


def test_l_ente_e_i_dati_dello_scenario_sono_di_fantasia():
    assert S.IBAN_TESORERIA.startswith("IT76X0100003245TEST")
    assert S.IBAN_PERSONE.startswith("IT76X0100003245TEST")
    assert "PROVA" in S.DENOMINAZIONE_ENTE
    assert {r.cognome for r in S.RAPPORTI} == {"PROVA"}


def test_l_aggiunta_fittizia_ha_solo_riferimenti_fittizi():
    testo = CORPUS_FITTIZIO.read_text(encoding="utf-8")
    riferimenti = re.findall(r'^riferimento = "([^"]+)"', testo, flags=re.MULTILINE)
    assert len(riferimenti) > 60
    assert all(r.startswith("fittizio:") for r in riferimenti)


def test_il_corpus_reale_resta_reale_e_l_unione_non_lo_e():
    reale = CORPUS_REALE.read_text(encoding="utf-8")
    fittizio = CORPUS_FITTIZIO.read_text(encoding="utf-8")
    assert Corpus.da_toml(reale, reale=True).reale
    assert "fittizio:" not in reale
    unione = Corpus.da_toml(reale + "\n" + fittizio)
    assert not unione.reale
    with pytest.raises(ErroreCorpus, match="fittizio"):
        Corpus.da_toml(reale + "\n" + fittizio, reale=True)


def test_il_resoconto_dichiara_in_testa_il_corpus_non_reale(resoconto):
    testa = resoconto.split("## Corpus")[0]
    assert "non reale" in testa and "fittizio:" in testa and "ADR 0003" in testa


def test_sindaco_e_cococo_superano_calcolo_versione_e_pagamento_di_marzo(esecuzione):
    passi = {(p.mese, p.nome): p for p in esecuzione.passi}
    calcolo = passi[("2026-03", "calcolo")].riuscito
    assert "R10: 2 importi, lordo 3000.00" in calcolo  # indennita' di funzione e quota dell'art. 86 (a carico dell'ente: fuori dal lordo)
    assert "R11: 1 importi, lordo 1500.00" in calcolo  # la rata attestata del piano
    versione = passi[("2026-03", "versione")].riuscito
    assert any(riga.startswith("netto R10: ") for riga in versione) and any(riga.startswith("netto R11: ") for riga in versione)
    assert not [f for f in passi[("2026-03", "calcolo")].fermi if f.rapporti in (("R10",), ("R11",))]


def test_la_rata_di_dicembre_non_attestata_resta_calcolata_ma_fuori_dalla_versione(esecuzione):
    passi = {(p.mese, p.nome): p for p in esecuzione.passi}
    assert "R11: 1 importi, lordo 1500.00" in passi[("2026-12", "calcolo")].riuscito
    assert esecuzione.arrivi[("2026-12", "R11")] == "versione"
    assert any("escluso compenso_collaborazione di R11" in nota for nota in passi[("2026-12", "versione")].note)
    assert esecuzione.arrivi[("2026-12", "R10")] == "completo"  # l'indennita' e la quota arrivano alla delega e al versamento


def test_la_lista_collaboratori_prende_solo_il_sindaco_e_il_cococo_e_la_listapospa_solo_i_dipendenti(esecuzione):
    note = {(p.mese, p.nome): p.note for p in esecuzione.passi}
    assert "rapporti che il regime assegna alla lista collaboratori: R10, R11" in note[("2026-03", "lista_collaboratori")]
    (assegnati,) = [n for n in note[("2026-03", "lista_pos_pa")] if n.startswith("rapporti che il regime assegna alla ListaPosPA")]
    assert "R10" not in assegnati and "R11" not in assegnati and "R01" in assegnati


def test_r12_a_tempo_determinato_ha_la_denuncia_individuale_di_marzo_trasmissibile(esecuzione):
    """Part-time verticale 50% in sostituzione: una settimana interamente non lavorata e una percentuale del mese intermedia."""
    vista = esecuzione.denunce_individuali[("2026-03", "R12")]
    assert vista.trasmissibile
    assert (vista.qualifica2, vista.qualifica3, vista.perc_part_time) == ("V", "A", 5000)
    assert 0 < vista.perc_part_time_mese < 10000
    assert (12, "D") in [(s.id, s.copertura) for s in vista.settimane]
    assert {r for (m, r) in esecuzione.denunce_individuali} == {"R12"}  # gli altri non sono a tempo determinato
