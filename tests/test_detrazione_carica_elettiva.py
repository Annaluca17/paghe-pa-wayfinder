"""Detrazione dell'art. 13 c. 5 per la carica elettiva e scelta della più favorevole col c. 1 (ADR 0019, ticket #97).

Codici fiscali e valori di fantasia. Le fasce del corpus reale si provano sugli estremi della norma
(`docs/research/detrazione-cariche-elettive.md`); il percorso con registro e pagamenti usa un corpus fittizio con
un c. 1 di 1200 annui ridotti fino a 40000 e un c. 5 di 900 annui fino a 20000 di reddito, per vedere la scelta in
entrambi i versi.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from paghe import Atto, Corpus, Mese, Periodo, calcola
from paghe.errori import ErroreCorpus, ErroreFormula
from paghe.fisco import AVVISO_SENZA_DICHIARAZIONE, SCELTA_ART13_C1, SCELTA_ART13_C5, _calcola
from test_fiscale import P, R, TESTO, assumi, dichiara, paga, stipendio

D = Decimal
CORPUS_REALE = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
CARICA = ("carica_elettiva",)
LAVORO = ("lavoro_dipendente",)
ENTRAMBE = ("lavoro_dipendente", "carica_elettiva")
DICHIARAZIONE = SimpleNamespace(valore="lavoro_dipendente")
C5_PROVA = "arrotonda(se(fisco.imponibile * fisco.periodi <= 20000, 900, 0) / fisco.periodi, 2)"


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS_REALE, reale=True)


def calcolo(reale, imponibile, categorie=CARICA, periodi=1, anno=2026, giorni=365, giorni_anno=365, dichiarazione=DICHIARAZIONE):
    giorno = date(anno, 6, 1)
    regola = reale.regola_ritenuta(giorno)
    return _calcola(reale, regola, D(imponibile), periodi, giorno, dichiarazione, giorni, giorni_anno, frozenset(categorie))


# Le fasce del c. 5 sul corpus reale, 2026 e 2027

@pytest.mark.parametrize("anno", [2026, 2027])
@pytest.mark.parametrize(
    ("reddito", "detrazione"),
    [
        ("5500", "1265.00"),  # lett. a): 5.500 compresi
        ("5500.01", "1264.92"),  # lett. b): 500 + 765 x 0,9999 (rapporto troncato)
        ("20000", "771.96"),  # 500 + 765 x 0,3555
        ("28000", "500.00"),  # lett. b) con 28.000 compresi: rapporto zero
        ("28000.01", "499.95"),  # lett. b-bis): 500 x 0,9999
        ("40000", "227.25"),  # 500 x 0,4545
        ("50000", "0.00"),  # 50.000 compresi, rapporto zero
        ("50000.01", "0.00"),
        ("80000", "0.00"),
    ],
)
def test_le_fasce_del_c_5(reale, anno, reddito, detrazione):
    assert calcolo(reale, reddito, anno=anno).detrazione == D(detrazione)


@pytest.mark.parametrize("anno", [2026, 2027])
@pytest.mark.parametrize(
    ("reddito", "detrazione"),
    [
        ("11000", "1077.96"),  # 11.000 escluso dall'aumento di 50
        ("11000.01", "1127.96"),
        ("17000", "923.93"),  # 17.000 compreso
        ("17000.01", "873.93"),
    ],
)
def test_l_aumento_di_50_euro_tra_11000_escluso_e_17000_compreso(reale, anno, reddito, detrazione):
    assert calcolo(reale, reddito, anno=anno).detrazione == D(detrazione)


def test_nella_ritenuta_del_mese_il_c_5_e_un_dodicesimo_per_pagamento(reale):
    # 1.000 al mese: reddito 12.000; (500 + 765 x 0,7111 + 50) / 12
    assert calcolo(reale, "1000", periodi=12, giorni=1, giorni_anno=1).detrazione == D("91.17")


@pytest.mark.parametrize("anno", [2026, 2027])
def test_la_sola_carica_elettiva_riceve_il_c_5_e_non_il_c_1(reale, anno):
    assert calcolo(reale, "20000", CARICA, anno=anno).detrazione == D("771.96")
    assert calcolo(reale, "20000", LAVORO, anno=anno).detrazione == D("2642.21")  # c. 1: 1.910 + 1.190 x 0,6153


@pytest.mark.parametrize("categoria", ["lavoro_dipendente", "collaborazione"])
def test_il_c_1_resta_a_lavoro_dipendente_e_collaborazione(reale, categoria):
    assert calcolo(reale, "9000", (categoria,)).detrazione == D("1955.00")


def test_la_carica_elettiva_non_ha_l_ulteriore_detrazione_ne_il_c_1(reale):
    c = calcolo(reale, "9000", CARICA)
    assert (c.detrazione, c.detrazione_automatica) == (D("1145.97"), D("0"))


def test_senza_dichiarazione_nessuna_detrazione_del_c_5(reale):
    assert calcolo(reale, "9000", CARICA, dichiarazione=None).detrazione == D("0")


# Con entrambi i redditi: la più alta, o la scelta della dichiarazione

def test_con_entrambi_i_redditi_vince_la_piu_alta_nei_due_versi(reale):
    # R 9.000: c. 1 = 1.955, c. 5 = 1.145,97
    primo = calcolo(reale, "9000", ENTRAMBE)
    assert primo.detrazione == D("1955.00")
    # il c. 1 rapportato a 30 giorni sale solo al minimo di 690: vince il c. 5, intero
    secondo = calcolo(reale, "9000", ENTRAMBE, giorni=30)
    assert secondo.detrazione == D("1145.97")


def test_la_scelta_scritta_nella_dichiarazione_prevale(reale):
    c1 = calcolo(reale, "9000", ENTRAMBE, giorni=30, dichiarazione=SimpleNamespace(valore=SCELTA_ART13_C1))
    c5 = calcolo(reale, "9000", ENTRAMBE, dichiarazione=SimpleNamespace(valore=SCELTA_ART13_C5))
    assert (c1.detrazione, c5.detrazione) == (D("690.00"), D("1145.97"))


def test_la_scelta_di_una_categoria_assente_non_si_applica(reale):
    solo_lavoro = calcolo(reale, "9000", LAVORO, dichiarazione=SimpleNamespace(valore=SCELTA_ART13_C5))
    solo_carica = calcolo(reale, "9000", CARICA, dichiarazione=SimpleNamespace(valore=SCELTA_ART13_C1))
    assert (solo_lavoro.detrazione, solo_carica.detrazione) == (D("1955.00"), D("1145.97"))



# Conguaglio con servizio parziale: il c. 5 è intero, il c. 1 è rapportato

def test_al_conguaglio_il_c_5_non_e_rapportato_ai_giorni_e_il_c_1_si(reale):
    parziale = 184
    c1 = calcolo(reale, "9000", LAVORO, giorni=parziale)
    c5 = calcolo(reale, "9000", CARICA, giorni=parziale)
    assert c1.detrazione == D("985.53")  # 1.955 x 184 / 365
    assert c5.detrazione == D("1145.97")  # intero


# Corpus fittizio: registro, pagamenti, spiegazione

def con_c5(testo=TESTO):
    marca = 'categorie = ["lavoro_dipendente"]\n'
    assert testo.count(marca) == 1
    return Corpus.da_toml(
        testo.replace(
            marca,
            'categorie = ["lavoro_dipendente", "carica_elettiva"]\n'
            'categorie_detrazione = ["lavoro_dipendente"]\n'
            'categorie_detrazione_carica_elettiva = ["carica_elettiva"]\n'
            f"detrazione_carica_elettiva = '''{C5_PROVA}'''\n",
        )
    )


@pytest.fixture
def prova():
    return con_c5()


def paga_mese(registro, orologio, corpus, stipendio_mese=None, gettone=None):
    mese = Mese(2026, 3)
    orologio.vai(3, 1)
    if stipendio_mese:
        registro.registra_fatto(R, "mensile", stipendio_mese, mese.primo_giorno, mese.ultimo_giorno)
    if gettone:
        registro.registra_fatto(R, "gettone", gettone, mese.primo_giorno, mese.ultimo_giorno)
    righe = calcola(registro, corpus, R, mese)
    return paga(registro, orologio, corpus, righe, date(2026, 3, 27))[1]


def test_la_regola_legge_i_campi_del_c_5(prova):
    regola = prova.regola_ritenuta(date(2026, 6, 1))
    assert regola.categorie_detrazione == ("lavoro_dipendente",)
    assert regola.categorie_detrazione_carica_elettiva == ("carica_elettiva",)
    assert regola.detrazione_carica_elettiva == C5_PROVA


def test_senza_i_campi_nuovi_la_regola_resta_come_prima():
    regola = Corpus.da_toml(TESTO).regola_ritenuta(date(2026, 6, 1))
    assert (regola.categorie_detrazione, regola.categorie_detrazione_carica_elettiva) == ((), ())
    assert regola.detrazione_carica_elettiva == "0"


def test_i_campi_nuovi_cambiano_l_impronta_del_corpus(prova):
    assert prova.versione != Corpus.da_toml(TESTO).versione


@pytest.mark.parametrize("formula", ["fatto.x", "importo.x", "base.x", "fisco.sconosciuto", "parametro.inesistente"])
def test_la_detrazione_del_c_5_ha_gli_stessi_controlli_delle_altre_formule(formula):
    marca = 'categorie = ["lavoro_dipendente"]\n'
    testo = TESTO.replace(marca, marca + f"detrazione_carica_elettiva = '''{formula}'''\n")
    with pytest.raises((ErroreCorpus, ErroreFormula)):
        Corpus.da_toml(testo)


def test_la_sola_carica_senza_dichiarazione_non_ha_detrazione_e_c_e_l_avviso(registro, orologio, prova):
    assumi(registro)
    fiscale = paga_mese(registro, orologio, prova, gettone="1500")
    assert fiscale.ritenuta.valore == D("216.67")
    assert any(avviso.tipo == AVVISO_SENZA_DICHIARAZIONE for avviso in fiscale.avvisi)


def test_la_sola_carica_con_dichiarazione_riceve_il_c_5_e_la_spiegazione_lo_dice(registro, orologio, prova):
    assumi(registro)
    dichiara(registro, orologio)
    fiscale = paga_mese(registro, orologio, prova, gettone="1500")
    assert fiscale.ritenuta.valore == D("216.67") - D("75.00")  # 900 / 12, non i 55,00 del c. 1
    formula = fiscale.ritenuta.derivazione.formula
    assert "art. 13 c. 5" in formula and "unica detrazione" in formula


def test_con_entrambi_i_redditi_vince_il_c_5_quando_e_piu_alta(registro, orologio, prova):
    assumi(registro)
    dichiara(registro, orologio)
    # 1.500 al mese: c. 1 = 55,00, c. 5 = 75,00
    fiscale = paga_mese(registro, orologio, prova, stipendio_mese="1000", gettone="500")
    assert fiscale.ritenuta.valore == D("216.67") - D("75.00")
    formula = fiscale.ritenuta.derivazione.formula
    assert "art. 13 c. 5" in formula and "più favorevole" in formula


def test_con_entrambi_i_redditi_vince_il_c_1_quando_e_piu_alta(registro, orologio, prova):
    assumi(registro)
    dichiara(registro, orologio)
    # 2.500 al mese: reddito 30.000, c. 5 = 0, c. 1 = 300 / 12 = 25,00
    fiscale = paga_mese(registro, orologio, prova, stipendio_mese="1500", gettone="1000")
    assert "art. 13 c. 1" in fiscale.ritenuta.derivazione.formula
    assert "più favorevole" in fiscale.ritenuta.derivazione.formula
    assert fiscale.ritenuta.valore == D("416.67") - D("25.00")


def test_la_scelta_del_c_1_nella_dichiarazione_prevale_sul_piu_favorevole(registro, orologio, prova):
    assumi(registro)
    registro.registra_dichiarazione_sostituito(
        P, SCELTA_ART13_C1, date(2026, 1, 1), None, _atto()
    )
    fiscale = paga_mese(registro, orologio, prova, stipendio_mese="1000", gettone="500")
    assert fiscale.ritenuta.valore == D("216.67") - D("55.00")
    formula = fiscale.ritenuta.derivazione.formula
    assert "art. 13 c. 1" in formula and "scelta" in formula


def test_una_dichiarazione_con_un_valore_ignoto_non_da_detrazione(registro, orologio, prova):
    assumi(registro)
    registro.registra_dichiarazione_sostituito(P, "altro", date(2026, 1, 1), None, _atto())
    fiscale = paga_mese(registro, orologio, prova, gettone="1500")
    assert fiscale.ritenuta.valore == D("216.67")
    assert any(avviso.tipo == AVVISO_SENZA_DICHIARAZIONE for avviso in fiscale.avvisi)


def test_la_scelta_del_c_5_nella_dichiarazione_prevale_sul_piu_favorevole(registro, orologio):
    corpus = con_c5()
    assumi(registro)
    registro.registra_dichiarazione_sostituito(P, SCELTA_ART13_C5, date(2026, 1, 1), None, _atto())
    # senza carica elettiva la scelta del c. 5 non si applica: resta il c. 1
    fiscale = paga_mese(registro, orologio, corpus, stipendio_mese="1500")
    assert fiscale.ritenuta.valore == D("216.67") - D("55.00")
    assert not any(avviso.tipo == AVVISO_SENZA_DICHIARAZIONE for avviso in fiscale.avvisi)


def _atto():
    return Atto("ente:c_x000:modulo:2026-01-10;1", date(2026, 1, 10))


# Corpus reale

@pytest.mark.parametrize(("anno", "versione"), [(2026, 1), (2027, 2)])
def test_il_corpus_reale_ha_il_c_5_in_tutte_e_due_le_versioni(reale, anno, versione):
    regola = reale.regola_ritenuta(date(anno, 6, 1))
    assert regola.versione == versione
    assert regola.categorie_detrazione == ("lavoro_dipendente", "collaborazione")
    assert regola.categorie_detrazione_carica_elettiva == ("carica_elettiva",)
    nomi = {nome for nome in regola.parametri if nome.startswith("art13_c5_")}
    assert len(nomi) == 12
    for nome in nomi:
        vigenza = reale.parametro(nome).vigenza_per(Periodo(date(anno, 6, 1), date(anno, 6, 1)))
        assert vigenza.riferimento.startswith("urn:nir:stato:")
        assert "art13-com5" in vigenza.riferimento or "art13-com7" in vigenza.riferimento
