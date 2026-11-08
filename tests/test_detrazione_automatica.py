"""Detrazione automatica e giorni di servizio nella ritenuta e nel conguaglio (ADR 0019, ticket #93).

Valori e fonti fittizi, sul corpus di test_fiscale (detrazione a richiesta: 55,00 al mese su 1500 al mese). La detrazione
automatica di prova è di 600 annui, rapportata ai giorni di servizio sull'anno e al periodo.
"""

import re
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.errori import ErroreCorpus, ErroreFormula
from test_fiscale import (
    ALTRO,
    CF,
    DETRAZIONE,
    P,
    R,
    TESTO,
    assumi,
    dichiara,
    paga,
    stipendio,
)

IMPOSTA_PROVA = "arrotonda(parametro.aliquota_1 * min(fisco.imponibile, parametro.limite_1 / fisco.periodi) + parametro.aliquota_2 * max(0, fisco.imponibile - parametro.limite_1 / fisco.periodi), 2)"
AUTOMATICA_PROVA = "arrotonda(parametro.detrazione_annua / 2 * fisco.giorni / fisco.giorni_anno / fisco.periodi, 2)"


def con_automatica(formula, imposta=None, detrazione=None):
    testo = TESTO
    if imposta is not None:
        testo = testo.replace(
            testo[testo.index("imposta = '''") : testo.index("detrazione = '''")], f"imposta = '''{imposta}'''\n"
        )
    marca = "detrazione_richiesta = \"lavoro_dipendente\"\n"
    assert marca in testo
    return testo.replace(marca, marca + f"detrazione_automatica = '''{formula}'''\n")


def test_la_regola_legge_la_detrazione_automatica():
    corpus = Corpus.da_toml(con_automatica(AUTOMATICA_PROVA))
    regola = corpus.regola_ritenuta(date(2026, 6, 1))
    assert regola.detrazione_automatica == AUTOMATICA_PROVA
    assert {"detrazione_annua"} <= regola.parametri


def test_senza_detrazione_automatica_vale_zero():
    regola = Corpus.da_toml(TESTO).regola_ritenuta(date(2026, 6, 1))
    assert regola.detrazione_automatica == "0"


@pytest.mark.parametrize(
    "formula",
    ["fatto.x", "importo.x", "base.x", "fisco.sconosciuto", "parametro.inesistente", "fisco.imponibile < 3"],
)
def test_la_detrazione_automatica_ha_gli_stessi_controlli_delle_altre_formule(formula):
    with pytest.raises((ErroreCorpus, ErroreFormula)):
        Corpus.da_toml(con_automatica(formula))


def test_giorni_e_giorni_anno_sono_ammessi_come_fisco():
    Corpus.da_toml(con_automatica("fisco.giorni / fisco.giorni_anno"))


def test_la_versione_del_corpus_cambia_con_la_detrazione_automatica():
    assert Corpus.da_toml(TESTO).versione != Corpus.da_toml(con_automatica(AUTOMATICA_PROVA)).versione


# Ritenuta del mese: detrazione a richiesta e detrazione automatica separate

def corpus_prova(automatica=AUTOMATICA_PROVA):
    return Corpus.da_toml(con_automatica(automatica))


def imposta_di(imponibile, periodi):
    """Imposta di prova: 10% fino a limite_1 (10000) ragguagliato al periodo, 20% oltre."""
    limite = Decimal(10000) / periodi
    return (Decimal("0.1") * min(imponibile, limite) + Decimal("0.2") * max(Decimal(0), imponibile - limite)).quantize(
        Decimal("0.01")
    )


def test_la_detrazione_automatica_si_applica_senza_dichiarazione(registro, orologio):
    corpus = corpus_prova()
    assumi(registro)
    esito, fiscale = paga(registro, orologio, corpus, stipendio(registro, corpus, Mese(2026, 6)), date(2026, 6, 27))
    # automatica del mese: 600 * 1 / 1 / 12 = 50,00 (nella ritenuta del mese i giorni non pesano)
    assert fiscale.ritenuta.valore == imposta_di(Decimal(1500), 12) - Decimal("50.00")


def test_con_la_dichiarazione_si_sommano_le_due_detrazioni(registro, orologio):
    corpus = corpus_prova()
    assumi(registro)
    dichiara(registro, orologio)
    _, fiscale = paga(registro, orologio, corpus, stipendio(registro, corpus, Mese(2026, 6)), date(2026, 6, 27))
    assert fiscale.ritenuta.valore == imposta_di(Decimal(1500), 12) - Decimal("55.00") - Decimal("50.00")
    formula = fiscale.ritenuta.derivazione.formula
    assert DETRAZIONE in formula and AUTOMATICA_PROVA in formula


def test_la_derivazione_dice_quando_la_detrazione_a_richiesta_non_e_applicata(registro, orologio):
    corpus = corpus_prova()
    assumi(registro)
    _, fiscale = paga(registro, orologio, corpus, stipendio(registro, corpus, Mese(2026, 6)), date(2026, 6, 27))
    formula = fiscale.ritenuta.derivazione.formula
    assert "non applicata" in formula and AUTOMATICA_PROVA in formula


def test_le_detrazioni_non_portano_la_ritenuta_sotto_zero(registro, orologio):
    corpus = corpus_prova()
    assumi(registro)
    dichiara(registro, orologio)
    _, fiscale = paga(registro, orologio, corpus, stipendio(registro, corpus, Mese(2026, 6), "100"), date(2026, 6, 27))
    assert fiscale.ritenuta.valore == Decimal("0.00")


# Conguaglio: giorni di servizio della persona nell'anno d'imposta

def servizio(registro, rapporto, dal, al=None, persona=P):
    if not registro.fatti_persona_noti(persona, "codice_fiscale", registro.adesso()):
        registro.registra_codice_persona(persona, "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(rapporto, persona, dal)
    registro.registra_codice(rapporto, "tipo_impiego", "1", dal, al)


def conguaglio_atteso(imponibile, operate, giorni, giorni_anno):
    automatica = (Decimal(600) * giorni / giorni_anno).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
    return max(Decimal(0), imposta_di(imponibile, 1) - automatica) - operate


def anno_con_servizio(registro, orologio, corpus, mesi, rapporto=R, ultimo=True, anno=2026, importo="1500"):
    """Un pagamento di 1500 il 27 di ognuno dei mesi; l'ultimo porta il conguaglio. Ritorna (fiscale, ritenute operate)."""
    operate = Decimal(0)
    for numero in mesi:
        orologio.vai(numero, 1, anno)
        righe = stipendio(registro, corpus, Mese(anno, numero), importo, rapporto)
        _, fiscale = paga(
            registro, orologio, corpus, righe, date(anno, numero, 27), rapporto, ultimo=ultimo and numero == mesi[-1]
        )
        operate += fiscale.ritenuta.valore
    return fiscale, operate


def test_il_conguaglio_rapporta_la_detrazione_automatica_ai_giorni_di_servizio(registro, orologio):
    corpus = corpus_prova()
    servizio(registro, R, date(2026, 7, 1))  # dal 1 luglio al 31 dicembre: 184 giorni su 365
    fiscale, operate = anno_con_servizio(registro, orologio, corpus, range(7, 13))
    assert fiscale.conguaglio.valore == conguaglio_atteso(Decimal(9000), operate, 184, 365)


def test_i_giorni_di_due_rapporti_si_contano_una_volta_sola(registro, orologio):
    corpus = corpus_prova()
    servizio(registro, R, date(2026, 3, 1), date(2026, 8, 31))
    servizio(registro, ALTRO, date(2026, 6, 1))  # sovrapposto a giugno-agosto: l'unione è dal 1 marzo, 306 giorni
    fiscale, operate = anno_con_servizio(registro, orologio, corpus, [3, 4, 5], ultimo=False, importo="5000")
    assert fiscale.conguaglio is None  # ALTRO ha ancora servizio: è una proiezione
    proiezione = fiscale.avvisi_di("proiezione_conguaglio")[0].valore
    assert proiezione == conguaglio_atteso(Decimal(15000), operate, 306, 365)


def test_i_giorni_dell_anno_sono_366_in_un_anno_bisestile(registro, orologio):
    corpus = corpus_prova()
    servizio(registro, R, date(2028, 1, 1))
    fiscale, operate = anno_con_servizio(registro, orologio, corpus, range(1, 13), anno=2028)
    # servizio tutto l'anno: giorni = giorni_anno = 366, detrazione automatica intera (600,00)
    assert fiscale.conguaglio.valore == conguaglio_atteso(Decimal(18000), operate, 366, 366)


def _senza_servizio(testo):
    """Il corpus di prova senza fatto di servizio: tolti anche le basi e i concorsi, che lo richiedono."""
    testo = testo.replace('[periodo_dichiarato]\nservizio = "tipo_impiego"\n', "")
    testo = re.sub(r"\[\[base\]\].*?riferimento = [^\n]*\n", "", testo, flags=re.DOTALL)
    return re.sub(r"\[\[concorso\]\].*?riferimento = [^\n]*\n", "", testo, flags=re.DOTALL)


def test_senza_fatto_di_servizio_nel_corpus_i_giorni_sono_quelli_dell_anno(registro, orologio):
    corpus = Corpus.da_toml(_senza_servizio(con_automatica(AUTOMATICA_PROVA)))
    assert corpus.fatto_servizio is None
    servizio(registro, R, date(2026, 7, 1))
    fiscale, operate = anno_con_servizio(registro, orologio, corpus, range(7, 13))
    assert fiscale.conguaglio.valore == conguaglio_atteso(Decimal(9000), operate, 365, 365)


# Avviso: il minimo di 1.380 euro per il tempo determinato non è applicato

def avvisi_td(fiscale):
    return fiscale.avvisi_di("tempo_determinato_sotto_soglia")


def test_avviso_per_il_tempo_determinato_sotto_i_15000_euro(registro, orologio):
    corpus = corpus_prova()
    if not registro.fatti_persona_noti(P, "codice_fiscale", registro.adesso()):
        registro.registra_codice_persona(P, "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(R, P, date(2026, 7, 1))
    registro.registra_codice(R, "tipo_impiego", "17", date(2026, 7, 1))
    fiscale, _ = anno_con_servizio(registro, orologio, corpus, range(7, 13))
    (avviso,) = avvisi_td(fiscale)
    assert (avviso.persona, avviso.anno, avviso.valore) == (P, 2026, Decimal(9000))


def test_nessun_avviso_per_il_tempo_determinato_da_15000_euro_in_su(registro, orologio):
    corpus = corpus_prova()
    if not registro.fatti_persona_noti(P, "codice_fiscale", registro.adesso()):
        registro.registra_codice_persona(P, "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(R, P, date(2026, 7, 1))
    registro.registra_codice(R, "tipo_impiego", "18", date(2026, 7, 1))
    fiscale, _ = anno_con_servizio(registro, orologio, corpus, range(7, 13), importo="2500")
    assert avvisi_td(fiscale) == ()


def test_nessun_avviso_per_il_tempo_indeterminato_sotto_i_15000_euro(registro, orologio):
    corpus = corpus_prova()
    servizio(registro, R, date(2026, 7, 1))
    fiscale, _ = anno_con_servizio(registro, orologio, corpus, range(7, 13))
    assert avvisi_td(fiscale) == ()


def test_avviso_anche_se_il_tempo_determinato_e_un_altro_rapporto_della_persona(registro, orologio):
    corpus = corpus_prova()
    servizio(registro, R, date(2026, 7, 1))
    registro.collega_rapporto(ALTRO, P, date(2026, 1, 1))
    registro.registra_codice(ALTRO, "tipo_impiego", "17", date(2026, 1, 1), date(2026, 2, 28))
    fiscale, _ = anno_con_servizio(registro, orologio, corpus, range(7, 13))
    assert len(avvisi_td(fiscale)) == 1


def test_niente_avviso_nella_proiezione_perche_l_imponibile_dell_anno_non_e_finale(registro, orologio):
    corpus = corpus_prova()
    registro.registra_codice_persona(P, "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(R, P, date(2026, 1, 1))
    registro.registra_codice(R, "tipo_impiego", "17", date(2026, 1, 1))
    fiscale, _ = anno_con_servizio(registro, orologio, corpus, [3], ultimo=False)
    assert avvisi_td(fiscale) == ()
