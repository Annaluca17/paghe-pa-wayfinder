"""Fatti contabili degli impegni, disponibilità e abbinamento delle righe di proposta (ADR 0031).

Il modello non produce impegni: li legge come fatti contabili che la Ragioneria comunica, con un identificativo
stabile. Per lo stesso (esercizio, numero) vale la disponibilità con la data più recente. Il modello sottrae da
quella disponibilità le righe delle proprie versioni inviate o confermate, registrate dalla data in poi.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .errori import ErroreRegistro
from .corpus import PIANO_DEI_CONTI
from .registro import Registro, _in_decimale

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
