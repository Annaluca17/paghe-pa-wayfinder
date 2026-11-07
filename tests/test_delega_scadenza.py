"""Scadenza del versamento F24EP da regola datata e calendario dei festivi (ADR 0023). Dati fittizi.

Le date attese sono contate a mano sul calendario: 16 aprile 2026 giovedì, 16 maggio 2026 sabato,
16 agosto 2026 domenica, 16 gennaio 2027 sabato, 16 maggio 2027 domenica, 20 agosto 2028 domenica.
"""

from datetime import date

import pytest

from paghe import Mese
from paghe.delega import calcola_scadenza
from paghe.errori import ParametroMancante

from materiale_delega import corpus_scadenza


def scadenza(anno, mese, **kwargs):
    return calcola_scadenza(corpus_scadenza(**kwargs), Mese(anno, mese))


def test_la_scadenza_e_il_16_del_mese_successivo_al_pagamento():
    s = scadenza(2026, 3)
    assert s.data == date(2026, 4, 16) and s.nominale == date(2026, 4, 16)
    assert not s.proroga_applicata and s.avvisi == ()


def test_la_scadenza_porta_il_riferimento_della_regola_usata():
    assert scadenza(2026, 3).riferimento == "fittizio:scadenza-2026"


def test_il_16_di_sabato_slitta_al_lunedi():
    assert scadenza(2026, 4).data == date(2026, 5, 18)


def test_il_16_di_domenica_slitta_al_lunedi():
    s = scadenza(2027, 4)
    assert (s.nominale, s.data) == (date(2027, 5, 16), date(2027, 5, 17))


def test_un_festivo_infrasettimanale_sposta_la_scadenza():
    s = scadenza(2026, 3, extra_festivi=("2026-04-16",))
    assert (s.nominale, s.data) == (date(2026, 4, 16), date(2026, 4, 17))


def test_lo_slittamento_prosegue_se_il_giorno_dopo_e_ancora_festivo():
    # 16 maggio 2026 sabato, lunedì 18 festivo: martedì 19
    assert scadenza(2026, 4, extra_festivi=("2026-05-18",)).data == date(2026, 5, 19)


def test_il_pagamento_di_luglio_scade_il_20_agosto_per_prassi():
    s = scadenza(2026, 7)
    assert (s.nominale, s.data, s.proroga_applicata) == (date(2026, 8, 16), date(2026, 8, 20), True)
    assert s.fonte_proroga == "prassi" and s.riferimento_proroga == "fittizio:proroga-2026"
    assert [a.tipo for a in s.avvisi] == ["scadenza_per_prassi"]


def test_la_proroga_vale_per_le_scadenze_dal_primo_al_venti_agosto_e_non_per_le_altre():
    assert not scadenza(2026, 8).proroga_applicata  # settembre
    assert scadenza(2026, 8).data == date(2026, 9, 16)
    assert not scadenza(2026, 6).proroga_applicata  # luglio


def test_se_il_20_agosto_e_domenica_si_applica_lo_slittamento_e_si_segnala_il_caso():
    s = scadenza(2028, 7)
    assert (s.nominale, s.data) == (date(2028, 8, 16), date(2028, 8, 21))
    assert sorted(a.tipo for a in s.avvisi) == ["proroga_su_festivo", "scadenza_per_prassi"]
    caso = next(a for a in s.avvisi if a.tipo == "proroga_su_festivo")
    assert "20 agosto" in caso.messaggio and "fonte" in caso.messaggio


def test_dal_2027_cambia_il_riferimento_e_non_il_contenuto():
    prima, dopo = scadenza(2026, 11), scadenza(2026, 12)
    assert (prima.riferimento, prima.data) == ("fittizio:scadenza-2026", date(2026, 12, 16))
    assert (dopo.riferimento, dopo.data) == ("fittizio:scadenza-2027", date(2027, 1, 18))
    assert scadenza(2027, 7).riferimento_proroga == "fittizio:proroga-2027"


def test_dicembre_scade_a_gennaio_dell_anno_dopo():
    assert scadenza(2026, 12).nominale == date(2027, 1, 16)


def test_senza_regola_vigente_la_scadenza_non_si_calcola():
    with pytest.raises(ParametroMancante, match="Scadenza F24EP"):
        scadenza(2019, 1)


def test_senza_calendario_dei_festivi_dell_anno_la_scadenza_non_si_calcola():
    with pytest.raises(ParametroMancante, match="2029"):
        scadenza(2028, 12)  # scade nel gennaio 2029, calendario non dichiarato
