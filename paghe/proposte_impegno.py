"""Proposte di impegno e di accertamento da un atto registrato (ADR 0031).

Quando nel registro entra un atto, con importo ed esercizio, di un tipo che l'origine di un istituto dichiara,
il modello emette una proposta immutabile: classificazione (V livello dal corpus, missione e programma dal
chiamante), esercizio, atto e importo. La proposta di impegno ha verso `spesa`, quella di accertamento `entrata`.
Sono eventi con identificativo stabile, come gli altri del registro: lo stato (inviata, confermata, respinta con
motivo) è un evento successivo, e l'ultimo vale.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .corpus import Corpus
from .errori import ClassificazioneMancante, ErroreRegistro
from .impegni import AUTOMATICO, AttoPresupposto
from .registro import Registro, _in_decimale
from .tempo import in_utc

VERSO_SPESA = "spesa"
VERSO_ENTRATA = "entrata"
TIPO_PROPOSTA = "proposta_impegno"
TIPO_STATO_PROPOSTA = "stato_proposta_impegno"
INVIATA = "inviata"
CONFERMATA = "confermata"
RESPINTA = "respinta"
_PREFISSO_DEL_VERSO = {VERSO_SPESA: "U.", VERSO_ENTRATA: "E."}


@dataclass(frozen=True)
class PropostaImpegno:
    chiave: str
    verso: str
    istituto: str
    piano_dei_conti: str
    missione: str
    programma: str
    esercizio: int
    atto: AttoPresupposto
    importo: Decimal
    stato: str = INVIATA
    motivo: str | None = None


def _contenuto(proposta: PropostaImpegno) -> dict:
    return {
        "verso": proposta.verso,
        "istituto": proposta.istituto,
        "piano_dei_conti": proposta.piano_dei_conti,
        "missione": proposta.missione,
        "programma": proposta.programma,
        "esercizio": proposta.esercizio,
        "atto": {"tipo": proposta.atto.tipo, "riferimento": proposta.atto.riferimento},
        "importo": str(proposta.importo),
    }


def _emetti(
    registro: Registro,
    corpus: Corpus,
    verso: str,
    chiave: str,
    adattatore: str,
    istituto: str,
    atto: AttoPresupposto,
    data_atto: date,
    importo: Decimal | int | str,
    esercizio: int,
    missione: str,
    programma: str,
) -> PropostaImpegno:
    classificazione = corpus.classificazione(istituto, data_atto)
    if classificazione is None:
        raise ClassificazioneMancante(
            f"Istituto {istituto}: nessuna dichiarazione di classificazione per un atto del {data_atto}"
        )
    if classificazione.origine_impegno == AUTOMATICO:
        raise ErroreRegistro(f"Istituto {istituto}: l'impegno è automatico, non genera proposte di impegno")
    if classificazione.origine_impegno != atto.tipo:
        raise ErroreRegistro(
            f"Istituto {istituto}: l'origine dell'impegno dichiara l'atto {classificazione.origine_impegno!r}, "
            f"non {atto.tipo!r}"
        )
    if not classificazione.piano_dei_conti.startswith(_PREFISSO_DEL_VERSO[verso]):
        raise ErroreRegistro(
            f"Istituto {istituto}: il codice {classificazione.piano_dei_conti} non è del verso {verso}"
        )
    valore = _in_decimale(importo)
    if valore <= 0:
        raise ErroreRegistro(f"L'importo della proposta è positivo, {importo!r}")
    if not isinstance(esercizio, int) or isinstance(esercizio, bool):
        raise ErroreRegistro(f"Esercizio non valido: {esercizio!r}")
    for nome, codice in (("missione", missione), ("programma", programma)):
        if not isinstance(codice, str) or not re.fullmatch(r"\d{2}", codice):
            raise ErroreRegistro(f"Proposta: {nome} non valida, {codice!r}; serve un codice di due cifre")
    proposta = PropostaImpegno(
        chiave, verso, istituto, classificazione.piano_dei_conti, missione, programma, esercizio, atto, valore
    )
    contenuto = _contenuto(proposta)
    if registro.evento_identico(chiave, TIPO_PROPOSTA, contenuto) is None:
        registro.registra_evento(chiave, TIPO_PROPOSTA, contenuto, adattatore)
    return proposta


def emetti_proposta_impegno(
    registro: Registro, corpus: Corpus, chiave: str, adattatore: str, istituto: str, atto: AttoPresupposto,
    data_atto: date, importo: Decimal | int | str, esercizio: int, missione: str, programma: str,
) -> PropostaImpegno:
    """Proposta di impegno di spesa per un atto del tipo che l'origine dell'istituto dichiara (altrimenti errore)."""
    return _emetti(
        registro, corpus, VERSO_SPESA, chiave, adattatore, istituto, atto, data_atto, importo, esercizio, missione, programma
    )


def emetti_proposta_accertamento(
    registro: Registro, corpus: Corpus, chiave: str, adattatore: str, istituto: str, atto: AttoPresupposto,
    data_atto: date, importo: Decimal | int | str, esercizio: int, missione: str, programma: str,
) -> PropostaImpegno:
    """Proposta di accertamento di entrata: stessa forma, verso entrata."""
    return _emetti(
        registro, corpus, VERSO_ENTRATA, chiave, adattatore, istituto, atto, data_atto, importo, esercizio, missione, programma
    )


def leggi_proposta(registro: Registro, chiave: str, noto_al: datetime | None = None) -> PropostaImpegno:
    """La proposta con il suo stato all'istante: l'ultimo evento di stato vale."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    evento = registro.evento(chiave)
    if evento is None or evento.tipo != TIPO_PROPOSTA or evento.registrato_il > istante:
        raise ErroreRegistro(f"Proposta {chiave} inesistente o non ancora nota al {istante}")
    c = evento.contenuto
    stato, motivo = INVIATA, None
    for decisione in _decisioni(registro, chiave, istante):
        stato, motivo = decisione.contenuto["stato"], decisione.contenuto["motivo"]
    return PropostaImpegno(
        chiave, c["verso"], c["istituto"], c["piano_dei_conti"], c["missione"], c["programma"], c["esercizio"],
        AttoPresupposto(c["atto"]["tipo"], c["atto"]["riferimento"]), Decimal(c["importo"]), stato, motivo,
    )


def _decisioni(registro: Registro, chiave: str, istante: datetime) -> list:
    return [e for e in registro.eventi(TIPO_STATO_PROPOSTA, istante) if e.contenuto["proposta"] == chiave]


def _decidi(registro: Registro, chiave: str, stato: str, motivo: str | None) -> None:
    proposta = leggi_proposta(registro, chiave)
    if proposta.stato != INVIATA:
        raise ErroreRegistro(f"Proposta {chiave}: non si decide una proposta {proposta.stato}, solo una inviata")
    numero = len(_decisioni(registro, chiave, registro.adesso())) + 1
    registro.registra_evento(
        f"{chiave}:stato:{numero}", TIPO_STATO_PROPOSTA, {"proposta": chiave, "stato": stato, "motivo": motivo}, "ragioneria"
    )


def conferma_proposta(registro: Registro, chiave: str) -> None:
    """La Ragioneria conferma la proposta."""
    _decidi(registro, chiave, CONFERMATA, None)


def respingi_proposta(registro: Registro, chiave: str, motivo: str) -> None:
    """La Ragioneria respinge la proposta, con un motivo obbligatorio."""
    if not motivo or not motivo.strip():
        raise ErroreRegistro("Il motivo del rifiuto è obbligatorio")
    _decidi(registro, chiave, RESPINTA, motivo)
