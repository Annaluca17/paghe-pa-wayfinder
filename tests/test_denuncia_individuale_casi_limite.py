"""DenunciaIndividuale: casi limite della rilettura del #77 (ADR 0027). Dati di fantasia."""

from datetime import date
from decimal import Decimal

from paghe import Mese, denuncia_individuale
from paghe.part_time import registra_programmazione
from test_denuncia_individuale import ATTO_PROGRAMMAZIONE, FESTIVI_2026, MARZO, corpus, corpus_con_festivi  # noqa: F401
from test_lista_pos_pa import R, assumi, paga, stipendi

APRILE = Mese(2026, 4)


def part_time(registro, tipo, ore_del_giorno, mesi, dal=date(2026, 1, 1)):
    assumi(registro, dal=dal, senza=("tipo_impiego",))
    registro.registra_codice(R, "tipo_impiego", "18", dal)
    registro.registra_fatto(R, "part_time", "50", dal)
    registro.registra_codice(R, "tipo_part_time", tipo, dal)
    registro.registra_codice(R, "qualifica_inps", "impiegato", dal)
    registro.registra_codice(R, "termine_per_sostituzione", "no", dal)
    registro.registra_codice(R, "prima_iscrizione_dal_1996", "no", dal)
    giorni = {g: ore_del_giorno(g) for mese in mesi for g in mese.giorni() if g >= dal}
    registra_programmazione(registro, R, giorni, ATTO_PROGRAMMAZIONE)


def test_un_tempo_determinato_che_diventa_indeterminato_nel_mese_ferma_la_vista(registro, orologio, corpus):
    # Stabilizzato dal 16/03: la seconda metà del mese non è un tempo determinato e non va nell'Imponibile NASpI.
    assumi(registro, senza=("tipo_impiego",))
    registro.registra_codice(R, "tipo_impiego", "17", date(2026, 1, 1), date(2026, 3, 15))
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 3, 16))
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus, R, MARZO)
    assert vista is not None and vista.fermi
    assert any("tipo_impiego" in f.motivo for f in vista.fermi)


def test_una_percentuale_del_mese_oltre_il_cento_per_cento_non_e_trasmissibile(registro, orologio, corpus_con_festivi):
    # Misto con 8 ore in ogni giorno lavorativo: 176 ore su 158,4 del tempo pieno = 111,11%.
    part_time(registro, "misto", lambda g: Decimal(8) if g.weekday() < 5 else Decimal(0), [MARZO])
    paga(registro, orologio, stipendi(registro, corpus_con_festivi, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus_con_festivi, R, MARZO)
    assert vista.perc_part_time_mese is None
    assert not vista.mancanti and any("oltre il 100%" in motivo for motivo in vista.bozza)


def test_la_settimana_a_cavallo_ha_la_stessa_copertura_nei_due_mesi(registro, orologio, corpus_con_festivi):
    # Verticale giovedì e venerdì: la settimana 29/03-04/04 (id 14) ha lavoro solo il 2 e il 3 aprile.
    # Non è «interamente non lavorata»: non può essere D a marzo e X ad aprile.
    part_time(registro, "verticale", lambda g: Decimal("7.2") if g.weekday() in (3, 4) else Decimal(0), [MARZO, APRILE])
    paga(registro, orologio, stipendi(registro, corpus_con_festivi, MARZO), date(2026, 3, 27))
    marzo = {s.id: s.copertura for s in denuncia_individuale(registro, corpus_con_festivi, R, MARZO).settimane}
    aprile = {s.id: s.copertura for s in denuncia_individuale(registro, corpus_con_festivi, R, APRILE).settimane}
    assert marzo[14] == aprile[14] == "X"


def test_assunto_a_meta_mese_la_percentuale_e_le_settimane_contano_solo_i_giorni_di_rapporto(
    registro, orologio, corpus_con_festivi
):
    # Dal 16/03, lunedì-mercoledì: 8 giorni programmati (57,6 ore) su 12 lavorativi di rapporto (86,4 ore) = 66,67%.
    part_time(registro, "verticale", lambda g: Decimal("7.2") if g.weekday() < 3 else Decimal(0), [MARZO], dal=date(2026, 3, 16))
    paga(registro, orologio, stipendi(registro, corpus_con_festivi, MARZO), date(2026, 3, 27))
    vista = denuncia_individuale(registro, corpus_con_festivi, R, MARZO)
    assert vista.perc_part_time_mese == 6667
    assert [s.id for s in vista.settimane] == [12, 13, 14]
    assert vista.giorni[0].giorno == date(2026, 3, 16)
