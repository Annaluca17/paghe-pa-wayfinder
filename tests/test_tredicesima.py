"""Tredicesima mensilità del comparto (ADR 0038, nota di prassi 12).

Tre gruppi. Il motore annuale con un corpus fittizio; il corpus reale, con importi ricalcolati a mano dal tabellare
mensile della nota di prassi 3 (Funzionari 2.192,02; Istruttori 2.019,63; Operatori 1.724,21 nel 2026); il fisco della
mensilità aggiuntiva con il corpus fittizio di `test_fiscale`. Persone e rapporti sono di fantasia.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Corpus, Mese, Periodo, calcola, calcola_annuale
from paghe.errori import CasoNonModellato, ErroreCorpus
from paghe.fisco import AVVISO_MENSILITA_AGGIUNTIVA, AVVISO_MENSILITA_FUORI_FINESTRA
from paghe.formula import riferimenti
from test_fiscale import TESTO, assumi, paga

CORPUS_REALE = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
R = "RAPPORTO-1"
AREE = ("funzionari", "istruttori", "operatori_esperti", "operatori")


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS_REALE, reale=True)


def assumi_comparto(registro, area="istruttori", regime="3", dal=date(2019, 1, 1), al=None):
    registro.registra_codice(R, "tipo_impiego", "1", dal, al)
    registro.registra_codice(R, "area", area, dal, al)
    registro.registra_codice(R, "regime_fine_servizio", regime, dal, al)


def valori(importi):
    return {importo.istituto: importo.valore for importo in importi}


# --- Motore annuale, corpus fittizio ---

ANNUALE = """
[periodo_dichiarato]
servizio = "servizio"

[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "365"
riferimento = "fittizio:d"

[[parametro]]
nome = "alta"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "2000.00"
riferimento = "fittizio:alta"

[[parametro]]
nome = "bassa"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "1000.00"
riferimento = "fittizio:bassa"

[[regola]]
istituto = "gratifica_alta"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:gratifica-alta"
formula = "parametro.alta"
maturazione = "annuale"
applica_se = "livello=alto"
conteggio = "calendario"
divisore = "d"
decimali = 2

[[regola]]
istituto = "gratifica_bassa"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:gratifica-bassa"
formula = "parametro.bassa"
maturazione = "annuale"
applica_se = "livello=basso"
conteggio = "calendario"
divisore = "d"
decimali = 2

[[regola]]
istituto = "riduzione"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:riduzione"
formula = "-arrotonda((importo.gratifica_alta + importo.gratifica_bassa) / 10, 2)"
maturazione = "annuale"
applica_se = "regime=1"
conteggio = "calendario"
divisore = "d"
decimali = 2
"""

PART_TIME = """
[[part_time]]
istituto = "gratifica_{livello}"
trattamento = "{trattamento}"
dal = 2020-01-01
riferimento = "fittizio:pt-gratifica-{livello}"
"""


def fittizio(trattamento="proporzionale"):
    extra = "".join(PART_TIME.format(livello=livello, trattamento=trattamento) for livello in ("alta", "bassa"))
    return Corpus.da_toml(ANNUALE + (extra if trattamento else ""))


def test_i_giorni_sono_quelli_di_servizio_e_la_regola_e_quella_dell_ultimo_giorno(registro):
    """Cambio di codice nell'anno: una sola regola, quella dell'ultimo giorno, su tutti i giorni di servizio."""
    registro.registra_codice(R, "servizio", "1", date(2026, 1, 1))
    registro.registra_codice(R, "livello", "basso", date(2026, 1, 1), date(2026, 1, 31))
    registro.registra_codice(R, "livello", "alto", date(2026, 2, 1))
    (importo,) = calcola_annuale(registro, fittizio(), R, 2026)
    assert (importo.istituto, importo.valore) == ("gratifica_alta", Decimal("2000.00"))
    assert importo.periodo == Periodo(date(2026, 1, 1), date(2026, 12, 31))
    assert importo.derivazione.quota.giorni == 365


def test_il_servizio_interrotto_non_matura(registro):
    """I giorni senza il fatto di servizio (sospensione senza retribuzione) non contano: 59 + 245 = 304 giorni."""
    registro.registra_codice(R, "servizio", "1", date(2026, 1, 1), date(2026, 2, 28))
    registro.registra_codice(R, "servizio", "1", date(2026, 5, 1))
    registro.registra_codice(R, "livello", "basso", date(2026, 1, 1))
    (importo,) = calcola_annuale(registro, fittizio(), R, 2026)
    assert importo.derivazione.quota.giorni == 304
    assert importo.valore == Decimal("832.88")  # 1000 * 304 / 365


def test_il_maturato_a_una_data_conta_i_giorni_fino_a_quel_giorno(registro):
    registro.registra_codice(R, "servizio", "1", date(2026, 1, 1))
    registro.registra_codice(R, "livello", "basso", date(2026, 1, 1))
    (importo,) = calcola_annuale(registro, fittizio(), R, 2026, fino_al=date(2026, 6, 30))
    assert importo.periodo == Periodo(date(2026, 1, 1), date(2026, 6, 30))
    assert importo.valore == Decimal("495.89")  # 1000 * 181 / 365
    assert calcola_annuale(registro, fittizio(), R, 2026, fino_al=date(2025, 12, 31)) == ()


def test_il_part_time_di_tutto_l_anno_riduce_in_proporzione(registro):
    registro.registra_codice(R, "servizio", "1", date(2026, 1, 1))
    registro.registra_codice(R, "livello", "basso", date(2026, 1, 1))
    registro.registra_fatto(R, "part_time", "60", date(2026, 1, 1))
    (importo,) = calcola_annuale(registro, fittizio(), R, 2026)
    assert importo.valore == Decimal("600.00")
    riduzione = importo.derivazione.part_time
    assert (riduzione.percentuale, riduzione.importo_pieno, riduzione.trattamento) == (
        Decimal("60.000000"), Decimal("1000.00"), "proporzionale",
    )
    assert any(fatto.tipo == "part_time" for fatto in importo.derivazione.fatti)


def test_il_part_time_che_cambia_nell_anno_pesa_i_periodi_a_giorni(registro):
    """50% fino al 31 ottobre (304 giorni), tempo pieno dal 1° novembre (61 giorni): (304 * 50 + 61 * 100) / 365."""
    registro.registra_codice(R, "servizio", "1", date(2026, 1, 1))
    registro.registra_codice(R, "livello", "basso", date(2026, 1, 1))
    registro.registra_fatto(R, "part_time", "50", date(2026, 1, 1), date(2026, 10, 31))
    (importo,) = calcola_annuale(registro, fittizio(), R, 2026)
    assert importo.valore == Decimal("583.56")
    assert importo.derivazione.part_time.percentuale == Decimal("58.356164")


def test_il_part_time_senza_trattamento_dichiarato_ferma_e_nomina(registro):
    registro.registra_codice(R, "servizio", "1", date(2026, 1, 1))
    registro.registra_codice(R, "livello", "basso", date(2026, 1, 1))
    registro.registra_fatto(R, "part_time", "60", date(2026, 1, 1))
    with pytest.raises(CasoNonModellato, match="gratifica_bassa non dichiara il trattamento nel part-time"):
        calcola_annuale(registro, fittizio(trattamento=None), R, 2026)


def test_il_trattamento_intero_non_riduce(registro):
    registro.registra_codice(R, "servizio", "1", date(2026, 1, 1))
    registro.registra_codice(R, "livello", "basso", date(2026, 1, 1))
    registro.registra_fatto(R, "part_time", "60", date(2026, 1, 1))
    (importo,) = calcola_annuale(registro, fittizio(trattamento="intero"), R, 2026)
    assert importo.valore == Decimal("1000.00")


def test_una_regola_annuale_deriva_da_importi_annuali_se_la_condizione_vale_l_ultimo_giorno(registro):
    registro.registra_codice(R, "servizio", "1", date(2026, 1, 1))
    registro.registra_codice(R, "livello", "basso", date(2026, 1, 1))
    assert set(valori(calcola_annuale(registro, fittizio(), R, 2026))) == {"gratifica_bassa"}
    registro.registra_codice(R, "regime", "1", date(2026, 7, 1))
    importi = calcola_annuale(registro, fittizio(), R, 2026)
    assert valori(importi) == {"gratifica_bassa": Decimal("1000.00"), "riduzione": Decimal("-100.00")}
    riduzione = next(importo for importo in importi if importo.istituto == "riduzione")
    assert riduzione.periodo == Periodo(date(2026, 1, 1), date(2026, 12, 31))
    assert [riga.istituto for riga in riduzione.derivazione.importi] == ["gratifica_bassa"]


def test_una_regola_annuale_non_legge_importi_del_mese():
    testo = ANNUALE.replace("importo.gratifica_alta + importo.gratifica_bassa", "importo.gratifica_alta + importo.mensile") + """
[[regola]]
istituto = "mensile"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:mensile"
formula = "parametro.bassa"
maturazione = "evento"
applica_se = "livello"
"""
    with pytest.raises(ErroreCorpus, match="una regola annuale legge solo importi annuali, non mensile"):
        Corpus.da_toml(testo)


def test_la_finestra_della_mensilita_aggiuntiva_va_dichiarata_intera():
    testo = ANNUALE + """
[[mensilita_aggiuntiva]]
istituto = "gratifica_alta"
dal = 2020-01-01
riferimento = "fittizio:aggiuntiva"
mese_pagamento = 12
"""
    with pytest.raises(ErroreCorpus, match="finestra di pagamento"):
        Corpus.da_toml(testo)


# --- Corpus reale ---

def test_servizio_di_tutto_l_anno_tredicesima_intera_sul_tabellare_dell_area(registro, reale):
    assumi_comparto(registro)
    (importo,) = calcola_annuale(registro, reale, R, 2026)
    assert (importo.istituto, importo.valore) == ("tredicesima_istruttori", Decimal("2019.63"))
    assert importo.periodo == Periodo(date(2026, 1, 1), date(2026, 12, 31))
    assert "art75" in importo.derivazione.riferimento


@pytest.mark.parametrize(
    ("area", "atteso"),
    [("funzionari", "2192.02"), ("istruttori", "2019.63"), ("operatori_esperti", "1796.60"), ("operatori", "1724.21")],
)
def test_le_quattro_aree_del_comparto(registro, reale, area, atteso):
    assumi_comparto(registro, area)
    assert valori(calcola_annuale(registro, reale, R, 2026)) == {f"tredicesima_{area}": Decimal(atteso)}


def test_la_tredicesima_non_e_nel_calcolo_del_mese(registro, reale):
    assumi_comparto(registro)
    assert not [i for i in calcola(registro, reale, R, Mese(2026, 12)) if "tredicesima" in i.istituto]


def test_assunto_in_corso_d_anno_365esimi(registro, reale):
    """Dal 24 agosto al 31 dicembre: 130 giorni. 2.019,63 * 130 / 365 = 719,32."""
    assumi_comparto(registro, dal=date(2026, 8, 24))
    (importo,) = calcola_annuale(registro, reale, R, 2026)
    assert importo.derivazione.quota.giorni == 130
    assert importo.valore == Decimal("719.32")


def test_cessato_in_corso_d_anno_sui_giorni_prestati(registro, reale):
    """Dal 1° gennaio al 14 marzo: 73 giorni. 2.019,63 * 73 / 365 = 403,93."""
    assumi_comparto(registro, al=date(2026, 3, 14))
    (importo,) = calcola_annuale(registro, reale, R, 2026)
    assert importo.periodo == Periodo(date(2026, 1, 1), date(2026, 3, 14))
    assert importo.valore == Decimal("403.93")


def test_progressione_nell_anno_tutta_la_tredicesima_sull_area_di_dicembre(registro, reale):
    registro.registra_codice(R, "tipo_impiego", "1", date(2019, 1, 1))
    registro.registra_codice(R, "regime_fine_servizio", "3", date(2019, 1, 1))
    registro.registra_codice(R, "area", "istruttori", date(2019, 1, 1), date(2026, 1, 31))
    registro.registra_codice(R, "area", "funzionari", date(2026, 2, 1))
    assert valori(calcola_annuale(registro, reale, R, 2026)) == {"tredicesima_funzionari": Decimal("2192.02")}


def test_part_time_al_60_per_cento(registro, reale):
    """1.724,21 * 60% = 1.034,53."""
    assumi_comparto(registro, "operatori")
    registro.registra_fatto(R, "part_time", "60", date(2019, 1, 1))
    registro.registra_codice(R, "tipo_part_time", "orizzontale", date(2019, 1, 1))
    assert valori(calcola_annuale(registro, reale, R, 2026)) == {"tredicesima_operatori": Decimal("1034.53")}


def test_part_time_fino_a_ottobre_e_tempo_pieno_da_novembre(registro, reale):
    """Parere ARAN CFL188 (nota di prassi 12): 2.192,02 * (304 * 50 + 61 * 100) / 36.500 = 1.279,18."""
    assumi_comparto(registro, "funzionari")
    registro.registra_fatto(R, "part_time", "50", date(2019, 1, 1), date(2026, 10, 31))
    registro.registra_codice(R, "tipo_part_time", "orizzontale", date(2019, 1, 1), date(2026, 10, 31))
    assert valori(calcola_annuale(registro, reale, R, 2026)) == {"tredicesima_funzionari": Decimal("1279.18")}


def test_in_regime_tfr_la_tredicesima_porta_la_riduzione_del_lordo(registro, reale):
    """80% di 2.019,63 = 1.615,70; il 2,50% e' 40,39."""
    assumi_comparto(registro, regime="1")
    assert valori(calcola_annuale(registro, reale, R, 2026)) == {
        "tredicesima_istruttori": Decimal("2019.63"),
        "riduzione_tfr_tredicesima": Decimal("-40.39"),
    }


def test_il_tabellare_del_2027_vale_per_la_tredicesima_del_2027(registro, reale):
    assumi_comparto(registro)
    assert valori(calcola_annuale(registro, reale, R, 2027)) == {"tredicesima_istruttori": Decimal("2055.86")}


def test_la_retribuzione_ridotta_ferma_anche_la_tredicesima(registro, reale):
    assumi_comparto(registro)
    registro.registra_fatto(R, "percentuale_retribuzione", "50", date(2026, 5, 1), date(2026, 5, 31))
    with pytest.raises(CasoNonModellato, match="retribuzione ridotta"):
        calcola_annuale(registro, reale, R, 2026)


@pytest.mark.parametrize("area", AREE)
def test_le_dichiarazioni_della_tredicesima(reale, area):
    istituto = f"tredicesima_{area}"
    for giorno in (date(2026, 12, 18), date(2027, 12, 17)):
        for base, misura in (
            ("cpdel", "intero"), ("fondo_credito", "intero"), ("tfs", "intero"), ("irap", "intero"),
            ("tfr_ulteriori", "escluso"), ("gestione_separata", "escluso"),
        ):
            assert reale.concorso(istituto, base, giorno).misura == misura
            assert reale.concorso("riduzione_tfr_tredicesima", base, giorno).misura == "escluso"
        assert reale.reddito(istituto, giorno).categoria == "lavoro_dipendente"
        assert reale.reddito("riduzione_tfr_tredicesima", giorno).categoria == "lavoro_dipendente"
        assert reale.trattamento_part_time(istituto, giorno).trattamento == "proporzionale"
        aggiuntiva = reale.mensilita_aggiuntiva(istituto, giorno)
        assert aggiuntiva.nella_finestra(giorno) and not aggiuntiva.nella_finestra(date(giorno.year, 12, 19))
    assert "art23-com2-letb" in reale.mensilita_aggiuntiva(istituto, date(2026, 12, 18)).riferimento
    assert reale.mensilita_aggiuntiva("riduzione_tfr_tredicesima", date(2026, 12, 18)) is None
    assert reale.mensilita_aggiuntiva(f"tabellare_{area}", date(2026, 12, 18)) is None


def test_le_due_riduzioni_tfr_leggono_tutte_le_voci_utili_al_tfs(reale):
    """Mese e tredicesima insieme coprono gli istituti che concorrono per intero alla base tfs (ADR 0010 e 0038)."""
    giorno = Periodo(date(2026, 11, 1), date(2026, 11, 1))
    del_mese = riferimenti(reale.regola_per("riduzione_tfr", giorno).formula).importi
    annuale = riferimenti(reale.regola_per("riduzione_tfr_tredicesima", giorno).formula).importi
    interi = {
        istituto
        for istituto in reale.istituti()
        if (concorso := reale.concorso(istituto, "tfs", date(2026, 11, 1))) and concorso.misura == "intero"
    }
    assert annuale == {f"tredicesima_{area}" for area in AREE}
    assert del_mese | annuale == interi and not del_mese & annuale


# --- Fisco della mensilità aggiuntiva, corpus fittizio di test_fiscale ---

AGGIUNTIVA = TESTO + """
[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "365"
riferimento = "fittizio:d"

[[regola]]
istituto = "gratifica"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:gratifica"
formula = "1500"
maturazione = "annuale"
applica_se = "tipo_impiego=1"
conteggio = "calendario"
divisore = "d"
decimali = 2

[[concorso]]
istituto = "gratifica"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-gratifica"

[[reddito]]
istituto = "gratifica"
categoria = "lavoro_dipendente"
dal = 2020-01-01
riferimento = "fittizio:reddito-gratifica"

[[mensilita_aggiuntiva]]
istituto = "gratifica"
dal = 2020-01-01
riferimento = "fittizio:aggiuntiva"
mese_pagamento = 12
giorno_dal = 10
giorno_al = 18
"""


@pytest.fixture
def fisco():
    return Corpus.da_toml(AGGIUNTIVA)


def test_la_mensilita_aggiuntiva_senza_conguaglio_ferma_il_calcolo_fiscale(registro, fisco, orologio):
    assumi(registro)
    gratifica = calcola_annuale(registro, fisco, R, 2026)
    assert valori(gratifica) == {"gratifica": Decimal("1500.00")}
    with pytest.raises(CasoNonModellato, match="mensilità aggiuntiva \\(gratifica\\) in un pagamento senza conguaglio"):
        paga(registro, orologio, fisco, gratifica, date(2026, 12, 15))


def test_con_il_conguaglio_la_mensilita_aggiuntiva_procede_con_un_avviso_e_il_totale_e_l_imposta_dell_anno(
    registro, fisco, orologio
):
    """Reddito dell'anno 1.500: imposta 150,00 qualunque sia la divisione fra ritenuta e conguaglio."""
    assumi(registro)
    gratifica = calcola_annuale(registro, fisco, R, 2026)
    _, fiscale = paga(registro, orologio, fisco, gratifica, date(2026, 12, 15), ultimo=True)
    assert fiscale.ritenuta.valore + fiscale.conguaglio.valore == Decimal("150.00")
    tipi = [avviso.tipo for avviso in fiscale.avvisi]
    assert AVVISO_MENSILITA_AGGIUNTIVA in tipi and AVVISO_MENSILITA_FUORI_FINESTRA not in tipi


def test_fuori_dalla_finestra_di_pagamento_un_avviso_per_chi_e_in_servizio(registro, fisco, orologio):
    assumi(registro)
    gratifica = calcola_annuale(registro, fisco, R, 2026)
    _, fiscale = paga(registro, orologio, fisco, gratifica, date(2026, 12, 22), ultimo=True)
    avviso = next(a for a in fiscale.avvisi if a.tipo == AVVISO_MENSILITA_FUORI_FINESTRA)
    assert "fuori dai giorni 10-18 del mese 12" in avviso.messaggio


def test_al_cessato_la_mensilita_aggiuntiva_fuori_finestra_non_da_avviso(registro, fisco, orologio):
    registro.registra_codice_persona("PERSONA-1", "codice_fiscale", "RSSMRA80A01H501U", date(1980, 1, 1))
    registro.collega_rapporto(R, "PERSONA-1", date(2026, 1, 1))
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 1, 1), date(2026, 3, 14))
    gratifica = calcola_annuale(registro, fisco, R, 2026)
    assert valori(gratifica) == {"gratifica": Decimal("300.00")}  # 1500 * 73 / 365
    _, fiscale = paga(registro, orologio, fisco, gratifica, date(2026, 3, 27), ultimo=True)
    tipi = [avviso.tipo for avviso in fiscale.avvisi]
    assert AVVISO_MENSILITA_AGGIUNTIVA in tipi and AVVISO_MENSILITA_FUORI_FINESTRA not in tipi
