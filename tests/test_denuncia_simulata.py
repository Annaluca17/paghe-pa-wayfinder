"""Denuncia in simulazione: come se un pagamento fosse già avvenuto, senza scrivere nel registro (ADR 0025). Dati fittizi."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, TipoEsito, calcola, calcola_denuncia, emetti_esito
from paghe.errori import ErroreCalcolo

from conftest import CORPUS_BASE

R = "RAPPORTO-1"
FEB = Mese(2026, 2)

CON_CONTRIBUTI = CORPUS_BASE + """
[periodo_dichiarato]
servizio = "compenso_mensile"

[[base]]
nome = "pens"
riferimento = "fittizio:base-pens"

[[regola]]
istituto = "contributo"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:contributo"
formula = "arrotonda(base.pens * parametro.aliquota, 2)"
maturazione = "periodo"

[[concorso]]
istituto = "compenso"
basi = ["pens"]
misura = "intero"
dal = 2026-01-01
riferimento = "fittizio:concorso-compenso"
"""


@pytest.fixture
def cassa():
    return Corpus.da_toml(CON_CONTRIBUTI)


def compenso(registro, cassa, mensile="1000", mese=FEB):
    registro.registra_fatto(R, "compenso_mensile", mensile, date(2026, 1, 1))
    return [riga for riga in calcola(registro, cassa, R, mese) if riga.istituto == "compenso"]


def ipotizza(righe, giorno):
    return tuple(replace(riga, data_pagamento=giorno) for riga in righe)


def senza_basi(denuncia):
    return all(not periodo.basi and not periodo.contributi for periodo in denuncia.periodi)


def contributo(denuncia):
    (periodo,) = denuncia.periodi
    return next(riga.valore for riga in periodo.contributi if riga.istituto == "contributo")


def test_la_simulazione_calcola_i_contributi_come_se_il_pagamento_fosse_avvenuto(registro, cassa):
    righe = compenso(registro, cassa)
    assert senza_basi(calcola_denuncia(registro, cassa, R, FEB))
    simulata = calcola_denuncia(registro, cassa, R, FEB, ipotetiche=ipotizza(righe, date(2026, 2, 27)))
    assert simulata.periodi[0].base("pens").valore == Decimal("1000.00")
    assert contributo(simulata) == Decimal("100.00")


def test_la_simulazione_non_scrive_nel_registro(registro, cassa, orologio):
    righe = compenso(registro, cassa)
    calcola_denuncia(registro, cassa, R, FEB, ipotetiche=ipotizza(righe, date(2026, 2, 27)))
    assert registro.esiti(TipoEsito.PAGATO, orologio()) == []
    assert registro.pagamenti(R, orologio()) == {}
    assert senza_basi(calcola_denuncia(registro, cassa, R, FEB))


def test_la_simulazione_si_somma_a_cio_che_e_gia_pagato_nel_mese(registro, cassa, orologio):
    righe = compenso(registro, cassa)
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 20), righe)
    registro.registra_pagamento(R, esito.id, date(2026, 2, 20))
    rimborso = replace(righe[0], istituto="compenso", periodo=righe[0].periodo, valore=Decimal("500"))
    simulata = calcola_denuncia(registro, cassa, R, FEB, ipotetiche=ipotizza([rimborso], date(2026, 2, 27)))
    assert simulata.periodi[0].base("pens").valore == Decimal("1500.00")
    assert contributo(simulata) == Decimal("150.00")


def test_una_riga_ipotetica_di_un_altro_mese_non_entra(registro, cassa):
    righe = compenso(registro, cassa)
    simulata = calcola_denuncia(registro, cassa, R, FEB, ipotetiche=ipotizza(righe, date(2026, 3, 2)))
    assert senza_basi(simulata)


def test_le_righe_ipotetiche_derivate_e_di_altri_rapporti_non_entrano_nelle_basi(registro, cassa):
    righe = compenso(registro, cassa)
    derivata = replace(righe[0], derivazione=replace(righe[0].derivazione, maturazione="ritenuta"), valore=Decimal("99"))
    altro = replace(righe[0], rapporto="RAPPORTO-2", valore=Decimal("777"))
    ipotetiche = ipotizza([*righe, derivata, altro], date(2026, 2, 27))
    simulata = calcola_denuncia(registro, cassa, R, FEB, ipotetiche=ipotetiche)
    assert simulata.periodi[0].base("pens").valore == Decimal("1000.00")


def test_una_riga_ipotetica_senza_data_di_pagamento_e_rifiutata(registro, cassa):
    righe = compenso(registro, cassa)
    with pytest.raises(ErroreCalcolo, match="data di pagamento"):
        calcola_denuncia(registro, cassa, R, FEB, ipotetiche=righe)
