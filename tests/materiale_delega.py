"""Materiale comune ai test della delega F24EP (ticket #54). Dati e riferimenti esclusivamente fittizi.

I codici tributo e le causali degli esempi sono quelli confermati dalla ricerca (`docs/research/versamenti-f24ep.md`):
100E, 104E (ritenute), P201 (CPDEL), 150E, 170E, 175E (crediti), 384E, 380E (con codice catastale o regione).
"""

from datetime import date

from paghe import Corpus

# Festivi del calendario di prova: i fissi e il lunedì di Pasqua (5 aprile 2026, 28 marzo 2027, 16 aprile 2028).
FESTIVI_FISSI = ("01-01", "01-06", "04-25", "05-01", "06-02", "08-15", "11-01", "12-08", "12-25", "12-26")
PASQUETTA = {2026: "2026-04-06", 2027: "2027-03-29", 2028: "2028-04-17"}


def _calendario(anno: int, extra: tuple[str, ...] = ()) -> str:
    giorni = [f"{anno}-{fisso}" for fisso in FESTIVI_FISSI] + [PASQUETTA[anno], *[e for e in extra if e.startswith(str(anno))]]
    return f'''
[[calendario_festivi]]
anno = {anno}
giorni = [{", ".join(sorted(giorni))}]
riferimento = "fittizio:festivi-{anno}"
'''


SCADENZE = '''
[[scadenza_f24ep]]
dal = 2020-01-01
al = 2026-12-31
giorno = 16
riferimento = "fittizio:scadenza-2026"
[scadenza_f24ep.proroga]
mese = 8
dal_giorno = 1
al_giorno = 20
fonte = "prassi"
riferimento = "fittizio:proroga-2026"

[[scadenza_f24ep]]
dal = 2027-01-01
giorno = 16
riferimento = "fittizio:scadenza-2027"
[scadenza_f24ep.proroga]
mese = 8
dal_giorno = 1
al_giorno = 20
fonte = "prassi"
riferimento = "fittizio:proroga-2027"
'''


def toml_scadenza(extra_festivi: tuple[str, ...] = ()) -> str:
    return SCADENZE + "".join(_calendario(anno, extra_festivi) for anno in (2026, 2027, 2028))


def corpus_scadenza(extra_festivi: tuple[str, ...] = ()) -> Corpus:
    return Corpus.da_toml(toml_scadenza(extra_festivi))
