"""Delega F24EP: vista del modello dagli esiti pagati alla delega trasmessa e versata (ADR 0023, 0025).

La delega nasce dalla composizione del pagamento: le righe con canale F24EP degli esiti pagati, non
ancora versate, diventano righe per sezione, codice tributo o causale e riferimenti, con i crediti
del sostituto compensati. Il codice è una mappatura datata dell'istituto (ADR 0022); un importo senza
mappatura ferma l'invio, non il calcolo. Questo modulo non decide nulla che l'ADR non dica: dove manca
una regola, la delega si ferma nominando il caso.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from .corpus import Corpus
from .errori import ErroreRegistro, ParametroMancante, VistaFerma
from .f24ep import problemi_dati_ente
from .f24ep import FornituraF24EP, ModelloF24EP, ModuloF24EP, RigaF24EP, serializza
from .modello import Esito, Evento, Importo, TipoEsito
from .proposta import (
    NATURE_A_CREDITO,
    TIPO_PAGAMENTO_ESEGUITO,
    TIPO_VERSAMENTO_ESEGUITO,
    DatoMancante,
    RiferimentoRiga,
    StatoDelega,
    _evento_gia_noto,
    leggi_versione,
    registra_versamento_eseguito,
    stato_delega,
)
from .registro import TIPO_CREDITO_RIPORTATO, TIPO_REGIONE_ENTE, Fatto, Registro
from .tempo import Mese, in_utc

# Sistema della mappatura esterna dell'istituto: codice tributo o causale F24EP (ADR 0022).
SISTEMA_F24EP = "codice_tributo_f24ep"
TIPO_DELEGA_TRASMESSA = "delega_trasmessa"
TIPO_DELEGA_ANNULLATA = "delega_annullata"

# Mappatura datata della regione al codice del campo «codice» del 380E (ticket #81, ADR 0028): valore = nome della
# regione, quello del fatto di sede di lavoro e quello della regione dell'ente.
SISTEMA_REGIONE_F24EP = "f24ep.codice_regione"
ELEMENTO_REGIONE_F24EP = "codice_regione"
TIPO_SEDE_DI_LAVORO = "sede_lavoro"

AVVISO_CAMBIO_SEDE_RECENTE = "cambio_sede_recente"
AVVISO_SCADENZA_PER_PRASSI = "scadenza_per_prassi"
AVVISO_PROROGA_SU_FESTIVO = "proroga_su_festivo"
AVVISO_VERSAMENTO_TARDIVO = "versamento_dopo_la_scadenza"
AVVISO_TRASMISSIONE_TARDIVA = "trasmissione_oltre_il_termine"


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


# Vista della delega

ORDINE_SEZIONI = "FIRSNQWGP5"  # l'ordine delle sezioni nella delega
RIGHE_PER_MODULO = 22
# Scelta del modello (Luca, 07/11/2026): i crediti si compensano prima contro le ritenute, poi contro gli altri debiti.
CODICE_PRIMA_COMPENSAZIONE = "100E"
TIPI_DATI_ENTE = ("codice_fiscale", "denominazione", "email", "iban_tesoreria")


@dataclass(frozen=True)
class Origine:
    """Da dove viene una parte di una riga: una riga di composizione (`riferimento`) o un credito riportato (`riporto`)."""

    valore: Decimal
    riferimento: RiferimentoRiga | None = None
    riporto: int | None = None


@dataclass(frozen=True)
class RigaDelega:
    sezione: str
    tributo: str
    codice: str
    estremi: str
    rif_a: str
    rif_b: str
    debito: Decimal
    credito: Decimal
    origine: tuple[Origine, ...]

    @property
    def chiave(self) -> tuple[str, str, str, str, str, str]:
        return (self.sezione, self.tributo, self.codice, self.estremi, self.rif_a, self.rif_b)


@dataclass(frozen=True)
class Compensazione:
    """Quanto di un credito (riga a credito) è assorbito da un debito, entrambi indicati dalla chiave della riga."""

    credito: tuple[str, str, str, str, str, str]
    debito: tuple[str, str, str, str, str, str]
    importo: Decimal


@dataclass(frozen=True)
class CreditoResiduo:
    """Credito non assorbito dai debiti della delega: resta visibile, con le righe da cui viene."""

    chiave: tuple[str, str, str, str, str, str]
    importo: Decimal
    origine: tuple[Origine, ...]


@dataclass(frozen=True)
class DatiEnte:
    """I fatti sull'ente che la delega legge; None dove il fatto manca."""

    codice_fiscale: str | None = None
    denominazione: str | None = None
    email: str | None = None
    iban_tesoreria: str | None = None
    sigla_provincia: str | None = None


@dataclass(frozen=True)
class FermoDelega:
    """Un caso che ferma l'invio della delega, non il calcolo: il motivo lo nomina."""

    caso: str
    motivo: str


@dataclass(frozen=True)
class Delega:
    mese_pagamento: Mese
    scadenza: Scadenza | None
    data_versamento: date | None
    righe: tuple[RigaDelega, ...]
    sorgenti: tuple[RiferimentoRiga, ...]
    ente: DatiEnte
    dati_mancanti: tuple[DatoMancante, ...]
    fermi: tuple[FermoDelega, ...]
    avvisi: tuple[AvvisoDelega, ...]
    compensazioni: tuple[Compensazione, ...] = ()
    residui: tuple[CreditoResiduo, ...] = ()
    altre_deleghe: tuple[str, ...] = ()
    riporti_usati: tuple[int, ...] = ()

    @property
    def totale_debito(self) -> Decimal:
        return sum((r.debito for r in self.righe), Decimal(0))

    @property
    def totale_credito(self) -> Decimal:
        return sum((r.credito for r in self.righe), Decimal(0))

    @property
    def saldo(self) -> Decimal:
        return self.totale_debito - self.totale_credito

    @property
    def pronta(self) -> bool:
        """Si può trasmettere: ha righe, nessun fermo e nessun dato mancante."""
        return bool(self.righe) and not self.fermi and not self.dati_mancanti


def _formato(formato: str, importo: Importo, pagamento: date) -> str:
    if formato == "nessuno":
        return ""
    if formato == "mese_pagamento":
        return f"00{pagamento.month:02d}"
    if formato == "anno_pagamento":
        return f"{pagamento.year:04d}"
    if formato == "anno_imposta":
        return f"{importo.anno_imposta:04d}"
    if formato == "periodo_inizio":
        return f"{importo.periodo.dal.month:02d}{importo.periodo.dal.year:04d}"
    return f"{importo.periodo.al.month:02d}{importo.periodo.al.year:04d}"  # periodo_fine


def _riferimento_da_dizionario(dati: dict) -> RiferimentoRiga:
    return RiferimentoRiga(
        dati["versione"], dati["rapporto"], dati["istituto"], dati["periodo"], tuple(dati["esiti_confrontati"])
    )


def _righe_versate(registro: Registro, istante: datetime) -> set[RiferimentoRiga]:
    return {
        _riferimento_da_dizionario(riga)
        for evento in registro.eventi(TIPO_VERSAMENTO_ESEGUITO, istante)
        for riga in evento.contenuto["righe"]
    }


def _chiave_delega(delega_id: str) -> str:
    return f"delega:{delega_id}"


def delega_attiva(registro: Registro, delega_id: str, noto_al: datetime | None = None) -> bool:
    """La delega è stata trasmessa e non è né scartata da una ricevuta né annullata."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    if registro.evento(_chiave_delega(delega_id)) is None:
        return False
    annullate = {e.contenuto["delega"] for e in registro.eventi(TIPO_DELEGA_ANNULLATA, istante)}
    return delega_id not in annullate and stato_delega(registro, delega_id, istante) is not StatoDelega.SCARTATA


def _righe_in_deleghe_attive(registro: Registro, istante: datetime, ignorando: str | None) -> dict[RiferimentoRiga, str]:
    """Le righe di composizione tenute da una delega attiva, con l'identificativo della delega."""
    tenute: dict[RiferimentoRiga, str] = {}
    for evento in registro.eventi(TIPO_DELEGA_TRASMESSA, istante):
        delega_id = evento.contenuto["id"]
        if delega_id == ignorando or not delega_attiva(registro, delega_id, istante):
            continue
        for riga in evento.contenuto["sorgenti"]:
            tenute[_riferimento_da_dizionario(riga)] = delega_id
    return tenute


@dataclass(frozen=True)
class CreditoRiportato:
    """Credito non assorbito da una delega, passato alla scadenza successiva come fatto sull'ente con la sua origine."""

    fatto_id: int
    chiave: tuple[str, str, str, str, str, str]
    importo: Decimal
    delega: str
    scadenza: date
    origine: tuple[Origine, ...]
    valido_dal: date


def _riporto_dal_fatto(fatto: Fatto) -> CreditoRiportato:
    dati = json.loads(fatto.valore)
    return CreditoRiportato(
        fatto.id,
        tuple(dati["chiave"]),
        Decimal(dati["importo"]),
        dati["delega"],
        date.fromisoformat(dati["scadenza"]),
        tuple(_origine_da_dizionario(o) for o in dati["origine"]),
        fatto.valido_dal,
    )


def crediti_riportati(registro: Registro, noto_al: datetime | None = None) -> tuple[CreditoRiportato, ...]:
    """I crediti riportati dalle deleghe ancora attive: se la delega d'origine è scartata o annullata, il riporto non vale."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    riporti = (_riporto_dal_fatto(f) for f in registro.fatti_ente_noti(TIPO_CREDITO_RIPORTATO, istante))
    return tuple(r for r in riporti if delega_attiva(registro, r.delega, istante))


def _riporti_usati_da_deleghe_attive(registro: Registro, istante: datetime, ignorando: str | None) -> set[int]:
    usati: set[int] = set()
    for evento in registro.eventi(TIPO_DELEGA_TRASMESSA, istante):
        delega_id = evento.contenuto["id"]
        if delega_id != ignorando and delega_attiva(registro, delega_id, istante):
            usati.update(evento.contenuto["riporti_usati"])
    return usati


def _righe_candidate(registro: Registro, mese: Mese, istante: datetime):
    """(riga di composizione, riferimento, data di pagamento) delle righe degli esiti pagati del mese che la delega legge.

    I debiti sono le righe con canale F24EP. I crediti si ricavano dalla natura, qualunque sia il canale: il rimborso
    al lavoratore e' una riga sola, sul netto e verso il beneficiario, letta anche dalla delega (ADR 0023). I rapporti
    sono quelli pagati dall'evento: un credito di un rapporto non pagato non entra.
    """
    for evento in registro.eventi(TIPO_PAGAMENTO_ESEGUITO, istante):
        pagamento = registro.esito(evento.esito_id).data
        if Mese(pagamento.year, pagamento.month) != mese:
            continue
        versione = leggi_versione(registro, evento.versione_id)
        for rapporto in evento.contenuto["rapporti"]:
            for riga in versione.righe_del_rapporto(rapporto):
                if riga.canale == "f24ep" or riga.natura in NATURE_A_CREDITO:
                    yield riga, versione.riferimento(riga), pagamento


def _dati_ente(registro: Registro, giorno: date, istante: datetime) -> DatiEnte:
    def valore(tipo: str) -> str | None:
        fatto = registro.vigente_ente(tipo, giorno, istante)
        return fatto.valore if fatto is not None else None

    return DatiEnte(*(valore(tipo) for tipo in (*TIPI_DATI_ENTE, "sigla_provincia")))


def _regione_dell_irap(registro: Registro, rapporto: str, pagamento: date, istante: datetime) -> str | None:
    """La regione dell'acconto IRAP: la sede di lavoro del rapporto al pagamento, altrimenti la regione dell'ente."""
    sedi = registro.fatti_noti(rapporto, TIPO_SEDE_DI_LAVORO, istante)
    sede = next((fatto for fatto in reversed(sedi) if fatto.copre(pagamento)), None)
    if sede is not None:
        return str(sede.valore)
    ente = registro.vigente_ente(TIPO_REGIONE_ENTE, pagamento, istante)
    return str(ente.valore) if ente is not None else None


def _tre_mesi_prima(giorno: date) -> date:
    mese = giorno.month - 3
    anno = giorno.year - (1 if mese < 1 else 0)
    mese = mese + 12 if mese < 1 else mese
    ultimo = (date(anno + (mese == 12), mese % 12 + 1, 1) - timedelta(days=1)).day
    return date(anno, mese, min(giorno.day, ultimo))


def _regione_lasciata_da_poco(registro: Registro, rapporto: str, pagamento: date, istante: datetime) -> str | None:
    """La regione della sede precedente, se la sede che vale al pagamento e' di un'altra regione e decorre da meno di tre mesi."""
    sedi = registro.fatti_noti(rapporto, TIPO_SEDE_DI_LAVORO, istante)
    attuale = next((fatto for fatto in reversed(sedi) if fatto.copre(pagamento)), None)
    if attuale is None or attuale.valido_dal <= _tre_mesi_prima(pagamento):
        return None
    prima = [fatto for fatto in sedi if fatto.valido_dal < attuale.valido_dal]
    if not prima:
        return None
    precedente = max(prima, key=lambda fatto: (fatto.valido_dal, fatto.id))
    return str(precedente.valore) if precedente.valore != attuale.valore else None


def _ordine_riga(riga: RigaDelega) -> tuple:
    return (ORDINE_SEZIONI.index(riga.sezione), riga.tributo, riga.codice, riga.rif_a, riga.rif_b)


def _compensa(
    debiti: list[RigaDelega], crediti: list[RigaDelega]
) -> tuple[list[RigaDelega], list[Compensazione], list[CreditoResiduo]]:
    """Assorbe i crediti nei debiti: prima le ritenute (100E), poi gli altri nell'ordine delle sezioni.

    Un credito si ferma quando i debiti sono finiti: la parte non assorbita non va nella delega, resta
    tra i residui. I debiti non cambiano mai di valore, e il saldo non può quindi scendere sotto zero.
    """
    da_assorbire = sorted(
        debiti, key=lambda r: (r.tributo != CODICE_PRIMA_COMPENSAZIONE, *_ordine_riga(r))
    )
    capienza = {riga.chiave: riga.debito for riga in da_assorbire}
    righe = list(debiti)
    compensazioni: list[Compensazione] = []
    residui: list[CreditoResiduo] = []
    for credito in sorted(crediti, key=_ordine_riga):
        resto = credito.credito
        for debito in da_assorbire:
            presa = min(resto, capienza[debito.chiave])
            if presa > 0:
                compensazioni.append(Compensazione(credito.chiave, debito.chiave, presa))
                capienza[debito.chiave] -= presa
                resto -= presa
        assorbito = credito.credito - resto
        if assorbito > 0:
            righe.append(
                RigaDelega(
                    credito.sezione, credito.tributo, credito.codice, credito.estremi, credito.rif_a, credito.rif_b,
                    Decimal(0), assorbito, credito.origine,
                )
            )
        if resto > 0:
            residui.append(CreditoResiduo(credito.chiave, resto, credito.origine))
    return sorted(righe, key=_ordine_riga), compensazioni, residui


def costruisci_delega(
    registro: Registro,
    corpus: Corpus,
    mese_pagamento: Mese,
    noto_al: datetime | None = None,
    ignorando_delega: str | None = None,
) -> Delega:
    """La delega dei pagamenti eseguiti nel mese: funzione pura di registro, corpus e istante; non scrive nulla.

    Le righe già versate, o tenute da un'altra delega attiva (trasmessa e non scartata né annullata), non
    entrano: lo stesso importo non sta in due deleghe. `ignorando_delega` rilegge la vista come la vedeva
    quella delega, per confrontarla con ciò che ha trasmesso.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    versate = _righe_versate(registro, istante)
    tenute = _righe_in_deleghe_attive(registro, istante, ignorando_delega)
    altre: list[str] = []
    fermi: dict[tuple[str, str], FermoDelega] = {}

    def ferma(caso: str, soggetto: str, motivo: str) -> None:
        fermi.setdefault((caso, soggetto), FermoDelega(caso, motivo))

    try:
        scadenza = calcola_scadenza(corpus, mese_pagamento)
    except ParametroMancante as errore:
        scadenza = None
        ferma("scadenza_non_calcolabile", "delega", str(errore))
    data_versamento = registro.data_versamento_scelta(mese_pagamento, istante)
    giorno_dei_fatti = data_versamento or (scadenza.data if scadenza else mese_pagamento.ultimo_giorno)
    ente = _dati_ente(registro, giorno_dei_fatti, istante)
    somme: dict[tuple, list] = {}
    sorgenti: list[RiferimentoRiga] = []
    serve_provincia = False
    mancanti_regione: dict[str, DatoMancante] = {}
    avvisi_sede: dict[str, AvvisoDelega] = {}

    for riga, riferimento, pagamento in _righe_candidate(registro, mese_pagamento, istante):
        if riferimento in versate:
            continue
        if riferimento in tenute:
            if tenute[riferimento] not in altre:
                altre.append(tenute[riferimento])
            continue
        istituto, importo = riga.istituto, riga.importo
        if importo.valore == 0:
            # Un importo nullo (es. acconto IRAP di una persona esclusa) non versa nulla: nessuna riga da 0,00 (#81).
            continue
        mappatura = corpus.mappatura(istituto, SISTEMA_F24EP, pagamento, importo.anno_imposta)
        if mappatura is None:
            ferma(
                "mappatura_mancante",
                istituto,
                f"Istituto {istituto}: importo pagato il {pagamento} con canale F24EP senza codice tributo o causale",
            )
            continue
        codice = mappatura.codice
        voce = corpus.codice_f24ep(codice, pagamento)
        if voce is None:
            ferma(
                "codice_fuori_catalogo",
                istituto,
                f"Istituto {istituto}: il codice {codice} non è nel catalogo dei codici F24EP vigente il {pagamento}",
            )
            continue
        a_credito = riga.natura in NATURE_A_CREDITO
        if a_credito and not voce.a_credito:
            ferma(
                "credito_su_codice_a_debito",
                istituto,
                f"Istituto {istituto}: credito su {codice}, un codice che il catalogo ammette solo a debito",
            )
            continue
        if a_credito and voce.limite_credito == "non_modellato":
            ferma(
                "limite_credito",
                istituto,
                f"Istituto {istituto}: credito su {codice}, di cui il limite di compensazione non è ancora modellato",
            )
            continue
        codice_regione = ""
        if riga.natura == "irap" and voce.codice_campo == "regione":
            nome_regione = _regione_dell_irap(registro, riga.rapporto, pagamento, istante)
            if nome_regione is None:
                mancanti_regione.setdefault(
                    "regione",
                    DatoMancante(
                        "regione", "ente",
                        f"manca il fatto dell'ente regione valido al {pagamento}: serve all'IRAP dei rapporti senza sede di lavoro",
                    ),
                )
                continue
            mappata = corpus.mappatura_di_fatto(
                SISTEMA_REGIONE_F24EP, ELEMENTO_REGIONE_F24EP, TIPO_SEDE_DI_LAVORO, nome_regione, pagamento
            )
            if mappata is None:
                ferma(
                    "regione_non_mappata",
                    nome_regione,
                    f"Istituto {istituto}: la regione {nome_regione} non ha un codice regione nel corpus per un pagamento del {pagamento}",
                )
                continue
            codice_regione = mappata.codice
            precedente = _regione_lasciata_da_poco(registro, riga.rapporto, pagamento, istante)
            if precedente is not None:
                avvisi_sede.setdefault(
                    riga.rapporto,
                    AvvisoDelega(
                        AVVISO_CAMBIO_SEDE_RECENTE,
                        f"Rapporto {riga.rapporto}: la sede di lavoro e' cambiata da {precedente} a {nome_regione} da meno di "
                        f"tre mesi al pagamento del {pagamento}: il riparto per regione dell'IRAP conta il personale con "
                        "continuita' da almeno tre mesi, la soglia e' del saldo annuale e il modello non la applica",
                    ),
                )
        elif voce.codice_campo in ("regione", "catastale"):
            cosa = "codice catastale del comune" if voce.codice_campo == "catastale" else "codice della regione"
            ferma(
                "codice_non_modellato",
                istituto,
                f"Istituto {istituto}: il codice {codice} vuole il {cosa} di residenza del sostituito, "
                "che nessun fatto del registro porta: caso non modellato",
            )
            continue
        if "anno_imposta" in (voce.rif_a, voce.rif_b) and importo.anno_imposta is None:
            ferma(
                "anno_imposta_mancante",
                istituto,
                f"Istituto {istituto}: il codice {codice} vuole l'anno d'imposta e l'importo non lo porta",
            )
            continue
        serve_provincia = serve_provincia or voce.codice_campo == "provincia"
        chiave = (
            voce.sezione,
            codice,
            (ente.sigla_provincia or "") if voce.codice_campo == "provincia" else codice_regione,
            "",
            _formato(voce.rif_a, importo, pagamento),
            _formato(voce.rif_b, importo, pagamento),
            a_credito,
        )
        somme.setdefault(chiave, []).append(Origine(importo.valore, riferimento))
        sorgenti.append(riferimento)
    riporti_usati: list[int] = []
    if scadenza is not None:
        usati_da_altre = _riporti_usati_da_deleghe_attive(registro, istante, ignorando_delega)
        for riporto in crediti_riportati(registro, istante):
            if riporto.valido_dal > scadenza.data or riporto.fatto_id in usati_da_altre:
                continue
            somme.setdefault((*riporto.chiave, True), []).append(Origine(riporto.importo, riporto=riporto.fatto_id))
            riporti_usati.append(riporto.fatto_id)
    debiti: list[RigaDelega] = []
    crediti: list[RigaDelega] = []
    for (sezione, tributo, codice_campo, estremi, rif_a, rif_b, a_credito), origine in somme.items():
        totale = sum((o.valore for o in origine), Decimal(0))
        riga = RigaDelega(
            sezione, tributo, codice_campo, estremi, rif_a, rif_b,
            Decimal(0) if a_credito else totale, totale if a_credito else Decimal(0), tuple(origine),
        )
        (crediti if a_credito else debiti).append(riga)
    for riga in debiti:
        if riga.debito < 0:
            ferma(
                "debito_negativo",
                "/".join(riga.chiave),
                f"Il totale a debito del codice {riga.tributo} e' negativo ({riga.debito}; sezione {riga.sezione}, "
                f"riferimenti {riga.rif_a or '-'}/{riga.rif_b or '-'}): i conguagli a credito superano le ritenute "
                "della delega. Il recupero dell'eccedenza non ha ancora una fonte, la delega non si trasmette",
            )
    for riga in crediti:
        if riga.credito < 0:
            ferma(
                "credito_negativo",
                "/".join(riga.chiave),
                f"Il totale a credito del codice {riga.tributo} e' negativo ({riga.credito}; sezione {riga.sezione}): "
                "un credito negativo non e' un caso modellato, la delega non si trasmette",
            )
    righe, compensazioni, residui = _compensa(debiti, crediti)
    if crediti and not debiti:
        ferma(
            "solo_crediti",
            "delega",
            "La delega ha solo crediti (" + ", ".join(sorted({r.tributo for r in crediti})) + ") e nessun debito da "
            "compensare: portare un credito senza debiti non è modellato",
        )
    if len(righe) > RIGHE_PER_MODULO:
        ferma(
            "piu_di_22_righe",
            "delega",
            f"La delega ha {len(righe)} righe e un modulo ne porta {RIGHE_PER_MODULO}: dividere i crediti "
            "tra più moduli non è modellato",
        )
    mancanti = list(mancanti_regione.values())
    obbligatori = (*TIPI_DATI_ENTE, *(("sigla_provincia",) if serve_provincia else ()))
    for tipo in obbligatori:
        if getattr(ente, tipo) is None:
            mancanti.append(DatoMancante(tipo, "ente", f"manca il fatto dell'ente {tipo} valido al {giorno_dei_fatti}"))
    if data_versamento is None:
        mancanti.append(
            DatoMancante(
                "data_versamento", "ente", f"manca la data di versamento scelta per i pagamenti di {mese_pagamento}"
            )
        )
    if all(getattr(ente, tipo) is not None for tipo in TIPI_DATI_ENTE):
        for problema in problemi_dati_ente(*(getattr(ente, tipo) for tipo in TIPI_DATI_ENTE)):
            ferma("dato_non_valido", problema, f"Dati dell'ente: {problema}")
    if serve_provincia and ente.sigla_provincia is not None and not re.fullmatch(r"[A-Z]{2}", ente.sigla_provincia):
        ferma(
            "dato_non_valido",
            "sigla_provincia",
            f"Dati dell'ente: sigla di provincia {ente.sigla_provincia!r}, servono due lettere maiuscole",
        )
    avvisi = list(scadenza.avvisi) if scadenza else []
    avvisi.extend(avvisi_sede.values())
    if scadenza and data_versamento and data_versamento > scadenza.data:
        avvisi.append(
            AvvisoDelega(
                AVVISO_VERSAMENTO_TARDIVO,
                f"La data di versamento {data_versamento} è dopo la scadenza {scadenza.data}: il versamento sarebbe "
                "tardivo, il ravvedimento non è modellato",
            )
        )
    return Delega(
        mese_pagamento, scadenza, data_versamento, tuple(righe), tuple(sorgenti), ente, tuple(mancanti),
        tuple(fermi.values()), tuple(avvisi), tuple(compensazioni), tuple(residui), tuple(altre),
        tuple(riporti_usati),
    )


# Delega trasmessa: esito dichiarato, file telematico, annullamento

@dataclass(frozen=True)
class DelegaTrasmessa:
    """La delega com'è stata trasmessa: un esito dichiarato, che non cambia più. Si rilegge dal registro."""

    id: str
    mese_pagamento: Mese
    scadenza: date
    data_versamento: date
    righe: tuple[RigaDelega, ...]
    compensazioni: tuple[Compensazione, ...]
    residui: tuple[CreditoResiduo, ...]
    ente: DatiEnte
    sorgenti: tuple[RiferimentoRiga, ...]
    riporti_usati: tuple[int, ...]
    esito_id: int
    avvisi: tuple[AvvisoDelega, ...]
    file: bytes

    @property
    def totale_debito(self) -> Decimal:
        return sum((r.debito for r in self.righe), Decimal(0))

    @property
    def totale_credito(self) -> Decimal:
        return sum((r.credito for r in self.righe), Decimal(0))

    @property
    def saldo(self) -> Decimal:
        return self.totale_debito - self.totale_credito


def _origine_in_dizionario(origine: Origine) -> dict:
    return {
        "valore": str(origine.valore),
        "riferimento": origine.riferimento.in_dizionario() if origine.riferimento else None,
        "riporto": origine.riporto,
    }


def _origine_da_dizionario(dati: dict) -> Origine:
    riferimento = _riferimento_da_dizionario(dati["riferimento"]) if dati["riferimento"] else None
    return Origine(Decimal(dati["valore"]), riferimento, dati["riporto"])


def _riga_in_dizionario(riga: RigaDelega) -> dict:
    return {
        "chiave": list(riga.chiave),
        "debito": str(riga.debito),
        "credito": str(riga.credito),
        "origine": [_origine_in_dizionario(o) for o in riga.origine],
    }


def _riga_da_dizionario(dati: dict) -> RigaDelega:
    sezione, tributo, codice, estremi, rif_a, rif_b = dati["chiave"]
    return RigaDelega(
        sezione, tributo, codice, estremi, rif_a, rif_b,
        Decimal(dati["debito"]), Decimal(dati["credito"]), tuple(_origine_da_dizionario(o) for o in dati["origine"]),
    )


def _contenuto_della_delega(delega_id: str, delega: Delega, riporti_usati: tuple[int, ...], avvisi) -> dict:
    return {
        "id": delega_id,
        "mese": str(delega.mese_pagamento),
        "scadenza": delega.scadenza.data.isoformat(),
        "scadenza_riferimento": delega.scadenza.riferimento,
        "data_versamento": delega.data_versamento.isoformat(),
        "righe": [_riga_in_dizionario(r) for r in delega.righe],
        "compensazioni": [
            {"credito": list(c.credito), "debito": list(c.debito), "importo": str(c.importo)}
            for c in delega.compensazioni
        ],
        "residui": [
            {"chiave": list(r.chiave), "importo": str(r.importo), "origine": [_origine_in_dizionario(o) for o in r.origine]}
            for r in delega.residui
        ],
        "ente": {tipo: getattr(delega.ente, tipo) for tipo in (*TIPI_DATI_ENTE, "sigla_provincia")},
        "sorgenti": [r.in_dizionario() for r in delega.sorgenti],
        "riporti_usati": list(riporti_usati),
        "avvisi": [{"tipo": a.tipo, "messaggio": a.messaggio} for a in avvisi],
    }


def _file_telematico(ente: DatiEnte, data_versamento: date, righe) -> bytes:
    modulo = ModuloF24EP(
        tuple(
            RigaF24EP(r.sezione, r.tributo, r.codice, r.estremi, r.rif_a, r.rif_b, r.debito, r.credito) for r in righe
        )
    )
    modello = ModelloF24EP(
        ente.codice_fiscale, ente.denominazione, ente.email, ente.iban_tesoreria, data_versamento, (modulo,)
    )
    return serializza(FornituraF24EP((modello,)))


def _trasmessa_dal_contenuto(esito_id: int, dati: dict) -> DelegaTrasmessa:
    ente = DatiEnte(**dati["ente"])
    righe = tuple(_riga_da_dizionario(r) for r in dati["righe"])
    data_versamento = date.fromisoformat(dati["data_versamento"])
    return DelegaTrasmessa(
        id=dati["id"],
        mese_pagamento=Mese.da_testo(dati["mese"]),
        scadenza=date.fromisoformat(dati["scadenza"]),
        data_versamento=data_versamento,
        righe=righe,
        compensazioni=tuple(
            Compensazione(tuple(c["credito"]), tuple(c["debito"]), Decimal(c["importo"])) for c in dati["compensazioni"]
        ),
        residui=tuple(
            CreditoResiduo(tuple(r["chiave"]), Decimal(r["importo"]), tuple(_origine_da_dizionario(o) for o in r["origine"]))
            for r in dati["residui"]
        ),
        ente=ente,
        sorgenti=tuple(_riferimento_da_dizionario(r) for r in dati["sorgenti"]),
        riporti_usati=tuple(dati["riporti_usati"]),
        esito_id=esito_id,
        avvisi=tuple(AvvisoDelega(a["tipo"], a["messaggio"]) for a in dati["avvisi"]),
        file=_file_telematico(ente, data_versamento, righe),
    )


def leggi_delega_trasmessa(registro: Registro, delega_id: str) -> DelegaTrasmessa:
    evento = registro.evento(_chiave_delega(delega_id))
    if evento is None or evento.tipo != TIPO_DELEGA_TRASMESSA:
        raise ErroreRegistro(f"Delega {delega_id}: inesistente")
    return _trasmessa_dal_contenuto(evento.esito_id, evento.contenuto)


# Termini dell'Allegato 2 (par. 3, lettere c e d), in ora italiana

def _ultima_domenica(anno: int, mese: int) -> date:
    giorno = date(anno, mese, 31)
    return giorno - timedelta(days=(giorno.weekday() + 1) % 7)


def _ora_italiana_in_utc(giorno: date, ore: int) -> datetime:
    """L'istante UTC di `ore` ore dopo la mezzanotte italiana di `giorno`: l'ora legale va da fine marzo a fine ottobre."""
    inizio = datetime.combine(_ultima_domenica(giorno.year, 3), datetime.min.time(), UTC) + timedelta(hours=1)
    fine = datetime.combine(_ultima_domenica(giorno.year, 10), datetime.min.time(), UTC) + timedelta(hours=1)
    mezzanotte_cet = datetime.combine(giorno, datetime.min.time(), UTC) - timedelta(hours=1)
    istante = mezzanotte_cet + timedelta(hours=ore)
    return istante - timedelta(hours=1) if inizio <= istante < fine else istante


def _giorno_lavorativo_prima(corpus: Corpus, giorno: date, quanti: int) -> date:
    while quanti:
        giorno -= timedelta(days=1)
        if _e_lavorativo(corpus, giorno):
            quanti -= 1
    return giorno


def termine_trasmissione(corpus: Corpus, data_versamento: date, saldo: Decimal) -> datetime:
    """Saldo maggiore di zero: le 20:00 del secondo giorno lavorativo prima. Saldo zero: le 24:00 del giorno di versamento."""
    if saldo > 0:
        return _ora_italiana_in_utc(_giorno_lavorativo_prima(corpus, data_versamento, 2), 20)
    return _ora_italiana_in_utc(data_versamento + timedelta(days=1), 0)


def termine_annullamento(corpus: Corpus, data_versamento: date, saldo: Decimal) -> datetime:
    """Saldo maggiore di zero: le 22:00 del secondo giorno lavorativo prima. Saldo zero: le 24:00 del giorno di versamento."""
    if saldo > 0:
        return _ora_italiana_in_utc(_giorno_lavorativo_prima(corpus, data_versamento, 2), 22)
    return _ora_italiana_in_utc(data_versamento + timedelta(days=1), 0)


def _importo_della_riga(registro: Registro, riferimento: RiferimentoRiga) -> Importo:
    versione = leggi_versione(registro, riferimento.versione_id)
    riga = next(r for r in versione.righe if versione.riferimento(r) == riferimento)
    return riga.importo


def _ragioni_di_fermo(delega: Delega) -> list[str]:
    ragioni = [f.motivo for f in delega.fermi]
    ragioni += [f"dato mancante {d.tipo}: {d.motivo}" for d in delega.dati_mancanti]
    if not delega.righe and not delega.fermi:
        gia = f" (già nelle deleghe {', '.join(delega.altre_deleghe)})" if delega.altre_deleghe else ""
        ragioni.append("nessuna riga da versare" + gia)
    return ragioni


def trasmetti_delega(
    registro: Registro, corpus: Corpus, delega_id: str, adattatore: str, mese_pagamento: Mese
) -> DelegaTrasmessa:
    """Trasmette la delega dei pagamenti del mese: l'esito dichiarato nasce qui e non cambia più.

    Con lo stesso identificativo e la stessa delega non ha effetto; con una delega diversa è un errore: una
    correzione è una nuova delega, dopo lo scarto o l'annullamento della precedente. Una delega ferma o con
    dati mancanti non si trasmette.
    """
    if not isinstance(delega_id, str) or not delega_id.strip():
        raise ErroreRegistro("La delega ha un identificativo")
    chiave = _chiave_delega(delega_id)
    delega = costruisci_delega(registro, corpus, mese_pagamento, ignorando_delega=delega_id)
    gia = registro.evento(chiave)
    if gia is not None:
        nuovo = _contenuto_della_delega(delega_id, delega, delega.riporti_usati, ()) if delega.pronta else None
        vecchio = {k: v for k, v in gia.contenuto.items() if k != "avvisi"}
        if nuovo is None or {k: v for k, v in nuovo.items() if k != "avvisi"} != vecchio:
            raise ErroreRegistro(f"Evento {chiave}: stesso identificativo con contenuto diverso, rifiutato")
        return _trasmessa_dal_contenuto(gia.esito_id, gia.contenuto)
    if not delega.pronta:
        raise VistaFerma(f"Delega {delega_id} non trasmissibile: " + "; ".join(_ragioni_di_fermo(delega)))
    istante = registro.adesso()
    avvisi = list(delega.avvisi)
    if istante > termine_trasmissione(corpus, delega.data_versamento, delega.saldo):
        avvisi.append(
            AvvisoDelega(
                AVVISO_TRASMISSIONE_TARDIVA,
                f"La delega è trasmessa oltre il termine per la data di versamento {delega.data_versamento}: "
                "sarà eseguita il secondo giorno lavorativo successivo alla ricezione (Allegato 2, par. 3, lettera c)",
            )
        )
    contenuto = _contenuto_della_delega(delega_id, delega, delega.riporti_usati, avvisi)
    with registro.atomico():
        esito = registro.registra_esito(
            TipoEsito.DICHIARATO, istante.date(), [_importo_della_riga(registro, r) for r in delega.sorgenti]
        )
        evento = registro.registra_evento(chiave, TIPO_DELEGA_TRASMESSA, contenuto, adattatore, esito_id=esito.id)
        for residuo in delega.residui:
            registro.registra_codice_ente(
                TIPO_CREDITO_RIPORTATO,
                json.dumps(
                    {
                        "delega": delega_id,
                        "scadenza": delega.scadenza.data.isoformat(),
                        "chiave": list(residuo.chiave),
                        "importo": str(residuo.importo),
                        "origine": [_origine_in_dizionario(o) for o in residuo.origine],
                    },
                    sort_keys=True,
                ),
                delega.scadenza.data + timedelta(days=1),
            )
    return _trasmessa_dal_contenuto(evento.esito_id, evento.contenuto)


def annulla_delega(registro: Registro, corpus: Corpus, chiave: str, adattatore: str, delega_id: str) -> Evento:
    """L'annullamento chiesto entro il termine dell'Allegato 2 è un fatto a sé: le righe tornano da versare."""
    contenuto = {"delega": delega_id}
    gia = _evento_gia_noto(registro, chiave, TIPO_DELEGA_ANNULLATA, contenuto)
    if gia is not None:
        return gia
    trasmessa = leggi_delega_trasmessa(registro, delega_id)
    istante = registro.adesso()
    if any(e.contenuto["delega"] == delega_id for e in registro.eventi(TIPO_DELEGA_ANNULLATA, istante)):
        raise ErroreRegistro(f"Delega {delega_id}: già annullata")
    termine = termine_annullamento(corpus, trasmessa.data_versamento, trasmessa.saldo)
    if istante > termine:
        raise ErroreRegistro(
            f"Delega {delega_id}: l'annullamento è fuori termine, scaduto il {termine:%Y-%m-%d %H:%M} UTC: "
            "il termine dell'Allegato 2 è passato"
        )
    return registro.registra_evento(chiave, TIPO_DELEGA_ANNULLATA, contenuto, adattatore)


# Esito versato

def registra_versamento_delega(
    registro: Registro, chiave: str, adattatore: str, delega_id: str, data: date, provenienza: str = "addebito"
) -> Esito:
    """L'addebito (o la regolarizzazione) della delega: ne nasce l'esito versato, una sola volta, con la data reale.

    Usa l'evento di versamento eseguito del nucleo: il suo identificativo di versamento è quello della delega e le
    righe versate sono quelle che la delega ha trasmesso, crediti compresi. Una delega scartata o annullata non si versa.
    """
    trasmessa = leggi_delega_trasmessa(registro, delega_id)
    istante = registro.adesso()
    if any(e.contenuto["delega"] == delega_id for e in registro.eventi(TIPO_DELEGA_ANNULLATA, istante)):
        raise ErroreRegistro(f"Delega {delega_id}: annullata, gli importi vanno versati con una nuova")
    return registra_versamento_eseguito(
        registro, chiave, adattatore, delega_id, data, trasmessa.sorgenti, "f24ep", provenienza
    )


@dataclass(frozen=True)
class SituazioneDelega:
    """Dove è arrivata la delega: stato dalle ricevute, data del versamento e ciò che la ferma."""

    stato: StatoDelega
    attiva: bool
    versata_il: date | None
    fermi: tuple[FermoDelega, ...]


def situazione_delega(registro: Registro, delega_id: str, noto_al: datetime | None = None) -> SituazioneDelega:
    """Un versamento dopo la scadenza ferma quella delega: il ravvedimento non è nel modello."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    trasmessa = leggi_delega_trasmessa(registro, delega_id)
    versamento = next(
        (e for e in registro.eventi(TIPO_VERSAMENTO_ESEGUITO, istante) if e.contenuto["versamento"] == delega_id), None
    )
    versata_il = registro.esito(versamento.esito_id).data if versamento is not None else None
    fermi = []
    if versata_il is not None and versata_il > trasmessa.scadenza:
        fermi.append(
            FermoDelega(
                "versamento_tardivo",
                f"Delega {delega_id}: versata il {versata_il}, dopo la scadenza {trasmessa.scadenza}: "
                "il ravvedimento non è modellato",
            )
        )
    return SituazioneDelega(
        stato_delega(registro, delega_id, istante), delega_attiva(registro, delega_id, istante), versata_il, tuple(fermi)
    )
