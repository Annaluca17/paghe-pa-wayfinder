"""Blocco dei pagamenti 48-bis: verifica prima di pagare e somma sospesa (ADR 0034). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.errori import ErroreCorpus, ErroreRegistro
from paghe import TipoEsito
from paghe.blocco_pagamenti import (
    StatoAccantonamento,
    importo_sospeso,
    registra_debito_estinto,
    registra_esito_verifica,
    registra_ordine_versamento,
    registra_richiesta_verifica,
    stato_accantonamento,
)
from paghe.proposta import emetti_versione, registra_versamento_eseguito

from materiale_48bis import CORPUS_48BIS, VALUTA, corpus_48bis
from materiale_proposta import P, P2, R, R2, assumi, paga, stipendio

FEB = Mese(2026, 2)
ADATTATORE = "adattatore-prova"


@pytest.fixture
def corpus_48():
    return corpus_48bis()


# 1. Soglie datate nel corpus, per titolo e periodo

def test_la_soglia_del_dipendente_e_2500_dal_2026_con_la_norma_di_ogni_periodo():
    corpus = corpus_48bis()
    nel_2026 = corpus.soglia_verifica("lavoro_dipendente", date(2026, 6, 30))
    nel_2027 = corpus.soglia_verifica("lavoro_dipendente", date(2027, 1, 1))
    assert (nel_2026.soglia, nel_2026.riferimento) == (Decimal("2500"), "fittizio:48bis-c1bis")
    assert (nel_2027.soglia, nel_2027.riferimento) == (Decimal("2500"), "fittizio:art-144-c2-3")


def test_gli_altri_titoli_hanno_5000_e_il_dipendente_prima_del_2026_nessuna_verifica():
    corpus = corpus_48bis()
    assert corpus.soglia_verifica("carica_elettiva", date(2026, 6, 30)).soglia == Decimal("5000")
    assert corpus.soglia_verifica("lavoro_dipendente", date(2025, 12, 31)).soglia is None


def test_due_soglie_dello_stesso_titolo_con_vigenze_sovrapposte_sono_rifiutate():
    doppia = CORPUS_48BIS + """
[[soglia_verifica]]
categoria = "lavoro_dipendente"
soglia = "3000"
dal = 2026-06-01
riferimento = "fittizio:soglia-doppia"
"""
    with pytest.raises(ErroreCorpus, match="vigenze sovrapposte"):
        Corpus.da_toml(doppia)


# 2. Netto per la soglia, sotto o uguale: nessun effetto

def test_un_netto_sotto_la_soglia_non_cambia_la_versione(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, stipendio(registro, corpus, FEB, "3000"))
    assert versione.fermi == ()
    assert [(n.rapporto, n.netto) for n in versione.netti] == [(R, Decimal("2360.00"))]
    assert {riga.istituto for riga in versione.righe_del_rapporto(R)} == {
        "stipendio", "contributo_lavoratore", "contributo_ente", "ritenuta_irpef",
    }


def test_un_netto_uguale_alla_soglia_non_cambia_la_versione(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, stipendio(registro, corpus, FEB, "3194.45"))
    assert versione.fermi == ()
    assert [(n.rapporto, n.netto) for n in versione.netti] == [(R, Decimal("2500.00"))]


# 3. Sopra soglia senza esito: il rapporto e' fermo, gli altri proseguono

def test_un_netto_sopra_la_soglia_senza_esito_ferma_il_rapporto_e_nomina_la_verifica_e_il_netto(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus, FEB, "3200") + stipendio(registro, corpus, FEB, "1500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert versione.rapporti == (R2,)
    (fermo,) = versione.fermi
    assert fermo.rapporto == R
    assert "verifica 48-bis mancante" in fermo.motivo and "2504.00" in fermo.motivo


# 4. Esito non inadempiente: si paga tutto

def richiedi(registro, persona=P, netto="2504.00", pagamento=VALUTA, data=date(2026, 2, 16), chiave="ric-1"):
    return registra_richiesta_verifica(registro, chiave, ADATTATORE, persona, data, Decimal(netto), pagamento)


def test_con_l_esito_non_inadempiente_si_paga_tutto_il_netto(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    importi = stipendio(registro, corpus, FEB, "3200")
    orologio.vai(2, 17)
    richiedi(registro)
    registra_esito_verifica(registro, "esi-1", ADATTATORE, "ric-1", date(2026, 2, 18), "non_inadempiente")
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert versione.fermi == ()
    assert [(n.rapporto, n.netto) for n in versione.netti] == [(R, Decimal("2504.00"))]
    assert "somma_sospesa_48bis" not in {riga.istituto for riga in versione.righe}


def test_la_richiesta_vale_per_il_netto_e_il_pagamento_comunicati(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    importi = stipendio(registro, corpus, FEB, "3200")
    orologio.vai(2, 17)
    richiedi(registro, netto="2500.00")  # un altro netto: non e' la verifica di questo pagamento
    registra_esito_verifica(registro, "esi-1", ADATTATORE, "ric-1", date(2026, 2, 18), "non_inadempiente")
    orologio.vai(2, 20)
    assumi(registro, R2, P2)
    versione = emetti_versione(registro, corpus, VALUTA, importi + stipendio(registro, corpus, FEB, "1500", R2))
    assert [f.rapporto for f in versione.fermi] == [R]


# 5. Richiesta senza risposta oltre 5 giorni feriali: come non inadempiente

def versione_di(registro, corpus, orologio, valuta, mese, importo="3200"):
    importi = stipendio(registro, corpus, mese, importo)
    orologio.vai(valuta.month, valuta.day - 1 if valuta.day > 1 else 1, valuta.year)
    return emetti_versione(registro, corpus, valuta, importi)


def test_senza_risposta_oltre_i_5_giorni_feriali_si_paga_tutto(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    orologio.vai(2, 16)
    richiedi(registro, data=date(2026, 2, 16))  # lunedi: i 5 giorni feriali scadono sabato 21
    versione = versione_di(registro, corpus, orologio, VALUTA, FEB)
    assert versione.fermi == ()
    assert [(n.rapporto, n.netto) for n in versione.netti] == [(R, Decimal("2504.00"))]


def test_entro_i_5_giorni_feriali_il_rapporto_resta_fermo(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    orologio.vai(2, 25)
    richiedi(registro, data=date(2026, 2, 25))  # mercoledi: i 5 giorni feriali scadono martedi 3 marzo
    importi = stipendio(registro, corpus, FEB, "3200")
    with pytest.raises(ErroreRegistro, match="verifica 48-bis mancante"):
        emetti_versione(registro, corpus, VALUTA, importi)


def test_i_festivi_del_calendario_non_sono_giorni_feriali(registro, orologio):
    corpus = corpus_48bis()
    marzo = Mese(2026, 3)
    assumi(registro)
    orologio.vai(3, 13)
    richiedi(registro, pagamento=date(2026, 3, 20), data=date(2026, 3, 13), chiave="ric-1")
    importi = stipendio(registro, corpus, marzo, "3200")
    # venerdi 13: sabato 14, lunedi 16, martedi 17, mercoledi 18, e' festivo giovedi 19, quindi venerdi 20
    with pytest.raises(ErroreRegistro, match="verifica 48-bis mancante"):
        emetti_versione(registro, corpus, date(2026, 3, 20), importi)
    registra_richiesta_verifica(registro, "ric-2", ADATTATORE, P, date(2026, 3, 13), Decimal("2504.00"), date(2026, 3, 23))
    versione = emetti_versione(registro, corpus, date(2026, 3, 23), importi)
    assert versione.fermi == ()


# 6. Esito inadempiente: la somma sospesa

NETTO_4000 = Decimal("3080.00")  # stipendio 4000: la fascia 1/7 sul netto da 3080 e' 440,00


def inadempiente(registro, debito, netto="3080.00", data_esito=date(2026, 2, 18)):
    richiedi(registro, netto=netto)
    registra_esito_verifica(registro, "esi-1", ADATTATORE, "ric-1", data_esito, "inadempiente", Decimal(debito))


def test_con_l_esito_inadempiente_la_versione_porta_la_somma_sospesa_senza_destinatario(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    importi = stipendio(registro, corpus, FEB, "4000")
    orologio.vai(2, 17)
    inadempiente(registro, "1000")
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    righe = {riga.istituto: riga for riga in versione.righe_del_rapporto(R)}
    sospesa = righe["somma_sospesa_48bis"]
    assert sospesa.importo.valore == Decimal("440.00")  # min(debito 1000; 3080 / 7; meta' 1540)
    assert (sospesa.natura, sospesa.effetto, sospesa.destinatario, sospesa.canale) == (
        "somma_sospesa_48bis", "meno", "ente", "accantonamento",
    )
    assert [(n.rapporto, n.netto) for n in versione.netti] == [(R, Decimal("2640.00"))]
    # ritenute e contributi non cambiano: la somma sospesa resta reddito del pagamento
    assert righe["ritenuta_irpef"].importo.valore == Decimal("600.00")
    assert righe["contributo_lavoratore"].importo.valore == Decimal("320.00")


def test_il_debito_minore_della_fascia_e_la_somma_sospesa(registro, orologio):
    corpus = corpus_48bis()
    assumi(registro)
    importi = stipendio(registro, corpus, FEB, "4000")
    orologio.vai(2, 17)
    inadempiente(registro, "200")
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert versione.netti[0].netto == NETTO_4000 - Decimal("200")


def test_la_fascia_si_sceglie_sul_netto_e_si_applica_a_tutto_il_netto():
    regola = corpus_48bis().regola_somma_sospesa(VALUTA)
    assert regola.quota_sul_netto(Decimal("2500")) == Decimal("250.00")  # 1/10
    assert regola.quota_sul_netto(Decimal("2500.01")) == Decimal("357.14")  # 1/7 di tutto il netto
    assert regola.quota_sul_netto(Decimal("5000")) == Decimal("714.28")
    assert regola.quota_sul_netto(Decimal("5240")) == Decimal("1048.00")  # 1/5


def test_la_somma_sospesa_cede_alle_trattenute_a_terzi_dello_stesso_pagamento():
    regola = corpus_48bis().regola_somma_sospesa(VALUTA)
    # netto 3000: fascia 1/7 = 428,57; meta' del netto 1500 meno 1200 di trattenute a terzi = 300
    assert importo_sospeso(regola, Decimal("3000"), Decimal("1200"), Decimal("5000")) == Decimal("300.00")
    # trattenute a terzi oltre la meta': niente da sospendere
    assert importo_sospeso(regola, Decimal("3000"), Decimal("1600"), Decimal("5000")) == Decimal(0)
    # il debito e' il minore dei tre
    assert importo_sospeso(regola, Decimal("3000"), Decimal("0"), Decimal("100")) == Decimal("100.00")
    assert importo_sospeso(regola, Decimal("3000"), Decimal("0"), Decimal("5000")) == Decimal("428.57")


# 7. Chiusura dell'accantonamento: ordine di versamento, debito pagato o ridotto, 60 giorni

MARZO = Mese(2026, 3)
APRILE = Mese(2026, 4)
VALUTA_MARZO = date(2026, 3, 27)
VALUTA_APRILE = date(2026, 4, 27)


def accantonata(registro, corpus, orologio):
    """Stipendio da 4000 pagato il 27/02 con esito inadempiente del 18/02 (debito 1000): sospesi 440,00."""
    assumi(registro)
    importi = stipendio(registro, corpus, FEB, "4000")
    orologio.vai(2, 17)
    inadempiente(registro, "1000")
    versione = paga(registro, corpus, orologio, importi, VALUTA, "pag-feb")
    return versione, registro.evento("pag-feb").esito_id


def versione_del_mese(registro, corpus, orologio, mese, valuta):
    importi = stipendio(registro, corpus, mese, "1500")
    orologio.vai(valuta.month, valuta.day - 1, valuta.year)
    return emetti_versione(registro, corpus, valuta, importi)


def test_dopo_il_pagamento_la_somma_e_accantonata_e_non_rientra_nel_mese_dopo(registro, corpus_48, orologio):
    corpus = corpus_48
    _, esito = accantonata(registro, corpus, orologio)
    accantonamento = stato_accantonamento(registro, corpus, esito, R, VALUTA_MARZO)
    assert (accantonamento.stato, accantonamento.importo, accantonamento.pagabile) == (
        StatoAccantonamento.SOSPESA, Decimal("440.00"), Decimal(0),
    )
    versione = versione_del_mese(registro, corpus, orologio, MARZO, VALUTA_MARZO)
    assert "rilascio_somma_sospesa_48bis" not in {riga.istituto for riga in versione.righe}


def test_l_ordine_di_versamento_fa_della_somma_una_trattenuta_a_terzi_versata_col_bonifico(registro, corpus_48, orologio):
    corpus = corpus_48
    versione, esito = accantonata(registro, corpus, orologio)
    orologio.vai(3, 5)
    registra_ordine_versamento(registro, "ord-1", ADATTATORE, esito, R, date(2026, 3, 4))
    assert stato_accantonamento(registro, corpus, esito, R, VALUTA_MARZO).stato is StatoAccantonamento.DA_VERSARE
    sospesa = next(r for r in versione.righe_del_rapporto(R) if r.istituto == "somma_sospesa_48bis")
    orologio.vai(3, 10)
    versato = registra_versamento_eseguito(
        registro, "ver-1", ADATTATORE, "bonifico-1", date(2026, 3, 10), [versione.riferimento(sospesa)], "bonifico", "bonifico"
    )
    assert versato.tipo is TipoEsito.VERSATO and [r.valore for r in versato.righe] == [Decimal("440.00")]
    assert stato_accantonamento(registro, corpus, esito, R, VALUTA_APRILE).stato is StatoAccantonamento.VERSATA
    successiva = versione_del_mese(registro, corpus, orologio, MARZO, VALUTA_MARZO)
    assert "rilascio_somma_sospesa_48bis" not in {riga.istituto for riga in successiva.righe}


def test_senza_l_ordine_la_somma_sospesa_non_si_versa_ad_ader(registro, corpus_48, orologio):
    corpus = corpus_48
    versione, _ = accantonata(registro, corpus, orologio)
    sospesa = next(r for r in versione.righe_del_rapporto(R) if r.istituto == "somma_sospesa_48bis")
    with pytest.raises(ErroreRegistro, match="ordine di versamento"):
        registra_versamento_eseguito(
            registro, "ver-1", ADATTATORE, "bonifico-1", date(2026, 3, 10), [versione.riferimento(sospesa)], "bonifico", "bonifico"
        )


def test_il_debito_pagato_o_ridotto_rende_pagabile_l_importo_indicato_nel_primo_pagamento_utile(registro, corpus_48, orologio):
    corpus = corpus_48
    _, esito = accantonata(registro, corpus, orologio)
    orologio.vai(3, 5)
    registra_debito_estinto(registro, "est-1", ADATTATORE, esito, R, date(2026, 3, 4), Decimal("300"))
    accantonamento = stato_accantonamento(registro, corpus, esito, R, VALUTA_MARZO)
    assert (accantonamento.stato, accantonamento.pagabile) == (StatoAccantonamento.PAGABILE, Decimal("300"))
    versione = versione_del_mese(registro, corpus, orologio, MARZO, VALUTA_MARZO)
    righe = {riga.istituto: riga for riga in versione.righe_del_rapporto(R)}
    rilascio = righe["rilascio_somma_sospesa_48bis"]
    assert rilascio.importo.valore == Decimal("300")
    assert (rilascio.effetto, rilascio.destinatario, rilascio.canale) == ("piu", "beneficiario", "accredito")
    assert rilascio.importo.esiti_confrontati == (esito,)
    # senza nuova tassazione: la ritenuta e' quella dello stipendio di 1500, e il netto cresce dell'importo rilasciato
    assert righe["ritenuta_irpef"].importo.valore == Decimal("100.00")
    assert versione.netti[0].netto == Decimal("1280.00") + Decimal("300")


def test_la_somma_rilasciata_entra_in_un_solo_pagamento(registro, corpus_48, orologio):
    corpus = corpus_48
    _, esito = accantonata(registro, corpus, orologio)
    orologio.vai(3, 5)
    registra_debito_estinto(registro, "est-1", ADATTATORE, esito, R, date(2026, 3, 4), Decimal("300"))
    importi = stipendio(registro, corpus, MARZO, "1500")
    paga(registro, corpus, orologio, importi, VALUTA_MARZO, "pag-mar")
    assert stato_accantonamento(registro, corpus, esito, R, VALUTA_APRILE).stato is StatoAccantonamento.RILASCIATA
    aprile = versione_del_mese(registro, corpus, orologio, APRILE, VALUTA_APRILE)
    assert "rilascio_somma_sospesa_48bis" not in {riga.istituto for riga in aprile.righe}


def test_dopo_60_giorni_dalla_comunicazione_senza_ordine_la_somma_torna_pagabile(registro, corpus_48, orologio):
    corpus = corpus_48
    _, esito = accantonata(registro, corpus, orologio)  # esito comunicato il 18/02: 60 giorni fino al 19/04
    assert stato_accantonamento(registro, corpus, esito, R, date(2026, 4, 19)).stato is StatoAccantonamento.SOSPESA
    dopo = stato_accantonamento(registro, corpus, esito, R, date(2026, 4, 20))
    assert (dopo.stato, dopo.pagabile) == (StatoAccantonamento.PAGABILE, Decimal("440.00"))
    marzo = versione_del_mese(registro, corpus, orologio, MARZO, VALUTA_MARZO)
    assert "rilascio_somma_sospesa_48bis" not in {riga.istituto for riga in marzo.righe}
    aprile = versione_del_mese(registro, corpus, orologio, APRILE, VALUTA_APRILE)
    (rilascio,) = [r for r in aprile.righe_del_rapporto(R) if r.istituto == "rilascio_somma_sospesa_48bis"]
    assert rilascio.importo.valore == Decimal("440.00")


def test_con_l_ordine_i_60_giorni_non_rendono_pagabile_la_somma(registro, corpus_48, orologio):
    corpus = corpus_48
    _, esito = accantonata(registro, corpus, orologio)
    orologio.vai(3, 5)
    registra_ordine_versamento(registro, "ord-1", ADATTATORE, esito, R, date(2026, 3, 4))
    assert stato_accantonamento(registro, corpus, esito, R, VALUTA_APRILE).stato is StatoAccantonamento.DA_VERSARE
    aprile = versione_del_mese(registro, corpus, orologio, APRILE, VALUTA_APRILE)
    assert "rilascio_somma_sospesa_48bis" not in {riga.istituto for riga in aprile.righe}


def test_un_debito_estinto_oltre_la_somma_sospesa_o_su_un_altro_rapporto_e_rifiutato(registro, corpus_48, orologio):
    corpus = corpus_48
    _, esito = accantonata(registro, corpus, orologio)
    with pytest.raises(ErroreRegistro, match="somma sospesa"):
        registra_debito_estinto(registro, "est-1", ADATTATORE, esito, R, date(2026, 3, 4), Decimal("500"))
    with pytest.raises(ErroreRegistro, match="somma sospesa"):
        registra_ordine_versamento(registro, "ord-1", ADATTATORE, esito, R2, date(2026, 3, 4))


# Corpus: convalida e impronta

def test_le_fasce_della_somma_sospesa_devono_chiudere_senza_limite():
    senza_chiusura = CORPUS_48BIS.replace('    { divisore = "5" },\n', '')
    with pytest.raises(ErroreCorpus, match="ultima fascia"):
        Corpus.da_toml(senza_chiusura)


def test_le_regole_del_blocco_entrano_nell_impronta_solo_se_presenti():
    from materiale_proposta import CORPUS_PROPOSTA

    base = Corpus.da_toml(CORPUS_PROPOSTA).versione
    assert corpus_48bis().versione != base
    assert Corpus.da_toml(CORPUS_PROPOSTA + "\n").versione == base
