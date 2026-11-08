"""Acconto dell'addizionale comunale (ticket #85, ADR 0029). Dati fittizi.

Acconto 2027 = 30% dell'addizionale comunale 2026 (99,00 sul comune X001) = 29,70, da marzo a novembre in nove rate: 3,30.
Senza il conguaglio 2026 nel modello la base viene dal fatto «reddito dell'anno precedente» (la CU) e si ricalcola con
aliquote e soglia del 2026.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto
from paghe.errori import ErroreRegistro, FattoMancante

from materiale_addizionali import anno_di_paghe, assumi_a, corpus_addizionali, paga, per_istituto
from materiale_proposta import P

D = Decimal
ACC = "addizionale_comunale_acconto"
ATTO_CU = Atto("ente:ente_di_prova:cu:2027-03-16;1", date(2027, 3, 16))


@pytest.fixture
def corpus():
    return corpus_addizionali()


@pytest.fixture
def dal_2027(registro, orologio, corpus):
    assumi_a(registro)
    anno_di_paghe(registro, orologio, corpus)
    return lambda mese, giorno=27: paga(registro, orologio, corpus, date(2027, mese, giorno))


def test_da_marzo_l_acconto_e_un_nono_del_30_per_cento_dell_addizionale_comunale_del_2026(dal_2027):
    assert ACC not in per_istituto(dal_2027(1).addizionali) and ACC not in per_istituto(dal_2027(2).addizionali)
    acconto = per_istituto(dal_2027(3).addizionali)[ACC]
    assert (acconto.valore, acconto.anno_imposta) == (D("3.30"), 2027)


def test_l_acconto_dice_da_dove_viene(dal_2027):
    dal_2027(1), dal_2027(2)
    acconto = per_istituto(dal_2027(3).addizionali)[ACC]
    assert [(i.istituto, i.valore) for i in acconto.derivazione.importi] == [("addizionale_comunale_dovuta", D("99.00"))]
    assert {p.nome: p.valore for p in acconto.derivazione.parametri} == {
        "addizionale_acconto_percentuale": D("0.30"),
        "addizionale_mese_prima_rata_acconto": D("3"),
        "addizionale_mese_ultima_rata": D("11"),
    }


def test_le_nove_rate_dell_acconto_fanno_il_30_per_cento(dal_2027):
    rate = [per_istituto(dal_2027(mese).addizionali).get(ACC) for mese in range(1, 13)]
    assert [r is not None for r in rate] == [False, False] + [True] * 9 + [False]
    assert sum(r.valore for r in rate if r) == D("29.70")


def test_senza_il_conguaglio_nel_modello_la_base_viene_dalla_cu(registro, orologio, corpus):
    assumi_a(registro)
    registro.registra_reddito_anno_precedente(P, 2026, "18000", ATTO_CU)
    fiscale = paga(registro, orologio, corpus, date(2027, 3, 27))
    acconto = per_istituto(fiscale.addizionali)[ACC]
    assert acconto.valore == D("3.30")  # 30% di 99,00 sul reddito 18000 con le aliquote 2026 del comune X001, in nove rate
    assert {f.tipo for f in acconto.derivazione.fatti} == {"reddito_anno_precedente", "domicilio_fiscale"}
    assert fiscale.avvisi_di("acconto_senza_base") == ()


def test_il_conguaglio_nel_modello_vince_sul_fatto_della_cu(registro, orologio, corpus):
    assumi_a(registro)
    anno_di_paghe(registro, orologio, corpus)
    registro.registra_reddito_anno_precedente(P, 2026, "50000", ATTO_CU)
    orologio.vai(3, 1, 2027)
    assert per_istituto(paga(registro, orologio, corpus, date(2027, 3, 27)).addizionali)[ACC].valore == D("3.30")


def test_con_la_cu_sotto_la_soglia_l_acconto_e_zero(registro, orologio, corpus):
    assumi_a(registro, "X002", "97")
    registro.registra_reddito_anno_precedente(P, 2026, "12000", ATTO_CU)
    fiscale = paga(registro, orologio, corpus, date(2027, 3, 27))
    assert ACC not in per_istituto(fiscale.addizionali) and fiscale.avvisi_di("acconto_senza_base") == ()


def test_un_reddito_nullo_della_cu_e_un_valore_non_un_dato_mancante(registro, orologio, corpus):
    assumi_a(registro)
    registro.registra_reddito_anno_precedente(P, 2026, "0", ATTO_CU)
    fiscale = paga(registro, orologio, corpus, date(2027, 3, 27))
    assert fiscale.addizionali == () and fiscale.avvisi_di("acconto_senza_base") == ()


def test_senza_conguaglio_ne_cu_niente_acconto_e_un_avviso_non_un_fermo(registro, orologio, corpus):
    assumi_a(registro)
    gennaio = paga(registro, orologio, corpus, date(2027, 1, 27))
    marzo = paga(registro, orologio, corpus, date(2027, 3, 27))
    assert marzo.addizionali == ()
    (avviso,) = marzo.avvisi_di("acconto_senza_base")
    assert (avviso.persona, avviso.anno) == (P, 2027) and "reddito dell'anno precedente" in avviso.messaggio
    assert gennaio.avvisi_di("acconto_senza_base") == ()  # a gennaio l'acconto non si trattiene ancora


def test_la_cu_senza_domicilio_ferma_il_calcolo_dell_acconto(registro, orologio, corpus):
    assumi_a(registro, comune=None)
    registro.registra_reddito_anno_precedente(P, 2026, "18000", ATTO_CU)
    with pytest.raises(FattoMancante, match="domicilio fiscale"):
        paga(registro, orologio, corpus, date(2027, 3, 27))


def test_il_reddito_dell_anno_precedente_vuole_la_cu_e_un_importo_non_negativo(registro):
    with pytest.raises(ErroreRegistro, match="CU"):
        registro.registra_reddito_anno_precedente(P, 2026, "100", None)
    with pytest.raises(ErroreRegistro, match="non negativo"):
        registro.registra_reddito_anno_precedente(P, 2026, "-1", ATTO_CU)
