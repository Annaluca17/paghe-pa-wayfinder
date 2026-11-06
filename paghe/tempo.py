"""Periodo di competenza e istanti di registrazione."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta


@dataclass(frozen=True, order=True)
class Mese:
    """Periodo di competenza mensile."""

    anno: int
    mese: int

    def __post_init__(self) -> None:
        if not 1 <= self.mese <= 12:
            raise ValueError(f"Mese non valido: {self.mese}")

    @classmethod
    def da_testo(cls, testo: str) -> "Mese":
        anno, mese = testo.split("-")
        return cls(int(anno), int(mese))

    @property
    def primo_giorno(self) -> date:
        return date(self.anno, self.mese, 1)

    @property
    def ultimo_giorno(self) -> date:
        return date(self.anno, self.mese, calendar.monthrange(self.anno, self.mese)[1])

    def giorni(self) -> list[date]:
        numero = (self.ultimo_giorno - self.primo_giorno).days + 1
        return [self.primo_giorno + timedelta(days=i) for i in range(numero)]

    @property
    def periodo(self) -> "Periodo":
        return Periodo(self.primo_giorno, self.ultimo_giorno)

    def __str__(self) -> str:
        return f"{self.anno:04d}-{self.mese:02d}"


@dataclass(frozen=True, order=True)
class Periodo:
    """Intervallo di giorni, estremi compresi."""

    dal: date
    al: date

    def __post_init__(self) -> None:
        if self.al < self.dal:
            raise ValueError(f"Periodo invertito: {self.dal} - {self.al}")

    @classmethod
    def da_testo(cls, testo: str) -> "Periodo":
        dal, al = testo.split("/")
        return cls(date.fromisoformat(dal), date.fromisoformat(al))

    @property
    def primo_giorno(self) -> date:
        return self.dal

    @property
    def ultimo_giorno(self) -> date:
        return self.al

    def giorni(self) -> list[date]:
        return [self.dal + timedelta(days=i) for i in range(self.giorni_calendario)]

    @property
    def giorni_calendario(self) -> int:
        return (self.al - self.dal).days + 1

    @property
    def giorni_lun_sab(self) -> int:
        return sum(1 for giorno in self.giorni() if giorno.weekday() != 6)

    def contiene(self, altro: "Periodo") -> bool:
        return self.dal <= altro.dal and altro.al <= self.al

    def __str__(self) -> str:
        return f"{self.dal.isoformat()}/{self.al.isoformat()}"


def in_utc(istante: datetime) -> datetime:
    """Normalizza un istante; un istante senza fuso è ambiguo e viene rifiutato."""
    if istante.tzinfo is None or istante.utcoffset() is None:
        raise ValueError("L'istante deve indicare il fuso orario")
    return istante.astimezone(UTC)


def istante_in_testo(istante: datetime) -> str:
    """Formato a larghezza fissa: l'ordine del testo coincide con l'ordine temporale."""
    return in_utc(istante).isoformat(timespec="microseconds")
