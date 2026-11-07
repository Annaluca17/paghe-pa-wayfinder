"""Il pagamento fisiologico lungo il ciclo della proposta, fino all'esito pagato (ticket #61). Dati fittizi."""

from datetime import date
from decimal import Decimal

from paghe import Corpus, Mese, TipoEsito
from paghe.proposta import emetti_versione

from materiale_proposta import CORPUS_PROPOSTA, R, assumi, paga, stipendio

FISIOLOGICO = """
[[pagamento_fisiologico]]
istituto = "stipendio"
dal = 2020-01-01
riferimento = "fittizio:fisiologico-stipendio"
"""
VALUTA = date(2027, 1, 13)


def test_un_importo_fisiologico_arriva_all_esito_pagato_nell_anno_del_pagamento(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_PROPOSTA + FISIOLOGICO)
    assumi(registro)
    importi = stipendio(registro, corpus, Mese(2026, 12))
    versione = paga(registro, corpus, orologio, importi, VALUTA, "pag-fisiologico")
    (esito,) = registro.esiti(TipoEsito.PAGATO, registro.adesso())
    righe = {riga.istituto: riga for riga in esito.righe}
    assert (righe["stipendio"].anno_imposta, righe["stipendio"].categoria_reddito) == (2027, "lavoro_dipendente")
    assert righe["ritenuta_irpef"].valore == Decimal("100.00")  # (1500 - 12000 / 12) * 0,20
    assert righe["ritenuta_irpef"].anno_imposta == 2027
    assert versione.rapporti == (R,)


def test_nella_stessa_versione_il_fisiologico_passa_e_la_competenza_di_due_anni_prima_ferma_il_suo_rapporto(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_PROPOSTA + FISIOLOGICO)
    assumi(registro)
    assumi(registro, "RAPPORTO-2", "PERSONA-2")
    importi = stipendio(registro, corpus, Mese(2026, 12)) + stipendio(registro, corpus, Mese(2025, 12), "500", "RAPPORTO-2")
    orologio.vai(1, 5, 2027)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert versione.rapporti == (R,)
    (fermo,) = versione.fermi
    assert fermo.rapporto == "RAPPORTO-2" and "due o più anni prima" in fermo.motivo


def test_senza_la_dichiarazione_dell_istituto_la_proposta_ferma_il_rapporto_e_nomina_il_caso(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_PROPOSTA)
    assumi(registro)
    assumi(registro, "RAPPORTO-2", "PERSONA-2")
    importi = stipendio(registro, corpus, Mese(2026, 12)) + stipendio(registro, corpus, Mese(2027, 1), "500", "RAPPORTO-2")
    orologio.vai(1, 5, 2027)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert versione.rapporti == ("RAPPORTO-2",)
    (fermo,) = versione.fermi
    assert fermo.rapporto == R and "non dichiara il pagamento fisiologico" in fermo.motivo
