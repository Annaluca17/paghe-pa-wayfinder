"""Delega F24EP: vista del modello dagli esiti pagati alla delega trasmessa e versata (ADR 0023, 0025).

La delega nasce dalla composizione del pagamento: le righe con canale F24EP degli esiti pagati, non
ancora versate, diventano righe per sezione, codice tributo o causale e riferimenti, con i crediti
del sostituto compensati. Il codice è una mappatura datata dell'istituto (ADR 0022); un importo senza
mappatura ferma l'invio, non il calcolo. Questo modulo non decide nulla che l'ADR non dica: dove manca
una regola, la delega si ferma nominando il caso.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from .corpus import Corpus
from .errori import ErroreCalcolo, ParametroMancante
from .modello import Importo
from .proposta import (
    TIPO_PAGAMENTO_ESEGUITO,
    DatoMancante,
    RiferimentoRiga,
    RigaComposizione,
    leggi_versione,
)
from .registro import Registro
from .tempo import Mese, in_utc

# Sistema della mappatura esterna dell'istituto: codice tributo o causale F24EP (ADR 0022).
SISTEMA_F24EP = "codice_tributo_f24ep"
TIPO_DELEGA_TRASMESSA = "delega_trasmessa"
TIPO_DELEGA_ANNULLATA = "delega_annullata"

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


# Vista della delega

ORDINE_SEZIONI = "FIRSNQWGP5"  # l'ordine delle sezioni nella delega
RIGHE_PER_MODULO = 22
NATURE_A_CREDITO = frozenset({"rimborso_730", "credito_sostituto"})
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


def _righe_candidate(registro: Registro, mese: Mese, istante: datetime):
    """(riga di composizione, riferimento, data di pagamento) delle righe F24EP degli esiti pagati del mese."""
    for evento in registro.eventi(TIPO_PAGAMENTO_ESEGUITO, istante):
        pagamento = registro.esito(evento.esito_id).data
        if Mese(pagamento.year, pagamento.month) != mese:
            continue
        versione = leggi_versione(registro, evento.versione_id)
        for rapporto in evento.contenuto["rapporti"]:
            for riga in versione.righe_del_rapporto(rapporto):
                if riga.canale == "f24ep":
                    yield riga, versione.riferimento(riga), pagamento


def _dati_ente(registro: Registro, giorno: date, istante: datetime) -> DatiEnte:
    def valore(tipo: str) -> str | None:
        fatto = registro.vigente_ente(tipo, giorno, istante)
        return fatto.valore if fatto is not None else None

    return DatiEnte(*(valore(tipo) for tipo in (*TIPI_DATI_ENTE, "sigla_provincia")))


def costruisci_delega(registro: Registro, corpus: Corpus, mese_pagamento: Mese, noto_al: datetime | None = None) -> Delega:
    """La delega dei pagamenti eseguiti nel mese: funzione pura di registro, corpus e istante; non scrive nulla."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    scadenza = calcola_scadenza(corpus, mese_pagamento)
    data_versamento = registro.data_versamento_scelta(mese_pagamento, istante)
    ente = _dati_ente(registro, data_versamento or scadenza.data, istante)
    somme: dict[tuple, list] = {}
    sorgenti: list[RiferimentoRiga] = []
    fermi: dict[tuple[str, str], FermoDelega] = {}

    def ferma(caso: str, soggetto: str, motivo: str) -> None:
        fermi.setdefault((caso, soggetto), FermoDelega(caso, motivo))

    for riga, riferimento, pagamento in _righe_candidate(registro, mese_pagamento, istante):
        istituto, importo = riga.istituto, riga.importo
        if riga.natura == "irap":
            ferma(
                "irap",
                istituto,
                f"Istituto {istituto}: riga IRAP nella delega, la scadenza e il riparto per regione non sono ancora modellati",
            )
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
        if voce.codice_campo in ("regione", "catastale"):
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
        chiave = (
            voce.sezione,
            codice,
            (ente.sigla_provincia or "") if voce.codice_campo == "provincia" else "",
            "",
            _formato(voce.rif_a, importo, pagamento),
            _formato(voce.rif_b, importo, pagamento),
            a_credito,
        )
        somme.setdefault(chiave, []).append(Origine(importo.valore, riferimento))
        sorgenti.append(riferimento)
    righe = []
    for (sezione, tributo, codice_campo, estremi, rif_a, rif_b, a_credito), origine in somme.items():
        totale = sum((o.valore for o in origine), Decimal(0))
        righe.append(
            RigaDelega(
                sezione, tributo, codice_campo, estremi, rif_a, rif_b,
                Decimal(0) if a_credito else totale, totale if a_credito else Decimal(0), tuple(origine),
            )
        )
    righe.sort(key=lambda r: (ORDINE_SEZIONI.index(r.sezione), r.tributo, r.codice, r.rif_a, r.rif_b))
    if len(righe) > RIGHE_PER_MODULO:
        ferma(
            "piu_di_22_righe",
            "delega",
            f"La delega ha {len(righe)} righe e un modulo ne porta {RIGHE_PER_MODULO}: dividere i crediti "
            "tra più moduli non è modellato",
        )
    mancanti = []
    return Delega(
        mese_pagamento, scadenza, data_versamento, tuple(righe), tuple(sorgenti), ente, tuple(mancanti),
        tuple(fermi.values()), (),
    )
