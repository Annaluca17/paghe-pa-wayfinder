"""Corpus di regole e parametri, con vigenza, fonte e versione."""

from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .errori import ErroreCorpus, ParametroMancante, ValiditaNonUniforme
from .formula import riferimenti
from .riferimento import motivo_rifiuto
from .tempo import Mese


def _riferimento_obbligatorio(riferimento: str, soggetto: str) -> None:
    if not isinstance(riferimento, str) or not riferimento.strip():
        raise ErroreCorpus(f"{soggetto}: riferimento normativo obbligatorio")
    motivo = motivo_rifiuto(riferimento)
    if motivo:
        raise ErroreCorpus(f"{soggetto}: riferimento non valido, {motivo}")


MATURAZIONI = {"giorni", "evento", "periodo", "annuale"}
CONTEGGI = {"lun_sab", "calendario"}
MISURE = {"intero", "parziale", "escluso"}


@dataclass(frozen=True)
class VigenzaParametro:
    dal: date
    valore: Decimal
    riferimento: str


@dataclass(frozen=True)
class Parametro:
    nome: str
    vigenze: tuple[VigenzaParametro, ...]

    def __post_init__(self) -> None:
        if not self.vigenze:
            raise ErroreCorpus(f"Parametro {self.nome}: nessuna vigenza")
        for vigenza in self.vigenze:
            _riferimento_obbligatorio(vigenza.riferimento, f"Parametro {self.nome}")
        decorrenze = [vigenza.dal for vigenza in self.vigenze]
        if len(set(decorrenze)) != len(decorrenze):
            raise ErroreCorpus(f"Parametro {self.nome}: decorrenze duplicate")
        object.__setattr__(self, "vigenze", tuple(sorted(self.vigenze, key=lambda v: v.dal)))

    def _vigente(self, giorno: date) -> VigenzaParametro | None:
        trovata = None
        for vigenza in self.vigenze:
            if vigenza.dal <= giorno:
                trovata = vigenza
        return trovata

    def vigenza_per(self, competenza: Mese) -> VigenzaParametro:
        inizio = self._vigente(competenza.primo_giorno)
        fine = self._vigente(competenza.ultimo_giorno)
        if fine is None:
            raise ParametroMancante(f"Parametro {self.nome}: nessuna vigenza per {competenza}")
        if inizio != fine:
            raise ValiditaNonUniforme(f"Parametro {self.nome}: cambia dentro {competenza}")
        return fine


@dataclass(frozen=True)
class Regola:
    """Una regola vale per un intervallo di competenza.

    Nuova vigenza: un'altra regola dello stesso istituto, con decorrenza successiva.
    Correzione: stessa vigenza e `versione` successiva, in un nuovo corpus.
    """

    istituto: str
    versione: int
    dal: date
    riferimento: str
    formula: str
    maturazione: str = ""
    al: date | None = None
    descrizione: str = ""
    applica_se: str | None = None
    conteggio: str | None = None
    divisore: str | None = None
    decimali: int | None = None

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Regola {self.istituto}")
        self._controlla_maturazione()
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"Regola {self.istituto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"Regola {self.istituto}: vigenza invertita")
        riferimenti(self.formula)

    def _controlla_maturazione(self) -> None:
        soggetto = f"Regola {self.istituto}"
        if self.maturazione not in MATURAZIONI:
            raise ErroreCorpus(f"{soggetto}: maturazione obbligatoria, una di {sorted(MATURAZIONI)}")
        a_quota = self.maturazione in ("giorni", "annuale")
        if a_quota:
            if not self.applica_se:
                raise ErroreCorpus(f"{soggetto}: una maturazione a quota richiede applica_se, il fatto che dà il servizio")
            if self.conteggio not in CONTEGGI:
                raise ErroreCorpus(f"{soggetto}: conteggio obbligatorio, uno di {sorted(CONTEGGI)}")
            if type(self.decimali) is not int or self.decimali < 0:
                raise ErroreCorpus(f"{soggetto}: decimali obbligatori")
            if not self.divisore and (self.conteggio == "lun_sab" or self.maturazione == "annuale"):
                raise ErroreCorpus(f"{soggetto}: divisore obbligatorio")
        elif self.conteggio or self.divisore or self.decimali is not None:
            raise ErroreCorpus(f"{soggetto}: conteggio, divisore e decimali valgono solo per le maturazioni a quota")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)

    def si_sovrappone(self, altra: "Regola") -> bool:
        return (altra.al is None or self.dal <= altra.al) and (self.al is None or altra.dal <= self.al)


@dataclass(frozen=True)
class Base:
    """Base imponibile: insieme degli importi pagati su cui si calcola una contribuzione (ADR 0005)."""

    nome: str
    riferimento: str

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Base {self.nome}")


@dataclass(frozen=True)
class Concorso:
    """Un istituto dichiara a quale base concorre, in che misura e per quali date di pagamento."""

    istituto: str
    base: str
    misura: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Concorso {self.istituto} -> {self.base}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.misura not in MISURE:
            raise ErroreCorpus(f"{soggetto}: misura obbligatoria, una di {sorted(MISURE)}")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)

    def si_sovrappone(self, altro: "Concorso") -> bool:
        return (altro.al is None or self.dal <= altro.al) and (self.al is None or altro.dal <= self.al)


class Corpus:
    """Insieme coerente e immutabile; la versione è l'impronta del contenuto."""

    def __init__(
        self,
        parametri: tuple[Parametro, ...],
        regole: tuple[Regola, ...],
        fatti_periodo_dichiarato: tuple[str, ...] = (),
        basi: tuple[Base, ...] = (),
        concorsi: tuple[Concorso, ...] = (),
        fatto_servizio: str | None = None,
    ):
        self.fatto_servizio = fatto_servizio
        fatti_periodo = tuple(fatti_periodo_dichiarato)
        if fatto_servizio and fatto_servizio not in fatti_periodo:
            fatti_periodo = (fatto_servizio, *fatti_periodo)
        self.fatti_periodo_dichiarato = fatti_periodo
        self._basi = {base.nome: base for base in basi}
        if len(self._basi) != len(basi):
            raise ErroreCorpus("Basi imponibili con lo stesso nome")
        self._concorsi = tuple(concorsi)
        self._parametri = {parametro.nome: parametro for parametro in parametri}
        if len(self._parametri) != len(parametri):
            raise ErroreCorpus("Parametri con lo stesso nome")
        self._regole: dict[str, list[Regola]] = {}
        for regola in regole:
            self._regole.setdefault(regola.istituto, []).append(regola)
        self._convalida()
        self._convalida_cassa()
        self.versione = self._impronta()

    def _convalida(self) -> None:
        dipendenze: dict[str, set[str]] = {}
        for istituto, regole in self._regole.items():
            dipendenze[istituto] = set()
            for indice, regola in enumerate(regole):
                for altra in regole[indice + 1 :]:
                    if regola.si_sovrappone(altra):
                        raise ErroreCorpus(f"Istituto {istituto}: regole con vigenze sovrapposte")
                letti = riferimenti(regola.formula)
                ignoti = letti.parametri - self._parametri.keys()
                if regola.divisore:
                    ignoti = ignoti | ({regola.divisore} - self._parametri.keys())
                if ignoti:
                    raise ErroreCorpus(f"Istituto {istituto}: parametri ignoti {sorted(ignoti)}")
                senza_regola = letti.importi - self._regole.keys()
                if senza_regola:
                    raise ErroreCorpus(f"Istituto {istituto}: importi senza regola {sorted(senza_regola)}")
                dipendenze[istituto] |= letti.importi
                self._controlla_livelli(regola, letti.importi)
        self._rifiuta_cicli(dipendenze)

    def _convalida_cassa(self) -> None:
        """Le regole di cassa leggono solo basi e altre regole di cassa, alla data di pagamento."""
        if self._basi and not self.fatto_servizio:
            raise ErroreCorpus("Le basi imponibili richiedono [periodo_dichiarato].servizio, il fatto che dà il servizio")
        cassa: set[str] = set()
        for istituto, regole in self._regole.items():
            for regola in regole:
                basi = riferimenti(regola.formula).basi
                ignote = basi - self._basi.keys()
                if ignote:
                    raise ErroreCorpus(f"Istituto {istituto}: basi ignote {sorted(ignote)}")
                if basi and regola.maturazione != "periodo":
                    raise ErroreCorpus(f"Regola {istituto}: solo una regola sul periodo dichiarato legge una base")
                if basi:
                    cassa.add(istituto)
        allargato = True
        while allargato:
            allargato = False
            for istituto, regole in self._regole.items():
                if istituto not in cassa and any(riferimenti(r.formula).importi & cassa for r in regole):
                    cassa.add(istituto)
                    allargato = True
        for istituto in cassa:
            for regola in self._regole[istituto]:
                letti = riferimenti(regola.formula)
                if not letti.basi and not letti.importi:
                    raise ErroreCorpus(f"Istituto {istituto}: regole di cassa e regole per competenza insieme")
                if letti.importi - cassa:
                    raise ErroreCorpus(
                        f"Regola {istituto}: una regola di cassa non legge importi per competenza {sorted(letti.importi - cassa)}"
                    )
        self.istituti_di_cassa = frozenset(cassa)
        for indice, concorso in enumerate(self._concorsi):
            if concorso.istituto not in self._regole:
                raise ErroreCorpus(f"Concorso: istituto senza regola {concorso.istituto}")
            if concorso.base not in self._basi:
                raise ErroreCorpus(f"Concorso {concorso.istituto}: base ignota {concorso.base}")
            for altro in self._concorsi[indice + 1 :]:
                if (altro.istituto, altro.base) == (concorso.istituto, concorso.base) and concorso.si_sovrappone(altro):
                    raise ErroreCorpus(f"Concorso {concorso.istituto} -> {concorso.base}: vigenze sovrapposte")

    def _controlla_livelli(self, regola: Regola, importi: frozenset[str]) -> None:
        """Una frazione non legge il periodo dichiarato, che ne è la somma; l'annuale legge solo fatti e parametri."""
        for nome in importi:
            if regola.maturazione == "annuale":
                raise ErroreCorpus(f"Regola {regola.istituto}: una regola annuale non legge importi")
            for dipendenza in self._regole[nome]:
                if dipendenza.maturazione == "annuale":
                    raise ErroreCorpus(f"Regola {regola.istituto}: non può leggere l'importo annuale {nome}")
                if dipendenza.maturazione == "periodo" and regola.maturazione != "periodo":
                    raise ErroreCorpus(f"Regola {regola.istituto}: una frazione non legge il periodo dichiarato {nome}")

    @staticmethod
    def _rifiuta_cicli(dipendenze: dict[str, set[str]]) -> None:
        conclusi: set[str] = set()

        def visita(istituto: str, percorso: tuple[str, ...]) -> None:
            if istituto in percorso:
                raise ErroreCorpus("Ciclo tra importi: " + " -> ".join((*percorso, istituto)))
            if istituto in conclusi:
                return
            for dipendenza in sorted(dipendenze[istituto]):
                visita(dipendenza, (*percorso, istituto))
            conclusi.add(istituto)

        for istituto in sorted(dipendenze):
            visita(istituto, ())

    def _impronta(self) -> str:
        contenuto = {
            "fatti_periodo_dichiarato": sorted(self.fatti_periodo_dichiarato),
            "servizio": self.fatto_servizio,
            "basi": [[base.nome, base.riferimento] for _, base in sorted(self._basi.items())],
            "concorsi": sorted(
                [c.istituto, c.base, c.dal.isoformat(), c.al.isoformat() if c.al else "", c.misura, c.riferimento]
                for c in self._concorsi
            ),
            "parametri": [
                {
                    "nome": parametro.nome,
                    "vigenze": [[v.dal.isoformat(), str(v.valore), v.riferimento] for v in parametro.vigenze],
                }
                for _, parametro in sorted(self._parametri.items())
            ],
            "regole": sorted(
                [
                    [r.istituto, r.dal.isoformat(), r.versione, r.al.isoformat() if r.al else None,
                     r.riferimento, r.formula, r.applica_se, r.maturazione, r.conteggio, r.divisore, r.decimali]
                    for regole in self._regole.values()
                    for r in regole
                ],
                key=lambda riga: (riga[0], riga[1]),
            ),
        }
        testo = json.dumps(contenuto, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:16]

    def istituti(self) -> list[str]:
        return sorted(self._regole)

    def parametro(self, nome: str) -> Parametro:
        return self._parametri[nome]

    def basi(self) -> tuple[Base, ...]:
        return tuple(base for _, base in sorted(self._basi.items()))

    def concorso(self, istituto: str, base: str, giorno: date) -> Concorso | None:
        """Dichiarazione vigente alla data di pagamento; None se l'istituto non dichiara nulla."""
        for concorso in self._concorsi:
            if (concorso.istituto, concorso.base) == (istituto, base) and concorso.copre(giorno):
                return concorso
        return None

    def regola_iniziata(self, istituto: str, giorno: date) -> bool:
        """Vero se l'istituto ha già una regola decorrente a quella data, anche se oggi scaduta."""
        return any(regola.dal <= giorno for regola in self._regole.get(istituto, ()))

    def regole_annuali(self) -> list[Regola]:
        """Una regola annuale per istituto: la vigente si sceglie sull'ultimo giorno di servizio."""
        trovate = {}
        for istituto, regole in sorted(self._regole.items()):
            for regola in regole:
                if regola.maturazione == "annuale":
                    trovate.setdefault(istituto, regola)
        return list(trovate.values())

    def tipi_fatto(self) -> tuple[str, ...]:
        """I tipi di fatto che possono dividere il mese in frazioni."""
        tipi = set(self.fatti_periodo_dichiarato)
        for regole in self._regole.values():
            for regola in regole:
                tipi |= riferimenti(regola.formula).fatti
                if regola.applica_se and regola.maturazione != "annuale":
                    tipi.add(regola.applica_se)
        return tuple(sorted(tipi))

    def firma_giorno(self, giorno: date) -> tuple:
        """Regole e parametri vigenti in un giorno: se cambia, il mese si divide."""
        parametri = []
        for nome, parametro in sorted(self._parametri.items()):
            vigenza = parametro._vigente(giorno)
            parametri.append((nome, vigenza.dal if vigenza else None))
        regole = tuple(
            (regola.istituto, regola.dal)
            for _, gruppo in sorted(self._regole.items())
            for regola in gruppo
            if regola.copre(giorno)
        )
        return (tuple(parametri), regole)

    def regola_per(self, istituto: str, competenza) -> Regola | None:
        """Regola che copre tutto il mese o periodo; None se l'istituto non ne ha alcuna."""
        presenti = [
            regola
            for regola in self._regole.get(istituto, [])
            if any(regola.copre(giorno) for giorno in competenza.giorni())
        ]
        if not presenti:
            return None
        if len(presenti) > 1 or not all(presenti[0].copre(giorno) for giorno in competenza.giorni()):
            raise ValiditaNonUniforme(f"Istituto {istituto}: la regola cambia dentro {competenza}")
        return presenti[0]

    @classmethod
    def da_toml(cls, testo: str) -> "Corpus":
        try:
            dati = tomllib.loads(testo)
            parametri = tuple(_parametro_da_toml(voce) for voce in dati.get("parametro", []))
            regole = tuple(_regola_da_toml(voce) for voce in dati.get("regola", []))
            basi = tuple(Base(voce["nome"], voce["riferimento"]) for voce in dati.get("base", []))
            concorsi = tuple(concorso for voce in dati.get("concorso", []) for concorso in _concorsi_da_toml(voce))
        except (tomllib.TOMLDecodeError, KeyError, TypeError) as errore:
            raise ErroreCorpus(f"Corpus TOML non valido: {errore!r}") from errore
        periodo = dati.get("periodo_dichiarato", {})
        return cls(parametri, regole, tuple(periodo.get("fatti", ())), basi, concorsi, periodo.get("servizio"))

    @classmethod
    def carica(cls, percorso: str | Path) -> "Corpus":
        return cls.da_toml(Path(percorso).read_text(encoding="utf-8"))


def _data(valore: object, campo: str) -> date:
    if isinstance(valore, datetime) or not isinstance(valore, date):
        raise ErroreCorpus(f"{campo}: serve una data, trovato {valore!r}")
    return valore


def _parametro_da_toml(voce: dict) -> Parametro:
    vigenze = []
    for vigenza in voce["vigenza"]:
        if not isinstance(vigenza["valore"], str):
            raise ErroreCorpus(f"Parametro {voce['nome']}: il valore va scritto come testo")
        try:
            valore = Decimal(vigenza["valore"])
        except InvalidOperation as errore:
            raise ErroreCorpus(f"Parametro {voce['nome']}: valore non numerico") from errore
        if not valore.is_finite():
            raise ErroreCorpus(f"Parametro {voce['nome']}: valore non finito")
        vigenze.append(VigenzaParametro(_data(vigenza["dal"], "dal"), valore, vigenza["riferimento"]))
    return Parametro(voce["nome"], tuple(vigenze))


def _concorsi_da_toml(voce: dict) -> list[Concorso]:
    if not voce["basi"]:
        raise ErroreCorpus(f"Concorso {voce['istituto']}: basi obbligatorie")
    return [
        Concorso(
            istituto=voce["istituto"],
            base=base,
            misura=voce["misura"],
            dal=_data(voce["dal"], "dal"),
            al=_data(voce["al"], "al") if "al" in voce else None,
            riferimento=voce["riferimento"],
        )
        for base in voce["basi"]
    ]


def _regola_da_toml(voce: dict) -> Regola:
    return Regola(
        istituto=voce["istituto"],
        versione=voce["versione"],
        dal=_data(voce["dal"], "dal"),
        al=_data(voce["al"], "al") if "al" in voce else None,
        riferimento=voce["riferimento"],
        formula=voce["formula"],
        descrizione=voce.get("descrizione", ""),
        applica_se=voce.get("applica_se"),
        maturazione=voce.get("maturazione", ""),
        conteggio=voce.get("conteggio"),
        divisore=voce.get("divisore"),
        decimali=voce.get("decimali"),
    )
