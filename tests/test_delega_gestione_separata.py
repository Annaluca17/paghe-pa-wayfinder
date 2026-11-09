"""Causale F24EP della gestione separata per posizione previdenziale (ticket #104). Dati fittizi.

CXX per `gestione_separata` e per l'onere dell'art. 86; C10 per `pensionato` e `altra_cassa`. Riferimento A: mese e
anno di PAGAMENTO (`MMAAAA`), non quelli di competenza; riferimento B: nessuno.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Periodo
from paghe.delega import costruisci_delega

from materiale_delega import R, R2, _codice, _istituto_a_mano, dati_ente, paga_a_mano, riga_a_mano, toml_delega

NOV = __import__("paghe").Mese(2026, 11)
VALUTA = date(2026, 11, 27)  # pagamento di novembre, compenso di competenza ottobre
OTTOBRE = Periodo(date(2026, 10, 1), date(2026, 10, 31))
D = Decimal

SISTEMA_CAUSALE = "f24ep.causale_gestione_separata"


def _per_posizione(posizione, codice):
    return f'''
[[mappatura_fatto]]
sistema = "{SISTEMA_CAUSALE}"
elemento = "causale"
fatto = "posizione_previdenziale"
valore = "{posizione}"
codice = "{codice}"
dal = 2020-01-01
riferimento = "fittizio:causale-gs-{posizione.replace("_", "-")}"
'''


EXTRA = (
    _codice("C10", "Q", "provincia", "facoltativo", "mese_anno_pagamento", "nessuno", "debito")
    + _codice("CXX", "Q", "provincia", "facoltativo", "mese_anno_pagamento", "nessuno", "debito")
    + _istituto_a_mano("gs_lavoratore", "trattenuta_terzi", "meno", "terzo", "f24ep", None)
    + _istituto_a_mano("gs_ente", "trattenuta_terzi", "meno", "terzo", "f24ep", None)
    + _istituto_a_mano("onere_art86", "trattenuta_terzi", "meno", "terzo", "f24ep", "CXX")
    + _per_posizione("gestione_separata", "CXX")
    + _per_posizione("pensionato", "C10")
    + _per_posizione("altra_cassa", "C10")
)


@pytest.fixture
def corpus():
    return Corpus.da_toml(toml_delega() + EXTRA)


@pytest.fixture
def ente(registro):
    dati_ente(registro)
    registro.registra_data_versamento(NOV, date(2026, 12, 16))


def posizione(registro, rapporto, valore):
    registro.registra_codice(rapporto, "posizione_previdenziale", valore, date(2026, 1, 1))


def delega_gs(registro, corpus, orologio, voci):
    """`voci`: [(istituto, rapporto, importo)], competenza ottobre, pagate il 27 novembre."""
    righe = [riga_a_mano(corpus, VALUTA, i, v, rapporto=r, periodo=OTTOBRE) for i, r, v in voci]
    paga_a_mano(registro, corpus, orologio, VALUTA, righe)
    return costruisci_delega(registro, corpus, NOV)


@pytest.mark.parametrize(
    "pos, causale", [("gestione_separata", "CXX"), ("pensionato", "C10"), ("altra_cassa", "C10")]
)
def test_la_causale_dipende_dalla_posizione_del_rapporto(registro, corpus, orologio, ente, pos, causale):
    posizione(registro, R, pos)
    d = delega_gs(registro, corpus, orologio, [("gs_lavoratore", R, "100.00"), ("gs_ente", R, "200.00")])
    (riga,) = d.righe
    assert (riga.sezione, riga.tributo, riga.rif_b) == ("Q", causale, "")
    assert riga.debito == D("300.00")
    assert d.fermi == () and d.dati_mancanti == ()


def test_l_onere_dell_art_86_va_su_cxx(registro, corpus, orologio, ente):
    d = delega_gs(registro, corpus, orologio, [("onere_art86", R, "528.51")])
    (riga,) = d.righe
    assert (riga.tributo, riga.debito) == ("CXX", D("528.51"))


def test_il_riferimento_a_e_mese_e_anno_di_pagamento_non_di_competenza(registro, corpus, orologio, ente):
    posizione(registro, R, "gestione_separata")
    d = delega_gs(registro, corpus, orologio, [("gs_lavoratore", R, "100.00")])  # competenza ottobre, pagato a novembre
    (riga,) = d.righe
    assert riga.rif_a == "112026"


def test_posizioni_diverse_danno_righe_diverse(registro, corpus, orologio, ente):
    posizione(registro, R, "gestione_separata")
    posizione(registro, R2, "pensionato")
    d = delega_gs(registro, corpus, orologio, [("gs_lavoratore", R, "100.00"), ("gs_lavoratore", R2, "50.00")])
    assert sorted((r.tributo, r.debito) for r in d.righe) == [("C10", D("50.00")), ("CXX", D("100.00"))]


def test_senza_posizione_la_delega_si_ferma_e_nomina_il_rapporto(registro, corpus, orologio, ente):
    d = delega_gs(registro, corpus, orologio, [("gs_lavoratore", R, "100.00")])
    assert d.righe == ()
    (mancante,) = d.dati_mancanti
    assert (mancante.tipo, mancante.soggetto) == ("posizione_previdenziale", R)
    assert R in mancante.motivo
    assert not d.pronta


def test_una_posizione_senza_causale_nel_corpus_ferma_l_invio_e_nomina_il_rapporto(registro, corpus, orologio, ente):
    posizione(registro, R, "inventata")
    d = delega_gs(registro, corpus, orologio, [("gs_ente", R, "100.00")])
    (fermo,) = d.fermi
    assert fermo.caso == "causale_non_mappata" and R in fermo.motivo and "inventata" in fermo.motivo
    assert d.righe == ()


def test_la_causale_segue_la_posizione_della_competenza_non_quella_del_pagamento(registro, corpus, orologio, ente):
    # Caso limite: il collaboratore va in pensione dal 1° novembre; il compenso di ottobre pagato a novembre resta CXX.
    posizione(registro, R, "gestione_separata")
    registro.registra_codice(R, "posizione_previdenziale", "pensionato", date(2026, 11, 1))
    d = delega_gs(registro, corpus, orologio, [("gs_lavoratore", R, "100.00")])
    (riga,) = d.righe
    assert (riga.tributo, riga.rif_a) == ("CXX", "112026")
