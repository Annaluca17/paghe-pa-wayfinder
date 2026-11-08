"""Addizionali regionale e comunale all'IRPEF: saldo, rate e acconto comunale (ticket #85, ADR 0029).

Si calcolano sull'imponibile fiscale dell'anno della persona, lo stesso del conguaglio (ADR 0019), con le aliquote
datate del corpus per il comune e la regione del domicilio fiscale al 1° gennaio. Questo modulo legge e non scrive:
gli importi che produce sono dei pagamenti, e il residuo da trattenere si ricalcola dagli esiti pagati.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .corpus import AliquotaAddizionale, Corpus, RegolaAddizionali
from .errori import FattoMancante, ParametroMancante
from .modello import Derivazione, Fatto, Importo, ParametroLetto
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
