"""Codici fiscali di fantasia con il carattere di controllo calcolato (mai scritto a mano).

Le sei lettere di cognome e nome seguono la regola standard sui nomi di fantasia dello scenario; data e luogo di
nascita sono scelti a caso. Nessun codice qui e' tratto da un flusso reale.
"""

from __future__ import annotations

_DISPARI = {
    **dict(zip("0123456789", (1, 0, 5, 7, 9, 13, 15, 17, 19, 21))),
    **dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", (1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23))),
}
_PARI = {**{c: int(c) for c in "0123456789"}, **{c: i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}}
_MESI = "ABCDEHLMPRST"
_VOCALI = "AEIOU"


def carattere_di_controllo(quindici: str) -> str:
    """Il sedicesimo carattere: somma dei valori per posizione dispari e pari, modulo 26."""
    if len(quindici) != 15:
        raise ValueError(f"Servono 15 caratteri, trovati {len(quindici)}")
    somma = sum((_DISPARI if indice % 2 == 0 else _PARI)[c] for indice, c in enumerate(quindici))
    return chr(ord("A") + somma % 26)


def _consonanti_e_vocali(testo: str) -> tuple[str, str]:
    lettere = [c for c in testo.upper() if c.isalpha()]
    return "".join(c for c in lettere if c not in _VOCALI), "".join(c for c in lettere if c in _VOCALI)


def _codice_cognome(cognome: str) -> str:
    consonanti, vocali = _consonanti_e_vocali(cognome)
    return (consonanti + vocali + "XXX")[:3]


def _codice_nome(nome: str) -> str:
    consonanti, vocali = _consonanti_e_vocali(nome)
    if len(consonanti) >= 4:
        consonanti = consonanti[0] + consonanti[2] + consonanti[3]
    return (consonanti + vocali + "XXX")[:3]


def codice_fiscale(cognome: str, nome: str, anno: int, mese: int, giorno: int, comune: str = "H501") -> str:
    """Codice fiscale maschile di fantasia, con il carattere di controllo."""
    quindici = f"{_codice_cognome(cognome)}{_codice_nome(nome)}{anno % 100:02d}{_MESI[mese - 1]}{giorno:02d}{comune}"
    return quindici + carattere_di_controllo(quindici)
