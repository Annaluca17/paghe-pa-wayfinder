"""Sintassi del campo riferimento (ricerca #17, ADR 0003).

Il riferimento identifica la fonte e non contiene mai un URL. Il controllo è solo
sintattico e non usa la rete: l'esistenza dell'atto si verifica a parte.
"""

from __future__ import annotations

import re
from datetime import date

_DATA = r"\d{4}-\d{2}-\d{2}"
_TOK = r"[a-z0-9]+(?:\.[a-z0-9]+)*"
_NUM = r"[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*"
_VAL = r"[0-9a-zA-Z]+(?:\.[0-9a-zA-Z]+)*"
_SEG = rf"(?:art|com|let|num|par|pag|all|tab){_VAL}"
_PART = rf"~{_SEG}(?:-{_SEG})*"

_CITAZIONE = re.compile(
    rf"""^(?:
    urn:nir:(?P<aut>{_TOK}):(?P<tipo>{_TOK}):(?P<data>{_DATA})(?:;(?P<num>{_NUM}))?(?::\d+)?(?P<part>{_PART})?(?:!vig=(?P<vig>{_DATA})|@originale)?
    |ccnl:[A-Z][0-9A-Z]{{3}}:(?P<cdata>{_DATA})(?P<cpart>{_PART})?
    |prassi:(?P<emit>{_TOK}):(?P<ptipo>{_TOK}):(?P<pdata>{_DATA});{_NUM}(?P<ppart>{_PART})?
    |ente:[a-z0-9_]+:{_TOK}:(?P<adata>{_DATA})(?:;{_NUM})?(?P<apart>{_PART})?
    |fittizio:[a-z0-9.-]+
    )$""",
    re.VERBOSE,
)

_ORDINE = {"all": 0, "art": 1, "par": 1, "pag": 1, "tab": 1, "com": 2, "let": 3, "num": 4}

# Elenchi chiusi: si ampliano quando una fonte reale lo richiede, così un refuso non passa.
_TIPI_NORMA = {
    "legge",
    "decreto.legge",
    "decreto.legislativo",
    "decreto.del.presidente.della.repubblica",
    "costituzione",
}
_TIPI_REGIONALI = {"legge", "regolamento"}
_TIPI_PRASSI = {
    "inps": {"circolare", "messaggio", "documento.tecnico"},
    "inpdap": {"nota.operativa"},
    "immedia": {"nota"},
    "ade": {"circolare", "risoluzione", "risposta.interpello", "provvedimento", "comunicato.stampa", "istruzioni"},
}


def _data_valida(testo: str | None) -> bool:
    if testo is None:
        return True
    try:
        date.fromisoformat(testo)
    except ValueError:
        return False
    return True


def _motivo_citazione(citazione: str) -> str | None:
    trovata = _CITAZIONE.match(citazione)
    if trovata is None:
        return f"sintassi non riconosciuta: {citazione!r}"

    gruppi = trovata.groupdict()
    for nome in ("data", "cdata", "pdata", "adata", "vig"):
        if not _data_valida(gruppi[nome]):
            return f"data inesistente: {citazione!r}"

    partizione = gruppi["part"] or gruppi["cpart"] or gruppi["ppart"] or gruppi["apart"]
    if partizione:
        livelli = [_ORDINE[segmento[:3]] for segmento in partizione[1:].split("-")]
        if livelli != sorted(livelli) or len(set(livelli)) != len(livelli):
            return f"partizioni fuori ordine o ripetute: {citazione!r}"

    autorita = gruppi["aut"]
    if autorita is not None:
        tipo = gruppi["tipo"]
        if autorita == "stato":
            if tipo not in _TIPI_NORMA:
                return f"tipo di norma non previsto, {tipo!r}: {citazione!r}"
        elif autorita.startswith("regione."):
            if tipo not in _TIPI_REGIONALI:
                return f"tipo di norma regionale non previsto, {tipo!r}: {citazione!r}"
        else:
            return f"autorità non prevista, {autorita!r}: {citazione!r}"
        if tipo != "costituzione" and not gruppi["num"]:
            return f"numero mancante: {citazione!r}"

    emittente = gruppi["emit"]
    if emittente is not None:
        tipi = _TIPI_PRASSI.get(emittente)
        if tipi is None:
            return f"emittente non previsto, {emittente!r}: {citazione!r}"
        if gruppi["ptipo"] not in tipi:
            return f"tipo di prassi non previsto, {gruppi['ptipo']!r}: {citazione!r}"
    return None


def motivo_rifiuto(riferimento: str) -> str | None:
    """None se il riferimento è valido, altrimenti il motivo del rifiuto."""
    if not isinstance(riferimento, str) or not riferimento.strip():
        return "riferimento vuoto"
    for citazione in riferimento.split(" + "):
        motivo = _motivo_citazione(citazione)
        if motivo:
            return motivo
    return None


def solo_prassi(riferimento: str) -> bool:
    """Vero se ogni citazione è una nota di prassi interna: la regola va segnalata (ADR 0004)."""
    return all(citazione.startswith("prassi:immedia:") for citazione in riferimento.split(" + "))


def data_atto(riferimento: str) -> date | None:
    """Data dell'atto che fissa il valore: la prima citazione. None per i riferimenti fittizi."""
    trovata = _CITAZIONE.match(riferimento.split(" + ")[0])
    if trovata is None:
        return None
    gruppi = trovata.groupdict()
    testo = gruppi["data"] or gruppi["cdata"] or gruppi["pdata"] or gruppi["adata"]
    return date.fromisoformat(testo) if testo else None
