"""Prospetto paga di un rapporto in un pagamento eseguito (ADR 0030, ticket #86).

Vista dell'esito pagato: non calcola, non arrotonda, non formatta. Le righe sono quelle del rapporto nell'esito; la dichiarazione
di composizione del corpus alla data di pagamento dice quali hanno effetto sul netto, come per la proposta.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .corpus import Corpus, DichiarazioneOutput
from .denuncia import _assegnata
from .modello import Fatto, TipoEsito
from .proposta import _righe_di_composizione
from .registro import Registro
from .tempo import Periodo, in_utc

VISTA = "prospetto_paga"
ENTE = ("codice_fiscale", "denominazione")
PERSONA = ("codice_fiscale", "cognome", "nome")


@dataclass(frozen=True)
class RigaProspetto:
    istituto: str
    periodo: Periodo
    valore: Decimal


@dataclass(frozen=True)
class ProspettoPaga:
    rapporto: str
    esito_id: int
    righe_sul_netto: tuple[RigaProspetto, ...]
    senza_effetto: tuple[RigaProspetto, ...]
    data_pagamento: date
    ente_codice_fiscale: str | None = None
    ente_denominazione: str | None = None
    codice_fiscale: str | None = None
    cognome: str | None = None
    nome: str | None = None
    posizione: str | None = None
    fine_servizio: str | None = None

    @property
    def netto(self) -> Decimal:
        return sum((riga.valore for riga in self.righe_sul_netto), Decimal(0))


def _vigente(fatti: list[Fatto], giorno: date) -> str | None:
    fatto = next((f for f in reversed(fatti) if f.copre(giorno)), None)
    return str(fatto.valore) if fatto is not None else None


def _regime(corpus: Corpus, importi, giorno: date) -> DichiarazioneOutput:
    return next(
        d for d in corpus.outputs(VISTA, giorno) if any(_assegnata(corpus, d, riga, giorno) for riga in importi)
    )


def prospetto_paga(
    registro: Registro, corpus: Corpus, rapporto: str, esito_id: int, noto_al: datetime | None = None
) -> ProspettoPaga:
    """Prospetto del rapporto nel pagamento eseguito indicato; funzione pura di registro, corpus e istante."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    esito = registro.esito(esito_id)
    data = registro.pagamenti(rapporto, istante)[esito_id].valido_dal
    importi = [riga for riga in esito.righe if riga.rapporto == rapporto]
    composte = _righe_di_composizione(corpus, importi, data)
    sul_netto = tuple(
        RigaProspetto(riga.istituto, riga.importo.periodo, riga.sul_netto) for riga in composte if riga.effetto != "nessuno"
    )
    senza_effetto = tuple(
        RigaProspetto(riga.istituto, riga.importo.periodo, riga.importo.valore) for riga in composte if riga.effetto == "nessuno"
    )
    regime = _regime(corpus, importi, data)
    persona = registro.persona_del_rapporto(rapporto, istante)
    anagrafica = {
        tipo: _vigente(registro.fatti_persona_noti(persona, tipo, istante), data) if persona else None for tipo in PERSONA
    }
    ente = {tipo: _vigente(registro.fatti_ente_noti(tipo, istante), data) for tipo in ENTE}
    return ProspettoPaga(
        rapporto,
        esito_id,
        sul_netto,
        senza_effetto,
        data,
        ente["codice_fiscale"],
        ente["denominazione"],
        anagrafica["codice_fiscale"],
        anagrafica["cognome"],
        anagrafica["nome"],
        _vigente(registro.fatti_noti(rapporto, regime.posizione, istante), data) if regime.posizione else None,
        _vigente(registro.fatti_noti(rapporto, regime.fine_servizio, istante), data) if regime.fine_servizio else None,
    )
