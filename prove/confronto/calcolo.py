"""Il mese dell'ente fatto girare sul nucleo: dai dati del gestionale ai fatti del registro, poi calcolo e versione di proposta.

Qui non c'e' nessuna regola di calcolo. I fatti vengono dall'anagrafica e dalla testata del cedolino; gli importi li produce
il nucleo. Il primo giro si ferma alla versione di proposta (lordo, contributi, ritenuta, netto): denuncia e delega dopo.
"""

from __future__ import annotations

import re

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

from paghe import Atto, Corpus, Mese, Registro, calcola, emetti_esito, emetti_versione
from paghe.modello import Derivazione, Importo, TipoEsito
from paghe.tempo import Periodo
from paghe.errori import ErrorePaghe
from paghe.impegni import registra_impegno

from . import aggiunta as A
from .lettura import Anagrafica, Cedolino

RADICE = Path(__file__).resolve().parents[2]
CORPUS_REALE = RADICE / "corpus" / "funzioni-locali-cpdel.toml"
CORPUS_FITTIZIO = RADICE / "prove" / "mese_di_prova" / "corpus_fittizio.toml"

IBAN_DI_PROVA = "IT76X0100003245TEST00000002"  # l'IBAN vero non serve al confronto e non si legge
QUALIFICHE = {"funzionari": "0FZEQF", "istruttori": "0IR000", "operatori_esperti": "0OEESP", "operatori": "0OP000"}
PIANI_DI_SPESA = (
    "U.1.01.01.01.002", "U.1.01.01.01.004", "U.1.01.02.01.001", "U.1.01.02.01.003", "U.1.02.01.01.001",
    "U.1.03.02.01.001", "U.1.03.02.12.003",
)
PROGRAMMA = "01.02"  # di comodo: nel primo giro la proposta contabile non si confronta
# Tabella ritenute del gestionale -> regime di fine servizio INPS (1 TFR, 3 TFS)
REGIMI = {"1": "3", "9": "1", "2": "1"}
ATTO = Atto("ente:ente_reale:estrazione.gestionale:2026-11-10;1", date(2026, 11, 10))


@dataclass
class Calcolato:
    matricola: int
    rapporto: str
    righe: list = field(default_factory=list)  # RigaComposizione
    netto: Decimal | None = None
    fermo: str = ""
    avvisi: list[str] = field(default_factory=list)

    def somma(self, natura: str | None = None, istituti=None) -> Decimal:
        return sum(
            (r.importo.valore for r in self.righe if (natura is None or r.natura == natura) and (istituti is None or r.istituto in istituti)),
            Decimal(0),
        )

    def imponibile_fiscale(self) -> Decimal | None:
        """L'imponibile su cui il nucleo ha calcolato la ritenuta: redditi letti meno deduzioni lette, dalla sua derivazione."""
        ritenuta = next((r.importo for r in self.righe if r.istituto == "ritenuta_irpef"), None)
        if ritenuta is None:
            return None
        letti = [i for i in ritenuta.derivazione.importi if i.istituto != "ritenuta_irpef"]
        redditi = sum((i.valore for i in letti if i.categoria_reddito is not None), Decimal(0))
        return redditi - sum((i.valore for i in letti if i.categoria_reddito is None), Decimal(0))

    def reddito_annuo(self) -> Decimal | None:
        """Il reddito annuo proiettato su cui il nucleo ha calcolato le detrazioni (ADR 0039), dalla formula della ritenuta."""
        ritenuta = next((r.importo for r in self.righe if r.istituto == "ritenuta_irpef"), None)
        trovato = re.search(r"reddito annuo = [^;]*= (-?[\d.]+);", ritenuta.derivazione.formula) if ritenuta else None
        return Decimal(trovato.group(1)) if trovato else None

    def valore(self, istituto: str) -> Decimal | None:
        trovate = [r.importo.valore for r in self.righe if r.istituto == istituto]
        return sum(trovate, Decimal(0)) if trovate else None


@dataclass
class Giro:
    calcolati: dict[int, Calcolato]
    tabellari: dict[str, tuple[Decimal, Decimal]]  # area -> (annuo del corpus, annuo usato)
    esclusi: dict[int, str]  # matricola -> perche' non e' nel primo giro
    fermi_versione: list[str]


def tabellari_dal_gestionale(cedolini: list[Cedolino], anagrafiche: dict[int, Anagrafica]) -> dict[str, Decimal]:
    """Il tabellare annuo di ogni area, dallo «stipendio base» dei cedolini: deve essere uno solo per area."""
    mensili: dict[str, set[Decimal]] = {}
    for c in cedolini:
        area = A.AREE.get(c.area)
        if area and A.VOCE_TABELLARE in c.fisse:
            mensili.setdefault(area, set()).add(c.fisse[A.VOCE_TABELLARE])
    annui = {}
    for area, valori in mensili.items():
        if len(valori) != 1:
            raise ValueError(f"area {area}: piu' di uno stipendio base nei cedolini ({sorted(valori)})")
        annui[area] = valori.pop() * 12
    return annui


def motivo_di_esclusione(c: Cedolino, a: Anagrafica, mese: Mese) -> str:
    """I casi che il primo giro non porta al calcolo, nominati."""
    if c.area not in A.AREE:
        return f"inquadramento «{c.area}» fuori dal comparto (segretario): non nel primo giro"
    if a.cessazione is not None and mese.primo_giorno <= a.cessazione <= mese.ultimo_giorno:
        return "cessazione nel mese con tredicesima e conguaglio fiscale di fine rapporto: non nel primo giro"
    if a["tipo p.t."]:
        return f"part-time ({a['tipo p.t.']}, {a['% p.t.']}%): serve la programmazione dell'orario, non nel primo giro"
    riga = c.riga("304")
    if riga is None or riga.giorni != Decimal("26.00"):
        return "retribuzione non di un mese intero (giorni diversi da 26): non nel primo giro"
    return ""


def _registra(reg: Registro, c: Cedolino, a: Anagrafica, mese: Mese, con_pregressi: bool) -> str:
    rapporto, persona = f"M{c.matricola}", f"P{c.matricola}"
    area = A.AREE[c.area]
    inizio_anno = date(mese.anno, 1, 1)
    # Con i pagati dei mesi prima (estrazione voci) il rapporto parte da inizio anno, o dall'assunzione se dopo: il nucleo
    # proietta il reddito annuo (ADR 0039) e stima quello teorico dal pagato diviso i giorni di servizio. Senza (mese
    # isolato) parte dal primo giorno del mese: la stima diventa il mese rapportato all'anno.
    dal = max(inizio_anno, a.assunzione or inizio_anno) if con_pregressi else mese.primo_giorno
    cognome, _, nome = c.nominativo.partition(" ")
    reg.registra_codice_persona(persona, "codice_fiscale", c.codice_fiscale, a.nascita or inizio_anno)
    reg.registra_codice_persona(persona, "cognome", cognome, a.nascita or inizio_anno)
    reg.registra_codice_persona(persona, "nome", nome or cognome, a.nascita or inizio_anno)
    reg.registra_iban_persona(persona, IBAN_DI_PROVA, dal)
    if a["detr.lav.dip."] != "Nessuna":
        reg.registra_dichiarazione_sostituito(persona, "lavoro_dipendente", dal, None, ATTO)
    reg.collega_rapporto(rapporto, persona, dal)
    reg.registra_programma_rapporto(rapporto, PROGRAMMA, dal)
    codici = {
        "tipo_impiego": "1",
        "tipo_servizio": "4",
        "contratto": "RALN",
        "qualifica": QUALIFICHE[area],
        "area": area,
        "regime_fine_servizio": REGIMI[a["tab.ritenute"]],
    }
    for tipo, valore in codici.items():
        reg.registra_codice(rapporto, tipo, valore, dal, None, None)
    for voce, importo in c.fisse.items():
        if voce in A.PER_VOCE:
            reg.registra_fatto(rapporto, A.PER_VOCE[voce].istituto, str(importo), dal, None, ATTO)
    return rapporto


ISTITUTO_PREGRESSO = A.PREGRESSO


def _paga_pregressi(reg: Registro, corpus: Corpus, rapporto: str, mesi: dict[int, Decimal], mese: Mese) -> None:
    """Un esito pagato per ogni mese prima di quello del confronto, con l'imponibile IRPEF del gestionale come reddito di
    lavoro dipendente dell'anno: e' il «pagato prima del mese» della proiezione. Ritenute e contributi non servono."""
    for numero, imponibile in sorted(mesi.items()):
        if numero >= mese.mese or not imponibile:
            continue
        periodo = Periodo(Mese(mese.anno, numero).primo_giorno, Mese(mese.anno, numero).ultimo_giorno)
        giorno = date(mese.anno, numero, 27)
        derivazione = Derivazione(
            ISTITUTO_PREGRESSO, "evento", 1, "fittizio:da-gestionale-estrazione-voci-9001",
            "imponibile IRPEF del mese letto dal gestionale", corpus.versione, datetime(mese.anno, mese.mese, 1, tzinfo=UTC), (), (), (),
        )
        riga = Importo(rapporto, ISTITUTO_PREGRESSO, periodo, imponibile, derivazione, data_pagamento=giorno,
                       anno_imposta=mese.anno, categoria_reddito="lavoro_dipendente")
        esito = emetti_esito(reg, TipoEsito.PAGATO, giorno, [riga])
        reg.registra_pagamento(rapporto, esito.id, giorno)


def gira(
    cedolini: list[Cedolino], anagrafiche: dict[int, Anagrafica], mese: Mese, valuta: date, tabellare: str,
    pregressi: dict[int, dict[int, Decimal]] | None = None,
) -> Giro:
    reale = A.estendi_riduzione_tfr(CORPUS_REALE.read_text(encoding="utf-8"))
    cambi: dict[str, tuple[Decimal, Decimal]] = {}
    if tabellare == "gestionale":
        reale, cambi = A.sostituisci_tabellari(reale, tabellari_dal_gestionale(cedolini, anagrafiche))
    # Il corpus fittizio del mese di prova porta le dichiarazioni di composizione degli istituti reali: senza, nessuna versione.
    corpus = Corpus.da_toml(reale + "\n" + CORPUS_FITTIZIO.read_text(encoding="utf-8") + "\n" + A.testo_aggiunta(), reale=False)

    ora = [datetime(mese.anno, mese.mese, 2, 9, 0, tzinfo=UTC)]
    reg = Registro(orologio=lambda: ora[0])
    numero = 0
    for piano in PIANI_DI_SPESA:
        numero += 1
        missione, _, programma = PROGRAMMA.partition(".")
        registra_impegno(reg, f"impegno-{numero}", "confronto", numero, mese.anno, piano, missione, programma, "10000000.00", date(mese.anno, 1, 1))
    for tipo, valore in (("codice_fiscale", "01234567897"), ("denominazione", "ENTE"), ("regione", "sicilia")):
        reg.registra_codice_ente(tipo, valore, date(mese.anno, 1, 1))

    calcolati: dict[int, Calcolato] = {}
    esclusi: dict[int, str] = {}
    importi = []
    for c in cedolini:
        a = anagrafiche[c.matricola]
        motivo = motivo_di_esclusione(c, a, mese)
        if motivo:
            esclusi[c.matricola] = motivo
            continue
        risultato = Calcolato(c.matricola, f"M{c.matricola}")
        calcolati[c.matricola] = risultato
        try:
            _registra(reg, c, a, mese, pregressi is not None)
            if pregressi is not None:
                _paga_pregressi(reg, corpus, risultato.rapporto, pregressi.get(c.matricola, {}), mese)
        except ErrorePaghe as errore:
            risultato.fermo = f"fatti: {errore}"
    ora[0] = datetime(valuta.year, valuta.month, max(valuta.day - 7, 1), 9, 0, tzinfo=UTC)
    for risultato in calcolati.values():
        if risultato.fermo:
            continue
        try:
            importi.extend(calcola(reg, corpus, risultato.rapporto, mese))
        except ErrorePaghe as errore:
            risultato.fermo = f"calcolo: {errore}"

    fermi_versione: list[str] = []
    try:
        versione = emetti_versione(reg, corpus, valuta, importi)
    except ErrorePaghe as errore:
        fermi_versione.append(str(errore))
        versione = None
    if versione is not None:
        per_rapporto = {r.rapporto: r for r in calcolati.values()}
        for riga in versione.righe:
            per_rapporto[riga.rapporto].righe.append(riga)
        for netto in versione.netti:
            per_rapporto[netto.rapporto].netto = netto.netto
        for fermo in versione.fermi:
            per_rapporto[fermo.rapporto].fermo = f"versione: {fermo.motivo}"
        for dato in versione.dati_mancanti:
            fermi_versione.append(f"dato mancante {dato.tipo} ({dato.soggetto}): {dato.motivo}")
        for avviso in versione.avvisi:
            fermi_versione.append(f"avviso {avviso.tipo}: {avviso.persona}")
    reg.chiudi()
    return Giro(calcolati, cambi, esclusi, fermi_versione)
