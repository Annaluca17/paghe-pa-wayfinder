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
from .errori import ComposizioneMancante, ErroreRegistro, VistaFerma
from .modello import Esito, Evento, Fatto, Importo, TipoEsito
from .proposta import _righe_di_composizione
from .registro import Registro
from .tempo import Periodo, in_utc

VISTA = "prospetto_paga"
TIPO_MESSA_A_DISPOSIZIONE = "messa_a_disposizione"
ENTE = ("codice_fiscale", "denominazione")
PERSONA = ("codice_fiscale", "cognome", "nome")


@dataclass(frozen=True)
class RigaProspetto:
    istituto: str
    periodo: Periodo
    valore: Decimal
    importo: Importo


@dataclass(frozen=True)
class ProspettoPaga:
    rapporto: str
    esito_id: int
    righe_sul_netto: tuple[RigaProspetto, ...]
    senza_effetto: tuple[RigaProspetto, ...]
    data_pagamento: date
    fermi: tuple[str, ...] = ()
    mancanti: tuple[str, ...] = ()
    avvisi: tuple[str, ...] = ()
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
        return not (self.fermi or self.mancanti)


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
        RigaProspetto(riga.istituto, riga.importo.periodo, riga.sul_netto, riga.importo) for riga in composte if riga.effetto != "nessuno"
    )
    senza_effetto = tuple(
        RigaProspetto(riga.istituto, riga.importo.periodo, riga.importo.valore, riga.importo) for riga in composte if riga.effetto == "nessuno"
    )
    regime = _regime(corpus, rapporto, importi, data)
    persona = registro.persona_del_rapporto(rapporto, istante)
    anagrafica = {
        tipo: _vigente(registro.fatti_persona_noti(persona, tipo, istante), data) if persona else None for tipo in PERSONA
    }
    ente = {tipo: _vigente(registro.fatti_ente_noti(tipo, istante), data) for tipo in ENTE}
    posizione = _vigente(registro.fatti_noti(rapporto, regime.posizione, istante), data) if regime.posizione else None
    fine_servizio = (
        _vigente(registro.fatti_noti(rapporto, regime.fine_servizio, istante), data) if regime.fine_servizio else None
    )
    # Il contenuto dell'art. 1 L. 4/1953 ferma il prospetto: nome, cognome, codice fiscale, posizione, voci.
    mancanti = tuple(
        dato
        for dato, presente in (
            ("codice_fiscale", anagrafica["codice_fiscale"]),
            ("cognome", anagrafica["cognome"]),
            ("nome", anagrafica["nome"]),
            ("posizione", posizione),
            ("voci", sul_netto),
        )
        if not presente
    )
    # Gli altri dati assenti non fermano: il contratto collettivo resta un avviso finche' il corpus non lo dichiara.
    avvisi = ("contratto_collettivo",) + tuple(
        dato
        for dato, assente in (
            ("ente_codice_fiscale", ente["codice_fiscale"] is None),
            ("ente_denominazione", ente["denominazione"] is None),
            ("fine_servizio", regime.fine_servizio is not None and fine_servizio is None),
        )
        if assente
    )
    return ProspettoPaga(
        rapporto,
        esito_id,
        sul_netto,
        senza_effetto,
        data,
        tuple(fermi),
        mancanti,
        avvisi,
        ente["codice_fiscale"],
        ente["denominazione"],
        anagrafica["codice_fiscale"],
        anagrafica["cognome"],
        anagrafica["nome"],
        posizione,
        fine_servizio,
    )


# Consegna: l'adattatore del canale riporta la messa a disposizione, da cui nasce l'esito dichiarato.

@dataclass(frozen=True)
class MessaADisposizione:
    esito: Esito
    evento: Evento


def _in_dizionario(prospetto: ProspettoPaga) -> dict:
    """Gli elementi del prospetto come testo: ciò che la messa a disposizione fissa."""

    def righe(elenco):
        return [[r.istituto, str(r.periodo), str(r.valore)] for r in elenco]

    return {
        "ente_codice_fiscale": prospetto.ente_codice_fiscale,
        "ente_denominazione": prospetto.ente_denominazione,
        "codice_fiscale": prospetto.codice_fiscale,
        "cognome": prospetto.cognome,
        "nome": prospetto.nome,
        "posizione": prospetto.posizione,
        "fine_servizio": prospetto.fine_servizio,
        "data_pagamento": prospetto.data_pagamento.isoformat(),
        "righe_sul_netto": righe(prospetto.righe_sul_netto),
        "senza_effetto": righe(prospetto.senza_effetto),
        "netto": str(prospetto.netto),
    }


def registra_messa_a_disposizione(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    esito_id: int,
    chiave: str,
    data: date,
    riferimento: str,
    adattatore: str,
) -> MessaADisposizione:
    """Evento di ritorno del canale di consegna: dal prospetto consegnabile nasce l'esito dichiarato, una sola volta.

    Stessa chiave e stesso contenuto non hanno effetto; contenuto diverso è rifiutato. Un prospetto fermo non si consegna.
    """
    if not isinstance(riferimento, str) or not riferimento.strip():
        raise ErroreRegistro("La messa a disposizione porta il riferimento del canale")
    prospetto = prospetto_paga(registro, corpus, rapporto, esito_id)
    contenuto = {
        "rapporto": rapporto,
        "esito_pagato": esito_id,
        "data": data.isoformat(),
        "riferimento": riferimento,
        "prospetto": _in_dizionario(prospetto),
    }
    gia = registro.evento(chiave)
    if gia is not None:
        if gia.tipo != TIPO_MESSA_A_DISPOSIZIONE or gia.contenuto != contenuto:
            raise ErroreRegistro(f"Evento {chiave}: stesso identificativo con contenuto diverso, rifiutato")
        return MessaADisposizione(registro.esito(gia.esito_id), gia)
    if not prospetto.consegnabile:
        motivi = [*prospetto.fermi, *(f"dato mancante {dato}" for dato in prospetto.mancanti)]
        raise VistaFerma(f"Prospetto del rapporto {rapporto}, esito {esito_id}, non consegnabile: " + "; ".join(motivi))
    righe = [riga.importo for riga in (*prospetto.righe_sul_netto, *prospetto.senza_effetto)]
    with registro.atomico():
        esito = registro.registra_esito(TipoEsito.DICHIARATO, data, righe)
        evento = registro.registra_evento(chiave, TIPO_MESSA_A_DISPOSIZIONE, contenuto, adattatore, esito_id=esito.id)
    return MessaADisposizione(esito, evento)
