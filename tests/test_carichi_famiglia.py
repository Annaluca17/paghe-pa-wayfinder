"""Carichi di famiglia: un fatto per familiare, detrazione a mese (ADR 0033, ticket #98). Dati di fantasia.

Codici fiscali di fantasia con carattere di controllo valido. Le formule del corpus reale si provano sui valori
della ricerca (`docs/research/carichi-di-famiglia.md`, tema 1); il percorso con registro e pagamenti usa un
corpus fittizio con formule semplici per i carichi, per vedere i mesi, l'età e il numero dei figli.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Atto, Corpus, Mese
from paghe.errori import ErroreCorpus, ErroreFormula, ErroreRegistro
from paghe.fisco import _calcola, _CaricoMese, _Voce
from paghe.registro import leggi_familiare
from test_fiscale import P, R, TESTO, assumi, dichiara, paga, stipendio

D = Decimal
CF_CONIUGE = "RSSLRA09B41H501N"
CF_FIGLIO = "RSSGNN05C10H501G"
CF_FIGLIO_2 = "RSSMRA10D41H501L"
CF_ASCENDENTE = "RSSPLA45E50H501C"
CF_ALTRO = "RSSLCU95H01H501H"
ATTO = Atto("ente:c_x000:modulo:2026-01-10;2", date(2026, 1, 10))
CORPUS_REALE = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"


def figlio(registro, persona=P, cf=CF_FIGLIO, nascita=date(2004, 8, 15), percentuale=100, dal=date(2026, 1, 1), al=None):
    return registro.registra_familiare_a_carico(persona, "figlio", cf, nascita, percentuale, dal, al, ATTO)


# Registro: un fatto per familiare

def test_il_familiare_si_registra_con_atto_e_codice_fiscale_valido(registro):
    fatto = figlio(registro)
    assert fatto.tipo == "familiare_a_carico"
    assert fatto.atto == ATTO
    assert registro.familiari_a_carico_del_mese(P, 2026, 3, registro.adesso()) == [fatto]
    familiare = leggi_familiare(fatto)
    assert (familiare.relazione, familiare.codice_fiscale, familiare.data_nascita, familiare.percentuale) == (
        "figlio", CF_FIGLIO, date(2004, 8, 15), 100
    )


def test_il_registro_rifiuta_il_familiare_senza_atto(registro):
    with pytest.raises(ErroreRegistro, match="documento di origine"):
        registro.registra_familiare_a_carico(P, "figlio", CF_FIGLIO, date(2004, 8, 15), 100, date(2026, 1, 1), None, None)


@pytest.mark.parametrize(
    "codice",
    ["RSSGNN05C10H501X", "RSSGNN05C10H501", "rssgnn05c10h501g", "RSSGNN05C10H501GG", "", "RSSGNN05C10H5@1G", None],
)
def test_il_registro_rifiuta_un_codice_fiscale_non_valido(registro, codice):
    with pytest.raises(ErroreRegistro, match="codice fiscale"):
        figlio(registro, cf=codice)


@pytest.mark.parametrize(
    ("relazione", "percentuale"),
    [
        ("nipote", 100),
        ("figlio", 30),
        ("figlio", 0),
        ("figlio_disabile", 75),
        ("coniuge", 50),
        ("figlio_in_luogo_del_coniuge", 50),
        ("ascendente", 0),
        ("ascendente", 101),
        ("ascendente", 33.5),
        ("figlio", True),
    ],
)
def test_il_registro_rifiuta_relazione_o_percentuale_non_ammesse(registro, relazione, percentuale):
    with pytest.raises(ErroreRegistro):
        registro.registra_familiare_a_carico(
            P, relazione, CF_FIGLIO, date(2004, 8, 15), percentuale, date(2026, 1, 1), None, ATTO
        )


@pytest.mark.parametrize(
    ("relazione", "percentuale"),
    [("coniuge", 100), ("figlio", 50), ("figlio_disabile", 100), ("figlio_in_luogo_del_coniuge", 100), ("ascendente", 25)],
)
def test_il_registro_accetta_le_combinazioni_ammesse(registro, relazione, percentuale):
    registro.registra_familiare_a_carico(P, relazione, CF_FIGLIO, date(2004, 8, 15), percentuale, date(2026, 1, 1), None, ATTO)


def test_la_validita_invertita_e_rifiutata(registro):
    with pytest.raises(ErroreRegistro):
        figlio(registro, dal=date(2026, 6, 1), al=date(2026, 5, 31))


def test_una_variazione_sostituisce_il_precedente_per_quel_familiare_e_non_gli_altri(registro):
    vecchio = figlio(registro, percentuale=100)
    altro = figlio(registro, cf=CF_FIGLIO_2, nascita=date(2005, 1, 5), percentuale=100)
    nuovo = figlio(registro, percentuale=50, dal=date(2026, 4, 1))
    marzo = {f.id for f in registro.familiari_a_carico_del_mese(P, 2026, 3, registro.adesso())}
    aprile = {f.id for f in registro.familiari_a_carico_del_mese(P, 2026, 4, registro.adesso())}
    assert marzo == {vecchio.id, altro.id}
    assert aprile == {nuovo.id, altro.id}


def test_un_mese_conta_se_il_fatto_copre_anche_un_solo_giorno(registro):
    figlio(registro, dal=date(2026, 3, 31), al=date(2026, 5, 1))
    mesi = [len(registro.familiari_a_carico_del_mese(P, 2026, m, registro.adesso())) for m in range(1, 7)]
    assert mesi == [0, 0, 1, 1, 1, 0]


def test_i_familiari_sono_per_persona(registro):
    figlio(registro, persona=P)
    assert registro.familiari_a_carico_del_mese("PERSONA-2", 2026, 3, registro.adesso()) == []


# Corpus: le formule dei carichi nella regola di ritenuta

CARICHI_PROVA = (
    "carichi_coniuge = '''720'''\n"
    "carichi_figlio = '''600 * fisco.figli'''\n"  # con due figli, 1200 ciascuno: si vede il conteggio del mese
    "carichi_ascendente = '''480'''\n"
)
MARCA = 'detrazione_richiesta = "lavoro_dipendente"\n'


def con_carichi(righe=CARICHI_PROVA):
    assert MARCA in TESTO
    return Corpus.da_toml(TESTO.replace(MARCA, MARCA + righe))


@pytest.fixture
def prova():
    return con_carichi()


def test_la_regola_legge_le_formule_dei_carichi(prova):
    regola = prova.regola_ritenuta(date(2026, 6, 1))
    assert (regola.carichi_coniuge, regola.carichi_ascendente) == ("720", "480")
    assert "600 * fisco.figli" in regola.carichi_figlio


def test_senza_formule_dei_carichi_valgono_zero():
    regola = Corpus.da_toml(TESTO).regola_ritenuta(date(2026, 6, 1))
    assert (regola.carichi_coniuge, regola.carichi_figlio, regola.carichi_ascendente) == ("0", "0", "0")


def test_il_numero_dei_figli_e_una_variabile_del_fisco_ammessa():
    con_carichi("carichi_figlio = '''fisco.figli'''\n")


@pytest.mark.parametrize(
    "formula", ["fatto.x", "importo.x", "base.x", "fisco.sconosciuto", "parametro.inesistente", "fisco.imponibile < 3"]
)
def test_i_carichi_hanno_gli_stessi_controlli_delle_altre_formule(formula):
    with pytest.raises((ErroreCorpus, ErroreFormula)):
        con_carichi(f"carichi_figlio = '''{formula}'''\n")


def test_la_versione_del_corpus_cambia_con_i_carichi(prova):
    assert Corpus.da_toml(TESTO).versione != prova.versione


# Ritenuta del mese: un dodicesimo per familiare a carico nel mese di paga

def ritenuta_di(registro, orologio, corpus, mese=6, dichiarazione=False):
    """Ritenuta del pagamento del 27 del mese su 1500 lordi: senza detrazioni 216,67; con la dichiarazione 55,00 in meno."""
    if dichiarazione:
        dichiara(registro, orologio)
    righe = stipendio(registro, corpus, Mese(2026, mese))
    return paga(registro, orologio, corpus, righe, date(2026, mese, 27))[1]


def test_il_coniuge_riduce_la_ritenuta_di_un_dodicesimo_anche_senza_dichiarazione(registro, orologio, prova):
    assumi(registro)
    registro.registra_familiare_a_carico(P, "coniuge", CF_CONIUGE, date(1982, 3, 1), 100, date(2026, 1, 1), None, ATTO)
    fiscale = ritenuta_di(registro, orologio, prova)
    assert fiscale.ritenuta.valore == D("156.67")  # 216,67 - 720 / 12
    assert fiscale.avvisi_di("senza_dichiarazione_sostituito")


def test_i_carichi_si_sommano_alla_detrazione_a_richiesta(registro, orologio, prova):
    assumi(registro)
    figlio(registro, nascita=date(2004, 8, 15))
    fiscale = ritenuta_di(registro, orologio, prova, dichiarazione=True)
    assert fiscale.ritenuta.valore == D("111.67")  # 216,67 - 55,00 - 600 / 12


def test_la_percentuale_riduce_la_quota_del_familiare(registro, orologio, prova):
    assumi(registro)
    figlio(registro, percentuale=50)
    assert ritenuta_di(registro, orologio, prova).ritenuta.valore == D("191.67")  # 216,67 - 600 * 50% / 12


def test_l_ascendente_e_pro_quota(registro, orologio, prova):
    assumi(registro)
    registro.registra_familiare_a_carico(P, "ascendente", CF_ASCENDENTE, date(1945, 5, 10), 25, date(2026, 1, 1), None, ATTO)
    assert ritenuta_di(registro, orologio, prova).ritenuta.valore == D("206.67")  # 216,67 - 480 * 25% / 12


def test_imposta_meno_le_detrazioni_non_scende_sotto_zero(registro, orologio, prova):
    assumi(registro)
    for cf, nascita in ((CF_FIGLIO, date(2004, 8, 15)), (CF_FIGLIO_2, date(2003, 2, 1)), (CF_ALTRO, date(2002, 4, 4))):
        figlio(registro, cf=cf, nascita=nascita)
    assert ritenuta_di(registro, orologio, prova).ritenuta.valore == D("0.00")  # 3 figli: 1800 / 12 ciascuno


def test_il_numero_dei_figli_del_mese_entra_nella_formula(registro, orologio, prova):
    assumi(registro)
    figlio(registro, nascita=date(2004, 8, 15))
    figlio(registro, cf=CF_FIGLIO_2, nascita=date(2003, 2, 1))
    assert ritenuta_di(registro, orologio, prova).ritenuta.valore == D("16.67")  # 216,67 - 2 * 1200 / 12


def test_il_figlio_in_luogo_del_coniuge_usa_la_formula_del_coniuge_e_conta_tra_i_figli(registro, orologio, prova):
    assumi(registro)
    registro.registra_familiare_a_carico(
        P, "figlio_in_luogo_del_coniuge", CF_FIGLIO, date(2004, 8, 15), 100, date(2026, 1, 1), None, ATTO
    )
    figlio(registro, cf=CF_FIGLIO_2, nascita=date(2003, 2, 1))
    # coniuge 720 / 12 = 60,00; il figlio con due figli nel mese 1200 / 12 = 100,00
    assert ritenuta_di(registro, orologio, prova).ritenuta.valore == D("56.67")


def test_il_figlio_di_15_anni_non_da_detrazione_e_segnala_un_avviso(registro, orologio, prova):
    assumi(registro)
    fatto = figlio(registro, nascita=date(2011, 3, 3))
    fiscale = ritenuta_di(registro, orologio, prova)
    assert fiscale.ritenuta.valore == D("216.67")
    (avviso,) = fiscale.avvisi_di("familiare_fuori_eta")
    assert avviso.persona == P and CF_FIGLIO in avviso.messaggio
    assert fatto not in fiscale.ritenuta.derivazione.fatti


def test_il_figlio_fuori_eta_non_conta_tra_i_figli_della_formula(registro, orologio, prova):
    assumi(registro)
    figlio(registro, nascita=date(2004, 8, 15))
    figlio(registro, cf=CF_FIGLIO_2, nascita=date(2012, 2, 1))
    assert ritenuta_di(registro, orologio, prova).ritenuta.valore == D("166.67")  # un solo figlio dà diritto: 600 / 12


@pytest.mark.parametrize(
    ("nascita", "mese", "detrazione"),
    [
        (date(2005, 7, 31), 6, False),  # compie 21 anni a luglio: giugno no
        (date(2005, 7, 31), 7, True),  # il mese del 21° compleanno conta intero
        (date(1996, 9, 10), 8, True),  # 30 anni a settembre: agosto è l'ultimo mese
        (date(1996, 9, 10), 9, False),
    ],
)
def test_il_figlio_da_diritto_dal_mese_del_21_compleanno_al_mese_prima_del_30(
    registro, orologio, prova, nascita, mese, detrazione
):
    assumi(registro)
    figlio(registro, nascita=nascita)
    fiscale = ritenuta_di(registro, orologio, prova, mese=mese)
    assert fiscale.ritenuta.valore == (D("166.67") if detrazione else D("216.67"))
    assert bool(fiscale.avvisi_di("familiare_fuori_eta")) is not detrazione


def test_il_figlio_con_disabilita_da_diritto_senza_limite_di_eta(registro, orologio, prova):
    assumi(registro)
    registro.registra_familiare_a_carico(P, "figlio_disabile", CF_FIGLIO, date(1970, 1, 1), 100, date(2026, 1, 1), None, ATTO)
    fiscale = ritenuta_di(registro, orologio, prova)
    assert fiscale.ritenuta.valore == D("166.67")
    assert not fiscale.avvisi_di("familiare_fuori_eta")


def test_la_derivazione_cita_i_familiari_usati(registro, orologio, prova):
    assumi(registro)
    fatto = figlio(registro, nascita=date(2004, 8, 15))
    fiscale = ritenuta_di(registro, orologio, prova, dichiarazione=True)
    derivazione = fiscale.ritenuta.derivazione
    assert fatto in derivazione.fatti
    assert any(f.tipo == "dichiarazione_sostituito" for f in derivazione.fatti)
    assert "carichi di famiglia" in derivazione.formula


def test_il_familiare_non_ancora_valido_nel_mese_non_conta(registro, orologio, prova):
    assumi(registro)
    figlio(registro, dal=date(2026, 7, 1))
    assert ritenuta_di(registro, orologio, prova, mese=6).ritenuta.valore == D("216.67")


# Conguaglio: la somma dei dodici mesi dell'anno

def anno_di_paghe_con_carichi(registro, orologio, corpus):
    ritenute, conguaglio = [], None
    for numero in range(1, 13):
        orologio.vai(numero, 1)
        righe = stipendio(registro, corpus, Mese(2026, numero))
        _, fiscale = paga(registro, orologio, corpus, righe, date(2026, numero, 27), ultimo=numero == 12)
        ritenute.append(fiscale.ritenuta.valore)
        conguaglio = fiscale.conguaglio
    return ritenute, conguaglio


def test_il_conguaglio_somma_i_mesi_a_carico_di_un_figlio_che_compie_21_anni_a_meta_anno(registro, orologio, prova):
    assumi(registro)
    dichiara(registro, orologio)
    figlio(registro, nascita=date(2005, 7, 10))
    ritenute, conguaglio = anno_di_paghe_con_carichi(registro, orologio, prova)
    assert ritenute[:6] == [D("161.67")] * 6  # 216,67 - 55,00
    assert ritenute[6:] == [D("111.67")] * 6  # e 600 / 12 da luglio
    # imposta 2600,00 - detrazione 660,00 - carichi 600 * 6 / 12 = 1640,00; già operato 970,02 + 670,02
    assert conguaglio.valore == D("-0.04")


def test_il_conguaglio_non_rapporta_i_carichi_ai_giorni_di_servizio(registro, orologio, prova):
    assumi(registro)
    figlio(registro, nascita=date(2004, 8, 15))
    _, conguaglio = anno_di_paghe_con_carichi(registro, orologio, prova)
    # senza dichiarazione: imposta 2600,00 - carichi 600,00 = 2000,00; ritenute 12 * (216,67 - 50,00) = 2000,04
    assert conguaglio.valore == D("-0.04")
    assert [f.tipo for f in conguaglio.derivazione.fatti] == ["familiare_a_carico"]
    assert "carichi di famiglia" in conguaglio.derivazione.formula


def test_il_conguaglio_con_due_figli_in_mesi_diversi_conta_i_figli_di_ogni_mese(registro, orologio, prova):
    assumi(registro)
    figlio(registro, nascita=date(2004, 8, 15))  # 12 mesi
    figlio(registro, cf=CF_FIGLIO_2, nascita=date(2005, 7, 10))  # da luglio: 6 mesi
    _, conguaglio = anno_di_paghe_con_carichi(registro, orologio, prova)
    # gennaio-giugno un figlio: 600 / 12 per 6 mesi = 300; luglio-dicembre due figli: 2 * 1200 / 12 per 6 mesi = 1200
    # dovuto 2600 - 1500 = 1100; ritenute 6 * 166,67 + 6 * 16,67 = 1100,04
    assert conguaglio.valore == D("-0.04")


def test_il_conguaglio_non_scende_sotto_zero(registro, orologio, prova):
    assumi(registro)
    for cf, nascita in ((CF_FIGLIO, date(2004, 8, 15)), (CF_FIGLIO_2, date(2003, 2, 1)), (CF_ALTRO, date(2002, 4, 4))):
        figlio(registro, cf=cf, nascita=nascita)
    ritenute, conguaglio = anno_di_paghe_con_carichi(registro, orologio, prova)
    assert ritenute == [D("0.00")] * 12
    assert conguaglio.valore == D("0.00")


# Formule del corpus reale: art. 12 c. 1 TUIR (2026) e art. 12 c. 1 del testo unico (2027), sui valori della ricerca

@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS_REALE, reale=True)


def annuo(reale, gruppo, reddito, figli=1, giorno=date(2026, 6, 1), percentuale=100):
    """Detrazione annua di un familiare: dodici mesi con lo stesso numero di figli, come nel conguaglio."""
    regola = reale.regola_ritenuta(giorno)
    voce = _Voce(gruppo, getattr(regola, gruppo), percentuale, None)
    mesi = tuple(_CaricoMese(figli, (voce,)) for _ in range(12))
    return _calcola(reale, regola, D(reddito), 1, giorno, None, carichi=mesi)


@pytest.mark.parametrize("giorno", [date(2026, 6, 1), date(2027, 6, 1)])
@pytest.mark.parametrize(
    ("reddito", "atteso"),
    [
        ("0", "0.00"),  # rapporto della fascia a1 pari a zero: non compete (art. 12 c. 4)
        ("10000", "726.67"),  # 800 - 110 x 0,6666 (rapporto troncato; arrotondato darebbe 726,66)
        ("15000", "690.00"),
        ("15000.01", "690.00"),
        ("29000", "690.00"),
        ("29000.01", "700.00"),  # maggiorazione di 10 euro, estremo inferiore escluso
        ("29200", "700.00"),
        ("29200.01", "710.00"),
        ("30000", "710.00"),
        ("34700", "710.00"),
        ("34700.01", "720.00"),
        ("35000", "720.00"),
        ("35000.01", "710.00"),
        ("35100", "710.00"),
        ("35100.01", "700.00"),
        ("35200", "700.00"),
        ("35200.01", "690.00"),
        ("40000", "690.00"),
        ("60000", "345.00"),
        ("79999", "0.00"),  # rapporto della fascia a3 troncato a zero: non compete
        ("80000", "0.00"),
        ("120000", "0.00"),
    ],
)
def test_coniuge(reale, giorno, reddito, atteso):
    assert annuo(reale, "carichi_coniuge", reddito, giorno=giorno).carichi == D(atteso)


@pytest.mark.parametrize("giorno", [date(2026, 6, 1), date(2027, 6, 1)])
@pytest.mark.parametrize(
    ("reddito", "figli", "atteso"),
    [
        ("0", 1, "0.00"),  # rapporto uguale a uno: non compete
        ("47000", 1, "479.94"),  # 950 x 0,5052 (rapporto troncato; arrotondato darebbe 0,5053)
        ("47500", 1, "475.00"),
        ("94999", 1, "0.00"),
        ("95000", 1, "0.00"),
        ("130000", 1, "0.00"),
        ("55000", 2, "475.00"),  # soglia 110.000: (110.000 - 55.000) / 110.000
        ("62500", 3, "475.00"),  # soglia 125.000
        ("100000", 2, "86.36"),  # 950 x 0,0909: con un figlio solo sarebbe zero
        ("100000", 1, "0.00"),
    ],
)
def test_figli(reale, giorno, reddito, figli, atteso):
    assert annuo(reale, "carichi_figlio", reddito, figli, giorno).carichi == D(atteso)


@pytest.mark.parametrize("giorno", [date(2026, 6, 1), date(2027, 6, 1)])
@pytest.mark.parametrize(
    ("reddito", "atteso"), [("0", "0.00"), ("40000", "375.00"), ("60000", "187.50"), ("79999", "0.00"), ("80000", "0.00")]
)
def test_ascendente(reale, giorno, reddito, atteso):
    assert annuo(reale, "carichi_ascendente", reddito, giorno=giorno).carichi == D(atteso)


def test_la_percentuale_e_pro_quota(reale):
    assert annuo(reale, "carichi_figlio", "47500", percentuale=50).carichi == D("237.50")
    assert annuo(reale, "carichi_ascendente", "40000", percentuale=40).carichi == D("150.00")


def test_la_ritenuta_mensile_e_un_dodicesimo_al_centesimo(reale):
    regola = reale.regola_ritenuta(date(2026, 6, 1))
    voce = _Voce("carichi_coniuge", regola.carichi_coniuge, 100, None)
    mese = _calcola(reale, regola, D("3333.33"), 12, date(2026, 6, 1), None, carichi=(_CaricoMese(0, (voce,)),))
    assert mese.carichi == D("57.50")  # R = 3.333,33 x 12 = 39.999,96: fascia da 690, un dodicesimo
    mese = _calcola(reale, regola, D("833.33"), 12, date(2026, 6, 1), None, carichi=(_CaricoMese(0, (voce,)),))
    assert mese.carichi == D("60.56")  # R = 9.999,96: 800 - 110 x 0,6666 = 726,674; diviso 12 = 60,5562


def test_il_reddito_dei_carichi_e_quello_dell_art_13(reale):
    """R = imponibile del periodo per i periodi: lo stesso della detrazione per lavoro dipendente."""
    regola = reale.regola_ritenuta(date(2026, 6, 1))
    voce = _Voce("carichi_figlio", regola.carichi_figlio, 100, None)
    mese = _calcola(reale, regola, D("3958.33"), 12, date(2026, 6, 1), None, carichi=(_CaricoMese(1, (voce,)),))
    assert mese.carichi == D("39.58")  # R = 47.499,96: 950 x 0,5 = 475; la tronca a 4 cifre dà 0,5000, un dodicesimo


def test_la_versione_2027_si_usa_per_i_pagamenti_2027_con_la_sua_fonte(reale):
    fonti = {
        giorno: {p.nome: p.riferimento for p in annuo(reale, "carichi_figlio", "47500", giorno=giorno).parametri}
        for giorno in (date(2026, 6, 1), date(2027, 6, 1))
    }
    figlio_2026 = {nome: r for nome, r in fonti[date(2026, 6, 1)].items() if nome.startswith("carichi_figlio")}
    figlio_2027 = {nome: r for nome, r in fonti[date(2027, 6, 1)].items() if nome.startswith("carichi_figlio")}
    assert figlio_2026 and figlio_2026.keys() == figlio_2027.keys()
    assert all(r.endswith("917~art12-com1-letc") for r in figlio_2026.values())
    assert set(figlio_2027.values()) == {"urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art12-com1"}
    regola_2026, regola_2027 = reale.regola_ritenuta(date(2026, 6, 1)), reale.regola_ritenuta(date(2027, 6, 1))
    assert regola_2026.versione == 1 and regola_2027.versione == 2


def test_le_formule_dei_carichi_sono_nelle_due_versioni_della_regola(reale):
    for giorno in (date(2026, 6, 1), date(2027, 6, 1)):
        regola = reale.regola_ritenuta(giorno)
        assert "0" not in (regola.carichi_coniuge, regola.carichi_figlio, regola.carichi_ascendente)
        assert "fisco.figli" in regola.carichi_figlio
