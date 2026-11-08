"""Casi limite della disponibilità e dei fermi per capienza (ADR 0031, rilettura #62). Dati fittizi.

Il denaro reale vince (ADR 0025): una versione pagata consuma l'impegno per i soli rapporti pagati,
anche se nel frattempo è diventata superata; i rapporti non pagati ripartono con una nuova versione.
"""

from datetime import date
from decimal import Decimal

from paghe import Mese
from paghe.impegni import disponibilita_residua
from paghe.proposta import conferma_versione, emetti_versione, registra_pagamento_eseguito

from materiale_impegni import PIANO_ENTE, impegno
from materiale_proposta import P2, R, R2, assumi_senza_impegni, corpus_p, stipendio  # noqa: F401 (fixture)

VALUTA = date(2026, 2, 27)
FEB = Mese(2026, 2)


def _impegni(registro, disponibilita="10000"):
    impegno(registro, "I-S", 1, 2026, disponibilita=disponibilita)
    impegno(registro, "I-E", 2, 2026, disponibilita="100000", piano=PIANO_ENTE)


def test_una_versione_superata_ma_pagata_consuma_l_impegno(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    _impegni(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    conferma_versione(registro, versione.id)
    orologio.avanza()
    registro.registra_stato_versione(versione.id, "superata", "fatto cambiato dopo la conferma")
    orologio.avanza()
    registra_pagamento_eseguito(registro, corpus_p, "PAG-1", "adattatore-prova", versione.id, VALUTA, [R])
    assert disponibilita_residua(registro, 2026, 1) == Decimal("8500")


def test_una_versione_pagata_in_parte_consuma_solo_i_rapporti_pagati(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    assumi_senza_impegni(registro, R2, P2)
    _impegni(registro)
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    conferma_versione(registro, versione.id)
    assert disponibilita_residua(registro, 2026, 1) == Decimal("8000")
    orologio.avanza()
    registra_pagamento_eseguito(registro, corpus_p, "PAG-1", "adattatore-prova", versione.id, VALUTA, [R])
    # R2 non è stato pagato: ripartirà con una nuova versione, che lo conterà di nuovo
    assert disponibilita_residua(registro, 2026, 1) == Decimal("8500")


def test_il_rapporto_fermo_per_capienza_non_lascia_dati_mancanti_nella_versione(registro, corpus_p, orologio):
    assumi_senza_impegni(registro, iban=False)
    assumi_senza_impegni(registro, R2, P2, programma="04.06")
    impegno(registro, "I-1", 1, 2026, disponibilita="1000")
    impegno(registro, "I-2", 2, 2026, disponibilita="100000", piano=PIANO_ENTE)
    impegno(registro, "I-3", 3, 2026, disponibilita="100000", missione="04", programma="06")
    impegno(registro, "I-4", 4, 2026, disponibilita="100000", missione="04", programma="06", piano=PIANO_ENTE)
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    assert [fermo.rapporto for fermo in versione.fermi] == [R]
    assert versione.rapporti == (R2,)
    assert not any(dato.tipo == "iban_beneficiario" for dato in versione.dati_mancanti)
