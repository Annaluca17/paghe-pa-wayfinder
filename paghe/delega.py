"""Delega F24EP: vista del modello dagli esiti pagati alla delega trasmessa e versata (ADR 0023, 0025).

La delega nasce dalla composizione del pagamento: le righe con canale F24EP degli esiti pagati, non
ancora versate, diventano righe per sezione, codice tributo o causale e riferimenti, con i crediti
del sostituto compensati. Il codice è una mappatura datata dell'istituto (ADR 0022); un importo senza
mappatura ferma l'invio, non il calcolo. Questo modulo non decide nulla che l'ADR non dica: dove manca
una regola, la delega si ferma nominando il caso.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .corpus import Corpus
from .errori import ParametroMancante
from .tempo import Mese

AVVISO_SCADENZA_PER_PRASSI = "scadenza_per_prassi"
AVVISO_PROROGA_SU_FESTIVO = "proroga_su_festivo"


@dataclass(frozen=True)
class AvvisoDelega:
    """Segnalazione che non ferma la delega."""

    tipo: str
    messaggio: str


@dataclass(frozen=True)
class Scadenza:
    """Scadenza ricavata dalla regola: `nominale` è il giorno della regola, `data` quella dopo proroga e slittamenti."""

    data: date
    nominale: date
    riferimento: str
    proroga_applicata: bool = False
    fonte_proroga: str | None = None
    riferimento_proroga: str | None = None
    avvisi: tuple[AvvisoDelega, ...] = ()


def _e_lavorativo(corpus: Corpus, giorno: date) -> bool:
    """Non è sabato, domenica né festivo del calendario dichiarato per quell'anno."""
    calendario = corpus.calendario_festivi(giorno.year)
    if calendario is None:
        raise ParametroMancante(f"Calendario dei festivi {giorno.year}: non dichiarato, la scadenza non si calcola")
    return giorno.weekday() < 5 and giorno not in calendario.giorni


def primo_giorno_lavorativo_dal(corpus: Corpus, giorno: date) -> date:
    """Il giorno stesso se è lavorativo, altrimenti il primo lavorativo dopo."""
    while not _e_lavorativo(corpus, giorno):
        giorno += timedelta(days=1)
    return giorno


def calcola_scadenza(corpus: Corpus, mese_pagamento: Mese) -> Scadenza:
    """Il giorno della regola del mese successivo al pagamento; con proroga e slittamento sul primo giorno lavorativo.

    La regola è quella vigente il primo del mese di scadenza. Le scadenze tra il 1° e il 20 agosto
    slittano al 20 per proroga, che il corpus marca come norma o come prassi.
    """
    anno, mese = (mese_pagamento.anno + 1, 1) if mese_pagamento.mese == 12 else (mese_pagamento.anno, mese_pagamento.mese + 1)
    regola = corpus.regola_scadenza_f24ep(date(anno, mese, 1))
    if regola is None:
        raise ParametroMancante(f"Scadenza F24EP: nessuna regola vigente per le scadenze di {anno:04d}-{mese:02d}")
    nominale = date(anno, mese, regola.giorno)
    giorno = nominale
    proroga = regola.proroga
    applicata = proroga is not None and mese == proroga.mese and proroga.dal_giorno <= nominale.day <= proroga.al_giorno
    avvisi = []
    if applicata:
        giorno = date(anno, mese, proroga.al_giorno)
        if proroga.fonte == "prassi":
            avvisi.append(
                AvvisoDelega(
                    AVVISO_SCADENZA_PER_PRASSI,
                    f"La scadenza del {nominale} slitta al {giorno} per una proroga che regge su una prassi "
                    f"({proroga.riferimento}), non su un testo di legge",
                )
            )
    definitiva = primo_giorno_lavorativo_dal(corpus, giorno)
    if applicata and definitiva != giorno:
        avvisi.append(
            AvvisoDelega(
                AVVISO_PROROGA_SU_FESTIVO,
                f"Il {giorno.day} agosto {giorno.year} cade di sabato, domenica o festivo: la fonte non dice cosa "
                f"accade alla proroga in questo caso, applicato lo slittamento al {definitiva}",
            )
        )
    return Scadenza(
        data=definitiva,
        nominale=nominale,
        riferimento=regola.riferimento,
        proroga_applicata=applicata,
        fonte_proroga=proroga.fonte if applicata else None,
        riferimento_proroga=proroga.riferimento if applicata else None,
        avvisi=tuple(avvisi),
    )
