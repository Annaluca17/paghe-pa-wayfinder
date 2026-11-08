"""Casi limite del prospetto paga (rilettura del ticket #86, ADR 0030): un prospetto per rapporto e per pagamento, mai per mese."""

from datetime import date
from decimal import Decimal

from test_prospetto_paga import DIP, NOVEMBRE, consegna, corpus, dipendente, paga  # noqa: F401 (corpus e' una fixture)

from paghe import Mese, TipoEsito
from paghe.prospetto_paga import prospetto_paga, segnala_scostamento_prospetto

OTTOBRE = Mese(2026, 10)
ARRETRATO = date(2026, 11, 10)
STIPENDIO = date(2026, 11, 27)


def due_pagamenti_nel_mese(registro, corpus, orologio):
    dipendente(registro)
    arretrato = paga(registro, orologio, corpus, DIP, mese=OTTOBRE, giorno=ARRETRATO)
    stipendio = paga(registro, orologio, corpus, DIP, mese=NOVEMBRE, giorno=STIPENDIO)
    return arretrato, stipendio


def test_due_pagamenti_nello_stesso_mese_danno_due_prospetti_ognuno_con_le_sue_righe_e_il_suo_netto(registro, corpus, orologio):
    arretrato, stipendio = due_pagamenti_nel_mese(registro, corpus, orologio)
    primo = prospetto_paga(registro, corpus, DIP, arretrato.id)
    secondo = prospetto_paga(registro, corpus, DIP, stipendio.id)

    assert (primo.data_pagamento, secondo.data_pagamento) == (ARRETRATO, STIPENDIO)
    assert {str(r.periodo) for r in primo.righe_sul_netto} == {"2026-10-01/2026-10-31"}
    assert {str(r.periodo) for r in secondo.righe_sul_netto} == {"2026-11-01/2026-11-30"}
    # Ogni netto e' la somma delle sole righe del suo esito: nessuna somma del mese.
    assert primo.netto == sum((r.valore for r in arretrato.righe), Decimal(0))
    assert secondo.netto == sum((r.valore for r in stipendio.righe), Decimal(0))


def test_la_consegna_e_lo_scostamento_di_un_pagamento_non_toccano_l_altro(registro, corpus, orologio):
    arretrato, stipendio = due_pagamenti_nel_mese(registro, corpus, orologio)
    prima = consegna(registro, corpus, arretrato, chiave="consegna-arretrato")
    seconda = consegna(registro, corpus, stipendio, chiave="consegna-stipendio")

    assert prima.esito.id != seconda.esito.id
    assert {r.periodo.dal.month for r in prima.esito.righe} == {10}
    assert {r.periodo.dal.month for r in seconda.esito.righe} == {11}
    assert segnala_scostamento_prospetto(registro, corpus, DIP, arretrato.id) == ()
    assert segnala_scostamento_prospetto(registro, corpus, DIP, stipendio.id) == ()
    assert len(registro.esiti(TipoEsito.DICHIARATO, registro.adesso())) == 2
