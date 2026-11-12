"""Lettura dei file del gestionale in uso: cedolini (PDF), anagrafiche (tabella HTML salvata come .xls), scritture F24EP (CSV).

Non calcola nulla: trascrive. Se trova una colonna o una voce fissa che non conosce si ferma e la nomina, non la indovina.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path


class ErroreLettura(Exception):
    pass


def soldi(testo: str) -> Decimal:
    """«1.715,27» -> 1715.27; «-1,06» -> -1.06."""
    return Decimal(testo.strip().replace(".", "").replace(",", "."))


def _data(testo: str) -> date | None:
    trovato = re.fullmatch(r"(\d{2})-(\d{2})-(\d{4})", (testo or "").strip())
    return date(int(trovato.group(3)), int(trovato.group(2)), int(trovato.group(1))) if trovato else None


# Cedolini

# Le voci fisse della testata del cedolino, cosi' come le scrive il gestionale.
VOCI_FISSE = (
    "STIPENDIO BASE",
    "IND.VACANZA CONT.",
    "ASS.AD PERSONAM",
    "IND.DI VIGILANZA",
    "IND.COMPARTO Q.F.",
    "DIFF.STIPENDIALE",
    "DIFF.STORICO",
    "VARIE PENSION.",
    "IND.SPECIFICA",
    "RETR.POSIZ.N.DIR.",
)

# Bordo destro delle colonne del corpo del cedolino (punti): i numeri sono allineati a destra.
_COLONNE = (("giorni", 255), ("base", 325), ("imponibile", 388), ("aliquota", 428), ("trattenuta", 500), ("competenza", 575))
_NUMERO = re.compile(r"-?\d[\d.]*,\d{2,3}")


@dataclass(frozen=True)
class RigaCedolino:
    codice: str
    descrizione: str
    giorni: Decimal | None = None
    base: Decimal | None = None
    imponibile: Decimal | None = None
    aliquota: Decimal | None = None
    trattenuta: Decimal | None = None
    competenza: Decimal | None = None


@dataclass
class Cedolino:
    ente: str = ""
    matricola: int = 0
    nominativo: str = ""
    codice_fiscale: str = ""
    profilo: str = ""
    area: str = ""  # sigla del gestionale: FUN, IST, OE, OP
    rapporto: str = ""  # TI, TD
    fisse: dict[str, Decimal] = field(default_factory=dict)
    righe: list[RigaCedolino] = field(default_factory=list)
    imponibile_irpef: Decimal | None = None
    imposta_lorda: Decimal | None = None
    detrazioni: Decimal | None = None
    imposta_netta: Decimal | None = None
    detrazioni_dettaglio: dict[str, Decimal] = field(default_factory=dict)
    totale_competenze: Decimal | None = None
    totale_contributi: Decimal | None = None
    totale_trattenute: Decimal | None = None
    netto: Decimal | None = None

    def riga(self, codice: str) -> RigaCedolino | None:
        return next((r for r in self.righe if r.codice == codice), None)

    def somma(self, codici, campo: str) -> Decimal:
        return sum((getattr(r, campo) or Decimal(0) for r in self.righe if r.codice in codici), Decimal(0))


def _linee(pagina) -> list[list[dict]]:
    """Le parole della pagina raggruppate per riga, da sinistra a destra."""
    parole = sorted(pagina.extract_words(x_tolerance=1.5), key=lambda p: (p["top"], p["x0"]))
    linee: list[list[dict]] = []
    for parola in parole:
        if linee and abs(parola["top"] - linee[-1][0]["top"]) <= 3:
            linee[-1].append(parola)
        else:
            linee.append([parola])
    return [sorted(linea, key=lambda p: p["x0"]) for linea in linee]


def _testo(linea: list[dict]) -> str:
    return " ".join(p["text"] for p in linea)


def _voci_fisse(nomi: str, valori: list[dict]) -> dict[str, Decimal]:
    resto, trovate = nomi, []
    while resto:
        nome = next((v for v in VOCI_FISSE if resto.startswith(v)), None)
        if nome is None:
            raise ErroreLettura(f"voce fissa del cedolino non conosciuta: «{resto}»")
        trovate.append(nome)
        resto = resto[len(nome):].strip()
    if len(trovate) != len(valori):
        raise ErroreLettura(f"voci fisse {trovate}: {len(valori)} importi")
    return {nome: soldi(p["text"]) for nome, p in zip(trovate, valori)}


def _riga_corpo(linea: list[dict]) -> RigaCedolino | None:
    if not re.fullmatch(r"\d{3,4}", linea[0]["text"]):
        return None
    descrizione, valori = [], {}
    for parola in linea[1:]:
        if _NUMERO.fullmatch(parola["text"]) and parola["x1"] > 225:
            colonna = next((nome for nome, bordo in _COLONNE if parola["x1"] <= bordo), None)
            if colonna is None or colonna in valori:
                raise ErroreLettura(f"riga del cedolino non leggibile: «{_testo(linea)}»")
            valori[colonna] = soldi(parola["text"])
        else:
            descrizione.append(parola["text"])
    return RigaCedolino(linea[0]["text"], " ".join(descrizione), **valori)


def _per_bordo(linea: list[dict], bordi) -> dict[str, Decimal]:
    letti = {}
    for parola in linea:
        if _NUMERO.fullmatch(parola["text"]):
            nome = next((n for n, bordo in bordi if parola["x1"] <= bordo), None)
            if nome:
                letti[nome] = soldi(parola["text"])
    return letti


_PIEDE = (("imponibile_irpef", 100), ("", 135), ("imposta_lorda", 175), ("", 205), ("detrazioni", 245), ("imposta_netta", 320))
_DETRAZIONI = (("coniuge", 95), ("figli", 165), ("altri_familiari", 240), ("altre", 320), ("oneri", 390))


def leggi_cedolini(percorso: Path) -> list[Cedolino]:
    import pdfplumber  # dipendenza solo di questa prova, non del nucleo

    cedolini = []
    with pdfplumber.open(percorso) as documento:
        for pagina in documento.pages:
            linee = _linee(pagina)
            testi = [_testo(linea) for linea in linee]
            if not any(t.startswith("MATRICOLA") for t in testi):
                continue
            c = Cedolino()
            corpo = False
            for i, (linea, testo) in enumerate(zip(linee, testi)):
                seguente = linee[i + 1] if i + 1 < len(linee) else []
                if testo.startswith("MATRICOLA"):
                    parole = _testo(seguente).split()
                    c.matricola, c.codice_fiscale, c.nominativo = int(parole[0]), parole[-1], " ".join(parole[1:-1])
                elif i == 1 and " - " in testo:
                    c.ente = testo.split(" - ")[0].strip()
                elif testo.startswith("PROFILO PROFESSIONALE"):
                    parole = _testo(seguente).split()
                    sigle = parole[-1].split("/")
                    c.profilo, c.area, c.rapporto = " ".join(parole[:-1]), sigle[0], sigle[-1]
                elif testo.startswith("COD. DESCRIZIONE"):
                    corpo = True
                    if i >= 2 and testi[i - 2].startswith(VOCI_FISSE):
                        c.fisse = _voci_fisse(testi[i - 2], linee[i - 1])
                elif testo.startswith("IMPONIBILE IRPEF IMPOSTA LORDA"):
                    corpo = False
                    for nome, valore in _per_bordo(seguente, _PIEDE).items():
                        setattr(c, nome, valore)
                    dopo = linee[i + 2] if i + 2 < len(linee) else []
                    c.totale_competenze = next((soldi(p["text"]) for p in dopo if p["x1"] > 500 and _NUMERO.fullmatch(p["text"])), None)
                elif testo.startswith("Detr.Coniuge"):
                    c.detrazioni_dettaglio = _per_bordo(seguente, _DETRAZIONI) if len(seguente) <= 5 else {}
                elif testo == "TOTALE RIT.CONTRIB.":
                    # L'importo sta sulla riga dopo le intestazioni degli arretrati, a destra.
                    for altra in linee[i + 1 : i + 3]:
                        valore = next((soldi(p["text"]) for p in altra if p["x1"] > 500 and _NUMERO.fullmatch(p["text"])), None)
                        if valore is not None:
                            c.totale_contributi = valore
                            break
                elif testo == "TOTALE TRATTENUTE":
                    c.totale_trattenute = next((soldi(p["text"]) for p in seguente if _NUMERO.fullmatch(p["text"])), None)
                elif testo.startswith("Euro "):
                    c.netto = soldi(linea[-1]["text"])
                elif corpo:
                    riga = _riga_corpo(linea)
                    if riga is not None:
                        c.righe.append(riga)
            if c.netto is None or c.totale_competenze is None:
                raise ErroreLettura(f"cedolino della matricola {c.matricola}: netto o totale delle competenze non letti")
            cedolini.append(c)
    return cedolini


# Anagrafiche

class _Tabelle(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tabelle: list[list[list[str]]] = []
        self._cella: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tabelle.append([])
        elif tag == "tr" and self.tabelle:
            self.tabelle[-1].append([])
        elif tag in ("td", "th") and self.tabelle and self.tabelle[-1]:
            self._cella = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cella is not None:
            self.tabelle[-1][-1].append(" ".join("".join(self._cella).split()))
            self._cella = None

    def handle_data(self, data):
        if self._cella is not None:
            self._cella.append(data)


@dataclass(frozen=True)
class Anagrafica:
    ente: str
    matricola: int
    campi: dict[str, str]

    def __getitem__(self, nome: str) -> str:
        return self.campi.get(nome, "")

    @property
    def assunzione(self) -> date | None:
        return _data(self["assunto il"])

    @property
    def cessazione(self) -> date | None:
        return _data(self["cessato il"])

    @property
    def nascita(self) -> date | None:
        return _data(self["nato il"])


def leggi_anagrafiche(percorso: Path) -> list[Anagrafica]:
    lettore = _Tabelle()
    lettore.feed(percorso.read_text(encoding="latin-1"))
    tabella = max(lettore.tabelle, key=len)
    testata = tabella[0]
    righe = []
    for celle in tabella[1:]:
        if len(celle) < 3 or not celle[1].strip().isdigit():
            continue
        # La colonna dopo «tab.ritenute» non ha titolo: e' la descrizione della tabella ritenute.
        campi = {(nome or f"colonna_{n}"): valore.strip() for n, (nome, valore) in enumerate(zip(testata, celle))}
        righe.append(Anagrafica(celle[0].strip(), int(celle[1]), campi))
    return righe


# Scritture F24EP: una riga per persona e voce, con la quota a carico dell'ente segnata da una X

@dataclass(frozen=True)
class ScritturaF24:
    ente: str
    matricola: int
    codice: str
    voce: str
    a_carico_ente: bool
    importo: Decimal
    tributo: str
    riferimento_b: str


def leggi_scritture_f24(percorso: Path) -> list[ScritturaF24]:
    with percorso.open(encoding="latin-1", newline="") as flusso:
        righe = list(csv.reader(flusso, delimiter=";"))
    testata = [nome.strip() for nome in righe[0]]
    scritture = []
    for celle in righe[1:]:
        d = dict(zip(testata, (c.strip() for c in celle)))
        if not d.get("matr.", "").isdigit() or d["matr."] == "0" or not d.get("importo"):
            continue  # riga del totale
        scritture.append(
            ScritturaF24(d["ente"], int(d["matr."]), d["cod."], d["voce"], d["c.ente"] == "X", soldi(d["importo"]), d["trib.F24EP"], d["rif.B"])
        )
    return scritture


# Estrazione voci: una riga per matricola, mese e voce dell'anno

VOCE_IMPONIBILE_IRPEF = "9001"


def leggi_imponibili_irpef(percorso: Path, anno: int) -> dict[int, dict[int, Decimal]]:
    """L'imponibile IRPEF di ogni mese pagato (voce 9001), per matricola: il pagato da inizio anno della proiezione."""
    lettore = _Tabelle()
    lettore.feed(percorso.read_text(encoding="latin-1"))
    tabella = max(lettore.tabelle, key=len)
    testata = [nome.strip() for nome in tabella[0]]
    imponibili: dict[int, dict[int, Decimal]] = {}
    for celle in tabella[1:]:
        d = dict(zip(testata, (c.strip() for c in celle)))
        if not d.get("Matr.", "").isdigit() or d.get("Anno") != str(anno):
            continue
        if d["Voce"].partition("-")[0] != VOCE_IMPONIBILE_IRPEF:
            continue
        mesi = imponibili.setdefault(int(d["Matr."]), {})
        mesi[int(d["Mese"])] = mesi.get(int(d["Mese"]), Decimal(0)) + soldi(d["Importo"])
    return imponibili
