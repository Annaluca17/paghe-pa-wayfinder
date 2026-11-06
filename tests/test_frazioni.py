"""Mese parziale, frazioni, periodo dichiarato e tredicesima. Valori e fonti sono fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from conftest import CORPUS_BASE
from paghe import Corpus, Mese, Periodo, TipoEsito, calcola, calcola_annuale, differenze, emetti_esito, spiega
from paghe.errori import ErroreCorpus, ParametroMancante
from paghe.riferimento import motivo_rifiuto, solo_prassi

R = "RAPPORTO-1"
AGOSTO = Mese(2026, 8)
SETTEMBRE = Mese(2026, 9)
FEB = Mese(2026, 2)


def del_istituto(importi, istituto):
    return [i for i in importi if i.istituto == istituto]


def corpus_giorni(conteggio="lun_sab", divisore='divisore = "d"', valore_divisore="26", extra=""):
    return Corpus.da_toml(
        f"""
[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "{valore_divisore}"
riferimento = "fittizio:d"

[[regola]]
istituto = "stipendio"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio"
formula = "fatto.mensile"
maturazione = "giorni"
applica_se = "mensile"
conteggio = "{conteggio}"
{divisore}
decimali = 2
{extra}
"""
    )


def test_periodo_conta_i_giorni():
    assert Periodo(date(2026, 8, 24), date(2026, 8, 31)).giorni_calendario == 8
    assert Periodo(date(2026, 8, 24), date(2026, 8, 31)).giorni_lun_sab == 7
    assert Mese(2026, 8).periodo.giorni_lun_sab == 26


@pytest.mark.parametrize(
    ("conteggio", "divisore", "valore_divisore", "atteso"),
    [
        ("lun_sab", 'divisore = "d"', "26", "269.23"),
        ("calendario", "", "26", "258.06"),
        ("calendario", 'divisore = "d"', "30", "266.67"),
    ],
)
def test_il_divisore_lo_sceglie_la_regola(registro, conteggio, divisore, valore_divisore, atteso):
    corpus = corpus_giorni(conteggio, divisore, valore_divisore)
    registro.registra_fatto(R, "mensile", "1000.00", date(2026, 8, 24))
    importi = calcola(registro, corpus, R, AGOSTO)
    assert [i.valore for i in importi] == [Decimal(atteso)]
    assert importi[0].periodo == Periodo(date(2026, 8, 24), date(2026, 8, 31))


def test_mese_successivo_intero_e_divisore_non_letto(registro):
    corpus = corpus_giorni()
    registro.registra_fatto(R, "mensile", "1000.00", date(2026, 8, 24))
    importi = calcola(registro, corpus, R, SETTEMBRE)
    assert [i.valore for i in importi] == [Decimal("1000.00")]
    assert importi[0].derivazione.parametri == ()


def test_aumento_a_meta_mese_due_frazioni_con_quota_complementare(registro):
    corpus = corpus_giorni()
    registro.registra_fatto(R, "mensile", "1000.00", date(2026, 1, 1))
    registro.registra_fatto(R, "mensile", "1300.00", date(2026, 8, 15))
    prima, dopo = calcola(registro, corpus, R, AGOSTO)
    # 01-14 agosto: 12 giorni da lunedì a sabato; il mese ne ha 26, quindi la seconda frazione vale 14/26.
    assert prima.periodo == Periodo(date(2026, 8, 1), date(2026, 8, 14))
    assert prima.valore == Decimal("461.54")
    assert dopo.periodo == Periodo(date(2026, 8, 15), date(2026, 8, 31))
    assert dopo.valore == Decimal("700.00")
    assert dopo.derivazione.quota.divisore is None


def test_mese_intero_diviso_da_altro_istituto_somma_esattamente_il_mensile(registro):
    corpus = Corpus.da_toml(
        CORPUS_BASE
        + """
[[regola]]
istituto = "premio"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:premio"
formula = "fatto.premio"
maturazione = "evento"
applica_se = "premio"
"""
    )
    # Mese da 27 giorni lunedì-sabato: senza residuo la somma delle quote supererebbe 1.
    registro.registra_fatto(R, "compenso_mensile", "1000.01", date(2026, 1, 1))
    registro.registra_fatto(R, "premio", "50", date(2026, 7, 10), date(2026, 7, 20))
    righe = del_istituto(calcola(registro, corpus, R, Mese(2026, 7)), "compenso")
    assert len(righe) == 3
    assert sum(r.valore for r in righe) == Decimal("1000.01")


def test_cessazione_a_meta_mese(registro):
    corpus = corpus_giorni()
    registro.registra_fatto(R, "mensile", "1000.00", date(2026, 1, 1), date(2026, 9, 10))
    importi = calcola(registro, corpus, R, SETTEMBRE)
    assert importi[0].periodo == Periodo(date(2026, 9, 1), date(2026, 9, 10))
    assert importi[0].valore == Decimal("346.15")


def test_cambio_di_parametro_a_meta_mese_divide_le_frazioni(registro):
    corpus = Corpus.da_toml(
        """
[[parametro]]
nome = "a"
[[parametro.vigenza]]
dal = 2026-01-01
valore = "1"
riferimento = "fittizio:a"
[[parametro.vigenza]]
dal = 2026-08-15
valore = "2"
riferimento = "fittizio:b"

[[regola]]
istituto = "x"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:x"
formula = "parametro.a"
maturazione = "evento"
"""
    )
    assert [i.valore for i in calcola(registro, corpus, R, AGOSTO)] == [Decimal(1), Decimal(2)]


def test_contributo_calcolato_sul_periodo_dichiarato_non_sulla_frazione(registro, corpus):
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    registro.registra_fatto(R, "compenso_mensile", "1300.00", date(2026, 8, 15))
    importi = calcola(registro, corpus, R, AGOSTO)
    assert len(del_istituto(importi, "compenso")) == 2
    ritenute = del_istituto(importi, "ritenuta")
    assert len(ritenute) == 1
    assert ritenute[0].periodo == AGOSTO.periodo
    assert ritenute[0].valore == Decimal("116.15")
    assert len(ritenute[0].derivazione.importi) == 2


def test_il_periodo_dichiarato_si_apre_solo_per_i_fatti_indicati(registro):
    corpus = Corpus.da_toml(
        CORPUS_BASE + '\n[periodo_dichiarato]\nfatti = ["tipo_impiego"]\n'
    )
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    registro.registra_fatto(R, "tipo_impiego", "1", date(2026, 1, 1), date(2026, 8, 14))
    registro.registra_fatto(R, "tipo_impiego", "2", date(2026, 8, 15))
    assert len(del_istituto(calcola(registro, corpus, R, AGOSTO), "ritenuta")) == 2
    assert len(del_istituto(calcola(registro, corpus, R, SETTEMBRE), "ritenuta")) == 1


def test_assunzione_retroattiva_produce_differenza(registro, corpus, orologio):
    orologio.vai(9, 25)
    assert differenze(registro, corpus, R, AGOSTO, TipoEsito.PAGATO) == ()
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 8, 24))
    voci = {v.istituto: v.valore for v in differenze(registro, corpus, R, AGOSTO, TipoEsito.PAGATO)}
    assert voci == {"compenso": Decimal("269.23"), "ritenuta": Decimal("26.92")}


def test_differenza_quando_i_fatti_cambiano_le_frazioni(registro, corpus, orologio):
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    orologio.vai(8, 27)
    emetti_esito(registro, TipoEsito.PAGATO, date(2026, 8, 27), calcola(registro, corpus, R, AGOSTO))
    orologio.vai(9, 15)
    registro.registra_fatto(R, "compenso_mensile", "1300.00", date(2026, 8, 15))
    voci = differenze(registro, corpus, R, AGOSTO, TipoEsito.PAGATO)
    per_istituto = {v.istituto: v for v in voci}
    assert per_istituto["compenso"].valore == Decimal("161.54")
    importo = per_istituto["compenso"].importo()
    assert importo.periodo == AGOSTO.periodo
    assert len(importo.derivazione.importi) == 2

    orologio.vai(9, 27)
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 9, 27), [v.importo() for v in voci])
    assert registro.esito(esito.id) == esito
    assert differenze(registro, corpus, R, AGOSTO, TipoEsito.PAGATO) == ()


TREDICESIMA = CORPUS_BASE + """
[[parametro]]
nome = "divisore_tredicesima"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "365"
riferimento = "fittizio:divisore-tredicesima"

[[regola]]
istituto = "tredicesima"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:tredicesima"
formula = "fatto.compenso_mensile"
maturazione = "annuale"
applica_se = "compenso_mensile"
conteggio = "calendario"
divisore = "divisore_tredicesima"
decimali = 2
"""


def test_tredicesima_intera_con_servizio_continuo_e_base_di_dicembre(registro):
    corpus = Corpus.da_toml(TREDICESIMA)
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2020, 1, 1))
    registro.registra_fatto(R, "compenso_mensile", "1200.00", date(2026, 11, 1))
    importo, = calcola_annuale(registro, corpus, R, 2026)
    assert importo.valore == Decimal("1200.00")
    assert importo.periodo == Periodo(date(2026, 1, 1), date(2026, 12, 31))


def test_tredicesima_anno_bisestile_con_tetto(registro):
    corpus = Corpus.da_toml(TREDICESIMA)
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2024, 1, 1))
    assert calcola_annuale(registro, corpus, R, 2024)[0].valore == Decimal("1000.00")


def test_tredicesima_in_365esimi_per_assunzione_in_corso_d_anno(registro):
    corpus = Corpus.da_toml(TREDICESIMA)
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 8, 24))
    importo, = calcola_annuale(registro, corpus, R, 2026)
    assert importo.derivazione.quota.giorni == 130
    assert importo.valore == Decimal("356.16")


def test_tredicesima_alla_cessazione_sulla_base_dell_ultimo_mese(registro):
    corpus = Corpus.da_toml(TREDICESIMA)
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1), date(2026, 3, 31))
    registro.registra_fatto(R, "compenso_mensile", "2000.00", date(2026, 4, 1), date(2026, 6, 30))
    importo, = calcola_annuale(registro, corpus, R, 2026)
    assert importo.periodo == Periodo(date(2026, 1, 1), date(2026, 6, 30))
    assert importo.valore == Decimal("991.78")


def test_tredicesima_fuori_dal_calcolo_mensile_e_con_differenza_annuale(registro, orologio):
    corpus = Corpus.da_toml(TREDICESIMA)
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    assert not del_istituto(calcola(registro, corpus, R, Mese(2026, 12)), "tredicesima")

    orologio.vai(12, 15)
    emetti_esito(registro, TipoEsito.PAGATO, date(2026, 12, 15), calcola_annuale(registro, corpus, R, 2026))
    assert differenze(registro, corpus, R, 2026, TipoEsito.PAGATO) == ()
    assert del_istituto(calcola(registro, corpus, R, Mese(2026, 12)), "compenso")

    orologio.vai(12, 20)
    registro.registra_fatto(R, "compenso_mensile", "1100.00", date(2026, 12, 1))
    voci = differenze(registro, corpus, R, 2026, TipoEsito.PAGATO)
    assert {v.istituto: v.valore for v in voci} == {"tredicesima": Decimal("100.00")}


def test_nota_di_prassi_valida_e_segnalata(registro):
    riferimento = "prassi:immedia:nota:2026-11-06;1"
    assert motivo_rifiuto(riferimento) is None
    assert solo_prassi(riferimento)
    assert not solo_prassi(f"ccnl:S105:2022-11-16~art74-com4 + {riferimento}")
    corpus = Corpus.da_toml(
        f"""
[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "26"
riferimento = "{riferimento}"

[[regola]]
istituto = "s"
versione = 1
dal = 2020-01-01
riferimento = "{riferimento}"
formula = "fatto.m"
maturazione = "giorni"
applica_se = "m"
conteggio = "lun_sab"
divisore = "d"
decimali = 2
"""
    )
    registro.registra_fatto(R, "m", "1000", date(2026, 8, 24))
    testo = spiega(calcola(registro, corpus, R, AGOSTO)[0])
    assert "fondata solo su prassi" in testo
    assert "[solo prassi]" in testo
    assert "7/26" in testo


def test_divisore_senza_vigenza_ferma_il_calcolo(registro):
    corpus = Corpus.da_toml(
        """
[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2027-01-01
valore = "26"
riferimento = "fittizio:d"

[[regola]]
istituto = "s"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:s"
formula = "fatto.m"
maturazione = "giorni"
applica_se = "m"
conteggio = "lun_sab"
divisore = "d"
decimali = 2
"""
    )
    registro.registra_fatto(R, "m", "1000", date(2026, 8, 24))
    with pytest.raises(ParametroMancante):
        calcola(registro, corpus, R, AGOSTO)


def regola(campi):
    return f"""
[[regola]]
istituto = "s"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:s"
formula = "fatto.m"
{campi}
"""


@pytest.mark.parametrize(
    "campi",
    [
        "",
        'maturazione = "boh"',
        'maturazione = "giorni"\nconteggio = "calendario"\ndecimali = 2',
        'maturazione = "giorni"\napplica_se = "m"\ndecimali = 2',
        'maturazione = "giorni"\napplica_se = "m"\nconteggio = "boh"\ndecimali = 2',
        'maturazione = "giorni"\napplica_se = "m"\nconteggio = "calendario"',
        'maturazione = "giorni"\napplica_se = "m"\nconteggio = "lun_sab"\ndecimali = 2',
        'maturazione = "annuale"\napplica_se = "m"\nconteggio = "calendario"\ndecimali = 2',
        'maturazione = "evento"\ndecimali = 2',
        'maturazione = "giorni"\napplica_se = "m"\nconteggio = "lun_sab"\ndivisore = "ignoto"\ndecimali = 2',
    ],
)
def test_maturazione_dichiarata_e_coerente(campi):
    with pytest.raises(ErroreCorpus):
        Corpus.da_toml(regola(campi))


def test_livelli_di_lettura_rifiutati():
    base = """
[[regola]]
istituto = "p"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:p"
formula = "fatto.m"
maturazione = "periodo"

[[regola]]
istituto = "f"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:f"
formula = "importo.p"
maturazione = "evento"
"""
    with pytest.raises(ErroreCorpus, match="periodo dichiarato"):
        Corpus.da_toml(base)
