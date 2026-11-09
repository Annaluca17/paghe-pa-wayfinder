"""Somma esente e trattamento integrativo nel corpus reale (ticket #95): fasce, soglie, rapporto ai giorni, versioni 2026 e 2027."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Corpus
from paghe.benefici import Contesto, _valuta

CORPUS_REALE = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
D = Decimal
ANNI = pytest.mark.parametrize("anno", [2026, 2027])


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS_REALE, reale=True)


def contesto(
    stimato="10000", dipendente="1000", imposta="0", detrazione="0", oneri="0", periodi=12, giorni=1, giorni_anno=1,
    fascia=None,
):
    return Contesto(
        D(stimato), "prova", D(dipendente), D(fascia if fascia is not None else stimato), D(imposta), D(detrazione),
        D(oneri), periodi, giorni, giorni_anno, importi=(),
    )


def somma_esente(reale, anno, **valori):
    regola = reale.regola_benefici(date(anno, 6, 1))
    return _valuta(reale, regola.somma_esente, contesto(**valori), date(anno, 6, 1))[0]


def integrativo(reale, anno, **valori):
    regola = reale.regola_benefici(date(anno, 6, 1))
    return _valuta(reale, regola.trattamento_integrativo, contesto(**valori), date(anno, 6, 1))[0]


@ANNI
@pytest.mark.parametrize(
    ("stimato", "atteso"),
    [
        ("8500", "71.00"),  # fino a 8.500 compresi: 7,1%
        ("8500.01", "53.00"),  # poi 5,3%
        ("15000", "53.00"),
        ("15000.01", "48.00"),  # poi 4,8%
        ("20000", "48.00"),
        ("20000.01", "0.00"),  # oltre 20.000 non spetta
    ],
)
def test_la_percentuale_della_somma_esente_segue_la_fascia_del_reddito_stimato(reale, anno, stimato, atteso):
    assert somma_esente(reale, anno, stimato=stimato, dipendente="1000") == D(atteso)


@ANNI
def test_la_somma_esente_e_la_percentuale_sul_reddito_di_lavoro_dipendente_del_periodo(reale, anno):
    assert somma_esente(reale, anno, stimato="12000", dipendente="1500") == D("79.50")  # 5,3% di 1500


@ANNI
def test_sotto_15000_il_trattamento_integrativo_e_un_dodicesimo_se_l_imposta_supera_la_detrazione_meno_75_rapportati(reale, anno):
    # detrazione del periodo 106,25 meno 75 / 12 = 100,00: l'imposta deve superarlo
    assert integrativo(reale, anno, stimato="14000", imposta="100.01", detrazione="106.25") == D("100.00")
    assert integrativo(reale, anno, stimato="14000", imposta="100.00", detrazione="106.25") == D("0.00")


@ANNI
def test_tra_15000_e_28000_conta_la_differenza_fra_detrazioni_e_imposta_lorda_fino_a_un_dodicesimo(reale, anno):
    assert integrativo(reale, anno, stimato="20000", imposta="60", detrazione="90") == D("30.00")
    assert integrativo(reale, anno, stimato="20000", imposta="10", detrazione="150") == D("100.00")  # tetto 1.200 / 12
    assert integrativo(reale, anno, stimato="20000", imposta="200", detrazione="150") == D("0.00")


@ANNI
def test_gli_oneri_comunicati_si_sommano_alle_detrazioni_note(reale, anno):
    assert integrativo(reale, anno, stimato="20000", imposta="200", detrazione="150", oneri="900") == D("25.00")


@ANNI
def test_oltre_28000_il_trattamento_integrativo_non_spetta(reale, anno):
    assert integrativo(reale, anno, stimato="28000", imposta="0", detrazione="90") == D("90.00")
    assert integrativo(reale, anno, stimato="28000.01", imposta="0", detrazione="90") == D("0.00")


@ANNI
def test_al_conguaglio_il_trattamento_integrativo_e_rapportato_ai_giorni_di_servizio(reale, anno):
    valore = integrativo(reale, anno, stimato="10000", imposta="900", detrazione="800", periodi=1, giorni=182, giorni_anno=365)
    assert valore == D("598.36")  # 1.200 * 182 / 365


def test_le_versioni_del_2027_hanno_gli_stessi_valori_e_citano_il_testo_unico(reale):
    prima, dopo = reale.regola_benefici(date(2026, 6, 1)), reale.regola_benefici(date(2027, 6, 1))
    assert (prima.versione, dopo.versione) == (1, 2)
    assert (prima.somma_esente, prima.trattamento_integrativo) == (dopo.somma_esente, dopo.trattamento_integrativo)
    assert "art376-com2" in dopo.riferimento and "art376-com2" not in prima.riferimento
    for nome in prima.parametri:
        assert reale.parametro(nome).vigenza_per(_mese(2026)).valore == reale.parametro(nome).vigenza_per(_mese(2027)).valore


def _mese(anno):
    from paghe import Mese

    return Mese(anno, 6)


def test_le_categorie_il_trattamento_integrativo_a_dipendenti_e_collaboratori_non_alle_cariche(reale):
    regola = reale.regola_benefici(date(2026, 6, 1))
    assert regola.categorie_somma_esente == ("lavoro_dipendente",)
    assert regola.categorie_trattamento_integrativo == ("lavoro_dipendente", "collaborazione")


def test_i_parametri_di_soglia_e_rate_dei_recuperi_sono_quelli_della_norma(reale):
    regola = reale.regola_benefici(date(2026, 6, 1))
    letti = {n: reale.parametro(n).vigenza_per(_mese(2026)).valore for n in (
        regola.soglia_recupero, regola.rate_trattamento_integrativo, regola.rate_somma_esente
    )}
    assert list(letti.values()) == [D(60), D(8), D(10)]


@ANNI
def test_i_codici_f24ep_sono_una_mappatura_datata_degli_istituti(reale, anno):
    giorno = date(anno, 6, 1)
    codici = {
        i: reale.mappatura(i, "codice_tributo_f24ep", giorno, anno).codice
        for i in ("somma_esente", "somma_esente_recupero", "trattamento_integrativo", "trattamento_integrativo_recupero")
    }
    assert codici == {
        "somma_esente": "175E",
        "somma_esente_recupero": "175E",
        "trattamento_integrativo": "170E",
        "trattamento_integrativo_recupero": "170E",
    }
    assert reale.composizione("trattamento_integrativo", giorno).natura == "credito_sostituto"
    assert reale.composizione("trattamento_integrativo_recupero", giorno).canale == "f24ep"
