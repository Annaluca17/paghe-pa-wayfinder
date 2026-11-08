"""Conguaglio fiscale al pagamento finale della persona, alla cessazione (ticket #70, ADR 0019). Dati fittizi.

La fine del servizio è la fine del fatto di servizio del corpus (`tipo_impiego`). Un pagamento è finale se, alla sua valuta
prevista, nessun rapporto della persona ha più servizio nell'anno d'imposta. Il conguaglio è della persona.

Numeri sul corpus di materiale_proposta con la franchigia annua a 1200 (ragguagliata al mese 100), aliquota 20%:
  stipendio 1500: ritenuta (1500 - 100) * 0,20 = 280,00; imposta dell'anno (1500 - 1200) * 0,20 = 60,00;
  conguaglio = 60,00 - 280,00 = -220,00.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Mese, calcola
from paghe.proposta import AVVISO_PERSONA_ASSENTE, emetti_versione

from materiale_proposta import CF, IBAN, P, P2, R, R2, paga, corpus_proposta, per_istituto, stipendio


@pytest.fixture
def corpus_c():
    return corpus_proposta(franchigia="1200")


def assumi_fino_al(registro, rapporto, persona, al=None, dal=date(2026, 1, 1)):
    """Un rapporto con il servizio dal `dal` e, se c'è `al`, cessato in quella data."""
    if not registro.fatti_persona_noti(persona, "codice_fiscale", registro.adesso()):
        registro.registra_codice_persona(persona, "codice_fiscale", CF, date(1980, 1, 1))
        registro.registra_iban_persona(persona, IBAN, date(2026, 1, 1))
    registro.collega_rapporto(rapporto, persona, dal)
    registro.registra_codice(rapporto, "tipo_impiego", "1", dal, al)
    registro.registra_programma_rapporto(rapporto, "01.02", dal)


def stipendio_fino_al(registro, corpus, mese, al, importo="1500", rapporto=R):
    """Lo stipendio del mese del rapporto cessato in `al`: il fatto mensile dura fino alla cessazione."""
    registro.registra_fatto(rapporto, "mensile", importo, mese.primo_giorno, al)
    return [riga for riga in calcola(registro, corpus, rapporto, mese) if riga.istituto == "stipendio"]


def test_il_pagamento_dopo_la_cessazione_porta_il_conguaglio_senza_il_fatto_dell_ente(registro, corpus_c, orologio):
    assumi_fino_al(registro, R, P, al=date(2026, 3, 14))
    importi = stipendio_fino_al(registro, corpus_c, Mese(2026, 3), date(2026, 3, 14))
    orologio.vai(3, 20)
    versione = emetti_versione(registro, corpus_c, date(2026, 3, 27), importi)
    righe = per_istituto(versione.righe)
    assert (righe["ritenuta_irpef"].importo.valore, righe["conguaglio_irpef"].importo.valore) == (
        Decimal("280.00"),
        Decimal("-220.00"),
    )
    assert [a.tipo for a in versione.avvisi if a.tipo == "proiezione_conguaglio"] == []
    assert versione.dati_mancanti == ()


def test_chi_ha_ancora_servizio_dopo_il_pagamento_non_ha_il_conguaglio(registro, corpus_c, orologio):
    assumi_fino_al(registro, R, P, al=date(2026, 3, 31))
    importi = stipendio_fino_al(registro, corpus_c, Mese(2026, 3), date(2026, 3, 31))
    orologio.vai(3, 20)
    versione = emetti_versione(registro, corpus_c, date(2026, 3, 27), importi)
    assert "conguaglio_irpef" not in per_istituto(versione.righe)
    assert [a.tipo for a in versione.avvisi if a.tipo == "proiezione_conguaglio"] == ["proiezione_conguaglio"]


def test_il_conguaglio_e_della_persona_se_un_altro_rapporto_ha_ancora_servizio_niente_conguaglio(registro, corpus_c, orologio):
    assumi_fino_al(registro, R, P, al=date(2026, 3, 14))
    assumi_fino_al(registro, "RAPPORTO-2", P)
    importi = stipendio_fino_al(registro, corpus_c, Mese(2026, 3), date(2026, 3, 14))
    orologio.vai(3, 20)
    versione = emetti_versione(registro, corpus_c, date(2026, 3, 27), importi)
    assert "conguaglio_irpef" not in per_istituto(versione.righe)


def test_chiuso_anche_l_altro_rapporto_il_pagamento_di_chi_cessa_per_ultimo_porta_il_conguaglio(registro, corpus_c, orologio):
    assumi_fino_al(registro, R, P, al=date(2026, 3, 14))
    assumi_fino_al(registro, "RAPPORTO-2", P, al=date(2026, 3, 20))
    importi = stipendio_fino_al(registro, corpus_c, Mese(2026, 3), date(2026, 3, 14))
    orologio.vai(3, 20)
    versione = emetti_versione(registro, corpus_c, date(2026, 3, 27), importi)
    assert "conguaglio_irpef" in per_istituto(versione.righe)


def test_un_arretrato_pagato_dopo_la_cessazione_porta_un_conguaglio_per_differenza(registro, corpus_c, orologio):
    """Pagamento finale di marzo: ritenuta 280, conguaglio -220, operato 60 (l'imposta dell'anno su 1500).

    Arretrato di 500 pagato il 10 maggio: ritenuta del mese (500 - 100) * 0,20 = 80,00; imposta dell'anno su 2000
    (2000 - 1200) * 0,20 = 160,00; già operato 280 - 220 + 80 = 140; conguaglio per differenza 20,00.
    """
    assumi_fino_al(registro, R, P, al=date(2026, 3, 14))
    marzo = stipendio_fino_al(registro, corpus_c, Mese(2026, 3), date(2026, 3, 14))
    orologio.vai(3, 20)
    paga(registro, corpus_c, orologio, marzo, date(2026, 3, 27), "pag-marzo")
    arretrato = stipendio_fino_al(registro, corpus_c, Mese(2026, 2), date(2026, 2, 28), "500")
    orologio.vai(5, 5)
    versione = emetti_versione(registro, corpus_c, date(2026, 5, 10), arretrato)
    righe = per_istituto(versione.righe)
    assert (righe["ritenuta_irpef"].importo.valore, righe["conguaglio_irpef"].importo.valore) == (
        Decimal("80.00"),
        Decimal("20.00"),
    )


def test_cessata_a_dicembre_prima_dell_ultimo_pagamento_dell_ente_ha_il_conguaglio_al_pagamento_finale(registro, corpus_c, orologio):
    """Il 18 dicembre è l'ultimo pagamento dell'ente; la persona cessa il 10 e viene pagata il 10: è il suo pagamento
    finale, con il conguaglio -220,00. Un arretrato di 500 pagato il 18 è nello stesso mese: ritenuta del mese
    (2000 - 100) * 0,20 = 380,00 meno 280,00 già operati = 100,00; imposta dell'anno su 2000 = 160,00, operato
    280 - 220 + 100 = 160: conguaglio per differenza 0,00, presente perché il 18 è l'ultimo pagamento dell'ente."""
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    assumi_fino_al(registro, R, P, al=date(2026, 12, 10))
    dicembre = stipendio_fino_al(registro, corpus_c, Mese(2026, 12), date(2026, 12, 10))
    orologio.vai(12, 5)
    finale = paga(registro, corpus_c, orologio, dicembre, date(2026, 12, 10), "pag-dic")
    assert per_istituto(finale.righe)["conguaglio_irpef"].importo.valore == Decimal("-220.00")
    arretrato = stipendio_fino_al(registro, corpus_c, Mese(2026, 11), date(2026, 11, 30), "500")
    orologio.vai(12, 12)
    versione = emetti_versione(registro, corpus_c, date(2026, 12, 18), arretrato)
    righe = per_istituto(versione.righe)
    assert (righe["ritenuta_irpef"].importo.valore, righe["conguaglio_irpef"].importo.valore) == (
        Decimal("100.00"),
        Decimal("0.00"),
    )


def test_la_persona_cessata_con_il_conguaglio_gia_fatto_non_e_assente_dall_ultimo_pagamento(registro, corpus_c, orologio):
    assumi_fino_al(registro, R, P, al=date(2026, 3, 14))
    assumi_fino_al(registro, R2, P2)
    orologio.vai(3, 20)
    paga(registro, corpus_c, orologio, stipendio_fino_al(registro, corpus_c, Mese(2026, 3), date(2026, 3, 14)), date(2026, 3, 27), "pag-p")
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    paga(registro, corpus_c, orologio, stipendio_fino_al(registro, corpus_c, Mese(2026, 1), date(2026, 1, 31), rapporto=R2), date(2026, 3, 28), "pag-p2")
    orologio.vai(12, 10)
    dicembre = stipendio_fino_al(registro, corpus_c, Mese(2026, 12), date(2026, 12, 31), rapporto=R2)
    versione = emetti_versione(registro, corpus_c, date(2026, 12, 18), dicembre)
    assert [a for a in versione.avvisi if a.tipo == AVVISO_PERSONA_ASSENTE] == []
