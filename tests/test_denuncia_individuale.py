"""DenunciaIndividuale dei tempi determinati (ADR 0027, ticket #77): vista della stessa denuncia della ListaPosPA.

Seam sotto prova: `denuncia_individuale`, `denuncia_aziendale`, `invia_denuncia_individuale` con la differenza
dall'ultimo invio, `controlla_completezza`, e le voci di corpus che li alimentano. Corpus reale CPDEL più, dove serve,
un'aggiunta di prova (festivi). Persone, rapporti e codici fiscali di fantasia.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto, Corpus, Mese, TipoEsito, calcola, controlla_completezza, emetti_esito, denuncia_aziendale, denuncia_individuale, invia_denuncia_individuale, leggi_invio_denuncia_individuale, segnala_scostamento_invio
from paghe.denuncia_individuale import DenunciaIndividuale
from paghe.errori import ErroreCorpus, ErrorePaghe, ErroreRegistro, VistaFerma
from paghe.part_time import registra_programmazione
from test_lista_pos_pa import CORPUS, R, assumi, paga, stipendi


@pytest.fixture(scope="module")
def corpus():
    return Corpus.carica(CORPUS, reale=True)


MARZO = Mese(2026, 3)


def test_un_rapporto_a_tempo_indeterminato_non_ha_la_denuncia_individuale(registro, corpus):
    assumi(registro)  # tipo impiego 1: tempo pieno indeterminato
    assert denuncia_individuale(registro, corpus, R, MARZO) is None


def in_servizio_con(registro, impiego, area="istruttori", qualifica_inps="impiegato"):
    assumi(registro, area=area, senza=("tipo_impiego",))
    registro.registra_codice(R, "tipo_impiego", impiego, date(2026, 1, 1))
    if qualifica_inps is not None:  # fatto del rapporto, inserito all'assunzione (grilling del #87)
        registro.registra_codice(R, "qualifica_inps", qualifica_inps, date(2026, 1, 1))


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


@pytest.mark.parametrize(("qualifica_inps", "qualifica1"), [("operaio", "1"), ("impiegato", "2"), ("dirigente", "3")])
def test_qualifica1_e_dalla_mappatura_del_corpus_per_la_qualifica_inps_del_rapporto(
    registro, orologio, corpus, qualifica_inps, qualifica1
):
    in_servizio_con(registro, "17", qualifica_inps=qualifica_inps)
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    assert denuncia_individuale(registro, corpus, R, MARZO).qualifica1 == qualifica1


@pytest.mark.parametrize("area", ["funzionari", "istruttori", "operatori_esperti", "operatori"])
def test_qualifica1_non_dipende_dall_area(registro, orologio, corpus, area):
    in_servizio_con(registro, "17", area, qualifica_inps="operaio")
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    assert denuncia_individuale(registro, corpus, R, MARZO).qualifica1 == "1"


def test_senza_la_qualifica_inps_la_vista_e_una_bozza_che_la_chiede_senza_default(registro, orologio, corpus):
    in_servizio_con(registro, "17", qualifica_inps=None)
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert "qualifica_inps" in [d.fatto for d in vista.mancanti]
    assert vista.qualifica1 is None and not vista.trasmissibile


def test_una_qualifica_inps_senza_mappatura_e_un_dato_mancante_che_la_nomina(registro, orologio, corpus):
    in_servizio_con(registro, "17", qualifica_inps="quadro")  # nell'Allegato 4.33.1 esiste, ma il corpus mappa solo tre valori
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert "mappatura Qualifica1 (qualifica_inps=quadro)" in [d.fatto for d in vista.mancanti]
    assert vista.qualifica1 is None


@pytest.mark.parametrize(("iscrizione", "regime_post95"), [("si", "S"), ("no", "N")])
def test_regime_post95_e_dalla_mappatura_del_corpus_per_la_prima_iscrizione(
    registro, orologio, corpus, iscrizione, regime_post95
):
    td_pagato(registro, orologio, corpus)
    registro.registra_codice(R, "prima_iscrizione_dal_1996", iscrizione, date(2026, 1, 1))
    assert denuncia_individuale(registro, corpus, R, MARZO).regime_post95 == regime_post95


def test_senza_la_prima_iscrizione_la_vista_e_una_bozza_che_la_chiede(registro, orologio, corpus):
    td_pagato(registro, orologio, corpus)
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert "prima_iscrizione_dal_1996" in [d.fatto for d in vista.mancanti]
    assert vista.regime_post95 is None and not vista.trasmissibile


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


FESTIVI_2026 = """
[[calendario_festivi]]
anno = 2026
feste = ["01-01", "01-06", "04-25", "05-01", "06-02", "08-15", "10-04", "11-01", "12-08", "12-25", "12-26"]
lunedi_dell_angelo = true
riferimento = "fittizio:festivi-prova"
"""


@pytest.fixture(scope="module")
def corpus_con_festivi():
    """Corpus reale più un calendario dei festivi di prova: il corpus reale non ne dichiara."""
    return Corpus.da_toml(CORPUS.read_text(encoding="utf-8") + FESTIVI_2026)


# Marzo 2026 ha 22 giorni lavorativi (158,4 ore a tempo pieno). Programmazione di prova: tre giorni lun-mer nelle
# settimane del 2-8, 9-15 e 23-29, il solo lunedì 30; la settimana del 15-21 resta interamente senza ore.
GIORNI_DEL_VERTICALE = {date(2026, 3, g) for g in (2, 3, 4, 9, 10, 11, 23, 24, 25, 30)}


def verticale(giorno):
    return Decimal("7.2") if giorno in GIORNI_DEL_VERTICALE else Decimal(0)


def test_il_verticale_ha_la_percentuale_del_mese_dalle_ore_programmate_sulle_ore_lavorabili_del_tempo_pieno(
    registro, orologio, corpus_con_festivi
):
    td_part_time(registro, orologio, corpus_con_festivi, "verticale", "50", verticale)
    vista = denuncia_individuale(registro, corpus_con_festivi, R, MARZO)
    # 10 giorni x 7,2 = 72 ore su 22 x 7,2 = 158,4: 45,4545% -> 4545 centesimi; la percentuale del contratto è 50%.
    assert (vista.qualifica2, vista.perc_part_time, vista.perc_part_time_mese) == ("V", 5000, 4545)
    assert (vista.ore_contribuite, vista.settimane_utili) == (7200, 200)


def test_il_misto_con_giorni_a_orario_diverso_si_distingue_solo_dalle_ore(registro, orologio, corpus_con_festivi):
    cinque_ore = {date(2026, 3, g) for g in (2, 3, 4, 5, 6, 9, 10, 11)}
    sette_ore_e_due = {date(2026, 3, g) for g in (12, 13, 16, 17, 18, 19)}
    ore = lambda giorno: Decimal(5) if giorno in cinque_ore else Decimal("7.2") if giorno in sette_ore_e_due else Decimal(0)
    td_part_time(registro, orologio, corpus_con_festivi, "misto", "60", ore)
    vista = denuncia_individuale(registro, corpus_con_festivi, R, MARZO)
    # 83,2 ore su 158,4 = 52,52% -> 5253 (a giorni sarebbero 14 su 22 = 6364).
    assert (vista.qualifica2, vista.perc_part_time, vista.perc_part_time_mese) == ("M", 6000, 5253)
    assert (vista.ore_contribuite, vista.settimane_utili) == (8320, 231)


PATRONO_DEL_CORPUS = '''
[patrono]
riferimento = "fittizio:patrono-prova"
'''


@pytest.fixture(scope="module")
def corpus_con_patrono():
    return Corpus.da_toml(CORPUS.read_text(encoding="utf-8") + FESTIVI_2026 + PATRONO_DEL_CORPUS)


def giorni_lavorati_di_marzo(registro, orologio, corpus, patrono, dal=date(2026, 1, 1), al=None):
    td_pagato(registro, orologio, corpus, "17")
    if patrono is not None:
        registro.registra_codice(R, "patrono_sede_lavoro", patrono, dal, al)
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    return vista, [g.giorno.day for g in vista.giorni if g.lavorato == "S"]


def test_senza_patrono_registrato_il_tempo_pieno_ha_tutti_i_giorni_lavorativi(
    registro, orologio, corpus_con_patrono
):
    _, senza = giorni_lavorati_di_marzo(registro, orologio, corpus_con_patrono, None)
    assert len(senza) == 22 and 17 in senza


def test_con_il_patrono_il_giorno_della_festa_non_e_lavorato(registro, orologio, corpus_con_patrono):
    vista, con = giorni_lavorati_di_marzo(registro, orologio, corpus_con_patrono, "H501 03-17")
    assert len(con) == 21 and 17 not in con
    assert not any("patrono" in d.fatto for d in vista.mancanti)


def test_il_patrono_di_sabato_non_toglie_giorni(registro, orologio, corpus_con_patrono):
    _, con = giorni_lavorati_di_marzo(registro, orologio, corpus_con_patrono, "H501 03-14")
    assert len(con) == 22


def test_se_il_patrono_cambia_nel_mese_vale_per_ogni_giorno_il_fatto_che_lo_copre(
    registro, orologio, corpus_con_patrono
):
    # Il patrono del 17 vale fino al 10 marzo, poi la sede cambia: il 17 torna lavorativo, il 24 no.
    td_pagato(registro, orologio, corpus_con_patrono, "17")
    registro.registra_codice(R, "patrono_sede_lavoro", "H501 03-17", date(2026, 1, 1), date(2026, 3, 10))
    registro.registra_codice(R, "patrono_sede_lavoro", "H501 03-24", date(2026, 3, 11))
    lavorati = [g.giorno.day for g in denuncia_individuale(registro, corpus_con_patrono, R, MARZO).giorni if g.lavorato == "S"]
    assert 17 in lavorati and 24 not in lavorati and len(lavorati) == 21


def test_un_patrono_nel_rapporto_senza_riferimento_nel_corpus_si_chiede(registro, orologio, corpus_con_festivi):
    vista, _ = giorni_lavorati_di_marzo(registro, orologio, corpus_con_festivi, "H501 03-17")
    assert "patrono (riferimento nel corpus)" in [d.fatto for d in vista.mancanti]
    assert not vista.trasmissibile


def test_un_patrono_malformato_ferma_il_calcolo_con_un_errore_chiaro(registro, orologio, corpus_con_patrono):
    td_pagato(registro, orologio, corpus_con_patrono, "17")
    registro.registra_codice(R, "patrono_sede_lavoro", "San Pietro", date(2026, 1, 1))
    with pytest.raises(ErrorePaghe, match="Patrono"):
        denuncia_individuale(registro, corpus_con_patrono, R, MARZO)


def test_senza_calendario_dei_festivi_il_verticale_chiede_il_dato_invece_di_stimare_le_ore_lavorabili(
    registro, orologio, corpus
):
    td_part_time(registro, orologio, corpus, "verticale", "50", verticale)  # il corpus reale non ha festivi
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert "calendario_festivi 2026" in [d.fatto for d in vista.mancanti]
    assert vista.perc_part_time_mese is None and not vista.trasmissibile


def test_nel_verticale_la_settimana_interamente_senza_ore_programmate_e_d_le_altre_x(
    registro, orologio, corpus_con_festivi
):
    td_part_time(registro, orologio, corpus_con_festivi, "verticale", "50", verticale)
    vista = denuncia_individuale(registro, corpus_con_festivi, R, MARZO)
    # Settimane domenica-sabato; il 1° marzo è domenica: 1-7 (id 10), 8-14, 15-21 (tutta senza ore), 22-28, 29-31.
    assert [(s.id, s.copertura) for s in vista.settimane] == [(10, "X"), (11, "X"), (12, "D"), (13, "X"), (14, "X")]


def ids_settimane(registro, corpus, mese):
    return [s.id for s in denuncia_individuale(registro, corpus, R, mese).settimane]


def test_la_settimana_a_cavallo_di_mese_si_dichiara_in_entrambi_i_mesi(registro, corpus):
    in_servizio_con(registro, "17")
    # La settimana 29 marzo - 4 aprile (id 14) è in marzo per i giorni 29-31 e in aprile per i giorni 1-4.
    assert ids_settimane(registro, corpus, MARZO)[-1] == 14
    assert ids_settimane(registro, corpus, Mese(2026, 4))[0] == 14


def test_l_id_settimana_parte_da_uno_nella_settimana_che_contiene_il_primo_gennaio(registro, corpus):
    in_servizio_con(registro, "17")
    # 1/1/2026 è giovedì: la settimana 28/12-3/1 è la prima. Dicembre 2026 arriva a 53; il 1/1/2027 (venerdì) apre
    # la settimana 27/12-2/1, che è la prima del 2027 e l'ultima del 2026.
    assert ids_settimane(registro, corpus, Mese(2026, 1)) == [1, 2, 3, 4, 5]
    assert ids_settimane(registro, corpus, Mese(2026, 12)) == [49, 50, 51, 52, 53]
    # Il corpus reale non copre il 2027: la prova usa il corpus piccolo.
    assert ids_settimane(registro, Corpus.da_toml(CORPUS_PICCOLO), Mese(2027, 1)) == [1, 2, 3, 4, 5, 6]


def test_nel_verticale_lavorato_e_s_nei_giorni_con_ore_programmate_e_n_negli_altri(
    registro, orologio, corpus_con_festivi
):
    td_part_time(registro, orologio, corpus_con_festivi, "verticale", "50", verticale)
    vista = denuncia_individuale(registro, corpus_con_festivi, R, MARZO)
    assert [g.giorno for g in vista.giorni] == MARZO.giorni()
    assert {g.giorno for g in vista.giorni if g.lavorato == "S"} == GIORNI_DEL_VERTICALE
    assert {g.lavorato for g in vista.giorni if g.giorno not in GIORNI_DEL_VERTICALE} == {"N"}


def test_a_tempo_pieno_lavorato_e_s_nei_giorni_lavorativi_non_festivi_del_calendario_del_corpus(
    registro, corpus_con_festivi
):
    in_servizio_con(registro, "17")
    vista = denuncia_individuale(registro, corpus_con_festivi, R, Mese(2026, 4))
    lavorati = {g.giorno for g in vista.giorni if g.lavorato == "S"}
    assert len(lavorati) == 21  # 22 giorni da lunedì a venerdì, meno il lunedì dell'Angelo (6 aprile)
    assert date(2026, 4, 6) not in lavorati and date(2026, 4, 3) in lavorati and date(2026, 4, 4) not in lavorati


def test_il_verticale_con_il_mese_interamente_non_lavorato_e_dr00_con_tutte_le_settimane_d_e_i_giorni_n(
    registro, orologio, corpus_con_festivi
):
    td_part_time(registro, orologio, corpus_con_festivi, "verticale", "50", lambda giorno: Decimal(0))
    # La settimana 29/03-04/04 è a cavallo: senza ore a marzo, la sua copertura legge anche i giorni di aprile.
    registra_programmazione(registro, R, {date(2026, 4, g): Decimal(0) for g in range(1, 5)}, ATTO_PROGRAMMAZIONE)
    vista = denuncia_individuale(registro, corpus_con_festivi, R, MARZO)
    assert vista.tipo_lav_stat == "DR00"
    assert {s.copertura for s in vista.settimane} == {"D"} and {g.lavorato for g in vista.giorni} == {"N"}
    assert vista.perc_part_time_mese == 0 and (vista.ore_contribuite, vista.settimane_utili) == (0, 0)


def test_dr00_non_si_usa_nei_mesi_con_ore_programmate_ne_a_tempo_pieno(registro, orologio, corpus_con_festivi):
    td_part_time(registro, orologio, corpus_con_festivi, "verticale", "50", verticale)
    assert denuncia_individuale(registro, corpus_con_festivi, R, MARZO).tipo_lav_stat is None


def individuale(rapporto, contributo, mese=MARZO):
    return DenunciaIndividuale(rapporto, mese, contributo=None if contributo is None else Decimal(contributo))


def test_la_denuncia_aziendale_quadra_il_numero_delle_individuali_e_il_totale_a_debito_all_euro():
    quadratura = denuncia_aziendale([individuale("A", "33.04"), individuale("B", "0.46"), individuale("C", None)])
    # 33,50 al centesimo di euro: la metà sale (ROUND_HALF_UP) -> 34; la vista senza imponibile conta ma non somma.
    assert (quadratura.mese, quadratura.num_den_indiv, quadratura.totale_a_debito) == (MARZO, 3, 34)


def test_la_denuncia_aziendale_non_mescola_mesi_diversi():
    with pytest.raises(ErrorePaghe, match="mesi diversi"):
        denuncia_aziendale([individuale("A", "1"), individuale("B", "1", Mese(2026, 4))])


def td_trasmissibile(registro, orologio, corpus, impiego="17", termine="no"):
    """Un tempo determinato a tempo pieno con tutti i fatti che la vista chiede, pagato a marzo."""
    in_servizio_con(registro, impiego)
    registro.registra_codice(R, "termine_per_sostituzione", termine, date(2026, 1, 1))
    registro.registra_codice(R, "prima_iscrizione_dal_1996", "no", date(2026, 1, 1))
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))


def test_l_invio_registra_un_esito_dichiarato_con_le_righe_pagate_dell_imponibile(registro, orologio, corpus_con_festivi):
    td_trasmissibile(registro, orologio, corpus_con_festivi)
    orologio.vai(4, 2)
    invio = invia_denuncia_individuale(registro, corpus_con_festivi, "DI-2026-03-R", "adattatore-prova", R, MARZO)
    esito = registro.esito(invio.esito_id)
    assert esito.tipo is TipoEsito.DICHIARATO
    assert {riga.istituto for riga in esito.righe} == {"tabellare_istruttori", "comparto_istruttori"}  # solo ciò che concorre alla base cpdel
    assert (invio.rapporto, invio.mese, invio.vista.imponibile, invio.vista.contributo) == (R, MARZO, 2052, Decimal("33.04"))
    assert invio.vista == denuncia_individuale(registro, corpus_con_festivi, R, MARZO)


def invia(registro, corpus, invio_id="DI-2026-03-R"):
    return invia_denuncia_individuale(registro, corpus, invio_id, "adattatore-prova", R, MARZO)


def test_lo_stesso_invio_ripetuto_non_ha_effetto_e_con_una_vista_diversa_e_rifiutato(registro, orologio, corpus_con_festivi):
    td_trasmissibile(registro, orologio, corpus_con_festivi)
    orologio.vai(4, 2)
    primo = invia(registro, corpus_con_festivi)
    assert invia(registro, corpus_con_festivi) == primo
    assert len(registro.esiti(TipoEsito.DICHIARATO, registro.adesso())) == 1
    orologio.vai(4, 3)
    registro.registra_codice(R, "termine_per_sostituzione", "si", date(2026, 1, 1))  # cambia Qualifica3
    with pytest.raises(ErroreRegistro, match="stesso identificativo con contenuto diverso"):
        invia(registro, corpus_con_festivi)


def test_una_vista_con_dati_mancanti_non_si_invia_e_non_registra_nulla(registro, orologio, corpus_con_festivi):
    td_pagato(registro, orologio, corpus_con_festivi)  # senza i fatti di inquadramento che la vista chiede
    with pytest.raises(VistaFerma, match="dato mancante termine_per_sostituzione"):
        invia(registro, corpus_con_festivi)
    assert registro.esiti(TipoEsito.DICHIARATO, registro.adesso()) == [] and registro.evento("denuncia_individuale:DI-2026-03-R") is None


def test_dopo_l_invio_un_fatto_che_cambia_la_vista_si_segnala_e_la_correzione_e_un_nuovo_invio(
    registro, orologio, corpus_con_festivi
):
    td_trasmissibile(registro, orologio, corpus_con_festivi)
    orologio.vai(4, 2)
    primo = invia(registro, corpus_con_festivi)
    assert segnala_scostamento_invio(registro, corpus_con_festivi, R, MARZO) == ()
    orologio.vai(4, 3)
    registro.registra_codice(R, "termine_per_sostituzione", "si", date(2026, 1, 1))
    scostamento, = segnala_scostamento_invio(registro, corpus_con_festivi, R, MARZO)
    assert (scostamento.campo, scostamento.inviato, scostamento.attuale) == ("qualifica3", "D", "A")
    orologio.vai(4, 4)
    secondo = invia(registro, corpus_con_festivi, "DI-2026-03-R-bis")
    assert secondo.vista.qualifica3 == "A" and secondo.esito_id != primo.esito_id
    assert segnala_scostamento_invio(registro, corpus_con_festivi, R, MARZO) == ()
    assert leggi_invio_denuncia_individuale(registro, "DI-2026-03-R").vista.qualifica3 == "D"  # il primo non è cambiato


FEBBRAIO = Mese(2026, 2)


def test_la_base_cpdel_pagata_a_un_tempo_determinato_non_in_servizio_e_un_assenza_che_nomina_il_rapporto(
    registro, orologio, corpus_con_festivi
):
    assumi(registro, al=date(2026, 2, 28), senza=("tipo_impiego",))
    registro.registra_codice(R, "tipo_impiego", "17", date(2026, 1, 1), date(2026, 2, 28))
    paga(registro, orologio, stipendi(registro, corpus_con_festivi, FEBBRAIO), date(2026, 3, 27))  # arretrato pagato a marzo
    assert denuncia_individuale(registro, corpus_con_festivi, R, MARZO) is None  # non è in servizio a marzo
    assenza, = controlla_completezza(registro, corpus_con_festivi, MARZO)
    assert assenza.rapporto == R and "2051.69" in assenza.motivo and "non in servizio" in assenza.motivo


def test_un_tempo_determinato_in_servizio_senza_denuncia_individuale_e_un_assenza(registro, orologio):
    corpus = Corpus.da_toml(CORPUS_SENZA_CPDEL)
    registro.registra_codice(R, "tipo_impiego", "17", date(2026, 1, 1))
    registro.registra_fatto(R, "compenso_mensile", "1300", date(2026, 1, 1))
    paga(registro, orologio, calcola(registro, corpus, R, MARZO), date(2026, 3, 27))
    assenza, = controlla_completezza(registro, corpus, MARZO)
    assert assenza.rapporto == R and "senza DenunciaIndividuale" in assenza.motivo and "non in CPDEL" in assenza.motivo


def test_un_tempo_determinato_completo_non_ha_assenze(registro, orologio, corpus_con_festivi):
    td_trasmissibile(registro, orologio, corpus_con_festivi)
    assert controlla_completezza(registro, corpus_con_festivi, MARZO) == ()


def test_l_assenza_di_un_altro_tempo_determinato_ferma_l_invio_senza_registrare_nulla(registro, orologio, corpus_con_festivi):
    altro = "RAPPORTO-2"
    registro.registra_codice_persona("PERSONA-2", "codice_fiscale", "RSSMRA85C01H501D", date(1985, 3, 1))
    registro.collega_rapporto(altro, "PERSONA-2", date(2026, 1, 1))
    for tipo, valore in (("tipo_impiego", "17"), ("tipo_servizio", "4"), ("contratto", "RALN"), ("qualifica", "0IR000"),
                         ("area", "istruttori"), ("regime_fine_servizio", "3")):
        registro.registra_codice(altro, tipo, valore, date(2026, 1, 1), date(2026, 2, 28))
    arretrato = calcola(registro, corpus_con_festivi, altro, FEBBRAIO)
    td_trasmissibile(registro, orologio, corpus_con_festivi)  # R, completo
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 3, 27), arretrato)
    registro.registra_pagamento(altro, esito.id, date(2026, 3, 27))  # il secondo è pagato a marzo da cessato
    orologio.vai(4, 2)
    with pytest.raises(VistaFerma, match=r"RAPPORTO-2.*non in servizio"):
        invia(registro, corpus_con_festivi)
    assert registro.esiti(TipoEsito.DICHIARATO, registro.adesso()) == []


def test_un_dato_che_cambia_nel_mese_ferma_la_vista_perche_servirebbero_due_denunce_individuali(
    registro, orologio, corpus_con_festivi
):
    in_servizio_con(registro, "18")
    registro.registra_fatto(R, "part_time", "50", date(2026, 1, 1))
    registro.registra_codice(R, "tipo_part_time", "orizzontale", date(2026, 1, 1), date(2026, 3, 15))
    registro.registra_codice(R, "tipo_part_time", "verticale", date(2026, 3, 16))
    registra_programmazione(registro, R, {g: Decimal(4) for g in MARZO.giorni()}, ATTO_PROGRAMMAZIONE)
    paga(registro, orologio, stipendi(registro, corpus_con_festivi, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus_con_festivi, R, MARZO)
    fermo, = vista.fermi
    assert "tipo_part_time" in fermo.motivo and "cambia nel mese" in fermo.motivo and not vista.trasmissibile


def test_il_corpus_rifiuta_due_mappature_di_fatto_sovrapposte_e_il_riferimento_fittizio_nel_corpus_reale():
    sovrapposta = MAPPATURA_PROVA + MAPPATURA_PROVA.replace("2026-01-01", "2026-06-01").replace("2026-12-31", "2027-12-31")
    with pytest.raises(ErroreCorpus, match="vigenze sovrapposte"):
        Corpus.da_toml(CORPUS_PICCOLO + sovrapposta)
    with pytest.raises(ErroreCorpus, match="fittizio"):
        Corpus.da_toml(CORPUS_PICCOLO.replace("fittizio:", "prassi:inps:circolare:2026-01-30;6~par5 + fittizio:") + MAPPATURA_PROVA, reale=True)


def test_una_qualifica_inps_che_cambia_nel_mese_ferma_la_vista(registro, orologio, corpus):
    # Qualifica1 è un criterio di univocità: operaio fino al 15, impiegato dal 16 richiederebbe due denunce (#105).
    in_servizio_con(registro, "17", qualifica_inps=None)
    registro.registra_codice(R, "qualifica_inps", "operaio", date(2026, 1, 1), date(2026, 3, 15))
    registro.registra_codice(R, "qualifica_inps", "impiegato", date(2026, 3, 16))
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert any("qualifica_inps" in f.motivo and "cambia nel mese" in f.motivo for f in vista.fermi)
    assert not vista.trasmissibile


def test_una_qualifica_inps_inserita_dopo_l_inizio_del_mese_non_vale_per_tutto_il_mese(registro, orologio, corpus):
    # Il fatto manca nei primi giorni del mese: niente default, la vista non si trasmette.
    in_servizio_con(registro, "17", qualifica_inps=None)
    registro.registra_codice(R, "qualifica_inps", "impiegato", date(2026, 3, 10))
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert not vista.trasmissibile
