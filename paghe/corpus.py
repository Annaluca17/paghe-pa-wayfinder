"""Corpus di regole e parametri, con vigenza, fonte e versione."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from .calendario import lunedi_dell_angelo
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


# `onere`: come `giorni`, ma l'importo e' a carico dell'ente: non e' reddito della persona e non concorre a nessuna base.
MATURAZIONI = {"giorni", "evento", "periodo", "mese", "annuale", "onere"}
# Maturazioni che leggono le basi della denuncia: sul periodo dichiarato o sul totale del mese.
MATURAZIONI_DI_CASSA = {"periodo", "mese"}
CONTEGGI = {"lun_sab", "calendario"}
MISURE = {"intero", "parziale", "escluso"}
AMBITI_FERMO = {"calcolo", "denuncia", "vista"}
FITTIZIO = "fittizio:"
# Codice di V livello del piano dei conti finanziario (allegato 6/1 D.Lgs. 118/2011), spesa o entrata (ADR 0031).
PIANO_DEI_CONTI = re.compile(r"[UE]\.\d\.\d{2}\.\d{2}\.\d{2}\.\d{3}")
# Dichiarazione di composizione (ADR 0025): valori ammessi.
NATURE = frozenset({
    "retribuzione", "ritenuta", "addizionale", "contributo_lavoratore", "contributo_ente",
    "rata_730", "rimborso_730", "credito_sostituto", "trattenuta_terzi", "irap", "imponibile_sostitutivo",
})
# Quota di reddito tassata con un'imposta sostitutiva (ADR 0035): resta nell'esito pagato, perché il conguaglio la legge,
# ma non muove denaro: nessun effetto sul netto, nessun destinatario, nessun canale.
NATURA_IMPONIBILE_SOSTITUTIVO = "imponibile_sostitutivo"
EFFETTI = frozenset({"piu", "meno", "nessuno"})
DESTINATARI = frozenset({"beneficiario", "terzo"})
CANALI = frozenset({"accredito", "f24ep", "bonifico"})
# Catalogo dei codici F24EP (ticket #54): valori ammessi.
SEZIONI_F24EP = frozenset({"F", "I", "R", "S", "N", "Q", "W", "G", "P", "5"})
CODICE_CAMPO_F24EP = frozenset({"nessuno", "regione", "catastale", "provincia"})
ESTREMI_F24EP = frozenset({"nessuno", "facoltativo"})
RIF_A_F24EP = frozenset({"nessuno", "mese_pagamento", "periodo_inizio", "mese_anno_pagamento"})
RIF_B_F24EP = frozenset({"nessuno", "anno_pagamento", "anno_imposta", "periodo_fine"})
MODALITA_F24EP = frozenset({"debito", "debito_credito"})
LIMITI_CREDITO_F24EP = frozenset({"nessuno", "non_modellato"})
FONTI_SCADENZA = frozenset({"norma", "prassi"})
# Trattamento nel part-time (ADR 0026): proporzionale si riduce, intero no, da_integrativo lo fissa l'ente con un input da atto.
TRATTAMENTI_PART_TIME = frozenset({"proporzionale", "intero", "da_integrativo"})
# Trattamento di un istituto nella malattia (ADR 0042): `decurtata` si toglie nei primi giorni dell'episodio, `intera` no;
# in entrambi i casi la percentuale del periodo si applica.
TRATTAMENTI_MALATTIA = frozenset({"decurtata", "intera"})


@dataclass(frozen=True)
class VigenzaParametro:
    dal: date
    valore: Decimal
    riferimento: str
    al: date | None = None
    applicabile_dal: date | None = None  # da quando si paga (ADR 0041); assente = vale dalla decorrenza


@dataclass(frozen=True)
class Parametro:
    """Un parametro annuale, come una soglia INPS, chiude l'ultima vigenza con `al`: oltre, il calcolo si ferma.

    Un importo del CCNL ha due date (ADR 0041): `dal` è la decorrenza, `applicabile_dal` la data da cui un pagamento lo
    usa. Una vigenza non ancora applicabile alla data di pagamento si salta e vale la precedente.
    """

    nome: str
    vigenze: tuple[VigenzaParametro, ...]

    def __post_init__(self) -> None:
        if not self.vigenze:
            raise ErroreCorpus(f"Parametro {self.nome}: nessuna vigenza")
        for vigenza in self.vigenze:
            _riferimento_obbligatorio(vigenza.riferimento, f"Parametro {self.nome}")
            if vigenza.al is not None and vigenza.al < vigenza.dal:
                raise ErroreCorpus(f"Parametro {self.nome}: vigenza invertita")
            if vigenza.applicabile_dal is not None and vigenza.applicabile_dal < vigenza.dal:
                raise ErroreCorpus(f"Parametro {self.nome}: applicabilità prima della decorrenza")
        decorrenze = [vigenza.dal for vigenza in self.vigenze]
        if len(set(decorrenze)) != len(decorrenze):
            raise ErroreCorpus(f"Parametro {self.nome}: decorrenze duplicate")
        ordinate = tuple(sorted(self.vigenze, key=lambda v: v.dal))
        if any(vigenza.al is not None for vigenza in ordinate[:-1]):
            raise ErroreCorpus(f"Parametro {self.nome}: solo l'ultima vigenza può avere una fine")
        object.__setattr__(self, "vigenze", ordinate)

    def _vigente(self, giorno: date, pagamento: date | None = None) -> VigenzaParametro | None:
        """La vigenza del giorno; con `pagamento`, solo tra quelle già applicabili a quella data."""
        trovata = None
        for vigenza in self.vigenze:
            if vigenza.dal <= giorno and (
                pagamento is None or vigenza.applicabile_dal is None or vigenza.applicabile_dal <= pagamento
            ):
                trovata = vigenza
        if trovata is not None and trovata.al is not None and giorno > trovata.al:
            return None
        return trovata

    def vigenza_per(self, competenza: Mese, pagamento: date | None = None) -> VigenzaParametro:
        inizio = self._vigente(competenza.primo_giorno, pagamento)
        fine = self._vigente(competenza.ultimo_giorno, pagamento)
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
    anche_se: tuple[str, ...] = ()

    @property
    def condizioni_aggiuntive(self) -> tuple[tuple[str, str], ...]:
        """Le altre condizioni `tipo=codice` che devono valere insieme ad `applica_se` (ticket #73, art. 86 TUEL)."""
        return tuple(tuple(condizione.split("=", 1)) for condizione in self.anche_se)

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
        self._controlla_condizioni_aggiuntive()
        self._controlla_maturazione()
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"Regola {self.istituto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"Regola {self.istituto}: vigenza invertita")
        if riferimenti(self.formula).fisco:
            raise ErroreCorpus(f"Regola {self.istituto}: `fisco.` vale solo per le formule di [[ritenuta]]")

    def _controlla_condizioni_aggiuntive(self) -> None:
        if not self.anche_se:
            return
        soggetto = f"Regola {self.istituto}"
        if not self.applica_se:
            raise ErroreCorpus(f"{soggetto}: anche_se richiede applica_se")
        if not isinstance(self.anche_se, tuple):
            raise ErroreCorpus(f"{soggetto}: anche_se e' un elenco di condizioni tipo=codice")
        for condizione in self.anche_se:
            tipo, uguale, codice = condizione.partition("=") if isinstance(condizione, str) else ("", "", "")
            if not uguale or not tipo or not codice or tipo != tipo.strip() or codice != codice.strip():
                raise ErroreCorpus(f"{soggetto}: condizione anche_se non valida, {condizione!r}: va scritta tipo=codice")

    def _controlla_maturazione(self) -> None:
        soggetto = f"Regola {self.istituto}"
        if self.maturazione not in MATURAZIONI:
            raise ErroreCorpus(f"{soggetto}: maturazione obbligatoria, una di {sorted(MATURAZIONI)}")
        a_quota = self.maturazione in ("giorni", "annuale", "onere")
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
    """Base imponibile: insieme degli importi pagati su cui si calcola una contribuzione (ADR 0005).

    Con `massimale`, il nome di un parametro annuo, la base di ogni mese si limita a cio' che resta sotto il massimale,
    sommando i mesi dell'anno nello stesso ente (ticket #73, gestione separata). Un altro committente ferma con un fermo.

    Con `esclusione`, il tipo di un fatto categoriale del rapporto, i pagamenti fatti mentre il fatto vale non entrano
    nella base; il codice del fatto e' il motivo e deve essere uno di `motivi_esclusione` (ticket #81, IRAP).
    """

    nome: str
    riferimento: str
    massimale: str | None = None
    esclusione: str | None = None
    motivi_esclusione: tuple[str, ...] = ()
    # Retribuzione virtuale (ADR 0042): la base conta gli importi come se la malattia non li avesse ridotti.
    retribuzione_virtuale: bool = False

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Base {self.nome}")
        if self.esclusione is not None and not self.motivi_esclusione:
            raise ErroreCorpus(f"Base {self.nome}: l'esclusione vuole l'elenco dei motivi ammessi")
        if self.massimale is not None and (not isinstance(self.massimale, str) or not self.massimale.strip()):
            raise ErroreCorpus(f"Base {self.nome}: il massimale e' il nome di un parametro")


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
    Con `manca` scatta al contrario quando il fatto non c'è: serve `se`, la condizione `tipo` o `tipo=codice` su un altro
    fatto che dice per chi quel fatto è obbligatorio (ticket #73, fascia del segretario). Nessun titolo è nominato nel motore.
    Con `manca`, `valori` limita i codici ammessi del fatto categoriale. Con `solo_se = "tipo=codice"` (da solo) scatta se il
    fatto c'è in un giorno in cui `tipo` ha un altro codice: il fatto è fuori dal suo regime. I giorni senza `tipo` non contano.
    """

    fatto: str
    caso: str
    ambito: str
    riferimento: str
    codice: str | None = None
    se: str | None = None
    manca: bool = False
    valori: tuple[str, ...] | None = None
    solo_se: str | None = None

    def __post_init__(self) -> None:
        soggetto = f"Fermo {self.fatto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.codice is not None and (not isinstance(self.codice, str) or not self.codice.strip()
                                        or self.codice != self.codice.strip()):
            raise ErroreCorpus(f"{soggetto}: codice non valido, {self.codice!r}")
        if not self.caso.strip():
            raise ErroreCorpus(f"{soggetto}: il caso va nominato")
        if self.manca != (self.se is not None):
            raise ErroreCorpus(f"{soggetto}: `manca` e `se` vanno indicati insieme")
        if self.manca and self.codice is not None:
            raise ErroreCorpus(f"{soggetto}: `manca` non si combina con `codice`")
        if self.valori is not None and (not self.manca or not self.valori or not all(
                isinstance(v, str) and v.strip() and v == v.strip() for v in self.valori)):
            raise ErroreCorpus(f"{soggetto}: `valori` vale solo con `manca` ed e' un elenco di codici non vuoti")
        if self.solo_se is not None:
            if self.manca or self.codice is not None:
                raise ErroreCorpus(f"{soggetto}: `solo_se` non si combina con `manca` né con `codice`")
            tipo, uguale, codice = self.solo_se.partition("=") if isinstance(self.solo_se, str) else ("", "", "")
            if not uguale or not tipo or not codice or tipo != tipo.strip() or codice != codice.strip():
                raise ErroreCorpus(f"{soggetto}: condizione `solo_se` non valida, {self.solo_se!r}")
        if self.manca and self.ambito == "vista":
            raise ErroreCorpus(f"{soggetto}: `manca` vale per l'ambito calcolo o denuncia, non per la vista")
        if self.se is not None and (not isinstance(self.se, str) or not self.se.strip() or self.se != self.se.strip()
                                    or self.se.startswith("=") or self.se.endswith("=")):
            raise ErroreCorpus(f"{soggetto}: condizione `se` non valida, {self.se!r}")
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
class RegolaMalattia:
    """Regole della malattia (ADR 0042): decurtazione dei primi giorni, finestra del comporto e fasce di retribuzione.

    `fasce` sono coppie (giorni di malattia, percentuale) in ordine: oltre l'ultima fascia l'assenza non è retribuita.
    I mesi del contratto sono contati a 30 giorni (9 mesi = 270 giorni): prassi, da verificare.
    """

    dal: date
    riferimento: str
    giorni_decurtati: int
    anni_finestra: int
    fasce: tuple[tuple[int, Decimal], ...]
    al: date | None = None

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, "Malattia")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus("Malattia: vigenza invertita")
        if self.giorni_decurtati < 0 or self.anni_finestra < 1 or not self.fasce:
            raise ErroreCorpus("Malattia: giorni decurtati, anni della finestra e fasce non validi")
        if any(giorni < 1 or not 0 <= percentuale <= 100 for giorni, percentuale in self.fasce):
            raise ErroreCorpus("Malattia: ogni fascia ha giorni positivi e percentuale tra 0 e 100")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)

    def percentuale(self, giorni_comporto: int) -> Decimal:
        """Percentuale spettante dal giorno di malattia numero `giorni_comporto` nella finestra; 0 oltre le fasce."""
        limite = 0
        for giorni, percentuale in self.fasce:
            limite += giorni
            if giorni_comporto <= limite:
                return percentuale
        return Decimal(0)


@dataclass(frozen=True)
class DichiarazioneMalattia:
    """L'istituto dichiara come si comporta nella malattia (ADR 0042), con date e fonte."""

    istituto: str
    trattamento: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Malattia {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        if self.trattamento not in TRATTAMENTI_MALATTIA:
            raise ErroreCorpus(f"{soggetto}: trattamento uno di {sorted(TRATTAMENTI_MALATTIA)}")

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
class DichiarazioneMensilitaAggiuntiva:
    """L'istituto dichiara di essere una mensilità aggiuntiva (art. 23 c. 2 lett. b D.P.R. 600/1973), con date e fonte.

    `mese_pagamento`, `giorno_dal` e `giorno_al` sono la finestra in cui la fonte vuole il pagamento per chi è in servizio:
    fuori dalla finestra la proposta porta un avviso, non un fermo (ADR 0038).
    """

    istituto: str
    dal: date
    riferimento: str
    al: date | None = None
    mese_pagamento: int | None = None
    giorno_dal: int | None = None
    giorno_al: int | None = None

    def __post_init__(self) -> None:
        soggetto = f"Mensilità aggiuntiva {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        finestra = (self.mese_pagamento, self.giorno_dal, self.giorno_al)
        if any(valore is not None for valore in finestra):
            if any(type(valore) is not int for valore in finestra):
                raise ErroreCorpus(f"{soggetto}: la finestra di pagamento chiede mese_pagamento, giorno_dal e giorno_al")
            if not 1 <= self.mese_pagamento <= 12 or not 1 <= self.giorno_dal <= self.giorno_al <= 31:
                raise ErroreCorpus(f"{soggetto}: finestra di pagamento non valida")

    def nella_finestra(self, giorno: date) -> bool:
        """Vero se la data cade nella finestra di pagamento, o se la dichiarazione non ne ha una."""
        if self.mese_pagamento is None:
            return True
        return giorno.month == self.mese_pagamento and self.giorno_dal <= giorno.day <= self.giorno_al


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


PERIODI_FISCALI = frozenset({"imponibile", "periodi", "giorni", "giorni_anno", "figli", "reddito_annuo", "quota_minimo"})


@dataclass(frozen=True)
class RegolaRitenuta:
    """Ritenuta del pagamento (ADR 0019), con scaglioni annui ragguagliati al periodo di paga.

    Le due formule leggono parametri e due valori che dà il motore: `fisco.imponibile`, il reddito del
    periodo di paga (o dell'anno, nel conguaglio), e `fisco.periodi`, i periodi di paga dell'anno
    (12 per il mese, 1 per il conguaglio). `detrazione` si applica solo con la dichiarazione del
    sostituito che chiede `detrazione_richiesta`. `detrazione_automatica` si applica sempre (l'ulteriore
    detrazione che il sostituto riconosce in via automatica) e vale 0 se la regola non la dichiara.
    `fisco.giorni` e `fisco.giorni_anno` servono a rapportare le detrazioni al periodo: nella ritenuta del mese sono i
    giorni del mese e i giorni dell'anno, nel conguaglio i giorni di servizio dell'anno e i giorni dell'anno.
    `fisco.reddito_annuo` è il reddito a cui si applicano le fasce delle detrazioni (ADR 0039): nella ritenuta la
    proiezione dell'anno (pagato, mese, mesi che restano, tredicesima), nel conguaglio l'imponibile dell'anno. Una formula
    che lo legge non divide per `fisco.periodi`: la quota del periodo è già nei giorni. `fisco.quota_minimo` è la quota
    da dare a un minimo annuo: 1 al conguaglio, giorni del mese su giorni dell'anno nella ritenuta.
    Carichi di famiglia (ADR 0033): `carichi_coniuge`, `carichi_figlio` e `carichi_ascendente` sono la detrazione ANNUA
    per un familiare a carico al 100%, nelle stesse variabili, più `fisco.figli`, il numero dei figli che danno diritto
    nello stesso mese (aumenta la soglia dei figli). Il coniuge vale anche per il figlio in luogo del coniuge. Il motore
    le applica per mese, per percentuale e per familiare, un dodicesimo ciascuna, senza la dichiarazione del sostituito.
    Carica elettiva (ADR 0019, ticket #97): `detrazione_carica_elettiva` è la detrazione dell'art. 13 c. 5, nelle stesse
    variabili, intera al conguaglio (non rapportata ai giorni) e un dodicesimo per pagamento nella ritenuta. Spetta se
    il reddito ha una delle `categorie_detrazione_carica_elettiva`; `detrazione` (c. 1) spetta se ha una delle
    `categorie_detrazione` (vuote: sempre, come prima). Le due non si cumulano: con la dichiarazione, il motore applica
    la più alta, o quella scelta dalla dichiarazione.
    La regola copre solo le `categorie` elencate.
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
    detrazione_automatica: str = "0"
    categorie_detrazione_automatica: tuple[str, ...] = ()
    carichi_coniuge: str = "0"
    carichi_figlio: str = "0"
    carichi_ascendente: str = "0"
    categorie_detrazione: tuple[str, ...] = ()
    detrazione_carica_elettiva: str = "0"
    categorie_detrazione_carica_elettiva: tuple[str, ...] = ()

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
        for formula in (
            self.imposta, self.detrazione, self.detrazione_automatica,
            self.carichi_coniuge, self.carichi_figlio, self.carichi_ascendente, self.detrazione_carica_elettiva,
        ):
            letti = riferimenti(formula)
            if letti.fatti or letti.importi or letti.basi:
                raise ErroreCorpus(f"{soggetto}: la formula legge solo parametri e fisco, non fatti, importi o basi")
            ignoti = letti.fisco - PERIODI_FISCALI
            if ignoti:
                raise ErroreCorpus(f"{soggetto}: fisco ignoto {sorted(ignoti)}; ammessi {sorted(PERIODI_FISCALI)}")

    @property
    def usa_la_proiezione(self) -> bool:
        """Una formula delle detrazioni legge `fisco.reddito_annuo`: la ritenuta deve proiettare il reddito dell'anno."""
        return any(
            "reddito_annuo" in riferimenti(formula).fisco
            for formula in (
                self.detrazione, self.detrazione_automatica, self.carichi_coniuge, self.carichi_figlio,
                self.carichi_ascendente, self.detrazione_carica_elettiva,
            )
        )

    @property
    def parametri(self) -> frozenset[str]:
        return (
            riferimenti(self.imposta).parametri
            | riferimenti(self.detrazione).parametri
            | riferimenti(self.detrazione_automatica).parametri
            | riferimenti(self.carichi_coniuge).parametri
            | riferimenti(self.carichi_figlio).parametri
            | riferimenti(self.carichi_ascendente).parametri
            | riferimenti(self.detrazione_carica_elettiva).parametri
        )


SUFFISSO_RESTO = "_resto"
SUFFISSO_INTERESSE = "_interesse"
SUFFISSO_NON_TRATTENUTO = "_non_trattenuto"


@dataclass(frozen=True)
class RegolaConguaglio:
    """Conguaglio fiscale (ADR 0019): le formule della ritenuta sull'imponibile fiscale dell'anno, con un solo periodo."""

    istituto: str
    versione: int
    dal: date
    riferimento: str
    al: date | None = None

    @property
    def istituto_resto(self) -> str:
        """Il resto differito dell'incapienza, trattenuto nei pagamenti successivi (ADR 0034)."""
        return f"{self.istituto}{SUFFISSO_RESTO}"

    @property
    def istituto_interesse(self) -> str:
        """L'interesse sul resto differito: un importo a sé, con il suo codice tributo (ADR 0034)."""
        return f"{self.istituto}{SUFFISSO_INTERESSE}"

    @property
    def istituto_non_trattenuto(self) -> str:
        """Il resto che non si e' potuto trattenere: un importo del conguaglio che la vista CU legge (ADR 0034)."""
        return f"{self.istituto}{SUFFISSO_NON_TRATTENUTO}"

    def __post_init__(self) -> None:
        soggetto = f"Conguaglio {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"{soggetto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")


ENTI_ADDIZIONALE = ("comune", "regione")


@dataclass(frozen=True)
class FasciaAddizionale:
    """Una fascia di reddito: l'aliquota si applica alla parte di reddito fino a `fino_a`; l'ultima fascia è aperta (None)."""

    fino_a: Decimal | None
    aliquota: Decimal


@dataclass(frozen=True)
class AliquotaAddizionale:
    """Aliquote dell'addizionale di un comune (codice catastale) o di una regione (codice regione) per un anno (ADR 0029).

    Le fasce si applicano a scaglioni. Con la `soglia` di esenzione, un reddito che non la supera non paga nulla; sopra,
    l'aliquota si applica a tutto il reddito. Il `riferimento` è la delibera o la legge regionale.
    """

    ente: str
    codice: str
    anno: int
    fasce: tuple[FasciaAddizionale, ...]
    riferimento: str
    soglia: Decimal = Decimal(0)

    def __post_init__(self) -> None:
        soggetto = f"Aliquota addizionale {self.ente} {self.codice} {self.anno}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.ente not in ENTI_ADDIZIONALE:
            raise ErroreCorpus(f"{soggetto}: ente ignoto, uno di {list(ENTI_ADDIZIONALE)}")
        if not isinstance(self.codice, str) or not self.codice.strip():
            raise ErroreCorpus(f"{soggetto}: codice obbligatorio")
        if type(self.anno) is not int:
            raise ErroreCorpus(f"{soggetto}: l'anno è un numero intero")
        if not self.fasce:
            raise ErroreCorpus(f"{soggetto}: almeno una fascia")
        if self.soglia < 0:
            raise ErroreCorpus(f"{soggetto}: soglia negativa")
        limiti = [fascia.fino_a for fascia in self.fasce[:-1]]
        if any(limite is None for limite in limiti) or self.fasce[-1].fino_a is not None:
            raise ErroreCorpus(f"{soggetto}: l'ultima fascia è aperta e le altre hanno un limite")
        if any(limite <= 0 for limite in limiti) or limiti != sorted(set(limiti)):
            raise ErroreCorpus(f"{soggetto}: i limiti delle fasce sono positivi e crescenti")
        if any(not 0 <= fascia.aliquota <= 1 for fascia in self.fasce):
            raise ErroreCorpus(f"{soggetto}: un'aliquota è tra 0 e 1")

    def su(self, reddito: Decimal) -> Decimal:
        """L'addizionale sul `reddito`, al centesimo: zero fino alla soglia, poi le fasce a scaglioni."""
        if reddito <= self.soglia:
            return Decimal("0.00")
        totale, sotto = Decimal(0), Decimal(0)
        for fascia in self.fasce:
            tetto = reddito if fascia.fino_a is None else min(reddito, fascia.fino_a)
            if tetto > sotto:
                totale += (tetto - sotto) * fascia.aliquota
                sotto = tetto
        return totale.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


RUOLI_ADDIZIONALE = (
    "regionale_dovuta", "comunale_dovuta", "regionale", "comunale_saldo", "comunale_acconto",
    "regionale_credito", "comunale_credito",
)
PARAMETRI_ADDIZIONALE = ("percentuale_acconto", "mese_prima_rata_acconto", "mese_ultima_rata")


@dataclass(frozen=True)
class RegolaAddizionali:
    """Regola delle addizionali (ADR 0029): quali istituti producono gli importi e quali parametri datati leggono.

    Gli istituti `*_dovuta` portano l'addizionale dell'anno calcolata al conguaglio; `regionale`, `comunale_saldo` e
    `comunale_acconto` sono le rate trattenute; `*_credito` la restituzione in unica soluzione. I tre parametri sono
    la percentuale dell'acconto, il primo mese delle rate dell'acconto e l'ultimo mese di tutte le rate.
    """

    versione: int
    dal: date
    riferimento: str
    percentuale_acconto: str
    mese_prima_rata_acconto: str
    mese_ultima_rata: str
    regionale_dovuta: str
    comunale_dovuta: str
    regionale: str
    comunale_saldo: str
    comunale_acconto: str
    regionale_credito: str
    comunale_credito: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = "Addizionali"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"{soggetto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        for campo in (*RUOLI_ADDIZIONALE, *PARAMETRI_ADDIZIONALE):
            valore = getattr(self, campo)
            if not isinstance(valore, str) or not valore.strip():
                raise ErroreCorpus(f"{soggetto}: {campo} obbligatorio")
        if len(set(self.istituti)) != len(RUOLI_ADDIZIONALE):
            raise ErroreCorpus(f"{soggetto}: ogni ruolo ha un istituto diverso")

    @property
    def istituti(self) -> tuple[str, ...]:
        return tuple(getattr(self, ruolo) for ruolo in RUOLI_ADDIZIONALE)

    @property
    def parametri(self) -> tuple[str, ...]:
        return tuple(getattr(self, nome) for nome in PARAMETRI_ADDIZIONALE)


# Nomi che le formule dei benefici leggono dal fisco della persona (ticket #95): il reddito annuo stimato (nel conguaglio il
# reddito vero), il reddito di lavoro dipendente del periodo, imposta lorda e detrazione dell'art. 13 del periodo, gli oneri
# detraibili comunicati (annui), i periodi e i giorni di servizio come nella ritenuta.
FISCO_BENEFICI = frozenset(
    {"reddito_stimato", "reddito_dipendente", "reddito_fascia", "imposta", "detrazione", "carichi", "oneri", "periodi", "giorni", "giorni_anno"}
)
ISTITUTI_BENEFICI = (
    "istituto_somma_esente", "istituto_trattamento_integrativo", "recupero_somma_esente", "recupero_trattamento_integrativo",
)
PARAMETRI_BENEFICI = ("soglia_recupero", "rate_somma_esente", "rate_trattamento_integrativo")


@dataclass(frozen=True)
class RegolaBenefici:
    """Somma esente e trattamento integrativo (ticket #95, ADR 0019): due importi a favore della persona, non reddito.

    `somma_esente` e `trattamento_integrativo` sono formule dell'importo del periodo di paga (o dell'anno, nel conguaglio
    con un solo periodo): leggono parametri e i valori `fisco.*` di `FISCO_BENEFICI`. Le categorie dicono a quali redditi
    spetta ciascun istituto. I quattro istituti sono i riconosciuti e i loro recuperi; `soglia_recupero` e le rate sono
    parametri datati: sotto la soglia il recupero e' in unica soluzione, sopra in `rate_*` rate dai pagamenti dopo il conguaglio.
    """

    versione: int
    dal: date
    riferimento: str
    somma_esente: str
    trattamento_integrativo: str
    categorie_somma_esente: tuple[str, ...]
    categorie_trattamento_integrativo: tuple[str, ...]
    istituto_somma_esente: str
    istituto_trattamento_integrativo: str
    recupero_somma_esente: str
    recupero_trattamento_integrativo: str
    soglia_recupero: str
    rate_somma_esente: str
    rate_trattamento_integrativo: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = "Benefici della persona"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"{soggetto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        for campo in (*ISTITUTI_BENEFICI, *PARAMETRI_BENEFICI):
            if not isinstance(getattr(self, campo), str) or not getattr(self, campo).strip():
                raise ErroreCorpus(f"{soggetto}: {campo} obbligatorio")
        if len(set(self.istituti)) != len(ISTITUTI_BENEFICI):
            raise ErroreCorpus(f"{soggetto}: ogni ruolo ha un istituto diverso")
        if not self.categorie_somma_esente or not self.categorie_trattamento_integrativo:
            raise ErroreCorpus(f"{soggetto}: categorie obbligatorie")
        for formula in (self.somma_esente, self.trattamento_integrativo):
            letti = riferimenti(formula)
            if letti.fatti or letti.importi or letti.basi:
                raise ErroreCorpus(f"{soggetto}: la formula legge solo parametri e fisco, non fatti, importi o basi")
            ignoti = letti.fisco - FISCO_BENEFICI
            if ignoti:
                raise ErroreCorpus(f"{soggetto}: fisco ignoto {sorted(ignoti)}; ammessi {sorted(FISCO_BENEFICI)}")

    @property
    def istituti(self) -> tuple[str, ...]:
        return tuple(getattr(self, ruolo) for ruolo in ISTITUTI_BENEFICI)

    @property
    def parametri(self) -> frozenset[str]:
        return (
            riferimenti(self.somma_esente).parametri
            | riferimenti(self.trattamento_integrativo).parametri
            | {getattr(self, nome) for nome in PARAMETRI_BENEFICI}
        )


@dataclass(frozen=True)
class DichiarazioneAccessorio:
    """L'istituto dichiara di essere trattamento accessorio, con date e fonte (ticket #96, ADR 0035)."""

    istituto: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        _riferimento_obbligatorio(self.riferimento, f"Accessorio {self.istituto}")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"Accessorio {self.istituto}: vigenza invertita")


PARAMETRI_SOSTITUTIVA = ("aliquota", "tetto", "limite")
ISTITUTI_SOSTITUTIVA = ("istituto", "istituto_base")


@dataclass(frozen=True)
class RegolaSostitutiva:
    """Sostitutiva sull'accessorio (ticket #96, ADR 0035): aliquota, tetto per persona e limite di reddito sono parametri datati.

    `istituto` è l'imposta trattenuta (versata con 179E); `istituto_base` è la quota di accessorio a sostitutiva, che
    esce dall'imponibile fiscale ordinario (va dichiarato riduttivo con `[[deduzione_fiscale]]`).
    """

    versione: int
    dal: date
    riferimento: str
    aliquota: str
    tetto: str
    limite: str
    istituto: str
    istituto_base: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = "Sostitutiva sull'accessorio"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if type(self.versione) is not int or self.versione < 1:
            raise ErroreCorpus(f"{soggetto}: versione non valida")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        for campo in (*PARAMETRI_SOSTITUTIVA, *ISTITUTI_SOSTITUTIVA):
            if not isinstance(getattr(self, campo), str) or not getattr(self, campo).strip():
                raise ErroreCorpus(f"{soggetto}: {campo} obbligatorio")
        if self.istituto == self.istituto_base:
            raise ErroreCorpus(f"{soggetto}: l'imposta e la quota a sostitutiva sono istituti diversi")

    @property
    def istituti(self) -> tuple[str, ...]:
        return tuple(getattr(self, ruolo) for ruolo in ISTITUTI_SOSTITUTIVA)

    @property
    def parametri(self) -> tuple[str, ...]:
        return tuple(getattr(self, nome) for nome in PARAMETRI_SOSTITUTIVA)


@dataclass(frozen=True)
class RegoleFiscali:
    categorie: tuple[CategoriaReddito, ...] = ()
    redditi: tuple[DichiarazioneReddito, ...] = ()
    ritenute: tuple[RegolaRitenuta, ...] = ()
    conguagli: tuple[RegolaConguaglio, ...] = ()
    fisiologici: tuple[DichiarazionePagamentoFisiologico, ...] = ()
    deduzioni: tuple[DichiarazioneDeduzione, ...] = ()
    aliquote: tuple[AliquotaAddizionale, ...] = ()
    addizionali: tuple[RegolaAddizionali, ...] = ()
    benefici: tuple[RegolaBenefici, ...] = ()
    accessori: tuple[DichiarazioneAccessorio, ...] = ()
    sostitutive: tuple[RegolaSostitutiva, ...] = ()
    aggiuntive: tuple[DichiarazioneMensilitaAggiuntiva, ...] = ()

    def __bool__(self) -> bool:
        return bool(
            self.categorie
            or self.redditi
            or self.ritenute
            or self.conguagli
            or self.fisiologici
            or self.deduzioni
            or self.aliquote
            or self.addizionali
            or self.benefici
            or self.accessori
            or self.sostitutive
            or self.aggiuntive
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
        if self.natura == NATURA_IMPONIBILE_SOSTITUTIVO:
            if self.effetto != "nessuno" or self.destinatario is not None or self.canale is not None:
                raise ErroreCorpus(f"{soggetto}: un imponibile sostitutivo ha effetto nessuno, senza destinatario né canale")
            return
        for nome, (valore, ammessi) in campi.items():
            if valore not in ammessi:
                raise ErroreCorpus(f"{soggetto}: {nome} obbligatorio, uno di {sorted(ammessi)}")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class DichiarazioneClassificazione:
    """L'istituto dichiara il codice di V livello del piano dei conti e l'origine del proprio impegno (ADR 0031).

    `origine_impegno` e' `automatico` (l'impegno nasce col bilancio) oppure il nome di un tipo di atto del registro.
    """

    istituto: str
    dal: date
    riferimento: str
    piano_dei_conti: str
    origine_impegno: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Classificazione {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        if not isinstance(self.origine_impegno, str) or not self.origine_impegno or self.origine_impegno != self.origine_impegno.strip():
            raise ErroreCorpus(f"{soggetto}: l'origine dell'impegno e' `automatico` o il nome di un tipo di atto")
        if not isinstance(self.piano_dei_conti, str) or not PIANO_DEI_CONTI.fullmatch(self.piano_dei_conti):
            raise ErroreCorpus(f"{soggetto}: codice del piano dei conti non valido, {self.piano_dei_conti!r}")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class CondizioneDiProposta:
    """Un fatto che il corpus richiede perche' un importo dell'istituto entri in una versione di proposta (ADR 0015).

    Senza il fatto per tutto il periodo dell'importo, l'importo resta calcolato e visibile tra gli esclusi.
    Esempio: l'attestazione della prestazione di una rata di collaborazione. Date e fonte come ogni dichiarazione.
    """

    istituto: str
    fatto: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Condizione di proposta {self.istituto}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if not isinstance(self.fatto, str) or not self.fatto.strip() or self.fatto != self.fatto.strip():
            raise ErroreCorpus(f"{soggetto}: il fatto richiesto va nominato")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class SogliaVerifica:
    """Soglia del netto di un pagamento oltre la quale l'ente verifica l'inadempimento presso AdER (ADR 0036).

    Per titolo (categoria di reddito, oppure `*` per tutti gli altri) e periodo. Senza `soglia` la verifica non
    si fa nel periodo (stipendi prima del 2026). `esclusi` sono gli istituti che non concorrono al netto della
    soglia, oltre ai rimborsi 730 (per esempio le trasferte documentate).
    """

    categoria: str
    dal: date
    riferimento: str
    soglia: Decimal | None = None
    al: date | None = None
    esclusi: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        soggetto = f"Soglia di verifica {self.categoria}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        if self.soglia is not None and self.soglia <= 0:
            raise ErroreCorpus(f"{soggetto}: la soglia è un importo positivo")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)


@dataclass(frozen=True)
class FasciaSommaSospesa:
    """Fascia sul netto: fino a `fino_a` (senza limite se None) si sospende 1/`divisore` di tutto il netto."""

    divisore: Decimal
    fino_a: Decimal | None = None


@dataclass(frozen=True)
class RegolaSommaSospesa:
    """Come si sospende e si rilascia la somma dopo un esito inadempiente (ADR 0036), con date e fonte.

    La fascia si sceglie sul netto e si applica a tutto il netto; `tetto` e' la quota del netto che la somma
    sospesa e le trattenute a terzi non superano insieme. I giorni sono quelli del DM 40/2008: risposta entro
    `giorni_risposta` feriali, sospensione di `giorni_sospensione` dalla comunicazione dell'esito.
    """

    dal: date
    riferimento: str
    fasce: tuple[FasciaSommaSospesa, ...]
    tetto: Decimal
    giorni_risposta: int
    giorni_sospensione: int
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = "Somma sospesa 48-bis"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")
        if not self.fasce or self.fasce[-1].fino_a is not None:
            raise ErroreCorpus(f"{soggetto}: l'ultima fascia non ha limite")
        limiti = [fascia.fino_a for fascia in self.fasce[:-1]]
        if any(limite is None for limite in limiti) or limiti != sorted(limiti):
            raise ErroreCorpus(f"{soggetto}: le fasce crescono e solo l'ultima è senza limite")
        if any(fascia.divisore <= 0 for fascia in self.fasce):
            raise ErroreCorpus(f"{soggetto}: il divisore di una fascia è positivo")
        if not Decimal(0) < self.tetto <= 1:
            raise ErroreCorpus(f"{soggetto}: il tetto è una frazione del netto tra 0 e 1")
        if self.giorni_risposta < 0 or self.giorni_sospensione < 0:
            raise ErroreCorpus(f"{soggetto}: i giorni non sono negativi")

    def copre(self, giorno: date) -> bool:
        return self.dal <= giorno and (self.al is None or giorno <= self.al)

    def quota_sul_netto(self, netto: Decimal) -> Decimal:
        """La fascia del netto, applicata a tutto il netto e arrotondata per difetto al centesimo."""
        fascia = next(f for f in self.fasce if f.fino_a is None or netto <= f.fino_a)
        return (netto / fascia.divisore).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


@dataclass(frozen=True)
class DichiarazioneOutput:
    """Il regime assegna a una vista i rapporti che hanno un importo pagato in certe basi o di certi istituti (ADR 0015).

    Una vista non conosce i titoli: prende i rapporti che la dichiarazione le assegna. `basi` elenca le basi a cui l'importo
    pagato concorre per intero; `istituti` gli istituti il cui importo pagato basta da solo. Date e fonte come ogni dichiarazione.
    """

    vista: str
    dal: date
    riferimento: str
    basi: tuple[str, ...] = ()
    istituti: tuple[str, ...] = ()
    al: date | None = None
    regime: str = ""
    posizione: str | None = None
    fine_servizio: str | None = None

    def __post_init__(self) -> None:
        soggetto = f"Output {self.vista}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if not isinstance(self.vista, str) or not self.vista.strip() or self.vista != self.vista.strip():
            raise ErroreCorpus(f"{soggetto}: la vista va nominata")
        for campo in ("posizione", "fine_servizio"):
            valore = getattr(self, campo)
            if valore is not None and (not isinstance(valore, str) or not valore.strip() or valore != valore.strip()):
                raise ErroreCorpus(f"{soggetto}: `{campo}` nomina un tipo di fatto")
        if not self.basi and not self.istituti:
            raise ErroreCorpus(f"{soggetto}: servono basi o istituti che assegnano i rapporti alla vista")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")

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
class MappaturaDiFatto:
    """Codice di un elemento di un sistema esterno, per il valore che un fatto del rapporto ha in un giorno.

    Come `MappaturaEsterna`, ma la chiave non è un istituto: è il valore di un fatto (ADR 0027, ticket #77).
    """

    sistema: str
    elemento: str
    fatto: str
    valore: str
    codice: str
    dal: date
    riferimento: str
    al: date | None = None

    def __post_init__(self) -> None:
        soggetto = f"Mappatura di fatto {self.sistema}.{self.elemento} ({self.fatto}={self.valore})"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        for campo in ("sistema", "elemento", "fatto", "valore", "codice"):
            valore = getattr(self, campo)
            if not isinstance(valore, str) or not valore.strip():
                raise ErroreCorpus(f"{soggetto}: {campo} obbligatorio, scritto come testo")
        if self.al is not None and self.al < self.dal:
            raise ErroreCorpus(f"{soggetto}: vigenza invertita")

    @property
    def chiave(self) -> tuple[str, str, str, str]:
        return (self.sistema, self.elemento, self.fatto, self.valore)


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
    """Festivi nazionali di un anno, dichiarati con il riferimento di legge (ticket #106).

    `feste` sono le feste fisse come MM-GG; `lunedi_dell_angelo` aggiunge il lunedì dopo la Pasqua, calcolata.
    Un anno senza calendario non ha festivi noti. Il patrono della sede non è qui: è un fatto del rapporto.
    """

    anno: int
    feste: tuple[str, ...]
    lunedi_dell_angelo: bool
    riferimento: str

    def __post_init__(self) -> None:
        soggetto = f"Calendario dei festivi {self.anno}"
        _riferimento_obbligatorio(self.riferimento, soggetto)
        if type(self.anno) is not int:
            raise ErroreCorpus(f"{soggetto}: anno non valido")
        for festa in self.feste:
            if not re.fullmatch(r"\d{2}-\d{2}", str(festa)):
                raise ErroreCorpus(f"{soggetto}: festa {festa!r} non valida, serve MM-GG")
            try:
                date(self.anno, int(festa[:2]), int(festa[3:]))
            except ValueError:
                raise ErroreCorpus(f"{soggetto}: festa {festa} inesistente nell'anno {self.anno}") from None
        if len(set(self.feste)) != len(self.feste):
            raise ErroreCorpus(f"{soggetto}: feste ripetute")

    @property
    def giorni(self) -> tuple[date, ...]:
        """Le date dei festivi nazionali dell'anno: le feste fisse e, se dichiarato, il lunedì dell'Angelo."""
        fisse = tuple(date(self.anno, int(festa[:2]), int(festa[3:])) for festa in self.feste)
        return fisse + ((lunedi_dell_angelo(self.anno),) if self.lunedi_dell_angelo else ())


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
        classificazioni: tuple[DichiarazioneClassificazione, ...] = (),
        mappature: tuple[MappaturaEsterna, ...] = (),
        mappature_di_fatto: tuple[MappaturaDiFatto, ...] = (),
        codici_f24ep: tuple[CodiceF24EP, ...] = (),
        scadenze_f24ep: tuple[RegolaScadenzaF24EP, ...] = (),
        calendari_festivi: tuple[CalendarioFestivi, ...] = (),
        riferimento_patrono: str | None = None,
        trattamenti_part_time: tuple[DichiarazioneTrattamentoPartTime, ...] = (),
        regole_malattia: tuple[RegolaMalattia, ...] = (),
        dichiarazioni_malattia: tuple[DichiarazioneMalattia, ...] = (),
        condizioni_di_proposta: tuple[CondizioneDiProposta, ...] = (),
        soglie_di_verifica: tuple[SogliaVerifica, ...] = (),
        regole_somma_sospesa: tuple[RegolaSommaSospesa, ...] = (),
        output: tuple[DichiarazioneOutput, ...] = (),
        fatto_cessazione: str | None = None,
        fatto_sospensione: str | None = None,
    ):
        self.reale = reale
        # Fatti del rapporto validi dal giorno dopo l'ultimo giorno di servizio (ticket #43, ADR 0018).
        self.fatto_cessazione = fatto_cessazione
        self.fatto_sospensione = fatto_sospensione
        self._output = tuple(output)
        self._condizioni_di_proposta = tuple(condizioni_di_proposta)
        self._soglie_di_verifica = tuple(soglie_di_verifica)
        self._regole_somma_sospesa = tuple(regole_somma_sospesa)
        self._trattamenti_part_time = tuple(trattamenti_part_time)
        self._regole_malattia = tuple(regole_malattia)
        self._dichiarazioni_malattia = tuple(dichiarazioni_malattia)
        self._scadenze_f24ep = tuple(scadenze_f24ep)
        self._calendari_festivi = tuple(calendari_festivi)
        self.riferimento_patrono = riferimento_patrono  # voce [patrono]: obbligatoria solo se un rapporto ha il patrono
        self._codici_f24ep = tuple(codici_f24ep)
        self._composizioni = tuple(composizioni)
        self._classificazioni = tuple(classificazioni)
        self._mappature = tuple(mappature)
        self._mappature_di_fatto = tuple(mappature_di_fatto)
        self.fiscale = fiscale or RegoleFiscali()
        self.fermi = tuple(fermi)
        self.denuncia = denuncia or RegoleDenuncia()
        self.fatto_servizio = fatto_servizio
        fatti_periodo = tuple(fatti_periodo_dichiarato)
        if trattamenti_part_time:
            # Un corpus che modella il part-time lo dichiara nel periodo: un cambio di percentuale o di tipo lo apre.
            fatti_periodo += tuple(f for f in (FATTO_PART_TIME, FATTO_TIPO_PART_TIME) if f not in fatti_periodo)
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
        self._convalida_classificazione()
        self._convalida_part_time()
        self._convalida_malattia()
        self._convalida_massimali_di_base()
        self._convalida_condizioni_di_proposta()
        self._convalida_blocco_pagamenti()
        self._convalida_output()
        self._convalida_mappature_di_fatto()
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
        elenco += [(f"Mensilità aggiuntiva {m.istituto}", m.riferimento) for m in fiscale.aggiuntive]
        elenco += [(f"Ritenuta {r.istituto}", r.riferimento) for r in fiscale.ritenute]
        elenco += [(f"Conguaglio {c.istituto}", c.riferimento) for c in fiscale.conguagli]
        elenco += [("Addizionali", a.riferimento) for a in fiscale.addizionali]
        elenco += [("Benefici della persona", b.riferimento) for b in fiscale.benefici]
        elenco += [(f"Accessorio {a.istituto}", a.riferimento) for a in fiscale.accessori]
        elenco += [("Sostitutiva sull'accessorio", r.riferimento) for r in fiscale.sostitutive]
        elenco += [(f"Aliquota addizionale {a.ente} {a.codice} {a.anno}", a.riferimento) for a in fiscale.aliquote]
        elenco += [(f"Composizione {c.istituto}", c.riferimento) for c in self._composizioni]
        elenco += [(f"Classificazione {c.istituto}", c.riferimento) for c in self._classificazioni]
        elenco += [(f"Mappatura {m.istituto} -> {m.sistema}", m.riferimento) for m in self._mappature]
        elenco += [
            (f"Mappatura di fatto {m.sistema}.{m.elemento} ({m.fatto}={m.valore})", m.riferimento)
            for m in self._mappature_di_fatto
        ]
        elenco += [(f"Part-time {t.istituto}", t.riferimento) for t in self._trattamenti_part_time]
        elenco += [("Malattia", r.riferimento) for r in self._regole_malattia]
        elenco += [(f"Malattia {d.istituto}", d.riferimento) for d in self._dichiarazioni_malattia]
        elenco += [(f"Condizione di proposta {c.istituto}", c.riferimento) for c in self._condizioni_di_proposta]
        elenco += [(f"Soglia di verifica {t.categoria}", t.riferimento) for t in self._soglie_di_verifica]
        elenco += [("Somma sospesa 48-bis", r.riferimento) for r in self._regole_somma_sospesa]
        elenco += [(f"Output {o.vista}", o.riferimento) for o in self._output]
        elenco += [(f"Codice F24EP {c.codice}", c.riferimento) for c in self._codici_f24ep]
        elenco += [("Scadenza F24EP", r.riferimento) for r in self._scadenze_f24ep]
        elenco += [("Proroga della scadenza F24EP", r.proroga.riferimento) for r in self._scadenze_f24ep if r.proroga]
        elenco += [(f"Calendario dei festivi {c.anno}", c.riferimento) for c in self._calendari_festivi]
        if self.riferimento_patrono is not None:
            elenco.append(("Patrono della sede di lavoro", self.riferimento_patrono))
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
        noti = set(self._regole) | {r.istituto for r in fiscale.ritenute} | {c.istituto for c in fiscale.conguagli}
        noti |= {i for c in fiscale.conguagli for i in (c.istituto_resto, c.istituto_interesse)}
        noti |= {i for regola in fiscale.addizionali for i in regola.istituti}
        noti |= {i for regola in fiscale.benefici for i in regola.istituti}
        return noti | {i for regola in fiscale.sostitutive for i in regola.istituti}

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

    def _convalida_massimali_di_base(self) -> None:
        for base in self._basi.values():
            if base.massimale is not None and base.massimale not in self._parametri:
                raise ErroreCorpus(f"Base {base.nome}: massimale, parametro ignoto {base.massimale}")

    def _convalida_output(self) -> None:
        for indice, dichiarazione in enumerate(self._output):
            for base in dichiarazione.basi:
                if base not in self._basi:
                    raise ErroreCorpus(f"Output {dichiarazione.vista}: base ignota {base}")
            for istituto in dichiarazione.istituti:
                if istituto not in self._regole:
                    raise ErroreCorpus(f"Output {dichiarazione.vista}: istituto senza regola {istituto}")
            for altra in self._output[indice + 1 :]:
                if (altra.vista, altra.regime) == (dichiarazione.vista, dichiarazione.regime):
                    _vigenze_sovrapposte([dichiarazione, altra], f"Output {dichiarazione.vista}")

    def _convalida_condizioni_di_proposta(self) -> None:
        for indice, condizione in enumerate(self._condizioni_di_proposta):
            if condizione.istituto not in self._regole:
                raise ErroreCorpus(f"Condizione di proposta {condizione.istituto}: istituto senza regola")
            for altra in self._condizioni_di_proposta[indice + 1 :]:
                if altra.istituto == condizione.istituto:
                    _vigenze_sovrapposte([condizione, altra], f"Condizione di proposta {condizione.istituto}")

    def _convalida_blocco_pagamenti(self) -> None:
        for indice, soglia in enumerate(self._soglie_di_verifica):
            for altra in self._soglie_di_verifica[indice + 1 :]:
                if altra.categoria == soglia.categoria:
                    _vigenze_sovrapposte([soglia, altra], f"Soglia di verifica {soglia.categoria}")
        _vigenze_sovrapposte(self._regole_somma_sospesa, "Somma sospesa 48-bis")

    def _convalida_mappature_di_fatto(self) -> None:
        for indice, mappatura in enumerate(self._mappature_di_fatto):
            altre = [a for a in self._mappature_di_fatto[indice + 1 :] if a.chiave == mappatura.chiave]
            if altre:
                _vigenze_sovrapposte([mappatura, *altre], "Mappatura di fatto {}.{} ({}={})".format(*mappatura.chiave))

    def _convalida_part_time(self) -> None:
        noti = self._istituti_noti()
        for indice, dichiarazione in enumerate(self._trattamenti_part_time):
            if dichiarazione.istituto not in noti:
                raise ErroreCorpus(f"Part-time {dichiarazione.istituto}: istituto ignoto")
            for altra in self._trattamenti_part_time[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], f"Part-time {dichiarazione.istituto}")

    def _convalida_malattia(self) -> None:
        noti = self._istituti_noti()
        _vigenze_sovrapposte(self._regole_malattia, "Malattia")
        for indice, dichiarazione in enumerate(self._dichiarazioni_malattia):
            if dichiarazione.istituto not in noti:
                raise ErroreCorpus(f"Malattia {dichiarazione.istituto}: istituto ignoto")
            for altra in self._dichiarazioni_malattia[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], f"Malattia {dichiarazione.istituto}")
        if self._dichiarazioni_malattia and not self._regole_malattia:
            raise ErroreCorpus("Malattia: gli istituti dichiarano un trattamento ma mancano le regole della malattia")

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
        chiavi = [(a.ente, a.codice, a.anno) for a in fiscale.aliquote]
        for chiave in chiavi:
            if chiavi.count(chiave) > 1:
                raise ErroreCorpus(f"Aliquota addizionale {chiave[0]} {chiave[1]} {chiave[2]}: dichiarata più volte")
        for indice, regola in enumerate(fiscale.addizionali):
            ignoti = set(regola.parametri) - self._parametri.keys()
            if ignoti:
                raise ErroreCorpus(f"Addizionali: parametri ignoti {sorted(ignoti)}")
            gia = [i for i in regola.istituti if i in self._regole]
            if gia:
                raise ErroreCorpus(f"Addizionali {gia[0]}: lo stesso istituto ha anche una regola")
            for altra in fiscale.addizionali[indice + 1 :]:
                _vigenze_sovrapposte([regola, altra], "Addizionali")
        for indice, regola in enumerate(fiscale.benefici):
            soggetto = "Benefici della persona"
            if not fiscale.ritenute:
                raise ErroreCorpus(f"{soggetto}: leggono imposta e detrazione della ritenuta, manca [[ritenuta]]")
            ignoti = regola.parametri - self._parametri.keys()
            if ignoti:
                raise ErroreCorpus(f"{soggetto}: parametri ignoti {sorted(ignoti)}")
            for categoria in (*regola.categorie_somma_esente, *regola.categorie_trattamento_integrativo):
                if categoria not in nomi:
                    raise ErroreCorpus(f"{soggetto}: categoria ignota {categoria}")
            gia = [i for i in regola.istituti if i in self._regole]
            if gia:
                raise ErroreCorpus(f"{soggetto} {gia[0]}: lo stesso istituto ha anche una regola")
            for altra in fiscale.benefici[indice + 1 :]:
                _vigenze_sovrapposte([regola, altra], soggetto)
        for indice, dichiarazione in enumerate(fiscale.accessori):
            soggetto = f"Accessorio {dichiarazione.istituto}"
            if dichiarazione.istituto not in self._regole:
                raise ErroreCorpus(f"{soggetto}: istituto ignoto")
            for altra in fiscale.accessori[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], soggetto)
        for indice, regola in enumerate(fiscale.sostitutive):
            soggetto = "Sostitutiva sull'accessorio"
            ignoti = set(regola.parametri) - self._parametri.keys()
            if ignoti:
                raise ErroreCorpus(f"{soggetto}: parametri ignoti {sorted(ignoti)}")
            gia = [i for i in regola.istituti if i in self._regole]
            if gia:
                raise ErroreCorpus(f"{soggetto} {gia[0]}: lo stesso istituto ha anche una regola")
            for altra in fiscale.sostitutive[indice + 1 :]:
                _vigenze_sovrapposte([regola, altra], soggetto)
        for indice, dichiarazione in enumerate(fiscale.fisiologici):
            soggetto = f"Pagamento fisiologico {dichiarazione.istituto}"
            if dichiarazione.istituto not in self._regole:
                raise ErroreCorpus(f"{soggetto}: istituto ignoto")
            for altra in fiscale.fisiologici[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], soggetto)
        for indice, dichiarazione in enumerate(fiscale.aggiuntive):
            soggetto = f"Mensilità aggiuntiva {dichiarazione.istituto}"
            if dichiarazione.istituto not in self._regole:
                raise ErroreCorpus(f"{soggetto}: istituto ignoto")
            for altra in fiscale.aggiuntive[indice + 1 :]:
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
                ignote = {b.removesuffix("_pagato") for b in basi} - self._basi.keys()
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
        """Una frazione non legge il periodo dichiarato, che ne è la somma; l'annuale legge solo importi annuali."""
        for nome in importi:
            if regola.maturazione == "annuale":
                if any(dipendenza.maturazione != "annuale" for dipendenza in self._regole[nome]):
                    raise ErroreCorpus(f"Regola {regola.istituto}: una regola annuale legge solo importi annuali, non {nome}")
                continue
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
            **({"fine_servizio": [self.fatto_cessazione, self.fatto_sospensione]} if self.fatto_cessazione or self.fatto_sospensione else {}),
            "basi": [
                [base.nome, base.riferimento, *([base.massimale] if base.massimale else []),
                 *(["esclusione", base.esclusione, sorted(base.motivi_esclusione)] if base.esclusione else [])]
                for _, base in sorted(self._basi.items())
            ],
            "concorsi": sorted(
                [c.istituto, c.base, c.dal.isoformat(), c.al.isoformat() if c.al else "", c.misura, c.riferimento]
                for c in self._concorsi
            ),
            "parametri": [
                {
                    "nome": parametro.nome,
                    "vigenze": [
                        [v.dal.isoformat(), str(v.valore), v.riferimento, *([v.al.isoformat()] if v.al else []),
                         *(["applicabile", v.applicabile_dal.isoformat()] if v.applicabile_dal else [])]
                        for v in parametro.vigenze
                    ],
                }
                for _, parametro in sorted(self._parametri.items())
            ],
            "regole": sorted(
                [
                    [r.istituto, r.dal.isoformat(), r.versione, r.al.isoformat() if r.al else None,
                     r.riferimento, r.formula, r.applica_se, r.maturazione, r.conteggio, r.divisore, r.decimali,
                     *(["anche_se", list(r.anche_se)] if r.anche_se else [])]
                    for regole in self._regole.values()
                    for r in regole
                ],
                key=lambda riga: (riga[0], riga[1]),
            ),
        }
        if self.fermi:
            contenuto["fermi"] = sorted(
                [f.fatto, f.caso, f.ambito, f.riferimento, *([f.codice] if f.codice is not None else []),
                 *(["manca", f.se] if f.manca else []),
                 *(["valori", sorted(f.valori)] if f.valori is not None else []),
                 *(["solo_se", f.solo_se] if f.solo_se is not None else [])]
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
                     r.imposta, r.detrazione, sorted(r.categorie), r.detrazione_richiesta,
                     *([r.detrazione_automatica] if r.detrazione_automatica != "0" else []),
                     *([r.carichi_coniuge, r.carichi_figlio, r.carichi_ascendente]
                       if (r.carichi_coniuge, r.carichi_figlio, r.carichi_ascendente) != ("0", "0", "0") else []),
                     *([sorted(r.categorie_detrazione), r.detrazione_carica_elettiva,
                        sorted(r.categorie_detrazione_carica_elettiva)]
                       if (r.categorie_detrazione, r.detrazione_carica_elettiva) != ((), "0") else [])]
                    for r in fiscale.ritenute
                ),
                "conguagli": sorted(
                    [c.istituto, c.versione, c.dal.isoformat(), c.al.isoformat() if c.al else "", c.riferimento]
                    for c in fiscale.conguagli
                ),
            }
            if fiscale.addizionali:
                contenuto["fiscale"]["addizionali"] = sorted(
                    [a.versione, a.dal.isoformat(), a.al.isoformat() if a.al else "", a.riferimento,
                     *a.parametri, *a.istituti]
                    for a in fiscale.addizionali
                )
            if fiscale.benefici:
                contenuto["fiscale"]["benefici"] = sorted(
                    [b.versione, b.dal.isoformat(), b.al.isoformat() if b.al else "", b.riferimento,
                     b.somma_esente, b.trattamento_integrativo, sorted(b.categorie_somma_esente),
                     sorted(b.categorie_trattamento_integrativo), *b.istituti, *(getattr(b, n) for n in PARAMETRI_BENEFICI)]
                    for b in fiscale.benefici
                )
            if fiscale.accessori:
                contenuto["fiscale"]["accessori"] = sorted(
                    [a.istituto, a.dal.isoformat(), a.al.isoformat() if a.al else "", a.riferimento]
                    for a in fiscale.accessori
                )
            if fiscale.sostitutive:
                contenuto["fiscale"]["sostitutive"] = sorted(
                    [r.versione, r.dal.isoformat(), r.al.isoformat() if r.al else "", r.riferimento, *r.parametri, *r.istituti]
                    for r in fiscale.sostitutive
                )
            if fiscale.aliquote:
                contenuto["fiscale"]["aliquote"] = sorted(
                    [a.ente, a.codice, a.anno, str(a.soglia), a.riferimento,
                     [[str(f.fino_a) if f.fino_a is not None else "", str(f.aliquota)] for f in a.fasce]]
                    for a in fiscale.aliquote
                )
            if fiscale.aggiuntive:
                contenuto["fiscale"]["aggiuntive"] = sorted(
                    [m.istituto, m.dal.isoformat(), m.al.isoformat() if m.al else "", m.riferimento,
                     m.mese_pagamento or 0, m.giorno_dal or 0, m.giorno_al or 0]
                    for m in fiscale.aggiuntive
                )
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
        if self._classificazioni:
            contenuto["classificazioni"] = sorted(
                [c.istituto, c.dal.isoformat(), c.al.isoformat() if c.al else "", c.piano_dei_conti, c.origine_impegno,
                 c.riferimento]
                for c in self._classificazioni
            )
        if self._trattamenti_part_time:
            contenuto["part_time"] = sorted(
                [t.istituto, t.trattamento, t.dal.isoformat(), t.al.isoformat() if t.al else "", t.fatto or "", t.riferimento]
                for t in self._trattamenti_part_time
            )
        if self._regole_malattia or self._dichiarazioni_malattia:
            contenuto["malattia"] = [
                sorted(
                    [r.dal.isoformat(), r.al.isoformat() if r.al else "", r.giorni_decurtati, r.anni_finestra,
                     [[g, str(p)] for g, p in r.fasce], r.riferimento]
                    for r in self._regole_malattia
                ),
                sorted(
                    [d.istituto, d.trattamento, d.dal.isoformat(), d.al.isoformat() if d.al else "", d.riferimento]
                    for d in self._dichiarazioni_malattia
                ),
            ]
        if any(b.retribuzione_virtuale for b in self._basi.values()):
            contenuto["basi_virtuali"] = sorted(b.nome for b in self._basi.values() if b.retribuzione_virtuale)
        if self._output:
            contenuto["output"] = sorted(
                [o.vista, sorted(o.basi), sorted(o.istituti), o.dal.isoformat(), o.al.isoformat() if o.al else "", o.riferimento]
                + ([o.regime, o.posizione or "", o.fine_servizio or ""] if o.regime or o.posizione or o.fine_servizio else [])
                for o in self._output
            )
        if self._condizioni_di_proposta:
            contenuto["condizioni_di_proposta"] = sorted(
                [c.istituto, c.fatto, c.dal.isoformat(), c.al.isoformat() if c.al else "", c.riferimento]
                for c in self._condizioni_di_proposta
            )
        if self._soglie_di_verifica:
            contenuto["soglie_di_verifica"] = sorted(
                [t.categoria, str(t.soglia) if t.soglia is not None else "", t.dal.isoformat(),
                 t.al.isoformat() if t.al else "", sorted(t.esclusi), t.riferimento]
                for t in self._soglie_di_verifica
            )
        if self._regole_somma_sospesa:
            contenuto["somma_sospesa"] = sorted(
                [r.dal.isoformat(), r.al.isoformat() if r.al else "",
                 [[str(f.divisore), str(f.fino_a) if f.fino_a is not None else ""] for f in r.fasce],
                 str(r.tetto), r.giorni_risposta, r.giorni_sospensione, r.riferimento]
                for r in self._regole_somma_sospesa
            )
        if self._mappature:
            contenuto["mappature"] = sorted(
                [m.istituto, m.sistema, m.codice, m.dal.isoformat(), m.al.isoformat() if m.al else "", m.riferimento]
                for m in self._mappature
            )
        if self._mappature_di_fatto:
            contenuto["mappature_di_fatto"] = sorted(
                [*m.chiave, m.codice, m.dal.isoformat(), m.al.isoformat() if m.al else "", m.riferimento]
                for m in self._mappature_di_fatto
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
                [c.anno, sorted(c.feste), c.lunedi_dell_angelo, c.riferimento] for c in self._calendari_festivi
            )
        if self.riferimento_patrono is not None:
            contenuto["patrono"] = self.riferimento_patrono
        testo = json.dumps(contenuto, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:16]

    def istituti(self) -> list[str]:
        return sorted(self._regole)

    def decorrenze_con_applicabilita(self, pagamento: date) -> tuple[date, ...]:
        """Le decorrenze degli importi con una data di applicabilità già raggiunta alla data di pagamento (ADR 0041)."""
        return tuple(sorted({
            vigenza.dal
            for parametro in self._parametri.values()
            for vigenza in parametro.vigenze
            if vigenza.applicabile_dal is not None and vigenza.applicabile_dal <= pagamento
        }))

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

    def mensilita_aggiuntiva(self, istituto: str, giorno: date) -> DichiarazioneMensilitaAggiuntiva | None:
        """Dichiarazione vigente alla data di pagamento; None se l'istituto non è una mensilità aggiuntiva."""
        return _vigente([m for m in self.fiscale.aggiuntive if m.istituto == istituto], giorno)

    def deduzione_fiscale(self, istituto: str, giorno: date) -> DichiarazioneDeduzione | None:
        """Dichiarazione vigente alla data di pagamento; None se l'importo dell'istituto non riduce l'imponibile fiscale."""
        return _vigente([d for d in self.fiscale.deduzioni if d.istituto == istituto], giorno)

    def accessorio(self, istituto: str, giorno: date) -> DichiarazioneAccessorio | None:
        """Dichiarazione vigente alla data; None se l'istituto non è trattamento accessorio."""
        return _vigente([a for a in self.fiscale.accessori if a.istituto == istituto], giorno)

    def regola_sostitutiva(self, giorno: date) -> RegolaSostitutiva | None:
        """Regola della sostitutiva sull'accessorio vigente alla data; None se il corpus non la calcola."""
        return _vigente(self.fiscale.sostitutive, giorno)

    def e_quota_sostitutiva(self, istituto: str) -> bool:
        """L'istituto è la quota di accessorio a sostitutiva di una regola, a qualunque data: esce dall'imponibile ordinario."""
        return any(regola.istituto_base == istituto for regola in self.fiscale.sostitutive)

    def aliquota_addizionale(self, ente: str, codice: str, anno: int) -> AliquotaAddizionale | None:
        """Aliquote dell'addizionale del comune o della regione per l'anno; None se il corpus non le dichiara."""
        return next((a for a in self.fiscale.aliquote if (a.ente, a.codice, a.anno) == (ente, codice, anno)), None)

    def _convalida_classificazione(self) -> None:
        noti = self._istituti_noti()
        for indice, dichiarazione in enumerate(self._classificazioni):
            if dichiarazione.istituto not in noti:
                raise ErroreCorpus(f"Classificazione {dichiarazione.istituto}: istituto ignoto")
            for altra in self._classificazioni[indice + 1 :]:
                if altra.istituto == dichiarazione.istituto:
                    _vigenze_sovrapposte([dichiarazione, altra], f"Classificazione {dichiarazione.istituto}")

    def regola_addizionali(self, giorno: date) -> RegolaAddizionali | None:
        """Regola delle addizionali vigente alla data; None se il corpus non le calcola."""
        return _vigente(self.fiscale.addizionali, giorno)

    def regola_benefici(self, giorno: date) -> RegolaBenefici | None:
        """Regola di somma esente e trattamento integrativo vigente alla data; None se il corpus non li calcola."""
        return _vigente(self.fiscale.benefici, giorno)

    def regola_ritenuta(self, giorno: date) -> RegolaRitenuta | None:
        return _vigente(self.fiscale.ritenute, giorno)

    def regola_conguaglio(self, giorno: date) -> RegolaConguaglio | None:
        return _vigente(self.fiscale.conguagli, giorno)

    def composizione(self, istituto: str, giorno: date) -> DichiarazioneComposizione | None:
        """Dichiarazione di composizione vigente alla data; None se l'istituto non ne dichiara."""
        return _vigente([c for c in self._composizioni if c.istituto == istituto], giorno)

    def classificazione(self, istituto: str, giorno: date) -> DichiarazioneClassificazione | None:
        """Dichiarazione di classificazione vigente alla data; None se l'istituto non ne dichiara."""
        return _vigente([c for c in self._classificazioni if c.istituto == istituto], giorno)

    def output(self, vista: str, giorno: date) -> DichiarazioneOutput | None:
        """Dichiarazione vigente alla data per la vista; None se il regime non la dichiara."""
        return _vigente([o for o in self._output if o.vista == vista], giorno)

    def outputs(self, vista: str, giorno: date) -> tuple[DichiarazioneOutput, ...]:
        """Tutte le dichiarazioni vigenti alla data per la vista, una per regime."""
        return tuple(o for o in self._output if o.vista == vista and o.copre(giorno))

    def condizione_di_proposta(self, istituto: str, giorno: date) -> CondizioneDiProposta | None:
        """Condizione vigente alla data della valuta; None se l'istituto non ne richiede."""
        return _vigente([c for c in self._condizioni_di_proposta if c.istituto == istituto], giorno)

    def soglia_verifica(self, categoria: str, giorno: date) -> SogliaVerifica | None:
        """Soglia della verifica 48-bis per il titolo alla data del pagamento; il titolo senza regola propria usa `*`."""
        propria = _vigente([t for t in self._soglie_di_verifica if t.categoria == categoria], giorno)
        return propria or _vigente([t for t in self._soglie_di_verifica if t.categoria == "*"], giorno)

    def regola_somma_sospesa(self, giorno: date) -> RegolaSommaSospesa | None:
        """Regola della somma sospesa vigente alla data; None se il corpus non blocca i pagamenti."""
        return _vigente(self._regole_somma_sospesa, giorno)

    def trattamento_part_time(self, istituto: str, giorno: date) -> DichiarazioneTrattamentoPartTime | None:
        """Trattamento nel part-time vigente alla data; None se l'istituto non lo dichiara."""
        return _vigente([t for t in self._trattamenti_part_time if t.istituto == istituto], giorno)

    def regola_malattia(self, giorno: date) -> RegolaMalattia | None:
        """Regole della malattia vigenti alla data; None se il corpus non modella la malattia."""
        return _vigente(list(self._regole_malattia), giorno)

    def trattamento_malattia(self, istituto: str, giorno: date) -> DichiarazioneMalattia | None:
        """Trattamento nella malattia vigente alla data; None se l'istituto non lo dichiara."""
        return _vigente([d for d in self._dichiarazioni_malattia if d.istituto == istituto], giorno)

    def mappatura(
        self, istituto: str, sistema: str, data_pagamento: date, anno_imposta: int | None = None
    ) -> MappaturaEsterna | None:
        """Codice del sistema esterno: per anno d'imposta, al 31 dicembre, se l'importo lo porta; altrimenti per data di pagamento."""
        giorno = date(anno_imposta, 12, 31) if anno_imposta is not None else data_pagamento
        return _vigente([m for m in self._mappature if (m.istituto, m.sistema) == (istituto, sistema)], giorno)

    def mappatura_di_fatto(
        self, sistema: str, elemento: str, fatto: str, valore: str, giorno: date
    ) -> MappaturaDiFatto | None:
        """Codice dell'elemento per il valore del fatto, vigente al giorno; None se il corpus non lo dichiara."""
        return _vigente(
            [m for m in self._mappature_di_fatto if m.chiave == (sistema, elemento, fatto, valore)], giorno
        )

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
        if self._regole_malattia:
            tipi.add("malattia")
        for regole in self._regole.values():
            for regola in regole:
                tipi |= riferimenti(regola.formula).fatti
                if regola.applica_se and regola.maturazione != "annuale":
                    tipi.add(regola.fatto_condizione)
                    tipi |= {tipo for tipo, _ in regola.condizioni_aggiuntive}
        return tuple(sorted(tipi))

    def firma_giorno(self, giorno: date, pagamento: date | None = None) -> tuple:
        """Regole e parametri vigenti in un giorno: se cambia, il mese si divide. Con `pagamento` valgono quelli applicabili."""
        parametri = []
        for nome, parametro in sorted(self._parametri.items()):
            vigenza = parametro._vigente(giorno, pagamento)
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
            basi = tuple(
                Base(
                    voce["nome"], voce["riferimento"], voce.get("massimale"), voce.get("esclusione"),
                    tuple(voce.get("motivi_esclusione", ())),
                    bool(voce.get("retribuzione_virtuale", False)),
                )
                for voce in dati.get("base", [])
            )
            concorsi = tuple(concorso for voce in dati.get("concorso", []) for concorso in _concorsi_da_toml(voce))
            fermi = tuple(
                Fermo(voce["fatto"], voce["caso"], voce["ambito"], voce["riferimento"], voce.get("codice"),
                      voce.get("se"), voce.get("manca", False),
                      tuple(voce["valori"]) if voce.get("valori") is not None else None, voce.get("solo_se"))
                for voce in dati.get("fermo", [])
            )
            denuncia = _denuncia_da_toml(dati.get("denuncia", {}))
            fiscale = _fiscale_da_toml(dati)
            composizioni = tuple(_composizione_da_toml(voce) for voce in dati.get("composizione", []))
            classificazioni = tuple(_classificazione_da_toml(voce) for voce in dati.get("classificazione", []))
            mappature = tuple(_mappatura_da_toml(voce) for voce in dati.get("mappatura", []))
            mappature_di_fatto = tuple(
                MappaturaDiFatto(
                    sistema=voce["sistema"],
                    elemento=voce["elemento"],
                    fatto=voce["fatto"],
                    valore=voce["valore"],
                    codice=voce["codice"],
                    dal=_data(voce["dal"], "dal"),
                    riferimento=voce["riferimento"],
                    al=_data(voce["al"], "al") if "al" in voce else None,
                )
                for voce in dati.get("mappatura_fatto", [])
            )
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
            regole_malattia = tuple(
                RegolaMalattia(
                    dal=_data(voce["dal"], "dal"),
                    riferimento=voce["riferimento"],
                    giorni_decurtati=voce["giorni_decurtati"],
                    anni_finestra=voce["anni_finestra"],
                    fasce=tuple((int(f[0]), Decimal(str(f[1]))) for f in voce["fasce"]),
                    al=_data(voce["al"], "al") if "al" in voce else None,
                )
                for voce in dati.get("malattia", [])
            )
            dichiarazioni_malattia = tuple(
                DichiarazioneMalattia(
                    istituto=voce["istituto"],
                    trattamento=voce["trattamento"],
                    dal=_data(voce["dal"], "dal"),
                    riferimento=voce["riferimento"],
                    al=_data(voce["al"], "al") if "al" in voce else None,
                )
                for voce in dati.get("malattia_istituto", [])
            )
            condizioni_di_proposta = tuple(
                CondizioneDiProposta(
                    istituto=voce["istituto"],
                    fatto=voce["fatto"],
                    dal=_data(voce["dal"], "dal"),
                    riferimento=voce["riferimento"],
                    al=_data(voce["al"], "al") if "al" in voce else None,
                )
                for voce in dati.get("condizione_di_proposta", [])
            )
            soglie_di_verifica = tuple(
                SogliaVerifica(
                    categoria=voce["categoria"],
                    dal=_data(voce["dal"], "dal"),
                    riferimento=voce["riferimento"],
                    soglia=_decimale(voce["soglia"], "Soglia di verifica") if "soglia" in voce else None,
                    al=_data(voce["al"], "al") if "al" in voce else None,
                    esclusi=tuple(voce.get("esclusi", ())),
                )
                for voce in dati.get("soglia_verifica", [])
            )
            regole_somma_sospesa = tuple(
                RegolaSommaSospesa(
                    dal=_data(voce["dal"], "dal"),
                    riferimento=voce["riferimento"],
                    fasce=tuple(
                        FasciaSommaSospesa(
                            _decimale(fascia["divisore"], "Fascia della somma sospesa"),
                            _decimale(fascia["fino_a"], "Fascia della somma sospesa") if "fino_a" in fascia else None,
                        )
                        for fascia in voce["fasce"]
                    ),
                    tetto=_decimale(voce["tetto"], "Tetto della somma sospesa"),
                    giorni_risposta=voce["giorni_risposta"],
                    giorni_sospensione=voce["giorni_sospensione"],
                    al=_data(voce["al"], "al") if "al" in voce else None,
                )
                for voce in dati.get("somma_sospesa", [])
            )
            output = tuple(
                DichiarazioneOutput(
                    vista=voce["vista"],
                    dal=_data(voce["dal"], "dal"),
                    riferimento=voce["riferimento"],
                    basi=tuple(voce.get("basi", ())),
                    istituti=tuple(voce.get("istituti", ())),
                    al=_data(voce["al"], "al") if "al" in voce else None,
                    regime=voce.get("regime", ""),
                    posizione=voce.get("posizione"),
                    fine_servizio=voce.get("fine_servizio"),
                )
                for voce in dati.get("output", [])
            )
            codici_f24ep = tuple(_codice_f24ep_da_toml(voce) for voce in dati.get("codice_f24ep", []))
            scadenze_f24ep = tuple(_scadenza_f24ep_da_toml(voce) for voce in dati.get("scadenza_f24ep", []))
            calendari_festivi = tuple(
                CalendarioFestivi(
                    voce["anno"],
                    tuple(voce["feste"]),
                    voce.get("lunedi_dell_angelo", False),
                    voce["riferimento"],
                )
                for voce in dati.get("calendario_festivi", [])
            )
            patrono = dati.get("patrono")
            riferimento_patrono = patrono["riferimento"] if patrono is not None else None
            if riferimento_patrono is not None:
                _riferimento_obbligatorio(riferimento_patrono, "Patrono della sede di lavoro")
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
            classificazioni=classificazioni,
            mappature=mappature,
            mappature_di_fatto=mappature_di_fatto,
            codici_f24ep=codici_f24ep,
            scadenze_f24ep=scadenze_f24ep,
            calendari_festivi=calendari_festivi,
            riferimento_patrono=riferimento_patrono,
            trattamenti_part_time=trattamenti_part_time,
            regole_malattia=regole_malattia,
            dichiarazioni_malattia=dichiarazioni_malattia,
            condizioni_di_proposta=condizioni_di_proposta,
            soglie_di_verifica=soglie_di_verifica,
            regole_somma_sospesa=regole_somma_sospesa,
            output=output,
            fatto_cessazione=periodo.get("cessazione"),
            fatto_sospensione=periodo.get("sospensione"),
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


def _classificazione_da_toml(voce: dict) -> DichiarazioneClassificazione:
    return DichiarazioneClassificazione(
        istituto=voce["istituto"],
        dal=_data(voce["dal"], "dal"),
        riferimento=voce["riferimento"],
        piano_dei_conti=voce["piano_dei_conti"],
        origine_impegno=voce["origine_impegno"],
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
        applicabile = _data(vigenza["applicabile_dal"], "applicabile_dal") if "applicabile_dal" in vigenza else None
        vigenze.append(VigenzaParametro(_data(vigenza["dal"], "dal"), valore, vigenza["riferimento"], al, applicabile))
    return Parametro(voce["nome"], tuple(vigenze))


def _denuncia_da_toml(voce: dict) -> RegoleDenuncia:
    massimale = voce.get("massimale")
    return RegoleDenuncia(
        persona=voce.get("persona"),
        massimale=Massimale(massimale["base"], massimale["parametro"]) if massimale else None,
        conguaglio_annuo=tuple(voce.get("conguaglio_annuo", ())),
    )


def _decimale(valore: object, soggetto: str) -> Decimal:
    if not isinstance(valore, str):
        raise ErroreCorpus(f"{soggetto}: il valore va scritto come testo")
    try:
        risultato = Decimal(valore)
    except InvalidOperation as errore:
        raise ErroreCorpus(f"{soggetto}: valore non numerico") from errore
    if not risultato.is_finite():
        raise ErroreCorpus(f"{soggetto}: valore non finito")
    return risultato


def _aliquota_da_toml(voce: dict) -> AliquotaAddizionale:
    soggetto = f"Aliquota addizionale {voce['ente']} {voce['codice']} {voce['anno']}"
    return AliquotaAddizionale(
        voce["ente"],
        voce["codice"],
        voce["anno"],
        tuple(
            FasciaAddizionale(
                _decimale(fascia["fino_a"], soggetto) if "fino_a" in fascia else None,
                _decimale(fascia["aliquota"], soggetto),
            )
            for fascia in voce["fascia"]
        ),
        voce["riferimento"],
        _decimale(voce["soglia"], soggetto) if "soglia" in voce else Decimal(0),
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
            detrazione_automatica=voce.get("detrazione_automatica", "0"),
            categorie_detrazione_automatica=tuple(voce.get("categorie_detrazione_automatica", ())),
            carichi_coniuge=voce.get("carichi_coniuge", "0"),
            carichi_figlio=voce.get("carichi_figlio", "0"),
            carichi_ascendente=voce.get("carichi_ascendente", "0"),
            categorie_detrazione=tuple(voce.get("categorie_detrazione", ())),
            detrazione_carica_elettiva=voce.get("detrazione_carica_elettiva", "0"),
            categorie_detrazione_carica_elettiva=tuple(voce.get("categorie_detrazione_carica_elettiva", ())),
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
    aliquote = tuple(_aliquota_da_toml(voce) for voce in dati.get("aliquota_addizionale", []))
    addizionali = tuple(
        RegolaAddizionali(
            versione=voce["versione"],
            dal=_data(voce["dal"], "dal"),
            riferimento=voce["riferimento"],
            al=_data(voce["al"], "al") if "al" in voce else None,
            **{campo: voce[campo] for campo in (*PARAMETRI_ADDIZIONALE, *RUOLI_ADDIZIONALE)},
        )
        for voce in dati.get("addizionale", [])
    )
    benefici = tuple(
        RegolaBenefici(
            versione=voce["versione"],
            dal=_data(voce["dal"], "dal"),
            riferimento=voce["riferimento"],
            al=_data(voce["al"], "al") if "al" in voce else None,
            somma_esente=voce["somma_esente"],
            trattamento_integrativo=voce["trattamento_integrativo"],
            categorie_somma_esente=tuple(voce["categorie_somma_esente"]),
            categorie_trattamento_integrativo=tuple(voce["categorie_trattamento_integrativo"]),
            **{campo: voce[campo] for campo in (*ISTITUTI_BENEFICI, *PARAMETRI_BENEFICI)},
        )
        for voce in dati.get("beneficio", [])
    )
    accessori = tuple(
        DichiarazioneAccessorio(
            voce["istituto"],
            _data(voce["dal"], "dal"),
            voce["riferimento"],
            _data(voce["al"], "al") if "al" in voce else None,
        )
        for voce in dati.get("accessorio", [])
    )
    sostitutive = tuple(
        RegolaSostitutiva(
            versione=voce["versione"],
            dal=_data(voce["dal"], "dal"),
            riferimento=voce["riferimento"],
            al=_data(voce["al"], "al") if "al" in voce else None,
            **{campo: voce[campo] for campo in (*PARAMETRI_SOSTITUTIVA, *ISTITUTI_SOSTITUTIVA)},
        )
        for voce in dati.get("sostitutiva", [])
    )
    aggiuntive = tuple(
        DichiarazioneMensilitaAggiuntiva(
            voce["istituto"],
            _data(voce["dal"], "dal"),
            voce["riferimento"],
            _data(voce["al"], "al") if "al" in voce else None,
            voce.get("mese_pagamento"),
            voce.get("giorno_dal"),
            voce.get("giorno_al"),
        )
        for voce in dati.get("mensilita_aggiuntiva", [])
    )
    return RegoleFiscali(
        categorie, redditi, ritenute, conguagli, fisiologici, deduzioni, aliquote, addizionali, benefici, accessori, sostitutive,
        aggiuntive,
    )


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
        anche_se=tuple(voce["anche_se"]) if voce.get("anche_se") is not None else (),
    )
