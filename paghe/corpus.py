"""Corpus di regole e parametri, con vigenza, fonte e versione."""

from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .errori import ErroreCorpus, ParametroMancante, ValiditaNonUniforme
from .formula import riferimenti
from .modello import FATTO_PART_TIME, FATTO_TIPO_PART_TIME
from .riferimento import motivo_rifiuto
from .tempo import Mese


def _riferimento_obbligatorio(riferimento: str, soggetto: str) -> None:
    if not isinstance(riferimento, str) or not riferimento.strip():
        raise ErroreCorpus(f"{soggetto}: riferimento normativo obbligatorio")
    motivo = motivo_rifiuto(riferimento)
    if motivo:
        raise ErroreCorpus(f"{soggetto}: riferimento non valido, {motivo}")


MATURAZIONI = {"giorni", "evento", "periodo", "mese", "annuale"}
# Maturazioni che leggono le basi della denuncia: sul periodo dichiarato o sul totale del mese.
MATURAZIONI_DI_CASSA = {"periodo", "mese"}
CONTEGGI = {"lun_sab", "calendario"}
MISURE = {"intero", "parziale", "escluso"}
AMBITI_FERMO = {"calcolo", "denuncia", "vista"}
FITTIZIO = "fittizio:"
# Dichiarazione di composizione (ADR 0025): valori ammessi.
NATURE = frozenset({
    "retribuzione", "ritenuta", "addizionale", "contributo_lavoratore", "contributo_ente",
    "rata_730", "rimborso_730", "credito_sostituto", "trattenuta_terzi", "irap",
})
EFFETTI = frozenset({"piu", "meno", "nessuno"})
DESTINATARI = frozenset({"beneficiario", "terzo"})
CANALI = frozenset({"accredito", "f24ep", "bonifico"})
# Catalogo dei codici F24EP (ticket #54): valori ammessi.
SEZIONI_F24EP = frozenset({"F", "I", "R", "S", "N", "Q", "W", "G", "P", "5"})
CODICE_CAMPO_F24EP = frozenset({"nessuno", "regione", "catastale", "provincia"})
ESTREMI_F24EP = frozenset({"nessuno", "facoltativo"})
RIF_A_F24EP = frozenset({"nessuno", "mese_pagamento", "periodo_inizio"})
RIF_B_F24EP = frozenset({"nessuno", "anno_pagamento", "anno_imposta", "periodo_fine"})
MODALITA_F24EP = frozenset({"debito", "debito_credito"})
LIMITI_CREDITO_F24EP = frozenset({"nessuno", "non_modellato"})
FONTI_SCADENZA = frozenset({"norma", "prassi"})
# Trattamento nel part-time (ADR 0026): proporzionale si riduce, intero no, da_integrativo lo fissa l'ente con un input da atto.
TRATTAMENTI_PART_TIME = frozenset({"proporzionale", "intero", "da_integrativo"})


@dataclass(frozen=True)
class VigenzaParametro:
    dal: date
    valore: Decimal
    riferimento: str
    al: date | None = None


@dataclass(frozen=True)
class Parametro:
    """Un parametro annuale, come una soglia INPS, chiude l'ultima vigenza con `al`: oltre, il calcolo si ferma."""

    nome: str
    vigenze: tuple[VigenzaParametro, ...]

    def __post_init__(self) -> None:
        if not self.vigenze:
            raise ErroreCorpus(f"Parametro {self.nome}: nessuna vigenza")
        for vigenza in self.vigenze:
            _riferimento_obbligatorio(vigenza.riferimento, f"Parametro {self.nome}")
            if vigenza.al is not None and vigenza.al < vigenza.dal:
                raise ErroreCorpus(f"Parametro {self.nome}: vigenza invertita")
        decorrenze = [vigenza.dal for vigenza in self.vigenze]
        if len(set(decorrenze)) != len(decorrenze):
            raise ErroreCorpus(f"Parametro {self.nome}: decorrenze duplicate")
        ordinate = tuple(sorted(self.vigenze, key=lambda v: v.dal))
        if any(vigenza.al is not None for vigenza in ordinate[:-1]):
            raise ErroreCorpus(f"Parametro {self.nome}: solo l'ultima vigenza può avere una fine")
        object.__setattr__(self, "vigenze", ordinate)

    def _vigente(self, giorno: date) -> VigenzaParametro | None:
        trovata = None
        for vigenza in self.vigenze:
            if vigenza.dal <= giorno:
                trovata = vigenza
        if trovata is not None and trovata.al is not None and giorno > trovata.al:
            return None
        return trovata

    def vigenza_per(self, competenza: Mese) -> VigenzaParametro:
        inizio = self._vigente(competenza.primo_giorno)
        fine = self._vigente(competenza.ultimo_giorno)
        if fine is None:
            raise ParametroMancante(f"Parametro {self.nome}: nessuna vigenza per {competenza}")
        if inizio != fine:
            raise ValiditaNonUniforme(f"Parametro {self.nome}: cambia dentro {competenza}")
        return fine


@dataclass(frozen=True)
class Regola:
    """Una regola vale per un intervallo di competenza.

    Nuova vigenza: un'altra regola dello stesso istituto, con decorrenza successiva.
    Correzione: stessa vigenza e `versione` successiva, in un nuovo corpus.
    """

    istituto: str
    versione: int
    dal: date
    riferimento: str
    formula: str
    maturazione: str = ""
    al: date | None = None
    descrizione: str = ""
    applica_se: str | None = None
    conteggio: str | None = None
    divisore: str | None = None
    decimali: int | None = None

    @property
    def fatto_condizione(self) -> str | None:
        """Tipo di fatto di `applica_se`; nella forma `tipo=codice` vale solo se il codice coincide."""
        return self.applica_se.split("=", 1)[0] if self.applica_se else None

    @property
    def codice_condizione(self) -> str | None:
        if not self.applica_se or "=" not in self.applica_se:
            return None
        return self.applica_se.split("=", 1)[1]

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Regola {self.istituto}")
        if self.applica_se is not None and "=" in self.applica_se:
            tipo, codice = self.applica_se.split("=", 1)
            if not tipo.strip() or not codice.strip() or tipo != tipo.strip() or codice != codice.strip():
                raise ErroreCorpus(f"Regola {self.istituto}: applica_se va scritto come tipo=codice")
        self._controlla_maturazione()
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"Regola {self.istituto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"Regola {self.istituto}: vigenza invertita")
        if riferimenti(self.formula).fisco:
            raise ErroreCorpus(f"Regola {self.istituto}: `fisco.` vale solo per le formule di [[ritenuta]]")

    def _controlla_maturazione(self) -> None:
        soggetto = f"Regola {self.istituto}"
        if self.maturazione not in MATURAZIONI:
            raise ErroreCorpus(f"{soggetto}: maturazione obbligatoria, una di {sorted(MATURAZIONI)}")
        a_quota = self.maturazione in ("giorni", "annuale")
        if a_quota:
            if not self.applica_se:
                raise ErroreCorpus(f"{soggetto}: una maturazione a quota richiede applica_se, il fatto che dà il servizio")
            if self.conteggio not in CONTEGGI:
                raise ErroreCorpus(f"{soggetto}: conteggio obbligatorio, uno di {sorted(CONTEGGI)}")
            if type(self.decimali) is not int or self.decimali < 0:
                raise ErroreCorpus(f"{soggetto}: decimali obbligatori")
            if not self.divisore and (self.conteggio == "lun_sab" or self.maturazione == "annuale"):
                raise ErroreCorpus(f"{soggetto}: divisore obbligatorio")
        elif self.conteggio or self.divisore or self.decimali is not None:
            raise ErroreCorpus(f"{soggetto}: conteggio, divisore e decimali valgono solo per le maturazioni a quota")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)

    def si_sovrappone(self, altra: "Regola") -> bool:
        return (altra.al is None or self.dal <= altra.al) and (self.al is None or altra.dal <= self.al)


@dataclass(frozen=True)
class Base:
    """Base imponibile: insieme degli importi pagati su cui si calcola una contribuzione (ADR 0005)."""

    nome: str
    riferimento: str

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Base {self.nome}")


@dataclass(frozen=True)
class Concorso:
    """Un istituto dichiara a quale base concorre, in che misura e per quali date di pagamento."""

    istituto: str
    base: str
    misura: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Concorso {self.istituto} -> {self.base}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.misura not in MISURE:
            raise ErroreCorpus(f"{soggetto}: misura obbligatoria, una di {sorted(MISURE)}")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)

    def si_sovrappone(self, altro: "Concorso") -> bool:
        return (altro.al is None or self.dal <= altro.al) and (self.al is None or altro.dal <= self.al)


@dataclass(frozen=True)
class Fermo:
    """Un fatto che chiede un caso non modellato: se c'è nel mese, il calcolo si ferma e lo nomina.

    `calcolo` ferma anche gli importi per competenza; `denuncia` solo basi e contributi; `vista`
    lascia calcolare la denuncia e rende la ListaPosPA una bozza non trasmissibile (ADR 0008).
    Con `codice` il fermo scatta solo se il fatto categoriale ha quel valore (ADR 0009).
    """

    fatto: str
    caso: str
    ambito: str
    riferimento: str
    codice: str | None = None

    def __post_init__(self) -> None:
        soggetto = f"Fermo {self.fatto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.codice is not None and (not isinstance(self.codice, str) or not self.codice.strip()
                                        or self.codice != self.codice.strip()):
            raise ErroreCorpus(f"{soggetto}: codice non valido, {self.codice!r}")
        if not self.caso.strip():
            raise ErroreCorpus(f"{soggetto}: il caso va nominato")
        if self.ambito not in AMBITI_FERMO:
            raise ErroreCorpus(f"{soggetto}: ambito obbligatorio, uno di {sorted(AMBITI_FERMO)}")


@dataclass(frozen=True)
class DichiarazioneTrattamentoPartTime:
    """L'istituto dichiara come si comporta nel part-time (ADR 0026), con date e fonte."""

    istituto: str
    trattamento: str
    dal: date
    riferimento: str
    al: date | None = None
    # Tipo del fatto del rapporto, con atto, che porta la percentuale fissata dall'ente: solo per `da_integrativo`.
    fatto: str | None = None

    def __post_init__(self) -> None:
        soggetto = f"Part-time {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        if self.trattamento not in TRATTAMENTI_PART_TIME:
            raise ErroreCorpus(f"{soggetto}: trattamento uno di {sorted(TRATTAMENTI_PART_TIME)}")
        if (self.trattamento == "da_integrativo") != bool(self.fatto):
            raise ErroreCorpus(f"{soggetto}: il fatto di input va indicato se, e solo se, il trattamento è da_integrativo")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class Massimale:
    """Base annua sottoposta a massimale: il superamento nell'anno ferma la denuncia (ADR 0005)."""

    base: str
    parametro: str


@dataclass(frozen=True)
class RegoleDenuncia:
    """Cumuli per persona e per anno che la prima fetta non modella: servono solo a fermarsi.

    `persona` è il fatto categoriale che identifica la persona, come il codice fiscale.
    `conguaglio_annuo` elenca le regole sul mese che l'anno può conguagliare.
    """

    persona: str | None = None
    massimale: Massimale | None = None
    conguaglio_annuo: tuple[str, ...] = ()


def _vigenze_sovrapposte(voci, soggetto: str) -> None:
    for indice, voce in enumerate(voci):
        for altra in voci[indice + 1 :]:
            if (altra.al is None or voce.dal <= altra.al) and (voce.al is None or altra.dal <= voce.al):
                raise ErroreCorpus(f"{soggetto}: vigenze sovrapposte")


def _vigente(voci, giorno: date):
    return next((voce for voce in voci if voce.dal <= giorno and (voce.al is None or giorno <= voce.al)), None)


@dataclass(frozen=True)
class CassaAllargata:
    """Se per la categoria vale la cassa allargata (somme pagate entro il 12 gennaio all'anno prima), con date e fonte."""

    dal: date
    vale: bool
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, "Cassa allargata")
        if type(self.vale) is not bool:
            raise ErroreCorpus("Cassa allargata: `vale` è vero o falso")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus("Cassa allargata: vigenza invertita")


@dataclass(frozen=True)
class CategoriaReddito:
    """Categoria logica del modello, senza articoli nel nome (ADR 0015). Dichiara la cassa allargata."""

    nome: str
    cassa_allargata: tuple[CassaAllargata, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ErroreCorpus("Categoria di reddito: il nome è obbligatorio")
        _vigenze_sovrapposte(self.cassa_allargata, f"Categoria {self.nome}: cassa allargata")

    def cassa_allargata_al(self, giorno: date) -> CassaAllargata | None:
        return _vigente(self.cassa_allargata, giorno)


@dataclass(frozen=True)
class DichiarazioneReddito:
    """L'istituto dichiara la categoria di reddito, con date e fonte (ADR 0015)."""

    istituto: str
    categoria: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Reddito {self.istituto}")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"Reddito {self.istituto}: vigenza invertita")


@dataclass(frozen=True)
class DichiarazionePagamentoFisiologico:
    """L'istituto dichiara che il suo pagamento oltre l'anno di competenza è fisiologico (ADR 0018), con date e fonte."""

    istituto: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Pagamento fisiologico {self.istituto}")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"Pagamento fisiologico {self.istituto}: vigenza invertita")


@dataclass(frozen=True)
class DichiarazioneDeduzione:
    """L'istituto dichiara che il suo importo riduce l'imponibile fiscale (art. 51 c. 2 lett. a TUIR), con date e fonte."""

    istituto: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Deduzione fiscale {self.istituto}")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"Deduzione fiscale {self.istituto}: vigenza invertita")


PERIODI_FISCALI = frozenset({"imponibile", "periodi"})


@dataclass(frozen=True)
class RegolaRitenuta:
    """Ritenuta del pagamento (ADR 0019), con scaglioni annui ragguagliati al periodo di paga.

    Le due formule leggono parametri e due valori che dà il motore: `fisco.imponibile`, il reddito del
    periodo di paga (o dell'anno, nel conguaglio), e `fisco.periodi`, i periodi di paga dell'anno
    (12 per il mese, 1 per il conguaglio). `detrazione` si applica solo con la dichiarazione del
    sostituito che chiede `detrazione_richiesta`. La regola copre solo le `categorie` elencate.
    """

    istituto: str
    versione: int
    dal: date
    riferimento: str
    imposta: str
    detrazione: str
    categorie: tuple[str, ...]
    detrazione_richiesta: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Ritenuta {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"{soggetto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        if not self.categorie:
            raise ErroreCorpus(f"{soggetto}: categorie obbligatorie")
        if not self.detrazione_richiesta.strip():
            raise ErroreCorpus(f"{soggetto}: detrazione_richiesta obbligatoria")
        for formula in (self.imposta, self.detrazione):
            letti = riferimenti(formula)
            if letti.fatti or letti.importi or letti.basi:
                raise ErroreCorpus(f"{soggetto}: la formula legge solo parametri e fisco, non fatti, importi o basi")
            ignoti = letti.fisco - PERIODI_FISCALI
            if ignoti:
                raise ErroreCorpus(f"{soggetto}: fisco ignoto {sorted(ignoti)}; ammessi {sorted(PERIODI_FISCALI)}")

    @property
    def parametri(self) -> frozenset[str]:
        return riferimenti(self.imposta).parametri | riferimenti(self.detrazione).parametri


@dataclass(frozen=True)
class RegolaConguaglio:
    """Conguaglio fiscale (ADR 0019): le formule della ritenuta sull'imponibile fiscale dell'anno, con un solo periodo."""

    istituto: str
    versione: int
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Conguaglio {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"{soggetto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")


@dataclass(frozen=True)
class RegoleFiscali:
    categorie: tuple[CategoriaReddito, ...] = ()
    redditi: tuple[DichiarazioneReddito, ...] = ()
    ritenute: tuple[RegolaRitenuta, ...] = ()
    conguagli: tuple[RegolaConguaglio, ...] = ()
    fisiologici: tuple[DichiarazionePagamentoFisiologico, ...] = ()
    deduzioni: tuple[DichiarazioneDeduzione, ...] = ()

    def __bool__(self) -> bool:
        return bool(
            self.categorie or self.redditi or self.ritenute or self.conguagli or self.fisiologici or self.deduzioni
        )


@dataclass(frozen=True)
class DichiarazioneComposizione:
    """L'istituto dichiara come entra nella composizione del pagamento (ADR 0025), con date e fonte.

    Natura, effetto sul netto, destinatario e canale; oppure `intermedio`: l'istituto, come un totale
    che somma altri, non entra nella composizione.
    """

    istituto: str
    dal: date
    riferimento: str
    natura: str | None = None
    effetto: str | None = None
    destinatario: str | None = None
    canale: str | None = None
    intermedio: bool = False
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Composizione {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        if type(self.intermedio) is not bool:
            raise ErroreCorpus(f"{soggetto}: `intermedio` è vero o falso")
        campi = {
            "natura": (self.natura, NATURE),
            "effetto": (self.effetto, EFFETTI),
            "destinatario": (self.destinatario, DESTINATARI),
            "canale": (self.canale, CANALI),
        }
        if self.intermedio:
            if any(valore is not None for valore, _ in campi.values()):
                raise ErroreCorpus(f"{soggetto}: un istituto intermedio non dichiara natura, effetto, destinatario o canale")
            return
        for nome, (valore, ammessi) in campi.items():
            if valore not in ammessi:
                raise ErroreCorpus(f"{soggetto}: {nome} obbligatorio, uno di {sorted(ammessi)}")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class MappaturaEsterna:
    """Corrispondenza datata tra un istituto e un codice di un sistema esterno: codice tributo, causale, SICO, punto CU."""

    istituto: str
    sistema: str
    codice: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Mappatura {self.istituto} -> {self.sistema}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if not isinstance(self.sistema, str) or not self.sistema.strip():
            raise ErroreCorpus(f"{soggetto}: sistema obbligatorio")
        if not isinstance(self.codice, str) or not self.codice.strip():
            raise ErroreCorpus(f"{soggetto}: il codice va scritto come testo")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class CodiceF24EP:
    """Voce del catalogo dei codici F24EP, con vigenza e fonte (ticket #54).

    Dice in quale sezione sta il codice tributo o la causale, che cosa va nel campo «codice» (regione,
    codice catastale, sigla di provincia), se gli estremi si compilano e da dove vengono i riferimenti
    A e B. `modalita` dice se il codice si usa solo a debito o anche a credito; `limite_credito`
    `non_modellato` ferma ogni delega che lo usa a credito, perché il suo limite non è ancora modellato.
    """

    codice: str
    sezione: str
    codice_campo: str
    estremi: str
    rif_a: str
    rif_b: str
    modalita: str
    dal: date
    riferimento: str
    limite_credito: str = "nessuno"
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Codice F24EP {self.codice}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if not isinstance(self.codice, str) or not self.codice.strip() or self.codice != self.codice.strip():
            raise ErroreCorpus(f"{soggetto}: il codice va scritto come testo")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        campi = {
            "sezione": (self.sezione, SEZIONI_F24EP),
            "codice_campo": (self.codice_campo, CODICE_CAMPO_F24EP),
            "estremi": (self.estremi, ESTREMI_F24EP),
            "rif_a": (self.rif_a, RIF_A_F24EP),
            "rif_b": (self.rif_b, RIF_B_F24EP),
            "modalita": (self.modalita, MODALITA_F24EP),
            "limite_credito": (self.limite_credito, LIMITI_CREDITO_F24EP),
        }
        for nome, (valore, ammessi) in campi.items():
            if valore not in ammessi:
                raise ErroreCorpus(f"{soggetto}: {nome} obbligatorio, uno di {sorted(ammessi)}")
        if self.limite_credito != "nessuno" and self.modalita != "debito_credito":
            raise ErroreCorpus(f"{soggetto}: limite_credito vale solo per un codice usabile a credito")

    @property
    def a_credito(self) -> bool:
        return self.modalita == "debito_credito"

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class ProrogaScadenza:
    """Le scadenze di un mese tra due giorni slittano a un giorno fisso (la proroga di agosto).

    `fonte` dice se la regola regge su una norma o solo su una prassi: il modello lo segnala.
    """

    mese: int
    dal_giorno: int
    al_giorno: int
    fonte: str
    riferimento: str

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, "Proroga della scadenza F24EP")
        if self.fonte not in FONTI_SCADENZA:
            raise ErroreCorpus(f"Proroga della scadenza F24EP: fonte obbligatoria, una di {sorted(FONTI_SCADENZA)}")
        if not 1 <= self.mese <= 12 or not 1 <= self.dal_giorno <= self.al_giorno <= 31:
            raise ErroreCorpus("Proroga della scadenza F24EP: proroga incoerente, mese o giorni non validi")


@dataclass(frozen=True)
class RegolaScadenzaF24EP:
    """Il versamento F24EP scade il `giorno` del mese successivo al pagamento; con la fonte e la vigenza."""

    dal: date
    riferimento: str
    giorno: int = 16
    proroga: ProrogaScadenza | None = None
    al: date | None = None

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, "Scadenza F24EP")
        if type(self.giorno) is not int or not 1 <= self.giorno <= 28:
            raise ErroreCorpus("Scadenza F24EP: giorno non valido, da 1 a 28")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus("Scadenza F24EP: vigenza invertita")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class CalendarioFestivi:
    """Giorni festivi infrasettimanali di un anno, dichiarati: un anno senza calendario non ha festivi noti."""

    anno: int
    giorni: tuple[date, ...]
    riferimento: str

    def __post_init__(self) -> None:
        soggetto = f"Calendario dei festivi {self.anno}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if any(giorno.year != self.anno for giorno in self.giorni):
            raise ErroreCorpus(f"{soggetto}: un giorno non cade nell'anno {self.anno}")
        if len(set(self.giorni)) != len(self.giorni):
            raise ErroreCorpus(f"{soggetto}: giorni ripetuti")


class Corpus:
    """Insieme coerente e immutabile; la versione è l'impronta del contenuto."""

    def __init__(
        self,
        parametri: tuple[Parametro, ...],
        regole: tuple[Regola, ...],
        fatti_periodo_dichiarato: tuple[str, ...] = (),
        basi: tuple[Base, ...] = (),
        concorsi: tuple[Concorso, ...] = (),
        fatto_servizio: str | None = None,
        fermi: tuple[Fermo, ...] = (),
        denuncia: RegoleDenuncia | None = None,
        reale: bool = False,
        fiscale: RegoleFiscali | None = None,
        composizioni: tuple[DichiarazioneComposizione, ...] = (),
        mappature: tuple[MappaturaEsterna, ...] = (),
        codici_f24ep: tuple[CodiceF24EP, ...] = (),
        scadenze_f24ep: tuple[RegolaScadenzaF24EP, ...] = (),
        calendari_festivi: tuple[CalendarioFestivi, ...] = (),
        trattamenti_part_time: tuple[DichiarazioneTrattamentoPartTime, ...] = (),
    ):
        self.reale = reale
        self._trattamenti_part_time = tuple(trattamenti_part_time)
        self._scadenze_f24ep = tuple(scadenze_f24ep)
        self._calendari_festivi = tuple(calendari_festivi)
        self._codici_f24ep = tuple(codici_f24ep)
        self._composizioni = tuple(composizioni)
        self._mappature = tuple(mappature)
        self.fiscale = fiscale or RegoleFiscali()
        self.fermi = tuple(fermi)
        self.denuncia = denuncia or RegoleDenuncia()
        self.fatto_servizio = fatto_servizio
        fatti_periodo = tuple(fatti_periodo_dichiarato)
        if fatto_servizio and fatto_servizio not in fatti_periodo:
            fatti_periodo = (fatto_servizio, *fatti_periodo)
        self.fatti_periodo_dichiarato = fatti_periodo
        self._basi = {base.nome: base for base in basi}
        if len(self._basi) != len(basi):
            raise ErroreCorpus("Basi imponibili con lo stesso nome")
        self._concorsi = tuple(concorsi)
        self._parametri = {parametro.nome: parametro for parametro in parametri}
        if len(self._parametri) != len(parametri):
            raise ErroreCorpus("Parametri con lo stesso nome")
        self._regole: dict[str, list[Regola]] = {}
        for regola in regole:
            self._regole.setdefault(regola.istituto, []).append(regola)
        self._convalida()
        self._convalida_cassa()
        self._convalida_denuncia()
        self._convalida_fiscale()
        self._convalida_composizione()
        self._convalida_part_time()
        self._convalida_catalogo_f24ep()
        if reale:
            self._rifiuta_fittizi()
        self.versione = self._impronta()

    def _riferimenti(self) -> list[tuple[str, str]]:
        elenco = [(f"Parametro {p.nome}", v.riferimento) for p in self._parametri.values() for v in p.vigenze]
        elenco += [(f"Regola {r.istituto}", r.riferimento) for regole in self._regole.values() for r in regole]
        elenco += [(f"Base {b.nome}", b.riferimento) for b in self._basi.values()]
        elenco += [(f"Concorso {c.istituto} -> {c.base}", c.riferimento) for c in self._concorsi]
        elenco += [(f"Fermo {f.fatto}", f.riferimento) for f in self.fermi]
        fiscale = self.fiscale
        elenco += [(f"Categoria {c.nome}", v.riferimento) for c in fiscale.categorie for v in c.cassa_allargata]
        elenco += [(f"Reddito {r.istituto}", r.riferimento) for r in fiscale.redditi]
        elenco += [(f"Pagamento fisiologico {f.istituto}", f.riferimento) for f in fiscale.fisiologici]
        elenco += [(f"Deduzione fiscale {d.istituto}", d.riferimento) for d in fiscale.deduzioni]
        elenco += [(f"Ritenuta {r.istituto}", r.riferimento) for r in fiscale.ritenute]
        elenco += [(f"Conguaglio {c.istituto}", c.riferimento) for c in fiscale.conguagli]
        elenco += [(f"Composizione {c.istituto}", c.riferimento) for c in self._composizioni]
        elenco += [(f"Mappatura {m.istituto} -> {m.sistema}", m.riferimento) for m in self._mappature]
        elenco += [(f"Part-time {t.istituto}", t.riferimento) for t in self._trattamenti_part_time]
        elenco += [(f"Codice F24EP {c.codice}", c.riferimento) for c in self._codici_f24ep]
        elenco += [("Scadenza F24EP", r.riferimento) for r in self._scadenze_f24ep]
        elenco += [("Proroga della scadenza F24EP", r.proroga.riferimento) for r in self._scadenze_f24ep if r.proroga]
        elenco += [(f"Calendario dei festivi {c.anno}", c.riferimento) for c in self._calendari_festivi]
        return elenco

    def _rifiuta_fittizi(self) -> None:
        """Il corpus reale non ammette riferimenti `fittizio:` (ADR 0003)."""
        for soggetto, riferimento in self._riferimenti():
            if any(citazione.startswith(FITTIZIO) for citazione in riferimento.split(" + ")):
                raise ErroreCorpus(f"{soggetto}: riferimento fittizio in un corpus reale: {riferimento!r}")

    def _convalida_denuncia(self) -> None:
        regole = self.denuncia
        massimale = regole.massimale
        if massimale is not None:
            if massimale.base not in self._basi:
                raise ErroreCorpus(f"Massimale: base ignota {massimale.base}")
            if massimale.parametro not in self._parametri:
                raise ErroreCorpus(f"Massimale: parametro ignoto {massimale.parametro}")
        for istituto in regole.conguaglio_annuo:
            if istituto not in self._regole or any(r.maturazione != "mese" for r in self._regole[istituto]):
                raise ErroreCorpus(f"Conguaglio annuo: {istituto} non è una regola sul mese")
        if (regole.persona or massimale or regole.conguaglio_annuo) and not self._basi:
            raise ErroreCorpus("[denuncia] richiede almeno una base imponibile")

    def _istituti_noti(self) -> set[str]:
        """Istituti con una regola, o con la ritenuta e il conguaglio fiscale."""
        fiscale = self.fiscale
        return set(self._regole) | {r.istituto for r in fiscale.ritenute} | {c.istituto for c in fiscale.conguagli}

    def _convalida_composizione(self) -> None:
        noti = self._istituti_noti()
        for indice, dichiarazione in enumerate(self._composizioni):
            if dichiarazione.istituto not in noti:
                raise ErroreCorpus(f"Composizione {dichiarazione.istituto}: istituto ignoto")
            for altra in self._composizioni[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], f"Composizione {dichiarazione.istituto}")
        for indice, mappatura in enumerate(self._mappature):
            soggetto = f"Mappatura {mappatura.istituto} -> {mappatura.sistema}"
            if mappatura.istituto not in noti:
                raise ErroreCorpus(f"{soggetto}: istituto ignoto")
            for altra in self._mappature[indice + 1 :]:
                if (altra.istituto, altra.sistema) == (mappatura.istituto, mappatura.sistema):
                    _vigenze_sovrapposte([mappatura, altra], soggetto)

    def _convalida_part_time(self) -> None:
        noti = self._istituti_noti()
        for indice, dichiarazione in enumerate(self._trattamenti_part_time):
            if dichiarazione.istituto not in noti:
                raise ErroreCorpus(f"Part-time {dichiarazione.istituto}: istituto ignoto")
            for altra in self._trattamenti_part_time[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], f"Part-time {dichiarazione.istituto}")

    def _convalida_catalogo_f24ep(self) -> None:
        for indice, voce in enumerate(self._codici_f24ep):
            for altra in self._codici_f24ep[indice + 1 :]:
                if altra.codice == voce.codice:
                    _vigenze_sovrapposte([voce, altra], f"Codice F24EP {voce.codice}")
        _vigenze_sovrapposte(self._scadenze_f24ep, "Scadenza F24EP")
        anni = [calendario.anno for calendario in self._calendari_festivi]
        for anno in set(anni):
            if anni.count(anno) > 1:
                raise ErroreCorpus(f"Calendario dei festivi {anno}: dichiarato più volte")

    def _convalida_fiscale(self) -> None:
        fiscale = self.fiscale
        nomi = [categoria.nome for categoria in fiscale.categorie]
        if len(set(nomi)) != len(nomi):
            raise ErroreCorpus("Categorie di reddito con lo stesso nome")
        for indice, dichiarazione in enumerate(fiscale.redditi):
            soggetto = f"Reddito {dichiarazione.istituto}"
            if dichiarazione.istituto not in self._regole:
                raise ErroreCorpus(f"{soggetto}: istituto senza regola")
            if dichiarazione.categoria not in nomi:
                raise ErroreCorpus(f"{soggetto}: categoria ignota {dichiarazione.categoria}")
            for altra in fiscale.redditi[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], soggetto)
        for indice, dichiarazione in enumerate(fiscale.fisiologici):
            soggetto = f"Pagamento fisiologico {dichiarazione.istituto}"
            if dichiarazione.istituto not in self._regole:
                raise ErroreCorpus(f"{soggetto}: istituto ignoto")
            for altra in fiscale.fisiologici[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], soggetto)
        for indice, dichiarazione in enumerate(fiscale.deduzioni):
            soggetto = f"Deduzione fiscale {dichiarazione.istituto}"
            if dichiarazione.istituto not in self._regole:
                raise ErroreCorpus(f"{soggetto}: istituto ignoto")
            for altra in fiscale.deduzioni[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], soggetto)
        for gruppo, soggetto in ((fiscale.ritenute, "Ritenuta"), (fiscale.conguagli, "Conguaglio")):
            for indice, regola in enumerate(gruppo):
                if regola.istituto in self._regole:
                    raise ErroreCorpus(f"{soggetto} {regola.istituto}: lo stesso istituto ha anche una regola")
                for altra in gruppo[indice + 1 :]:
                    if altra.istituto == regola.istituto:
                        _vigenze_sovrapposte([regola, altra], f"{soggetto} {regola.istituto}")
        if {r.istituto for r in fiscale.ritenute} & {c.istituto for c in fiscale.conguagli}:
            raise ErroreCorpus("Ritenuta e conguaglio non possono avere lo stesso istituto")
        for regola in fiscale.ritenute:
            soggetto = f"Ritenuta {regola.istituto}"
            ignoti = regola.parametri - self._parametri.keys()
            if ignoti:
                raise ErroreCorpus(f"{soggetto}: parametri ignoti {sorted(ignoti)}")
            for categoria in regola.categorie:
                if categoria not in nomi:
                    raise ErroreCorpus(f"{soggetto}: categoria ignota {categoria}")
        if fiscale.conguagli and not fiscale.ritenute:
            raise ErroreCorpus("Il conguaglio legge le formule della ritenuta: manca [[ritenuta]]")

    def _convalida(self) -> None:
        dipendenze: dict[str, set[str]] = {}
        for istituto, regole in self._regole.items():
            dipendenze[istituto] = set()
            for indice, regola in enumerate(regole):
                for altra in regole[indice + 1 :]:
                    if regola.si_sovrappone(altra):
                        raise ErroreCorpus(f"Istituto {istituto}: regole con vigenze sovrapposte")
                letti = riferimenti(regola.formula)
                ignoti = letti.parametri - self._parametri.keys()
                if regola.divisore:
                    ignoti = ignoti | ({regola.divisore} - self._parametri.keys())
                if ignoti:
                    raise ErroreCorpus(f"Istituto {istituto}: parametri ignoti {sorted(ignoti)}")
                senza_regola = letti.importi - self._regole.keys()
                if senza_regola:
                    raise ErroreCorpus(f"Istituto {istituto}: importi senza regola {sorted(senza_regola)}")
                dipendenze[istituto] |= letti.importi
                self._controlla_livelli(regola, letti.importi)
        self._rifiuta_cicli(dipendenze)

    def _convalida_cassa(self) -> None:
        """Le regole di cassa leggono solo basi e altre regole di cassa, alla data di pagamento."""
        if self._basi and not self.fatto_servizio:
            raise ErroreCorpus("Le basi imponibili richiedono [periodo_dichiarato].servizio, il fatto che dà il servizio")
        cassa: set[str] = set()
        for istituto, regole in self._regole.items():
            for regola in regole:
                basi = riferimenti(regola.formula).basi
                ignote = basi - self._basi.keys()
                if ignote:
                    raise ErroreCorpus(f"Istituto {istituto}: basi ignote {sorted(ignote)}")
                if basi and regola.maturazione not in MATURAZIONI_DI_CASSA:
                    raise ErroreCorpus(
                        f"Regola {istituto}: solo una regola sul periodo dichiarato o sul mese legge una base"
                    )
                if basi:
                    cassa.add(istituto)
        allargato = True
        while allargato:
            allargato = False
            for istituto, regole in self._regole.items():
                if istituto not in cassa and any(riferimenti(r.formula).importi & cassa for r in regole):
                    cassa.add(istituto)
                    allargato = True
        for istituto in cassa:
            for regola in self._regole[istituto]:
                letti = riferimenti(regola.formula)
                if not letti.basi and not letti.importi:
                    raise ErroreCorpus(f"Istituto {istituto}: regole di cassa e regole per competenza insieme")
                if letti.importi - cassa:
                    raise ErroreCorpus(
                        f"Regola {istituto}: una regola di cassa non legge importi per competenza {sorted(letti.importi - cassa)}"
                    )
        self.istituti_di_cassa = frozenset(cassa)
        self._convalida_mese(cassa)
        for indice, concorso in enumerate(self._concorsi):
            if concorso.istituto not in self._regole:
                raise ErroreCorpus(f"Concorso: istituto senza regola {concorso.istituto}")
            if concorso.base not in self._basi:
                raise ErroreCorpus(f"Concorso {concorso.istituto}: base ignota {concorso.base}")
            for altro in self._concorsi[indice + 1 :]:
                if (altro.istituto, altro.base) == (concorso.istituto, concorso.base) and concorso.si_sovrappone(altro):
                    raise ErroreCorpus(f"Concorso {concorso.istituto} -> {concorso.base}: vigenze sovrapposte")

    def _convalida_mese(self, cassa: set[str]) -> None:
        """Una regola sul mese legge il totale del mese: solo basi e altre regole sul mese, mai il contrario."""
        sul_mese = {
            istituto for istituto, regole in self._regole.items() if any(r.maturazione == "mese" for r in regole)
        }
        for istituto in sul_mese:
            if istituto not in cassa:
                raise ErroreCorpus(f"Regola {istituto}: una regola sul mese deve leggere una base")
        for istituto, regole in self._regole.items():
            for regola in regole:
                letti = riferimenti(regola.formula).importi
                if regola.maturazione == "mese" and letti - sul_mese:
                    raise ErroreCorpus(
                        f"Regola {istituto}: una regola sul mese legge solo basi e regole sul mese, non {sorted(letti - sul_mese)}"
                    )
                if regola.maturazione != "mese" and letti & sul_mese:
                    raise ErroreCorpus(
                        f"Regola {istituto}: solo una regola sul mese legge {sorted(letti & sul_mese)}"
                    )
        self.istituti_sul_mese = frozenset(sul_mese)

    def _controlla_livelli(self, regola: Regola, importi: frozenset[str]) -> None:
        """Una frazione non legge il periodo dichiarato, che ne è la somma; l'annuale legge solo fatti e parametri."""
        for nome in importi:
            if regola.maturazione == "annuale":
                raise ErroreCorpus(f"Regola {regola.istituto}: una regola annuale non legge importi")
            for dipendenza in self._regole[nome]:
                if dipendenza.maturazione == "annuale":
                    raise ErroreCorpus(f"Regola {regola.istituto}: non può leggere l'importo annuale {nome}")
                if dipendenza.maturazione in MATURAZIONI_DI_CASSA and regola.maturazione not in MATURAZIONI_DI_CASSA:
                    raise ErroreCorpus(f"Regola {regola.istituto}: una frazione non legge il periodo dichiarato {nome}")

    @staticmethod
    def _rifiuta_cicli(dipendenze: dict[str, set[str]]) -> None:
        conclusi: set[str] = set()

        def visita(istituto: str, percorso: tuple[str, ...]) -> None:
            if istituto in percorso:
                raise ErroreCorpus("Ciclo tra importi: " + " -> ".join((*percorso, istituto)))
            if istituto in conclusi:
                return
            for dipendenza in sorted(dipendenze[istituto]):
                visita(dipendenza, (*percorso, istituto))
            conclusi.add(istituto)

        for istituto in sorted(dipendenze):
            visita(istituto, ())

    def _impronta(self) -> str:
        contenuto = {
            "fatti_periodo_dichiarato": sorted(self.fatti_periodo_dichiarato),
            "servizio": self.fatto_servizio,
            "basi": [[base.nome, base.riferimento] for _, base in sorted(self._basi.items())],
            "concorsi": sorted(
                [c.istituto, c.base, c.dal.isoformat(), c.al.isoformat() if c.al else "", c.misura, c.riferimento]
                for c in self._concorsi
            ),
            "parametri": [
                {
                    "nome": parametro.nome,
                    "vigenze": [
                        [v.dal.isoformat(), str(v.valore), v.riferimento, *([v.al.isoformat()] if v.al else [])]
                        for v in parametro.vigenze
                    ],
                }
                for _, parametro in sorted(self._parametri.items())
            ],
            "regole": sorted(
                [
                    [r.istituto, r.dal.isoformat(), r.versione, r.al.isoformat() if r.al else None,
                     r.riferimento, r.formula, r.applica_se, r.maturazione, r.conteggio, r.divisore, r.decimali]
                    for regole in self._regole.values()
                    for r in regole
                ],
                key=lambda riga: (riga[0], riga[1]),
            ),
        }
        if self.fermi:
            contenuto["fermi"] = sorted(
                [f.fatto, f.caso, f.ambito, f.riferimento, *([f.codice] if f.codice is not None else [])]
                for f in self.fermi
            )
        if self.denuncia != RegoleDenuncia():
            massimale = self.denuncia.massimale
            contenuto["denuncia"] = {
                "persona": self.denuncia.persona,
                "massimale": [massimale.base, massimale.parametro] if massimale else None,
                "conguaglio_annuo": sorted(self.denuncia.conguaglio_annuo),
            }
        if self.fiscale:
            fiscale = self.fiscale
            contenuto["fiscale"] = {
                "categorie": sorted(
                    [c.nome, sorted([v.dal.isoformat(), v.al.isoformat() if v.al else "", v.vale, v.riferimento]
                                    for v in c.cassa_allargata)]
                    for c in fiscale.categorie
                ),
                "redditi": sorted(
                    [r.istituto, r.categoria, r.dal.isoformat(), r.al.isoformat() if r.al else "", r.riferimento]
                    for r in fiscale.redditi
                ),
                "ritenute": sorted(
                    [r.istituto, r.versione, r.dal.isoformat(), r.al.isoformat() if r.al else "", r.riferimento,
                     r.imposta, r.detrazione, sorted(r.categorie), r.detrazione_richiesta]
                    for r in fiscale.ritenute
                ),
                "conguagli": sorted(
                    [c.istituto, c.versione, c.dal.isoformat(), c.al.isoformat() if c.al else "", c.riferimento]
                    for c in fiscale.conguagli
                ),
            }
            if fiscale.fisiologici:
                contenuto["fiscale"]["fisiologici"] = sorted(
                    [f.istituto, f.dal.isoformat(), f.al.isoformat() if f.al else "", f.riferimento]
                    for f in fiscale.fisiologici
                )
            if fiscale.deduzioni:
                contenuto["fiscale"]["deduzioni"] = sorted(
                    [d.istituto, d.dal.isoformat(), d.al.isoformat() if d.al else "", d.riferimento]
                    for d in fiscale.deduzioni
                )
        if self._composizioni:
            contenuto["composizioni"] = sorted(
                [c.istituto, c.dal.isoformat(), c.al.isoformat() if c.al else "", c.natura or "", c.effetto or "",
                 c.destinatario or "", c.canale or "", c.intermedio, c.riferimento]
                for c in self._composizioni
            )
        if self._trattamenti_part_time:
            contenuto["part_time"] = sorted(
                [t.istituto, t.trattamento, t.dal.isoformat(), t.al.isoformat() if t.al else "", t.fatto or "", t.riferimento]
                for t in self._trattamenti_part_time
            )
        if self._mappature:
            contenuto["mappature"] = sorted(
                [m.istituto, m.sistema, m.codice, m.dal.isoformat(), m.al.isoformat() if m.al else "", m.riferimento]
                for m in self._mappature
            )
        if self._codici_f24ep:
            contenuto["codici_f24ep"] = sorted(
                [c.codice, c.sezione, c.codice_campo, c.estremi, c.rif_a, c.rif_b, c.modalita, c.limite_credito,
                 c.dal.isoformat(), c.al.isoformat() if c.al else "", c.riferimento]
                for c in self._codici_f24ep
            )
        if self._scadenze_f24ep:
            contenuto["scadenze_f24ep"] = sorted(
                [r.dal.isoformat(), r.al.isoformat() if r.al else "", r.giorno, r.riferimento,
                 [r.proroga.mese, r.proroga.dal_giorno, r.proroga.al_giorno, r.proroga.fonte, r.proroga.riferimento]
                 if r.proroga else None]
                for r in self._scadenze_f24ep
            )
        if self._calendari_festivi:
            contenuto["calendari_festivi"] = sorted(
                [c.anno, sorted(g.isoformat() for g in c.giorni), c.riferimento] for c in self._calendari_festivi
            )
        testo = json.dumps(contenuto, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:16]

    def istituti(self) -> list[str]:
        return sorted(self._regole)

    def parametro(self, nome: str) -> Parametro:
        return self._parametri[nome]

    def basi(self) -> tuple[Base, ...]:
        return tuple(base for _, base in sorted(self._basi.items()))

    def concorso(self, istituto: str, base: str, giorno: date) -> Concorso | None:
        """Dichiarazione vigente alla data di pagamento; None se l'istituto non dichiara nulla."""
        for concorso in self._concorsi:
            if (concorso.istituto, concorso.base) == (istituto, base) and concorso.copre(giorno):
                return concorso
        return None

    def categoria_reddito(self, nome: str) -> CategoriaReddito:
        for categoria in self.fiscale.categorie:
            if categoria.nome == nome:
                return categoria
        raise ErroreCorpus(f"Categoria di reddito ignota: {nome}")

    def reddito(self, istituto: str, giorno: date) -> DichiarazioneReddito | None:
        """Categoria dichiarata dall'istituto alla data; None se non ne dichiara."""
        return _vigente([r for r in self.fiscale.redditi if r.istituto == istituto], giorno)

    def pagamento_fisiologico(self, istituto: str, giorno: date) -> DichiarazionePagamentoFisiologico | None:
        """Dichiarazione vigente alla data di pagamento; None se l'istituto non dichiara il pagamento fisiologico."""
        return _vigente([f for f in self.fiscale.fisiologici if f.istituto == istituto], giorno)

    def deduzione_fiscale(self, istituto: str, giorno: date) -> DichiarazioneDeduzione | None:
        """Dichiarazione vigente alla data di pagamento; None se l'importo dell'istituto non riduce l'imponibile fiscale."""
        return _vigente([d for d in self.fiscale.deduzioni if d.istituto == istituto], giorno)

    def regola_ritenuta(self, giorno: date) -> RegolaRitenuta | None:
        return _vigente(self.fiscale.ritenute, giorno)

    def regola_conguaglio(self, giorno: date) -> RegolaConguaglio | None:
        return _vigente(self.fiscale.conguagli, giorno)

    def composizione(self, istituto: str, giorno: date) -> DichiarazioneComposizione | None:
        """Dichiarazione di composizione vigente alla data; None se l'istituto non ne dichiara."""
        return _vigente([c for c in self._composizioni if c.istituto == istituto], giorno)

    def trattamento_part_time(self, istituto: str, giorno: date) -> DichiarazioneTrattamentoPartTime | None:
        """Trattamento nel part-time vigente alla data; None se l'istituto non lo dichiara."""
        return _vigente([t for t in self._trattamenti_part_time if t.istituto == istituto], giorno)

    def mappatura(
        self, istituto: str, sistema: str, data_pagamento: date, anno_imposta: int | None = None
    ) -> MappaturaEsterna | None:
        """Codice del sistema esterno: per anno d'imposta, al 31 dicembre, se l'importo lo porta; altrimenti per data di pagamento."""
        giorno = date(anno_imposta, 12, 31) if anno_imposta is not None else data_pagamento
        return _vigente([m for m in self._mappature if (m.istituto, m.sistema) == (istituto, sistema)], giorno)

    def codice_f24ep(self, codice: str, giorno: date) -> CodiceF24EP | None:
        """Voce del catalogo vigente alla data; None se il codice non è dichiarato."""
        return _vigente([c for c in self._codici_f24ep if c.codice == codice], giorno)

    def regola_scadenza_f24ep(self, giorno: date) -> RegolaScadenzaF24EP | None:
        """Regola di scadenza vigente alla data; None se non ce n'è."""
        return _vigente(self._scadenze_f24ep, giorno)

    def calendario_festivi(self, anno: int) -> CalendarioFestivi | None:
        return next((c for c in self._calendari_festivi if c.anno == anno), None)

    def regola_iniziata(self, istituto: str, giorno: date) -> bool:
        """Vero se l'istituto ha già una regola decorrente a quella data, anche se oggi scaduta."""
        return any(regola.dal <= giorno for regola in self._regole.get(istituto, ()))

    def regole_annuali(self) -> list[Regola]:
        """Una regola annuale per istituto: la vigente si sceglie sull'ultimo giorno di servizio."""
        trovate = {}
        for istituto, regole in sorted(self._regole.items()):
            for regola in regole:
                if regola.maturazione == "annuale":
                    trovate.setdefault(istituto, regola)
        return list(trovate.values())

    def tipi_fatto(self) -> tuple[str, ...]:
        """I tipi di fatto che possono dividere il mese in frazioni."""
        tipi = set(self.fatti_periodo_dichiarato) | {FATTO_PART_TIME, FATTO_TIPO_PART_TIME}
        tipi |= {t.fatto for t in self._trattamenti_part_time if t.fatto}
        for regole in self._regole.values():
            for regola in regole:
                tipi |= riferimenti(regola.formula).fatti
                if regola.applica_se and regola.maturazione != "annuale":
                    tipi.add(regola.fatto_condizione)
        return tuple(sorted(tipi))

    def firma_giorno(self, giorno: date) -> tuple:
        """Regole e parametri vigenti in un giorno: se cambia, il mese si divide."""
        parametri = []
        for nome, parametro in sorted(self._parametri.items()):
            vigenza = parametro._vigente(giorno)
            parametri.append((nome, vigenza.dal if vigenza else None))
        regole = tuple(
            (regola.istituto, regola.dal)
            for _, gruppo in sorted(self._regole.items())
            for regola in gruppo
            if regola.copre(giorno)
        )
        return (tuple(parametri), regole)

    def regola_per(self, istituto: str, competenza) -> Regola | None:
        """Regola che copre tutto il mese o periodo; None se l'istituto non ne ha alcuna."""
        presenti = [
            regola
            for regola in self._regole.get(istituto, [])
            if any(regola.copre(giorno) for giorno in competenza.giorni())
        ]
        if not presenti:
            return None
        if len(presenti) > 1 or not all(presenti[0].copre(giorno) for giorno in competenza.giorni()):
            raise ValiditaNonUniforme(f"Istituto {istituto}: la regola cambia dentro {competenza}")
        return presenti[0]

    @classmethod
    def da_toml(cls, testo: str, reale: bool = False) -> "Corpus":
        """`reale` vero: il corpus produce importi veri e rifiuta i riferimenti fittizi (ADR 0003)."""
        try:
            dati = tomllib.loads(testo)
            parametri = tuple(_parametro_da_toml(voce) for voce in dati.get("parametro", []))
            regole = tuple(_regola_da_toml(voce) for voce in dati.get("regola", []))
            basi = tuple(Base(voce["nome"], voce["riferimento"]) for voce in dati.get("base", []))
            concorsi = tuple(concorso for voce in dati.get("concorso", []) for concorso in _concorsi_da_toml(voce))
            fermi = tuple(
                Fermo(voce["fatto"], voce["caso"], voce["ambito"], voce["riferimento"], voce.get("codice"))
                for voce in dati.get("fermo", [])
            )
            denuncia = _denuncia_da_toml(dati.get("denuncia", {}))
            fiscale = _fiscale_da_toml(dati)
            composizioni = tuple(_composizione_da_toml(voce) for voce in dati.get("composizione", []))
            mappature = tuple(_mappatura_da_toml(voce) for voce in dati.get("mappatura", []))
            trattamenti_part_time = tuple(
                DichiarazioneTrattamentoPartTime(
                    istituto=voce["istituto"],
                    trattamento=voce["trattamento"],
                    dal=_data(voce["dal"], "dal"),
                    riferimento=voce["riferimento"],
                    al=_data(voce["al"], "al") if "al" in voce else None,
                    fatto=voce.get("fatto"),
                )
                for voce in dati.get("part_time", [])
            )
            codici_f24ep = tuple(_codice_f24ep_da_toml(voce) for voce in dati.get("codice_f24ep", []))
            scadenze_f24ep = tuple(_scadenza_f24ep_da_toml(voce) for voce in dati.get("scadenza_f24ep", []))
            calendari_festivi = tuple(
                CalendarioFestivi(
                    voce["anno"],
                    tuple(_data(giorno, "giorni") for giorno in voce["giorni"]),
                    voce["riferimento"],
                )
                for voce in dati.get("calendario_festivi", [])
            )
        except (tomllib.TOMLDecodeError, KeyError, TypeError, AttributeError) as errore:
            raise ErroreCorpus(f"Corpus TOML non valido: {errore!r}") from errore
        periodo = dati.get("periodo_dichiarato", {})
        return cls(
            parametri,
            regole,
            tuple(periodo.get("fatti", ())),
            basi,
            concorsi,
            periodo.get("servizio"),
            fermi=fermi,
            denuncia=denuncia,
            reale=reale,
            fiscale=fiscale,
            composizioni=composizioni,
            mappature=mappature,
            codici_f24ep=codici_f24ep,
            scadenze_f24ep=scadenze_f24ep,
            calendari_festivi=calendari_festivi,
            trattamenti_part_time=trattamenti_part_time,
        )

    @classmethod
    def carica(cls, percorso: str | Path, reale: bool = False) -> "Corpus":
        return cls.da_toml(Path(percorso).read_text(encoding="utf-8"), reale=reale)


def _data(valore: object, campo: str) -> date:
    if isinstance(valore, datetime) or not isinstance(valore, date):
        raise ErroreCorpus(f"{campo}: serve una data, trovato {valore!r}")
    return valore


def _composizione_da_toml(voce: dict) -> DichiarazioneComposizione:
    return DichiarazioneComposizione(
        istituto=voce["istituto"],
        dal=_data(voce["dal"], "dal"),
        riferimento=voce["riferimento"],
        natura=voce.get("natura"),
        effetto=voce.get("effetto"),
        destinatario=voce.get("destinatario"),
        canale=voce.get("canale"),
        intermedio=voce.get("intermedio", False),
        al=_data(voce["al"], "al") if "al" in voce else None,
    )


def _codice_f24ep_da_toml(voce: dict) -> CodiceF24EP:
    return CodiceF24EP(
        codice=voce["codice"],
        sezione=voce["sezione"],
        codice_campo=voce["codice_campo"],
        estremi=voce["estremi"],
        rif_a=voce["rif_a"],
        rif_b=voce["rif_b"],
        modalita=voce["modalita"],
        limite_credito=voce.get("limite_credito", "nessuno"),
        dal=_data(voce["dal"], "dal"),
        riferimento=voce["riferimento"],
        al=_data(voce["al"], "al") if "al" in voce else None,
    )


def _scadenza_f24ep_da_toml(voce: dict) -> RegolaScadenzaF24EP:
    proroga = voce.get("proroga")
    return RegolaScadenzaF24EP(
        dal=_data(voce["dal"], "dal"),
        riferimento=voce["riferimento"],
        giorno=voce["giorno"],
        proroga=(
            ProrogaScadenza(
                proroga["mese"], proroga["dal_giorno"], proroga["al_giorno"], proroga.get("fonte"), proroga["riferimento"]
            )
            if proroga
            else None
        ),
        al=_data(voce["al"], "al") if "al" in voce else None,
    )


def _mappatura_da_toml(voce: dict) -> MappaturaEsterna:
    return MappaturaEsterna(
        istituto=voce["istituto"],
        sistema=voce["sistema"],
        codice=voce["codice"],
        dal=_data(voce["dal"], "dal"),
        riferimento=voce["riferimento"],
        al=_data(voce["al"], "al") if "al" in voce else None,
    )


def _parametro_da_toml(voce: dict) -> Parametro:
    vigenze = []
    for vigenza in voce["vigenza"]:
        if not isinstance(vigenza["valore"], str):
            raise ErroreCorpus(f"Parametro {voce['nome']}: il valore va scritto come testo")
        try:
            valore = Decimal(vigenza["valore"])
        except InvalidOperation as errore:
            raise ErroreCorpus(f"Parametro {voce['nome']}: valore non numerico") from errore
        if not valore.is_finite():
            raise ErroreCorpus(f"Parametro {voce['nome']}: valore non finito")
        al = _data(vigenza["al"], "al") if "al" in vigenza else None
        vigenze.append(VigenzaParametro(_data(vigenza["dal"], "dal"), valore, vigenza["riferimento"], al))
    return Parametro(voce["nome"], tuple(vigenze))


def _denuncia_da_toml(voce: dict) -> RegoleDenuncia:
    massimale = voce.get("massimale")
    return RegoleDenuncia(
        persona=voce.get("persona"),
        massimale=Massimale(massimale["base"], massimale["parametro"]) if massimale else None,
        conguaglio_annuo=tuple(voce.get("conguaglio_annuo", ())),
    )


def _fiscale_da_toml(dati: dict) -> RegoleFiscali:
    categorie = tuple(
        CategoriaReddito(
            voce["nome"],
            tuple(
                CassaAllargata(
                    _data(cassa["dal"], "dal"),
                    cassa["vale"],
                    cassa["riferimento"],
                    _data(cassa["al"], "al") if "al" in cassa else None,
                )
                for cassa in voce.get("cassa_allargata", [])
            ),
        )
        for voce in dati.get("categoria_reddito", [])
    )
    redditi = tuple(
        DichiarazioneReddito(
            voce["istituto"],
            voce["categoria"],
            _data(voce["dal"], "dal"),
            voce["riferimento"],
            _data(voce["al"], "al") if "al" in voce else None,
        )
        for voce in dati.get("reddito", [])
    )
    ritenute = tuple(
        RegolaRitenuta(
            istituto=voce["istituto"],
            versione=voce["versione"],
            dal=_data(voce["dal"], "dal"),
            riferimento=voce["riferimento"],
            imposta=voce["imposta"],
            detrazione=voce["detrazione"],
            categorie=tuple(voce["categorie"]),
            detrazione_richiesta=voce["detrazione_richiesta"],
            al=_data(voce["al"], "al") if "al" in voce else None,
        )
        for voce in dati.get("ritenuta", [])
    )
    conguagli = tuple(
        RegolaConguaglio(
            voce["istituto"],
            voce["versione"],
            _data(voce["dal"], "dal"),
            voce["riferimento"],
            _data(voce["al"], "al") if "al" in voce else None,
        )
        for voce in dati.get("conguaglio", [])
    )
    fisiologici = tuple(
        DichiarazionePagamentoFisiologico(
            voce["istituto"],
            _data(voce["dal"], "dal"),
            voce["riferimento"],
            _data(voce["al"], "al") if "al" in voce else None,
        )
        for voce in dati.get("pagamento_fisiologico", [])
    )
    deduzioni = tuple(
        DichiarazioneDeduzione(
            voce["istituto"],
            _data(voce["dal"], "dal"),
            voce["riferimento"],
            _data(voce["al"], "al") if "al" in voce else None,
        )
        for voce in dati.get("deduzione_fiscale", [])
    )
    return RegoleFiscali(categorie, redditi, ritenute, conguagli, fisiologici, deduzioni)


def _concorsi_da_toml(voce: dict) -> list[Concorso]:
    if not voce["basi"]:
        raise ErroreCorpus(f"Concorso {voce['istituto']}: basi obbligatorie")
    return [
        Concorso(
            istituto=voce["istituto"],
            base=base,
            misura=voce["misura"],
            dal=_data(voce["dal"], "dal"),
            al=_data(voce["al"], "al") if "al" in voce else None,
            riferimento=voce["riferimento"],
        )
        for base in voce["basi"]
    ]


def _regola_da_toml(voce: dict) -> Regola:
    return Regola(
        istituto=voce["istituto"],
        versione=voce["versione"],
        dal=_data(voce["dal"], "dal"),
        al=_data(voce["al"], "al") if "al" in voce else None,
        riferimento=voce["riferimento"],
        formula=voce["formula"],
        descrizione=voce.get("descrizione", ""),
        applica_se=voce.get("applica_se"),
        maturazione=voce.get("maturazione", ""),
        conteggio=voce.get("conteggio"),
        divisore=voce.get("divisore"),
        decimali=voce.get("decimali"),
    )
