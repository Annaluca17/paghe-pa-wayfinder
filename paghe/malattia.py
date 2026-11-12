"""Malattia del comparto (ADR 0042, ticket #130): episodi, decurtazione dei primi giorni, comporto e percentuale.

L'ufficio registra la malattia come fatto categoriale per periodo, con il tipo: `ordinaria`, `ricovero` (compresi day
hospital e convalescenza), `salvavita`, `infortunio`. Da lì il modulo ricava, per ogni giorno, lo stato:

- **Episodio.** Giorni consecutivi di malattia `ordinaria` o `ricovero`; i certificati continui sono un solo episodio.
  Fra due certificati i giorni non lavorati (sabato, domenica, festivi del corpus) restano nello stesso episodio; un
  giorno lavorato in mezzo ne apre uno nuovo.
- **Decurtazione.** Solo i giorni `ordinaria` dei primi `giorni_decurtati` di calendario dell'episodio (art. 71 DL 112/2008).
- **Comporto.** Giorni di malattia (`ordinaria` e `ricovero`) nei tre anni fino a quel giorno compreso, ricalcolati a
  ogni giorno; la percentuale (100, 90, 50, 0) segue le fasce del corpus. Salvavita e infortunio hanno comporto a parte
  e non contano.

Il modulo non sa nulla degli importi: li riduce il motore, secondo la dichiarazione di ciascun istituto.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from .corpus import Corpus
from .errori import CasoNonModellato, ErroreRegistro
from .modello import Atto
from .registro import Registro
from .tempo import Periodo

TIPO_MALATTIA = "malattia"
ORDINARIA = "ordinaria"
RICOVERO = "ricovero"
SALVAVITA = "salvavita"
INFORTUNIO = "infortunio"
TIPI_MALATTIA = frozenset({ORDINARIA, RICOVERO, SALVAVITA, INFORTUNIO})
_NEL_COMPORTO = frozenset({ORDINARIA, RICOVERO})


@dataclass(frozen=True)
class StatoMalattia:
    """Lo stato di un giorno di malattia."""

    tipo: str
    decurtazione: bool
    percentuale: Decimal
    giorno_episodio: int
    giorni_comporto: int

    @property
    def firma(self) -> tuple:
        """Ciò che, se cambia da un giorno all'altro, divide il mese in frazioni."""
        return (self.tipo, self.decurtazione, self.percentuale)


def registra_malattia(
    registro: Registro, rapporto: str, tipo: str, dal: date, al: date, atto: Atto | None = None
) -> None:
    """Registra un periodo di malattia (un certificato). Un periodo già registrato si sostituisce con un fatto nuovo."""
    if tipo not in TIPI_MALATTIA:
        raise ErroreRegistro(f"Tipo di malattia {tipo!r} ignoto; ammessi {sorted(TIPI_MALATTIA)}")
    registro.registra_codice(rapporto, TIPO_MALATTIA, tipo, dal, al, atto)


def _non_lavorato(corpus: Corpus, giorno: date) -> bool:
    if giorno.weekday() >= 5:
        return True
    calendario = corpus.calendario_festivi(giorno.year)
    return calendario is not None and giorno in calendario.giorni


def stati_del_periodo(
    registro: Registro, corpus: Corpus, rapporto: str, periodo: Periodo, noto_al: datetime | None = None
) -> dict[date, StatoMalattia]:
    """Stato dei giorni di malattia del periodo; i giorni senza malattia non compaiono.

    Senza regole della malattia nel corpus l'esito è vuoto. La finestra dei tre anni parte dal primo giorno del periodo.
    """
    regole = corpus.regola_malattia(periodo.al)
    if regole is None:
        return {}
    istante = noto_al if noto_al is not None else registro.adesso()
    inizio = _anni_prima(periodo.dal, regole.anni_finestra)
    esteso = Periodo(inizio, periodo.al)
    giorni = esteso.giorni()
    fatti = registro.vigenti_per_giorno(rapporto, TIPO_MALATTIA, esteso, istante)
    tipo_del_giorno: dict[date, str] = {}
    for giorno, fatto in zip(giorni, fatti):
        if fatto is None:
            continue
        tipo = str(fatto.valore)
        if tipo not in TIPI_MALATTIA:
            raise CasoNonModellato(f"Rapporto {rapporto}: tipo di malattia {tipo!r} ignoto (fatto #{fatto.id})")
        tipo_del_giorno[giorno] = tipo

    # Giorni dell'episodio: i giorni di malattia del comporto, più i giorni non lavorati fra due di essi.
    nel_comporto = {g for g, t in tipo_del_giorno.items() if t in _NEL_COMPORTO}
    tipo_effettivo = dict(tipo_del_giorno)
    precedente: date | None = None
    for giorno in sorted(nel_comporto):
        if precedente is not None and (giorno - precedente).days > 1:
            in_mezzo = [precedente + timedelta(days=n) for n in range(1, (giorno - precedente).days)]
            if all(_non_lavorato(corpus, g) and g not in tipo_del_giorno for g in in_mezzo):
                for g in in_mezzo:
                    tipo_effettivo[g] = tipo_del_giorno[precedente]
        precedente = giorno
    computati = sorted(g for g, t in tipo_effettivo.items() if t in _NEL_COMPORTO)

    stati: dict[date, StatoMalattia] = {}
    inizio_episodio: date | None = None
    precedente = None
    nella_finestra: list[date] = []
    for giorno in computati:
        if precedente is None or (giorno - precedente).days > 1:
            inizio_episodio = giorno
        precedente = giorno
        nella_finestra.append(giorno)
        limite = _anni_prima(giorno, regole.anni_finestra)
        while nella_finestra[0] <= limite:
            nella_finestra.pop(0)
        if giorno < periodo.dal:
            continue
        numero = (giorno - inizio_episodio).days + 1
        tipo = tipo_effettivo[giorno]
        stati[giorno] = StatoMalattia(
            tipo=tipo,
            decurtazione=tipo == ORDINARIA and numero <= regole.giorni_decurtati,
            percentuale=regole.percentuale(len(nella_finestra)),
            giorno_episodio=numero,
            giorni_comporto=len(nella_finestra),
        )
    for giorno, tipo in tipo_del_giorno.items():
        if tipo not in _NEL_COMPORTO and periodo.dal <= giorno <= periodo.al:
            stati[giorno] = StatoMalattia(tipo, False, Decimal(100), 0, 0)
    return dict(sorted(stati.items()))


def _anni_prima(giorno: date, anni: int) -> date:
    try:
        return giorno.replace(year=giorno.year - anni)
    except ValueError:  # 29 febbraio
        return giorno.replace(year=giorno.year - anni, day=28)
