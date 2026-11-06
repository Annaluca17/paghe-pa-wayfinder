"""Dimostrazione: `python -m paghe`. Tutti i dati, le norme e i valori sono fittizi."""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime

from . import Atto, Corpus, Mese, Registro, TipoEsito, calcola, differenze, emetti_esito, spiega

CORPUS = """
[[parametro]]
nome = "aliquota_prova"
[[parametro.vigenza]]
dal = 2026-01-01
valore = "{aliquota}"
riferimento = "fittizio:fonte-prova"

[[parametro]]
nome = "divisore_giornaliero"
[[parametro.vigenza]]
dal = 2026-01-01
valore = "26"
riferimento = "fittizio:fonte-divisore"

[[regola]]
istituto = "compenso_prova"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:contratto-prova-art-1"
formula = "fatto.compenso_mensile"
maturazione = "giorni"
applica_se = "compenso_mensile"
conteggio = "lun_sab"
divisore = "divisore_giornaliero"
decimali = 2

[[regola]]
istituto = "ritenuta_prova"
versione = {versione_ritenuta}
dal = 2026-01-01
riferimento = "fittizio:contratto-prova-art-2"
formula = "arrotonda(importo.compenso_prova * parametro.aliquota_prova, 2)"
maturazione = "periodo"
"""


def corpus(aliquota: str = "0.10", versione_ritenuta: int = 1) -> Corpus:
    return Corpus.da_toml(CORPUS.format(aliquota=aliquota, versione_ritenuta=versione_ritenuta))


def _elenca(importi) -> None:
    for importo in importi:
        print(f"  {importo.istituto}: {importo.valore}")


def _elenca_differenze(voci) -> None:
    if not voci:
        print("  nessuna differenza")
    for voce in voci:
        print(f"  {voce.istituto}: dovuto {voce.dovuto} - esitato {voce.gia_esitato} = {voce.valore}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    orologio = {"ora": datetime(2026, 1, 10, 9, 0, tzinfo=UTC)}

    def imposta(mese: int, giorno: int) -> datetime:
        orologio["ora"] = datetime(2026, mese, giorno, 9, 0, tzinfo=UTC)
        return orologio["ora"]

    registro = Registro(orologio=lambda: orologio["ora"])
    regole = corpus()
    rapporto = "RAPPORTO-PROVA-1"
    febbraio = Mese(2026, 2)

    print("DATI FITTIZI: nessun valore di questa dimostrazione è una norma reale.\n")
    print(f"Corpus {regole.versione}")

    print("\n1. Il 10/01 si registra il compenso; il 27/02 si paga febbraio.")
    registro.registra_fatto(rapporto, "compenso_mensile", "1000.00", date(2026, 1, 1))
    pagamento = imposta(2, 27)
    importi_pagati = calcola(registro, regole, rapporto, febbraio)
    _elenca(importi_pagati)
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), importi_pagati)
    print(f"  esito #{esito.id} registrato")

    print("\n2. Il 15/03 arriva un atto con effetto dal 01/02: il compenso sale a 1100.")
    imposta(3, 15)
    registro.registra_fatto(
        rapporto,
        "compenso_mensile",
        "1100.00",
        date(2026, 2, 1),
        atto=Atto("fittizio:determina-prova-1", date(2026, 3, 10)),
    )

    print("\n3. Febbraio com'è dovuto oggi:")
    _elenca(calcola(registro, regole, rapporto, febbraio))
    print("   Febbraio come risultava al pagamento:")
    _elenca(calcola(registro, regole, rapporto, febbraio, noto_al=pagamento))

    print("\n4. Differenze rispetto al pagato:")
    arretrati = differenze(registro, regole, rapporto, febbraio, TipoEsito.PAGATO)
    _elenca_differenze(arretrati)
    imposta(3, 27)
    emetti_esito(registro, TipoEsito.PAGATO, date(2026, 3, 27), [voce.importo() for voce in arretrati])
    print("   Dopo il pagamento dell'arretrato:")
    _elenca_differenze(differenze(registro, regole, rapporto, febbraio, TipoEsito.PAGATO))

    print("\n5. Si corregge l'aliquota nel corpus: l'esito resta fermo, emerge la differenza.")
    corretto = corpus(aliquota="0.12", versione_ritenuta=2)
    print(f"   Corpus {corretto.versione}")
    _elenca_differenze(differenze(registro, corretto, rapporto, febbraio, TipoEsito.PAGATO))
    print(f"   L'esito #{esito.id} conserva il corpus {sorted(registro.esito(esito.id).versioni_corpus)[0]}")

    print("\n6. Da dove viene la ritenuta di febbraio:")
    ritenuta = next(i for i in calcola(registro, regole, rapporto, febbraio) if i.istituto == "ritenuta_prova")
    print(spiega(ritenuta))

    print("\n7. Un secondo rapporto inizia il 24/08 a 1000: agosto vale 7 giorni su 26, settembre intero.")
    secondo = "RAPPORTO-PROVA-2"
    registro.registra_fatto(secondo, "compenso_mensile", "1000.00", date(2026, 8, 24))
    _elenca(calcola(registro, regole, secondo, Mese(2026, 8)))
    _elenca(calcola(registro, regole, secondo, Mese(2026, 9)))
    registro.chiudi()


if __name__ == "__main__":
    main()
