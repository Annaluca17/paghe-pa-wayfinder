"""Esito 730-4 minimo (ticket #71, CONTEXT: Esito 730-4). Dati fittizi.

Fatto della persona con la provenienza, l'importo del rimborso e l'anno dei redditi dichiarati. Un 730-4 rettificativo
lo sostituisce con un nuovo fatto. Rate, acconti e debiti sono fuori.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto
from paghe.errori import ErroreRegistro
from paghe.esito_730_4 import Esito730, esito_730_4

from materiale_proposta import P

D = Decimal
ATTO = Atto("ente:ente_di_prova:comunicazione.730:2026-06-20;1", date(2026, 6, 20))
ATTO_RETTIFICA = Atto("ente:ente_di_prova:comunicazione.730:2026-07-10;2", date(2026, 7, 10))
GIORNO = date(2026, 8, 1)


def test_l_esito_730_4_e_un_fatto_della_persona_con_provenienza_rimborso_e_anno_dei_redditi(registro):
    registro.registra_esito_730_4(P, D("150.00"), 2025, date(2026, 6, 20), ATTO)
    esito = esito_730_4(registro, P, GIORNO, registro.adesso())
    assert (esito.rimborso, esito.anno_redditi) == (D("150.00"), 2025)
    assert esito.fatto.atto == ATTO and esito.fatto.soggetto == "persona"


def test_senza_esito_730_4_non_c_e_nulla_da_leggere(registro):
    assert esito_730_4(registro, P, GIORNO, registro.adesso()) is None


def test_un_730_4_rettificativo_sostituisce_il_precedente_con_un_nuovo_fatto(registro, orologio):
    vecchio = registro.registra_esito_730_4(P, D("150.00"), 2025, date(2026, 6, 20), ATTO)
    orologio.avanza()
    nuovo = registro.registra_esito_730_4(P, D("120.00"), 2025, date(2026, 6, 20), ATTO_RETTIFICA)
    esito = esito_730_4(registro, P, GIORNO, registro.adesso())
    assert esito.rimborso == D("120.00") and esito.fatto.id == nuovo.id != vecchio.id
    # Il registro non perde il vecchio: com'era noto prima della rettifica, si rilegge.
    prima = esito_730_4(registro, P, GIORNO, vecchio.registrato_il)
    assert prima.rimborso == D("150.00")


@pytest.mark.parametrize("rimborso", ["0", "-10"])
def test_un_importo_che_non_e_un_rimborso_e_fuori(registro, rimborso):
    with pytest.raises(ErroreRegistro, match="rimborso"):
        registro.registra_esito_730_4(P, D(rimborso), 2025, date(2026, 6, 20), ATTO)


def test_l_esito_730_4_vuole_il_documento_di_origine(registro):
    with pytest.raises(ErroreRegistro, match="documento"):
        registro.registra_esito_730_4(P, D("150"), 2025, date(2026, 6, 20), None)


def test_l_anno_dei_redditi_e_un_anno(registro):
    with pytest.raises(ErroreRegistro, match="anno"):
        registro.registra_esito_730_4(P, D("150"), "2025", date(2026, 6, 20), ATTO)
