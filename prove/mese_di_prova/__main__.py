"""`python -m prove.mese_di_prova`: fa girare il mese di prova e scrive il resoconto. Tutti i dati sono fittizi."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .percorso import esegui
from .resoconto import scrivi

CARTELLA = Path(__file__).resolve().parent
USCITA = CARTELLA / "uscita"
ATTESO = CARTELLA / "resoconto-atteso.md"


def main(argomenti: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Un mese intero di un ente fittizio, dai fatti ai file.")
    parser.add_argument("--uscita", type=Path, default=USCITA, help="cartella dei file prodotti (ignorata da Git)")
    parser.add_argument("--aggiorna-atteso", action="store_true", help=f"riscrive {ATTESO.name}, il resoconto fissato dal test")
    parser.add_argument("--denuncia-di-dicembre", action="store_true", help="esegue anche la denuncia e la ListaPosPA di dicembre (lento)")
    dati = parser.parse_args(argomenti)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    testo = scrivi(esegui(dati.uscita, denuncia_di_dicembre=dati.denuncia_di_dicembre))
    dati.uscita.mkdir(parents=True, exist_ok=True)
    (dati.uscita / "resoconto.md").write_text(testo, encoding="utf-8", newline="\n")
    if dati.aggiorna_atteso:
        ATTESO.write_text(testo, encoding="utf-8", newline="\n")
    print(testo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
