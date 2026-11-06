"""Proiezione degli importi dal registro, differenze rispetto agli esiti, spiegazione."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal

from .corpus import Corpus
from .errori import ErroreCalcolo, FattoMancante
from .formula import valuta
from .modello import Derivazione, Esito, Fatto, Importo, ParametroLetto, TipoEsito
from .registro import Registro
from .tempo import Mese, in_utc


class _Calcolo:
    def __init__(self, registro: Registro, corpus: Corpus, rapporto: str, competenza: Mese, noto_al: datetime):
        self.registro = registro
        self.corpus = corpus
        self.rapporto = rapporto
        self.competenza = competenza
        self.noto_al = noto_al
        self.calcolati: dict[str, Importo | None] = {}

    def importo(self, istituto: str) -> Importo | None:
        """None se la regola non si applica al rapporto (`applica_se` senza fatto)."""
        if istituto in self.calcolati:
            return self.calcolati[istituto]
        regola = self.corpus.regola_per(istituto, self.competenza)
        if regola is None:
            raise ErroreCalcolo(f"Istituto {istituto}: nessuna regola vigente per {self.competenza}")

        fatti: dict[int, Fatto] = {}
        if regola.applica_se is not None:
            condizione = self._fatto(regola.applica_se)
            if condizione is None:
                self.calcolati[istituto] = None
                return None
            fatti[condizione.id] = condizione

        parametri: dict[str, ParametroLetto] = {}
        dipendenze: dict[str, Importo] = {}

        def risolvi(origine: str, nome: str) -> Decimal:
            if origine == "fatto":
                fatto = self._fatto(nome)
                if fatto is None:
                    raise FattoMancante(
                        f"Rapporto {self.rapporto}, istituto {istituto}: "
                        f"manca il fatto {nome} per {self.competenza}"
                    )
                fatti[fatto.id] = fatto
                return fatto.valore
            if origine == "parametro":
                vigenza = self.corpus.parametro(nome).vigenza_per(self.competenza)
                parametri[nome] = ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento)
                return vigenza.valore
            dipendenza = self.importo(nome)
            if dipendenza is None:
                return Decimal(0)
            dipendenze[nome] = dipendenza
            return dipendenza.valore

        valore = valuta(regola.formula, risolvi)
        risultato = Importo(
            rapporto=self.rapporto,
            istituto=istituto,
            competenza=self.competenza,
            valore=valore,
            derivazione=Derivazione(
                istituto=istituto,
                regola_versione=regola.versione,
                riferimento=regola.riferimento,
                formula=regola.formula,
                versione_corpus=self.corpus.versione,
                noto_al=self.noto_al,
                parametri=tuple(parametri[nome] for nome in sorted(parametri)),
                fatti=tuple(fatti[numero] for numero in sorted(fatti)),
                importi=tuple(dipendenze[nome] for nome in sorted(dipendenze)),
            ),
        )
        self.calcolati[istituto] = risultato
        return risultato

    def _fatto(self, tipo: str) -> Fatto | None:
        return self.registro.fatto_nel_mese(self.rapporto, tipo, self.competenza, self.noto_al)


def calcola(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    competenza: Mese,
    noto_al: datetime | None = None,
) -> tuple[Importo, ...]:
    """Stato completo del periodo; funzione pura di registro, corpus e istante."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    calcolo = _Calcolo(registro, corpus, rapporto, competenza, istante)
    importi = []
    for istituto in corpus.istituti():
        if corpus.regola_per(istituto, competenza) is None:
            continue
        importo = calcolo.importo(istituto)
        if importo is not None:
            importi.append(importo)
    return tuple(importi)


@dataclass(frozen=True)
class Differenza:
    rapporto: str
    istituto: str
    competenza: Mese
    dovuto: Decimal
    gia_esitato: Decimal
    esiti: tuple[int, ...]
    _base: Importo

    @property
    def valore(self) -> Decimal:
        return self.dovuto - self.gia_esitato

    def importo(self) -> Importo:
        """La differenza come importo da includere in un nuovo esito."""
        return replace(self._base, valore=self.valore, esiti_confrontati=self.esiti)


def _esiti_di_confronto(registro: Registro, rapporto: str, competenza: Mese, tipo: TipoEsito, istante: datetime) -> list[Esito]:
    """Pagato e versato si sommano; una dichiarazione sostituisce per intero il periodo."""
    interessati = [
        esito
        for esito in registro.esiti(tipo, istante)
        if any(riga.rapporto == rapporto and riga.competenza == competenza for riga in esito.righe)
    ]
    if tipo is TipoEsito.DICHIARATO:
        return interessati[-1:]
    return interessati


def differenze(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    competenza: Mese,
    tipo: TipoEsito,
    noto_al: datetime | None = None,
) -> tuple[Differenza, ...]:
    """Dovuto ricalcolato meno quanto risulta dagli esiti, mai da un ricalcolo del passato."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    dovuti = {importo.istituto: importo for importo in calcola(registro, corpus, rapporto, competenza, istante)}

    esitati: dict[str, Decimal] = {}
    fonti: dict[str, list[int]] = {}
    ultima_riga: dict[str, Importo] = {}
    for esito in _esiti_di_confronto(registro, rapporto, competenza, tipo, istante):
        for riga in esito.righe:
            if riga.rapporto == rapporto and riga.competenza == competenza:
                esitati[riga.istituto] = esitati.get(riga.istituto, Decimal(0)) + riga.valore
                fonti.setdefault(riga.istituto, []).append(esito.id)
                ultima_riga[riga.istituto] = riga

    risultato = []
    for istituto in sorted(dovuti.keys() | esitati.keys()):
        dovuto = dovuti[istituto].valore if istituto in dovuti else Decimal(0)
        gia_esitato = esitati.get(istituto, Decimal(0))
        if dovuto != gia_esitato:
            risultato.append(
                Differenza(
                    rapporto=rapporto,
                    istituto=istituto,
                    competenza=competenza,
                    dovuto=dovuto,
                    gia_esitato=gia_esitato,
                    esiti=tuple(fonti.get(istituto, ())),
                    _base=dovuti.get(istituto) or ultima_riga[istituto],
                )
            )
    return tuple(risultato)


def emetti_esito(registro: Registro, tipo: TipoEsito, data: date, righe) -> Esito:
    """Fissa gli importi in un'istantanea verso terzi."""
    return registro.registra_esito(tipo, data, righe)


def spiega(importo: Importo, rientro: int = 0) -> str:
    """Catena leggibile: importo, regola e norma, parametri, fatti e atti, importi d'origine."""
    margine = "  " * rientro
    d = importo.derivazione
    righe = [
        f"{margine}{importo.istituto} [{importo.competenza}] rapporto {importo.rapporto}: {importo.valore}",
        f"{margine}  regola v{d.regola_versione}: {d.formula}",
        f"{margine}  riferimento: {d.riferimento}",
    ]
    if importo.esiti_confrontati:
        elenco = ", ".join(f"#{numero}" for numero in importo.esiti_confrontati)
        righe.append(f"{margine}  differenza rispetto agli esiti: {elenco}")
    for parametro in d.parametri:
        righe.append(
            f"{margine}  parametro {parametro.nome} = {parametro.valore} "
            f"(dal {parametro.dal}; fonte: {parametro.riferimento})"
        )
    for fatto in d.fatti:
        atto = f"; atto: {fatto.atto.riferimento} del {fatto.atto.data}" if fatto.atto else ""
        righe.append(
            f"{margine}  fatto #{fatto.id} {fatto.tipo} = {fatto.valore} "
            f"(valido dal {fatto.valido_dal}; registrato {fatto.registrato_il:%Y-%m-%d %H:%M}{atto})"
        )
    for dipendenza in d.importi:
        righe.append(spiega(dipendenza, rientro + 1))
    return "\n".join(righe)
