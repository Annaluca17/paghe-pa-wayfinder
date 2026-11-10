"""Incapienza del conguaglio IRPEF e richiesta di differimento (ticket #99, ADR 0034).

La capienza del conguaglio è il netto del pagamento senza il conguaglio: se il conguaglio a debito la supera si trattiene
solo fino a netto zero, e il resto è l'incapienza. Solo il conguaglio IRPEF: se il netto resta negativo per altro, il
fermo «netto negativo» resta.

Senza la richiesta di differimento (fatto della persona) il resto è un importo **non trattenuto**, nella derivazione del
conguaglio, che la vista CU legge. Con la richiesta è una decisione di **resto differito**, anch'essa nella derivazione
del conguaglio: non è un fatto, ogni pagamento successivo ricava il resto aperto dagli esiti pagati (come il riporto
dei recuperi e le rate dei benefici) e trattiene interesse e resto fino a capienza. Alla fine del differimento il resto
ancora aperto diventa non trattenuto.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from .corpus import SUFFISSO_INTERESSE, SUFFISSO_NON_TRATTENUTO, SUFFISSO_RESTO, Corpus
from .errori import ParametroMancante
from .modello import (
    MATURAZIONE_INTERESSE,
    MATURAZIONE_NON_TRATTENUTO,
    MATURAZIONE_RESTO_DA_DIFFERIRE,
    MATURAZIONE_RESTO_DIFFERITO,
    Derivazione,
    Fatto,
    Importo,
    ParametroLetto,
)
from .tempo import Periodo

PARAMETRO_INTERESSE = "interesse_differimento_mensile"
CENTESIMO = Decimal("0.01")
MESE_DI_CHIUSURA = 12


def anno_di_trattenuta(giorno: date) -> int:
    """L'anno in cui si trattiene il resto: quello del conguaglio, o il successivo se il conguaglio è di dicembre.

    Lettura nostra di «ultimo pagamento di dicembre dell'anno in cui si trattiene» (ADR 0034): un conguaglio fatto
    nell'ultimo pagamento dell'anno non avrebbe nessun pagamento in cui differire.
    """
    return giorno.year + (1 if giorno.month == MESE_DI_CHIUSURA else 0)


def _ultimo_del_mese(giorno: date) -> date:
    primo_dopo = date(giorno.year + (giorno.month == 12), giorno.month % 12 + 1, 1)
    return date.fromordinal(primo_dopo.toordinal() - 1)


def _periodo_del_mese(giorno: date) -> Periodo:
    return Periodo(giorno.replace(day=1), _ultimo_del_mese(giorno))


def _senza_derivazione(importo: Importo) -> Importo:
    """Il riferimento a un importo già pagato senza il suo albero: ogni riga cita le precedenti e l'albero raddoppierebbe."""
    return replace(importo, derivazione=replace(importo.derivazione, importi=()))


def _importo_derivato(
    conguaglio: Importo,
    istituto: str,
    maturazione: str,
    periodo: Periodo,
    valore: Decimal,
    formula: str,
    istante: datetime,
    parametri: tuple[ParametroLetto, ...] = (),
    fatti: tuple[Fatto, ...] = (),
    importi: tuple[Importo, ...] = (),
    riferimenti: tuple[str, ...] = (),
) -> Importo:
    origine = conguaglio.derivazione
    riferimento = " + ".join(dict.fromkeys((origine.riferimento, *riferimenti)))
    return Importo(
        rapporto=conguaglio.rapporto,
        istituto=istituto,
        periodo=periodo,
        valore=valore,
        anno_imposta=conguaglio.anno_imposta,
        categoria_reddito=conguaglio.categoria_reddito,
        derivazione=Derivazione(
            istituto=istituto,
            maturazione=maturazione,
            regola_versione=origine.regola_versione,
            riferimento=riferimento,
            formula=formula,
            versione_corpus=origine.versione_corpus,
            noto_al=istante,
            parametri=parametri,
            fatti=fatti,
            importi=importi,
        ),
    )


def _istituto_base(istituto_del_resto: str) -> str:
    return istituto_del_resto[: -len(SUFFISSO_RESTO)]


def dividi_conguaglio(
    conguaglio: Importo,
    capienza: Decimal,
    richiesta: Fatto | None,
    finale: bool,
    valuta: date,
    istante: datetime,
) -> Importo:
    """Il conguaglio a debito portato alla `capienza`: si trattiene fino lì, il resto è differito o non trattenuto.

    `richiesta` è il fatto vigente alla valuta. Alla cessazione (`finale`) nessun pagamento successivo prenderebbe il
    resto: è non trattenuto anche con la richiesta.
    """
    resto = conguaglio.valore - capienza
    base = (
        f"incapienza: conguaglio {conguaglio.valore} oltre la capienza del netto senza il conguaglio ({capienza}), "
        f"si trattiene {capienza} e il resto è {resto}"
    )
    if richiesta is not None and not finale:
        decisione = _importo_derivato(
            conguaglio, f"{conguaglio.istituto}{SUFFISSO_RESTO}", MATURAZIONE_RESTO_DA_DIFFERIRE, Periodo(valuta, valuta), resto,
            f"resto = conguaglio ({conguaglio.valore}) meno capienza ({capienza}); richiesta di differimento valida dal "
            f"{richiesta.valido_dal}: il resto si trattiene nei pagamenti successivi con l'interesse, fino all'ultimo "
            f"pagamento di dicembre del {anno_di_trattenuta(valuta)} o alla cessazione",
            istante, fatti=(richiesta,),
        )
        testo = f"{base}; con la richiesta di differimento il resto è differito"
        fatti = (*conguaglio.derivazione.fatti, richiesta)
    else:
        motivo = "alla cessazione" if finale else "senza richiesta di differimento"
        decisione = _importo_derivato(
            conguaglio, f"{conguaglio.istituto}{SUFFISSO_NON_TRATTENUTO}", MATURAZIONE_NON_TRATTENUTO, conguaglio.periodo, resto,
            f"non trattenuto = conguaglio ({conguaglio.valore}) meno capienza ({capienza}), {motivo}: la CU lo riporta e la "
            "persona lo versa entro il 15 gennaio",
            istante,
        )
        testo = f"{base}; {motivo} è non trattenuto"
        fatti = conguaglio.derivazione.fatti
    derivazione = replace(
        conguaglio.derivazione,
        formula=f"{conguaglio.derivazione.formula}; {testo}",
        fatti=fatti,
        importi=(*conguaglio.derivazione.importi, decisione),
    )
    return replace(conguaglio, valore=capienza, derivazione=derivazione)


# Resto aperto, dagli esiti pagati

@dataclass(frozen=True)
class Resto:
    """Un resto differito deciso da un conguaglio pagato, con le trattenute già fatte."""

    decisione: Importo
    data: date
    trattenute: tuple[tuple[Importo, date], ...]
    interessi: tuple[date, ...] = ()

    @property
    def aperto(self) -> Decimal:
        return self.decisione.valore - sum((riga.valore for riga, _ in self.trattenute), Decimal(0))

    @property
    def ultimo_movimento(self) -> date:
        """Anche un interesse trattenuto senza quota del resto è un movimento: l'interesse non si paga due volte."""
        return max((*(giorno for _, giorno in self.trattenute), *self.interessi), default=self.data)

    @property
    def anno_di_trattenuta(self) -> int:
        return anno_di_trattenuta(self.data)

    @property
    def istituto_interesse(self) -> str:
        return _istituto_base(self.decisione.istituto) + SUFFISSO_INTERESSE


def resti_aperti(pagate: list[tuple[Importo, date]]) -> list[Resto]:
    """I resti differiti dei conguagli pagati non ancora chiusi (trattenuti per intero o passati a non trattenuto)."""
    decisioni: dict[tuple, tuple[Importo, date]] = {}
    for riga, giorno in pagate:
        if riga.derivazione.maturazione != "conguaglio":
            continue
        for importo in riga.derivazione.importi:
            if importo.derivazione.maturazione == MATURAZIONE_RESTO_DA_DIFFERIRE:
                decisioni[(importo.istituto, importo.anno_imposta, importo.periodo)] = (importo, giorno)
    aperti = []
    for (istituto, anno, periodo), (decisione, giorno) in sorted(decisioni.items(), key=lambda voce: voce[1][1]):
        trattenute = tuple(
            (riga, data)
            for riga, data in pagate
            if riga.istituto == istituto
            and riga.anno_imposta == anno
            and riga.derivazione.maturazione == MATURAZIONE_RESTO_DIFFERITO
            and riga.derivazione.importi
            and riga.derivazione.importi[0].periodo == periodo
        )
        chiuso = any(
            importo.derivazione.maturazione == MATURAZIONE_NON_TRATTENUTO
            for riga, _ in trattenute
            for importo in riga.derivazione.importi
        )
        interessi = tuple(
            data
            for riga, data in pagate
            if riga.istituto == _istituto_base(istituto) + SUFFISSO_INTERESSE
            and riga.anno_imposta == anno
            and riga.derivazione.maturazione == MATURAZIONE_INTERESSE
            and riga.derivazione.importi
            and riga.derivazione.importi[0].periodo == periodo
        )
        resto = Resto(decisione, giorno, trattenute, interessi)
        if not chiuso and resto.aperto > 0:
            aperti.append(resto)
    return aperti


def _parametro_interesse(corpus: Corpus, giorno: date) -> ParametroLetto:
    try:
        parametro = corpus.parametro(PARAMETRO_INTERESSE)
    except KeyError:
        raise ParametroMancante(
            f"Parametro {PARAMETRO_INTERESSE}: il corpus non lo dichiara, serve all'interesse sul resto differito"
        ) from None
    vigenza = parametro.vigenza_per(Periodo(giorno, giorno))
    return ParametroLetto(PARAMETRO_INTERESSE, vigenza.valore, vigenza.dal, vigenza.riferimento)


def fine_del_differimento(resto: Resto, valuta: date, ultimo_di_dicembre: bool, finale: bool) -> bool:
    """All'ultimo pagamento di dicembre dell'anno di trattenuta, o alla cessazione se viene prima (ADR 0034)."""
    anno = resto.anno_di_trattenuta
    return finale or valuta.year > anno or (valuta.year == anno and valuta.month == MESE_DI_CHIUSURA and ultimo_di_dicembre)


def trattieni_resto(
    corpus: Corpus, resto: Resto, rapporto: str, capienza: Decimal, valuta: date, fine: bool, istante: datetime
) -> tuple[tuple[Importo, ...], Decimal]:
    """Interesse e resto trattenuti nel pagamento, fino alla `capienza`; alla `fine` quel che resta è non trattenuto.

    L'interesse è semplice, per i mesi dall'ultimo movimento del resto, sul resto aperto; si trattiene prima, il resto
    con quello che avanza. Restituisce gli importi da comporre e la capienza che rimane al conguaglio del pagamento.
    """
    parametro = _parametro_interesse(corpus, valuta)
    decisione = _senza_derivazione(resto.decisione)
    precedenti = tuple(_senza_derivazione(riga) for riga, _ in resto.trattenute)
    mesi = (valuta.year - resto.ultimo_movimento.year) * 12 + valuta.month - resto.ultimo_movimento.month
    dovuto = (resto.aperto * parametro.valore * max(mesi, 0)).quantize(CENTESIMO, rounding=ROUND_HALF_UP)
    capienza = max(capienza, Decimal(0))
    interesse = min(dovuto, capienza)
    capienza -= interesse
    trattenuto = min(resto.aperto, capienza)
    capienza -= trattenuto
    mese = _periodo_del_mese(valuta)
    conguaglio = replace(resto.decisione, rapporto=rapporto)
    non_trattenuto = resto.aperto - trattenuto if fine else Decimal(0)
    importi: list[Importo] = []
    if trattenuto > 0 or non_trattenuto > 0:
        chiusura: tuple[Importo, ...] = ()
        testo = ""
        if non_trattenuto > 0:
            chiusura = (
                _importo_derivato(
                    conguaglio, _istituto_base(resto.decisione.istituto) + SUFFISSO_NON_TRATTENUTO, MATURAZIONE_NON_TRATTENUTO,
                    mese, non_trattenuto,
                    f"non trattenuto = resto aperto ({resto.aperto}) meno trattenuto ({trattenuto}) alla fine del differimento: "
                    "la CU lo riporta e la persona lo versa entro il 15 gennaio",
                    istante,
                ),
            )
            testo = f"; alla fine del differimento {non_trattenuto} passa a non trattenuto"
        importi.append(
            _importo_derivato(
                conguaglio, resto.decisione.istituto, MATURAZIONE_RESTO_DIFFERITO, mese, trattenuto,
                f"resto trattenuto = minimo fra resto aperto ({resto.aperto}) e capienza rimasta dopo l'interesse; "
                f"resto differito dal conguaglio del {resto.data}{testo}",
                istante, importi=(decisione, *precedenti, *chiusura),
            )
        )
    if interesse > 0:
        parziale = f"; trattenuto {interesse} dei {dovuto} dovuti per la capienza" if interesse < dovuto else ""
        importi.append(
            _importo_derivato(
                conguaglio, resto.istituto_interesse, MATURAZIONE_INTERESSE, mese, interesse,
                f"interesse semplice = resto aperto ({resto.aperto}) per l'aliquota mensile ({parametro.valore}) per i mesi "
                f"di differimento ({mesi}, dall'ultimo movimento del {resto.ultimo_movimento}){parziale}",
                istante, parametri=(parametro,), importi=(decisione, *precedenti), riferimenti=(parametro.riferimento,),
            )
        )
    return tuple(importi), capienza
