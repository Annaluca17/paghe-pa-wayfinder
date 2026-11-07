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
from decimal import Decimal

from .corpus import Corpus, RegolaConguaglio, RegolaRitenuta
from .errori import CasoNonModellato, ErroreCalcolo, FattoMancante, RedditoMancante
from .formula import valuta
from .modello import MATURAZIONI_FISCALI, Derivazione, Fatto, Importo, ParametroLetto, TipoEsito
from .registro import TIPO_ANNO_IMPOSTA_DIVERSO, TIPO_DICHIARAZIONE_SOSTITUITO, Registro
from .denuncia import MATURAZIONI_DERIVATE
from .tempo import Periodo, in_utc

PERIODI_MENSILI = 12  # periodi di paga in un anno per il mese: struttura del calendario, non un valore normativo
GIORNO_CASSA_ALLARGATA = 12  # art. 51 c. 1 TUIR: somme corrisposte entro il 12 gennaio
ULTIMO_GIORNO_CONGUAGLIO = (2, 28)  # entro il 28 febbraio (art. 23 c. 3 DPR 600/1973)

AVVISO_SENZA_DICHIARAZIONE = "senza_dichiarazione_sostituito"
AVVISO_PROIEZIONE = "proiezione_conguaglio"
AVVISO_RIDUZIONE_TFR = "riduzione_tfr_senza_effetto_fiscale"
# Nome convenzionale dell'istituto della riduzione del lordo TFR (ADR 0010), com'è nel corpus: serve solo all'avviso.
ISTITUTO_RIDUZIONE_TFR = "riduzione_tfr"


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
    ritenuta: Importo
    conguaglio: Importo | None = None
    avvisi: tuple[Avviso, ...] = ()

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
class _Calcolo:
    imposta: Decimal
    detrazione: Decimal
    dovuto: Decimal
    parametri: tuple[ParametroLetto, ...]
    fatti: tuple[Fatto, ...]


def _dichiarazione(registro: Registro, persona: str, regola: RegolaRitenuta, giorno: date, istante: datetime) -> Fatto | None:
    fatto = registro.vigente_persona(persona, TIPO_DICHIARAZIONE_SOSTITUITO, giorno, istante)
    if fatto is not None and fatto.valore == regola.detrazione_richiesta:
        return fatto
    return None


def _calcola(
    corpus: Corpus, regola: RegolaRitenuta, imponibile: Decimal, periodi: int, riferimento: date, dichiarazione: Fatto | None
) -> _Calcolo:
    """Imposta, detrazione (solo con la dichiarazione) e dovuto del periodo, o dell'anno con un solo periodo."""
    parametri: dict[str, ParametroLetto] = {}

    def risolvi(origine: str, nome: str) -> Decimal:
        if origine == "fisco":
            return imponibile if nome == "imponibile" else Decimal(periodi)
        vigenza = corpus.parametro(nome).vigenza_per(Periodo(riferimento, riferimento))
        parametri[nome] = ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento)
        return vigenza.valore

    imposta = valuta(regola.imposta, risolvi)
    detrazione = valuta(regola.detrazione, risolvi) if dichiarazione is not None else Decimal(0)
    return _Calcolo(
        imposta,
        detrazione,
        max(Decimal(0), imposta - detrazione),
        tuple(parametri[nome] for nome in sorted(parametri)),
        (dichiarazione,) if dichiarazione is not None else (),
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
    calcolo = _calcola(corpus, regola, imponibile, PERIODI_MENSILI, riferimento, dichiarazione)
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
                "ritenuta = imposta meno detrazione meno ritenute già operate nel periodo"
            ),
            versione_corpus=corpus.versione,
            noto_al=istante,
            parametri=calcolo.parametri,
            fatti=calcolo.fatti,
            importi=(*gia_pagate, *righe, *gia_dedotte, *deduzioni, *gia_operate),
        ),
    )
    return importo, regola, riferimento, dichiarazione


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
    calcolo = _calcola(
        corpus,
        regola_ritenuta,
        sum((riga.valore for riga in reddito), Decimal(0)) - sum((riga.valore for riga in deduzioni), Decimal(0)),
        1,
        riferimento,
        dichiarazione,
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
                f"{annuale.regola_ritenuta.detrazione if annuale.calcolo.fatti else 'non applicata'}; "
                "conguaglio = imposta meno detrazione meno ritenute e conguagli già operati, con un solo periodo"
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
    ritenuta, regola, _, dichiarazione = _ritenuta(
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
    for riga in righe:
        if riga.istituto == ISTITUTO_RIDUZIONE_TFR and not _e_deduzione(corpus, riga, data_pagamento):
            avvisi.append(
                Avviso(
                    AVVISO_RIDUZIONE_TFR,
                    f"Persona {persona}: la riduzione TFR di {riga.valore} non riduce l'imponibile fiscale della "
                    "ritenuta: il DPCM 20/12/1999 e la sentenza Corte cost. 213/2018 parlano di invarianza della "
                    "retribuzione netta e dell'imponibile fiscale rispetto al TFS, effetto da verificare (ticket #70)",
                    persona,
                    anno,
                    riga.valore,
                )
            )
    conguaglio = None
    if ultimo_dell_anno:
        _controlla_ultimo(registro, persona, anno, data_pagamento, istante)
        annuale = _annuale(
            registro, corpus, persona, anno, data_pagamento, istante, reddito, (ritenuta,), deduzioni
        )
        conguaglio = _importo_conguaglio(corpus, rapporto, anno, annuale, istante)
    else:
        annuale = _annuale(
            registro, corpus, persona, anno, data_pagamento, istante, reddito, (ritenuta,), deduzioni
        )
        avvisi.append(_avviso_proiezione(persona, anno, annuale))
    return FiscaleDelPagamento(ritenuta, conguaglio, tuple(avvisi))


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
    if annuale.valore == 0:
        return None
    return _importo_conguaglio(corpus, rapporto, anno, annuale, istante)
