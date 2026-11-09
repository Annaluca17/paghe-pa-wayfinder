"""Sostitutiva del 15% sull'accessorio 2026: quota nel pagamento, ricalcolo al conguaglio, scomputo (ticket #96, ADR 0035).

L'imposta sostituisce IRPEF e addizionali sugli importi degli istituti accessori del personale non dirigenziale, fino a
800 euro per persona nell'anno, se il reddito di lavoro dipendente non supera 50.000 euro (L. 199/2025 art. 1 c. 237).
Ogni pagamento produce due importi non reddito: la quota di accessorio a sostitutiva (`istituto_base`, esce
dall'imponibile fiscale ordinario) e l'imposta (`istituto`, trattenuta e versata con 179E, ris. 4/E/2026). L'imposta
è calcolata sul cumulato dell'anno, così i centesimi non si perdono tra un pagamento e l'altro.

Questo modulo legge e non scrive: il chiamante (fisco) dà il netto dell'accessorio, il reddito stimato e il già pagato.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from .corpus import Corpus, RegolaSostitutiva
from .modello import MATURAZIONE_SOSTITUTIVA, Derivazione, Fatto, Importo, ParametroLetto
from .tempo import Periodo

CENTESIMO = Decimal("0.01")


def _parametro(corpus: Corpus, nome: str, giorno: date) -> ParametroLetto:
    vigenza = corpus.parametro(nome).vigenza_per(Periodo(giorno, giorno))
    return ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento)


def parametri(corpus: Corpus, regola: RegolaSostitutiva, giorno: date) -> tuple[ParametroLetto, ParametroLetto, ParametroLetto]:
    """(aliquota, tetto, limite) alla data."""
    return tuple(_parametro(corpus, nome, giorno) for nome in regola.parametri)  # type: ignore[return-value]


def imposta_su(base: Decimal, aliquota: Decimal) -> Decimal:
    return (base * aliquota).quantize(CENTESIMO, rounding=ROUND_HALF_UP)


def netto_accessorio(accessorio: Decimal, reddito: Decimal, contributi: Decimal) -> Decimal:
    """Accessorio al netto dei contributi a carico del dipendente, in proporzione al reddito del pagamento.

    Stessa base dell'imponibile fiscale (analogia con i premi di produttività, da verificare, ADR 0035).
    """
    if reddito <= 0:
        return Decimal(0)
    return max(Decimal(0), accessorio - contributi * accessorio / reddito).quantize(CENTESIMO, rounding=ROUND_HALF_UP)


def scomputo(aliquota: Decimal, base_totale: Decimal, imposta_totale: Decimal) -> Decimal:
    """Sostitutiva trattenuta oltre quella che spetta sulla quota rimasta a sostitutiva: si scomputa dall'IRPEF dovuta.

    Come una ritenuta già operata, senza credito su 179E (ADR 0035, da verificare).
    """
    return max(Decimal(0), imposta_totale - imposta_su(base_totale, aliquota))


def _ultimo_del_mese(giorno: date) -> date:
    return giorno.replace(day=calendar.monthrange(giorno.year, giorno.month)[1])


def _importi(
    corpus: Corpus,
    regola: RegolaSostitutiva,
    rapporto: str,
    anno: int,
    periodo: Periodo,
    base: Decimal,
    imposta: Decimal,
    formula: str,
    letti: tuple[ParametroLetto, ...],
    fonti: tuple[Importo, ...],
    fatti: tuple[Fatto, ...],
    istante: datetime,
) -> tuple[Importo, ...]:
    """Quota a sostitutiva e imposta, senza gli importi nulli."""
    risultato = []
    for istituto, valore in ((regola.istituto_base, base), (regola.istituto, imposta)):
        if valore == 0:
            continue
        derivazione = Derivazione(
            istituto=istituto,
            maturazione=MATURAZIONE_SOSTITUTIVA,
            regola_versione=regola.versione,
            riferimento=regola.riferimento,
            formula=formula,
            versione_corpus=corpus.versione,
            noto_al=istante,
            parametri=letti,
            fatti=fatti,
            importi=fonti,
        )
        risultato.append(Importo(rapporto, istituto, periodo, valore, derivazione, anno_imposta=anno))
    return tuple(risultato)


def del_pagamento(
    corpus: Corpus,
    regola: RegolaSostitutiva,
    rapporto: str,
    anno: int,
    data_pagamento: date,
    riferimento: date,
    netto: Decimal,
    stimato: Decimal,
    origine_stimato: str,
    base_gia: Decimal,
    imposta_gia: Decimal,
    fonti: tuple[Importo, ...],
    fatti: tuple[Fatto, ...],
    istante: datetime,
) -> tuple[Importo, ...]:
    """Quota a sostitutiva e imposta del pagamento; vuoto se non c'è nulla da tassare così.

    La quota è il netto dell'accessorio fino a esaurire il tetto della persona nell'anno (`base_gia` somma i suoi
    rapporti e i pagamenti precedenti), se il reddito annuo stimato, accessorio compreso, non supera il limite.
    """
    aliquota, tetto, limite = parametri(corpus, regola, riferimento)
    if stimato > limite.valore:
        return ()
    quota = max(Decimal(0), min(netto, tetto.valore - base_gia))
    if quota == 0:
        return ()
    imposta = max(Decimal(0), imposta_su(base_gia + quota, aliquota.valore) - imposta_gia)
    periodo = Periodo(data_pagamento.replace(day=1), _ultimo_del_mese(data_pagamento))
    formula = (
        f"quota a sostitutiva = minimo tra accessorio netto dei contributi ({netto}) e tetto ({tetto.valore}) meno già "
        f"a sostitutiva nell'anno ({base_gia}); reddito annuo stimato {stimato} ({origine_stimato}) non oltre {limite.valore}; "
        f"imposta = {aliquota.valore} sul cumulato dell'anno ({base_gia + quota}) meno imposta già trattenuta ({imposta_gia})"
    )
    return _importi(
        corpus, regola, rapporto, anno, periodo, quota, imposta, formula, (aliquota, tetto, limite), fonti, fatti, istante
    )


def al_conguaglio(
    corpus: Corpus,
    regola: RegolaSostitutiva,
    rapporto: str,
    anno: int,
    data_pagamento: date,
    riferimento: date,
    netto_anno: Decimal,
    reddito_vero: Decimal,
    base_gia: Decimal,
    imposta_gia: Decimal,
    fonti: tuple[Importo, ...],
    fatti: tuple[Fatto, ...],
    istante: datetime,
) -> tuple[Importo, ...]:
    """Differenza tra la sostitutiva già applicata e quella che spetta sul reddito vero dell'anno.

    Sopra il limite nulla spetta: la quota si toglie e l'imposta già versata non si restituisce, si scomputa dall'IRPEF
    dovuta (`scomputo`). Sotto il limite la sostitutiva spetta sui primi `tetto` euro dell'accessorio dell'anno.
    """
    aliquota, tetto, limite = parametri(corpus, regola, riferimento)
    spettante = Decimal(0) if reddito_vero > limite.valore else min(netto_anno, tetto.valore)
    differenza = spettante - base_gia
    imposta = max(Decimal(0), imposta_su(spettante, aliquota.valore) - imposta_gia)
    if differenza == 0 and imposta == 0:
        return ()
    formula = (
        f"quota a sostitutiva dell'anno = {'zero' if reddito_vero > limite.valore else 'minimo tra accessorio netto'} "
        f"({netto_anno}) e tetto ({tetto.valore}); reddito vero dell'anno, accessorio compreso, {reddito_vero} contro il "
        f"limite {limite.valore}; spettante {spettante}, già a sostitutiva {base_gia}: differenza {differenza}; "
        f"imposta in più = {aliquota.valore} sullo spettante meno imposta già trattenuta ({imposta_gia}), non sotto zero"
    )
    periodo = Periodo(date(anno, 1, 1), date(anno, 12, 31))
    return _importi(
        corpus, regola, rapporto, anno, periodo, differenza, imposta, formula, (aliquota, tetto, limite), fonti, fatti, istante
    )
