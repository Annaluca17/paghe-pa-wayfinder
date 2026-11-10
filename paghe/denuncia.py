"""Denuncia del mese: basi imponibili per cassa e contributi (ADR 0005 e 0006).

La base somma ciò che risulta pagato nel mese: legge le righe degli esiti pagati con la
loro data di pagamento, non ricalcola la competenza. Un arretrato entra così nel mese in
cui è pagato e il mese originario non cambia. Regole di cassa, parametri e concorsi si
scelgono alla data di pagamento.

Le regole sul mese leggono il totale del mese e si espongono sull'ultimo periodo (nota di
prassi 2). I recuperi sono casi modellati (ADR 0018, ticket #43):

- in servizio: l'importo negativo si detrae dalla base del periodo, che si ferma a zero (l'E0 non espone mai un
  negativo, Manuale ListaPosPA 2017, pp. 20 e 33). L'eccedenza e' un riporto, calcolato e non registrato: passa al
  periodo in servizio successivo per la stessa base. Ogni denuncia lo ricava dalla precedente, base per base,
  in `Denuncia.riporti` (`riporto.<base>`, negativo) con la derivazione fino al recupero d'origine; nella base che lo
  detrae compare come riga. Se non entra nemmeno nel mese dopo, continua;
- su cessato: periodo fuori servizio, negativo, dopo una fine del servizio con il fatto di cessazione;
- da sospeso: il recupero pagato in un mese senza servizio, dopo una fine del servizio con il fatto di sospensione,
  non entra nel mese: passa al riporto e attende il primo periodo in servizio dopo il rientro, come ogni riporto
  aperto alla sospensione.

Cessazione e sospensione sono fatti del rapporto validi dal giorno dopo l'ultimo giorno di servizio; il rientro e'
un nuovo fatto di servizio. Una fine del servizio senza nessuno dei due, o un riporto ancora aperto alla cessazione,
fermano il calcolo e nominano il caso. Gli altri casi, e i cumuli per persona e per anno che la prima fetta non
calcola, fermano la denuncia e li nominano. Il recupero ha la data del pagamento in cui la trattenuta e' operata.
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
from .modello import MATURAZIONE_ACCANTONAMENTO, MATURAZIONE_BENEFICIO, MATURAZIONE_SOSTITUTIVA, MATURAZIONI_FISCALI, ConcorsoLetto, Derivazione, Fatto, Importo, ParametroLetto, TipoEsito
from .registro import Registro
from .tempo import Mese, Periodo, in_utc

FORMULA_BASE = "somma degli importi pagati nel periodo"
FORMULA_BASE_MESE = "somma delle basi dei periodi del mese"
FORMULA_BASE_CON_RIPORTO = f"{FORMULA_BASE}, al netto del riporto dei recuperi, ferma a zero"
FORMULA_RIPORTO = "eccedenza del recupero non detratta dalla base, riportata al periodo in servizio successivo"
RIPORTO = "riporto"
# Derivano dagli importi pagati: non sono retribuzione e non concorrono a una base.
# `onere`: a carico dell'ente, non e' retribuzione della persona (ticket #73).
# `addizionale`: addizionali regionale e comunale, dovute al conguaglio o trattenute a rate (ticket #85).
# `beneficio`: somma esente, trattamento integrativo e recuperi, non sono reddito (ticket #95).
MATURAZIONI_DERIVATE = {
    "periodo", "mese", "cassa", "onere", "addizionale", MATURAZIONE_BENEFICIO, MATURAZIONE_ACCANTONAMENTO, MATURAZIONE_SOSTITUTIVA,
} | MATURAZIONI_FISCALI
IN_SERVIZIO = "in servizio"
SU_CESSATO = "su cessato"
CESSAZIONE = "cessazione"
SOSPENSIONE = "sospensione"


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
    # Riporto dei recuperi ancora aperto a fine mese, un importo `riporto.<base>` negativo per base (ADR 0018).
    riporti: tuple[Importo, ...] = ()


@dataclass(frozen=True)
class _RigaPagata:
    """`fatto` è la data di pagamento registrata; None per una riga ipotetica, mai registrata."""

    importo: Importo
    fatto: Fatto | None


def _righe_ipotetiche(rapporto: str, mese: Mese, ipotetiche) -> list[_RigaPagata]:
    """Righe che si ipotizza pagate, ciascuna con la propria data di pagamento: entrano solo se cadono nel mese."""
    righe = []
    for riga in ipotetiche:
        if riga.data_pagamento is None:
            raise ErroreCalcolo(
                f"Rapporto {riga.rapporto}, istituto {riga.istituto}: una riga ipotetica vuole la data di pagamento"
            )
        if (
            riga.rapporto == rapporto
            and riga.derivazione.maturazione not in MATURAZIONI_DERIVATE
            and mese.primo_giorno <= riga.data_pagamento <= mese.ultimo_giorno
        ):
            righe.append(_RigaPagata(riga, None))
    return righe


def _righe_pagate(
    registro: Registro, rapporto: str, mese: Mese, istante: datetime, ipotetiche=()
) -> tuple[list[_RigaPagata], tuple[int, ...]]:
    """Righe del rapporto pagate nel mese, ed esiti che ancora non hanno una data di pagamento.

    Le righe `ipotetiche` si aggiungono a quelle registrate: servono alla simulazione di un pagamento (ADR 0025).
    """
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
    pagate.extend(_righe_ipotetiche(rapporto, mese, ipotetiche))
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


def _fine_del_servizio(
    registro: Registro, corpus: Corpus, rapporto: str, giorno: date, istante: datetime
) -> tuple[date | None, str]:
    """Ultimo giorno di servizio fino a `giorno` e come finisce: `cessazione` o `sospensione`.

    Il fatto vale dal giorno dopo l'ultimo giorno di servizio. Se il corpus non dichiara i due fatti la
    fine resta `cessazione`. Una fine senza nessuno dei due ferma il calcolo e nomina il caso (ticket #43).
    """
    ultimo = _ultimo_giorno_fino_a(registro, corpus, rapporto, giorno, istante)
    if ultimo is None or not (corpus.fatto_cessazione or corpus.fatto_sospensione):
        return ultimo, CESSAZIONE
    dopo = ultimo + timedelta(days=1)

    def presente(tipo: str | None) -> bool:
        return tipo is not None and any(
            fatto.valido_dal == dopo for fatto in registro.fatti_noti(rapporto, tipo, istante)
        )

    if presente(corpus.fatto_cessazione):
        return ultimo, CESSAZIONE
    if presente(corpus.fatto_sospensione):
        return ultimo, SOSPENSIONE
    raise CasoNonModellato(
        f"Rapporto {rapporto}: caso non modellato, il servizio finisce il {ultimo} senza cessazione né sospensione "
        f"dal {dopo}"
    )


def _ultimo_giorno_fino_a(registro: Registro, corpus: Corpus, rapporto: str, giorno: date, istante: datetime) -> date | None:
    giorni = [
        min(fatto.valido_al or giorno, giorno)
        for fatto in registro.fatti_noti(rapporto, corpus.fatto_servizio, istante)
        if fatto.valido_dal <= giorno
    ]
    for candidato in sorted(set(giorni), reverse=True):
        if registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, Periodo(candidato, candidato), istante)[0] is not None:
            return candidato
    return None


def _recuperi(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, periodo: PeriodoDenuncia, istante: datetime
) -> tuple[Recupero, ...]:
    """Classifica gli importi negativi entrati nelle basi; i casi non modellati fermano la denuncia."""
    righe: list[Importo] = []
    for base in periodo.basi:
        for riga in base.derivazione.importi:
            # Una riga negativa calcolata su un altro importo, come il dimezzamento dell'indennita' di funzione, e' una
            # riduzione dello stesso pagamento: non recupera nulla (ticket #81).
            if riga.valore < 0 and not riga.derivazione.importi and riga not in righe:
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
        _fine_del_servizio(registro, corpus, rapporto, mese.primo_giorno - timedelta(days=1), istante)
        caso = SU_CESSATO
    return tuple(Recupero(caso, riga) for riga in righe)


def _riga_recupero(riga: Importo) -> bool:
    """Importo negativo pagato, non calcolato su un altro importo (ticket #81)."""
    return riga.valore < 0 and not riga.derivazione.importi


def _residuo(
    corpus: Corpus, base: Base, periodo: Periodo, valore: Decimal, origine: tuple[Importo, ...], istante: datetime
) -> Importo:
    """Eccedenza di recupero che passa al periodo in servizio successivo, con la derivazione fino all'origine."""
    return Importo(
        rapporto=origine[0].rapporto,
        istituto=f"riporto.{base.nome}",
        periodo=periodo,
        valore=valore,
        derivazione=Derivazione(
            istituto=f"riporto.{base.nome}",
            maturazione=RIPORTO,
            regola_versione=1,
            riferimento=base.riferimento,
            formula=FORMULA_RIPORTO,
            versione_corpus=corpus.versione,
            noto_al=istante,
            parametri=(),
            fatti=(),
            importi=origine,
        ),
    )


def _con_riporto(
    importo: Importo | None, base: Base, riporto: dict[str, Importo], periodo: Periodo, corpus: Corpus, istante: datetime
) -> Importo | None:
    """Detrae dalla base del periodo il riporto entrante e ferma la base a zero; l'eccedenza resta in `riporto`.

    L'E0 non espone mai una base negativa (Manuale ListaPosPA 2017, pp. 20 e 33). Senza importi nel periodo il
    riporto non entra e continua. `riporto` si aggiorna sul posto.
    """
    entrante = riporto.get(base.nome)
    if importo is None:
        return None
    if entrante is None and importo.valore >= 0:
        return importo
    righe = importo.derivazione.importi
    totale = importo.valore
    if entrante is not None:
        giorno = min(riga.data_pagamento for riga in righe)
        applicato = replace(
            _residuo(corpus, base, periodo, entrante.valore, (entrante,), istante),
            data_pagamento=giorno,
        )
        righe = (applicato, *righe)
        totale += entrante.valore
    if totale < 0:
        origine = tuple(riga for riga in importo.derivazione.importi if _riga_recupero(riga)) or importo.derivazione.importi
        riporto[base.nome] = _residuo(
            corpus, base, periodo, totale, ((entrante,) if entrante is not None else ()) + origine, istante
        )
    else:
        riporto.pop(base.nome, None)
    return replace(
        importo,
        valore=max(totale, Decimal(0)),
        derivazione=replace(importo.derivazione, formula=FORMULA_BASE_CON_RIPORTO, importi=righe),
    )


def _base_del_periodo(
    base: Base, righe: list[_RigaPagata], periodo: Periodo, corpus: Corpus, istante: datetime, esclusione=lambda giorno: None
) -> Importo | None:
    """Una dichiarazione assente o parziale ferma il calcolo; un istituto escluso resta tracciato.

    `esclusione(giorno)` e' il fatto che toglie la persona dalla base alla data di pagamento, se la base lo dichiara.
    """
    entrano: list[_RigaPagata] = []
    letti: list[ConcorsoLetto] = []
    for riga in righe:
        importo = riga.importo
        if esclusione(importo.data_pagamento) is not None:
            continue
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
    fatti = {riga.fatto.id: riga.fatto for riga in entrano if riga.fatto is not None}
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


def _esclusione(lettore: _Lettore, base: Base):
    """Il fatto di esclusione della base valido alla data di pagamento; un motivo non ammesso ferma il calcolo."""
    if base.esclusione is None:
        return lambda giorno: None
    noti = lettore.registro.fatti_noti(lettore.rapporto, base.esclusione, lettore.noto_al)

    def alla_data(giorno: date) -> Fatto | None:
        fatto = next((f for f in reversed(noti) if f.copre(giorno)), None)
        if fatto is not None and str(fatto.valore) not in base.motivi_esclusione:
            raise CasoNonModellato(
                f"Rapporto {lettore.rapporto}: caso non modellato, il motivo {fatto.valore} del fatto {base.esclusione} "
                f"non e' uno di {', '.join(base.motivi_esclusione)}"
            )
        return fatto

    return alla_data


def _base_dei_mesi_prima(registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, base: Base, istante: datetime) -> Decimal:
    """Somma, senza limite, di cio' che e' entrato nella base nei mesi dell'anno prima di questo (massimale della base)."""
    inizio = date(mese.anno, 1, 1)
    pagamenti = registro.pagamenti(rapporto, istante)
    totale = Decimal(0)
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        fatto = pagamenti.get(esito.id)
        if fatto is None or not inizio <= fatto.valido_dal < mese.primo_giorno:
            continue
        for riga in esito.righe:
            if riga.rapporto != rapporto or riga.derivazione.maturazione in MATURAZIONI_DERIVATE:
                continue
            concorso = corpus.concorso(riga.istituto, base.nome, fatto.valido_dal)
            if concorso is not None and concorso.misura == "intero":
                totale += riga.valore
    return totale


def _con_massimale(
    importo: Importo | None, base: Base, cumulato: dict[str, Decimal], corpus: Corpus, mese: Mese, dei_mesi_prima
) -> Importo | None:
    """La base di un mese si limita a cio' che resta sotto il massimale annuo; il parametro resta nella derivazione.

    Il cumulo dei mesi prima si legge solo se la base del mese ha importi: `dei_mesi_prima(base)` lo calcola.
    """
    if importo is None or base.massimale is None:
        return importo
    if base.nome not in cumulato:
        cumulato[base.nome] = dei_mesi_prima(base)
    vigenza = corpus.parametro(base.massimale).vigenza_per(Periodo(mese.ultimo_giorno, mese.ultimo_giorno))
    spazio = max(vigenza.valore - cumulato[base.nome], Decimal(0))
    cumulato[base.nome] += importo.valore
    letto = ParametroLetto(base.massimale, vigenza.valore, vigenza.dal, vigenza.riferimento)
    return replace(
        importo,
        valore=min(importo.valore, spazio),
        derivazione=replace(
            importo.derivazione, formula=f"{FORMULA_BASE}, fino al massimale annuo", parametri=(letto,)
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
            if not self.lettore.condizioni_aggiuntive(regola, self.condizione_su, fatti):
                return None

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
    ipotetiche=(),
) -> Denuncia:
    """Periodi dichiarati del mese con basi e contributi; funzione pura di registro, corpus e istante.

    Con `ipotetiche`, righe con la loro data di pagamento, simula un pagamento non ancora avvenuto:
    non scrive nulla nel registro (ADR 0025).
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    ipotetiche = tuple(ipotetiche)
    denuncia = _denuncia(registro, corpus, rapporto, mese, istante, ipotetiche)
    if denuncia.periodi:
        _controlla_cumuli(registro, corpus, denuncia, istante)
    return denuncia


def _primo_mese_con_recupero(registro: Registro, rapporto: str, mese: Mese, istante: datetime) -> Mese | None:
    """Primo mese, prima di `mese`, in cui e' stato pagato un importo negativo: da li' puo' esserci un riporto."""
    pagamenti = registro.pagamenti(rapporto, istante)
    primi: list[date] = []
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        fatto = pagamenti.get(esito.id)
        if fatto is None or fatto.valido_dal >= mese.primo_giorno:
            continue
        if any(
            riga.rapporto == rapporto and riga.derivazione.maturazione not in MATURAZIONI_DERIVATE and _riga_recupero(riga)
            for riga in esito.righe
        ):
            primi.append(fatto.valido_dal)
    return Mese(min(primi).year, min(primi).month) if primi else None


def _riporto_entrante(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime
) -> dict[str, Importo]:
    """Residuo dei recuperi a inizio mese, ricavato mese per mese dalla denuncia precedente (ADR 0018)."""
    corrente = _primo_mese_con_recupero(registro, rapporto, mese, istante)
    riporto: dict[str, Importo] = {}
    while corrente is not None and corrente < mese:
        denuncia = _denuncia_del_mese(registro, corpus, rapporto, corrente, istante, (), riporto)
        riporto = {riga.istituto.removeprefix("riporto."): riga for riga in denuncia.riporti}
        corrente = Mese(corrente.anno + 1, 1) if corrente.mese == 12 else Mese(corrente.anno, corrente.mese + 1)
    return riporto


def _denuncia(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime, ipotetiche=()
) -> Denuncia:
    riporto = _riporto_entrante(registro, corpus, rapporto, mese, istante) if corpus.basi() else {}
    return _denuncia_del_mese(registro, corpus, rapporto, mese, istante, ipotetiche, riporto)


def _servizio_al(registro: Registro, corpus: Corpus, rapporto: str, giorno: date, istante: datetime) -> bool:
    return registro.vigenti_per_giorno(rapporto, corpus.fatto_servizio, Periodo(giorno, giorno), istante)[0] is not None


def _chiudi_il_mese(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime, riporto: dict[str, Importo]
) -> None:
    """Un riporto aperto con il servizio finito entro il mese: attende il rientro se e' sospensione, ferma se e' cessazione."""
    if not riporto or _servizio_al(registro, corpus, rapporto, mese.ultimo_giorno + timedelta(days=1), istante):
        return
    ultimo, fine = _fine_del_servizio(registro, corpus, rapporto, mese.ultimo_giorno, istante)
    if fine == CESSAZIONE:
        aperto = next(iter(riporto.values()))
        raise CasoNonModellato(
            f"Rapporto {rapporto}: caso non modellato, riporto del recupero ancora aperto alla cessazione "
            f"({aperto.istituto} = {aperto.valore}, servizio finito il {ultimo})"
        )


def _denuncia_del_mese(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    mese: Mese,
    istante: datetime,
    ipotetiche,
    riporto_entrante: dict[str, Importo],
) -> Denuncia:
    if not corpus.basi():
        raise ErroreCorpus("Il corpus non dichiara alcuna base imponibile")
    lettore = _Lettore(registro, corpus, rapporto, istante)
    lettore.controlla_fermi(mese, {"calcolo", "denuncia"})
    pagate, senza_data = _righe_pagate(registro, rapporto, mese, istante, ipotetiche)

    riporto = dict(riporto_entrante)
    periodi = _periodi_in_servizio(lettore, mese)
    in_servizio = bool(periodi)
    if not in_servizio:
        pagate = _recuperi_da_sospeso(registro, corpus, lettore, rapporto, mese, istante, pagate, riporto)
        if not pagate:
            _chiudi_il_mese(registro, corpus, rapporto, mese, istante, riporto)
            return Denuncia(rapporto, mese, (), senza_data, tuple(riporto.values()))
        periodi = [mese.periodo]

    gruppi: dict[Periodo, list[_RigaPagata]] = {periodo: [] for periodo in periodi}
    for riga in pagate:
        gruppi[_periodo_della_riga(riga.importo, periodi, mese)].append(riga)

    sul_periodo = corpus.istituti_di_cassa - corpus.istituti_sul_mese
    condizione_su = None if in_servizio else _ultimo_giorno_di_servizio(registro, corpus, rapporto, mese, istante)
    cumulato: dict[str, Decimal] = {}

    def dei_mesi_prima(base: Base) -> Decimal:
        return _base_dei_mesi_prima(registro, corpus, rapporto, mese, base, istante)

    def _del_periodo(base: Base, righe: list[_RigaPagata], periodo: Periodo) -> Importo | None:
        """Base del periodo; in servizio con il riporto dei recuperi, fuori servizio il recupero resta negativo."""
        importo = _base_del_periodo(base, righe, periodo, corpus, istante, _esclusione(lettore, base))
        return _con_riporto(importo, base, riporto, periodo, corpus, istante) if in_servizio else importo

    risultato: list[PeriodoDenuncia] = []
    for periodo in periodi:
        basi = tuple(
            importo
            for importo in (
                _con_massimale(
                    _del_periodo(base, gruppi[periodo], periodo),
                    base, cumulato, corpus, mese, dei_mesi_prima
                )
                for base in corpus.basi()
            )
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
    _chiudi_il_mese(registro, corpus, rapporto, mese, istante, riporto)
    return Denuncia(rapporto, mese, tuple(risultato), senza_data, tuple(riporto.values()))


def _recuperi_da_sospeso(
    registro: Registro,
    corpus: Corpus,
    lettore: _Lettore,
    rapporto: str,
    mese: Mese,
    istante: datetime,
    pagate: list[_RigaPagata],
    riporto: dict[str, Importo],
) -> list[_RigaPagata]:
    """Mese senza servizio: i recuperi di un sospeso passano al riporto, il resto resta nel mese.

    Da cessato i recuperi restano nel mese (caso `su cessato`); `riporto` si aggiorna sul posto.
    """
    recuperi = [riga for riga in pagate if _riga_recupero(riga.importo)]
    if not recuperi:
        return pagate
    if _fine_del_servizio(registro, corpus, rapporto, mese.primo_giorno - timedelta(days=1), istante)[1] != SOSPENSIONE:
        return pagate
    for base in corpus.basi():
        importo = _base_del_periodo(base, recuperi, mese.periodo, corpus, istante, _esclusione(lettore, base))
        if importo is None:
            continue
        entrante = riporto.get(base.nome)
        origine = ((entrante,) if entrante is not None else ()) + importo.derivazione.importi
        totale = importo.valore + (entrante.valore if entrante is not None else Decimal(0))
        riporto[base.nome] = _residuo(corpus, base, mese.periodo, totale, origine, istante)
    return [riga for riga in pagate if riga not in recuperi]


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


def rapporti_della_vista(
    registro: Registro, corpus: Corpus, vista: str, mese: Mese, rapporti, noto_al: datetime | None = None
) -> tuple[str, ...]:
    """I `rapporti` che il regime assegna alla vista nel mese, nell'ordine dato (ADR 0015).

    Un rapporto e' della vista se nel mese ha un importo pagato che concorre per intero a una delle basi dichiarate, o di
    uno degli istituti dichiarati. La vista non conosce i titoli. Senza dichiarazione per la vista il corpus e' incompleto.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    dichiarazione = corpus.output(vista, mese.ultimo_giorno)
    if dichiarazione is None:
        raise ErroreCorpus(f"Il corpus non dichiara quali rapporti assegna alla vista {vista} per {mese}")
    risultato = []
    for rapporto in rapporti:
        pagamenti = registro.pagamenti(rapporto, istante)
        for esito in registro.esiti(TipoEsito.PAGATO, istante):
            fatto = pagamenti.get(esito.id)
            if fatto is None or not mese.primo_giorno <= fatto.valido_dal <= mese.ultimo_giorno:
                continue
            if any(
                riga.rapporto == rapporto and _assegnata(corpus, dichiarazione, riga, fatto.valido_dal) for riga in esito.righe
            ):
                risultato.append(rapporto)
                break
    return tuple(risultato)


def _assegnata(corpus: Corpus, dichiarazione, riga: Importo, giorno: date) -> bool:
    if riga.istituto in dichiarazione.istituti:
        return True
    if riga.derivazione.maturazione in MATURAZIONI_DERIVATE:
        return False
    return any(
        (concorso := corpus.concorso(riga.istituto, base, giorno)) is not None and concorso.misura == "intero"
        for base in dichiarazione.basi
    )


def _controlla_cumuli(registro: Registro, corpus: Corpus, denuncia: Denuncia, istante: datetime) -> None:
    """Più rapporti, massimale e conguaglio annuo non sono modellati: se servono, la denuncia si ferma."""
    regole = corpus.denuncia
    rapporto, mese = denuncia.rapporto, denuncia.mese
    anno = Periodo(date(mese.anno, 1, 1), date(mese.anno, 12, 31))
    if regole.persona:
        persona = registro.persona_del_rapporto(rapporto, istante)
        if persona is None:
            raise FattoMancante(f"Rapporto {rapporto}: manca il legame con la persona, serve per i cumuli per persona")
        if not registro.fatti_persona_noti(persona, regole.persona, istante):
            raise FattoMancante(
                f"Persona {persona}: manca il fatto {regole.persona}, serve per i cumuli per persona"
            )
        for altro in registro.rapporti_della_persona(persona, istante):
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
