"""Esito 730-4 minimo e il rimborso che ne nasce (ticket #71, ADR 0023).

L'esito e' un fatto della persona (`Registro.registra_esito_730_4`): provenienza, rimborso e anno dei redditi
dichiarati. Qui si legge il fatto vigente e lo si rende importo del rapporto della persona, con l'anno dei redditi
dichiarati nell'anno d'imposta, che e' quello che la delega F24EP legge (150E, riferimento B). Rate, acconti e debiti
del 730-4 non sono modellati.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .modello import Fatto
from .registro import TIPO_ESITO_730_4, Registro


@dataclass(frozen=True)
class Esito730:
    """L'esito 730-4 vigente di una persona: il fatto, il rimborso e l'anno dei redditi dichiarati."""

    fatto: Fatto
    rimborso: Decimal
    anno_redditi: int


def esito_730_4(registro: Registro, persona: str, giorno: date, noto_al: datetime) -> Esito730 | None:
    """L'ultimo esito 730-4 registrato della persona che copre il giorno; None se non ce n'e'."""
    fatto = registro.vigente_persona(persona, TIPO_ESITO_730_4, giorno, noto_al)
    if fatto is None:
        return None
    dati = json.loads(fatto.valore)
    return Esito730(fatto, Decimal(dati["rimborso"]), dati["anno_redditi"])
