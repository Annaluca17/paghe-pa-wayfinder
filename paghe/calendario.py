"""Giorni festivi di un anno: Pasqua calcolata e patrono della sede di lavoro (ticket #106).

Il calendario nazionale è un dato del corpus (`CalendarioFestivi`, con il riferimento di legge); qui stanno solo le
regole pure che non cambiano da un anno all'altro.

Il patrono è un fatto datato della sede di lavoro del rapporto, tipo `patrono_sede_lavoro`, con valore
`"<codice comune> MM-GG"` (per esempio `"H501 06-29"`). Per il segretario in convenzione vale il patrono del comune
capofila: basta che l'ufficio registri sul rapporto del segretario quello del capofila, senza logica speciale.
Un patrono di sabato, di domenica o che cade su una festa nazionale non aggiunge giorni: i festivi sono un'unione di
insiemi.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

from .errori import ErroreCalcolo

TIPO_PATRONO = "patrono_sede_lavoro"

_PATRONO = re.compile(r"(?P<comune>[A-Z]\d{3}) (?P<mese>\d{2})-(?P<giorno>\d{2})")


def pasqua(anno: int) -> date:
    """Domenica di Pasqua gregoriana, con l'algoritmo di Gauss nella forma di Meeus."""
    a, b, c = anno % 19, anno // 100, anno % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    ll = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ll) // 451
    mese, giorno = divmod(h + ll - 7 * m + 114, 31)
    return date(anno, mese, giorno + 1)


def lunedi_dell_angelo(anno: int) -> date:
    return pasqua(anno) + timedelta(days=1)


def e_patrono(valore: str, giorno: date) -> bool:
    """Vero se il giorno è la festa del patrono dichiarata; errore chiaro se il valore è malformato."""
    trovato = _PATRONO.fullmatch(str(valore))
    if trovato is None:
        raise ErroreCalcolo(f"Patrono della sede di lavoro non valido: {valore!r}; serve «<codice comune> MM-GG»")
    mese, giorno_del_mese = int(trovato["mese"]), int(trovato["giorno"])
    try:
        date(2000, mese, giorno_del_mese)  # anno bisestile: il 29 febbraio è ammesso
    except ValueError:
        raise ErroreCalcolo(f"Patrono della sede di lavoro non valido: {valore!r}; data inesistente") from None
    return (giorno.month, giorno.day) == (mese, giorno_del_mese)


def e_lavorativo(calendario, giorno: date, patrono: str | None = None) -> bool:
    """Giorno da lunedì a venerdì non festivo: né nazionale (calendario dell'anno) né patrono della sede.

    `patrono` è il valore del fatto vigente quel giorno (None se la sede non ne ha registrato uno).
    """
    del_patrono = patrono is not None and e_patrono(patrono, giorno)  # un valore malformato dà errore anche nel weekend
    return giorno.weekday() < 5 and giorno not in calendario.giorni and not del_patrono
