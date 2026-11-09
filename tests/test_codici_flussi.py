"""Codici dei flussi (ticket #105): riferimenti CNEL del corpus e contratto RALN nei flussi generati.

Seam sotto prova: il corpus FL-CPDEL letto come dato, e i flussi `lista_pos_pa` / `in_xml` / `denuncia_individuale`.
Persone, enti e codici fiscali di fantasia.
"""

import tomllib
from datetime import date

import pytest

from paghe import Mese, denuncia_individuale, lista_pos_pa
from paghe.uniemens import in_xml
from test_denuncia_individuale import MARZO, corpus, in_servizio_con, stipendi, paga  # noqa: F401
from test_lista_pos_pa import CORPUS, ENTE, MITTENTE, R, assumi, reale  # noqa: F401

NOVEMBRE = Mese(2026, 11)

# Area dirigenziale (dirigenti e segretari): codice CNEL S125; il comparto, S105 (file CNEL ccnl-settore-pubblico.xlsx).
FERMI_AREA = {
    "retribuzione_risultato", "interim", "fascia_segretario", "convenzione_segreteria", "scavalco", "galleggiamento",
    "posizione_annua_segretario", "posizione_annua_dirigente",
}
PARAMETRI_AREA = {
    "tabellare_annuo_dirigenti", "tabellare_annuo_segretario_a", "tabellare_annuo_segretario_b", "tabellare_annuo_segretario_c",
}
ISTITUTI_AREA = {
    "tabellare_dirigenti", "posizione_dirigenti", "tabellare_segretario_a", "tabellare_segretario_b",
    "tabellare_segretario_c", "posizione_segretario",
}


def _riferimenti_del_corpus():
    """(area?, riferimento) di ogni fermo, vigenza di parametro e regola del corpus."""
    dati = tomllib.loads(CORPUS.read_text(encoding="utf-8"))
    voci = [(f["fatto"] in FERMI_AREA, f["riferimento"]) for f in dati.get("fermo", []) if "riferimento" in f]
    for p in dati.get("parametro", []):
        voci += [(p["nome"] in PARAMETRI_AREA, v["riferimento"]) for v in p["vigenza"]]
    voci += [(r["istituto"] in ISTITUTI_AREA, r["riferimento"]) for r in dati.get("regola", [])]
    return voci


def test_i_riferimenti_dell_area_dirigenziale_sono_s125_e_non_s105():
    area = [rif for e_area, rif in _riferimenti_del_corpus() if e_area]
    assert len(area) >= 19
    assert all("ccnl:S125:" in rif and "ccnl:S105:" not in rif for rif in area)


def test_i_riferimenti_del_comparto_restano_s105_e_non_citano_s125():
    comparto = [rif for e_area, rif in _riferimenti_del_corpus() if not e_area]
    assert comparto
    assert all("ccnl:S125:" not in rif for rif in comparto)


def test_la_lista_pos_pa_scrive_il_contratto_raln_dal_fatto_del_rapporto(registro, reale, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, reale, NOVEMBRE), date(2026, 11, 27))
    xml = in_xml([lista_pos_pa(registro, reale, R, NOVEMBRE)], ENTE, MITTENTE, mese=NOVEMBRE, bozza=True)
    assert "<Contratto>RALN</Contratto>" in xml
    assert "S105" not in xml and "S125" not in xml


def test_la_denuncia_individuale_non_porta_i_codici_cnel_del_corpus(registro, orologio, corpus):
    in_servizio_con(registro, "17")
    paga(registro, orologio, stipendi(registro, corpus, MARZO), date(2026, 3, 27))
    testo = repr(denuncia_individuale(registro, corpus, R, MARZO))
    assert "S105" not in testo and "S125" not in testo
