"""Il pagamento fisiologico lungo il ciclo della proposta, fino all'esito pagato (ticket #61). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, TipoEsito
from paghe.errori import CasoNonModellato
from paghe.fisco import proiezione_conguaglio
from paghe.proposta import (
    AVVISO_COMPETENZA_AL_PAGAMENTO,
    conferma_versione,
    emetti_versione,
    registra_pagamento_eseguito,
)

from materiale_proposta import CORPUS_PROPOSTA, P, R, assumi, paga, stipendio

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


def test_il_controllo_si_ripete_al_pagamento_eseguito_e_ferma_il_fisco_della_persona(registro, orologio):
    """ADR 0018: la dichiarazione vale alla valuta prevista ma è scaduta alla valuta reale, nello stesso anno d'imposta."""
    corpus = Corpus.da_toml(CORPUS_PROPOSTA + FISIOLOGICO.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2027-01-31"))
    assumi(registro)
    importi = stipendio(registro, corpus, Mese(2026, 12))
    orologio.vai(1, 20, 2027)
    versione = emetti_versione(registro, corpus, date(2027, 1, 28), importi)
    conferma_versione(registro, versione.id)
    eseguito = registra_pagamento_eseguito(registro, corpus, "pag-1", "adattatore-prova", versione.id, date(2027, 2, 3), [R])
    assert AVVISO_COMPETENZA_AL_PAGAMENTO in {avviso.tipo for avviso in eseguito.avvisi}
    with pytest.raises(CasoNonModellato):
        proiezione_conguaglio(registro, corpus, P, 2027, date(2027, 2, 3))


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
