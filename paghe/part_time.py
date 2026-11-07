"""Programmazione del part-time (ADR 0026): per ogni giorno, se è lavorativo e con quante ore.

È un input da atto del rapporto. Nel registro è un fatto per giorno, valido solo in quel giorno, con le ore
(zero per un giorno non lavorativo): il registro già sa sostituire un giorno con un fatto successivo, tenere
l'atto di ciascuno e rispondere «com'era noto al» un istante. Un periodo di qualunque durata (mese, trimestre,
anno) è un insieme di giorni; i giorni non registrati non sono coperti. La programmazione non è il lavorato.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Mapping

from .errori import ErroreRegistro
from .modello import Atto
from .registro import Registro
from .tempo import Mese, Periodo, in_utc

TIPO_PROGRAMMAZIONE = "programmazione_part_time"
ORE_MASSIME_AL_GIORNO = Decimal(24)


@dataclass(frozen=True)
class Programmazione:
    """Le ore programmate nei giorni coperti del mese."""

    mese: Mese
    ore: Mapping[date, Decimal]

    @property
    def mancanti(self) -> tuple[Periodo, ...]:
        """Periodi di giorni del mese senza programmazione."""
        periodi: list[Periodo] = []
        inizio = None
        precedente = None
        for giorno in self.mese.giorni():
            if giorno in self.ore:
                if inizio is not None:
                    periodi.append(Periodo(inizio, precedente))
                    inizio = None
            elif inizio is None:
                inizio = giorno
            precedente = giorno
        if inizio is not None:
            periodi.append(Periodo(inizio, precedente))
        return tuple(periodi)

    @property
    def completa(self) -> bool:
        return not self.mancanti

    @property
    def giorni_lavorativi(self) -> int:
        return sum(1 for ore in self.ore.values() if ore > 0)

    @property
    def ore_totali(self) -> Decimal:
        return sum(self.ore.values(), Decimal(0))


def registra_programmazione(
    registro: Registro, rapporto: str, ore_per_giorno: Mapping[date, Decimal | int | str], atto: Atto | None
) -> None:
    """Registra le ore di ciascun giorno; un giorno già programmato è sostituito, non modificato."""
    if atto is None:
        raise ErroreRegistro("La programmazione del part-time è un input da atto: serve l'atto")
    valori = {giorno: Decimal(str(ore)) for giorno, ore in ore_per_giorno.items()}
    for giorno, ore in valori.items():
        if not 0 <= ore <= ORE_MASSIME_AL_GIORNO:
            raise ErroreRegistro(f"Le ore del {giorno} stanno fra 0 e {ORE_MASSIME_AL_GIORNO}: {ore}")
    for giorno in sorted(valori):
        registro.registra_fatto(rapporto, TIPO_PROGRAMMAZIONE, valori[giorno], giorno, giorno, atto)


def programmazione_del_mese(
    registro: Registro, rapporto: str, mese: Mese, noto_al: datetime | None = None
) -> Programmazione:
    """Programmazione nota al `noto_al` per i giorni del mese."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    vigenti = registro.vigenti_per_giorno(rapporto, TIPO_PROGRAMMAZIONE, mese, istante)
    ore = {giorno: fatto.valore for giorno, fatto in zip(mese.giorni(), vigenti) if fatto is not None}
    return Programmazione(mese, ore)
