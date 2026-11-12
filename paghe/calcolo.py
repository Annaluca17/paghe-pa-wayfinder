"""Proiezione degli importi dal registro, differenze rispetto agli esiti, spiegazione.

Il mese si divide in frazioni in cui fatti, regole e parametri sono uniformi. Le regole
a giorni e a evento producono un importo per frazione; quelle sul periodo dichiarato ne
leggono la somma; quelle annuali si calcolano sul servizio dell'anno (ADR 0004).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, localcontext
from typing import Callable

from .corpus import Corpus, Regola
from .errori import CasoNonModellato, ErroreCalcolo, FattoMancante
from .formula import PRECISIONE, riferimenti, valuta
from .modello import (
    FATTO_PART_TIME,
    MATURAZIONI_FISCALI,
    Derivazione,
    Esito,
    Fatto,
    Importo,
    ParametroLetto,
    Quota,
    RiduzionePartTime,
    TipoEsito,
)
from .registro import Registro
from .riferimento import solo_prassi
from .tempo import Mese, Periodo, in_utc


def _arrotonda(valore: Decimal, decimali: int) -> Decimal:
    return valore.quantize(Decimal(1).scaleb(-decimali), rounding=ROUND_HALF_UP)


def _raggruppa(giorni: list[date], firme: list[tuple]) -> list[Periodo]:
    """Periodi massimali di giorni consecutivi con la stessa firma."""
    periodi = []
    inizio = 0
    for indice in range(1, len(giorni) + 1):
        if indice == len(giorni) or firme[indice] != firme[inizio]:
            periodi.append(Periodo(giorni[inizio], giorni[indice - 1]))
            inizio = indice
    return periodi


class _Lettore:
    """Valuta una regola su un periodo e raccoglie ciò che ha letto."""

    def __init__(
        self, registro: Registro, corpus: Corpus, rapporto: str, noto_al: datetime, pagamento: date | None = None
    ):
        self.registro = registro
        self.corpus = corpus
        self.rapporto = rapporto
        self.noto_al = noto_al
        self.pagamento = pagamento  # data di pagamento: sceglie la vigenza applicabile dei parametri (ADR 0041)

    def fatto(self, tipo: str, periodo: Periodo) -> Fatto | None:
        return self.registro.fatto_nel_periodo(self.rapporto, tipo, periodo, self.noto_al)

    def valore_fatto(self, istituto: str, tipo: str, periodo: Periodo, fatti: dict[int, Fatto]) -> Decimal:
        """Valore numerico letto da una formula; un fatto assente o categoriale ferma il calcolo."""
        fatto = self.fatto(tipo, periodo)
        if fatto is None:
            raise FattoMancante(
                f"Rapporto {self.rapporto}, istituto {istituto}: manca il fatto {tipo} per {periodo}"
            )
        if fatto.categoriale:
            raise ErroreCalcolo(
                f"Rapporto {self.rapporto}, istituto {istituto}: il fatto {tipo} è un codice, una formula non lo legge"
            )
        fatti[fatto.id] = fatto
        return fatto.valore

    def soddisfa(self, regola: Regola, fatto: Fatto) -> bool:
        """`applica_se = "tipo=codice"` vale solo per un fatto categoriale con quel codice."""
        codice = regola.codice_condizione
        if codice is None:
            return True
        if not fatto.categoriale:
            raise ErroreCalcolo(
                f"Rapporto {self.rapporto}, istituto {regola.istituto}: il fatto {fatto.tipo} non è un codice, "
                f"la condizione {regola.applica_se} non si può verificare"
            )
        return fatto.valore == codice

    def condizioni_aggiuntive(self, regola: Regola, periodo: Periodo, fatti: dict[int, Fatto]) -> bool:
        """`anche_se`: ogni altra condizione `tipo=codice` vale nel periodo; i fatti letti restano nella derivazione."""
        for tipo, codice in regola.condizioni_aggiuntive:
            fatto = self.fatto(tipo, periodo)
            if fatto is None:
                return False
            if not fatto.categoriale:
                raise ErroreCalcolo(
                    f"Rapporto {self.rapporto}, istituto {regola.istituto}: il fatto {tipo} non è un codice, "
                    f"la condizione {tipo}={codice} non si può verificare"
                )
            if fatto.valore != codice:
                return False
            fatti[fatto.id] = fatto
        return True

    def controlla_fermi(self, periodo: Mese | Periodo, ambiti: set[str]) -> None:
        """Un fatto dichiarato come fermo nel periodo chiede un caso non modellato (ADR 0005)."""
        for fermo in self.corpus.fermi:
            if fermo.ambito not in ambiti:
                continue
            if fermo.manca:
                self._controlla_fatto_obbligatorio(fermo, periodo)
                continue
            if fermo.solo_se is not None:
                self._controlla_fatto_nel_suo_regime(fermo, periodo)
                continue
            presenti = [
                f
                for f in self.registro.vigenti_per_giorno(self.rapporto, fermo.fatto, periodo, self.noto_al)
                if f and (fermo.codice is None or str(f.valore) == fermo.codice)
            ]
            if presenti:
                valore = f" = {fermo.codice}" if fermo.codice is not None else ""
                raise CasoNonModellato(
                    f"Rapporto {self.rapporto}: caso non modellato, {fermo.caso} "
                    f"(fatto {fermo.fatto}{valore} dal {presenti[0].valido_dal}; {fermo.riferimento})"
                )

    def _controlla_fatto_obbligatorio(self, fermo, periodo: Mese | Periodo) -> None:
        """Un fermo `manca`: dove vale la condizione `se`, il fatto deve esserci ogni giorno, senza scegliere un valore."""
        tipo, _, codice = fermo.se.partition("=")
        condizioni = self.registro.vigenti_per_giorno(self.rapporto, tipo, periodo, self.noto_al)
        presenti = self.registro.vigenti_per_giorno(self.rapporto, fermo.fatto, periodo, self.noto_al)
        for giorno, condizione, presente in zip(periodo.giorni(), condizioni, presenti):
            if not condizione or (codice and str(condizione.valore) != codice):
                continue
            if not presente:
                raise CasoNonModellato(
                    f"Rapporto {self.rapporto}: caso non modellato, {fermo.caso} "
                    f"(manca il fatto {fermo.fatto} il {giorno} con {fermo.se}; {fermo.riferimento})"
                )
            if fermo.valori is not None and not (presente.categoriale and str(presente.valore) in fermo.valori):
                raise CasoNonModellato(
                    f"Rapporto {self.rapporto}: caso non modellato, {fermo.caso} "
                    f"(il fatto {fermo.fatto} = {presente.valore} il {giorno} non è uno di {', '.join(fermo.valori)}; "
                    f"{fermo.riferimento})"
                )

    def _controlla_fatto_nel_suo_regime(self, fermo, periodo: Mese | Periodo) -> None:
        """Un fermo `solo_se`: il fatto presente in un giorno in cui la condizione ha un altro valore è fuori dal suo regime.

        I giorni senza il fatto della condizione (fuori servizio, dopo una cessazione) non si guardano: un fatto rimasto
        aperto oltre la fine del rapporto non è un errore di regime."""
        tipo, _, codice = fermo.solo_se.partition("=")
        condizioni = self.registro.vigenti_per_giorno(self.rapporto, tipo, periodo, self.noto_al)
        presenti = self.registro.vigenti_per_giorno(self.rapporto, fermo.fatto, periodo, self.noto_al)
        for giorno, condizione, presente in zip(periodo.giorni(), condizioni, presenti):
            if presente and condizione and codice and str(condizione.valore) != codice:
                raise CasoNonModellato(
                    f"Rapporto {self.rapporto}: caso non modellato, {fermo.caso} "
                    f"(il fatto {fermo.fatto} il {giorno} è fuori dal suo regime, vale solo con {fermo.solo_se}; "
                    f"{fermo.riferimento})"
                )

    def parametro(self, nome: str, periodo: Periodo) -> ParametroLetto:
        vigenza = self.corpus.parametro(nome).vigenza_per(periodo, self.pagamento)
        return ParametroLetto(nome, vigenza.valore, vigenza.dal, vigenza.riferimento, vigenza.applicabile_dal)

    def importo(
        self,
        regola: Regola,
        periodo: Periodo,
        leggi_importo: Callable[[str], list[Importo]],
    ) -> Importo | None:
        """None se la regola non si applica (`applica_se` senza fatto, importi letti assenti)."""
        fatti: dict[int, Fatto] = {}
        if regola.applica_se is not None:
            condizione = self.fatto(regola.fatto_condizione, periodo)
            if condizione is None or not self.soddisfa(regola, condizione):
                return None
            fatti[condizione.id] = condizione
            if not self.condizioni_aggiuntive(regola, periodo, fatti):
                return None

        parametri: dict[str, ParametroLetto] = {}
        dipendenze: dict[tuple, Importo] = {}

        def risolvi(origine: str, nome: str) -> Decimal:
            if origine == "fatto":
                return self.valore_fatto(regola.istituto, nome, periodo, fatti)
            if origine == "parametro":
                parametri[nome] = self.parametro(nome, periodo)
                return parametri[nome].valore
            lette = leggi_importo(nome)
            for riga in lette:
                dipendenze[riga.chiave] = riga
            return sum((riga.valore for riga in lette), Decimal(0))

        valore = valuta(regola.formula, risolvi)
        if riferimenti(regola.formula).importi and not dipendenze and regola.applica_se is None:
            return None
        righe = [dipendenze[chiave] for chiave in sorted(dipendenze, key=str)]
        return Importo(
            rapporto=self.rapporto,
            istituto=regola.istituto,
            periodo=periodo,
            valore=valore,
            derivazione=Derivazione(
                istituto=regola.istituto,
                maturazione=regola.maturazione,
                regola_versione=regola.versione,
                riferimento=regola.riferimento,
                formula=regola.formula,
                versione_corpus=self.corpus.versione,
                noto_al=self.noto_al,
                parametri=tuple(parametri[nome] for nome in sorted(parametri)),
                fatti=tuple(fatti[numero] for numero in sorted(fatti)),
                importi=tuple(righe),
            ),
        )


    def con_part_time(self, regola: Regola, periodo: Periodo, importo: Importo) -> Importo:
        """Rapporto in part-time: l'importo pieno della frazione si riduce secondo il trattamento dichiarato (ADR 0026)."""
        if riferimenti(regola.formula).importi:
            return importo  # deriva da importi già ridotti
        percentuale = self.fatto(FATTO_PART_TIME, periodo)
        if percentuale is None:
            return importo
        dichiarazione = self.corpus.trattamento_part_time(regola.istituto, periodo.dal)
        if dichiarazione is None or not dichiarazione.copre(periodo.al):
            raise CasoNonModellato(
                f"Rapporto {self.rapporto}: caso non modellato, l'istituto {regola.istituto} non dichiara il "
                f"trattamento nel part-time per {periodo} (fatto {FATTO_PART_TIME} dal {percentuale.valido_dal})"
            )
        fatti = {fatto.id: fatto for fatto in importo.derivazione.fatti}
        fatti[percentuale.id] = percentuale
        misura = percentuale
        if dichiarazione.trattamento == "da_integrativo":
            misura = self.fatto(dichiarazione.fatto, periodo)
            if misura is None:
                raise CasoNonModellato(
                    f"Rapporto {self.rapporto}: caso non modellato, il trattamento nel part-time di {regola.istituto} "
                    f"è da integrativo e manca l'input da atto (fatto {dichiarazione.fatto}) per {periodo}"
                )
            if misura.atto is None or misura.categoriale:
                raise CasoNonModellato(
                    f"Rapporto {self.rapporto}: caso non modellato, il fatto {dichiarazione.fatto} di {regola.istituto} "
                    f"non è un valore numerico con atto (#{misura.id})"
                )
            fatti[misura.id] = misura
        valore = importo.valore
        if dichiarazione.trattamento != "intero":
            with localcontext() as contesto:
                contesto.prec = PRECISIONE
                valore = _arrotonda(importo.valore * misura.valore / 100, regola.decimali)
        return replace(
            importo,
            valore=valore,
            derivazione=replace(
                importo.derivazione,
                fatti=tuple(fatti[numero] for numero in sorted(fatti)),
                part_time=RiduzionePartTime(misura.valore, importo.valore, dichiarazione.trattamento),
            ),
        )


class _Calcolo:
    def __init__(self, lettore: _Lettore, competenza: Mese):
        self.lettore = lettore
        self.corpus = lettore.corpus
        self.competenza = competenza
        giorni = competenza.giorni()
        self.frazioni = _raggruppa(giorni, self._firme(giorni, self.corpus.tipi_fatto(), True))
        self.periodi = _raggruppa(giorni, self._firme(giorni, self.corpus.fatti_periodo_dichiarato, False))
        self._righe_frazione: dict[str, dict[int, Importo]] = {}
        self._righe_periodo: dict[str, dict[int, Importo]] = {}

    def _firme(self, giorni: list[date], tipi: tuple[str, ...], con_corpus: bool) -> list[tuple]:
        lettore = self.lettore
        periodo = Periodo(giorni[0], giorni[-1])
        vigenti = [
            lettore.registro.vigenti_per_giorno(lettore.rapporto, tipo, periodo, lettore.noto_al)
            for tipo in tipi
        ]
        firme = []
        for indice, giorno in enumerate(giorni):
            # Le frazioni seguono ogni fatto; un periodo dichiarato solo i cambi di valore.
            parte_fatti = tuple(
                (colonna[indice].id if con_corpus else colonna[indice].valore) if colonna[indice] else None
                for colonna in vigenti
            )
            firme.append((parte_fatti, self.corpus.firma_giorno(giorno, lettore.pagamento) if con_corpus else ()))
        return firme

    def _regola_richiesta(self, istituto: str, periodo: Periodo) -> Regola:
        regola = self.corpus.regola_per(istituto, periodo)
        if regola is None:
            raise ErroreCalcolo(f"Istituto {istituto}: nessuna regola vigente per {periodo}")
        return regola

    def righe_frazione(self, istituto: str) -> dict[int, Importo]:
        if istituto in self._righe_frazione:
            return self._righe_frazione[istituto]
        righe: dict[int, Importo] = {}
        for indice, frazione in enumerate(self.frazioni):
            regola = self.corpus.regola_per(istituto, frazione)
            if regola is None or regola.maturazione in ("periodo", "mese", "annuale"):
                continue

            def leggi(nome: str, posizione: int = indice, tratto: Periodo = frazione) -> list[Importo]:
                self._regola_richiesta(nome, tratto)
                riga = self.righe_frazione(nome).get(posizione)
                return [riga] if riga else []

            importo = self.lettore.importo(regola, frazione, leggi)
            if importo is not None:
                righe[indice] = self.lettore.con_part_time(regola, frazione, importo)
        righe = self._applica_quote(istituto, righe)
        self._righe_frazione[istituto] = righe
        return righe

    def _applica_quote(self, istituto: str, righe: dict[int, Importo]) -> dict[int, Importo]:
        """Le regole a giorni: la formula dà il mensile, la quota lo riporta alla frazione."""
        ordinate = sorted(righe)
        if not ordinate or righe[ordinate[0]].derivazione.maturazione not in ("giorni", "onere"):
            return righe
        coperti = sum(righe[indice].periodo.giorni_calendario for indice in ordinate)
        intero = coperti == len(self.competenza.giorni())
        stessa_base = len({righe[indice].valore for indice in ordinate}) == 1
        risultato: dict[int, Importo] = {}
        with localcontext() as contesto:
            contesto.prec = PRECISIONE
            residuo = Decimal(1)
            pagato = Decimal(0)
            for posizione, indice in enumerate(ordinate):
                riga = righe[indice]
                regola = self._regola_richiesta(istituto, riga.periodo)
                ultima = posizione == len(ordinate) - 1
                giorni = (
                    riga.periodo.giorni_lun_sab if regola.conteggio == "lun_sab" else riga.periodo.giorni_calendario
                )
                parametri = riga.derivazione.parametri
                if intero and ultima:
                    divisore = None
                    quota = residuo
                else:
                    if regola.divisore is not None:
                        letto = self.lettore.parametro(regola.divisore, riga.periodo)
                        divisore = letto.valore
                        parametri = tuple(sorted((*parametri, letto), key=lambda p: p.nome))
                    else:
                        divisore = Decimal(len(self.competenza.giorni()))
                    quota = min(Decimal(giorni) / divisore, residuo)
                residuo -= quota
                if intero and ultima and stessa_base:
                    valore = _arrotonda(riga.valore - pagato, regola.decimali)
                else:
                    valore = _arrotonda(riga.valore * quota, regola.decimali)
                pagato += valore
                risultato[indice] = replace(
                    riga,
                    valore=valore,
                    derivazione=replace(
                        riga.derivazione,
                        parametri=parametri,
                        quota=Quota(regola.conteggio, giorni, divisore, quota, riga.valore),
                    ),
                )
        return risultato

    def righe_periodo(self, istituto: str) -> dict[int, Importo]:
        if istituto in self._righe_periodo:
            return self._righe_periodo[istituto]
        righe: dict[int, Importo] = {}
        if istituto in self.corpus.istituti_di_cassa:
            return righe
        for indice, periodo in enumerate(self.periodi):
            regola = self.corpus.regola_per(istituto, periodo)
            if regola is None or regola.maturazione != "periodo":
                continue

            def leggi(nome: str, posizione: int = indice, tratto: Periodo = periodo) -> list[Importo]:
                dipendenza = self._regola_richiesta(nome, tratto)
                if dipendenza.maturazione == "periodo":
                    riga = self.righe_periodo(nome).get(posizione)
                    return [riga] if riga else []
                return [
                    riga
                    for posto, riga in sorted(self.righe_frazione(nome).items())
                    if tratto.contiene(self.frazioni[posto])
                ]

            importo = self.lettore.importo(regola, periodo, leggi)
            if importo is None:
                continue
            letti = importo.derivazione.importi
            if letti:
                dal = min(riga.periodo.dal for riga in letti)
                al = max(riga.periodo.al for riga in letti)
                importo = replace(importo, periodo=Periodo(dal, al))
            righe[indice] = importo
        self._righe_periodo[istituto] = righe
        return righe


def calcola(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    competenza: Mese,
    noto_al: datetime | None = None,
    pagamento: date | None = None,
) -> tuple[Importo, ...]:
    """Stato completo del mese; funzione pura di registro, corpus e istante. Esclude gli annuali.

    `pagamento` è la data in cui l'importo si paga: sceglie, tra le vigenze dei parametri, quelle già applicabili
    (ADR 0041). Senza, l'applicabilità non conta e vale la decorrenza."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    lettore = _Lettore(registro, corpus, rapporto, istante, pagamento)
    lettore.controlla_fermi(competenza, {"calcolo"})
    calcolo = _Calcolo(lettore, competenza)
    importi: list[Importo] = []
    for istituto in corpus.istituti():
        importi.extend(calcolo.righe_frazione(istituto).values())
        importi.extend(calcolo.righe_periodo(istituto).values())
    return tuple(sorted(importi, key=lambda i: (i.istituto, i.periodo)))


def _giorni_dell_annuale(lettore: _Lettore, regola: Regola, anno: Periodo) -> list[date]:
    """Giorni dell'anno su cui matura una regola annuale.

    Con una condizione `tipo=codice` e un fatto di servizio nel corpus, i giorni sono quelli di servizio e la condizione
    vale sull'ultimo: chi cambia codice nell'anno matura tutto l'anno sulla regola dell'ultimo giorno (ADR 0038).
    Altrimenti i giorni sono quelli in cui il fatto della condizione è presente.
    """
    registro, rapporto, istante = lettore.registro, lettore.rapporto, lettore.noto_al
    servizio = lettore.corpus.fatto_servizio
    if regola.codice_condizione is None or servizio is None:
        vigenti = registro.vigenti_per_giorno(rapporto, regola.fatto_condizione, anno, istante)
        return [g for g, fatto in zip(anno.giorni(), vigenti) if fatto is not None and lettore.soddisfa(regola, fatto)]
    in_servizio = registro.vigenti_per_giorno(rapporto, servizio, anno, istante)
    giorni = [g for g, fatto in zip(anno.giorni(), in_servizio) if fatto is not None]
    if not giorni:
        return []
    ultimo = Periodo(giorni[-1], giorni[-1])
    condizione = lettore.fatto(regola.fatto_condizione, ultimo)
    if condizione is None or not lettore.soddisfa(regola, condizione):
        return []
    return giorni


def _part_time_dell_anno(
    lettore: _Lettore, regola: Regola, giorni: list[date], anno: Periodo
) -> tuple[Decimal, str, tuple[Fatto, ...]] | None:
    """Percentuale media del part-time sui giorni di maturazione, trattamento dichiarato e fatti letti; None senza part-time.

    Ogni giorno conta per la sua percentuale, 100 a tempo pieno: i periodi si pesano in 365esimi (nota di prassi 12).
    """
    vigenti = lettore.registro.vigenti_per_giorno(lettore.rapporto, FATTO_PART_TIME, anno, lettore.noto_al)
    per_giorno = dict(zip(anno.giorni(), vigenti))
    fatti = {per_giorno[g].id: per_giorno[g] for g in giorni if per_giorno[g] is not None}
    if not fatti:
        return None
    primo = min(fatti.values(), key=lambda fatto: fatto.valido_dal)
    dichiarazione = lettore.corpus.trattamento_part_time(regola.istituto, giorni[-1])
    if dichiarazione is None:
        raise CasoNonModellato(
            f"Rapporto {lettore.rapporto}: caso non modellato, l'istituto {regola.istituto} non dichiara il "
            f"trattamento nel part-time (fatto {FATTO_PART_TIME} dal {primo.valido_dal})"
        )
    if dichiarazione.trattamento == "da_integrativo":
        raise CasoNonModellato(
            f"Rapporto {lettore.rapporto}: caso non modellato, il trattamento nel part-time di {regola.istituto} "
            "è da integrativo e una regola annuale non lo applica"
        )
    letti = tuple(fatti[numero] for numero in sorted(fatti))
    if dichiarazione.trattamento == "intero":
        return Decimal(100), dichiarazione.trattamento, letti
    somma = sum((per_giorno[g].valore if per_giorno[g] is not None else Decimal(100) for g in giorni), Decimal(0))
    return somma / len(giorni), dichiarazione.trattamento, letti


def calcola_annuale(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    anno: int,
    noto_al: datetime | None = None,
    fino_al: date | None = None,
) -> tuple[Importo, ...]:
    """Regole annuali: base dell'ultimo giorno di servizio, quota sui giorni di servizio dell'anno.

    Senza `fino_al` è l'importo atteso a fine anno con i fatti noti: un servizio senza fine vale fino al 31 dicembre.
    Con `fino_al` è il maturato a quella data: contano solo i giorni dal 1° gennaio a quel giorno compreso.
    Una regola annuale che legge importi (annuali) ne deriva, senza una quota propria (ADR 0038).
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    lettore = _Lettore(registro, corpus, rapporto, istante)
    intero_anno = Periodo(date(anno, 1, 1), date(anno, 12, 31))
    considerato = intero_anno
    if fino_al is not None:
        if fino_al < intero_anno.dal:
            return ()
        considerato = Periodo(intero_anno.dal, min(fino_al, intero_anno.al))
    calcolati: dict[str, Importo] = {}
    derivate: list[tuple[Regola, list[date]]] = []
    annuali = corpus.regole_annuali()
    if annuali:
        lettore.controlla_fermi(considerato, {"calcolo"})
    for regola_tipo in annuali:
        giorni = _giorni_dell_annuale(lettore, regola_tipo, considerato)
        if not giorni:
            continue
        ultimo = Periodo(giorni[-1], giorni[-1])
        regola = corpus.regola_per(regola_tipo.istituto, ultimo)
        if regola is None or regola.maturazione != "annuale":
            continue
        if riferimenti(regola.formula).importi:
            derivate.append((regola, giorni))
            continue
        base = lettore.importo(regola, ultimo, lambda _: [])
        letto = lettore.parametro(regola.divisore, ultimo)
        part_time = _part_time_dell_anno(lettore, regola, giorni, considerato)
        with localcontext() as contesto:
            contesto.prec = PRECISIONE
            continuo = len(giorni) == intero_anno.giorni_calendario
            quota = Decimal(1) if continuo else min(Decimal(len(giorni)) / letto.valore, Decimal(1))
            pieno = _arrotonda(base.valore * quota, regola.decimali)
            valore = pieno
            if part_time is not None and part_time[1] != "intero":
                valore = _arrotonda(base.valore * quota * part_time[0] / 100, regola.decimali)
        parametri = tuple(sorted((*base.derivazione.parametri, letto), key=lambda p: p.nome))
        fatti = {fatto.id: fatto for fatto in base.derivazione.fatti}
        riduzione = None
        if part_time is not None:
            fatti.update({fatto.id: fatto for fatto in part_time[2]})
            riduzione = RiduzionePartTime(part_time[0].quantize(Decimal("0.000001")), pieno, part_time[1])
        calcolati[regola.istituto] = replace(
            base,
            periodo=Periodo(giorni[0], giorni[-1]),
            valore=valore,
            derivazione=replace(
                base.derivazione,
                parametri=parametri,
                fatti=tuple(fatti[numero] for numero in sorted(fatti)),
                quota=Quota(regola.conteggio, len(giorni), letto.valore, quota, base.valore),
                part_time=riduzione,
            ),
        )
    for regola, giorni in derivate:
        ultimo = Periodo(giorni[-1], giorni[-1])
        importo = lettore.importo(regola, ultimo, lambda nome: [calcolati[nome]] if nome in calcolati else [])
        if importo is None or not importo.derivazione.importi:
            continue
        calcolati[regola.istituto] = replace(importo, periodo=Periodo(giorni[0], giorni[-1]))
    return tuple(sorted(calcolati.values(), key=lambda i: i.istituto))


@dataclass(frozen=True)
class Differenza:
    rapporto: str
    istituto: str
    competenza: Mese | int
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


def _riga_nel_confronto(riga: Importo, rapporto: str, competenza: Mese | int, corpus: Corpus) -> bool:
    """Le righe che derivano dal pagato (ritenute, contributi di cassa) non sono dovuto per competenza."""
    if riga.rapporto != rapporto or riga.derivazione.maturazione in MATURAZIONI_FISCALI:
        return False
    if riga.istituto in corpus.istituti_di_cassa:
        return False
    if isinstance(competenza, int):
        return riga.derivazione.maturazione == "annuale" and riga.periodo.dal.year == competenza
    return riga.derivazione.maturazione != "annuale" and competenza.periodo.contiene(riga.periodo)


def _esiti_di_confronto(
    registro: Registro, corpus: Corpus, rapporto: str, competenza: Mese | int, tipo: TipoEsito, istante: datetime
) -> list[Esito]:
    """Pagato e versato si sommano; una dichiarazione sostituisce per intero il periodo."""
    interessati = [
        esito
        for esito in registro.esiti(tipo, istante)
        if any(_riga_nel_confronto(riga, rapporto, competenza, corpus) for riga in esito.righe)
    ]
    if tipo is TipoEsito.DICHIARATO:
        return interessati[-1:]
    return interessati


def _somma_righe(righe: list[Importo]) -> Importo:
    """Un solo importo per istituto: con più frazioni, conserva le frazioni nella derivazione."""
    if len(righe) == 1:
        return righe[0]
    ultima = righe[-1]
    return replace(
        ultima,
        periodo=Periodo(righe[0].periodo.dal, ultima.periodo.al),
        valore=sum((riga.valore for riga in righe), Decimal(0)),
        derivazione=replace(
            ultima.derivazione,
            formula="somma delle frazioni",
            quota=None,
            parametri=(),
            fatti=(),
            importi=tuple(righe),
        ),
    )


def differenze(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    competenza: Mese | int,
    tipo: TipoEsito,
    noto_al: datetime | None = None,
    pagamento: date | None = None,
) -> tuple[Differenza, ...]:
    """Dovuto ricalcolato meno quanto risulta dagli esiti, mai da un ricalcolo del passato.

    `competenza` è un mese oppure, per gli importi annuali, un anno. Il confronto è per
    istituto: se i fatti cambiano le frazioni, le frazioni nuove non combaciano con le vecchie.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    if isinstance(competenza, int):
        calcolati = calcola_annuale(registro, corpus, rapporto, competenza, istante)
    else:
        calcolati = calcola(registro, corpus, rapporto, competenza, istante, pagamento)
    dovuti: dict[str, list[Importo]] = {}
    for importo in calcolati:
        dovuti.setdefault(importo.istituto, []).append(importo)

    esitati: dict[str, Decimal] = {}
    fonti: dict[str, list[int]] = {}
    ultima_riga: dict[str, Importo] = {}
    for esito in _esiti_di_confronto(registro, corpus, rapporto, competenza, tipo, istante):
        for riga in esito.righe:
            if _riga_nel_confronto(riga, rapporto, competenza, corpus):
                esitati[riga.istituto] = esitati.get(riga.istituto, Decimal(0)) + riga.valore
                fonti.setdefault(riga.istituto, [])
                if esito.id not in fonti[riga.istituto]:
                    fonti[riga.istituto].append(esito.id)
                ultima_riga[riga.istituto] = riga

    risultato = []
    for istituto in sorted(dovuti.keys() | esitati.keys()):
        righe = dovuti.get(istituto, [])
        dovuto = sum((riga.valore for riga in righe), Decimal(0))
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
                    _base=_somma_righe(righe) if righe else ultima_riga[istituto],
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
        f"{margine}{importo.istituto} [{importo.periodo}] rapporto {importo.rapporto}: {importo.valore}",
        f"{margine}  regola v{d.regola_versione} ({d.maturazione}): {d.formula}",
        f"{margine}  riferimento: {d.riferimento}",
    ]
    if solo_prassi(d.riferimento):
        righe.append(f"{margine}  ATTENZIONE: fondata solo su prassi")
    if importo.data_pagamento is not None:
        righe.append(f"{margine}  pagato il {importo.data_pagamento}")
    for concorso in d.concorsi:
        righe.append(
            f"{margine}  concorso {concorso.istituto} -> {concorso.base}: {concorso.misura} "
            f"(dal {concorso.dal}; fonte: {concorso.riferimento})"
        )
    if d.quota is not None:
        quota = d.quota
        calcolo = f"mese intero, residuo {quota.quota:.6f}" if quota.divisore is None else f"{quota.giorni}/{quota.divisore}"
        righe.append(f"{margine}  quota ({quota.conteggio}): {calcolo} su base {quota.base}")
    if importo.esiti_confrontati:
        elenco = ", ".join(f"#{numero}" for numero in importo.esiti_confrontati)
        righe.append(f"{margine}  differenza rispetto agli esiti: {elenco}")
    for parametro in d.parametri:
        avviso = " [solo prassi]" if solo_prassi(parametro.riferimento) else ""
        righe.append(
            f"{margine}  parametro {parametro.nome} = {parametro.valore} "
            f"(dal {parametro.dal}; fonte: {parametro.riferimento}){avviso}"
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
