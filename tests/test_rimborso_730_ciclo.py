"""Il rimborso da 730-4 dal fatto alla delega versata (ticket #71). Dati fittizi.

Stipendio di 1500 ad agosto 2026, pagato il 27: ritenuta 100,00, contributi 480,00 (lavoratore 120 e ente 360). Il
rimborso di 150,00 e' una riga sola: sul netto del lavoratore e, con l'anno dei redditi dichiarati, credito della delega.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese, TipoEsito
from paghe.errori import ErroreRegistro
from paghe.delega import costruisci_delega, registra_versamento_delega, trasmetti_delega
from paghe.esito_730_4 import rimborso_730_4
from paghe.proposta import conferma_versione, emetti_versione, registra_pagamento_eseguito

from controlli_f24ep import controlla
from materiale_delega import ADATTATORE, dati_ente
from materiale_proposta import P, R, assumi, stipendio
from materiale_rimborso import ATTO_730_4, corpus_rimborso

AGO = Mese(2026, 8)
VALUTA = date(2026, 8, 27)
D = Decimal


@pytest.fixture
def corpus():
    return corpus_rimborso()


@pytest.fixture
def pagato(registro, corpus, orologio):
    dati_ente(registro)
    registro.registra_data_versamento(AGO, date(2026, 9, 16))
    assumi(registro)
    registro.registra_esito_730_4(P, D("150.00"), 2025, date(2026, 6, 20), ATTO_730_4)
    importi = stipendio(registro, corpus, AGO) + [rimborso_730_4(registro, corpus, R, VALUTA)]
    orologio.vai(8, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    conferma_versione(registro, versione.id)
    registra_pagamento_eseguito(registro, corpus, "pag-1", ADATTATORE, versione.id, VALUTA, versione.rapporti)
    return versione


def test_il_rimborso_e_sul_netto_del_lavoratore_verso_il_beneficiario(pagato):
    (riga,) = [r for r in pagato.righe if r.istituto == "rimborso_730_4"]
    assert (riga.natura, riga.effetto, riga.destinatario, riga.canale) == ("rimborso_730", "piu", "beneficiario", "accredito")
    assert [n.netto for n in pagato.netti] == [D("1430.00")]  # 1500 - 120 - 100 + 150


def test_la_delega_porta_lo_stesso_rimborso_a_credito_con_l_anno_dei_redditi(registro, corpus, pagato):
    d = costruisci_delega(registro, corpus, AGO)
    righe = {(r.tributo, r.rif_b): (r.debito, r.credito) for r in d.righe}
    assert righe == {
        ("100E", "2026"): (D("100.00"), D("0")),
        ("P201", "082026"): (D("480.00"), D("0")),
        ("150E", "2025"): (D("0"), D("150.00")),
    }
    assert d.saldo == D("430.00") and d.residui == () and d.pronta


def test_la_delega_si_trasmette_e_si_versa_e_il_rimborso_non_si_conta_due_volte(registro, corpus, orologio, pagato):
    orologio.vai(9, 10)
    t = trasmetti_delega(registro, corpus, "DELEGA-AGO", ADATTATORE, AGO)
    assert controlla(t.file) == ([], [])
    esito = registra_versamento_delega(registro, "ver-1", ADATTATORE, "DELEGA-AGO", date(2026, 9, 16))
    assert esito.tipo is TipoEsito.VERSATO
    assert {r.istituto: r.valore for r in esito.righe}["rimborso_730_4"] == D("150.00")
    # Il rimborso e' pagato: il calcolo successivo non lo riemette (stessa chiave gia' in un esito pagato).
    orologio.vai(9, 20)
    importi = [rimborso_730_4(registro, corpus, R, date(2026, 9, 27))]
    with pytest.raises(ErroreRegistro, match="Nessun rapporto"):
        emetti_versione(registro, corpus, date(2026, 9, 27), importi)
