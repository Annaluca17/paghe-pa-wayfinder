"""Grammatica delle formule delle regole.

Una formula è testo, non codice: viene analizzata e mai eseguita. Ammette
`fatto.x`, `parametro.x`, `importo.x`, `base.x`, `fisco.x`, le quattro operazioni, il meno unario,
`min`, `max`, `arrotonda(valore, decimali)` e `se(condizione, allora, altrimenti)`.

`se` sceglie fra due espressioni con un solo confronto (`<`, `<=`, `>`, `>=`) fra due espressioni:
serve alle norme a fasce con un salto, che con `min` e `max` non si scrivono (ADR 0002, ticket #93).
Il confronto vale solo come primo argomento di `se`; si valuta soltanto il ramo scelto.

Le costanti sono solo intere: un valore normativo non può stare in una formula,
deve essere un parametro con vigenza e fonte. L'arrotondamento non è implicito:
lo dichiara la regola, perché dipende dalla norma (ticket #15).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, DecimalException, localcontext
from functools import lru_cache
from typing import Callable

from .errori import ErroreFormula

PRECISIONE = 50
SORGENTI = {"fatto", "parametro", "importo", "base", "fisco"}
OPERATORI = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
}
CONFRONTI = {
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
}


@dataclass(frozen=True)
class Riferimenti:
    """Nomi letti da una formula."""

    fatti: frozenset[str]
    parametri: frozenset[str]
    importi: frozenset[str]
    basi: frozenset[str] = frozenset()
    fisco: frozenset[str] = frozenset()


@lru_cache(maxsize=None)
def _compila(sorgente: str) -> ast.expr:
    if not sorgente.strip():
        raise ErroreFormula("Formula vuota")
    try:
        radice = ast.parse(sorgente.strip(), mode="eval").body
    except SyntaxError as errore:
        raise ErroreFormula(f"Sintassi non valida: {sorgente!r}") from errore
    _controlla(radice, sorgente)
    return radice


def _controlla(nodo: ast.expr, sorgente: str) -> None:
    match nodo:
        case ast.BinOp(left=sinistra, op=op, right=destra) if type(op) in OPERATORI:
            _controlla(sinistra, sorgente)
            _controlla(destra, sorgente)
        case ast.UnaryOp(op=ast.USub(), operand=operando):
            _controlla(operando, sorgente)
        case ast.Constant(value=valore) if type(valore) is int:
            pass
        case ast.Constant():
            raise ErroreFormula(
                f"Costante non ammessa in {sorgente!r}: "
                "i valori normativi vanno espressi come parametri"
            )
        case ast.Attribute(value=ast.Name(id=origine)) if origine in SORGENTI:
            pass
        case ast.Call(func=ast.Name(id="arrotonda"), args=[valore, ast.Constant(value=decimali)], keywords=[]):
            if type(decimali) is not int or decimali < 0:
                raise ErroreFormula(f"Decimali non validi in {sorgente!r}")
            _controlla(valore, sorgente)
        case ast.Call(func=ast.Name(id="min" | "max"), args=argomenti, keywords=[]) if argomenti:
            for argomento in argomenti:
                _controlla(argomento, sorgente)
        case ast.Call(func=ast.Name(id="se"), args=[condizione, allora, altrimenti], keywords=[]):
            match condizione:
                case ast.Compare(left=sinistra, ops=[op], comparators=[destra]) if type(op) in CONFRONTI:
                    _controlla(sinistra, sorgente)
                    _controlla(destra, sorgente)
                case _:
                    raise ErroreFormula(
                        f"Condizione non ammessa in {sorgente!r}: serve un solo confronto fra <, <=, > e >="
                    )
            _controlla(allora, sorgente)
            _controlla(altrimenti, sorgente)
        case _:
            raise ErroreFormula(f"Elemento non ammesso in {sorgente!r}: {ast.dump(nodo)}")


def riferimenti(sorgente: str) -> Riferimenti:
    """Dichiara cosa legge la formula, senza valutarla."""
    trovati: dict[str, set[str]] = {origine: set() for origine in SORGENTI}
    for nodo in ast.walk(_compila(sorgente)):
        if isinstance(nodo, ast.Attribute) and isinstance(nodo.value, ast.Name):
            trovati[nodo.value.id].add(nodo.attr)
    return Riferimenti(
        fatti=frozenset(trovati["fatto"]),
        parametri=frozenset(trovati["parametro"]),
        importi=frozenset(trovati["importo"]),
        basi=frozenset(trovati["base"]),
        fisco=frozenset(trovati["fisco"]),
    )


def valuta(sorgente: str, risolvi: Callable[[str, str], Decimal]) -> Decimal:
    """Valuta la formula; `risolvi(origine, nome)` fornisce i valori letti."""
    radice = _compila(sorgente)
    with localcontext() as contesto:
        contesto.prec = PRECISIONE
        try:
            return _valuta(radice, risolvi)
        except DecimalException as errore:
            raise ErroreFormula(f"Formula non valutabile {sorgente!r}: {errore!r}") from errore


def _valuta(nodo: ast.expr, risolvi: Callable[[str, str], Decimal]) -> Decimal:
    match nodo:
        case ast.BinOp(left=sinistra, op=op, right=destra):
            return OPERATORI[type(op)](_valuta(sinistra, risolvi), _valuta(destra, risolvi))
        case ast.UnaryOp(operand=operando):
            return -_valuta(operando, risolvi)
        case ast.Constant(value=valore):
            return Decimal(valore)
        case ast.Attribute(value=ast.Name(id=origine), attr=nome):
            return risolvi(origine, nome)
        case ast.Call(func=ast.Name(id="arrotonda"), args=[valore, ast.Constant(value=decimali)]):
            passo = Decimal(1).scaleb(-decimali)
            return _valuta(valore, risolvi).quantize(passo, rounding=ROUND_HALF_UP)
        case ast.Call(func=ast.Name(id="se"), args=[condizione, allora, altrimenti]):
            sinistra, destra = condizione.left, condizione.comparators[0]
            vero = CONFRONTI[type(condizione.ops[0])](_valuta(sinistra, risolvi), _valuta(destra, risolvi))
            return _valuta(allora if vero else altrimenti, risolvi)
        case ast.Call(func=ast.Name(id=nome), args=argomenti):
            funzione = min if nome == "min" else max
            return funzione(_valuta(argomento, risolvi) for argomento in argomenti)
    raise ErroreFormula(f"Nodo non valutabile: {ast.dump(nodo)}")
