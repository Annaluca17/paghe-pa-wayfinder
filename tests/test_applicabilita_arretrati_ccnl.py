"""Due date per ogni importo del CCNL: decorrenza e applicabilità (ADR 0041, ticket #126).

Corpus fittizio: importi inventati, nessuna norma. Il tabellare nuovo decorre dal 01/01/2026 ma è applicabile dal
29/10/2026 (giorno dopo la firma, art. 2 c. 2 CCNL 28/10/2026); la vacanza contrattuale si azzera alla stessa data
(art. 35 c. 3: gli incrementi la comprendono).
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, TipoEsito, calcola, differenze, emetti_esito
from paghe.arretrati import arretrati_ccnl
from paghe.errori import ErroreCorpus, ParametroMancante

R = "RAPPORTO-1"
FIRMA_EFFETTI = date(2026, 10, 29)

CORPUS_CCNL = """
[periodo_dichiarato]
servizio = "tipo_impiego"
cessazione = "cessazione"

[[parametro]]
nome = "divisore_giornaliero"
[[parametro.vigenza]]
dal = 2025-01-01
valore = "26"
riferimento = "fittizio:divisore"

[[parametro]]
nome = "tab_mensile"
[[parametro.vigenza]]
dal = 2025-01-01
valore = "1000.00"
riferimento = "fittizio:tab-vecchia"
[[parametro.vigenza]]
dal = 2026-01-01
applicabile_dal = 2026-10-29
valore = "1100.00"
riferimento = "fittizio:tab-nuova"

[[parametro]]
nome = "vacanza_mensile"
[[parametro.vigenza]]
dal = 2025-01-01
valore = "20.00"
riferimento = "fittizio:vacanza"
[[parametro.vigenza]]
dal = 2026-01-01
applicabile_dal = 2026-10-29
valore = "0.00"
riferimento = "fittizio:vacanza-riassorbita"

[[regola]]
istituto = "tabellare"
versione = 1
dal = 2025-01-01
riferimento = "fittizio:art-tab"
formula = "parametro.tab_mensile"
maturazione = "giorni"
applica_se = "tipo_impiego"
conteggio = "lun_sab"
divisore = "divisore_giornaliero"
decimali = 2

[[regola]]
istituto = "vacanza"
versione = 1
dal = 2025-01-01
riferimento = "fittizio:art-vac"
formula = "parametro.vacanza_mensile"
maturazione = "giorni"
applica_se = "tipo_impiego"
conteggio = "lun_sab"
divisore = "divisore_giornaliero"
decimali = 2
"""


@pytest.fixture
def ccnl():
    return Corpus.da_toml(CORPUS_CCNL)


def servizio(registro, fine=None):
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 1, 1), fine)
    if fine is not None:
        registro.registra_codice(R, "cessazione", "1", fine + timedelta(days=1))


def per_istituto(importi):
    return {i.istituto: i.valore for i in importi}


def paga_mese(registro, corpus, orologio, mese, giorno_pagamento):
    """Il mese pagato come il motore lo calcola alla data di pagamento."""
    orologio.vai(giorno_pagamento.month, giorno_pagamento.day, giorno_pagamento.year)
    righe = calcola(registro, corpus, R, mese, pagamento=giorno_pagamento)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno_pagamento, righe)
    registro.registra_pagamento(R, esito.id, giorno_pagamento)
    orologio.avanza()
    return esito


# --- scelta della vigenza per data di pagamento ---


def test_pagamento_prima_della_firma_usa_il_tabellare_precedente_e_la_vacanza(registro, ccnl):
    servizio(registro)
    importi = per_istituto(calcola(registro, ccnl, R, Mese(2026, 10), pagamento=date(2026, 10, 27)))
    assert importi == {"tabellare": Decimal("1000.00"), "vacanza": Decimal("20.00")}


def test_pagamento_dal_giorno_dopo_la_firma_usa_il_nuovo_tabellare(registro, ccnl):
    servizio(registro)
    dopo = per_istituto(calcola(registro, ccnl, R, Mese(2026, 10), pagamento=FIRMA_EFFETTI))
    assert dopo == {"tabellare": Decimal("1100.00"), "vacanza": Decimal("0.00")}
    giorno_firma = per_istituto(calcola(registro, ccnl, R, Mese(2026, 10), pagamento=date(2026, 10, 28)))
    assert giorno_firma["tabellare"] == Decimal("1000.00")


def test_senza_data_di_pagamento_l_applicabilita_non_conta(registro, ccnl):
    servizio(registro)
    assert per_istituto(calcola(registro, ccnl, R, Mese(2026, 3)))["tabellare"] == Decimal("1100.00")


def test_senza_vigenza_applicabile_il_calcolo_si_ferma(registro):
    vecchia = '[[parametro.vigenza]]\ndal = 2025-01-01\nvalore = "1000.00"\nriferimento = "fittizio:tab-vecchia"\n'
    assert vecchia in CORPUS_CCNL
    corpus = Corpus.da_toml(CORPUS_CCNL.replace(vecchia, ""))
    servizio(registro)
    with pytest.raises(ParametroMancante):
        calcola(registro, corpus, R, Mese(2026, 3), pagamento=date(2026, 3, 27))


def test_nel_mese_della_firma_la_vigenza_segue_la_data_di_pagamento_non_il_giorno(registro, ccnl):
    """Le frazioni del mese non si dividono per una decorrenza non ancora applicabile."""
    servizio(registro)
    importi = calcola(registro, ccnl, R, Mese(2026, 10), pagamento=date(2026, 10, 27))
    assert len([i for i in importi if i.istituto == "tabellare"]) == 1


# --- convalida ---


def test_applicabilita_prima_della_decorrenza_e_rifiutata():
    errato = CORPUS_CCNL.replace("applicabile_dal = 2026-10-29", "applicabile_dal = 2025-12-31", 1)
    with pytest.raises(ErroreCorpus, match="applicabil"):
        Corpus.da_toml(errato)


def test_l_applicabilita_cambia_la_versione_del_corpus(ccnl):
    senza = Corpus.da_toml(CORPUS_CCNL.replace("applicabile_dal = 2026-10-29\n", ""))
    assert senza.versione != ccnl.versione


# --- arretrati automatici ---


def paga_gennaio_ottobre(registro, ccnl, orologio):
    esiti = []
    for numero in range(1, 11):
        esiti.append(paga_mese(registro, ccnl, orologio, Mese(2026, numero), date(2026, numero, 27)))
    return esiti


def test_arretrati_da_gennaio_alla_firma_al_netto_della_vacanza(registro, ccnl, orologio):
    servizio(registro)
    paga_gennaio_ottobre(registro, ccnl, orologio)
    arretrati = arretrati_ccnl(registro, ccnl, R, date(2026, 11, 27))

    assert [d.competenza for d in arretrati.differenze if d.istituto == "tabellare"] == [
        Mese(2026, n) for n in range(1, 11)
    ]
    assert arretrati.totale == Decimal("800.00")  # 10 mesi x (1100 - 1000 - 20)
    mese = [d for d in arretrati.differenze if d.competenza == Mese(2026, 5)]
    assert {d.istituto: d.valore for d in mese} == {"tabellare": Decimal("100.00"), "vacanza": Decimal("-20.00")}
    assert not arretrati.cessato


def test_arretrati_pagati_una_volta_sola(registro, ccnl, orologio):
    servizio(registro)
    paga_gennaio_ottobre(registro, ccnl, orologio)
    orologio.vai(11, 27)
    arretrati = arretrati_ccnl(registro, ccnl, R, date(2026, 11, 27))
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 11, 27), arretrati.importi())
    registro.registra_pagamento(R, esito.id, date(2026, 11, 27))
    orologio.avanza()
    assert arretrati_ccnl(registro, ccnl, R, date(2026, 12, 18)).differenze == ()


def test_nessun_arretrato_se_il_pagato_e_gia_col_nuovo_tabellare(registro, ccnl, orologio):
    servizio(registro)
    paga_mese(registro, ccnl, orologio, Mese(2026, 11), date(2026, 11, 27))
    assert arretrati_ccnl(registro, ccnl, R, date(2026, 11, 27)).differenze == ()


def test_i_mesi_mai_pagati_non_sono_arretrati(registro, ccnl, orologio):
    servizio(registro)
    paga_mese(registro, ccnl, orologio, Mese(2026, 9), date(2026, 9, 27))
    arretrati = arretrati_ccnl(registro, ccnl, R, date(2026, 11, 27))
    assert {d.competenza for d in arretrati.differenze} == {Mese(2026, 9)}


def test_prima_della_firma_non_ci_sono_arretrati(registro, ccnl, orologio):
    servizio(registro)
    paga_mese(registro, ccnl, orologio, Mese(2026, 9), date(2026, 9, 27))
    assert arretrati_ccnl(registro, ccnl, R, date(2026, 10, 27)).differenze == ()


def test_corpus_senza_applicabilita_non_ha_arretrati_automatici(registro, orologio):
    senza = Corpus.da_toml(CORPUS_CCNL.replace("applicabile_dal = 2026-10-29\n", ""))
    servizio(registro)
    assert arretrati_ccnl(registro, senza, R, date(2026, 11, 27)).differenze == ()


# --- cessati ---


def test_cessato_a_meta_anno_ha_gli_arretrati_in_un_pagamento_a_parte_e_la_segnalazione(registro, ccnl, orologio):
    servizio(registro, fine=date(2026, 6, 30))
    for numero in range(1, 7):
        paga_mese(registro, ccnl, orologio, Mese(2026, numero), date(2026, numero, 27))
    orologio.vai(11, 27)
    arretrati = arretrati_ccnl(registro, ccnl, R, date(2026, 11, 27))

    assert arretrati.totale == Decimal("480.00")  # sei mesi di servizio
    assert {d.competenza for d in arretrati.differenze} == {Mese(2026, n) for n in range(1, 7)}
    assert arretrati.cessato
    assert arretrati.cessazione == date(2026, 6, 30)
    assert arretrati.scaglionamenti == (date(2026, 1, 1),)
    assert arretrati.ricalcolo_fine_servizio
    assert arretrati.pagamento_a_parte


def test_in_servizio_non_segnala_la_fine_servizio(registro, ccnl, orologio):
    servizio(registro)
    paga_gennaio_ottobre(registro, ccnl, orologio)
    arretrati = arretrati_ccnl(registro, ccnl, R, date(2026, 11, 27))
    assert not arretrati.ricalcolo_fine_servizio
    assert not arretrati.pagamento_a_parte
    assert arretrati.cessazione is None


def test_gli_scaglionamenti_sono_solo_quelli_maturati_alla_cessazione(registro, orologio):
    """Art. 36 c. 2: per TFR e indennità di fine servizio contano le decorrenze fino alla cessazione."""
    corpus = Corpus.da_toml(
        CORPUS_CCNL
        + """
[[parametro]]
nome = "altro"
[[parametro.vigenza]]
dal = 2026-01-01
applicabile_dal = 2026-10-29
valore = "1.00"
riferimento = "fittizio:a"
[[parametro.vigenza]]
dal = 2026-09-01
applicabile_dal = 2026-10-29
valore = "2.00"
riferimento = "fittizio:b"
"""
    )
    servizio(registro, fine=date(2026, 6, 30))
    for numero in range(1, 7):
        paga_mese(registro, corpus, orologio, Mese(2026, numero), date(2026, numero, 27))
    arretrati = arretrati_ccnl(registro, corpus, R, date(2026, 11, 27))
    assert arretrati.scaglionamenti == (date(2026, 1, 1),)


# --- corpus reale ---


def test_il_corpus_reale_ha_il_tabellare_applicabile_dal_giorno_dopo_la_firma():
    from pathlib import Path

    reale = Corpus.carica(Path(__file__).parent.parent / "corpus" / "funzioni-locali-cpdel.toml", reale=True)
    parametro = reale.parametro("tabellare_annuo_funzionari")
    assert parametro.vigenza_per(Mese(2026, 3), date(2026, 10, 29)).valore == Decimal("26304.27")
    assert parametro.vigenza_per(Mese(2026, 3)).valore == Decimal("26304.27")
    with pytest.raises(ParametroMancante):  # il tabellare del CCNL 23/02/2026 non è nel corpus: da fornire con due fonti
        parametro.vigenza_per(Mese(2026, 3), date(2026, 10, 28))
    assert reale.decorrenze_con_applicabilita(date(2026, 11, 27)) == (date(2026, 1, 1),)
