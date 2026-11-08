"""Addizionali regionale e comunale all'IRPEF: saldo, rate e acconto comunale (ticket #85, ADR 0029).

Si calcolano sull'imponibile fiscale dell'anno della persona, lo stesso del conguaglio (ADR 0019), con le aliquote
datate del corpus per il comune e la regione del domicilio fiscale al 1° gennaio. Questo modulo legge e non scrive:
gli importi che produce sono dei pagamenti, e il residuo da trattenere si ricalcola dagli esiti pagati.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from .corpus import AliquotaAddizionale, Corpus, RegolaAddizionali
from .errori import FattoMancante, ParametroMancante
from .modello import Derivazione, Fatto, Importo, ParametroLetto, TipoEsito
from .registro import TIPO_DOMICILIO_FISCALE, Registro
from .tempo import Periodo


@dataclass(frozen=True)
class Domicilio:
    """Il domicilio fiscale vigente di una persona: il fatto, il codice catastale del comune e il codice della regione."""

    fatto: Fatto
    comune: str
    regione: str


def domicilio_fiscale(registro: Registro, persona: str, giorno: date, noto_al: datetime) -> Domicilio | None:
    """Il domicilio fiscale della persona al `giorno`; None se manca."""
    fatto = registro.vigente_persona(persona, TIPO_DOMICILIO_FISCALE, giorno, noto_al)
    if fatto is None:
        return None
    dati = json.loads(fatto.valore)
    return Domicilio(fatto, dati["comune"], dati["regione"])


# Importi dovuti al conguaglio

def _riferimento_unito(*riferimenti: str) -> str:
    unici = []
    for riferimento in riferimenti:
        if riferimento not in unici:
            unici.append(riferimento)
    return " + ".join(unici)


def _lette(nome: str, aliquota: AliquotaAddizionale) -> tuple[ParametroLetto, ...]:
    """Soglia e fasce lette, una per una: nome `addizionale_<ente>.<codice>.<anno>.<voce>`, con la fonte dell'aliquota."""
    prefisso = f"addizionale_{nome}.{aliquota.codice}.{aliquota.anno}"
    dal = date(aliquota.anno, 1, 1)
    letti = [ParametroLetto(f"{prefisso}.soglia", aliquota.soglia, dal, aliquota.riferimento)]
    for numero, fascia in enumerate(aliquota.fasce, start=1):
        if fascia.fino_a is not None:
            letti.append(ParametroLetto(f"{prefisso}.fascia_{numero}.fino_a", fascia.fino_a, dal, aliquota.riferimento))
        letti.append(ParametroLetto(f"{prefisso}.fascia_{numero}.aliquota", fascia.aliquota, dal, aliquota.riferimento))
    return tuple(letti)


def _dovuta(
    corpus: Corpus,
    regola: RegolaAddizionali,
    ente: str,
    rapporto: str,
    persona: str,
    anno: int,
    imponibile: Decimal,
    irpef_dovuta: Decimal,
    domicilio: Domicilio | None,
    istante: datetime,
) -> Importo:
    istituto = regola.comunale_dovuta if ente == "comune" else regola.regionale_dovuta
    nome = "comunale" if ente == "comune" else "regionale"
    periodo = Periodo(date(anno, 1, 1), date(anno, 12, 31))
    base = dict(
        istituto=istituto,
        maturazione="addizionale",
        regola_versione=regola.versione,
        versione_corpus=corpus.versione,
        noto_al=istante,
        importi=(),
    )
    if irpef_dovuta <= 0:
        derivazione = Derivazione(
            riferimento=regola.riferimento,
            formula=f"addizionale {nome} = zero: l'IRPEF dell'anno, al netto delle detrazioni, non è dovuta",
            parametri=(),
            fatti=(),
            **base,
        )
        return Importo(rapporto, istituto, periodo, Decimal(0), derivazione, anno_imposta=anno)
    if domicilio is None:
        raise FattoMancante(
            f"Manca il domicilio fiscale della persona {persona} al 1° gennaio {anno}, serve all'addizionale {nome} "
            f"dell'anno d'imposta {anno}"
        )
    codice = domicilio.comune if ente == "comune" else domicilio.regione
    aliquota = corpus.aliquota_addizionale(ente, codice, anno)
    if aliquota is None:
        raise ParametroMancante(
            f"Aliquote dell'addizionale {nome}: nessuna per {'il comune' if ente == 'comune' else 'la regione'} "
            f"{codice} nell'anno {anno}"
        )
    derivazione = Derivazione(
        riferimento=_riferimento_unito(regola.riferimento, aliquota.riferimento),
        formula=(
            f"addizionale {nome} = aliquote {ente} {codice} {anno} sull'imponibile fiscale dell'anno ({imponibile}), "
            "a fasce; zero fino alla soglia, oltre la soglia su tutto il reddito"
        ),
        parametri=_lette(nome, aliquota),
        fatti=(domicilio.fatto,),
        **base,
    )
    return Importo(rapporto, istituto, periodo, aliquota.su(imponibile), derivazione, anno_imposta=anno)


def dovute_dell_anno(
    registro: Registro,
    corpus: Corpus,
    regola: RegolaAddizionali,
    rapporto: str,
    persona: str,
    anno: int,
    imponibile: Decimal,
    irpef_dovuta: Decimal,
    istante: datetime,
) -> tuple[Importo, Importo]:
    """Le addizionali regionale e comunale dell'anno, sull'imponibile fiscale usato dal conguaglio.

    Sono zero se l'IRPEF dell'anno al netto delle detrazioni non è dovuta. Altrimenti servono il domicilio fiscale
    al 1° gennaio e le aliquote del suo comune e della sua regione per l'anno: se mancano, il calcolo si ferma.
    """
    domicilio = domicilio_fiscale(registro, persona, date(anno, 1, 1), istante)
    return tuple(
        _dovuta(corpus, regola, ente, rapporto, persona, anno, imponibile, irpef_dovuta, domicilio, istante)
        for ente in ("regione", "comune")
    )


# Residuo e rate, dagli esiti pagati

CENTESIMO = Decimal("0.01")


@dataclass(frozen=True)
class _Pagata:
    riga: Importo
    data: date


@dataclass(frozen=True)
class _Natura:
    """I quattro istituti di un'addizionale: dovuta al conguaglio, rata, acconto trattenuto (solo la comunale) e credito."""

    nome: str
    dovuta: str
    rata: str
    acconto: str | None
    credito: str


def _nature(regola: RegolaAddizionali) -> tuple[_Natura, _Natura]:
    return (
        _Natura("regionale", regola.regionale_dovuta, regola.regionale, None, regola.regionale_credito),
        _Natura("comunale", regola.comunale_dovuta, regola.comunale_saldo, regola.comunale_acconto, regola.comunale_credito),
    )


def _pagate(registro: Registro, persona: str, istante: datetime) -> list[_Pagata]:
    """Le righe degli esiti pagati dei rapporti della persona, con la data di pagamento (quella dell'esito se manca)."""
    pagamenti = {r: registro.pagamenti(r, istante) for r in registro.rapporti_della_persona(persona, istante)}
    pagate = []
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        for riga in esito.righe:
            if riga.rapporto in pagamenti:
                fatto = pagamenti[riga.rapporto].get(esito.id)
                pagate.append(_Pagata(riga, fatto.valido_dal if fatto else esito.data))
    return pagate


@dataclass(frozen=True)
class _Residuo:
    valore: Decimal
    importi: tuple[Importo, ...]
    conguaglio: date | None


def _residuo(pagate: list[_Pagata], natura: _Natura, anno: int) -> _Residuo:
    """Quanto resta da trattenere dell'addizionale dell'anno: la dovuta dell'ultimo conguaglio pagato, meno l'acconto
    trattenuto e le rate già pagate, più quanto già restituito. Nessun piano salvato: si ricalcola ogni volta."""
    dovuta, conguaglio = None, None
    for pagata in pagate:
        riga = pagata.riga
        if riga.derivazione.maturazione == "conguaglio" and riga.anno_imposta == anno:
            trovate = [d for d in riga.derivazione.importi if d.istituto == natura.dovuta]
            if trovate:
                dovuta, conguaglio = trovate[0], pagata.data
    if dovuta is None:
        return _Residuo(Decimal(0), (), None)
    valore, usati = dovuta.valore, [dovuta]
    for istituto, segno in ((natura.acconto, -1), (natura.rata, -1), (natura.credito, 1)):
        for pagata in pagate:
            if istituto is not None and pagata.riga.istituto == istituto and pagata.riga.anno_imposta == anno:
                valore += segno * pagata.riga.valore
                usati.append(pagata.riga)
    return _Residuo(valore, tuple(usati), conguaglio)


def _letto(corpus: Corpus, nome: str, giorno: date) -> ParametroLetto:
    vigenza = corpus.parametro(nome).vigenza_per(Periodo(giorno, giorno))
    return ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento)


def _importo_trattenuto(
    corpus: Corpus,
    regola: RegolaAddizionali,
    istituto: str,
    rapporto: str,
    anno: int,
    valore: Decimal,
    formula: str,
    parametri: tuple[ParametroLetto, ...],
    residuo: _Residuo,
    istante: datetime,
) -> Importo:
    derivazione = Derivazione(
        istituto=istituto,
        maturazione="addizionale",
        regola_versione=regola.versione,
        riferimento=_riferimento_unito(regola.riferimento, *(d.derivazione.riferimento for d in residuo.importi[:1])),
        formula=formula,
        versione_corpus=corpus.versione,
        noto_al=istante,
        parametri=parametri,
        fatti=(),
        importi=residuo.importi,
    )
    return Importo(rapporto, istituto, Periodo(date(anno, 1, 1), date(anno, 12, 31)), valore, derivazione, anno_imposta=anno)


def _rata(residuo: Decimal, mesi_rimasti: int) -> Decimal:
    """Il residuo diviso i mesi rimasti, al centesimo: la differenza di centesimi resta per l'ultima rata."""
    if mesi_rimasti <= 1:
        return residuo
    return (residuo / mesi_rimasti).quantize(CENTESIMO, rounding=ROUND_HALF_UP)


def rate_del_mese(
    registro: Registro,
    corpus: Corpus,
    regola: RegolaAddizionali,
    rapporto: str,
    persona: str,
    data_pagamento: date,
    istante: datetime,
) -> tuple[Importo, ...]:
    """Le rate delle addizionali dell'anno prima da trattenere nel pagamento: una sola per persona e per mese.

    La rata è il residuo da trattenere diviso i mesi rimasti fino all'ultimo mese delle rate (compreso), dal mese dopo
    il conguaglio. Il primo pagamento del mese le trattiene; dopo l'ultimo mese non c'è nulla.
    """
    pagate = _pagate(registro, persona, istante)
    mese = (data_pagamento.year, data_pagamento.month)
    if any(
        (p.data.year, p.data.month) == mese and p.riga.istituto in (n.rata for n in _nature(regola))
        for p in pagate
    ):
        return ()
    ultimo = _letto(corpus, regola.mese_ultima_rata, data_pagamento)
    mesi_rimasti = int(ultimo.valore) - data_pagamento.month + 1
    if mesi_rimasti < 1:
        return ()
    anno = data_pagamento.year - 1
    rate = []
    for natura in _nature(regola):
        residuo = _residuo(pagate, natura, anno)
        if residuo.valore <= 0 or residuo.conguaglio is None or (residuo.conguaglio.year, residuo.conguaglio.month) >= mese:
            continue
        rate.append(
            _importo_trattenuto(
                corpus, regola, natura.rata, rapporto, anno, _rata(residuo.valore, mesi_rimasti),
                f"rata = residuo da trattenere ({residuo.valore}) diviso i mesi rimasti fino al mese {ultimo.valore} "
                f"compreso ({mesi_rimasti}); i centesimi sull'ultima",
                (ultimo,), residuo, istante,
            )
        )
    return tuple(rate)
