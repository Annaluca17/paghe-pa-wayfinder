"""Part-time: trattamento dichiarato dall'istituto, calcolo mensilizzato, programmazione (ADR 0026, ticket #72).

Valori e fonti fittizi: nessun valore qui è una norma.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, Periodo, calcola
from paghe.errori import CasoNonModellato, ErroreCorpus, FattoMancante

R = "RAPPORTO-1"
NOVEMBRE = Mese(2026, 11)

BASE = """
[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "26"
riferimento = "fittizio:d"

[[regola]]
istituto = "stipendio"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio"
formula = "fatto.mensile"
maturazione = "giorni"
applica_se = "mensile"
conteggio = "lun_sab"
divisore = "d"
decimali = 2
"""


def dichiarazione(trattamento="proporzionale", istituto="stipendio", dal="2020-01-01", extra=""):
    return f"""
[[part_time]]
istituto = "{istituto}"
trattamento = "{trattamento}"
dal = {dal}
riferimento = "fittizio:part-time-{istituto}"
{extra}
"""


def corpus_con(*dichiarazioni, base=BASE):
    return Corpus.da_toml(base + "".join(dichiarazioni))


def test_un_istituto_dichiara_il_trattamento_nel_part_time():
    corpus = corpus_con(dichiarazione("proporzionale"))
    voce = corpus.trattamento_part_time("stipendio", date(2026, 11, 1))
    assert voce.trattamento == "proporzionale"
    assert voce.riferimento == "fittizio:part-time-stipendio"
    assert corpus.trattamento_part_time("altro", date(2026, 11, 1)) is None


@pytest.mark.parametrize(
    ("voci", "messaggio"),
    [
        ((dichiarazione("riproporzionato"),), "trattamento"),
        ((dichiarazione(istituto="ignoto"),), "ignoto"),
        ((dichiarazione(), dichiarazione("intero")), "sovrapposte"),
        ((dichiarazione().replace('riferimento = "fittizio:part-time-stipendio"', 'riferimento = ""'),), "riferimento"),
        ((dichiarazione("da_integrativo"),), "fatto"),
        ((dichiarazione("proporzionale", extra='fatto = "misura"'),), "fatto"),
    ],
)
def test_una_dichiarazione_del_trattamento_non_valida_e_rifiutata(voci, messaggio):
    with pytest.raises(ErroreCorpus, match=messaggio):
        corpus_con(*voci)


def test_la_dichiarazione_entra_nell_impronta_solo_se_presente():
    senza = Corpus.da_toml(BASE)
    con = corpus_con(dichiarazione())
    altra = corpus_con(dichiarazione("intero"))
    assert senza.versione != con.versione != altra.versione
    assert Corpus.da_toml(BASE).versione == senza.versione


def test_il_corpus_reale_rifiuta_il_riferimento_fittizio_del_part_time():
    with pytest.raises(ErroreCorpus, match="fittizio"):
        Corpus.da_toml(BASE.replace("fittizio:", "prassi:immedia:nota:2026-11-06;1 + fittizio:") + dichiarazione(), reale=True)


def assumi_part_time(registro, percentuale="60", tipo="orizzontale", dal=date(2026, 1, 1)):
    registro.registra_fatto(R, "mensile", "1000.00", date(2026, 1, 1))
    registro.registra_fatto(R, "part_time", percentuale, dal)
    registro.registra_codice(R, "tipo_part_time", tipo, dal)


def test_il_proporzionale_vale_l_importo_pieno_per_la_percentuale(registro):
    assumi_part_time(registro, "60")
    (stipendio,) = calcola(registro, corpus_con(dichiarazione("proporzionale")), R, NOVEMBRE)
    assert stipendio.valore == Decimal("600.00")
    riduzione = stipendio.derivazione.part_time
    assert (riduzione.percentuale, riduzione.importo_pieno, riduzione.trattamento) == (
        Decimal("60"), Decimal("1000.00"), "proporzionale",
    )
    assert "part_time" in [fatto.tipo for fatto in stipendio.derivazione.fatti]


def test_il_proporzionale_arrotonda_come_la_regola(registro):
    assumi_part_time(registro, "66.6667")
    (stipendio,) = calcola(registro, corpus_con(dichiarazione()), R, NOVEMBRE)
    assert stipendio.valore == Decimal("666.67")
