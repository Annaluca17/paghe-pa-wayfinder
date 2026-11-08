"""Righe di proposta: una per classificazione e impegno, con i riferimenti alle righe di composizione (ADR 0031). Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.errori import ClassificazioneMancante, ErroreRegistro
from paghe.proposta import emetti_versione, leggi_versione

from materiale_proposta import CORPUS_PROPOSTA, P2, R, R2, assumi, corpus_p, stipendio

VALUTA = date(2026, 2, 27)
FEB = Mese(2026, 2)


def test_la_versione_porta_una_riga_per_classificazione_con_i_riferimenti_e_il_totale(registro, corpus_p, orologio):
    assumi(registro)
    assumi(registro, R2, P2)
    registro.registra_programma_rapporto(R, "01.02", date(2026, 1, 1))
    registro.registra_programma_rapporto(R2, "01.02", date(2026, 1, 1))
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    righe = {riga.piano_dei_conti: riga for riga in versione.righe_proposta}
    assert set(righe) == {"U.1.01.01.01.002", "U.1.01.02.01.001"}  # niente ritenute né contributi del lavoratore
    paga_riga = righe["U.1.01.01.01.002"]
    assert (paga_riga.missione, paga_riga.programma, paga_riga.totale) == ("01", "02", Decimal("2000"))
    assert paga_riga.riferimenti == tuple(
        versione.riferimento(r) for r in versione.righe if r.istituto == "stipendio"
    )
    assert righe["U.1.01.02.01.001"].totale == Decimal("480.00")


def test_le_righe_di_proposta_si_rileggono_dalla_versione_registrata(registro, corpus_p, orologio):
    assumi(registro)
    registro.registra_programma_rapporto(R, "01.02", date(2026, 1, 1))
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    emessa = emetti_versione(registro, corpus_p, VALUTA, importi)
    letta = leggi_versione(registro, emessa.id)
    assert letta.righe_proposta == emessa.righe_proposta
    assert all(rif.versione_id == emessa.id for riga in letta.righe_proposta for rif in riga.riferimenti)


def test_senza_classificazione_alla_valuta_la_versione_non_si_emette_e_l_errore_nomina_l_istituto(registro, orologio):
    corpus = Corpus.da_toml(
        CORPUS_PROPOSTA.replace(
            'istituto = "contributo_ente"\ndal = 2020-01-01\nriferimento = "fittizio:class-',
            'istituto = "contributo_ente"\ndal = 2030-01-01\nriferimento = "fittizio:class-',
        )
    )
    assumi(registro)
    importi = stipendio(registro, corpus, FEB)  # il calcolo non si ferma
    assert importi
    orologio.vai(2, 20)
    with pytest.raises(ClassificazioneMancante, match="contributo_ente"):
        emetti_versione(registro, corpus, VALUTA, importi)
    assert registro.versioni_registrate(orologio()) == []


def test_senza_programma_del_rapporto_la_riga_resta_vuota_e_il_dato_manca(registro, corpus_p, orologio):
    assumi(registro, programma=None)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    assert {(r.missione, r.programma, r.impegno) for r in versione.righe_proposta} == {("", "", None)}
    (mancante,) = [d for d in versione.dati_mancanti if d.tipo == "programma_rapporto"]
    assert mancante.soggetto == R


def test_il_programma_e_quello_vigente_alla_valuta_prevista(registro, corpus_p, orologio):
    assumi(registro, programma=None)
    registro.registra_programma_rapporto(R, "01.02", date(2026, 1, 1), date(2026, 2, 15))
    registro.registra_programma_rapporto(R, "04.06", date(2026, 2, 16))
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    assert {(r.missione, r.programma) for r in versione.righe_proposta} == {("04", "06")}
    assert not [d for d in versione.dati_mancanti if d.tipo == "programma_rapporto"]


@pytest.mark.parametrize("programma", ["1.2", "0102", "01.2", "AB.CD", ""])
def test_il_programma_ha_il_formato_missione_punto_programma(registro, programma):
    with pytest.raises(ErroreRegistro, match="Programma"):
        registro.registra_programma_rapporto(R, programma, date(2026, 1, 1))
