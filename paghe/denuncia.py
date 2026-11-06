"""Denuncia del mese: basi imponibili per cassa e contributi (ADR 0005 e 0006).

La base somma ciò che risulta pagato nel mese: legge le righe degli esiti pagati con la
loro data di pagamento, non ricalcola la competenza. Un arretrato entra così nel mese in
cui è pagato e il mese originario non cambia. Regole di cassa, parametri e concorsi si
scelgono alla data di pagamento.

Le regole sul mese leggono il totale del mese e si espongono sull'ultimo periodo (nota di
prassi 2). I recuperi in servizio e su cessato sono casi modellati; gli altri, e i cumuli
per persona e per anno che la prima fetta non calcola, fermano la denuncia e li nominano.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from decimal import Decimal

from .calcolo import _Calcolo, _Lettore
from .corpus import Base, Corpus, Regola
from .errori import (
    CasoNonModellato,
    ConcorsoMancante,
    ConcorsoParziale,
    ErroreCalcolo,
    ErroreCorpus,
    FattoMancante,
    ValiditaNonUniforme,
)
from .formula import valuta
from .modello import ConcorsoLetto, Derivazione, Fatto, Importo, ParametroLetto, TipoEsito
from .registro import Registro
from .tempo import Mese, Periodo, in_utc

FORMULA_BASE = "somma degli importi pagati nel periodo"
FORMULA_BASE_MESE = "somma delle basi dei periodi del mese"
# Derivano dagli importi pagati: non sono retribuzione e non concorrono a una base.
MATURAZIONI_DERIVATE = {"periodo", "mese", "cassa"}
IN_SERVIZIO = "in servizio"
SU_CESSATO = "su cessato"


@dataclass(frozen=True)
class Recupero:
    """Importo negativo entrato in una base: caso `in servizio` o `su cessato` (ADR 0005, nota di prassi 2)."""

    caso: str
    importo: Importo


@dataclass(frozen=True)
class PeriodoDenuncia:
    """Periodo dichiarato del mese. `in_servizio` falso: importi pagati in un mese senza servizio."""

    periodo: Periodo
    in_servizio: bool
    basi: tuple[Importo, ...] = ()
    contributi: tuple[Importo, ...] = ()
    recuperi: tuple[Recupero, ...] = ()

    def base(self, nome: str) -> Importo | None:
        return next((riga for riga in self.basi if riga.istituto == f"base.{nome}"), None)


@dataclass(frozen=True)
class Denuncia:
    rapporto: str
    mese: Mese
    periodi: tuple[PeriodoDenuncia, ...]
    esiti_senza_data: tuple[int, ...] = ()


@dataclass(frozen=True)
class _RigaPagata:
    importo: Importo
    fatto: Fatto


def _righe_pagate(
    registro: Registro, rapporto: str, mese: Mese, istante: datetime
) -> tuple[list[_RigaPagata], tuple[int, ...]]:
    """Righe del rapporto pagate nel mese, ed esiti che ancora non hanno una data di pagamento."""
    pagamenti = registro.pagamenti(rapporto, istante)
    pagate: list[_RigaPagata] = []
    senza_data: list[int] = []
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        righe = [
            riga
            for riga in esito.righe
            if riga.rapporto == rapporto and riga.derivazione.maturazione not in MATURAZIONI_DERIVATE
        ]
        if not righe:
            continue
        fatto = pagamenti.get(esito.id)
        if fatto is None:
            senza_data.append(esito.id)
        elif mese.primo_giorno <= fatto.valido_dal <= mese.ultimo_giorno:
            pagate.extend(_RigaPagata(replace(riga, data_pagamento=fatto.valido_dal), fatto) for riga in righe)
    return pagate, tuple(senza_data)


def _periodo_della_riga(riga: Importo, periodi: list[Periodo], mese: Mese) -> Periodo:
    """Il fisso resta sui propri giorni; il resto segue la data di pagamento (nota di prassi 2)."""
    if riga.derivazione.maturazione == "giorni":
        for periodo in periodi:
            if periodo.contiene(riga.periodo):
                return periodo
    data = riga.data_pagamento
    for periodo in periodi:
        if periodo.dal <= data <= periodo.al:
            return periodo
    if data > periodi[-1].al:
        return periodi[-1]
    raise ErroreCalcolo(
        f"Rapporto {riga.rapporto}, istituto {riga.istituto}: pagato il {data}, fuori dai periodi di "
        f"servizio di {mese}. Caso non modellato: pagamento prima dell'inizio del servizio o tra due periodi"
    )


def _date_di_pagamento(base: Importo) -> set[date]:
    """La base del mese somma le basi dei periodi: le date stanno un livello sotto."""
    if base.derivazione.maturazione == "mese":
        return {giorno for riga in base.derivazione.importi for giorno in _date_di_pagamento(riga)}
    return {riga.data_pagamento for riga in base.derivazione.importi}


def _basi_del_mese(periodi: list[PeriodoDenuncia], corpus: Corpus, istante: datetime) -> tuple[Importo, ...]:
    """Totale del mese per ogni base, letto dalle regole sul mese (nota di prassi 2)."""
    risultato = []
    for base in corpus.basi():
        righe = [riga for periodo in periodi if (riga := periodo.base(base.nome)) is not None]
        if not righe:
            continue
        risultato.append(
            Importo(
                rapporto=righe[0].rapporto,
                istituto=f"base.{base.nome}",
                periodo=Periodo(periodi[0].periodo.dal, periodi[-1].periodo.al),
                valore=sum((riga.valore for riga in righe), Decimal(0)),
                derivazione=Derivazione(
                    istituto=f"base.{base.nome}",
                    maturazione="mese",
                    regola_versione=1,
                    riferimento=base.riferimento,
                    formula=FORMULA_BASE_MESE,
                    versione_corpus=corpus.versione,
                    noto_al=istante,
                    parametri=(),
                    fatti=(),
                    importi=tuple(righe),
                ),
            )
        )
    return tuple(risultato)


def _recuperi(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, periodo: PeriodoDenuncia, istante: datetime
) -> tuple[Recupero, ...]:
    """Classifica gli importi negativi entrati nelle basi; i casi non modellati fermano la denuncia."""
    if periodo.in_servizio:
        negative = [base for base in periodo.basi if base.valore < 0]
        if negative:
            raise CasoNonModellato(
                f"Rapporto {rapporto}: caso non modellato, mese negativo nel periodo {periodo.periodo} "
                f"(base {negative[0].istituto} = {negative[0].valore})"
            )
    righe: list[Importo] = []
    for base in periodo.basi:
        for riga in base.derivazione.importi:
            if riga.valore < 0 and riga not in righe:
                righe.append(riga)
    if not righe:
        return ()
    if periodo.in_servizio:
        caso = IN_SERVIZIO
    else:
        servizio = registro.fatti_noti(rapporto, corpus.fatto_servizio, istante)
        if not any(fatto.valido_dal < mese.primo_giorno for fatto in servizio):
            raise CasoNonModellato(
                f"Rapporto {rapporto}: caso non modellato, recupero fuori servizio senza servizio precedente in {mese}"
            )
        caso = SU_CESSATO
    return tuple(Recupero(caso, riga) for riga in righe)


def _base_del_periodo(
    base: Base, righe: list[_RigaPagata], periodo: Periodo, corpus: Corpus, istante: datetime
) -> Importo | None:
    """Una dichiarazione assente o parziale ferma il calcolo; un istituto escluso resta tracciato."""
    entrano: list[_RigaPagata] = []
    letti: list[ConcorsoLetto] = []
    for riga in righe:
        importo = riga.importo
        concorso = corpus.concorso(importo.istituto, base.nome, importo.data_pagamento)
        if concorso is None:
            raise ConcorsoMancante(
                f"Rapporto {importo.rapporto}, istituto {importo.istituto}: nessuna dichiarazione di concorso "
                f"alla base {base.nome} per un pagamento del {importo.data_pagamento}"
            )
        if concorso.misura == "parziale":
            raise ConcorsoParziale(
                f"Rapporto {importo.rapporto}, istituto {importo.istituto}: concorso parziale alla base "
                f"{base.nome} non modellato ({concorso.riferimento})"
            )
        letto = ConcorsoLetto(concorso.istituto, concorso.base, concorso.misura, concorso.dal, concorso.riferimento)
        if letto not in letti:
            letti.append(letto)
        if concorso.misura == "intero":
            entrano.append(riga)
    if not entrano:
        return None
    fatti = {riga.fatto.id: riga.fatto for riga in entrano}
    return Importo(
        rapporto=entrano[0].importo.rapporto,
        istituto=f"base.{base.nome}",
        periodo=periodo,
        valore=sum((riga.importo.valore for riga in entrano), Decimal(0)),
        derivazione=Derivazione(
            istituto=f"base.{base.nome}",
            maturazione="cassa",
            regola_versione=1,
            riferimento=base.riferimento,
            formula=FORMULA_BASE,
            versione_corpus=corpus.versione,
            noto_al=istante,
            parametri=(),
            fatti=tuple(fatti[numero] for numero in sorted(fatti)),
            importi=tuple(riga.importo for riga in entrano),
            concorsi=tuple(letti),
        ),
    )


class _Contributi:
    """Regole di cassa di un periodo, valutate alle date di pagamento degli importi nelle basi.

    `applica_se` si legge su `condizione_su`: il periodo stesso, oppure, fuori servizio, l'ultimo
    giorno di servizio. Un recupero su cessato segue così il regime che aveva il servizio (ADR 0009).
    """

    def __init__(
        self, lettore: _Lettore, periodo: Periodo, basi: tuple[Importo, ...], condizione_su: Periodo | None = None
    ):
        self.lettore = lettore
        self.corpus = lettore.corpus
        self.periodo = periodo
        self.condizione_su = condizione_su or periodo
        self.basi = {riga.istituto.removeprefix("base."): riga for riga in basi}
        self.date = sorted({giorno for base in basi for giorno in _date_di_pagamento(base)})
        self._calcolati: dict[str, Importo | None] = {}

    def tutti(self, istituti) -> tuple[Importo, ...]:
        return tuple(importo for importo in (self.importo(nome) for nome in sorted(istituti)) if importo is not None)

    def _regola(self, istituto: str) -> Regola | None:
        regole = set()
        for giorno in self.date:
            regola = self.corpus.regola_per(istituto, Periodo(giorno, giorno))
            if regola is None and self.corpus.regola_iniziata(istituto, giorno):
                raise ErroreCalcolo(f"Istituto {istituto}: nessuna regola vigente per un pagamento del {giorno}")
            regole.add(regola)
        if len(regole) > 1:
            raise ValiditaNonUniforme(f"Istituto {istituto}: la regola cambia tra i pagamenti del periodo {self.periodo}")
        return regole.pop()

    def _parametro(self, nome: str) -> ParametroLetto:
        parametro = self.corpus.parametro(nome)
        vigenze = {parametro.vigenza_per(Periodo(giorno, giorno)) for giorno in self.date}
        if len(vigenze) > 1:
            raise ValiditaNonUniforme(
                f"Parametro {nome}: cambia tra i pagamenti del periodo {self.periodo}. "
                "Caso non modellato: serve un'aliquota per ciascun pagamento"
            )
        vigenza = vigenze.pop()
        return ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento)

    def importo(self, istituto: str) -> Importo | None:
        if istituto not in self._calcolati:
            self._calcolati[istituto] = self._calcola(istituto)
        return self._calcolati[istituto]

    def _calcola(self, istituto: str) -> Importo | None:
        regola = self._regola(istituto)
        if regola is None:
            return None
        parametri: dict[str, ParametroLetto] = {}
        fatti: dict[int, Fatto] = {}
        letti: dict[str, Importo] = {}
        if regola.applica_se is not None:
            condizione = self.lettore.fatto(regola.fatto_condizione, self.condizione_su)
            if condizione is None or not self.lettore.soddisfa(regola, condizione):
                return None
            fatti[condizione.id] = condizione

        def risolvi(origine: str, nome: str) -> Decimal:
            if origine == "fatto":
                return self.lettore.valore_fatto(istituto, nome, self.periodo, fatti)
            if origine == "parametro":
                parametri[nome] = self._parametro(nome)
                return parametri[nome].valore
            riga = self.basi.get(nome) if origine == "base" else self.importo(nome)
            if riga is None:
                return Decimal(0)
            letti[riga.istituto] = riga
            return riga.valore

        valore = valuta(regola.formula, risolvi)
        if not letti:
            return None
        return Importo(
            rapporto=self.lettore.rapporto,
            istituto=istituto,
            periodo=self.periodo,
            valore=valore,
            derivazione=Derivazione(
                istituto=istituto,
                maturazione=regola.maturazione,
                regola_versione=regola.versione,
                riferimento=regola.riferimento,
                formula=regola.formula,
                versione_corpus=self.corpus.versione,
                noto_al=self.lettore.noto_al,
                parametri=tuple(parametri[nome] for nome in sorted(parametri)),
                fatti=tuple(fatti[numero] for numero in sorted(fatti)),
                importi=tuple(letti[nome] for nome in sorted(letti)),
            ),
        )


def calcola_denuncia(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    mese: Mese,
    noto_al: datetime | None = None,
) -> Denuncia:
    """Periodi dichiarati del mese con basi e contributi; funzione pura di registro, corpus e istante."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    denuncia = _denuncia(registro, corpus, rapporto, mese, istante)
    if denuncia.periodi:
        _controlla_cumuli(registro, corpus, denuncia, istante)
    return denuncia


def _denuncia(registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime) -> Denuncia:
    if not corpus.basi():
        raise ErroreCorpus("Il corpus non dichiara alcuna base imponibile")
    lettore = _Lettore(registro, corpus, rapporto, istante)
    lettore.controlla_fermi(mese, {"calcolo", "denuncia"})
    pagate, senza_data = _righe_pagate(registro, rapporto, mese, istante)

    periodi = _periodi_in_servizio(lettore, mese)
    in_servizio = bool(periodi)
    if not in_servizio:
        if not pagate:
            return Denuncia(rapporto, mese, (), senza_data)
        periodi = [mese.periodo]

    gruppi: dict[Periodo, list[_RigaPagata]] = {periodo: [] for periodo in periodi}
    for riga in pagate:
        gruppi[_periodo_della_riga(riga.importo, periodi, mese)].append(riga)

    sul_periodo = corpus.istituti_di_cassa - corpus.istituti_sul_mese
    condizione_su = None if in_servizio else _ultimo_giorno_di_servizio(registro, corpus, rapporto, mese, istante)
    risultato: list[PeriodoDenuncia] = []
    for periodo in periodi:
        basi = tuple(
            importo
            for importo in (_base_del_periodo(base, gruppi[periodo], periodo, corpus, istante) for base in corpus.basi())
            if importo is not None
        )
        contributi = _Contributi(lettore, periodo, basi, condizione_su).tutti(sul_periodo) if basi else ()
        dichiarato = PeriodoDenuncia(periodo, in_servizio, basi, contributi)
        risultato.append(replace(dichiarato, recuperi=_recuperi(registro, corpus, rapporto, mese, dichiarato, istante)))

    if corpus.istituti_sul_mese and any(periodo.basi for periodo in risultato):
        ultimo = risultato[-1]
        basi_mese = _basi_del_mese(risultato, corpus, istante)
        del_mese = _Contributi(lettore, ultimo.periodo, basi_mese, condizione_su).tutti(corpus.istituti_sul_mese)
        risultato[-1] = replace(ultimo, contributi=ultimo.contributi + del_mese)
    return Denuncia(rapporto, mese, tuple(risultato), senza_data)


def _ultimo_giorno_di_servizio(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime
) -> Periodo | None:
    """Ultimo giorno coperto dal servizio prima del mese; None se il servizio non c'è mai stato."""
    prima = mese.primo_giorno - timedelta(days=1)
    giorni = [
        min(fatto.valido_al or prima, prima)
        for fatto in registro.fatti_noti(rapporto, corpus.fatto_servizio, istante)
        if fatto.valido_dal <= prima
    ]
    for giorno in sorted(set(giorni), reverse=True):
        if registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, Periodo(giorno, giorno), istante)[0] is not None:
            return Periodo(giorno, giorno)
    return None


def _periodi_in_servizio(lettore: _Lettore, mese: Mese) -> list[Periodo]:
    servizio = lettore.registro.vigenti_per_giorno(lettore.rapporto, lettore.corpus.fatto_servizio, mese, lettore.noto_al)
    giorni = mese.giorni()
    return [periodo for periodo in _Calcolo(lettore, mese).periodi if servizio[giorni.index(periodo.dal)] is not None]


def periodi_in_servizio(registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime) -> list[Periodo]:
    """Periodi dichiarati del mese coperti dal servizio, come li apre la denuncia."""
    return _periodi_in_servizio(_Lettore(registro, corpus, rapporto, istante), mese)


def righe_pagate(registro: Registro, rapporto: str, mese: Mese, istante: datetime) -> list[Importo]:
    """Righe degli esiti pagati nel mese, con la loro data di pagamento."""
    return [riga.importo for riga in _righe_pagate(registro, rapporto, mese, istante)[0]]


def _controlla_cumuli(registro: Registro, corpus: Corpus, denuncia: Denuncia, istante: datetime) -> None:
    """Più rapporti, massimale e conguaglio annuo non sono modellati: se servono, la denuncia si ferma."""
    regole = corpus.denuncia
    rapporto, mese = denuncia.rapporto, denuncia.mese
    anno = Periodo(date(mese.anno, 1, 1), date(mese.anno, 12, 31))
    if regole.persona:
        codici = registro.fatti_noti(rapporto, regole.persona, istante)
        if not codici:
            raise FattoMancante(f"Rapporto {rapporto}: manca il fatto {regole.persona}, serve per i cumuli per persona")
        for altro in registro.rapporti_con_codice(regole.persona, str(codici[-1].valore), istante):
            if altro != rapporto and any(registro.vigenti_per_giorno(altro, corpus.fatto_servizio, anno, istante)):
                raise CasoNonModellato(
                    f"Rapporto {rapporto}: caso non modellato, più rapporti della stessa persona nel {mese.anno} "
                    f"(anche {altro}): l'1% e il massimale vanno calcolati per persona"
                )
    if not regole.massimale and not regole.conguaglio_annuo:
        return
    denunce = [_denuncia(registro, corpus, rapporto, Mese(mese.anno, numero), istante) for numero in range(1, mese.mese)]
    denunce.append(denuncia)
    massimale = regole.massimale
    if massimale is not None:
        totale = sum(
            (riga.valore for d in denunce for p in d.periodi if (riga := p.base(massimale.base)) is not None),
            Decimal(0),
        )
        vigenza = corpus.parametro(massimale.parametro).vigenza_per(Periodo(mese.ultimo_giorno, mese.ultimo_giorno))
        if totale > vigenza.valore:
            raise CasoNonModellato(
                f"Rapporto {rapporto}: caso non modellato, superamento del massimale annuo nel {mese.anno} "
                f"(base {massimale.base} da gennaio a {mese} = {totale}, massimale {vigenza.valore}; "
                f"{vigenza.riferimento})"
            )
    if regole.conguaglio_annuo and _mese_di_conguaglio(registro, corpus, rapporto, mese, istante):
        scattate = [
            riga
            for d in denunce
            for p in d.periodi
            for riga in p.contributi
            if riga.istituto in regole.conguaglio_annuo and riga.valore != 0
        ]
        if scattate:
            raise CasoNonModellato(
                f"Rapporto {rapporto}: caso non modellato, conguaglio annuo di {scattate[0].istituto} in {mese} "
                f"(già esposto nel periodo {scattate[0].periodo})"
            )


def _mese_di_conguaglio(registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime) -> bool:
    """Dicembre, o il mese in cui il servizio finisce."""
    if mese.mese == 12:
        return True
    esteso = Periodo(mese.primo_giorno, mese.ultimo_giorno + timedelta(days=1))
    servizio = registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, esteso, istante)
    return any(servizio[indice] and not servizio[indice + 1] for indice in range(len(servizio) - 1))
