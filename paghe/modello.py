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
    valore: Decimal | str
    valido_dal: date
    valido_al: date | None
    registrato_il: datetime
    atto: Atto | None = None
    categoriale: bool = False
    # `rapporto` o `persona`: il campo `rapporto` porta l'identificativo del soggetto (ADR 0012).
    soggetto: str = "rapporto"

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
            "categoriale": self.categoriale,
            "soggetto": self.soggetto,
        }

    @classmethod
    def da_dizionario(cls, dati: dict) -> "Fatto":
        atto = dati["atto"]
        categoriale = dati.get("categoriale", False)
        return cls(
            id=dati["id"],
            rapporto=dati["rapporto"],
            tipo=dati["tipo"],
            valore=dati["valore"] if categoriale else Decimal(dati["valore"]),
            valido_dal=date.fromisoformat(dati["valido_dal"]),
            valido_al=date.fromisoformat(dati["valido_al"]) if dati["valido_al"] else None,
            registrato_il=datetime.fromisoformat(dati["registrato_il"]),
            atto=Atto(atto["riferimento"], date.fromisoformat(atto["data"])) if atto else None,
            categoriale=categoriale,
            soggetto=dati.get("soggetto", "rapporto"),
        )


@dataclass(frozen=True)
class ParametroLetto:
    nome: str
    valore: Decimal
    dal: date
    riferimento: str


@dataclass(frozen=True)
class ConcorsoLetto:
    """Dichiarazione applicata a un importo pagato: a quale base concorre e in che misura."""

    istituto: str
    base: str
    misura: str
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


# Fatti del part-time (ADR 0026): la percentuale è numerica, il tipo un codice.
FATTO_PART_TIME = "part_time"
FATTO_TIPO_PART_TIME = "tipo_part_time"


@dataclass(frozen=True)
class RiduzionePartTime:
    """Il part-time applicato a un importo: percentuale, importo pieno prima della riduzione e trattamento dichiarato."""

    percentuale: Decimal
    importo_pieno: Decimal
    trattamento: str


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
    concorsi: tuple[ConcorsoLetto, ...] = ()
    part_time: RiduzionePartTime | None = None


# Importi calcolati sul pagato, non sulla competenza: ritenuta e conguaglio fiscale (ADR 0019).
MATURAZIONI_FISCALI = frozenset({"ritenuta", "conguaglio"})


@dataclass(frozen=True)
class Importo:
    rapporto: str
    istituto: str
    periodo: Periodo
    valore: Decimal
    derivazione: Derivazione
    esiti_confrontati: tuple[int, ...] = ()
    data_pagamento: date | None = None
    # Attribuzione fiscale, congelata nell'esito pagato (ADR 0015, 0019).
    anno_imposta: int | None = None
    categoria_reddito: str | None = None

    @property
    def chiave(self) -> tuple[str, str, Periodo]:
        return (self.rapporto, self.istituto, self.periodo)

    def in_dizionario(self) -> dict:
        d = self.derivazione
        fiscale = {}
        if self.anno_imposta is not None:
            fiscale["anno_imposta"] = self.anno_imposta
        if self.categoria_reddito is not None:
            fiscale["categoria_reddito"] = self.categoria_reddito
        return {
            **fiscale,
            "rapporto": self.rapporto,
            "istituto": self.istituto,
            "periodo": str(self.periodo),
            "valore": str(self.valore),
            "esiti_confrontati": list(self.esiti_confrontati),
            "data_pagamento": self.data_pagamento.isoformat() if self.data_pagamento else None,
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
                "concorsi": [
                    {"istituto": c.istituto, "base": c.base, "misura": c.misura, "dal": c.dal.isoformat(), "riferimento": c.riferimento}
                    for c in d.concorsi
                ],
                **(
                    {
                        "part_time": {
                            "percentuale": str(d.part_time.percentuale),
                            "importo_pieno": str(d.part_time.importo_pieno),
                            "trattamento": d.part_time.trattamento,
                        }
                    }
                    if d.part_time
                    else {}
                ),
            },
        }

    @classmethod
    def da_dizionario(cls, dati: dict) -> "Importo":
        d = dati["derivazione"]
        q = d["quota"]
        pagato = dati.get("data_pagamento")
        return cls(
            rapporto=dati["rapporto"],
            istituto=dati["istituto"],
            periodo=Periodo.da_testo(dati["periodo"]),
            valore=Decimal(dati["valore"]),
            esiti_confrontati=tuple(dati["esiti_confrontati"]),
            data_pagamento=date.fromisoformat(pagato) if pagato else None,
            anno_imposta=dati.get("anno_imposta"),
            categoria_reddito=dati.get("categoria_reddito"),
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
                concorsi=tuple(
                    ConcorsoLetto(c["istituto"], c["base"], c["misura"], date.fromisoformat(c["dal"]), c["riferimento"])
                    for c in d.get("concorsi", ())
                ),
                part_time=(
                    RiduzionePartTime(
                        Decimal(d["part_time"]["percentuale"]),
                        Decimal(d["part_time"]["importo_pieno"]),
                        d["part_time"]["trattamento"],
                    )
                    if d.get("part_time")
                    else None
                ),
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


@dataclass(frozen=True)
class Evento:
    """Evento di ritorno registrato (ADR 0025): identificativo stabile, contenuto e adattatore che l'ha portato.

    `versione_id` è la versione di proposta a cui si riferisce; `esito_id` l'esito che ne è nato o a cui si riferisce.
    """

    id: int
    chiave: str
    tipo: str
    contenuto: dict
    adattatore: str
    registrato_il: datetime
    versione_id: int | None = None
    esito_id: int | None = None
