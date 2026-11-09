"""Controllo formale del codice fiscale delle persone fisiche: 16 caratteri e carattere di controllo (D.M. 23/12/1976)."""

from __future__ import annotations

import re

_FORMA = re.compile(r"[A-Z0-9]{16}")  # le lettere al posto delle cifre sono le omocodie
_DISPARI = dict(zip("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", (
    1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23,
)))


def _valore_pari(carattere: str) -> int:
    return int(carattere) if carattere.isdigit() else ord(carattere) - ord("A")


def codice_fiscale_valido(codice: object) -> bool:
    """Sedici caratteri maiuscoli con il carattere di controllo corretto. Non verifica che i dati anagrafici tornino."""
    if not isinstance(codice, str) or not _FORMA.fullmatch(codice):
        return False
    somma = sum(_DISPARI[c] if indice % 2 == 0 else _valore_pari(c) for indice, c in enumerate(codice[:15]))
    return codice[15] == chr(ord("A") + somma % 26)
