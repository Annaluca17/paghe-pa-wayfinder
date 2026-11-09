"""Somma esente e trattamento integrativo: importi a favore della persona, recuperi e rate (ticket #95, ADR 0019).

Sono due istituti pagati in busta, non reddito e non detrazioni: non entrano nell'imponibile fiscale né nelle basi
contributive. In ogni pagamento si riconosce l'importo del mese, calcolato dalle formule del corpus sul reddito annuo
stimato; al conguaglio si ricalcola l'annuo sul reddito vero e la differenza con quanto già riconosciuto si paga o si
recupera. Un recupero fino alla soglia, o alla cessazione, è in unica soluzione; oltre la soglia è a rate dai pagamenti
dopo il conguaglio. Il piano a rate non è salvato: la sua decisione sta nella derivazione del conguaglio e le rate si
ricalcolano dagli esiti pagati, come le addizionali (ADR 0029).

Questo modulo legge e non scrive: il chiamante (fisco) dà i valori del fisco della persona e gli esiti pagati.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from .corpus import Corpus, RegolaBenefici
from .formula import valuta
from .modello import MATURAZIONE_BENEFICIO, MATURAZIONE_DA_RECUPERARE, Derivazione, Fatto, Importo, ParametroLetto
from .tempo import Periodo

CENTESIMO = Decimal("0.01")
GIORNI_REDDITO_ANNUO = 365  # circ. AdE 4/E/2025 par. 1.2: reddito annuo teorico = reddito / giorni di lavoro * 365 (prassi)

# Una riga già pagata con la sua data di pagamento.
Pagata = tuple[Importo, date]


@dataclass(frozen=True)
class Contesto:
    """I valori che le formule leggono (`fisco.*`) e da dove vengono, per la derivazione."""

    reddito_stimato: Decimal
    origine_stimato: str
    reddito_dipendente: Decimal
    reddito_fascia: Decimal
    imposta: Decimal
    detrazione: Decimal
    oneri: Decimal
    periodi: int
    giorni: int
    giorni_anno: int
    importi: tuple[Importo, ...]
    fatti: tuple[Fatto, ...] = ()


@dataclass(frozen=True)
class _Beneficio:
    nome: str
    istituto: str
    recupero: str
    formula: str
    categorie: tuple[str, ...]
    rate: str


def _benefici(regola: RegolaBenefici) -> tuple[_Beneficio, _Beneficio]:
    return (
        _Beneficio(
            "somma esente", regola.istituto_somma_esente, regola.recupero_somma_esente, regola.somma_esente,
            regola.categorie_somma_esente, regola.rate_somma_esente,
        ),
        _Beneficio(
            "trattamento integrativo", regola.istituto_trattamento_integrativo, regola.recupero_trattamento_integrativo,
            regola.trattamento_integrativo, regola.categorie_trattamento_integrativo, regola.rate_trattamento_integrativo,
        ),
    )


def reddito_annuo_stimato(pagato: Decimal, giorni_di_servizio: int) -> Decimal:
    """Pagato dall'inizio dell'anno diviso i giorni di servizio per 365; senza giorni di servizio il pagato com'e'."""
    if giorni_di_servizio <= 0:
        return pagato
    return (pagato * GIORNI_REDDITO_ANNUO / giorni_di_servizio).quantize(CENTESIMO, rounding=ROUND_HALF_UP)


def reddito_idoneo(redditi, deduzioni, categorie: tuple[str, ...]) -> Decimal:
    """Reddito delle `categorie` al netto della loro parte di deduzioni (in proporzione al reddito complessivo)."""
    totale = sum((riga.valore for riga in redditi), Decimal(0))
    idoneo = sum((riga.valore for riga in redditi if riga.categoria_reddito in categorie), Decimal(0))
    if totale <= 0:
        return Decimal(0)
    dedotto = sum((riga.valore for riga in deduzioni), Decimal(0)) * idoneo / totale
    return max(Decimal(0), idoneo - dedotto)


def _valuta(corpus: Corpus, formula: str, contesto: Contesto, giorno: date) -> tuple[Decimal, tuple[ParametroLetto, ...]]:
    letti: dict[str, ParametroLetto] = {}
    valori = {
        "reddito_stimato": contesto.reddito_stimato,
        "reddito_dipendente": contesto.reddito_dipendente,
        "reddito_fascia": contesto.reddito_fascia,
        "imposta": contesto.imposta,
        "detrazione": contesto.detrazione,
        "oneri": contesto.oneri,
        "periodi": Decimal(contesto.periodi),
        "giorni": Decimal(contesto.giorni),
        "giorni_anno": Decimal(contesto.giorni_anno),
    }

    def risolvi(origine: str, nome: str) -> Decimal:
        if origine == "fisco":
            return valori[nome]
        vigenza = corpus.parametro(nome).vigenza_per(Periodo(giorno, giorno))
        letti[nome] = ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento)
        return vigenza.valore

    valore = valuta(formula, risolvi)
    return valore, tuple(letti[nome] for nome in sorted(letti))


def _parametro(corpus: Corpus, nome: str, giorno: date) -> ParametroLetto:
    vigenza = corpus.parametro(nome).vigenza_per(Periodo(giorno, giorno))
    return ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento)


def _letture(contesto: Contesto) -> str:
    return (
        f"reddito annuo stimato = {contesto.reddito_stimato} ({contesto.origine_stimato}); "
        f"reddito di lavoro dipendente = {contesto.reddito_dipendente}; "
        f"reddito per la percentuale della somma esente = {contesto.reddito_fascia}; imposta lorda = {contesto.imposta}; "
        f"detrazione dell'art. 13 = {contesto.detrazione} (calcolata anche senza dichiarazione del sostituito); "
        f"oneri detraibili comunicati = {contesto.oneri}"
    )


def _importo(
    corpus: Corpus,
    regola: RegolaBenefici,
    istituto: str,
    rapporto: str,
    anno: int,
    periodo: Periodo,
    valore: Decimal,
    formula: str,
    parametri: tuple[ParametroLetto, ...],
    importi: tuple[Importo, ...],
    fatti: tuple[Fatto, ...],
    istante: datetime,
    maturazione: str = MATURAZIONE_BENEFICIO,
) -> Importo:
    derivazione = Derivazione(
        istituto=istituto,
        maturazione=maturazione,
        regola_versione=regola.versione,
        riferimento=regola.riferimento,
        formula=formula,
        versione_corpus=corpus.versione,
        noto_al=istante,
        parametri=parametri,
        fatti=fatti,
        importi=importi,
    )
    return Importo(rapporto, istituto, periodo, valore, derivazione, anno_imposta=anno)


def _ultimo_del_mese(giorno: date) -> date:
    return giorno.replace(day=calendar.monthrange(giorno.year, giorno.month)[1])


def _anno(anno: int) -> Periodo:
    return Periodo(date(anno, 1, 1), date(anno, 12, 31))


# Il pagamento del mese

def riconosciuti_del_mese(
    corpus: Corpus,
    regola: RegolaBenefici,
    rapporto: str,
    anno: int,
    data_pagamento: date,
    riferimento: date,
    contesto: Contesto,
    categorie_presenti: frozenset[str],
    gia_nel_mese: list[Importo],
    istante: datetime,
) -> tuple[Importo, ...]:
    """Somma esente e trattamento integrativo del pagamento, per i redditi che li danno.

    L'importo è quello del mese (con i redditi del mese già pagati) meno quanto già riconosciuto nello stesso mese,
    non sotto zero: un eccesso si corregge al conguaglio.
    """
    periodo = Periodo(data_pagamento.replace(day=1), _ultimo_del_mese(data_pagamento))
    risultato = []
    for beneficio in _benefici(regola):
        if not categorie_presenti & set(beneficio.categorie):
            continue
        gia = tuple(riga for riga in gia_nel_mese if riga.istituto == beneficio.istituto)
        del_mese, parametri = _valuta(corpus, beneficio.formula, contesto, riferimento)
        riconosciuto = sum((riga.valore for riga in gia), Decimal(0))
        risultato.append(
            _importo(
                corpus, regola, beneficio.istituto, rapporto, anno, periodo, max(Decimal(0), del_mese - riconosciuto),
                f"{beneficio.nome} del periodo = {beneficio.formula}; {_letture(contesto)}; "
                f"valore del periodo = {del_mese}; già riconosciuto nel mese = {riconosciuto}; "
                "importo = valore del periodo meno già riconosciuto nel mese, non sotto zero",
                parametri, (*contesto.importi, *gia), contesto.fatti, istante,
            )
        )
    return tuple(risultato)


# Il conguaglio: spettante dell'anno, differenza, recupero

def al_conguaglio(
    corpus: Corpus,
    regola: RegolaBenefici,
    rapporto: str,
    anno: int,
    data_pagamento: date,
    riferimento: date,
    contesto: Contesto,
    categorie_presenti: frozenset[str],
    riconosciuti: list[Importo],
    finale: bool,
    ulteriore_in_piu: Decimal,
    istante: datetime,
) -> tuple[tuple[Importo, ...], tuple[Importo, ...]]:
    """(importi del pagamento, recuperi a rate da mettere nella derivazione del conguaglio).

    Lo spettante dell'anno si calcola sul reddito vero. Se supera il già riconosciuto nell'anno la differenza si paga
    in questo pagamento; se è inferiore, la differenza si recupera. Un recupero fino alla soglia, o alla cessazione, è
    in unica soluzione; oltre la soglia è a rate dai pagamenti dopo il conguaglio. Per la somma esente la soglia si
    guarda sul recupero meno l'ulteriore detrazione spettante in più (circ. AdE 4/E/2025, prassi).
    """
    periodo = Periodo(data_pagamento.replace(day=1), _ultimo_del_mese(data_pagamento))
    importi: list[Importo] = []
    piani: list[Importo] = []
    soglia = _parametro(corpus, regola.soglia_recupero, riferimento)
    for beneficio in _benefici(regola):
        if not categorie_presenti & set(beneficio.categorie):
            continue
        gia = tuple(riga for riga in riconosciuti if riga.istituto == beneficio.istituto)
        spettante, parametri = _valuta(corpus, beneficio.formula, contesto, riferimento)
        riconosciuto = sum((riga.valore for riga in gia), Decimal(0))
        differenza = spettante - riconosciuto
        importi.append(
            _importo(
                corpus, regola, beneficio.istituto, rapporto, anno, periodo, max(Decimal(0), differenza),
                f"{beneficio.nome} al conguaglio = {beneficio.formula} sull'anno intero; {_letture(contesto)}; "
                f"spettante dell'anno = {spettante}; già riconosciuto nell'anno = {riconosciuto}; "
                "importo = spettante meno già riconosciuto, non sotto zero",
                parametri, (*contesto.importi, *gia), contesto.fatti, istante,
            )
        )
        da_recuperare = -differenza
        if da_recuperare <= 0:
            continue
        in_piu = ulteriore_in_piu if beneficio.istituto == regola.istituto_somma_esente else Decimal(0)
        confronto = da_recuperare - in_piu
        base = (
            f"{beneficio.nome} riconosciuta nell'anno ({riconosciuto}) oltre lo spettante ({spettante}): "
            f"da recuperare {da_recuperare}"
        )
        if in_piu:
            base += f"; ulteriore detrazione spettante in più {in_piu}, recupero da confrontare con la soglia {confronto}"
        if finale or confronto <= soglia.valore:
            motivo = "alla cessazione, in unica soluzione" if finale else f"fino a {soglia.valore}, in unica soluzione"
            importi.append(
                _importo(
                    corpus, regola, beneficio.recupero, rapporto, anno, _anno(anno), da_recuperare,
                    f"recupero = {base}; {motivo}", (soglia,), (*gia, *contesto.importi), (), istante,
                )
            )
            continue
        rate = _parametro(corpus, beneficio.rate, riferimento)
        piano = _importo(
            corpus, regola, beneficio.recupero, rapporto, anno, _anno(anno), da_recuperare,
            f"recupero a rate = {base}; oltre {soglia.valore}, {rate.valore} rate di pari ammontare dal pagamento "
            "del conguaglio",
            (soglia, rate), (*gia, *contesto.importi), (), istante, MATURAZIONE_DA_RECUPERARE,
        )
        piani.append(piano)
        # La prima rata sta nel pagamento del conguaglio: «dalla retribuzione che sconta gli effetti del conguaglio»
        # (D.L. 3/2020 art. 1 c. 3; L. 207/2024 art. 1 c. 7, «dalla prima retribuzione su cui incide il conguaglio»).
        importi.append(
            _importo(
                corpus, regola, beneficio.recupero, rapporto, anno, _anno(anno), _rata(da_recuperare, int(rate.valore)),
                f"prima rata = recupero ({da_recuperare}) diviso {rate.valore} rate, nel pagamento del conguaglio",
                (soglia, rate), (piano,), (), istante,
            )
        )
    return tuple(importi), tuple(piani)


# Residuo e rate, dagli esiti pagati

@dataclass(frozen=True)
class _Piano:
    decisione: Importo
    conguaglio: Importo
    data: date
    rate_pagate: tuple[Pagata, ...]
    rate_totali: int

    @property
    def residuo(self) -> Decimal:
        return self.decisione.valore - sum((riga.valore for riga, _ in self.rate_pagate), Decimal(0))

    @property
    def rate_rimaste(self) -> int:
        return self.rate_totali - len(self.rate_pagate)


def _piani(regola: RegolaBenefici, pagate: list[Pagata]) -> list[_Piano]:
    """I recuperi a rate decisi dai conguagli pagati, con le rate già trattenute; vince l'ultimo conguaglio dell'anno."""
    nomi_rate = {regola.rate_somma_esente, regola.rate_trattamento_integrativo}
    decisioni: dict[tuple[str, int], tuple[Importo, Importo, date]] = {}
    for riga, data in pagate:
        if riga.derivazione.maturazione != "conguaglio":
            continue
        for importo in riga.derivazione.importi:
            if importo.derivazione.maturazione == MATURAZIONE_DA_RECUPERARE:
                decisioni[(importo.istituto, importo.anno_imposta)] = (importo, riga, data)
    piani = []
    for (istituto, anno), (decisione, conguaglio, data) in sorted(decisioni.items()):
        rate = tuple(
            (riga, giorno)
            for riga, giorno in pagate
            if riga.istituto == istituto and riga.anno_imposta == anno and riga.derivazione.maturazione == MATURAZIONE_BENEFICIO
        )
        totali = int(next(p.valore for p in decisione.derivazione.parametri if p.nome in nomi_rate))
        piani.append(_Piano(decisione, conguaglio, data, rate, totali))
    return piani


def _senza_derivazione(riga: Importo) -> Importo:
    """La rata già pagata come riferimento, senza la sua derivazione: ogni rata cita le precedenti e l'albero raddoppierebbe."""
    return replace(riga, derivazione=replace(riga.derivazione, importi=()))


def _rata(residuo: Decimal, rate_rimaste: int) -> Decimal:
    """Il residuo diviso le rate rimaste, al centesimo: la differenza di centesimi resta per l'ultima rata."""
    if rate_rimaste <= 1:
        return residuo
    return (residuo / rate_rimaste).quantize(CENTESIMO, rounding=ROUND_HALF_UP)


def rate_del_mese(
    corpus: Corpus,
    regola: RegolaBenefici,
    rapporto: str,
    data_pagamento: date,
    finale: bool,
    pagate: list[Pagata],
    istante: datetime,
) -> tuple[Importo, ...]:
    """Le rate dei recuperi decisi dai conguagli precedenti: una per recupero e per mese, dal mese dopo il conguaglio.

    Alla cessazione (`finale`) il residuo di ogni recupero si trattiene tutto in questo pagamento: nessuna rata
    successiva lo prenderebbe (circ. AdE 4/E/2025 e 29/E/2020 per il recupero alla cessazione; per le rate già in corso
    è una lettura, da verificare).
    """
    mese = (data_pagamento.year, data_pagamento.month)
    importi = []
    for piano in _piani(regola, pagate):
        if piano.residuo <= 0 or piano.rate_rimaste <= 0:
            continue
        istituto, anno = piano.decisione.istituto, piano.decisione.anno_imposta
        if finale:
            valore = piano.residuo
            testo = (
                f"alla cessazione, residuo del recupero ({piano.residuo}) in unica soluzione; "
                f"recupero deciso dal conguaglio del {piano.data}"
            )
        else:
            if (piano.data.year, piano.data.month) >= mese:
                continue
            if any((giorno.year, giorno.month) == mese for _, giorno in piano.rate_pagate):
                continue
            valore = _rata(piano.residuo, piano.rate_rimaste)
            testo = (
                f"rata = residuo ({piano.residuo}) diviso le rate rimaste ({piano.rate_rimaste} di {piano.rate_totali}); "
                f"i centesimi sull'ultima; recupero deciso dal conguaglio del {piano.data}"
            )
        importi.append(
            _importo(
                corpus, regola, istituto, rapporto, anno, _anno(anno), valore, testo,
                piano.decisione.derivazione.parametri,
                (piano.conguaglio, *(_senza_derivazione(riga) for riga, _ in piano.rate_pagate)), (), istante,
            )
        )
    return tuple(importi)
