"""Contributi del lavoratore che riducono l'imponibile fiscale (ticket #70, art. 51 c. 2 lett. a TUIR). Dati fittizi.

Numeri scelti per tornare a mano, sul corpus di test_fiscale (scaglioni 10% fino a 10000, 20% fino a 30000, 30% oltre,
ragguagliati al mese; nessuna detrazione senza dichiarazione del sostituto).
Uno stipendio mensile di 1500 con un contributo del lavoratore di 120:
  imponibile fiscale = 1500 - 120 = 1380; scaglioni mensili 833,33 e 2500;
  ritenuta = 0,10 * 833,33 + 0,20 * (1380 - 833,33) = 83,33 + 109,33 = 192,67 (senza deduzione: 216,67).
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, TipoEsito, attribuisci_reddito, calcola_fiscale, emetti_esito, imponibile_fiscale
from paghe.errori import ErroreCorpus

from test_fiscale import TESTO, assumi, paga, stipendio

CONTRIBUTO = """
[[regola]]
istituto = "contributo_lavoratore"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:contributo-lavoratore"
formula = "arrotonda(base.pens * parametro.aliquota_1, 2)"
maturazione = "periodo"
"""

DEDUZIONE = """
[[deduzione_fiscale]]
istituto = "contributo_lavoratore"
dal = 2020-01-01
riferimento = "fittizio:deduzione-contributo-lavoratore"
"""


# Dichiarazione dell'istituto nel corpus

def test_l_istituto_dichiara_che_l_importo_riduce_l_imponibile_fiscale_con_date_e_riferimento():
    corpus = Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-12-31"))
    dichiarazione = corpus.deduzione_fiscale("contributo_lavoratore", date(2026, 6, 1))
    assert (dichiarazione.istituto, dichiarazione.riferimento) == (
        "contributo_lavoratore",
        "fittizio:deduzione-contributo-lavoratore",
    )
    assert corpus.deduzione_fiscale("contributo_lavoratore", date(2027, 1, 1)) is None
    assert corpus.deduzione_fiscale("stipendio", date(2026, 6, 1)) is None


def test_la_deduzione_di_un_istituto_ignoto_e_rifiutata():
    with pytest.raises(ErroreCorpus, match="istituto ignoto"):
        Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace('"contributo_lavoratore"', '"contributo_inesistente"'))


def test_due_deduzioni_dello_stesso_istituto_non_si_sovrappongono():
    seconda = DEDUZIONE.replace("2020-01-01", "2026-01-01").replace("deduzione-contributo-lavoratore", "deduzione-bis")
    with pytest.raises(ErroreCorpus, match="sovrappost"):
        Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-06-30") + seconda)
    adiacenti = DEDUZIONE.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2025-12-31") + seconda
    corpus = Corpus.da_toml(TESTO + CONTRIBUTO + adiacenti)
    assert corpus.deduzione_fiscale("contributo_lavoratore", date(2026, 1, 1)).riferimento == "fittizio:deduzione-bis"


def test_la_versione_del_corpus_cambia_con_la_deduzione_e_resta_senza():
    senza = Corpus.da_toml(TESTO + CONTRIBUTO)
    con = Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE)
    altra = Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace("deduzione-contributo-lavoratore", "deduzione-altra"))
    assert len({senza.versione, con.versione, altra.versione}) == 3


def test_la_deduzione_senza_riferimento_e_rifiutata():
    with pytest.raises(ErroreCorpus, match="riferimento normativo obbligatorio"):
        Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace('riferimento = "fittizio:deduzione-contributo-lavoratore"', 'riferimento = ""'))


def test_il_corpus_reale_rifiuta_il_riferimento_fittizio_della_deduzione():
    from test_fiscale import CORPUS_REALE

    reale = Corpus.carica(CORPUS_REALE, reale=True)
    testo = CORPUS_REALE.read_text(encoding="utf-8") + DEDUZIONE.replace('"contributo_lavoratore"', f'"{reale.istituti()[0]}"')
    with pytest.raises(ErroreCorpus, match="Deduzione fiscale.*fittizio"):
        Corpus.da_toml(testo, reale=True)


# Effetto sulla ritenuta del pagamento

def contributo(riga, valore):
    """Un contributo del lavoratore sul pagamento, derivato dal pagato come quelli della denuncia."""
    derivazione = replace(riga.derivazione, istituto="contributo_lavoratore", maturazione="periodo")
    # Un contributo non ha categoria di reddito, anche se la riga da cui lo si ricava e' gia' attribuita (ADR 0037).
    return replace(riga, istituto="contributo_lavoratore", valore=Decimal(valore), derivazione=derivazione, categoria_reddito=None)


@pytest.fixture
def con_deduzione():
    return Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE)


def test_la_ritenuta_si_calcola_sull_imponibile_al_netto_dei_contributi_del_lavoratore(registro, con_deduzione, orologio):
    assumi(registro)
    giorno = date(2026, 6, 27)
    (riga,) = stipendio(registro, con_deduzione, Mese(2026, 6))
    attribuite = attribuisci_reddito(con_deduzione, [riga], giorno)
    fiscale = calcola_fiscale(registro, con_deduzione, "RAPPORTO-1", [*attribuite, contributo(riga, "120")], giorno)
    assert fiscale.ritenuta.valore == Decimal("192.67")


def test_senza_dichiarazione_i_contributi_non_riducono_l_imponibile(registro, orologio):
    corpus = Corpus.da_toml(TESTO + CONTRIBUTO)
    assumi(registro)
    giorno = date(2026, 6, 27)
    (riga,) = stipendio(registro, corpus, Mese(2026, 6))
    attribuite = attribuisci_reddito(corpus, [riga], giorno)
    fiscale = calcola_fiscale(registro, corpus, "RAPPORTO-1", [*attribuite, contributo(riga, "120")], giorno)
    assert fiscale.ritenuta.valore == Decimal("216.67")


def test_la_dichiarazione_vale_alla_data_di_pagamento(registro, orologio):
    corpus = Corpus.da_toml(TESTO + CONTRIBUTO + DEDUZIONE.replace("dal = 2020-01-01", "dal = 2026-07-01"))
    assumi(registro)
    giorno = date(2026, 6, 27)
    (riga,) = stipendio(registro, corpus, Mese(2026, 6))
    attribuite = attribuisci_reddito(corpus, [riga], giorno)
    fiscale = calcola_fiscale(registro, corpus, "RAPPORTO-1", [*attribuite, contributo(riga, "120")], giorno)
    assert fiscale.ritenuta.valore == Decimal("216.67")


def test_la_derivazione_della_ritenuta_porta_i_contributi_dedotti(registro, con_deduzione, orologio):
    assumi(registro)
    giorno = date(2026, 6, 27)
    (riga,) = stipendio(registro, con_deduzione, Mese(2026, 6))
    attribuite = attribuisci_reddito(con_deduzione, [riga], giorno)
    fiscale = calcola_fiscale(registro, con_deduzione, "RAPPORTO-1", [*attribuite, contributo(riga, "120")], giorno)
    assert [i.istituto for i in fiscale.ritenuta.derivazione.importi] == ["stipendio", "contributo_lavoratore"]


def paga_con_contributo(registro, orologio, corpus, righe, valore, giorno, ultimo=False):
    """Un pagamento col suo contributo del lavoratore: l'esito pagato li comprende entrambi, come la proposta."""
    orologio.vai(giorno.month, giorno.day, giorno.year)
    attribuite = attribuisci_reddito(corpus, righe, giorno)
    versati = [contributo(righe[0], valore)]
    fiscale = calcola_fiscale(registro, corpus, "RAPPORTO-1", [*attribuite, *versati], giorno, ultimo_dell_anno=ultimo)
    contenuto = [*attribuite, *versati, fiscale.ritenuta, *([fiscale.conguaglio] if fiscale.conguaglio else [])]
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, contenuto)
    registro.registra_pagamento("RAPPORTO-1", esito.id, giorno)
    orologio.avanza()
    return fiscale


def test_la_ritenuta_di_un_secondo_pagamento_del_mese_deduce_anche_i_contributi_gia_pagati(registro, con_deduzione, orologio):
    """Imponibile del mese 2000 - 160 = 1840: imposta 83,33 + 0,20 * (1840 - 833,33) = 284,67; già operati 192,67."""
    assumi(registro)
    primo = paga_con_contributo(
        registro, orologio, con_deduzione, stipendio(registro, con_deduzione, Mese(2026, 6)), "120", date(2026, 6, 20)
    )
    secondo = paga_con_contributo(
        registro, orologio, con_deduzione, stipendio(registro, con_deduzione, Mese(2026, 5), "500"), "40", date(2026, 6, 27)
    )
    assert (primo.ritenuta.valore, secondo.ritenuta.valore) == (Decimal("192.67"), Decimal("92.00"))


# Effetto sull'imponibile fiscale per persona e anno d'imposta

def test_l_imponibile_fiscale_dell_anno_e_al_netto_dei_contributi_del_lavoratore(registro, con_deduzione, orologio):
    assumi(registro)
    paga_con_contributo(
        registro, orologio, con_deduzione, stipendio(registro, con_deduzione, Mese(2026, 3)), "120", date(2026, 3, 27)
    )
    paga_con_contributo(
        registro, orologio, con_deduzione, stipendio(registro, con_deduzione, Mese(2026, 4), "1000"), "80", date(2026, 4, 27)
    )
    base = imponibile_fiscale(registro, "PERSONA-1", 2026, corpus=con_deduzione)
    assert base.valore == Decimal("2300")
    assert imponibile_fiscale(registro, "PERSONA-1", 2027, corpus=con_deduzione).valore == Decimal(0)


def test_senza_il_corpus_l_imponibile_fiscale_non_conosce_le_deduzioni(registro, con_deduzione, orologio):
    assumi(registro)
    paga_con_contributo(
        registro, orologio, con_deduzione, stipendio(registro, con_deduzione, Mese(2026, 3)), "120", date(2026, 3, 27)
    )
    assert imponibile_fiscale(registro, "PERSONA-1", 2026).valore == Decimal("1500")


# Effetto sul conguaglio e sulla proiezione

def test_il_conguaglio_dell_ultimo_pagamento_e_sull_imponibile_al_netto_dei_contributi(registro, con_deduzione, orologio):
    """Un solo pagamento nell'anno: 1500 - 120 = 1380 in un solo periodo.

    Imposta annua sotto il primo scaglione: 0,10 * 1380 = 138,00. La ritenuta mensile, ragguagliata, è 192,67:
    il conguaglio la riporta a 138,00, cioè 138,00 - 192,67 = -54,67.
    """
    assumi(registro)
    fiscale = paga_con_contributo(
        registro, orologio, con_deduzione, stipendio(registro, con_deduzione, Mese(2026, 6)), "120", date(2026, 6, 27), ultimo=True
    )
    assert fiscale.ritenuta.valore == Decimal("192.67")
    assert fiscale.conguaglio.valore == Decimal("-54.67")


def test_la_proiezione_del_conguaglio_e_sull_imponibile_al_netto_dei_contributi(registro, con_deduzione, orologio):
    assumi(registro)
    fiscale = paga_con_contributo(
        registro, orologio, con_deduzione, stipendio(registro, con_deduzione, Mese(2026, 6)), "120", date(2026, 6, 27)
    )
    (proiezione,) = fiscale.avvisi_di("proiezione_conguaglio")
    assert proiezione.valore == Decimal("-54.67")


# Riduzione del lordo TFR: e' retribuzione in meno, quindi reddito negativo (DPCM 20/12/1999 art. 1 c. 2-3; ADR 0037)

RIDUZIONE = """
[[regola]]
istituto = "riduzione_tfr"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:riduzione-tfr"
formula = "-arrotonda(importo.stipendio * parametro.aliquota_1, 2)"
maturazione = "periodo"
applica_se = "regime_tfr"
"""

REDDITO_RIDUZIONE = """
[[reddito]]
istituto = "riduzione_tfr"
categoria = "lavoro_dipendente"
dal = 2020-01-01
riferimento = "fittizio:reddito-riduzione-tfr"
"""


def riduzione_tfr(riga, valore="-30"):
    derivazione = replace(riga.derivazione, istituto="riduzione_tfr", maturazione="periodo")
    return replace(riga, istituto="riduzione_tfr", valore=Decimal(valore), derivazione=derivazione)


def test_la_riduzione_tfr_dichiarata_reddito_riduce_l_imponibile_della_ritenuta(registro, orologio):
    """1500 di stipendio e 30 di riduzione: imponibile 1470, ritenuta 83,33 + 0,20 * (1470 - 833,33) = 210,67."""
    corpus = Corpus.da_toml(TESTO + RIDUZIONE + REDDITO_RIDUZIONE)
    assumi(registro)
    giorno = date(2026, 6, 27)
    (riga,) = stipendio(registro, corpus, Mese(2026, 6))
    attribuite = attribuisci_reddito(corpus, [riga, riduzione_tfr(riga)], giorno)
    riduzione = next(r for r in attribuite if r.istituto == "riduzione_tfr")
    assert (riduzione.categoria_reddito, riduzione.anno_imposta) == (riga.categoria_reddito or "lavoro_dipendente", 2026)
    fiscale = calcola_fiscale(registro, corpus, "RAPPORTO-1", attribuite, giorno)
    assert fiscale.ritenuta.valore == Decimal("210.67")


def test_la_riduzione_tfr_pagata_riduce_l_imponibile_fiscale_dell_anno(registro, orologio):
    corpus = Corpus.da_toml(TESTO + RIDUZIONE + REDDITO_RIDUZIONE)
    assumi(registro)
    (riga,) = stipendio(registro, corpus, Mese(2026, 6))
    paga(registro, orologio, corpus, [riga, riduzione_tfr(riga)], date(2026, 6, 27))
    assert imponibile_fiscale(registro, "PERSONA-1", 2026, corpus=corpus).valore == Decimal("1470")


def test_un_importo_derivato_senza_dichiarazione_di_reddito_resta_fuori_dall_imponibile(registro, orologio):
    """Senza la dichiarazione nel corpus un importo sul periodo non e' reddito: la ritenuta resta 216,67."""
    corpus = Corpus.da_toml(TESTO + RIDUZIONE)
    assumi(registro)
    giorno = date(2026, 6, 27)
    (riga,) = stipendio(registro, corpus, Mese(2026, 6))
    attribuite = attribuisci_reddito(corpus, [riga, riduzione_tfr(riga)], giorno)
    assert next(r for r in attribuite if r.istituto == "riduzione_tfr").categoria_reddito is None
    assert calcola_fiscale(registro, corpus, "RAPPORTO-1", attribuite, giorno).ritenuta.valore == Decimal("216.67")
