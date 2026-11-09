"""Fisco del lavoro dipendente: anno d'imposta, imponibile fiscale, ritenuta e conguaglio (ADR 0015, 0019).

L'imposta riguarda la persona. Ogni pagamento ha la propria ritenuta, calcolata sulle somme pagate
nel periodo di paga (il mese della data di pagamento) con gli scaglioni annui ragguagliati al periodo e
le detrazioni rapportate. Il conguaglio è un calcolo distinto: l'imposta dell'anno sull'imponibile
fiscale della persona, meno quanto già operato. Legge solo gli esiti pagati e non li cambia: un
nuovo conguaglio è un nuovo importo, per differenza.

Il calcolo si ferma, e nomina il caso, quando serve ciò che questa fetta non modella: un pagamento
di competenza di un altro anno (tassazione separata, ADR 0018), una categoria di reddito che la
regola non copre, un conguaglio per differenza dopo il 28 febbraio (serve la cessazione).
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from . import addizionali
from .corpus import Corpus, RegolaConguaglio, RegolaRitenuta
from .errori import CasoNonModellato, ErroreCalcolo, FattoMancante, RedditoMancante
from .formula import valuta
from .modello import MATURAZIONI_FISCALI, Derivazione, Fatto, Importo, ParametroLetto, TipoEsito
from .registro import TIPO_ANNO_IMPOSTA_DIVERSO, TIPO_DICHIARAZIONE_SOSTITUITO, Registro, leggi_familiare
from .denuncia import MATURAZIONI_DERIVATE
from .denuncia_individuale import IMPIEGHI_TEMPO_DETERMINATO
from .tempo import Periodo, in_utc

PERIODI_MENSILI = 12  # periodi di paga in un anno per il mese: struttura del calendario, non un valore normativo
GIORNO_CASSA_ALLARGATA = 12  # art. 51 c. 1 TUIR: somme corrisposte entro il 12 gennaio
ULTIMO_GIORNO_CONGUAGLIO = (2, 28)  # entro il 28 febbraio (art. 23 c. 3 DPR 600/1973)

AVVISO_SENZA_DICHIARAZIONE = "senza_dichiarazione_sostituito"
AVVISO_PROIEZIONE = "proiezione_conguaglio"
AVVISO_ACCONTO_SENZA_BASE = "acconto_senza_base"
AVVISO_TEMPO_DETERMINATO = "tempo_determinato_sotto_soglia"
AVVISO_FAMILIARE_FUORI_ETA = "familiare_fuori_eta"
# Carichi di famiglia (ADR 0032): la regola di ritenuta ha una formula annua per gruppo di relazioni. Il figlio in luogo
# del coniuge usa quella del coniuge ma conta tra i figli dell'aumento della soglia.
FORMULA_PER_RELAZIONE = {
    "coniuge": "carichi_coniuge",
    "figlio_in_luogo_del_coniuge": "carichi_coniuge",
    "figlio": "carichi_figlio",
    "figlio_disabile": "carichi_figlio",
    "ascendente": "carichi_ascendente",
}
RELAZIONI_FIGLIO = frozenset({"figlio", "figlio_disabile", "figlio_in_luogo_del_coniuge"})
# Art. 12 c. 1 lett. c) TUIR (stessa lettera nel testo unico dal 2027): i figli danno diritto dal compimento del 21° anno,
# senza limite se disabili, altrimenti fino al mese prima del 30° compleanno (prassi: circ. AdE 4/E 2025, § 1.3).
ETA_INIZIO_FIGLI = 21
ETA_FINE_FIGLI = 30
# Art. 13 c. 1 lett. a TUIR: sotto questo reddito complessivo il tempo determinato ha un minimo di 1.380 euro, che il
# modello non applica (ADR 0019, ticket #93). È la soglia di un avviso, non entra in nessun calcolo.
SOGLIA_MINIMO_TEMPO_DETERMINATO = Decimal(15000)


@dataclass(frozen=True)
class Avviso:
    """Segnalazione che non ferma e non cambia nessuna ritenuta."""

    tipo: str
    messaggio: str
    persona: str
    anno: int | None = None
    valore: Decimal | None = None


@dataclass(frozen=True)
class ImponibileFiscale:
    """Base per persona e anno d'imposta: gli esiti pagati di tutti i suoi rapporti, in regime ordinario.

    `valore` è la somma dei redditi (`righe`) meno gli importi che l'istituto dichiara riduttivi (`deduzioni`).
    """

    persona: str
    anno: int
    valore: Decimal
    righe: tuple[Importo, ...]
    deduzioni: tuple[Importo, ...] = ()


@dataclass(frozen=True)
class FiscaleDelPagamento:
    """Ritenuta, conguaglio (con le addizionali dovute dell'anno nella sua derivazione) e importi delle addizionali (ADR 0029)."""

    ritenuta: Importo
    conguaglio: Importo | None = None
    avvisi: tuple[Avviso, ...] = ()
    addizionali: tuple[Importo, ...] = ()

    def avvisi_di(self, tipo: str) -> tuple[Avviso, ...]:
        return tuple(avviso for avviso in self.avvisi if avviso.tipo == tipo)


@dataclass(frozen=True)
class _Pagata:
    riga: Importo
    data: date | None
    valuta: date
    anno_esito: int | None


def anno_imposta(corpus: Corpus, categoria: str, data_pagamento: date) -> int:
    """Anno della data di pagamento, o l'anno prima per le somme pagate entro il 12 gennaio con la cassa allargata."""
    cassa = corpus.categoria_reddito(categoria).cassa_allargata_al(data_pagamento)
    if cassa is None:
        raise RedditoMancante(
            f"Categoria {categoria}: nessuna dichiarazione della cassa allargata per un pagamento del {data_pagamento}"
        )
    if cassa.vale and data_pagamento.month == 1 and data_pagamento.day <= GIORNO_CASSA_ALLARGATA:
        return data_pagamento.year - 1
    return data_pagamento.year


def _controlla_competenza(corpus: Corpus, importo: Importo, anno: int, data_pagamento: date) -> None:
    """Una competenza fuori dall'anno d'imposta ferma il calcolo, salvo il pagamento fisiologico dell'anno prima (ADR 0018).

    Il fermo nomina il caso. La dichiarazione dell'istituto si sceglie per la data di pagamento.
    """
    dal, al = importo.periodo.dal.year, importo.periodo.al.year
    if dal == al == anno:
        return
    soggetto = f"Rapporto {importo.rapporto}, istituto {importo.istituto}: caso non modellato"
    if dal != al:
        raise CasoNonModellato(
            f"{soggetto}, competenza {importo.periodo} a cavallo di due anni, pagata nell'anno d'imposta {anno}"
        )
    if dal > anno:
        raise CasoNonModellato(
            f"{soggetto}, competenza {importo.periodo} posteriore all'anno d'imposta {anno}"
        )
    if dal <= anno - 2:
        raise CasoNonModellato(
            f"{soggetto}, competenza {importo.periodo} di due o più anni prima dell'anno d'imposta {anno}: "
            "serve la causa del pagamento tardivo (tassazione separata, ADR 0018)"
        )
    if corpus.pagamento_fisiologico(importo.istituto, data_pagamento) is None:
        raise CasoNonModellato(
            f"{soggetto}, competenza {importo.periodo} pagata nell'anno d'imposta {anno}: l'istituto non dichiara "
            f"il pagamento fisiologico per un pagamento del {data_pagamento}, serve la causa del pagamento "
            "tardivo (tassazione separata, ADR 0018)"
        )


def attribuisci_reddito(corpus: Corpus, importi, valuta_prevista: date) -> tuple[Importo, ...]:
    """Categoria di reddito e anno d'imposta di ogni importo da pagare, da congelare nell'esito (ADR 0015).

    Gli importi che derivano dal pagato (contributi, ritenute) restano come sono. L'anno si calcola
    sulla valuta prevista; la dichiarazione dell'istituto si sceglie in base a quell'anno.
    """
    risultato = []
    for importo in importi:
        if importo.derivazione.maturazione in MATURAZIONI_DERIVATE:
            risultato.append(importo)
            continue
        dichiarazione = corpus.reddito(importo.istituto, valuta_prevista)
        if dichiarazione is None:
            raise RedditoMancante(
                f"Rapporto {importo.rapporto}, istituto {importo.istituto}: nessuna categoria di reddito "
                f"dichiarata per un pagamento del {valuta_prevista}"
            )
        categoria = dichiarazione.categoria
        anno = anno_imposta(corpus, categoria, valuta_prevista)
        if anno != valuta_prevista.year:
            dichiarata_all_anno = corpus.reddito(importo.istituto, date(anno, 12, 31))
            if dichiarata_all_anno is None or dichiarata_all_anno.categoria != categoria:
                raise CasoNonModellato(
                    f"Rapporto {importo.rapporto}, istituto {importo.istituto}: caso non modellato, la categoria di "
                    f"reddito cambia tra la data di pagamento {valuta_prevista} e l'anno d'imposta {anno}"
                )
        _controlla_competenza(corpus, importo, anno, valuta_prevista)
        risultato.append(replace(importo, anno_imposta=anno, categoria_reddito=categoria))
    return tuple(risultato)


def _controlla_anno_dei_pagamenti(registro: Registro, persona: str, istante: datetime) -> None:
    """Un pagamento eseguito in un anno d'imposta diverso dal previsto ferma il calcolo fiscale della persona (ADR 0025)."""
    for fatto in registro.fatti_persona_noti(persona, TIPO_ANNO_IMPOSTA_DIVERSO, istante):
        raise CasoNonModellato(
            f"Persona {persona}: caso non modellato, l'esito {int(fatto.valore)} è stato pagato il {fatto.valido_dal} "
            "senza l'attribuzione fiscale prevista (anno d'imposta diverso dal previsto, o competenza non più "
            "ammessa alla valuta reale): il calcolo fiscale si ferma"
        )


def _persona(registro: Registro, rapporto: str, istante: datetime) -> str:
    persona = registro.persona_del_rapporto(rapporto, istante)
    if persona is None:
        raise FattoMancante(f"Rapporto {rapporto}: manca il legame con la persona, serve per il calcolo fiscale")
    _controlla_anno_dei_pagamenti(registro, persona, istante)
    return persona


def _pagati(registro: Registro, persona: str, istante: datetime) -> list[_Pagata]:
    """Righe degli esiti pagati dei rapporti della persona, con la data di pagamento se registrata."""
    pagamenti = {rapporto: registro.pagamenti(rapporto, istante) for rapporto in registro.rapporti_della_persona(persona, istante)}
    pagate = []
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        for riga in esito.righe:
            if riga.rapporto in pagamenti:
                fatto = pagamenti[riga.rapporto].get(esito.id)
                anni = {r.anno_imposta for r in esito.righe if r.rapporto == riga.rapporto and _e_reddito(r)}
                anno_esito = anni.pop() if len(anni) == 1 else None
                pagate.append(_Pagata(riga, fatto.valido_dal if fatto else None, esito.data, anno_esito))
    return pagate


def _e_deduzione(corpus: Corpus, riga: Importo, giorno: date) -> bool:
    """Un importo derivato dal pagato che l'istituto dichiara riduttivo dell'imponibile fiscale alla data di pagamento."""
    return not _e_reddito(riga) and corpus.deduzione_fiscale(riga.istituto, giorno) is not None


def _anno_della_deduzione(pagata: _Pagata) -> int:
    """L'anno d'imposta del reddito pagato insieme alla deduzione; senza reddito, l'anno della data di pagamento."""
    return pagata.riga.anno_imposta or pagata.anno_esito or (pagata.data or pagata.valuta).year


def _e_reddito(riga: Importo) -> bool:
    return riga.derivazione.maturazione not in MATURAZIONI_DERIVATE


def _controlla_anno(riga: Importo) -> None:
    if riga.anno_imposta is None:
        raise RedditoMancante(
            f"Rapporto {riga.rapporto}, istituto {riga.istituto}: esito pagato senza anno d'imposta, "
            "l'importo va attribuito prima del pagamento"
        )


def imponibile_fiscale(
    registro: Registro, persona: str, anno: int, noto_al: datetime | None = None, *, corpus: Corpus | None = None
) -> ImponibileFiscale:
    """Somma gli esiti pagati di tutti i rapporti della persona attribuiti all'anno, con l'anno congelato.

    Con il `corpus`, toglie gli importi pagati che l'istituto dichiara riduttivi dell'imponibile fiscale
    (i contributi del lavoratore), scelti con la data di pagamento. Senza il corpus non ci sono dichiarazioni
    da leggere e l'imponibile resta la somma dei redditi.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    righe = []
    deduzioni = []
    for pagata in _pagati(registro, persona, istante):
        if _e_reddito(pagata.riga):
            _controlla_anno(pagata.riga)
            if pagata.riga.anno_imposta == anno:
                righe.append(pagata.riga)
        elif (
            corpus is not None
            and _e_deduzione(corpus, pagata.riga, pagata.data or pagata.valuta)
            and _anno_della_deduzione(pagata) == anno
        ):
            deduzioni.append(pagata.riga)
    valore = sum((riga.valore for riga in righe), Decimal(0)) - sum((riga.valore for riga in deduzioni), Decimal(0))
    return ImponibileFiscale(persona, anno, valore, tuple(righe), tuple(deduzioni))


@dataclass(frozen=True)
class _Voce:
    """Un familiare a carico in un mese: la formula annua del suo gruppo di relazioni e la quota."""

    gruppo: str
    formula: str
    percentuale: int
    fatto: Fatto | None


@dataclass(frozen=True)
class _CaricoMese:
    """I familiari che danno detrazione in un mese e il numero dei figli che danno diritto nello stesso mese."""

    figli: int
    voci: tuple[_Voce, ...]


@dataclass(frozen=True)
class _Calcolo:
    imponibile: Decimal
    imposta: Decimal
    detrazione: Decimal
    detrazione_automatica: Decimal
    dovuto: Decimal
    parametri: tuple[ParametroLetto, ...]
    fatti: tuple[Fatto, ...]
    carichi: Decimal = Decimal(0)
    dichiarata: bool = False
    testo_carichi: str = ""


def _mese_assoluto(anno: int, mese: int) -> int:
    return anno * 12 + mese - 1


def _da_diritto(relazione: str, nascita: date, anno: int, mese: int) -> bool:
    """Il familiare dà detrazione nel mese di paga: l'età conta per i figli, per mese e non per giorno (art. 12 c. 3)."""
    if relazione not in RELAZIONI_FIGLIO:
        return True
    corrente = _mese_assoluto(anno, mese)
    if corrente < _mese_assoluto(nascita.year + ETA_INIZIO_FIGLI, nascita.month):
        return False
    return relazione == "figlio_disabile" or corrente < _mese_assoluto(nascita.year + ETA_FINE_FIGLI, nascita.month)


def _carichi_del_mese(
    registro: Registro, regola: RegolaRitenuta, persona: str, anno: int, mese: int, istante: datetime
) -> tuple[_CaricoMese, tuple[Fatto, ...]]:
    """Familiari del mese che danno detrazione, e quelli registrati che non la danno per l'età (con un avviso)."""
    voci, fuori_eta, figli = [], [], 0
    for fatto in registro.familiari_a_carico_del_mese(persona, anno, mese, istante):
        familiare = leggi_familiare(fatto)
        if not _da_diritto(familiare.relazione, familiare.data_nascita, anno, mese):
            fuori_eta.append(fatto)
            continue
        figli += familiare.relazione in RELAZIONI_FIGLIO
        gruppo = FORMULA_PER_RELAZIONE[familiare.relazione]
        formula = getattr(regola, gruppo)
        if formula != "0":
            voci.append(_Voce(gruppo, formula, familiare.percentuale, fatto))
    return _CaricoMese(figli, tuple(voci)), tuple(fuori_eta)


def _dichiarazione(registro: Registro, persona: str, regola: RegolaRitenuta, giorno: date, istante: datetime) -> Fatto | None:
    fatto = registro.vigente_persona(persona, TIPO_DICHIARAZIONE_SOSTITUITO, giorno, istante)
    if fatto is not None and fatto.valore == regola.detrazione_richiesta:
        return fatto
    return None


def _calcola(
    corpus: Corpus,
    regola: RegolaRitenuta,
    imponibile: Decimal,
    periodi: int,
    riferimento: date,
    dichiarazione: Fatto | None,
    giorni: int = 1,
    giorni_anno: int = 1,
    categorie: frozenset[str] = frozenset(),
    carichi: tuple[_CaricoMese, ...] = (),
) -> _Calcolo:
    """Imposta, detrazioni e dovuto del periodo, o dell'anno con un solo periodo.

    La detrazione a richiesta c'è solo con la dichiarazione, la detrazione automatica sempre. Nella ritenuta del
    mese `giorni` e `giorni_anno` valgono 1: il rapporto è neutro e il periodo è un dodicesimo per pagamento.
    I `carichi` sono i mesi con familiari a carico: la ritenuta ne ha uno, il conguaglio fino a dodici (ADR 0032).
    Ogni familiare dà la formula annua per la sua quota, un dodicesimo per mese; i carichi non seguono i giorni di servizio.
    """
    parametri: dict[str, ParametroLetto] = {}
    valori_fisco = {
        "imponibile": imponibile,
        "periodi": Decimal(periodi),
        "giorni": Decimal(giorni),
        "giorni_anno": Decimal(giorni_anno),
        "figli": Decimal(0),
    }

    def risolvi(origine: str, nome: str) -> Decimal:
        if origine == "fisco":
            return valori_fisco[nome]
        vigenza = corpus.parametro(nome).vigenza_per(Periodo(riferimento, riferimento))
        parametri[nome] = ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento)
        return vigenza.valore

    imposta = valuta(regola.imposta, risolvi)
    detrazione = valuta(regola.detrazione, risolvi) if dichiarazione is not None else Decimal(0)
    spetta = not regola.categorie_detrazione_automatica or bool(categorie & set(regola.categorie_detrazione_automatica))
    automatica = valuta(regola.detrazione_automatica, risolvi) if spetta else Decimal(0)
    somma_carichi = Decimal(0)
    usati: dict[int, Fatto] = {}
    formule: set[str] = set()
    for mese in carichi:
        valori_fisco["figli"] = Decimal(mese.figli)
        for voce in mese.voci:
            somma_carichi += valuta(voce.formula, risolvi) * voce.percentuale / 100
            formule.add(f"{voce.gruppo.removeprefix('carichi_')}: {voce.formula}")
            if voce.fatto is not None:
                usati[voce.fatto.id] = voce.fatto
    detrazione_carichi = (somma_carichi / PERIODI_MENSILI).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return _Calcolo(
        imponibile,
        imposta,
        detrazione,
        automatica,
        max(Decimal(0), imposta - detrazione - automatica - detrazione_carichi),
        tuple(parametri[nome] for nome in sorted(parametri)),
        ((dichiarazione,) if dichiarazione is not None else ()) + tuple(usati[i] for i in sorted(usati)),
        detrazione_carichi,
        dichiarazione is not None,
        "; ".join(sorted(formule)),
    )


def _regola_ritenuta(corpus: Corpus, anno: int, data_pagamento: date) -> tuple[RegolaRitenuta, date]:
    """Regola e parametri si scelgono all'anno d'imposta: per un pagamento di gennaio dell'anno prima, al 31 dicembre."""
    riferimento = min(data_pagamento, date(anno, 12, 31))
    regola = corpus.regola_ritenuta(riferimento)
    if regola is None:
        raise ErroreCalcolo(f"Nessuna regola di ritenuta vigente per un pagamento del {data_pagamento} (anno d'imposta {anno})")
    return regola, riferimento


def _regola_conguaglio(corpus: Corpus, riferimento: date) -> RegolaConguaglio:
    regola = corpus.regola_conguaglio(riferimento)
    if regola is None:
        raise ErroreCalcolo(f"Nessuna regola di conguaglio vigente per il {riferimento}")
    return regola


def _controlla_righe(registro: Registro, rapporto: str, persona: str, righe, regola: RegolaRitenuta, istante: datetime) -> tuple[Importo, ...]:
    rapporti = set(registro.rapporti_della_persona(persona, istante))
    reddito = tuple(riga for riga in righe if _e_reddito(riga))
    if not reddito:
        raise ErroreCalcolo(f"Rapporto {rapporto}: nessun importo da tassare nel pagamento")
    for riga in reddito:
        if riga.rapporto not in rapporti:
            raise ErroreCalcolo(
                f"Rapporto {riga.rapporto}, istituto {riga.istituto}: l'importo è di un'altra persona, "
                f"non della persona {persona} del rapporto {rapporto}"
            )
        _controlla_anno(riga)
        if riga.categoria_reddito not in regola.categorie:
            raise CasoNonModellato(
                f"Rapporto {riga.rapporto}, istituto {riga.istituto}: caso non modellato, la ritenuta {regola.istituto} "
                f"non copre la categoria di reddito {riga.categoria_reddito}"
            )
    if len({riga.anno_imposta for riga in reddito}) > 1:
        raise CasoNonModellato(f"Rapporto {rapporto}: caso non modellato, un pagamento con più anni d'imposta")
    return reddito


def _categoria_unica(righe) -> str | None:
    categorie = {riga.categoria_reddito for riga in righe}
    return categorie.pop() if len(categorie) == 1 else None


def _riferimento_unito(*riferimenti: str) -> str:
    unici = []
    for riferimento in riferimenti:
        if riferimento not in unici:
            unici.append(riferimento)
    return " + ".join(unici)


def _ritenuta(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    persona: str,
    righe: tuple[Importo, ...],
    data_pagamento: date,
    istante: datetime,
    deduzioni: tuple[Importo, ...] = (),
) -> tuple[Importo, RegolaRitenuta, date, Fatto | None]:
    anno = righe[0].anno_imposta
    regola, riferimento = _regola_ritenuta(corpus, anno, data_pagamento)
    del_periodo = [
        pagata.riga
        for pagata in _pagati(registro, persona, istante)
        if pagata.data is not None
        and (pagata.data.year, pagata.data.month) == (data_pagamento.year, data_pagamento.month)
        and (_e_reddito(pagata.riga) or pagata.riga.istituto == regola.istituto)
        and pagata.riga.anno_imposta == anno
    ]
    gia_operate = [riga for riga in del_periodo if riga.istituto == regola.istituto]
    gia_pagate = [riga for riga in del_periodo if _e_reddito(riga)]
    gia_dedotte = [
        pagata.riga
        for pagata in _pagati(registro, persona, istante)
        if pagata.data is not None
        and (pagata.data.year, pagata.data.month) == (data_pagamento.year, data_pagamento.month)
        and _e_deduzione(corpus, pagata.riga, pagata.data)
        and _anno_della_deduzione(pagata) == anno
    ]
    imponibile = sum((riga.valore for riga in (*gia_pagate, *righe)), Decimal(0)) - sum(
        (riga.valore for riga in (*gia_dedotte, *deduzioni)), Decimal(0)
    )
    dichiarazione = _dichiarazione(registro, persona, regola, data_pagamento, istante)
    carico, _ = _carichi_del_mese(registro, regola, persona, data_pagamento.year, data_pagamento.month, istante)
    calcolo = _calcola(
        corpus, regola, imponibile, PERIODI_MENSILI, riferimento, dichiarazione,
        categorie=frozenset(riga.categoria_reddito for riga in (*gia_pagate, *righe)),
        carichi=(carico,),
    )
    operato = sum((riga.valore for riga in gia_operate), Decimal(0))
    importo = Importo(
        rapporto=rapporto,
        istituto=regola.istituto,
        periodo=Periodo(data_pagamento.replace(day=1), _ultimo_del_mese(data_pagamento)),
        valore=calcolo.dovuto - operato,
        anno_imposta=anno,
        categoria_reddito=_categoria_unica((*gia_pagate, *righe)),
        derivazione=Derivazione(
            istituto=regola.istituto,
            maturazione="ritenuta",
            regola_versione=regola.versione,
            riferimento=regola.riferimento,
            formula=(
                f"imposta del periodo = {regola.imposta}; detrazione rapportata = "
                f"{regola.detrazione if dichiarazione is not None else 'non applicata'}; "
                f"detrazione automatica = {regola.detrazione_automatica}; "
                f"{_formula_carichi(calcolo)}"
                "ritenuta = imposta meno detrazione meno detrazione automatica meno carichi di famiglia "
                "meno ritenute già operate nel periodo"
            ),
            versione_corpus=corpus.versione,
            noto_al=istante,
            parametri=calcolo.parametri,
            fatti=calcolo.fatti,
            importi=(*gia_pagate, *righe, *gia_dedotte, *deduzioni, *gia_operate),
        ),
    )
    return importo, regola, riferimento, dichiarazione


def _formula_carichi(calcolo: _Calcolo) -> str:
    if not calcolo.testo_carichi:
        return ""
    return (
        "detrazione carichi di famiglia = per ogni familiare a carico nel mese la formula annua della relazione "
        f"({calcolo.testo_carichi}) per la percentuale, un dodicesimo per mese; "
    )


def _ultimo_del_mese(giorno: date) -> date:
    return giorno.replace(day=calendar.monthrange(giorno.year, giorno.month)[1])


@dataclass(frozen=True)
class _Annuale:
    calcolo: _Calcolo
    operato: Decimal
    righe: tuple[Importo, ...]
    regola: RegolaConguaglio
    regola_ritenuta: RegolaRitenuta

    @property
    def valore(self) -> Decimal:
        return self.calcolo.dovuto - self.operato


def _giorni_di_servizio(registro: Registro, corpus: Corpus, persona: str, anno: int, istante: datetime) -> tuple[int, int]:
    """Giorni di servizio della persona nell'anno d'imposta e giorni dell'anno (ADR 0019, ticket #93).

    I giorni sono quelli del fatto di servizio del corpus sull'unione dei rapporti della persona, festivi compresi, e
    nessun giorno si conta due volte. Senza fatto di servizio nel corpus la persona ha servizio tutto l'anno.
    """
    anno_intero = Periodo(date(anno, 1, 1), date(anno, 12, 31))
    giorni_anno = len(anno_intero.giorni())
    if corpus.fatto_servizio is None:
        return giorni_anno, giorni_anno
    in_servizio = [False] * giorni_anno
    for rapporto in registro.rapporti_della_persona(persona, istante):
        vigenti = registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, anno_intero, istante)
        for indice, fatto in enumerate(vigenti):
            if fatto is not None:
                in_servizio[indice] = True
    return sum(in_servizio), giorni_anno


def _mesi_di_servizio(registro: Registro, corpus: Corpus, persona: str, anno: int, istante: datetime) -> frozenset[int]:
    """Mesi dell'anno con almeno un giorno di servizio della persona, su tutti i suoi rapporti (ADR 0032).

    Al conguaglio i carichi di famiglia contano solo in questi mesi: le istruzioni CU 2026 (prassi) li legano al
    periodo di lavoro, salvo la richiesta per l'intero anno (codice AC), non modellata. Senza fatto di servizio nel
    corpus la persona ha servizio tutto l'anno.
    """
    if corpus.fatto_servizio is None:
        return frozenset(range(1, PERIODI_MENSILI + 1))
    anno_intero = Periodo(date(anno, 1, 1), date(anno, 12, 31))
    giorni = anno_intero.giorni()
    mesi: set[int] = set()
    for rapporto in registro.rapporti_della_persona(persona, istante):
        vigenti = registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, anno_intero, istante)
        mesi.update(giorno.month for giorno, fatto in zip(giorni, vigenti) if fatto is not None)
    return frozenset(mesi)


def _ha_tempo_determinato(registro: Registro, corpus: Corpus, persona: str, anno: int, istante: datetime) -> bool:
    """Un rapporto della persona è a tempo determinato (tipo di impiego 17 o 18) in almeno un giorno dell'anno."""
    if corpus.fatto_servizio is None:
        return False
    anno_intero = Periodo(date(anno, 1, 1), date(anno, 12, 31))
    return any(
        fatto is not None and fatto.valore in IMPIEGHI_TEMPO_DETERMINATO
        for rapporto in registro.rapporti_della_persona(persona, istante)
        for fatto in registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, anno_intero, istante)
    )


def _annuale(
    registro: Registro,
    corpus: Corpus,
    persona: str,
    anno: int,
    data_pagamento: date,
    istante: datetime,
    righe_nuove: tuple[Importo, ...] = (),
    ritenute_nuove: tuple[Importo, ...] = (),
    deduzioni_nuove: tuple[Importo, ...] = (),
) -> _Annuale:
    """Imposta dell'anno sull'imponibile fiscale della persona, meno ritenute e conguagli già operati."""
    regola_ritenuta, riferimento = _regola_ritenuta(corpus, anno, data_pagamento)
    regola = _regola_conguaglio(corpus, riferimento)
    base = imponibile_fiscale(registro, persona, anno, istante, corpus=corpus)
    reddito = (*base.righe, *righe_nuove)
    deduzioni = (*base.deduzioni, *deduzioni_nuove)
    for riga in reddito:
        if riga.categoria_reddito not in regola_ritenuta.categorie:
            raise CasoNonModellato(
                f"Rapporto {riga.rapporto}, istituto {riga.istituto}: caso non modellato, il conguaglio {regola.istituto} "
                f"non copre la categoria di reddito {riga.categoria_reddito}"
            )
    operate = [
        pagata.riga
        for pagata in _pagati(registro, persona, istante)
        if pagata.riga.derivazione.maturazione in MATURAZIONI_FISCALI
        and pagata.riga.istituto in (regola_ritenuta.istituto, regola.istituto)
        and pagata.riga.anno_imposta == anno
    ]
    operate += list(ritenute_nuove)
    dichiarazione = _dichiarazione(registro, persona, regola_ritenuta, data_pagamento, istante)
    giorni, giorni_anno = _giorni_di_servizio(registro, corpus, persona, anno, istante)
    carichi = tuple(
        _carichi_del_mese(registro, regola_ritenuta, persona, anno, mese, istante)[0]
        for mese in sorted(_mesi_di_servizio(registro, corpus, persona, anno, istante))
    )
    calcolo = _calcola(
        corpus,
        regola_ritenuta,
        sum((riga.valore for riga in reddito), Decimal(0)) - sum((riga.valore for riga in deduzioni), Decimal(0)),
        1,
        riferimento,
        dichiarazione,
        giorni,
        giorni_anno,
        frozenset(riga.categoria_reddito for riga in reddito),
        carichi,
    )
    return _Annuale(
        calcolo, sum((riga.valore for riga in operate), Decimal(0)), (*reddito, *deduzioni, *operate), regola, regola_ritenuta
    )


def _importo_conguaglio(
    corpus: Corpus, rapporto: str, anno: int, annuale: _Annuale, istante: datetime
) -> Importo:
    regola = annuale.regola
    return Importo(
        rapporto=rapporto,
        istituto=regola.istituto,
        periodo=Periodo(date(anno, 1, 1), date(anno, 12, 31)),
        valore=annuale.valore,
        anno_imposta=anno,
        categoria_reddito=_categoria_unica(riga for riga in annuale.righe if _e_reddito(riga)),
        derivazione=Derivazione(
            istituto=regola.istituto,
            maturazione="conguaglio",
            regola_versione=regola.versione,
            riferimento=_riferimento_unito(regola.riferimento, annuale.regola_ritenuta.riferimento),
            formula=(
                f"imposta dell'anno = {annuale.regola_ritenuta.imposta}; detrazione = "
                f"{annuale.regola_ritenuta.detrazione if annuale.calcolo.dichiarata else 'non applicata'}; "
                f"detrazione automatica = {annuale.regola_ritenuta.detrazione_automatica}; "
                f"{_formula_carichi(annuale.calcolo)}"
                "conguaglio = imposta meno detrazione meno detrazione automatica meno carichi di famiglia "
                "meno ritenute e conguagli già operati, con un solo periodo"
            ),
            versione_corpus=corpus.versione,
            noto_al=istante,
            parametri=annuale.calcolo.parametri,
            fatti=annuale.calcolo.fatti,
            importi=annuale.righe,
        ),
    )


def pagamento_finale(
    registro: Registro, corpus: Corpus, persona: str, anno: int, valuta: date, noto_al: datetime | None = None
) -> bool:
    """Un pagamento della persona alla `valuta` dopo il quale nessun suo rapporto ha servizio nell'anno d'imposta.

    La fine del servizio è la fine del fatto di servizio del corpus (ADR 0019: alla cessazione il conguaglio si fa
    sul pagamento finale); il registro non ha un fatto «cessazione». Vale per la persona: se un altro suo rapporto
    ha ancora servizio, non è finale. Serve che la persona abbia avuto servizio fino alla valuta. Per una valuta
    oltre il 31 dicembre (cassa allargata) conta il servizio del giorno dopo la valuta.
    """
    if corpus.fatto_servizio is None:
        return False
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    dopo = valuta + timedelta(days=1)
    seguente = Periodo(dopo, max(date(anno, 12, 31), dopo))
    avuto = False
    for rapporto in registro.rapporti_della_persona(persona, istante):
        if any(fatto.valido_dal <= valuta for fatto in registro.fatti_noti(rapporto, corpus.fatto_servizio, istante)):
            avuto = True
        if any(fatto is not None for fatto in registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, seguente, istante)):
            return False
    return avuto


def _controlla_ultimo(registro: Registro, persona: str, anno: int, data_pagamento: date, istante: datetime) -> None:
    successivi = [
        pagata
        for pagata in _pagati(registro, persona, istante)
        if _e_reddito(pagata.riga)
        and pagata.riga.anno_imposta == anno
        and pagata.data is not None
        and pagata.data > data_pagamento
    ]
    if successivi:
        raise ErroreCalcolo(
            f"Persona {persona}: il pagamento del {data_pagamento} non è l'ultimo attribuito all'anno {anno}: "
            f"ce n'è uno del {max(pagata.data for pagata in successivi)}"
        )


def calcola_fiscale(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    righe,
    data_pagamento: date,
    ultimo_dell_anno: bool = False,
    noto_al: datetime | None = None,
) -> FiscaleDelPagamento:
    """Ritenuta del pagamento e, sull'ultimo pagamento attribuito all'anno, conguaglio.

    `righe` sono gli importi del pagamento, già attribuiti con `attribuisci_reddito`; la ritenuta è
    operata sul `rapporto` indicato. L'ultimo pagamento dell'anno non si ricava dal registro, che
    non conosce i pagamenti futuri: lo dichiara il chiamante, e il calcolo rifiuta un pagamento
    che ne ha già uno successivo. Senza `ultimo_dell_anno` il conguaglio resta una proiezione.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    persona = _persona(registro, rapporto, istante)
    righe = tuple(righe)
    regola_provvisoria = None
    for riga in righe:
        if _e_reddito(riga):
            _controlla_anno(riga)
            regola_provvisoria, _ = _regola_ritenuta(corpus, riga.anno_imposta, data_pagamento)
            break
    if regola_provvisoria is None:
        raise ErroreCalcolo(f"Rapporto {rapporto}: nessun importo da tassare nel pagamento")
    reddito = _controlla_righe(registro, rapporto, persona, righe, regola_provvisoria, istante)
    anno = reddito[0].anno_imposta
    deduzioni = tuple(riga for riga in righe if _e_deduzione(corpus, riga, data_pagamento))
    ritenuta, regola, riferimento, dichiarazione = _ritenuta(
        registro, corpus, rapporto, persona, reddito, data_pagamento, istante, deduzioni
    )
    avvisi: list[Avviso] = []
    if dichiarazione is None:
        avvisi.append(
            Avviso(
                AVVISO_SENZA_DICHIARAZIONE,
                f"Persona {persona}: senza dichiarazione del sostituito per {regola.detrazione_richiesta}, "
                "nessuna detrazione nella ritenuta",
                persona,
                anno,
            )
        )
    _, fuori_eta = _carichi_del_mese(registro, regola, persona, data_pagamento.year, data_pagamento.month, istante)
    for fatto in fuori_eta:
        familiare = leggi_familiare(fatto)
        avvisi.append(
            Avviso(
                AVVISO_FAMILIARE_FUORI_ETA,
                f"Persona {persona}: il familiare {familiare.codice_fiscale} ({familiare.relazione}) è registrato ma, "
                "per l'età, nel mese del pagamento non dà detrazione",
                persona,
                anno,
            )
        )
    conguaglio, chiusura, finale = None, (), False
    if ultimo_dell_anno:
        _controlla_ultimo(registro, persona, anno, data_pagamento, istante)
        annuale = _annuale(
            registro, corpus, persona, anno, data_pagamento, istante, reddito, (ritenuta,), deduzioni
        )
        conguaglio = _importo_conguaglio(corpus, rapporto, anno, annuale, istante)
        if annuale.calcolo.imponibile < SOGLIA_MINIMO_TEMPO_DETERMINATO and _ha_tempo_determinato(
            registro, corpus, persona, anno, istante
        ):
            avvisi.append(
                Avviso(
                    AVVISO_TEMPO_DETERMINATO,
                    f"Persona {persona}: rapporto a tempo determinato e imponibile {annuale.calcolo.imponibile} "
                    f"sotto {SOGLIA_MINIMO_TEMPO_DETERMINATO}: il minimo della detrazione per il tempo determinato "
                    "non è applicato",
                    persona,
                    anno,
                    annuale.calcolo.imponibile,
                )
            )
        finale = corpus.regola_addizionali(riferimento) is not None and pagamento_finale(
            registro, corpus, persona, anno, data_pagamento, istante
        )
        conguaglio, chiusura = _con_le_addizionali_dovute(
            registro, corpus, conguaglio, persona, anno, annuale, riferimento, finale, istante
        )
    else:
        annuale = _annuale(
            registro, corpus, persona, anno, data_pagamento, istante, reddito, (ritenuta,), deduzioni
        )
        avvisi.append(_avviso_proiezione(persona, anno, annuale))
    rate = addizionali.RateDelMese() if finale else _rate_delle_addizionali(
        registro, corpus, rapporto, persona, data_pagamento, istante
    )
    if rate.acconto_senza_base is not None:
        avvisi.append(
            Avviso(
                AVVISO_ACCONTO_SENZA_BASE,
                f"Persona {persona}: senza il conguaglio dell'anno prima né il reddito dell'anno precedente, "
                f"niente acconto dell'addizionale comunale {rate.acconto_senza_base}: passa tutto al saldo",
                persona,
                rate.acconto_senza_base,
            )
        )
    return FiscaleDelPagamento(ritenuta, conguaglio, tuple(avvisi), (*chiusura, *rate.importi))


def _rate_delle_addizionali(
    registro: Registro, corpus: Corpus, rapporto: str, persona: str, data_pagamento: date, istante: datetime
) -> addizionali.RateDelMese:
    regola = corpus.regola_addizionali(data_pagamento)
    if regola is None:
        return addizionali.RateDelMese()
    return addizionali.rate_del_mese(
        registro, corpus, regola, rapporto, persona, data_pagamento, istante,
        lambda anno: imponibile_fiscale(registro, persona, anno, istante, corpus=corpus).valore,
    )


def _con_le_addizionali_dovute(
    registro: Registro,
    corpus: Corpus,
    conguaglio: Importo,
    persona: str,
    anno: int,
    annuale: _Annuale,
    riferimento: date,
    finale: bool,
    istante: datetime,
) -> tuple[Importo, tuple[Importo, ...]]:
    """Il conguaglio porta le addizionali dell'anno nella sua derivazione, da cui si ricava il residuo da trattenere.

    Restituisce anche gli importi che il pagamento trattiene o restituisce subito (credito, cessazione).
    """
    regola = corpus.regola_addizionali(riferimento)
    if regola is None:
        return conguaglio, ()
    dovute = addizionali.dovute_dell_anno(
        registro, corpus, regola, conguaglio.rapporto, persona, anno,
        annuale.calcolo.imponibile, annuale.calcolo.dovuto, istante,
    )
    derivazione = replace(conguaglio.derivazione, importi=(*conguaglio.derivazione.importi, *dovute))
    chiusura = addizionali.chiusura_dell_anno(
        registro, corpus, regola, conguaglio.rapporto, persona, anno, dovute, finale, istante
    )
    return replace(conguaglio, derivazione=derivazione), chiusura


def _avviso_proiezione(persona: str, anno: int, annuale: _Annuale) -> Avviso:
    return Avviso(
        AVVISO_PROIEZIONE,
        f"Persona {persona}: se l'anno {anno} finisse qui, il conguaglio sarebbe {annuale.valore}: "
        f"dovuto {annuale.calcolo.dovuto}, già operato {annuale.operato}",
        persona,
        anno,
        annuale.valore,
    )


def proiezione_conguaglio(
    registro: Registro, corpus: Corpus, persona: str, anno: int, data_pagamento: date, noto_al: datetime | None = None
) -> Avviso:
    """Il conguaglio che risulterebbe sugli esiti pagati fino ad ora: un avviso, non cambia le ritenute."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    _controlla_anno_dei_pagamenti(registro, persona, istante)
    return _avviso_proiezione(persona, anno, _annuale(registro, corpus, persona, anno, data_pagamento, istante))


def conguaglio_per_differenza(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    anno: int,
    data_pagamento: date,
    noto_al: datetime | None = None,
) -> Importo | None:
    """Nuovo conguaglio dell'anno, per differenza con quanto già operato; None se non c'è differenza.

    Si fa su un pagamento dell'anno, o entro il 28 febbraio dell'anno dopo. Dopo, serve la
    cessazione, che il modello non ha ancora: il calcolo si ferma. Gli esiti già fissati non cambiano.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    limite = date(anno + 1, *ULTIMO_GIORNO_CONGUAGLIO)
    if not date(anno, 1, 1) <= data_pagamento <= limite:
        raise CasoNonModellato(
            f"Rapporto {rapporto}: caso non modellato, conguaglio per differenza dell'anno {anno} su un pagamento "
            f"del {data_pagamento}: dopo il 28 febbraio serve la cessazione, non ancora modellata"
        )
    persona = _persona(registro, rapporto, istante)
    annuale = _annuale(registro, corpus, persona, anno, data_pagamento, istante)
    _controlla_addizionali_invariate(registro, corpus, rapporto, persona, anno, data_pagamento, annuale, istante)
    if annuale.valore == 0:
        return None
    return _importo_conguaglio(corpus, rapporto, anno, annuale, istante)


def _controlla_addizionali_invariate(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    persona: str,
    anno: int,
    data_pagamento: date,
    annuale: _Annuale,
    istante: datetime,
) -> None:
    """Il conguaglio per differenza non ricalcola ancora le addizionali (ADR 0029): se cambierebbero, si ferma."""
    _, riferimento = _regola_ritenuta(corpus, anno, data_pagamento)
    regola = corpus.regola_addizionali(riferimento)
    if regola is None:
        return
    pagate = addizionali.dovute_pagate(registro, regola, persona, anno, istante)
    nuove = addizionali.dovute_dell_anno(
        registro, corpus, regola, rapporto, persona, anno, annuale.calcolo.imponibile, annuale.calcolo.dovuto, istante
    )
    if any(pagate.get(dovuta.istituto) != dovuta.valore for dovuta in nuove):
        raise CasoNonModellato(
            f"Rapporto {rapporto}: caso non modellato, il conguaglio per differenza dell'anno {anno} cambierebbe le "
            "addizionali, che non ricalcola ancora"
        )
