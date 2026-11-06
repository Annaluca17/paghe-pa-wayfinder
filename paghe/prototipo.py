"""PROTOTIPO DA BUTTARE (ticket #37): dal fatto alla ListaPosPA, su una pagina HTML statica.

    python -m paghe.prototipo <cartella>

Scrive `<cartella>/index.html`. Domanda a cui risponde: chi non è sviluppatore riesce a seguire,
su una pagina, da dove viene ogni numero della denuncia e dove il modello si ferma? Non è
l'interfaccia del modello (la mappa #1 la esclude): legge solo le funzioni pubbliche del nucleo.

Persone e codici fiscali sono di fantasia; il corpus è quello reale (`corpus/`).
"""

from __future__ import annotations

import html
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from . import Corpus, Mese, Registro, TipoEsito, calcola, calcola_denuncia, differenze, emetti_esito, lista_pos_pa
from .errori import ErrorePaghe, VistaFerma
from .modello import Fatto, Importo
from .registro import TIPO_DATA_PAGAMENTO
from .riferimento import solo_prassi
from .uniemens import Ente, Mittente, in_xml

RADICE = Path(__file__).resolve().parent.parent
CORPUS = RADICE / "corpus" / "funzioni-locali-cpdel.toml"
REPO = "https://github.com/Annaluca17/paghe-pa-wayfinder/blob/main"

# Ente e mittente di fantasia, gli stessi dei test della vista.
ENTE = Ente(
    cf_azienda="01234567897",
    ragione_sociale="ENTE DI PROVA",
    prg_azienda="00000",
    cf_rappresentante_firmatario="BNCGNN70C03L219U",
)
MITTENTE = Mittente(
    cf_persona="VRDLGU75B12F205B",
    ragione_sociale="UFFICIO PERSONALE DI PROVA",
    cf_mittente="01234567897",
    cf_softwarehouse="98765432103",
    tipo="1",
)
QUALIFICA = {"funzionari": "0FZEQF", "istruttori": "0IR000", "operatori_esperti": "0OEESP", "operatori": "0OP000"}

# --- La storia di un rapporto: registro in memoria e diario di ciò che è successo -------------


@dataclass
class Evento:
    istante: datetime
    azione: str  # "registra", "annulla", "paga"
    fatto: Fatto | None = None
    nota: str = ""


class Storia:
    def __init__(self, rapporto: str):
        self.rapporto = rapporto
        self.ora = datetime(2026, 1, 2, 9, 0, tzinfo=UTC)
        self.registro = Registro(orologio=lambda: self.ora)
        self.diario: list[Evento] = []

    def il(self, giorno: date) -> None:
        nuova = datetime(giorno.year, giorno.month, giorno.day, 9, 0, tzinfo=UTC)
        self.ora = max(nuova, self.ora)

    def _passa(self) -> None:
        self.ora += timedelta(seconds=1)

    def registra(self, tipo: str, valore: str, dal: date, al: date | None = None) -> Fatto:
        fatto = self.registro.registra_codice(self.rapporto, tipo, valore, dal, al)
        self.diario.append(Evento(self.ora, "registra", fatto))
        self._passa()
        return fatto

    def annulla(self, fatto: Fatto, motivo: str) -> None:
        self.registro.annulla_fatto(fatto.id, motivo)
        self.diario.append(Evento(self.ora, "annulla", fatto, motivo))
        self._passa()

    def paga(self, righe: list[Importo], giorno: date, nota: str = "") -> None:
        self.il(giorno)
        esito = emetti_esito(self.registro, TipoEsito.PAGATO, giorno, righe)
        fatto = self.registro.registra_pagamento(self.rapporto, esito.id, giorno)
        self.diario.append(Evento(self.ora, "paga", fatto, nota))
        self._passa()


def assumi(storia: Storia, cf: str, cognome: str, nome: str, area: str, dal: date, regime: str) -> dict[str, Fatto]:
    fatti = {
        "codice_fiscale": (cf, None),
        "cognome": (cognome, None),
        "nome": (nome, None),
        "comune_sede_lavoro": ("H501", None),
        "cap_sede_lavoro": ("00100", None),
        "tipo_impiego": ("1", None),
        "tipo_servizio": ("4", None),
        "contratto": ("RALN", None),
        "qualifica": (QUALIFICA[area], None),
        "area": (area, None),
        "regime_fine_servizio": (regime, None),
    }
    return {tipo: storia.registra(tipo, valore, dal, al) for tipo, (valore, al) in fatti.items()}


def stipendi(storia: Storia, corpus: Corpus, *mesi: Mese) -> list[Importo]:
    return [riga for mese in mesi for riga in calcola(storia.registro, corpus, storia.rapporto, mese)]


# --- I casi ------------------------------------------------------------------------------------


@dataclass
class Caso:
    id: str
    titolo: str
    racconto: str
    storia: Storia
    competenze: list[Mese]
    denunce: list[Mese]
    da_guardare: str = ""
    note: list[str] = field(default_factory=list)


def mese_intero(corpus: Corpus) -> Caso:
    s = Storia("RAPPORTO-1")
    assumi(s, "RSSMRA80A01H501U", "ROSSI", "MARIO", "istruttori", date(2026, 1, 1), regime="3")
    s.paga(stipendi(s, corpus, Mese(2026, 11)), date(2026, 11, 27), "stipendio di novembre")
    return Caso(
        id="mese-intero",
        titolo="Un mese intero",
        racconto=(
            "Mario Rossi è istruttore a tempo pieno dal 1° gennaio 2026, in regime TFS. "
            "Lo stipendio di novembre è pagato il 27 novembre."
        ),
        storia=s,
        competenze=[Mese(2026, 11)],
        denunce=[Mese(2026, 11)],
        da_guardare=(
            "Il caso semplice: un solo quadro E0. La base CPDEL somma tabellare e indennità di comparto, "
            "la base TFS solo il tabellare, all'80%."
        ),
    )


def assunzione(corpus: Corpus) -> Caso:
    s = Storia("RAPPORTO-2")
    s.il(date(2026, 8, 20))
    assumi(s, "BNCNNA85M41F205Q", "BIANCHI", "ANNA", "funzionari", date(2026, 8, 24), regime="1")
    s.paga(stipendi(s, corpus, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25), "agosto e settembre insieme")
    return Caso(
        id="assunzione",
        titolo="Assunzione a metà mese, pagata il mese dopo",
        racconto=(
            "Anna Bianchi entra in servizio lunedì 24 agosto 2026 come funzionaria, in regime TFR. "
            "Agosto non si paga ad agosto: i giorni di agosto e il mese di settembre escono insieme il 25 settembre."
        ),
        storia=s,
        competenze=[Mese(2026, 8), Mese(2026, 9)],
        denunce=[Mese(2026, 8), Mese(2026, 9)],
        da_guardare=(
            "Agosto vale 7 giorni su 26 per competenza, ma entra nella denuncia di settembre, quando è pagato. "
            "Ad agosto non c'è nessun quadro; a settembre l'E0 porta tutto e un V1 causale 5 dichiara solo il servizio "
            "di agosto. In regime TFR il lordo è ridotto, ma le basi restano sul lordo intero."
        ),
    )


def arretrato(corpus: Corpus) -> Caso:
    s = Storia("RAPPORTO-3")
    s.il(date(2026, 11, 10))
    assumi(s, "VRDLCU90C15L219S", "VERDI", "LUCA", "operatori_esperti", date(2026, 9, 1), regime="3")
    s.paga(stipendi(s, corpus, Mese(2026, 9), Mese(2026, 10), Mese(2026, 11)), date(2026, 11, 27), "settembre, ottobre e novembre")
    s.paga(stipendi(s, corpus, Mese(2026, 12)), date(2026, 12, 18), "dicembre")
    return Caso(
        id="arretrato",
        titolo="Arretrato che supera la prima fascia",
        racconto=(
            "Luca Verdi, operatore esperto, è in servizio dal 1° settembre 2026, ma la presa di servizio arriva "
            "all'ufficio personale solo il 10 novembre. I fatti si registrano quel giorno con validità dal 1° settembre, "
            "e il 27 novembre si pagano insieme settembre, ottobre e novembre."
        ),
        storia=s,
        competenze=[Mese(2026, 9), Mese(2026, 10), Mese(2026, 11)],
        denunce=[Mese(2026, 11), Mese(2026, 12)],
        da_guardare=(
            "Tre mesi pagati in un mese portano la base CPDEL di novembre oltre la prima fascia mensile (4.685 euro): "
            "scatta il contributo aggiuntivo dell'1% sulla parte eccedente. Settembre e ottobre si dichiarano come V1 "
            "causale 5. A dicembre servirebbe il conguaglio annuo dell'1%, che il modello non calcola: la denuncia si "
            "ferma e lo dice."
        ),
    )


def recupero(corpus: Corpus) -> Caso:
    s = Storia("RAPPORTO-4")
    fatti = assumi(s, "NREGLI78E52H501Y", "NERI", "GIULIA", "istruttori", date(2026, 1, 1), regime="3")
    s.paga(stipendi(s, corpus, Mese(2026, 10)), date(2026, 10, 27), "ottobre intero")
    s.il(date(2026, 11, 3))
    for tipo in ("tipo_impiego", "tipo_servizio", "contratto", "qualifica", "area", "regime_fine_servizio"):
        s.annulla(fatti[tipo], "cessazione al 15/10 comunicata in ritardo")
        s.registra(tipo, str(fatti[tipo].valore), date(2026, 1, 1), date(2026, 10, 15))
    s.registra("codice_cessazione", "1", date(2026, 10, 15), date(2026, 10, 15))
    rapporto, reg = s.rapporto, s.registro
    s.paga([v.importo() for v in differenze(reg, corpus, rapporto, Mese(2026, 10), TipoEsito.PAGATO)], date(2026, 11, 20), "recupero della seconda metà di ottobre")
    return Caso(
        id="recupero",
        titolo="Recupero su cessato: il quadro che si ferma",
        racconto=(
            "Giulia Neri, istruttrice, è cessata il 15 ottobre 2026, ma la cessazione arriva all'ufficio il 3 novembre, "
            "quando ottobre è già stato pagato per intero. I fatti di servizio si annullano e si registrano di nuovo con "
            "la fine al 15 ottobre; il 20 novembre si recupera la differenza."
        ),
        storia=s,
        competenze=[Mese(2026, 10)],
        denunce=[Mese(2026, 11)],
        da_guardare=(
            "Ottobre, per competenza, oggi vale mezzo mese: la differenza rispetto al pagato è negativa ed entra nella "
            "denuncia di novembre come recupero su cessato, in un periodo fuori servizio. Il calcolo c'è; il quadro che "
            "lo dichiara (V1 causale 7, codice motivo 7) non è ancora modellato: la ListaPosPA lo nomina, conserva gli "
            "importi e non produce l'XML."
        ),
    )


CASI = [mese_intero, assunzione, arretrato, recupero]

# --- Etichette in lingua del dominio -----------------------------------------------------------

_FATTI = {
    "codice_fiscale": "Codice fiscale",
    "cognome": "Cognome",
    "nome": "Nome",
    "comune_sede_lavoro": "Comune della sede di lavoro",
    "cap_sede_lavoro": "CAP della sede di lavoro",
    "tipo_impiego": "Tipo impiego (servizio)",
    "tipo_servizio": "Tipo servizio",
    "contratto": "Contratto",
    "qualifica": "Qualifica",
    "area": "Area",
    "regime_fine_servizio": "Regime di fine servizio",
    "codice_cessazione": "Codice di cessazione",
    TIPO_DATA_PAGAMENTO: "Data di pagamento",
}
_REGIMI = {"1": "TFR", "2": "optante", "3": "TFS"}
_AREE = {
    "funzionari": "Funzionari ed EQ",
    "istruttori": "Istruttori",
    "operatori_esperti": "Operatori esperti",
    "operatori": "Operatori",
}
_ISTITUTI = {
    "cpdel_totale": "CPDEL, contributo totale",
    "cpdel_lavoratore": "CPDEL, quota del lavoratore",
    "cpdel_ente": "CPDEL, quota dell'ente",
    "fondo_credito": "Fondo Credito",
    "contributo_aggiuntivo": "Contributo aggiuntivo 1%",
    "imponibile_tfs": "Imponibile TFS (80%)",
    "tfs_totale": "TFS, contributo totale",
    "tfs_lavoratore": "TFS, quota del lavoratore",
    "tfs_ente": "TFS, quota dell'ente",
    "riduzione_tfr": "Riduzione del lordo TFR",
    "imponibile_tfr": "Imponibile TFR (80%)",
    "contributo_tfr": "Contributo TFR",
    "contributo_tfr_ulteriori": "Contributo TFR, ulteriori elementi",
    "retribuzione_valutabile_tfr": "Retribuzione valutabile TFR",
    "base.cpdel": "Base CPDEL",
    "base.fondo_credito": "Base Fondo Credito",
    "base.tfs": "Base TFS (voci utili, al 100%)",
    "base.tfr_ulteriori": "Base ulteriori elementi TFR",
}
_MATURAZIONI = {
    "giorni": "a giorni",
    "periodo": "sul periodo dichiarato",
    "mese": "sul totale del mese",
    "cassa": "per cassa",
    "evento": "a evento",
    "annuale": "annuale",
}
_CAUSALI = {"5": "solo giuridico", "1": "arretrato a cessato o sospeso"}
_MESI = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()


def _e(testo) -> str:
    return html.escape(str(testo), quote=True)


def euro(valore: Decimal | None) -> str:
    if valore is None:
        return "—"
    testo = f"{valore:,.2f}"
    return testo.replace(",", "§").replace(".", ",").replace("§", ".")


def numero(valore: Decimal) -> str:
    """Parametro con tutte le sue cifre, in forma italiana: 4.685,00 o 0,0880."""
    testo = f"{valore:,f}"
    return testo.replace(",", "§").replace(".", ",").replace("§", ".")


def _data(giorno: date | None) -> str:
    return giorno.strftime("%d/%m/%Y") if giorno else "—"


def _periodo(p) -> str:
    return f"{_data(p.dal)} – {_data(p.al)}"


def _mese(m: Mese) -> str:
    return f"{_MESI[m.mese - 1]} {m.anno}"


def istituto(nome: str) -> str:
    for prefisso, etichetta in (("tabellare_", "Stipendio tabellare"), ("comparto_", "Indennità di comparto")):
        if nome.startswith(prefisso):
            return f"{etichetta} ({_AREE.get(nome[len(prefisso):], nome[len(prefisso):]).lower()})"
    return _ISTITUTI.get(nome, nome)


def _valore_fatto(fatto: Fatto) -> str:
    if fatto.tipo == "regime_fine_servizio":
        return f"{fatto.valore} · {_REGIMI.get(str(fatto.valore), '?')}"
    if fatto.tipo == "area":
        return _AREE.get(str(fatto.valore), str(fatto.valore))
    if fatto.tipo == TIPO_DATA_PAGAMENTO:
        return f"esito #{int(fatto.valore)}"
    return str(fatto.valore)


# --- Fonti: norma, istruzione INPS, nota di prassi interna -------------------------------------

_SEGMENTI = {"art": "art. ", "com": "c. ", "let": "lett. ", "num": "n. ", "par": "§ ", "pag": "p. ", "all": "all. ", "tab": "tab. "}
_ATTI = {
    ("stato", "legge"): "L.",
    ("stato", "decreto.legge"): "D.L.",
    ("stato", "decreto.legislativo"): "D.Lgs.",
    ("stato", "decreto.del.presidente.della.repubblica"): "D.P.R.",
    ("presidente.consiglio.ministri", "decreto"): "DPCM",
}


def _partizione(testo: str) -> str:
    pezzi = []
    for segmento in testo.split("-"):
        trovato = re.match(r"(art|com|let|num|par|pag|all|tab)(.*)", segmento)
        pezzi.append(_SEGMENTI[trovato[1]] + trovato[2] if trovato else segmento)
    return " ".join(pezzi)


def _gg(testo: str) -> str:
    return date.fromisoformat(testo).strftime("%d/%m/%Y")


def _note_di_prassi() -> dict[str, str]:
    return {p.name.split("-")[3]: p.name for p in sorted((RADICE / "docs" / "prassi").glob("2026-11-06-*.md"))}


def fonte(citazione: str) -> tuple[str, str]:
    """(genere, testo leggibile) di una citazione: genere 'norma', 'istruzione' o 'prassi'."""
    pulita = re.sub(r"(!vig=[\d-]+|@originale)$", "", citazione)
    testa, _, parte = pulita.partition("~")
    parte = f", {_partizione(parte)}" if parte else ""
    pezzi = testa.split(":")
    try:
        if pezzi[0] == "urn":
            data, _, numero = pezzi[4].partition(";")
            nome = _ATTI.get((pezzi[2], pezzi[3]), pezzi[3].replace(".", " "))
            return "norma", f"{nome} {_gg(data)}{' n. ' + numero if numero else ''}{parte}"
        if pezzi[0] == "ccnl":
            return "norma", f"CCNL Funzioni Locali {_gg(pezzi[2])}{parte}"
        if pezzi[0] == "prassi":
            data, _, numero = pezzi[3].partition(";")
            if pezzi[1] == "immedia":
                return "prassi", f"Nota di prassi {numero} del {_gg(data)}"
            tipo = pezzi[2].replace(".", " ").capitalize()
            return "istruzione", f"{tipo} {pezzi[1].upper()} {_gg(data)} n. {numero}{parte}"
    except (IndexError, ValueError):
        pass
    return "altro", citazione


def _fonti(riferimento: str) -> str:
    note = _note_di_prassi()
    pezzi = []
    for citazione in riferimento.split(" + "):
        genere, testo = fonte(citazione)
        etichetta = f'<span class="fonte {genere}" title="{_e(citazione)}">{_e(testo)}</span>'
        if genere == "prassi":
            numero = citazione.rsplit(";", 1)[-1]
            if numero in note:
                etichetta = f'<a href="{REPO}/docs/prassi/{note[numero]}">{etichetta}</a>'
        pezzi.append(etichetta)
    if solo_prassi(riferimento):
        pezzi.append('<span class="badge prassi-sola">SOLO PRASSI</span>')
    return " ".join(pezzi)


# --- Spiegazione di un importo ------------------------------------------------------------------


def spiegazione(importo: Importo) -> str:
    d = importo.derivazione
    righe = [
        f'<div class="riga"><b>Regola</b> v{d.regola_versione}, {_MATURAZIONI.get(d.maturazione, d.maturazione)}: '
        f"<code>{_e(d.formula)}</code></div>",
        f'<div class="riga"><b>Fonte</b> {_fonti(d.riferimento)}</div>',
    ]
    if importo.data_pagamento:
        righe.append(f'<div class="riga"><b>Pagato il</b> {_data(importo.data_pagamento)}</div>')
    for c in d.concorsi:
        righe.append(
            f'<div class="riga"><b>Concorre</b> a {_e(istituto("base." + c.base))}: {_e(c.misura)} '
            f"(dal {_data(c.dal)}) {_fonti(c.riferimento)}</div>"
        )
    if d.quota is not None:
        q = d.quota
        calcolo = "mese intero" if q.divisore is None else f"{q.giorni} giorni su {q.divisore}"
        righe.append(f'<div class="riga"><b>Quota del mese</b> {calcolo} di {euro(q.base)} ({_e(q.conteggio)})</div>')
    for p in d.parametri:
        righe.append(
            f'<div class="riga"><b>Parametro</b> <code>{_e(p.nome)}</code> = {numero(p.valore)} '
            f"(dal {_data(p.dal)}) {_fonti(p.riferimento)}</div>"
        )
    for f in d.fatti:
        righe.append(
            f'<div class="riga"><b>Fatto</b> #{f.id} {_e(_FATTI.get(f.tipo, f.tipo))} = {_e(_valore_fatto(f))} '
            f"(valido dal {_data(f.valido_dal)}, registrato il {f.registrato_il:%d/%m/%Y})</div>"
        )
    if d.importi:
        figli = "".join(_importo_espandibile(figlio) for figlio in d.importi)
        righe.append(f'<div class="riga"><b>Deriva da</b></div><div class="figli">{figli}</div>')
    return "".join(righe)


def _importo_espandibile(importo: Importo) -> str:
    return (
        f'<details class="importo"><summary><span>{_e(istituto(importo.istituto))}</span>'
        f'<span class="periodo">{_periodo(importo.periodo)}</span>'
        f'<span class="valore">{euro(importo.valore)}</span></summary>'
        f'<div class="spiega">{spiegazione(importo)}</div></details>'
    )


def _righe_importi(importi) -> str:
    return "".join(_importo_espandibile(i) for i in importi) or '<p class="vuoto">Nessun importo.</p>'


# --- Le sezioni di un caso ------------------------------------------------------------------------


def leggibile(testo: str) -> str:
    """Messaggi del nucleo con date, mesi e istituti come li legge l'ufficio personale."""
    testo = re.sub(r"(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})", lambda m: f"{_gg(m[1])} – {_gg(m[2])}", testo)
    testo = re.sub(r"\b(\d{4})-(\d{2})\b(?!-)", lambda m: _mese(Mese(int(m[1]), int(m[2]))), testo)
    return re.sub(r"\b[a-z]+(?:_[a-z]+)+\b", lambda m: istituto(m[0]) if istituto(m[0]) != m[0] else m[0], testo)


def _fermo(titolo: str, testo: str) -> str:
    return f'<div class="fermo"><div class="fermo-titolo">{_e(titolo)}</div><p>{_e(leggibile(testo))}</p></div>'


def _caso_non_modellato(errore: ErrorePaghe, cosa: str) -> str:
    testo = str(errore)
    if "caso non modellato, " in testo:
        testo = testo.split("caso non modellato, ", 1)[1]
    return _fermo(f"Caso non modellato: {cosa} si ferma", testo)


def _diario(storia: Storia) -> str:
    righe = []
    for ev in storia.diario:
        f = ev.fatto
        if ev.azione == "registra":
            cosa = "Registrato"
        elif ev.azione == "annulla":
            cosa = f"Annullato: {ev.nota}"
        else:
            cosa = f"Pagamento{': ' + ev.nota if ev.nota else ''}"
        validita = _data(f.valido_dal) + (f" – {_data(f.valido_al)}" if f.valido_al else " in poi")
        righe.append(
            f'<tr class="{ev.azione}"><td>{ev.istante:%d/%m/%Y}</td><td>{_e(cosa)}</td>'
            f"<td>{_e(_FATTI.get(f.tipo, f.tipo))}</td><td>{_e(_valore_fatto(f))}</td><td>{validita}</td></tr>"
        )
    return (
        '<table class="tabella"><thead><tr><th>Registrato il</th><th>Cosa</th><th>Fatto</th><th>Valore</th>'
        f"<th>Vale per</th></tr></thead><tbody>{''.join(righe)}</tbody></table>"
    )


def _competenze(caso: Caso, corpus: Corpus) -> str:
    blocchi = []
    for mese in caso.competenze:
        try:
            corpo = _righe_importi(calcola(caso.storia.registro, corpus, caso.storia.rapporto, mese))
        except ErrorePaghe as errore:
            corpo = _caso_non_modellato(errore, "il calcolo")
        blocchi.append(f"<h4>Competenza {_mese(mese)}</h4>{corpo}")
    return "".join(blocchi)


def _denuncia(caso: Caso, corpus: Corpus, mese: Mese) -> str:
    try:
        denuncia = calcola_denuncia(caso.storia.registro, corpus, caso.storia.rapporto, mese)
    except ErrorePaghe as errore:
        return _caso_non_modellato(errore, "la denuncia")
    if not denuncia.periodi:
        return '<p class="vuoto">Nessun importo pagato nel mese: nessun periodo con imponibili.</p>'
    blocchi = []
    for p in denuncia.periodi:
        stato = "in servizio" if p.in_servizio else "fuori servizio"
        recuperi = "".join(
            f'<li>Recupero <b>{_e(r.caso)}</b>: {_e(istituto(r.importo.istituto))} di competenza '
            f"{_periodo(r.importo.periodo)}, {euro(r.importo.valore)}</li>"
            for r in p.recuperi
        )
        blocchi.append(
            f'<div class="periodo-denuncia"><h4>Periodo dichiarato {_periodo(p.periodo)} · {stato}</h4>'
            f'<div class="colonne"><div><h5>Basi imponibili</h5>{_righe_importi(p.basi)}</div>'
            f"<div><h5>Contributi</h5>{_righe_importi(p.contributi)}</div></div>"
            + (f'<ul class="recuperi">{recuperi}</ul>' if recuperi else "")
            + "</div>"
        )
    return "".join(blocchi)


def _voce(nome: str, valore) -> str:
    return f"<dt>{_e(nome)}</dt><dd>{valore}</dd>" if valore not in (None, "", "—") else ""


def _quadro(q) -> str:
    nome = q.tipo if q.causale is None else f"{q.tipo} causale {q.causale} · {_CAUSALI.get(q.causale, '')}"
    i = q.inquadramento
    voci = [
        _voce("Qualifica / contratto", f"{_e(i.qualifica)} / {_e(i.contratto)}"),
        _voce("Regime di fine servizio", f"{_e(i.regime_fine_servizio)} · {_REGIMI.get(i.regime_fine_servizio or '', '?')}"),
    ]
    if q.pensionistica:
        voci.append(_voce("CPDEL", f"imponibile {euro(q.pensionistica.imponibile)}, contributo {euro(q.pensionistica.contributo)}"))
    voci.append(_voce("Contributo aggiuntivo 1%", euro(q.contrib_1_per_cento) if q.contrib_1_per_cento else None))
    if q.credito:
        voci.append(_voce("Fondo Credito", f"imponibile {euro(q.credito.imponibile)}, contributo {euro(q.credito.contributo)}"))
    pv = q.previdenziale
    if pv:
        if pv.imponibile_tfs is not None:
            voci.append(_voce(f"TFS (gestione {pv.cod_gestione})", f"imponibile {euro(pv.imponibile_tfs)}, contributo {euro(pv.contributo_tfs)}"))
        if pv.imponibile_tfr is not None:
            voci.append(_voce(f"TFR (gestione {pv.cod_gestione})", f"imponibile {euro(pv.imponibile_tfr)}, contributo {euro(pv.contributo_tfr)}"))
        if pv.imponibile_tfr_ulteriori is not None:
            voci.append(_voce("TFR ulteriori elementi", f"imponibile {euro(pv.imponibile_tfr_ulteriori)}, contributo {euro(pv.contributo_tfr_ulteriori)}"))
    voci.append(_voce("Retribuzione teorica tabellare TFR", euro(q.retrib_teorica_tfr) if q.retrib_teorica_tfr is not None else None))
    voci.append(_voce("Retribuzione valutabile TFR", euro(q.retrib_valutabile_tfr) if q.retrib_valutabile_tfr is not None else None))
    voci.append(_voce("Codice di cessazione", _e(q.codice_cessazione) if q.codice_cessazione else None))
    for ev in q.enti_versanti:
        voci.append(
            _voce(
                f"Ente versante, tipo contributo {ev.tipo_contributo}",
                f"imponibile {euro(ev.imponibile)}, contributo {euro(ev.contributo)}, pagato in {_mese(ev.anno_mese_erogazione)}",
            )
        )
    if not (q.pensionistica or q.credito or pv):
        voci.append(_voce("Gestioni", "nessuna: il quadro dichiara il servizio, gli importi stanno nel mese di pagamento"))
    return f'<div class="quadro"><div class="quadro-nome">{_e(nome)}</div><div class="quadro-periodo">{_periodo(q.periodo)}</div><dl>{"".join(voci)}</dl></div>'


def _lista(caso: Caso, corpus: Corpus, mese: Mese) -> tuple[str, bool]:
    try:
        vista = lista_pos_pa(caso.storia.registro, corpus, caso.storia.rapporto, mese)
    except ErrorePaghe as errore:
        return _caso_non_modellato(errore, "la ListaPosPA"), False
    parti = []
    stato = '<span class="badge ok">Trasmissibile</span>' if vista.trasmissibile else '<span class="badge ko">Non trasmissibile</span>'
    parti.append(f'<p class="stato">{stato}</p>')
    parti.extend(_quadro(q) for q in vista.quadri)
    for f in vista.fermi:
        parti.append(
            _fermo(f"Quadro fermo: {f.quadro}", f"Periodo {_periodo(f.periodo)}. {f.motivo}")
            + (f'<div class="conservati"><h5>Importi calcolati e conservati</h5>{_righe_importi(f.importi)}</div>' if f.importi else "")
        )
    for m in vista.mancanti:
        parti.append(_fermo("Dato da registrare", f"Il tracciato chiede «{_FATTI.get(m.fatto, m.fatto)}»{' per il periodo ' + _periodo(m.periodo) if m.periodo else ''}: la vista non lo stima."))
    for motivo in vista.bozza:
        parti.append(_fermo("Bozza non trasmissibile", motivo))
    for avviso in vista.avvisi:
        parti.append(f'<div class="avviso">{_e(leggibile(avviso))}</div>')
    if not vista.quadri and not vista.fermi:
        parti.append('<p class="vuoto">Nessun quadro in questo mese.</p>')
    try:
        xml = in_xml([vista], ENTE, MITTENTE, mese=mese)
        parti.append(f'<details class="xml"><summary>XML ListaPosPA di {_mese(mese)}</summary><pre>{_e(xml)}</pre></details>')
    except VistaFerma as errore:
        parti.append(f'<p class="vuoto">L\'XML non si produce: {_e(errore)}</p>')
    return "".join(parti), vista.trasmissibile


def _scheda(numero: int, caso: Caso, corpus: Corpus) -> tuple[str, list[bool]]:
    s = caso.storia
    cf = next((ev.fatto.valore for ev in s.diario if ev.fatto and ev.fatto.tipo == "codice_fiscale"), "")
    denunce, esiti = [], []
    for mese in caso.denunce:
        lista, trasmissibile = _lista(caso, corpus, mese)
        esiti.append(trasmissibile)
        denunce.append(
            f'<div class="mese-denuncia"><h3>Denuncia di {_mese(mese)}</h3>'
            f'<div class="passo"><span class="num">3</span><h4>Basi e contributi, per cassa</h4></div>{_denuncia(caso, corpus, mese)}'
            f'<div class="passo"><span class="num">4</span><h4>ListaPosPA</h4></div>{lista}</div>'
        )
    note = "".join(f"<li>{_e(n)}</li>" for n in caso.note)
    corpo = (
        f'<section id="{caso.id}" class="caso">'
        f'<div class="caso-testa"><span class="label">Dipendente {numero} · {_e(s.rapporto)} · {_e(cf)}</span>'
        f"<h2>{_e(caso.titolo)}</h2><p>{_e(caso.racconto)}</p>"
        + (f'<p class="guarda"><b>Da guardare.</b> {_e(caso.da_guardare)}</p>' if caso.da_guardare else "")
        + (f'<ul class="note">{note}</ul>' if note else "")
        + "</div>"
        f'<div class="passo"><span class="num">1</span><h3>Fatti registrati</h3></div>{_diario(s)}'
        f'<div class="passo"><span class="num">2</span><h3>Importi per competenza, come risultano oggi</h3></div>'
        f"{_competenze(caso, corpus)}"
        + "".join(denunce)
        + "</section>"
    )
    return corpo, esiti


# --- Pagina -------------------------------------------------------------------------------------

STILE = """
:root{--cyan:#00AEEF;--navy:#1E2939;--ocean:#0369A1;--gold:#C48820;--bg:#F9FAFB;--ice:#EFF6FF;
--testo:#333;--medio:#4A5565;--tenue:#6A7282;--bordo:#E5E7EB;--rosso:#DC2626;--verde:#166534}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--testo);font:15px/1.6 Inter,Arial,sans-serif}
header{background:var(--navy);color:#fff;padding:28px 16px}
header .dentro,main{max-width:1080px;margin:0 auto}
main{padding:16px}
h1,h2,h3{font-family:Nunito,Arial,sans-serif;color:var(--navy);margin:0 0 8px}
header h1{color:#fff;font-size:28px}
header p{color:#D1D5DB;margin:4px 0}
h2{font-size:24px}h3{font-size:18px}h4{font-size:15px;margin:16px 0 6px;color:var(--navy)}h5{font-size:13px;margin:4px 0;color:var(--tenue);text-transform:uppercase;letter-spacing:.05em}
.prototipo{background:#FEF3C7;color:#92400E;border-radius:8px;padding:10px 14px;margin:16px 0;font-weight:600}
.label{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--tenue)}
.indice{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0}
.indice a{display:block;background:#fff;border:1px solid var(--bordo);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--testo);box-shadow:0 1px 2px rgba(0,0,0,.05)}
.indice a:hover{border-color:var(--cyan)}
.indice b{display:block;color:var(--navy)}
.caso{background:#fff;border:1px solid var(--bordo);border-radius:16px;padding:20px;margin:24px 0;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.caso-testa{border-left:4px solid var(--cyan);padding-left:12px;margin-bottom:16px}
.guarda{background:var(--ice);border-radius:8px;padding:8px 12px}
.passo{display:flex;align-items:center;gap:10px;margin:22px 0 8px}
.passo h3,.passo h4{margin:0}
.num{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:50%;background:var(--cyan);color:#fff;font-weight:700;font-size:13px;flex:none}
.mese-denuncia{border-top:2px solid var(--ice);margin-top:24px;padding-top:12px}
.tabella{width:100%;border-collapse:collapse;font-size:13px;display:block;overflow-x:auto}
.tabella th{text-align:left;color:var(--tenue);font-weight:600;border-bottom:1px solid var(--bordo);padding:6px 8px;white-space:nowrap}
.tabella td{border-bottom:1px solid #F3F4F6;padding:5px 8px;vertical-align:top}
tr.annulla td{color:var(--rosso);text-decoration:line-through}
tr.annulla td:nth-child(2){text-decoration:none}
tr.paga td{background:#F0FDF4}
details.importo{border:1px solid var(--bordo);border-radius:8px;margin:4px 0;background:#fff}
details.importo>summary{cursor:pointer;display:flex;gap:12px;align-items:baseline;padding:6px 10px;list-style:none}
details.importo>summary::-webkit-details-marker{display:none}
details.importo>summary::before{content:"▸";color:var(--cyan)}
details.importo[open]>summary::before{content:"▾"}
summary .periodo{color:var(--tenue);font-size:12px}
summary .valore{margin-left:auto;font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap}
.spiega{padding:6px 12px 10px 26px;font-size:13px;border-top:1px solid #F3F4F6;background:#FCFCFD}
.riga{margin:3px 0}
.figli{margin-left:6px;border-left:2px solid var(--ice);padding-left:8px}
code{font-family:"Courier New",monospace;font-size:12px;background:#F3F4F6;border-radius:4px;padding:1px 4px;word-break:break-word}
.fonte{display:inline-block;border-radius:9999px;padding:0 8px;font-size:12px;font-weight:600;margin:1px 0}
.fonte.norma{background:#DCFCE7;color:var(--verde)}
.fonte.istruzione{background:#DBEAFE;color:#1D4ED8}
.fonte.prassi{background:#FEF3C7;color:#92400E}
.fonte.altro{background:#F3F4F6;color:var(--medio)}
a .fonte{text-decoration:underline}
.badge{display:inline-block;border-radius:9999px;padding:2px 10px;font-size:12px;font-weight:700;letter-spacing:.02em}
.badge.ok{background:#DCFCE7;color:var(--verde)}
.badge.ko{background:#FEE2E2;color:var(--rosso)}
.badge.prassi-sola{background:var(--gold);color:#fff}
.colonne{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:760px){.colonne{grid-template-columns:1fr}}
.quadro{border:1px solid var(--bordo);border-left:4px solid var(--ocean);border-radius:8px;padding:10px 14px;margin:8px 0}
.quadro-nome{font-weight:700;color:var(--navy)}
.quadro-periodo{color:var(--tenue);font-size:13px}
.quadro dl{display:grid;grid-template-columns:max-content 1fr;gap:2px 14px;margin:8px 0 0;font-size:13px}
.quadro dt{color:var(--tenue)}.quadro dd{margin:0}
.fermo{border:1px solid #FCD34D;background:#FFFBEB;border-left:4px solid var(--gold);border-radius:8px;padding:10px 14px;margin:8px 0}
.fermo-titolo{font-weight:700;color:#92400E}
.fermo p{margin:4px 0 0;font-size:14px}
.avviso{background:var(--ice);border-radius:8px;padding:8px 12px;margin:8px 0;font-size:14px}
.vuoto{color:var(--tenue);font-style:italic}
details.xml{margin:10px 0}
details.xml summary{cursor:pointer;color:var(--ocean);font-weight:600}
pre{background:var(--navy);color:#E5E7EB;border-radius:8px;padding:12px;overflow-x:auto;font-size:12px;line-height:1.45}
.legenda span{margin-right:6px}
footer{max-width:1080px;margin:0 auto;padding:16px 16px 40px;color:var(--tenue);font-size:13px}
"""


def pagina(corpus: Corpus) -> str:
    schede, indice = [], []
    for numero, costruisci in enumerate(CASI, start=1):
        caso = costruisci(corpus)
        corpo, esiti = _scheda(numero, caso, corpus)
        schede.append(corpo)
        stato = "trasmissibile" if all(esiti) else "con un caso fermo"
        indice.append(f'<a href="#{caso.id}"><span class="label">Dipendente {numero}</span><b>{_e(caso.titolo)}</b>{stato}</a>')
        caso.storia.registro.chiudi()
    legenda = (
        '<p class="legenda">Fonti: <span class="fonte norma">norma o CCNL</span>'
        '<span class="fonte istruzione">istruzione INPS</span>'
        '<span class="fonte prassi">nota di prassi interna</span>'
        '<span class="badge prassi-sola">SOLO PRASSI</span> quando una regola o un parametro non ha altra fonte. '
        "Clic su un importo per vedere da dove viene.</p>"
    )
    return (
        "<!doctype html>\n<html lang=\"it\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>Dal fatto alla ListaPosPA</title><style>{STILE}</style></head><body>"
        '<header><div class="dentro"><span class="label" style="color:#00AEEF">Paghe Enti Locali · comparto Funzioni Locali</span>'
        "<h1>Dal fatto alla ListaPosPA</h1>"
        "<p>Per ogni dipendente: i fatti registrati, gli importi per competenza, la denuncia per cassa, "
        "la ListaPosPA e, per ogni importo, la catena fino alla norma.</p></div></header><main>"
        '<div class="prototipo">PROTOTIPO DA BUTTARE (ticket #37): una dimostrazione, non l\'interfaccia. '
        "Persone e codici fiscali di fantasia; regole e parametri dal corpus reale "
        f"<code>{_e(CORPUS.name)}</code>, versione <code>{_e(corpus.versione[:12])}</code>.</div>"
        f"{legenda}<nav class=\"indice\">{''.join(indice)}</nav>"
        + "".join(schede)
        + "</main><footer>Rigenerare: <code>python -m paghe.prototipo &lt;cartella&gt;</code> dalla radice del repo. "
        "La pagina non si committa.</footer></body></html>\n"
    )


def genera(cartella: str | Path) -> Path:
    cartella = Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    corpus = Corpus.carica(CORPUS, reale=True)
    percorso = cartella / "index.html"
    percorso.write_text(pagina(corpus), encoding="utf-8")
    return percorso


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.exit("Uso: python -m paghe.prototipo <cartella>")
    print(genera(argv[0]))


if __name__ == "__main__":
    main()
