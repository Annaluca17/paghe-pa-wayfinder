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
from .errori import ComposizioneMancante, VistaFerma
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
    fermi: tuple[str, ...] = ()
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

    @property
    def consegnabile(self) -> bool:
        return not self.fermi


def _vigente(fatti: list[Fatto], giorno: date) -> str | None:
    fatto = next((f for f in reversed(fatti) if f.copre(giorno)), None)
    return str(fatto.valore) if fatto is not None else None


def _regime(corpus: Corpus, rapporto: str, importi, giorno: date) -> DichiarazioneOutput:
    """La dichiarazione che assegna il rapporto al prospetto: una sola, altrimenti la vista si ferma."""
    trovate = [d for d in corpus.outputs(VISTA, giorno) if any(_assegnata(corpus, d, riga, giorno) for riga in importi)]
    if not trovate:
        raise VistaFerma(f"Rapporto {rapporto}: il corpus non dichiara che il prospetto paga spetti al regime, al {giorno}")
    if len(trovate) > 1:
        raise VistaFerma(f"Rapporto {rapporto}: più regimi assegnano il prospetto paga ({', '.join(d.regime for d in trovate)})")
    return trovate[0]


def prospetto_paga(
    registro: Registro, corpus: Corpus, rapporto: str, esito_id: int, noto_al: datetime | None = None
) -> ProspettoPaga:
    """Prospetto del rapporto nel pagamento eseguito indicato; funzione pura di registro, corpus e istante."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    esito = registro.esito(esito_id)
    pagamento = registro.pagamenti(rapporto, istante).get(esito_id)
    importi = [riga for riga in esito.righe if riga.rapporto == rapporto]
    if esito.tipo != TipoEsito.PAGATO or pagamento is None or not importi:
        raise VistaFerma(f"Rapporto {rapporto}: nessuna riga pagata nell'esito {esito_id}, nessun prospetto")
    data = pagamento.valido_dal
    composte, fermi = [], []
    for importo in importi:
        try:
            composte.extend(_righe_di_composizione(corpus, [importo], data))
        except ComposizioneMancante as errore:
            fermi.append(str(errore))
    sul_netto = tuple(
        RigaProspetto(riga.istituto, riga.importo.periodo, riga.sul_netto) for riga in composte if riga.effetto != "nessuno"
    )
    senza_effetto = tuple(
        RigaProspetto(riga.istituto, riga.importo.periodo, riga.importo.valore) for riga in composte if riga.effetto == "nessuno"
    )
    regime = _regime(corpus, rapporto, importi, data)
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
        tuple(fermi),
        ente["codice_fiscale"],
        ente["denominazione"],
        anagrafica["codice_fiscale"],
        anagrafica["cognome"],
        anagrafica["nome"],
        _vigente(registro.fatti_noti(rapporto, regime.posizione, istante), data) if regime.posizione else None,
        _vigente(registro.fatti_noti(rapporto, regime.fine_servizio, istante), data) if regime.fine_servizio else None,
    )
