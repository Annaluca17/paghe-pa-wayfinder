"""Materiale comune ai test degli impegni, dell'abbinamento e delle proposte di impegno. Dati esclusivamente fittizi."""

from datetime import date
from decimal import Decimal

from paghe.impegni import registra_impegno

PIANO = "U.1.01.01.01.002"  # voci stipendiali: classificazione dello stipendio nel corpus di prova
PIANO_ENTE = "U.1.01.02.01.001"  # contributi a carico ente: classificazione del contributo_ente


def impegno(registro, chiave="IMP-1", numero=1, esercizio=2026, disponibilita="10000", data=date(2026, 1, 1), atto=None,
            piano=PIANO, missione="01", programma="02"):
    return registra_impegno(
        registro, chiave, "adattatore-prova", numero, esercizio, piano, missione, programma, disponibilita, data, atto
    )


def impegni_capienti(registro, esercizio=2026, numero=1, disponibilita="100000", data=date(2026, 1, 1)):
    """Gli impegni automatici dei due istituti di spesa del corpus di prova, a 01.02, con molta disponibilità."""
    impegno(registro, f"IMP-{esercizio}-{numero}-S", numero, esercizio, disponibilita, data, piano=PIANO)
    impegno(registro, f"IMP-{esercizio}-{numero}-E", numero + 1000, esercizio, disponibilita, data, piano=PIANO_ENTE)
