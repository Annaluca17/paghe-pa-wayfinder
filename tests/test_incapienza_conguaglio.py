"""Incapienza del conguaglio IRPEF e richiesta di differimento (ticket #99, ADR 0034). Dati fittizi, numeri in materiale_incapienza."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, TipoEsito, calcola
from paghe import conguaglio_per_differenza
from paghe.errori import ErroreRegistro
from paghe.proposta import emetti_versione

from materiale_incapienza import (
    corpus_incapienza,
    fino_a_dicembre,
    netto_di,
    paga_dicembre,
    paga_mese,
    righe_del,
    toml_incapienza,
    versione_di_dicembre,
)
from materiale_proposta import P, R, paga, per_istituto, stipendio

D = Decimal


def richiesta(registro):
    registro.registra_richiesta_differimento(P, date(2026, 1, 1))


def non_trattenuti(importo):
    return [i for i in importo.derivazione.importi if i.derivazione.maturazione == "non_trattenuto"]


# Senza la richiesta di differimento

def test_il_conguaglio_si_trattiene_fino_a_netto_zero_e_il_resto_e_non_trattenuto(registro, orologio):
    versione = versione_di_dicembre(registro, orologio, corpus_incapienza())
    assert versione.fermi == ()
    conguaglio = per_istituto(versione.righe)["conguaglio_irpef"].importo
    assert (conguaglio.valore, netto_di(versione)) == (D("236.00"), D("0.00"))
    (non_trattenuto,) = non_trattenuti(conguaglio)
    assert (non_trattenuto.istituto, non_trattenuto.valore, non_trattenuto.anno_imposta) == (
        "conguaglio_irpef_non_trattenuto", D("144.00"), 2026
    )
    assert "senza richiesta di differimento" in non_trattenuto.derivazione.formula
    assert "oltre la capienza" in conguaglio.derivazione.formula


def test_un_netto_negativo_che_non_dipende_dal_conguaglio_resta_un_fermo(registro, orologio):
    corpus = corpus_incapienza(contributo="0.95")  # il netto di dicembre senza il conguaglio: 300 - 285 - 40 = -25
    with pytest.raises(ErroreRegistro, match="netto negativo di -"):
        versione_di_dicembre(registro, orologio, corpus)


def test_un_conguaglio_che_ci_sta_non_e_toccato(registro, orologio):
    versione = versione_di_dicembre(registro, orologio, corpus_incapienza(), dicembre="1500")
    conguaglio = per_istituto(versione.righe)["conguaglio_irpef"].importo
    assert non_trattenuti(conguaglio) == [] and netto_di(versione) > 0


# Con la richiesta di differimento

def test_con_la_richiesta_di_differimento_il_resto_e_differito_e_non_e_un_fatto(registro, orologio):
    corpus = corpus_incapienza()
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus)
    esito = registro.esiti(TipoEsito.PAGATO, orologio())[-1]
    conguaglio = next(riga for riga in esito.righe if riga.istituto == "conguaglio_irpef")
    assert conguaglio.valore == D("236.00")
    (decisione,) = [i for i in conguaglio.derivazione.importi if i.derivazione.maturazione == "resto_da_differire"]
    assert (decisione.istituto, decisione.valore) == ("conguaglio_irpef_resto", D("144.00"))
    assert non_trattenuti(conguaglio) == []
    assert [f.tipo for f in decisione.derivazione.fatti] == ["richiesta_differimento"]
    assert [f.tipo for f in conguaglio.derivazione.fatti if f.tipo == "richiesta_differimento"] == ["richiesta_differimento"]


def test_il_pagamento_successivo_trattiene_il_resto_e_l_interesse_semplice_di_un_mese(registro, orologio):
    corpus = corpus_incapienza()
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus)
    versione = paga_mese(registro, orologio, corpus, 2027, 1)
    (resto,) = righe_del(versione, "conguaglio_irpef_resto")
    (interesse,) = righe_del(versione, "conguaglio_irpef_interesse")
    assert (resto.valore, interesse.valore) == (D("144.00"), D("0.72"))  # 144,00 * 0,005 * 1 mese
    assert netto_di(versione) == D("955.28")  # 1500 - 120 - 280 - 144 - 0,72
    assert "interesse semplice" in interesse.derivazione.formula and "0.005" in interesse.derivazione.formula
    assert [(p.nome, p.valore, p.riferimento) for p in interesse.derivazione.parametri] == [
        ("interesse_differimento_mensile", D("0.005"), "fittizio:interesse-differimento")
    ]
    assert "fittizio:interesse-differimento" in interesse.derivazione.riferimento
    assert interesse.istituto != resto.istituto  # l'interesse è un importo a sé
    assert resto.anno_imposta == interesse.anno_imposta == 2026


def test_se_il_netto_non_basta_il_resto_resta_aperto_e_l_interesse_si_trattiene_per_primo(registro, orologio):
    corpus = corpus_incapienza()
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus)
    gennaio = paga_mese(registro, orologio, corpus, 2027, 1, importo="100")
    # netto 100 - 8 = 92,00: interesse 0,72, resto 91,28; restano aperti 52,72
    assert netto_di(gennaio) == D("0.00")
    assert righe_del(gennaio, "conguaglio_irpef_interesse")[0].valore == D("0.72")
    assert righe_del(gennaio, "conguaglio_irpef_resto")[0].valore == D("91.28")
    febbraio = paga_mese(registro, orologio, corpus, 2027, 2)
    # dal movimento di gennaio: 52,72 * 0,005 * 1 = 0,2636, cioè 0,26
    assert righe_del(febbraio, "conguaglio_irpef_interesse")[0].valore == D("0.26")
    assert righe_del(febbraio, "conguaglio_irpef_resto")[0].valore == D("52.72")
    marzo = paga_mese(registro, orologio, corpus, 2027, 3)
    assert righe_del(marzo, "conguaglio_irpef_resto") == [] and righe_del(marzo, "conguaglio_irpef_interesse") == []


def test_senza_il_parametro_dell_interesse_il_rapporto_col_resto_aperto_e_fermo(registro, orologio):
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus_incapienza())
    senza = corpus_incapienza(con_interesse=False)
    orologio.vai(1, 20, 2027)
    importi = stipendio(registro, senza, Mese(2027, 1), "1500")
    with pytest.raises(ErroreRegistro, match="interesse_differimento_mensile"):
        emetti_versione(registro, senza, date(2027, 1, 27), importi)


# Fine del differimento

def test_all_ultimo_pagamento_di_dicembre_il_resto_ancora_aperto_diventa_non_trattenuto(registro, orologio):
    corpus = corpus_incapienza()
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus)
    paga_mese(registro, orologio, corpus, 2027, 1, importo="20")  # netto 18,40: interesse 0,72, resto 17,68, aperti 126,32
    dicembre = paga_mese(registro, orologio, corpus, 2027, 12, giorno=18, importo="20", ultimo=date(2027, 12, 18))
    (interesse,) = righe_del(dicembre, "conguaglio_irpef_interesse")
    (resto,) = righe_del(dicembre, "conguaglio_irpef_resto")
    assert interesse.valore == D("6.95")  # 126,32 * 0,005 * 11 mesi
    assert resto.valore == D("11.45")  # il netto di 18,40 meno l'interesse
    (non_trattenuto,) = non_trattenuti(resto)
    assert (non_trattenuto.istituto, non_trattenuto.valore, non_trattenuto.anno_imposta) == (
        "conguaglio_irpef_non_trattenuto", D("114.87"), 2026
    )
    gennaio = paga_mese(registro, orologio, corpus, 2028, 1)  # chiuso: nessun pagamento successivo lo riprende
    assert righe_del(gennaio, "conguaglio_irpef_resto") == []


def test_prima_di_dicembre_il_resto_aperto_non_diventa_non_trattenuto(registro, orologio):
    corpus = corpus_incapienza()
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus)
    gennaio = paga_mese(registro, orologio, corpus, 2027, 1, importo="20")
    (resto,) = righe_del(gennaio, "conguaglio_irpef_resto")
    assert non_trattenuti(resto) == []


def test_alla_cessazione_il_resto_aperto_diventa_non_trattenuto(registro, orologio):
    corpus = corpus_incapienza()
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus, servizio_fino_al=date(2027, 1, 20))
    registro.registra_fatto(R, "mensile", "20", date(2027, 1, 1), date(2027, 1, 20))
    orologio.vai(1, 20, 2027)
    importi = [i for i in calcola(registro, corpus, R, Mese(2027, 1)) if i.istituto == "stipendio"]
    gennaio = paga(registro, corpus, orologio, importi, date(2027, 1, 27), "pag-cessazione")
    (resto,) = righe_del(gennaio, "conguaglio_irpef_resto")
    assert resto.valore == D("17.68")
    (non_trattenuto,) = non_trattenuti(resto)
    assert non_trattenuto.valore == D("126.32")


def test_se_il_conguaglio_e_alla_cessazione_la_richiesta_non_differisce_nulla(registro, orologio):
    corpus = corpus_incapienza()
    richiesta(registro)
    versione = versione_di_dicembre(registro, orologio, corpus, dicembre="100", servizio_fino_al=date(2026, 12, 18))
    conguaglio = per_istituto(versione.righe)["conguaglio_irpef"].importo
    assert [i.derivazione.maturazione for i in conguaglio.derivazione.importi if i.istituto.startswith("conguaglio_irpef_")] == [
        "non_trattenuto"
    ]
    assert "alla cessazione" in non_trattenuti(conguaglio)[0].derivazione.formula


def test_la_richiesta_vale_alla_data_del_conguaglio(registro, orologio):
    registro.registra_richiesta_differimento(P, date(2026, 1, 1), date(2026, 11, 30))  # scaduta prima del conguaglio
    versione = versione_di_dicembre(registro, orologio, corpus_incapienza())
    conguaglio = per_istituto(versione.righe)["conguaglio_irpef"].importo
    assert len(non_trattenuti(conguaglio)) == 1


# Il conguaglio per differenza non riprende ciò che l'incapienza ha già deciso

def test_il_non_trattenuto_non_e_ripreso_da_un_conguaglio_per_differenza(registro, orologio):
    corpus = corpus_incapienza()
    paga_dicembre(registro, orologio, corpus)
    assert conguaglio_per_differenza(registro, corpus, R, 2026, date(2027, 1, 20)) is None


def test_il_resto_differito_non_e_ripreso_da_un_conguaglio_per_differenza(registro, orologio):
    corpus = corpus_incapienza()
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus)
    assert conguaglio_per_differenza(registro, corpus, R, 2026, date(2027, 1, 20)) is None


def test_un_interesse_trattenuto_solo_in_parte_conta_come_movimento_e_non_si_paga_due_volte(registro, orologio):
    """Prova della rilettura: a gennaio il netto copre solo parte dell'interesse e nessuna quota del resto."""
    corpus = corpus_incapienza()
    richiesta(registro)
    paga_dicembre(registro, orologio, corpus)
    gennaio = paga_mese(registro, orologio, corpus, 2027, 1, importo="0.50")
    assert righe_del(gennaio, "conguaglio_irpef_resto") == []
    (parziale,) = righe_del(gennaio, "conguaglio_irpef_interesse")
    assert D("0") < parziale.valore < D("0.72") and netto_di(gennaio) == D("0.00")
    febbraio = paga_mese(registro, orologio, corpus, 2027, 2)
    # un solo mese dal movimento di gennaio: 144,00 * 0,005 * 1, non due mesi da dicembre
    assert righe_del(febbraio, "conguaglio_irpef_interesse")[0].valore == D("0.72")
    assert righe_del(febbraio, "conguaglio_irpef_resto")[0].valore == D("144.00")
