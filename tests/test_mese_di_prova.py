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


def test_il_percorso_di_marzo_arriva_all_esito_versato_per_chi_non_si_ferma(esecuzione):
    arrivi = {r: a for (m, r), a in esecuzione.arrivi.items() if m == "2026-03"}
    assert [r for r, a in arrivi.items() if a == "completo"] == ["R01", "R02", "R03", "R05", "R06", "R07"]
    # R04, a tempo parziale al 60% (verticale), supera il calcolo e arriva alla ListaPosPA, ma e' una bozza (ticket #72).
    assert arrivi["R04"] == "lista_pos_pa"
    assert {arrivi[r] for r in ("R08", "R09", "R10", "R11")} == {"calcolo"}


def test_i_fermi_del_mese_nominano_il_caso_e_il_rapporto(esecuzione):
    per_causa = {g["causa"]: g for g in cause_ordinate(esecuzione)}
    assert per_causa["regime del titolo assente nel corpus"]["bloccati"] == {"R08", "R09", "R10", "R11"}
    assert "part-time, riproporzionamento non modellato" not in per_causa
    assert per_causa["bozza non trasmissibile"]["bloccati"] == {"R04", "R12"}  # ListaPosPA del part-time verticale
    # Il rimborso 730 di R07 non ferma piu' la delega di dicembre: il fermo e' il debito negativo del 100E, nominato.
    assert not [causa for causa in per_causa if "150E" in causa]
    (stop_debito,) = [g for causa, g in per_causa.items() if causa.startswith("debito_negativo")]
    assert "100E" in stop_debito["causa"] and stop_debito["bloccati"] == {"R01", "R02", "R03", "R04", "R06", "R07", "R12"}


def test_il_rimborso_730_di_r07_e_sul_netto_e_credito_nella_delega_di_dicembre(esecuzione, resoconto):
    """Un esito 730-4 vero, la dichiarazione sul netto verso il beneficiario: nessun difetto del rimborso o del debito negativo."""
    assert esecuzione.difetti == []
    assert "netto R07: 1988.79" in resoconto  # 1838.79 prima del rimborso, piu' 150.00
    assert "R07: rimborso del 730-4: 150.00, anno dei redditi dichiarati 2025" in resoconto
    assert "150E -150.00" in resoconto  # la riga a credito e' nella delega costruita, anche se non trasmissibile
    assert "esito 730-4" in resoconto and "rimborso_irpef_730" not in resoconto


def test_l_elenco_delle_cause_e_ordinato_per_rapporti_e_poi_per_passi(esecuzione):
    cause = cause_ordinate(esecuzione)
    chiavi = [(-len(g["bloccati"]), -g["passi"]) for g in cause]
    assert chiavi == sorted(chiavi)


def test_il_conteggio_dei_passaggi_distingue_avvio_e_ricorrenti(esecuzione):
    categorie = {p.categoria for p in esecuzione.passaggi}
    assert categorie == {"avvio", "ricorrente", "conferma", "scelta", "evento", "comando"}
    marzo = [p for p in esecuzione.passaggi if p.quando == "2026-03" and p.categoria == "ricorrente"]
    assert len(marzo) == 16  # performance, progressione (area e qualifica), cessazione (6 annullamenti, 6 fatti, codice)
    assert all(p.categoria != "ricorrente" for p in esecuzione.passaggi if p.quando == "avvio")


def test_i_file_prodotti_sono_validi(esecuzione, uscita):
    assert sorted(esecuzione.file_prodotti) == ["f24ep-2026-03.txt", "lista-pos-pa-2026-03.xml"]
    f24ep = (uscita / "f24ep-2026-03.txt").read_bytes()
    assert controlla(f24ep) == ([], [])
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


def test_i_titoli_senza_regime_hanno_il_rapporto_e_si_fermano_nominando_il_caso(esecuzione):
    fermi = [f for f in esecuzione.fermi if f.causa == "regime del titolo assente nel corpus" and f.mese == "2026-03"]
    assert {f.caso for f in fermi} == {"dirigente", "segretario", "sindaco", "co.co.co."}
    assert all(f.passo == "calcolo" for f in fermi)



def test_r12_a_tempo_determinato_ha_la_denuncia_individuale_di_marzo_trasmissibile(esecuzione):
    """Part-time verticale 50% in sostituzione: una settimana interamente non lavorata e una percentuale del mese intermedia."""
    vista = esecuzione.denunce_individuali[("2026-03", "R12")]
    assert vista.trasmissibile
    assert (vista.qualifica2, vista.qualifica3, vista.perc_part_time) == ("V", "A", 5000)
    assert 0 < vista.perc_part_time_mese < 10000
    assert (12, "D") in [(s.id, s.copertura) for s in vista.settimane]
    assert {r for (m, r) in esecuzione.denunce_individuali} == {"R12"}  # gli altri non sono a tempo determinato
