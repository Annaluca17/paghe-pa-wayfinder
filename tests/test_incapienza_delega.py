"""Resto differito e interesse nella delega F24EP (ticket #99, ADR 0034, ADR 0023). Dati fittizi.

Il resto trattenuto versa sul codice del conguaglio (100E) con le altre ritenute; l'interesse è un importo a sé con il suo
codice tributo. Il codice dell'interesse non si inventa: nel corpus reale manca, e la delega si ferma nominando l'istituto.
Il codice di prova (199E) esiste solo nel materiale di test.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.delega import costruisci_delega

from materiale_delega import CATALOGO, _codice, dati_ente, toml_delega
from materiale_incapienza import CODICE_DI_PROVA, paga_dicembre, paga_mese, toml_incapienza
from materiale_proposta import P

D = Decimal
GENNAIO = Mese(2027, 1)
CATALOGO_CON_INTERESSE = _codice(CODICE_DI_PROVA, "F", "nessuno", "nessuno", "mese_pagamento", "anno_pagamento", "debito")


def corpus_delega_incapienza(**kwargs) -> Corpus:
    return Corpus.da_toml(toml_incapienza(base=toml_delega(), **kwargs) + CATALOGO_CON_INTERESSE)


def gennaio_pagato(registro, orologio, corpus):
    dati_ente(registro)
    registro.registra_data_versamento(GENNAIO, date(2027, 2, 16))
    registro.registra_richiesta_differimento(P, date(2026, 1, 1))
    paga_dicembre(registro, orologio, corpus)
    paga_mese(registro, orologio, corpus, 2027, 1)


def test_il_resto_versa_sul_codice_del_conguaglio_e_l_interesse_sul_suo(registro, orologio):
    corpus = corpus_delega_incapienza()
    gennaio_pagato(registro, orologio, corpus)
    delega = costruisci_delega(registro, corpus, GENNAIO)
    assert delega.fermi == ()
    per_codice = {riga.chiave[1]: riga.debito for riga in delega.righe}
    # 100E: la ritenuta di gennaio (280,00) e il resto (144,00); 199E: l'interesse (0,72)
    assert per_codice["100E"] == D("424.00") and per_codice[CODICE_DI_PROVA] == D("0.72")


def test_senza_il_codice_tributo_dell_interesse_la_delega_si_ferma_e_lo_nomina(registro, orologio):
    corpus = corpus_delega_incapienza(con_mappatura=False)
    gennaio_pagato(registro, orologio, corpus)
    delega = costruisci_delega(registro, corpus, GENNAIO)
    assert not delega.pronta
    (fermo,) = delega.fermi
    assert fermo.caso == "mappatura_mancante" and "conguaglio_irpef_interesse" in fermo.motivo
