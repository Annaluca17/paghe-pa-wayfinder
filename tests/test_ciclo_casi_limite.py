"""Casi limite del ciclo di pagamento (ADR 0025). Dati fittizi."""

from datetime import date

import pytest

from paghe import Corpus, Mese, TipoEsito
from paghe.errori import ErroreRegistro
from paghe.proposta import (
    emetti_versione,
    registra_ricevuta_delega,
    registra_versamento_eseguito,
    segnala_scostamento_contributi,
)

from materiale_proposta import CORPUS_PROPOSTA, R, assumi, corpus_p, paga, stipendio

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)
ADATTATORE = "adattatore-prova"

INTERMEDIO = """
[[regola]]
istituto = "contributo_totale"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:contributo-totale"
formula = "arrotonda(base.pens * parametro.aliquota_ente, 2)"
maturazione = "periodo"

[[composizione]]
istituto = "contributo_totale"
dal = 2020-01-01
riferimento = "fittizio:comp-contributo-totale"
intermedio = true
"""


def righe_a_terzi(versione):
    return [versione.riferimento(riga) for riga in versione.righe if riga.destinatario == "terzo"]


def test_un_istituto_intermedio_non_e_uno_scostamento_tra_denuncia_e_contributi(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_PROPOSTA + INTERMEDIO)
    assumi(registro)
    paga(registro, corpus, orologio, stipendio(registro, corpus, FEB), VALUTA, "pag-1")
    assert segnala_scostamento_contributi(registro, corpus, R, FEB) == ()


def test_la_stessa_riga_non_si_versa_in_due_versamenti_diversi(registro, corpus_p, orologio):
    assumi(registro)
    versione = paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, FEB), VALUTA, "pag-1")
    righe = righe_a_terzi(versione)
    registra_versamento_eseguito(registro, "ver-1", ADATTATORE, "V-1", date(2026, 3, 16), righe, "f24ep", "addebito")
    orologio.avanza()
    with pytest.raises(ErroreRegistro, match="già versata"):
        registra_versamento_eseguito(registro, "ver-2", ADATTATORE, "V-2", date(2026, 3, 16), righe, "f24ep", "addebito")
    assert len(registro.esiti(TipoEsito.VERSATO, orologio())) == 1


def test_una_delega_scartata_non_produce_un_esito_versato(registro, corpus_p, orologio):
    assumi(registro)
    versione = paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, FEB), VALUTA, "pag-1")
    registra_ricevuta_delega(registro, "r-1", ADATTATORE, "V-1", "controlli_formali", "negativo")
    orologio.avanza()
    with pytest.raises(ErroreRegistro, match="scartata"):
        registra_versamento_eseguito(
            registro, "ver-1", ADATTATORE, "V-1", date(2026, 3, 16), righe_a_terzi(versione), "f24ep", "addebito"
        )
    assert registro.esiti(TipoEsito.VERSATO, orologio()) == []


def test_dopo_una_delega_scartata_gli_importi_si_versano_con_una_nuova(registro, corpus_p, orologio):
    assumi(registro)
    versione = paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, FEB), VALUTA, "pag-1")
    registra_ricevuta_delega(registro, "r-1", ADATTATORE, "V-1", "controlli_formali", "negativo")
    orologio.avanza()
    esito = registra_versamento_eseguito(
        registro, "ver-2", ADATTATORE, "V-2", date(2026, 3, 16), righe_a_terzi(versione), "f24ep", "addebito"
    )
    assert esito.tipo is TipoEsito.VERSATO


def test_senza_cassa_allargata_un_pagamento_di_gennaio_non_chiede_l_ultimo_pagamento(registro, orologio):
    """Con la cassa allargata spenta il 5 gennaio è già l'anno nuovo, lontano dalla sua fine."""
    corpus = Corpus.da_toml(CORPUS_PROPOSTA.replace("vale = true", "vale = false"))
    assumi(registro)
    importi = stipendio(registro, corpus, Mese(2026, 1))
    orologio.vai(1, 5, 2026)
    versione = emetti_versione(registro, corpus, date(2026, 1, 5), importi)
    assert [d.tipo for d in versione.dati_mancanti] == []


def test_con_la_cassa_allargata_il_pagamento_entro_il_12_gennaio_chiede_l_ultimo_pagamento(registro, corpus_p, orologio):
    assumi(registro, dal=date(2025, 12, 1))
    importi = stipendio(registro, corpus_p, Mese(2025, 12))
    orologio.vai(1, 5, 2026)
    versione = emetti_versione(registro, corpus_p, date(2026, 1, 5), importi)
    assert [d.tipo for d in versione.dati_mancanti] == ["ultimo_pagamento_dell_anno"]
