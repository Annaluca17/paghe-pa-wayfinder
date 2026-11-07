"""Vista lista collaboratori di un rapporto nel mese (ADR 0015, 0022, ticket #73).

Denuncia di chi e' in gestione separata: i compensi di collaborazione e le quote forfettarie degli amministratori.
Ha struttura e identita' proprie, separata dalla ListaPosPA, e segue il mese di erogazione, cioe' quello del pagamento.
La vista legge la denuncia calcolata (base e contributi della gestione separata) e gli importi pagati della quota
forfettaria, che non sta su una base. Non conosce i titoli: quali rapporti le spettano lo dice il corpus
(`paghe.denuncia.rapporti_della_vista`).

I codici del tracciato non sono stati letti sul testo: la vista resta una bozza non trasmissibile finche' il corpus non
li dichiara, e non ne inventa. La cassa allargata (somme pagate entro il 12 gennaio, attribuite all'anno prima) non ha
una regola di esposizione nel tracciato: resta bozza. La vista non arrotonda ne' formatta.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .denuncia import calcola_denuncia
from .modello import Importo, TipoEsito
from .registro import Registro
from .corpus import Corpus
from .tempo import Mese, Periodo, in_utc

VISTA = "lista_collaboratori"
BASE = "gestione_separata"
TOTALE = "gs_totale"
QUOTA_COLLABORATORE = "gs_lavoratore"
QUOTA_ENTE = "gs_ente"
ANAGRAFICA = ("codice_fiscale", "cognome", "nome")
MOTIVO_TRACCIATO = (
    "tracciato della lista collaboratori: elementi e codici non letti sul testo ufficiale e non dichiarati nel corpus: "
    "bozza non trasmissibile"
)


@dataclass(frozen=True)
class Collaboratore:
    codice_fiscale: str | None
    cognome: str | None
    nome: str | None


@dataclass(frozen=True)
class RigaCollaboratore:
    """Imponibile e contributo di un periodo in gestione separata, o la quota forfettaria (senza imponibile)."""

    periodo: Periodo
    imponibile: Decimal | None
    contributo: Decimal
    quota_collaboratore: Decimal | None
    quota_ente: Decimal
    importi: tuple[Importo, ...]
    forfettaria: bool = False


@dataclass(frozen=True)
class ListaCollaboratori:
    rapporto: str
    mese_erogazione: Mese
    collaboratore: Collaboratore
    righe: tuple[RigaCollaboratore, ...]
    mancanti: tuple[str, ...] = ()
    bozza: tuple[str, ...] = ()

    @property
    def trasmissibile(self) -> bool:
        return not (self.mancanti or self.bozza)


def _collaboratore(registro: Registro, rapporto: str, mese: Mese, istante: datetime) -> tuple[Collaboratore, tuple[str, ...]]:
    persona = registro.persona_del_rapporto(rapporto, istante)
    valori: dict[str, str | None] = {}
    for tipo in ANAGRAFICA:
        noti = registro.fatti_persona_noti(persona, tipo, istante) if persona else []
        noti = [fatto for fatto in noti if fatto.valido_dal <= mese.ultimo_giorno]
        vigente = next((f for f in reversed(noti) if f.copre(mese.ultimo_giorno)), noti[-1] if noti else None)
        valori[tipo] = str(vigente.valore) if vigente is not None else None
    mancanti = tuple(tipo for tipo, valore in valori.items() if valore is None)
    return Collaboratore(**valori), mancanti


def _pagati_del_mese(registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istituti, istante: datetime):
    """(riga, data di pagamento) degli importi pagati nel mese dagli istituti dati."""
    pagamenti = registro.pagamenti(rapporto, istante)
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        fatto = pagamenti.get(esito.id)
        if fatto is None or not mese.primo_giorno <= fatto.valido_dal <= mese.ultimo_giorno:
            continue
        for riga in esito.righe:
            if riga.rapporto == rapporto and riga.istituto in istituti:
                yield riga, fatto.valido_dal


def _cassa_allargata(registro: Registro, rapporto: str, mese: Mese, istante: datetime) -> list[str]:
    """Somme pagate nel mese e attribuite a un altro anno d'imposta: il tracciato non dice come esporle."""
    motivi = []
    pagamenti = registro.pagamenti(rapporto, istante)
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        fatto = pagamenti.get(esito.id)
        if fatto is None or not mese.primo_giorno <= fatto.valido_dal <= mese.ultimo_giorno:
            continue
        for riga in esito.righe:
            if riga.rapporto == rapporto and riga.anno_imposta is not None and riga.anno_imposta != fatto.valido_dal.year:
                motivi.append(
                    f"cassa allargata: {riga.istituto} pagato il {fatto.valido_dal} e attribuito all'anno d'imposta "
                    f"{riga.anno_imposta}, esposizione nella lista non definita: bozza non trasmissibile"
                )
    return sorted(set(motivi))


def lista_collaboratori(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, noto_al: datetime | None = None
) -> ListaCollaboratori:
    """Lista collaboratori del rapporto nel mese di erogazione; funzione pura di registro, corpus e istante."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    dichiarazione = corpus.output(VISTA, mese.ultimo_giorno)
    forfettari = dichiarazione.istituti if dichiarazione is not None else ()
    collaboratore, mancanti = _collaboratore(registro, rapporto, mese, istante)

    righe: list[RigaCollaboratore] = []
    for periodo in calcola_denuncia(registro, corpus, rapporto, mese, istante).periodi:
        base = periodo.base(BASE)
        if base is None:
            continue
        contributi = {riga.istituto: riga for riga in periodo.contributi}
        quote = [contributi.get(nome) for nome in (TOTALE, QUOTA_COLLABORATORE, QUOTA_ENTE)]
        righe.append(
            RigaCollaboratore(
                periodo=periodo.periodo,
                imponibile=base.valore,
                contributo=quote[0].valore if quote[0] else Decimal(0),
                quota_collaboratore=quote[1].valore if quote[1] else Decimal(0),
                quota_ente=quote[2].valore if quote[2] else Decimal(0),
                importi=(base, *(q for q in quote if q is not None)),
            )
        )
    for riga, _ in _pagati_del_mese(registro, corpus, rapporto, mese, forfettari, istante):
        righe.append(
            RigaCollaboratore(
                periodo=riga.periodo,
                imponibile=None,
                contributo=riga.valore,
                quota_collaboratore=None,
                quota_ente=riga.valore,
                importi=(riga,),
                forfettaria=True,
            )
        )
    bozza = [MOTIVO_TRACCIATO, *_cassa_allargata(registro, rapporto, mese, istante)]
    return ListaCollaboratori(rapporto, mese, collaboratore, tuple(righe), mancanti, tuple(bozza))
