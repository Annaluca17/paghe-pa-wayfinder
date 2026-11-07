"""Esito 730-4 minimo e il rimborso che ne nasce (ticket #71, ADR 0023).

L'esito e' un fatto della persona (`Registro.registra_esito_730_4`): provenienza, rimborso e anno dei redditi
dichiarati. Qui si legge il fatto vigente e lo si rende importo del rapporto della persona, con l'anno dei redditi
dichiarati nell'anno d'imposta, che e' quello che la delega F24EP legge (150E, riferimento B). Rate, acconti e debiti
del 730-4 non sono modellati.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .corpus import Corpus
from .errori import ParametroMancante
from .modello import Derivazione, Fatto, Importo, ParametroLetto
from .registro import TIPO_ESITO_730_4, Registro
from .tempo import Mese, Periodo, in_utc

ISTITUTO_RIMBORSO_730 = "rimborso_730_4"
# Il primo mese utile per operare il rimborso e' un parametro del corpus: nessuna norma e' scritta nel codice.
PARAMETRO_PRIMO_MESE = "rimborso_730_primo_mese"


@dataclass(frozen=True)
class Esito730:
    """L'esito 730-4 vigente di una persona: il fatto, il rimborso e l'anno dei redditi dichiarati."""

    fatto: Fatto
    rimborso: Decimal
    anno_redditi: int


def esito_730_4(registro: Registro, persona: str, giorno: date, noto_al: datetime) -> Esito730 | None:
    """L'ultimo esito 730-4 registrato della persona che copre il giorno; None se non ce n'e'."""
    fatto = registro.vigente_persona(persona, TIPO_ESITO_730_4, giorno, noto_al)
    if fatto is None:
        return None
    dati = json.loads(fatto.valore)
    return Esito730(fatto, Decimal(dati["rimborso"]), dati["anno_redditi"])


def rimborso_730_4(
    registro: Registro, corpus: Corpus, rapporto: str, valuta: date, noto_al: datetime | None = None
) -> Importo | None:
    """Il rimborso del 730-4 della persona come importo del `rapporto`, da pagare alla `valuta`; None se non c'e'.

    L'importo porta l'anno dei redditi dichiarati nell'anno d'imposta e, come competenza, quell'anno intero: cosi'
    la sua chiave (rapporto, istituto, periodo) e' la stessa per un 730-4 rettificativo e lo stesso rimborso non si
    paga due volte. Non c'e' rimborso prima del primo mese utile dell'anno dopo i redditi, che il corpus dichiara.
    Senza quel parametro il rimborso non si calcola.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    persona = registro.persona_del_rapporto(rapporto, istante)
    if persona is None:
        return None
    esito = esito_730_4(registro, persona, valuta, istante)
    if esito is None:
        return None
    try:
        vigenza = corpus.parametro(PARAMETRO_PRIMO_MESE).vigenza_per(Mese(valuta.year, valuta.month))
    except KeyError:
        raise ParametroMancante(
            f"Rapporto {rapporto}, istituto {ISTITUTO_RIMBORSO_730}: il corpus non dichiara il parametro "
            f"{PARAMETRO_PRIMO_MESE}, il primo mese utile per il rimborso del 730-4"
        ) from None
    if valuta < date(esito.anno_redditi + 1, int(vigenza.valore), 1):
        return None
    letto = ParametroLetto(PARAMETRO_PRIMO_MESE, vigenza.valore, vigenza.dal, vigenza.riferimento)
    derivazione = Derivazione(
        istituto=ISTITUTO_RIMBORSO_730,
        maturazione="periodo",
        regola_versione=1,
        riferimento=esito.fatto.atto.riferimento,
        formula="esito_730_4",
        versione_corpus=corpus.versione,
        noto_al=istante,
        parametri=(letto,),
        fatti=(esito.fatto,),
        importi=(),
    )
    periodo = Periodo(date(esito.anno_redditi, 1, 1), date(esito.anno_redditi, 12, 31))
    return Importo(
        rapporto, ISTITUTO_RIMBORSO_730, periodo, esito.rimborso, derivazione, anno_imposta=esito.anno_redditi
    )
