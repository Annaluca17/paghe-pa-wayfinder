"""Fatti, importi ed esiti, con la loro forma serializzata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from .tempo import Periodo, istante_in_testo


@dataclass(frozen=True)
class Atto:
    """Atto fonte di un fatto. La data serve da sola: decide l'esercizio d'impegno."""

    riferimento: str
    data: date


@dataclass(frozen=True)
class Fatto:
    id: int
    rapporto: str
    tipo: str
    valore: Decimal
    valido_dal: date
    valido_al: date | None
    registrato_il: datetime
    atto: Atto | None = None

    def copre(self, giorno: date) -> bool:
        return self.valido_dal <= giorno and (self.valido_al is None or giorno <= self.valido_al)

    def in_dizionario(self) -> dict:
        return {
            "id": self.id,
            "rapporto": self.rapporto,
            "tipo": self.tipo,
            "valore": str(self.valore),
            "valido_dal": self.valido_dal.isoformat(),
            "valido_al": self.valido_al.isoformat() if self.valido_al else None,
            "registrato_il": istante_in_testo(self.registrato_il),
            "atto": {"riferimento": self.atto.riferimento, "data": self.atto.data.isoformat()} if self.atto else None,
        }

    @classmethod
    def da_dizionario(cls, dati: dict) -> "Fatto":
        atto = dati["atto"]
        return cls(
            id=dati["id"],
            rapporto=dati["rapporto"],
            tipo=dati["tipo"],
            valore=Decimal(dati["valore"]),
            valido_dal=date.fromisoformat(dati["valido_dal"]),
            valido_al=date.fromisoformat(dati["valido_al"]) if dati["valido_al"] else None,
            registrato_il=datetime.fromisoformat(dati["registrato_il"]),
            atto=Atto(atto["riferimento"], date.fromisoformat(atto["data"])) if atto else None,
        )


@dataclass(frozen=True)
class ParametroLetto:
    nome: str
    valore: Decimal
    dal: date
    riferimento: str


@dataclass(frozen=True)
class Quota:
    """Come una base mensile o annuale è stata riportata al periodo. `divisore` None: residuo a mese intero."""

    conteggio: str
    giorni: int
    divisore: Decimal | None
    quota: Decimal
    base: Decimal


@dataclass(frozen=True)
class Derivazione:
    """Da dove viene un importo, fino a norma, parametri e fatti."""

    istituto: str
    maturazione: str
    regola_versione: int
    riferimento: str
    formula: str
    versione_corpus: str
    noto_al: datetime
    parametri: tuple[ParametroLetto, ...]
    fatti: tuple[Fatto, ...]
    importi: tuple["Importo", ...]
    quota: Quota | None = None


@dataclass(frozen=True)
class Importo:
    rapporto: str
    istituto: str
    periodo: Periodo
    valore: Decimal
    derivazione: Derivazione
    esiti_confrontati: tuple[int, ...] = ()

    @property
    def chiave(self) -> tuple[str, str, Periodo]:
        return (self.rapporto, self.istituto, self.periodo)

    def in_dizionario(self) -> dict:
        d = self.derivazione
        return {
            "rapporto": self.rapporto,
            "istituto": self.istituto,
            "periodo": str(self.periodo),
            "valore": str(self.valore),
            "esiti_confrontati": list(self.esiti_confrontati),
            "derivazione": {
                "istituto": d.istituto,
                "maturazione": d.maturazione,
                "quota": (
                    {
                        "conteggio": d.quota.conteggio,
                        "giorni": d.quota.giorni,
                        "divisore": str(d.quota.divisore) if d.quota.divisore is not None else None,
                        "quota": str(d.quota.quota),
                        "base": str(d.quota.base),
                    }
                    if d.quota
                    else None
                ),
                "regola_versione": d.regola_versione,
                "riferimento": d.riferimento,
                "formula": d.formula,
                "versione_corpus": d.versione_corpus,
                "noto_al": istante_in_testo(d.noto_al),
                "parametri": [
                    {"nome": p.nome, "valore": str(p.valore), "dal": p.dal.isoformat(), "riferimento": p.riferimento}
                    for p in d.parametri
                ],
                "fatti": [fatto.in_dizionario() for fatto in d.fatti],
                "importi": [importo.in_dizionario() for importo in d.importi],
            },
        }

    @classmethod
    def da_dizionario(cls, dati: dict) -> "Importo":
        d = dati["derivazione"]
        q = d["quota"]
        return cls(
            rapporto=dati["rapporto"],
            istituto=dati["istituto"],
            periodo=Periodo.da_testo(dati["periodo"]),
            valore=Decimal(dati["valore"]),
            esiti_confrontati=tuple(dati["esiti_confrontati"]),
            derivazione=Derivazione(
                istituto=d["istituto"],
                maturazione=d["maturazione"],
                quota=(
                    Quota(
                        q["conteggio"],
                        q["giorni"],
                        Decimal(q["divisore"]) if q["divisore"] is not None else None,
                        Decimal(q["quota"]),
                        Decimal(q["base"]),
                    )
                    if q
                    else None
                ),
                regola_versione=d["regola_versione"],
                riferimento=d["riferimento"],
                formula=d["formula"],
                versione_corpus=d["versione_corpus"],
                noto_al=datetime.fromisoformat(d["noto_al"]),
                parametri=tuple(
                    ParametroLetto(p["nome"], Decimal(p["valore"]), date.fromisoformat(p["dal"]), p["riferimento"])
                    for p in d["parametri"]
                ),
                fatti=tuple(Fatto.da_dizionario(f) for f in d["fatti"]),
                importi=tuple(cls.da_dizionario(i) for i in d["importi"]),
            ),
        )


class TipoEsito(StrEnum):
    PAGATO = "pagato"
    DICHIARATO = "dichiarato"
    VERSATO = "versato"


@dataclass(frozen=True)
class Esito:
    """Istantanea immutabile: non dipende più da regole e fatti successivi."""

    id: int
    tipo: TipoEsito
    data: date
    registrato_il: datetime
    righe: tuple[Importo, ...]

    @property
    def versioni_corpus(self) -> frozenset[str]:
        return frozenset(riga.derivazione.versione_corpus for riga in self.righe)

    @property
    def versioni_regole(self) -> dict[str, int]:
        return {riga.istituto: riga.derivazione.regola_versione for riga in self.righe}

    @property
    def noti_al(self) -> frozenset[datetime]:
        """Tempo di registrazione dei fatti letti per ciascuna riga."""
        return frozenset(riga.derivazione.noto_al for riga in self.righe)
