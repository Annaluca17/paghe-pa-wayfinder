"""Addizionali regionale e comunale all'IRPEF: saldo, rate e acconto comunale (ticket #85, ADR 0029).

Si calcolano sull'imponibile fiscale dell'anno della persona, lo stesso del conguaglio (ADR 0019), con le aliquote
datate del corpus per il comune e la regione del domicilio fiscale al 1° gennaio. Questo modulo legge e non scrive:
gli importi che produce sono dei pagamenti, e il residuo da trattenere si ricalcola dagli esiti pagati.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime

from .modello import Fatto
from .registro import TIPO_DOMICILIO_FISCALE, Registro


@dataclass(frozen=True)
class Domicilio:
    """Il domicilio fiscale vigente di una persona: il fatto, il codice catastale del comune e il codice della regione."""

    fatto: Fatto
    comune: str
    regione: str


def domicilio_fiscale(registro: Registro, persona: str, giorno: date, noto_al: datetime) -> Domicilio | None:
    """Il domicilio fiscale della persona al `giorno`; None se manca."""
    fatto = registro.vigente_persona(persona, TIPO_DOMICILIO_FISCALE, giorno, noto_al)
    if fatto is None:
        return None
    dati = json.loads(fatto.valore)
    return Domicilio(fatto, dati["comune"], dati["regione"])
