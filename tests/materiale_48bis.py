"""Materiale dei test del blocco dei pagamenti 48-bis (ADR 0034). Dati esclusivamente fittizi.

Stipendio mensile X, con il corpus di `materiale_proposta`: contributo del lavoratore 8%, ritenuta 20% su
X meno 1000 di franchigia mensile (netto = X - 0,08 X - 0,20 (X - 1000)). Il netto della soglia e' quindi:
  X = 3000: contributo 240,00; ritenuta 400,00; netto 2360,00
  X = 3194,45: contributo 255,56; ritenuta 438,89; netto 2500,00 (esattamente la soglia dei dipendenti)
  X = 3200: contributo 256,00; ritenuta 440,00; netto 2504,00
  X = 4000: contributo 320,00; ritenuta 600,00; netto 3080,00
  X = 6000: contributo 480,00; ritenuta 1000,00; netto 4520,00
  X = 7000: contributo 560,00; ritenuta 1200,00; netto 5240,00
"""

from datetime import date, datetime, UTC
from decimal import Decimal

from paghe import Corpus
from materiale_proposta import CORPUS_PROPOSTA

VERIFICA_48BIS = """
[[soglia_verifica]]
categoria = "lavoro_dipendente"
dal = 2000-01-01
al = 2025-12-31
riferimento = "fittizio:48bis-stipendi-prima-del-2026"

[[soglia_verifica]]
categoria = "lavoro_dipendente"
soglia = "2500"
dal = 2026-01-01
al = 2026-12-31
riferimento = "fittizio:48bis-c1bis"

[[soglia_verifica]]
categoria = "lavoro_dipendente"
soglia = "2500"
dal = 2027-01-01
riferimento = "fittizio:art-144-c2-3"

[[soglia_verifica]]
categoria = "*"
soglia = "5000"
dal = 2008-03-29
riferimento = "fittizio:48bis-c1"

[[somma_sospesa]]
dal = 2026-01-01
giorni_risposta = 5
giorni_sospensione = 60
tetto = "0.5"
fasce = [
    { fino_a = "2500", divisore = "10" },
    { fino_a = "5000", divisore = "7" },
    { divisore = "5" },
]
riferimento = "fittizio:72-ter-e-dm-40-2008"

[[calendario_festivi]]
anno = 2026
feste = ["03-19"]
lunedi_dell_angelo = false
riferimento = "fittizio:festivi-2026"

[[calendario_festivi]]
anno = 2027
feste = []
lunedi_dell_angelo = false
riferimento = "fittizio:festivi-2027"
"""

CORPUS_48BIS = CORPUS_PROPOSTA + VERIFICA_48BIS


def corpus_48bis() -> Corpus:
    return Corpus.da_toml(CORPUS_48BIS)


def istante(mese: int, giorno: int, anno: int = 2026) -> datetime:
    return datetime(anno, mese, giorno, 9, 0, tzinfo=UTC)


def dec(testo: str) -> Decimal:
    return Decimal(testo)


VALUTA = date(2026, 2, 27)
