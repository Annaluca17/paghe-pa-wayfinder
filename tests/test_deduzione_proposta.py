"""La proposta calcola i contributi del lavoratore prima della ritenuta e la ritenuta li deduce (ticket #70).

Sul corpus di materiale_proposta: stipendio 1500, contributo del lavoratore 8% = 120,00, franchigia ragguagliata 1000.
Con la dichiarazione di deduzione: ritenuta = (1500 - 120 - 1000) * 0,20 = 76,00; netto = 1500 - 120 - 76 = 1304,00.
Senza: ritenuta 100,00, netto 1280,00.
"""

from datetime import date
from decimal import Decimal

from paghe import Corpus, Mese
from paghe.proposta import emetti_versione

from materiale_proposta import CORPUS_PROPOSTA, R, assumi, stipendio

DEDUZIONE = """
[[deduzione_fiscale]]
istituto = "contributo_lavoratore"
dal = 2020-01-01
riferimento = "fittizio:deduzione-contributo-lavoratore"
"""


def _versione(registro, corpus, orologio):
    assumi(registro)
    orologio.vai(6, 20)
    return emetti_versione(registro, corpus, date(2026, 6, 27), stipendio(registro, corpus, Mese(2026, 6)))


def _valore(versione, istituto):
    return next(riga.importo.valore for riga in versione.righe if riga.istituto == istituto)


def test_senza_dichiarazione_la_proposta_resta_com_e(registro, orologio):
    versione = _versione(registro, Corpus.da_toml(CORPUS_PROPOSTA), orologio)
    assert (_valore(versione, "ritenuta_irpef"), versione.netti[0].netto) == (Decimal("100.00"), Decimal("1280.00"))


def test_la_ritenuta_della_proposta_deduce_i_contributi_del_lavoratore_del_pagamento(registro, orologio):
    versione = _versione(registro, Corpus.da_toml(CORPUS_PROPOSTA + DEDUZIONE), orologio)
    assert _valore(versione, "contributo_lavoratore") == Decimal("120.00")
    assert (_valore(versione, "ritenuta_irpef"), versione.netti[0].netto) == (Decimal("76.00"), Decimal("1304.00"))


def test_un_secondo_pagamento_del_mese_deduce_i_contributi_anche_del_primo(registro, orologio):
    """Il secondo pagamento paga 500 di arretrato di maggio, contributo 40: imponibile del mese 2000 - 160 = 1840,
    ritenuta del mese (1840 - 1000) * 0,20 = 168,00, già operati 76,00, quindi 92,00."""
    from materiale_proposta import paga

    corpus = Corpus.da_toml(CORPUS_PROPOSTA + DEDUZIONE)
    assumi(registro)
    paga(registro, corpus, orologio, stipendio(registro, corpus, Mese(2026, 6)), date(2026, 6, 20), "pag-1")
    versione = emetti_versione(registro, corpus, date(2026, 6, 27), stipendio(registro, corpus, Mese(2026, 5), "500"))
    assert _valore(versione, "contributo_lavoratore") == Decimal("40.00")
    assert _valore(versione, "ritenuta_irpef") == Decimal("92.00")
