"""Denuncia del mese: basi imponibili per cassa e contributi (ADR 0005 e 0006).

La base somma ciò che risulta pagato nel mese: legge le righe degli esiti pagati con la
loro data di pagamento, non ricalcola la competenza. Un arretrato entra così nel mese in
cui è pagato e il mese originario non cambia. Regole di cassa, parametri e concorsi si
scelgono alla data di pagamento.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal

from .calcolo import _Calcolo, _Lettore
from .corpus import Base, Corpus, Regola
from .errori import ConcorsoMancante, ConcorsoParziale, ErroreCalcolo, ErroreCorpus, ValiditaNonUniforme
from .formula import valuta
from .modello import ConcorsoLetto, Derivazione, Fatto, Importo, ParametroLetto, TipoEsito
from .registro import Registro
from .tempo import Mese, Periodo, in_utc

FORMULA_BASE = "somma degli importi pagati nel periodo"
# Derivano dagli importi pagati: non sono retribuzione e non concorrono a una base.
MATURAZIONI_DERIVATE = {"periodo", "cassa"}


@dataclass(frozen=True)
class PeriodoDenuncia:
    """Periodo dichiarato del mese. `in_servizio` falso: importi pagati in un mese senza servizio."""

    periodo: Periodo
    in_servizio: bool
    basi: tuple[Importo, ...] = ()
    contributi: tuple[Importo, ...] = ()

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
    """Regole di cassa di un periodo, valutate alle date di pagamento degli importi nelle basi."""

    def __init__(self, lettore: _Lettore, periodo: Periodo, basi: tuple[Importo, ...]):
        self.lettore = lettore
        self.corpus = lettore.corpus
        self.periodo = periodo
        self.basi = {riga.istituto.removeprefix("base."): riga for riga in basi}
        self.date = sorted({riga.data_pagamento for base in basi for riga in base.derivazione.importi})
        self._calcolati: dict[str, Importo | None] = {}

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
    if not corpus.basi():
        raise ErroreCorpus("Il corpus non dichiara alcuna base imponibile")
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    lettore = _Lettore(registro, corpus, rapporto, istante)
    pagate, senza_data = _righe_pagate(registro, rapporto, mese, istante)

    servizio = registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, mese, istante)
    giorni = mese.giorni()
    periodi = [
        periodo
        for periodo in _Calcolo(lettore, mese).periodi
        if servizio[giorni.index(periodo.dal)] is not None
    ]
    in_servizio = bool(periodi)
    if not in_servizio:
        if not pagate:
            return Denuncia(rapporto, mese, (), senza_data)
        periodi = [mese.periodo]

    gruppi: dict[Periodo, list[_RigaPagata]] = {periodo: [] for periodo in periodi}
    for riga in pagate:
        gruppi[_periodo_della_riga(riga.importo, periodi, mese)].append(riga)

    risultato = []
    for periodo in periodi:
        basi = tuple(
            importo
            for importo in (_base_del_periodo(base, gruppi[periodo], periodo, corpus, istante) for base in corpus.basi())
            if importo is not None
        )
        contributi: tuple[Importo, ...] = ()
        if basi:
            calcolo = _Contributi(lettore, periodo, basi)
            contributi = tuple(
                importo
                for importo in (calcolo.importo(istituto) for istituto in sorted(corpus.istituti_di_cassa))
                if importo is not None
            )
        risultato.append(PeriodoDenuncia(periodo, in_servizio, basi, contributi))
    return Denuncia(rapporto, mese, tuple(risultato), senza_data)
