"""Fatti contabili degli impegni, disponibilità e abbinamento delle righe di proposta (ADR 0031).

Il modello non produce impegni: li legge come fatti contabili che la Ragioneria comunica, con un identificativo
stabile. Per lo stesso (esercizio, numero) vale la disponibilità con la data più recente. Il modello sottrae da
quella disponibilità le righe delle proprie versioni inviate o confermate, registrate dalla data in poi.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .errori import ErroreRegistro
from .corpus import PIANO_DEI_CONTI
from .registro import Registro, _in_decimale
from .tempo import in_utc

TIPO_IMPEGNO = "fatto_contabile_impegno"


@dataclass(frozen=True)
class AttoPresupposto:
    """L'atto da cui nasce l'impegno: il tipo, che l'origine dell'istituto dichiara, e il riferimento."""

    tipo: str
    riferimento: str


@dataclass(frozen=True)
class Impegno:
    numero: int
    esercizio: int
    piano_dei_conti: str
    missione: str
    programma: str
    atto: AttoPresupposto | None
    disponibilita: Decimal
    data: date

    @property
    def chiave(self) -> tuple[int, int]:
        return (self.esercizio, self.numero)


def _contenuto(impegno: Impegno) -> dict:
    return {
        "numero": impegno.numero,
        "esercizio": impegno.esercizio,
        "piano_dei_conti": impegno.piano_dei_conti,
        "missione": impegno.missione,
        "programma": impegno.programma,
        "atto": {"tipo": impegno.atto.tipo, "riferimento": impegno.atto.riferimento} if impegno.atto else None,
        "disponibilita": str(impegno.disponibilita),
        "data": impegno.data.isoformat(),
    }


def _da_contenuto(dati: dict) -> Impegno:
    atto = AttoPresupposto(dati["atto"]["tipo"], dati["atto"]["riferimento"]) if dati["atto"] else None
    return Impegno(
        dati["numero"],
        dati["esercizio"],
        dati["piano_dei_conti"],
        dati["missione"],
        dati["programma"],
        atto,
        Decimal(dati["disponibilita"]),
        date.fromisoformat(dati["data"]),
    )


def registra_impegno(
    registro: Registro,
    chiave: str,
    adattatore: str,
    numero: int,
    esercizio: int,
    piano_dei_conti: str,
    missione: str,
    programma: str,
    disponibilita: Decimal | int | str,
    data: date,
    atto: AttoPresupposto | None = None,
) -> Impegno:
    """Fatto contabile in ingresso: l'impegno con la sua disponibilità alla `data` (nessun atto se è automatico)."""
    if not isinstance(numero, int) or isinstance(numero, bool) or numero < 1:
        raise ErroreRegistro(f"Numero dell'impegno non valido: {numero!r}")
    if not isinstance(esercizio, int) or isinstance(esercizio, bool):
        raise ErroreRegistro(f"Esercizio dell'impegno non valido: {esercizio!r}")
    if not isinstance(piano_dei_conti, str) or not PIANO_DEI_CONTI.fullmatch(piano_dei_conti):
        raise ErroreRegistro(f"Codice del piano dei conti non valido: {piano_dei_conti!r}")
    for nome, valore in (("missione", missione), ("programma", programma)):
        if not isinstance(valore, str) or not re.fullmatch(r"\d{2}", valore):
            raise ErroreRegistro(f"Impegno: {nome} non valida, {valore!r}; serve un codice di due cifre")
    importo = _in_decimale(disponibilita)
    if importo < 0:
        raise ErroreRegistro(f"La disponibilità dell'impegno non è negativa: {disponibilita!r}")
    impegno = Impegno(numero, esercizio, piano_dei_conti, missione, programma, atto, importo, data)
    contenuto = _contenuto(impegno)
    if registro.evento_identico(chiave, TIPO_IMPEGNO, contenuto) is None:
        registro.registra_evento(chiave, TIPO_IMPEGNO, contenuto, adattatore)
    return impegno


def impegni_noti(registro: Registro, noto_al: datetime) -> dict[tuple[int, int], Impegno]:
    """Gli impegni noti all'istante, per (esercizio, numero); vale la disponibilità con la data più recente."""
    noti: dict[tuple[int, int], Impegno] = {}
    for evento in registro.eventi(TIPO_IMPEGNO, noto_al):
        impegno = _da_contenuto(evento.contenuto)
        attuale = noti.get(impegno.chiave)
        if attuale is None or impegno.data >= attuale.data:
            noti[impegno.chiave] = impegno
    return noti


# Disponibilità e abbinamento

STATI_VIVI = ("inviata", "confermata")
AUTOMATICO = "automatico"
# Cambio di abbinamento fatto dalla Ragioneria in conferma, con l'impegno proposto e quello scelto (ADR 0031).
TIPO_ABBINAMENTO = "abbinamento_confermato"


def chiave_riga(piano_dei_conti: str, missione: str, programma: str, impegno: tuple[int, int] | None) -> list:
    """La chiave di una riga di proposta nella forma in cui sta nel registro."""
    return [piano_dei_conti, missione, programma, list(impegno) if impegno else None]


@dataclass(frozen=True)
class Abbinamento:
    """L'impegno scelto per una riga, o perché non c'è: nessun impegno adatto noto, o nessuno capiente."""

    impegno: Impegno | None
    adatti: int
    mancante: Decimal = Decimal(0)


class DisponibilitaImpegni:
    """Impegni noti e righe delle versioni vive a un istante: da qui la disponibilità residua e la regola di abbinamento."""

    def __init__(self, registro: Registro, istante: datetime):
        self.noti = impegni_noti(registro, istante)
        self._consumi: list[tuple[date, tuple[int, int], Decimal]] = []
        for versione_id in registro.versioni_registrate(istante):
            stati = registro.stati_versione(versione_id, istante)
            if not stati or stati[-1][0] not in STATI_VIVI:
                continue
            _, registrato, dati = registro.versione_registrata(versione_id)
            scelte = {
                json.dumps(evento.contenuto["riga"]): tuple(evento.contenuto["scelto"])
                for evento in registro.eventi(TIPO_ABBINAMENTO, istante)
                if evento.versione_id == versione_id
            }
            for riga in dati.get("righe_proposta", []):
                proposto = tuple(riga["impegno"]) if riga["impegno"] else None
                chiave = json.dumps(chiave_riga(riga["piano_dei_conti"], riga["missione"], riga["programma"], proposto))
                effettivo = scelte.get(chiave, proposto)
                if effettivo is not None:
                    self._consumi.append((registrato.date(), effettivo, Decimal(riga["totale"])))

    def residua(self, impegno: Impegno) -> Decimal:
        """Disponibilità a una data meno le righe delle versioni vive registrate da quella data in poi."""
        usato = sum(
            (totale for registrata, chiave, totale in self._consumi if chiave == impegno.chiave and registrata >= impegno.data),
            Decimal(0),
        )
        return impegno.disponibilita - usato

    def adatti(self, piano_dei_conti: str, missione: str, programma: str, origine: str, anno: int) -> list[Impegno]:
        """Gli impegni noti adatti, nell'ordine di preferenza: l'esercizio della valuta, poi i residui dal più vecchio."""
        stessa = [
            i for i in self.noti.values()
            if (i.piano_dei_conti, i.missione, i.programma) == (piano_dei_conti, missione, programma)
        ]
        if origine == AUTOMATICO:
            ammessi = [i for i in stessa if i.atto is None and i.esercizio == anno]
        else:
            ammessi = [i for i in stessa if i.atto is not None and i.atto.tipo == origine and i.esercizio <= anno]
        return sorted(ammessi, key=lambda i: (i.esercizio != anno, i.esercizio, i.numero))

    def abbina(
        self, piano_dei_conti: str, missione: str, programma: str, origine: str, anno: int, totale: Decimal
    ) -> Abbinamento:
        """Il primo impegno adatto con capienza sulla riga intera, che non si spezza mai su due impegni."""
        adatti = self.adatti(piano_dei_conti, missione, programma, origine, anno)
        for impegno in adatti:
            if self.residua(impegno) >= totale:
                return Abbinamento(impegno, len(adatti))
        if not adatti:
            return Abbinamento(None, 0)
        return Abbinamento(None, len(adatti), totale - max(self.residua(i) for i in adatti))


def disponibilita_residua(registro: Registro, esercizio: int, numero: int, noto_al: datetime | None = None) -> Decimal:
    """Quanto resta dell'impegno: la disponibilità più recente meno le righe abbinate delle versioni vive."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    disponibilita = DisponibilitaImpegni(registro, istante)
    impegno = disponibilita.noti.get((esercizio, numero))
    if impegno is None:
        raise ErroreRegistro(f"Impegno {esercizio}/{numero} non noto al {istante}")
    return disponibilita.residua(impegno)


@dataclass(frozen=True)
class CambioAbbinamento:
    """Traccia di una conferma: per la riga, l'impegno proposto dal modello e quello scelto dalla Ragioneria."""

    riga: tuple[str, str, str, tuple[int, int] | None]
    proposto: tuple[int, int] | None
    scelto: tuple[int, int]
    incapiente: bool


def registra_cambio_abbinamento(
    registro: Registro, versione_id: int, riga: tuple, proposto: tuple[int, int] | None, scelto: tuple[int, int], incapiente: bool
) -> None:
    contenuto = {
        "riga": chiave_riga(*riga),
        "proposto": list(proposto) if proposto else None,
        "scelto": list(scelto),
        "incapiente": incapiente,
    }
    chiave = f"abbinamento:{versione_id}:{json.dumps(contenuto['riga'])}"
    registro.registra_evento(chiave, TIPO_ABBINAMENTO, contenuto, "ragioneria", versione_id)


def abbinamenti_confermati(registro: Registro, versione_id: int, noto_al: datetime | None = None) -> tuple[CambioAbbinamento, ...]:
    """I cambi di abbinamento che la Ragioneria ha fatto confermando la versione."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    return tuple(
        CambioAbbinamento(
            (e.contenuto["riga"][0], e.contenuto["riga"][1], e.contenuto["riga"][2],
             tuple(e.contenuto["riga"][3]) if e.contenuto["riga"][3] else None),
            tuple(e.contenuto["proposto"]) if e.contenuto["proposto"] else None,
            tuple(e.contenuto["scelto"]),
            e.contenuto["incapiente"],
        )
        for e in registro.eventi(TIPO_ABBINAMENTO, istante)
        if e.versione_id == versione_id
    )
