"""DenunciaIndividuale dei tempi determinati (ADR 0027, ticket #77): vista della stessa denuncia della ListaPosPA.

Seam sotto prova: `denuncia_individuale`, `denuncia_aziendale`, `invia_denuncia_individuale` con la differenza
dall'ultimo invio, `controlla_completezza`, e le voci di corpus che li alimentano. Corpus reale CPDEL più, dove serve,
un'aggiunta di prova (festivi). Persone, rapporti e codici fiscali di fantasia.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto, Corpus, Mese, calcola, denuncia_individuale
from paghe.part_time import registra_programmazione
from test_lista_pos_pa import CORPUS, R, assumi, paga, stipendi


@pytest.fixture(scope="module")
def corpus():
    return Corpus.carica(CORPUS, reale=True)


MARZO = Mese(2026, 3)


def test_un_rapporto_a_tempo_indeterminato_non_ha_la_denuncia_individuale(registro, corpus):
    assumi(registro)  # tipo impiego 1: tempo pieno indeterminato
    assert denuncia_individuale(registro, corpus, R, MARZO) is None


def in_servizio_con(registro, impiego, area="istruttori"):
    assumi(registro, area=area, senza=("tipo_impiego",))
    registro.registra_codice(R, "tipo_impiego", impiego, date(2026, 1, 1))


@pytest.mark.parametrize("impiego", ["48", "49", "52", "53"])
def test_cfl_apprendisti_e_ricerca_fermano_la_vista_e_nominano_il_caso(registro, corpus, impiego):
    in_servizio_con(registro, impiego)
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    fermo, = vista.fermi
    assert f"Tipo impiego {impiego}" in fermo.motivo
    assert not vista.trasmissibile


CORPUS_SENZA_CPDEL = """
[periodo_dichiarato]
servizio = "tipo_impiego"

[[base]]
nome = "fpld"
riferimento = "fittizio:base-fpld"

[[parametro]]
nome = "divisore_giornaliero"
[[parametro.vigenza]]
dal = 2026-01-01
valore = "26"
riferimento = "fittizio:divisore"

[[regola]]
istituto = "compenso"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:compenso"
formula = "fatto.compenso_mensile"
maturazione = "giorni"
applica_se = "compenso_mensile"
conteggio = "lun_sab"
divisore = "divisore_giornaliero"
decimali = 2

[[concorso]]
istituto = "compenso"
basi = ["fpld"]
misura = "intero"
dal = 2026-01-01
riferimento = "fittizio:concorso-fpld"
"""


def test_un_tempo_determinato_pagato_senza_base_cpdel_ferma_la_vista_e_nomina_il_caso(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_SENZA_CPDEL)
    registro.registra_codice(R, "tipo_impiego", "17", date(2026, 1, 1))
    registro.registra_fatto(R, "compenso_mensile", "1300", date(2026, 1, 1))
    paga(registro, orologio, calcola(registro, corpus, R, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    fermo, = vista.fermi
    assert "pensione non in CPDEL" in fermo.motivo


def td_pagato(registro, orologio, corpus, impiego="17", mese=MARZO, giorno=date(2026, 3, 27)):
    in_servizio_con(registro, impiego)
    paga(registro, orologio, stipendi(registro, corpus, mese), giorno)


def test_il_contributo_e_l_aliquota_naspi_sull_imponibile_intero_dichiarato(registro, orologio, corpus):
    td_pagato(registro, orologio, corpus)
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    # Base CPDEL 2051,69 -> Imponibile 2052 all'euro; contributo = 2052 x 1,61% = 33,0372 -> 33,04 (non su 2051,69).
    assert (vista.tipo_contribuzione, vista.imponibile, vista.contributo) == ("71", 2052, Decimal("33.04"))


CORPUS_PICCOLO = CORPUS_SENZA_CPDEL.replace("fpld", "cpdel") + """
[[parametro]]
nome = "aliquota_naspi_ordinaria"
[[parametro.vigenza]]
dal = 2013-01-01
valore = "1.31"
riferimento = "fittizio:naspi-ordinaria"

[[parametro]]
nome = "aliquota_naspi_integrativa"
[[parametro.vigenza]]
dal = 2013-01-01
valore = "0.30"
riferimento = "fittizio:naspi-integrativa"
"""


def test_il_contributo_arrotonda_i_millesimi_da_5_a_9_al_centesimo_superiore(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_PICCOLO)
    registro.registra_codice(R, "tipo_impiego", "17", date(2026, 1, 1))
    registro.registra_fatto(R, "compenso_mensile", "50", date(2026, 1, 1))
    paga(registro, orologio, calcola(registro, corpus, R, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    # 50 x 1,61% = 0,805: il millesimo 5 sale al centesimo superiore, 0,81 (DT p. 31).
    assert (vista.imponibile, vista.contributo) == (50, Decimal("0.81"))


def test_l_aliquota_naspi_del_corpus_reale_ha_le_due_componenti_datate_con_la_fonte(corpus):
    for nome, valore, fonte in (
        ("aliquota_naspi_ordinaria", "1.31", "legge:2012-06-28;92~art2-com25"),
        ("aliquota_naspi_integrativa", "0.30", "legge:1978-12-21;845~art25-com4"),
    ):
        vigenza, = corpus.parametro(nome).vigenze
        assert (vigenza.dal, vigenza.valore) == (date(2013, 1, 1), Decimal(valore))
        assert fonte in vigenza.riferimento


MAPPATURA_PROVA = """
[[mappatura_fatto]]
sistema = "prova"
elemento = "Qualifica3"
fatto = "termine_per_sostituzione"
valore = "si"
codice = "A"
dal = 2026-01-01
al = 2026-12-31
riferimento = "fittizio:qualifica3-sostituzione"
"""


def test_una_mappatura_di_fatto_e_datata_e_dice_il_codice_di_un_elemento_per_il_valore_di_un_fatto():
    corpus = Corpus.da_toml(CORPUS_PICCOLO + MAPPATURA_PROVA)
    cerca = lambda valore, giorno: corpus.mappatura_di_fatto("prova", "Qualifica3", "termine_per_sostituzione", valore, giorno)
    assert cerca("si", date(2026, 3, 1)).codice == "A"
    assert cerca("si", date(2027, 1, 1)) is None  # scaduta
    assert cerca("no", date(2026, 3, 1)) is None  # nessun valore dichiarato per «no»


@pytest.mark.parametrize(("termine", "qualifica3"), [("si", "A"), ("no", "D")])
def test_qualifica3_e_a_per_la_sostituzione_e_d_per_gli_altri_dalla_mappatura_del_corpus(
    registro, orologio, corpus, termine, qualifica3
):
    td_pagato(registro, orologio, corpus)
    registro.registra_codice(R, "termine_per_sostituzione", termine, date(2026, 1, 1))
    assert denuncia_individuale(registro, corpus, R, MARZO).qualifica3 == qualifica3


def test_senza_il_fatto_della_sostituzione_la_vista_e_una_bozza_che_lo_chiede_e_il_calcolo_resta(registro, orologio, corpus):
    td_pagato(registro, orologio, corpus)
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert "termine_per_sostituzione" in [d.fatto for d in vista.mancanti]
    assert vista.qualifica3 is None and not vista.trasmissibile
    assert vista.contributo == Decimal("33.04")


def test_un_valore_senza_mappatura_nel_corpus_e_un_dato_mancante_che_la_nomina(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_PICCOLO)  # nessuna mappatura
    registro.registra_codice(R, "tipo_impiego", "17", date(2026, 1, 1))
    registro.registra_codice(R, "termine_per_sostituzione", "si", date(2026, 1, 1))
    registro.registra_fatto(R, "compenso_mensile", "1300", date(2026, 1, 1))
    paga(registro, orologio, calcola(registro, corpus, R, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert "mappatura Qualifica3 (termine_per_sostituzione=si)" in [d.fatto for d in vista.mancanti]


@pytest.mark.parametrize("area", ["funzionari", "istruttori", "operatori_esperti", "operatori"])
def test_qualifica1_e_dalla_mappatura_del_corpus_per_l_area_del_comparto(registro, orologio, corpus, area):
    in_servizio_con(registro, "17", area)
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    assert denuncia_individuale(registro, corpus, R, MARZO).qualifica1 == "2"


@pytest.mark.parametrize(("iscrizione", "regime_post95"), [("si", "S"), ("no", "N")])
def test_regime_post95_e_dalla_mappatura_del_corpus_per_la_prima_iscrizione(
    registro, orologio, corpus, iscrizione, regime_post95
):
    td_pagato(registro, orologio, corpus)
    registro.registra_codice(R, "prima_iscrizione_dal_1996", iscrizione, date(2026, 1, 1))
    assert denuncia_individuale(registro, corpus, R, MARZO).regime_post95 == regime_post95


def test_codice_contratto_e_il_suo_tipo_sono_nel_corpus_per_il_contratto_del_rapporto(registro, orologio, corpus):
    td_pagato(registro, orologio, corpus)  # contratto RALN
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert (vista.codice_contratto, vista.tipo_codice_contratto) == ("CPUB", "02")


def test_il_tempo_pieno_ha_qualifica2_f_e_nessuna_percentuale_di_part_time(registro, orologio, corpus):
    td_pagato(registro, orologio, corpus, "17")
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert vista.qualifica2 == "F"
    assert (vista.perc_part_time, vista.perc_part_time_mese, vista.ore_contribuite, vista.settimane_utili) == (None,) * 4


ATTO_PROGRAMMAZIONE = Atto("fittizio:programmazione-prova", date(2026, 2, 20))


def td_part_time(registro, orologio, corpus, tipo, percentuale, ore_del_giorno, mese=MARZO):
    """Tempo determinato part-time (tipo impiego 18) con la programmazione del mese; ore_del_giorno(giorno) -> ore."""
    in_servizio_con(registro, "18")
    registro.registra_fatto(R, "part_time", percentuale, date(2026, 1, 1))
    registro.registra_codice(R, "tipo_part_time", tipo, date(2026, 1, 1))
    if ore_del_giorno is not None:
        registra_programmazione(registro, R, {g: ore_del_giorno(g) for g in mese.giorni()}, ATTO_PROGRAMMAZIONE)
    paga(registro, orologio, stipendi(registro, corpus, mese), date(2026, 3, 27))


def lun_ven(ore):
    return lambda giorno: Decimal(str(ore)) if giorno.weekday() < 5 else Decimal(0)


def test_il_part_time_orizzontale_ha_percentuale_in_centesimi_ore_e_settimane_utili_dalla_programmazione(
    registro, orologio, corpus
):
    td_part_time(registro, orologio, corpus, "orizzontale", "50", lun_ven("3.6"))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    # 22 giorni lavorativi a 3,6 ore = 79,2 ore: OreContribuite in centesimi di ora, SettimaneUtili = 79,2 / 36 = 2,20.
    assert (vista.qualifica2, vista.perc_part_time, vista.perc_part_time_mese) == ("P", 5000, None)
    assert (vista.ore_contribuite, vista.settimane_utili) == (7920, 220)


def test_senza_programmazione_il_part_time_chiede_il_dato_e_il_calcolo_non_si_ferma(registro, orologio, corpus):
    td_part_time(registro, orologio, corpus, "orizzontale", "50", None)
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert "programmazione_part_time" in [d.fatto for d in vista.mancanti]
    assert not vista.trasmissibile
    assert (vista.ore_contribuite, vista.settimane_utili) == (None, None)
    assert vista.perc_part_time == 5000
    assert vista.imponibile > 0 and vista.contributo > 0  # il calcolo c'è


def test_un_giorno_non_programmato_del_mese_chiede_la_programmazione(registro, orologio, corpus):
    ore = lambda giorno: None if giorno == date(2026, 3, 17) else Decimal(4)
    in_servizio_con(registro, "18")
    registro.registra_fatto(R, "part_time", "50", date(2026, 1, 1))
    registro.registra_codice(R, "tipo_part_time", "orizzontale", date(2026, 1, 1))
    registra_programmazione(
        registro, R, {g: ore(g) for g in MARZO.giorni() if ore(g) is not None}, ATTO_PROGRAMMAZIONE
    )
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert "programmazione_part_time" in [d.fatto for d in vista.mancanti]


def test_un_mese_in_servizio_senza_importi_pagati_ha_la_vista_senza_imponibile_ne_contributo(registro, corpus):
    in_servizio_con(registro, "17")
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert vista is not None
    assert (vista.tipo_contribuzione, vista.imponibile, vista.contributo) == ("71", None, None)
