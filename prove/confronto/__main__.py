"""Confronto di un mese tra il gestionale in uso e il nucleo.

    python -m prove.confronto <cartella dell'ente> --mese 2026-10 --valuta 2026-10-27

La cartella sta fuori dal repo e contiene `anagrafiche/` e `gestionale/` con i file cosi' come escono dal gestionale.
Il risultato e' un file Excel scritto nella stessa cartella, in `confronto/`.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from paghe import Mese

from . import aggiunta as A
from . import irpef
from .calcolo import REGIMI, Calcolato, Giro, gira
from .lettura import Anagrafica, Cedolino, ScritturaF24, leggi_anagrafiche, leggi_cedolini, leggi_imponibili_irpef, leggi_scritture_f24

ZERO = Decimal(0)
TOLLERANZA = Decimal("0.01")
ADDIZIONALI = ("1711", "1712", "1713", "9211", "9213")
ASSENZE = ("6571", "6576", "7050")
CONTRIBUTI = ("8117", "8118", "8119", "8120")
NOTE_FISSE = ("304", "1140", "9012", *ADDIZIONALI, *ASSENZE, *CONTRIBUTI)


@dataclass(frozen=True)
class Riga:
    matricola: int
    nominativo: str
    gruppo: str
    voce: str
    gestionale: Decimal | None
    prototipo: Decimal | None
    origine: str  # «calcolato» dal nucleo o «letto dal gestionale»
    nota: str = ""

    @property
    def differenza(self) -> Decimal | None:
        if self.gestionale is None or self.prototipo is None:
            return None
        return self.prototipo - self.gestionale

    @property
    def esito(self) -> str:
        if self.origine == "letto dal gestionale":
            return "non confrontabile"
        if self.differenza is None:
            return "manca da un lato"
        return "uguale" if abs(self.differenza) <= TOLLERANZA else "diverso"


def _f24(scritture: list[ScritturaF24], matricola: int, codice: str, ente: bool) -> Decimal | None:
    trovate = [s.importo for s in scritture if s.matricola == matricola and s.codice == codice and s.a_carico_ente == ente]
    return sum(trovate, ZERO) if trovate else None


def _note_persona(c: Cedolino) -> list[str]:
    note = []
    for r in c.righe:
        if r.codice in ASSENZE:
            note.append(f"assenza: {r.descrizione} ({r.giorni or ''} gg/ore, {r.imponibile})")
        elif r.codice not in NOTE_FISSE:
            valore = r.competenza if r.competenza is not None else r.trattenuta
            note.append(f"voce non nel confronto: {r.codice} {r.descrizione} ({valore})")
    carichi = {k: v for k, v in c.detrazioni_dettaglio.items() if k in ("coniuge", "figli", "altri_familiari")}
    if carichi:
        note.append("carichi di famiglia non registrati: " + ", ".join(f"{k} {v}" for k, v in carichi.items()))
    return note


def righe_di_confronto(c: Cedolino, a: Anagrafica, r: Calcolato, scritture: list[ScritturaF24]) -> list[Riga]:
    area = A.AREE[c.area]
    righe: list[Riga] = []

    def aggiungi(gruppo, voce, gestionale, prototipo, origine="calcolato", nota=""):
        if gestionale is None and prototipo is None:
            return
        righe.append(Riga(c.matricola, c.nominativo, gruppo, voce, gestionale, prototipo, origine, nota))

    assenze = c.somma(ASSENZE, "imponibile")
    altre = sum((x.competenza or ZERO for x in c.righe if x.codice not in NOTE_FISSE), ZERO)
    terzi = sum((x.trattenuta or ZERO for x in c.righe if x.codice not in NOTE_FISSE), ZERO)
    nota_assenze = f"il gestionale riduce di {assenze} per assenze, non modellate" if assenze else ""
    nota_lordo = "; ".join(n for n in (nota_assenze, f"il gestionale ha altre competenze per {altre}, non modellate" if altre else "") if n)

    # Voci fisse
    for voce, importo in c.fisse.items():
        if voce == A.VOCE_TABELLARE:
            aggiungi("Voci fisse", voce, importo, r.valore(f"tabellare_{area}"), "letto dal gestionale", "tabellare del corpus sostituito, vedi Sintesi")
        elif voce == A.VOCE_COMPARTO:
            aggiungi("Voci fisse", voce, importo, r.valore(f"comparto_{area}"))
        else:
            aggiungi("Voci fisse", voce, importo, r.valore(A.PER_VOCE[voce].istituto), "letto dal gestionale")
    lordo = r.somma("retribuzione") - (r.valore("riduzione_tfr") or ZERO)
    aggiungi("Lordo", "Retribuzione mensile (304)", c.riga("304").competenza, lordo)
    aggiungi("Lordo", "Riduzione 2,50% TFR (1140)", c.somma(("1140",), "competenza") or None, r.valore("riduzione_tfr"), nota=nota_assenze)
    aggiungi("Lordo", "Totale competenze", c.totale_competenze, r.somma("retribuzione"), nota=nota_lordo)

    # Contributi a carico del lavoratore (cedolino)
    figurativo = c.somma(("8120",), "trattenuta")
    aggiungi("Contributi lavoratore", "CPDEL (8118)", c.somma(("8118",), "trattenuta"), r.valore("cpdel_lavoratore"), nota=nota_lordo)
    aggiungi(
        "Contributi lavoratore", "Fondo credito (8119 + 8120)", c.somma(("8119", "8120"), "trattenuta"), r.valore("fondo_credito"),
        nota="; ".join(n for n in (nota_lordo, f"di cui {figurativo} sul figurativo delle assenze" if figurativo else "") if n),
    )
    aggiungi("Contributi lavoratore", "TFS (8117)", c.somma(("8117",), "trattenuta") or None, r.valore("tfs_lavoratore"), nota=nota_lordo)

    # Contributi e IRAP a carico dell'ente (scritture F24EP)
    for voce, codice, istituto in (
        ("CPDEL ente (8118)", "8118", "cpdel_ente"),
        ("TFS ente (8117)", "8117", "tfs_ente"),
        ("TFR (8115)", "8115", "contributo_tfr"),
        ("TFR ulteriori elementi 6,91% (8106)", "8106", "contributo_tfr_ulteriori"),
        ("IRAP (8001)", "8001", "irap_acconto"),
    ):
        aggiungi("Carico ente", voce, _f24(scritture, c.matricola, codice, True), r.valore(istituto), nota=nota_lordo)

    # Fisco
    imponibile = r.imponibile_fiscale()
    riduzione = r.valore("riduzione_tfr") or ZERO
    if imponibile is not None and riduzione and imponibile == r.somma("retribuzione") - riduzione - r.somma("contributo_lavoratore"):
        nota_lordo = "; ".join(n for n in (nota_lordo, f"il nucleo non toglie dall'imponibile fiscale la riduzione TFR ({riduzione})") if n)
    carichi = sum((v for k, v in c.detrazioni_dettaglio.items() if k in ("coniuge", "figli", "altri_familiari")), ZERO)
    dedotti = sum((x.trattenuta or ZERO for x in c.righe if x.codice == "1367"), ZERO)
    nota_fisco = "; ".join(
        n for n in (nota_lordo, f"il gestionale deduce {dedotti} di riscatto, non modellato" if dedotti else "") if n
    )
    aggiungi("Fisco", "Imponibile IRPEF", c.imponibile_irpef, imponibile, nota=nota_fisco)
    aggiungi(
        "Fisco", "IRPEF netta, senza carichi di famiglia", (c.imposta_netta or ZERO) + carichi, r.valore("ritenuta_irpef"),
        nota="; ".join(
            n
            for n in (
                f"gestionale: lorda {c.imposta_lorda}, detrazione lavoro {c.detrazioni_dettaglio.get('altre', ZERO)}, ulteriore detrazione "
                f"{c.somma(('9012',), 'base')}" + (f", carichi {carichi} tolti dal confronto" if carichi else ""),
                # Con lo stesso imponibile l'imposta lorda e' la stessa: le detrazioni del prototipo sono lorda meno ritenuta.
                f"prototipo: detrazioni totali {c.imposta_lorda - r.valore('ritenuta_irpef')}"
                if c.imponibile_irpef == imponibile and c.imposta_lorda is not None and r.valore("ritenuta_irpef") is not None else "",
                nota_fisco,
            )
            if n
        ),
    )
    for voce, istituto in (("Somma esente (L. 207/2024)", "somma_esente"), ("Trattamento integrativo", "trattamento_integrativo")):
        valore = r.valore(istituto)
        if valore:
            aggiungi("Fisco", voce, ZERO, valore, nota="il cedolino del gestionale non ha questa voce")

    # Netto, prima delle addizionali (aliquote dei comuni non nel corpus) e delle trattenute a terzi (non modellate)
    addizionali = c.somma(ADDIZIONALI, "trattenuta")
    addizionali_nucleo = sum((x.importo.valore for x in r.righe if x.natura == "addizionale" and x.effetto == "meno"), ZERO)
    aggiungi(
        "Netto", "Netto prima di addizionali e trattenute a terzi", c.netto + addizionali + terzi,
        (r.netto + addizionali_nucleo) if r.netto is not None else None,
        nota=f"gestionale: netto in busta {c.netto}, addizionali {addizionali}, trattenute a terzi {terzi}",
    )
    return righe


# Excel

def _scrivi(percorso: Path, mese: Mese, valuta: date, tabellare: str, cedolini, anagrafiche, giro: Giro, righe: list[Riga], fiscali=()) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    grassetto = Font(bold=True)
    testata = PatternFill("solid", fgColor="D9E1F2")
    colori = {"diverso": "F8CBAD", "uguale": "C6EFCE", "non confrontabile": "EDEDED", "manca da un lato": "FFE699"}

    def intesta(foglio, titoli, larghezze):
        foglio.append(titoli)
        for n, larghezza in enumerate(larghezze, 1):
            cella = foglio.cell(row=foglio.max_row, column=n)
            cella.font, cella.fill = grassetto, testata
            foglio.column_dimensions[get_column_letter(n)].width = larghezza
        foglio.freeze_panes = foglio.cell(row=foglio.max_row + 1, column=1)

    libro = Workbook()
    per_matricola = {c.matricola: c for c in cedolini}

    # Sintesi
    s = libro.active
    s.title = "Sintesi"
    s.column_dimensions["A"].width = 62
    for lettera in "BCDE":
        s.column_dimensions[lettera].width = 20

    def titolo(testo):
        s.append([])
        s.append([testo])
        s.cell(row=s.max_row, column=1).font = grassetto

    s.append([f"Confronto gestionale / prototipo, competenza {mese}"])
    s["A1"].font = Font(bold=True, size=14)
    s.append(["Data di pagamento usata (valuta)", valuta.isoformat()])
    s.append(["Cedolini letti", len(cedolini)])
    s.append(["Dipendenti portati al calcolo", len(giro.calcolati)])
    s.append(["Dipendenti fuori dal primo giro", len(giro.esclusi)])
    fermi = [r for r in giro.calcolati.values() if r.fermo]
    s.append(["Dipendenti su cui il nucleo si ferma", len(fermi)])

    titolo("Esito per voce (solo le voci calcolate dal nucleo)")
    s.append(["Voce", "uguali", "diverse", "manca da un lato", "somma delle differenze"])
    for cella in s[s.max_row]:
        cella.font, cella.fill = grassetto, testata
    voci: dict[tuple[str, str], list[Riga]] = {}
    for riga in righe:
        if riga.origine == "calcolato":
            voci.setdefault((riga.gruppo, riga.voce), []).append(riga)
    for (gruppo, voce), gruppo_righe in voci.items():
        somma = sum((r.differenza for r in gruppo_righe if r.differenza is not None), ZERO)
        s.append([
            f"{gruppo}: {voce}",
            sum(1 for r in gruppo_righe if r.esito == "uguale"),
            sum(1 for r in gruppo_righe if r.esito == "diverso"),
            sum(1 for r in gruppo_righe if r.esito == "manca da un lato"),
            float(somma),
        ])
        s.cell(row=s.max_row, column=5).number_format = "#,##0.00"

    titolo("Stipendio tabellare: corpus e gestionale")
    s.append(["Area", "annuo nel corpus", "annuo dai cedolini", "mensile corpus", "mensile cedolini"])
    for cella in s[s.max_row]:
        cella.font, cella.fill = grassetto, testata
    for area, (corpus, usato) in giro.tabellari.items():
        s.append([area, float(corpus), float(usato), float(round(corpus / 12, 2)), float(round(usato / 12, 2))])
    s.append([
        "Il corpus ha solo il tabellare del CCNL 28/10/2026 con decorrenza 01/01/2026. Il gestionale paga ottobre con il tabellare "
        "precedente piu' la vacanza contrattuale. "
        + ("Per confrontare contributi, fisco e netto sullo stesso lordo, il calcolo usa il tabellare dei cedolini."
           if tabellare == "gestionale" else "Il calcolo usa il tabellare del corpus: lordo, contributi, fisco e netto differiscono di conseguenza.")
    ])

    titolo("Cosa NON e' calcolato dal nucleo in questo confronto")
    for testo in (
        "Voci fisse lette dal cedolino e trattate come misura mensile da atto: " + ", ".join(i.voce for i in A.ISTITUTI_LETTI),
        "Concorso di queste voci alle basi (CPDEL, Fondo credito, TFS, TFR ulteriori, IRAP): come osservato sul gestionale, non letto sulla norma",
        "Assenze (malattia, congedo parentale): nessuna regola nel corpus; le righe interessate portano la nota",
        "Addizionali regionale e comunale: le aliquote dei comuni di domicilio non sono nel corpus; tolte dal netto confrontato",
        "Trattenute a terzi (sindacato, cessioni, deleghe, pignoramento) e riscatti: tolti dal netto confrontato",
        "Carichi di famiglia: l'estrazione anagrafica non ha i familiari; tolti dall'IRPEF confrontata",
        "Mese isolato: il registro non ha i pagamenti da gennaio a settembre; ogni rapporto parte dal primo giorno del mese",
        "ListaPosPA, DMA2, F24EP e proposta contabile: non ancora confrontati (il giro si ferma alla versione di proposta)",
        "Amministratori (ente 9): non ancora nel confronto",
    ):
        s.append([testo])

    titolo("Dipendenti fuori dal primo giro")
    for matricola, motivo in giro.esclusi.items():
        s.append([f"{matricola} {per_matricola[matricola].nominativo}", motivo])
    if fermi:
        titolo("Fermi del nucleo")
        for r in fermi:
            s.append([f"{r.matricola} {per_matricola[r.matricola].nominativo}", r.fermo])
    avvisi = sorted({testo.split(":")[0] for testo in giro.fermi_versione})
    if avvisi:
        titolo("Avvisi e dati mancanti della versione di proposta")
        for testo in avvisi:
            s.append([testo, sum(1 for t in giro.fermi_versione if t.startswith(testo))])

    # Persone
    p = libro.create_sheet("Persone")
    intesta(
        p,
        ["Matricola", "Nominativo", "Area", "Regime fine servizio", "Voci uguali", "Voci diverse", "Netto gestionale*", "Netto prototipo*", "Differenza", "Note"],
        [10, 30, 8, 10, 10, 10, 16, 16, 12, 110],
    )
    for matricola, r in giro.calcolati.items():
        c = per_matricola[matricola]
        sue = [x for x in righe if x.matricola == matricola]
        netto = next((x for x in sue if x.gruppo == "Netto"), None)
        p.append([
            matricola, c.nominativo, c.area, {"3": "TFS", "1": "TFR"}[REGIMI[anagrafiche[matricola]["tab.ritenute"]]],
            sum(1 for x in sue if x.esito == "uguale"), sum(1 for x in sue if x.esito == "diverso"),
            float(netto.gestionale) if netto and netto.gestionale is not None else None,
            float(netto.prototipo) if netto and netto.prototipo is not None else None,
            float(netto.differenza) if netto and netto.differenza is not None else None,
            "; ".join(([f"FERMO: {r.fermo}"] if r.fermo else []) + _note_persona(c)),
        ])
        for colonna in (7, 8, 9):
            p.cell(row=p.max_row, column=colonna).number_format = "#,##0.00"
    p.append([])
    p.append(["* netto prima delle addizionali e delle trattenute a terzi"])

    # Confronto
    f = libro.create_sheet("Confronto")
    intesta(
        f, ["Matricola", "Nominativo", "Gruppo", "Voce", "Gestionale", "Prototipo", "Differenza", "Esito", "Origine nel prototipo", "Nota"],
        [10, 30, 22, 44, 14, 14, 12, 18, 22, 120],
    )
    for riga in righe:
        f.append([
            riga.matricola, riga.nominativo, riga.gruppo, riga.voce,
            float(riga.gestionale) if riga.gestionale is not None else None,
            float(riga.prototipo) if riga.prototipo is not None else None,
            float(riga.differenza) if riga.differenza is not None else None,
            riga.esito, riga.origine, riga.nota,
        ])
        n = f.max_row
        for colonna in (5, 6, 7):
            f.cell(row=n, column=colonna).number_format = "#,##0.00"
        f.cell(row=n, column=8).fill = PatternFill("solid", fgColor=colori[riga.esito])
        f.cell(row=n, column=10).alignment = Alignment(wrap_text=False)
    f.auto_filter.ref = f"A1:J{f.max_row}"

    # IRPEF: la differenza scomposta
    i = libro.create_sheet("IRPEF")
    intesta(
        i,
        ["Matricola", "Nominativo", "Imponibile gest.", "Imponibile prot.", "Lorda gest.", "Lorda prot.", "Detr. lavoro gest.", "Detr. lavoro prot.",
         "Ulteriore detr. gest.", "Ulteriore detr. prot.", "Carichi gest.", "Netta gest.", "Ritenuta prot.", "Differenza senza carichi",
         "Reddito annuo gest. (implicito)", "Reddito annuo prot.", "Mensilita' implicite", "Imponibile anno prima (anagrafica)",
         "Ricostruzione quadra col nucleo", "Cause"],
        [10, 30, 13, 13, 11, 11, 13, 13, 13, 13, 11, 11, 12, 13, 16, 14, 12, 16, 14, 150],
    )
    for x in fiscali:
        i.append([
            x.matricola, x.nominativo, *map(float, (
                x.imponibile_gestionale, x.imponibile_prototipo, x.lorda_gestionale, x.lorda_prototipo, x.lavoro_gestionale, x.lavoro_prototipo,
                x.ulteriore_gestionale, x.ulteriore_prototipo, x.carichi_gestionale, x.netta_gestionale, x.ritenuta_prototipo,
                x.ritenuta_prototipo - x.netta_gestionale - x.carichi_gestionale,
            )),
            float(x.reddito_gestionale) if x.reddito_gestionale is not None else None, float(x.reddito_prototipo),
            float(x.mensilita) if x.mensilita is not None else None, x.reddito_anno_prima, "si'" if x.quadra else "NO", x.cause(),
        ])
        for colonna in range(3, 17):
            i.cell(row=i.max_row, column=colonna).number_format = "#,##0.00"
    i.append([])
    for testo in (
        "Le componenti del prototipo sono ricostruite dalle formule del corpus e controllate contro la ritenuta del nucleo (colonna «quadra»).",
        "Il reddito annuo del gestionale non e' nei file: e' quello per cui la detrazione di lavoro dell'art. 13, rapportata ai giorni del mese, da' l'importo del cedolino.",
        "I carichi di famiglia del gestionale sono tolti dalla differenza: l'estrazione anagrafica non ha i familiari.",
    ):
        i.append([testo])

    percorso.parent.mkdir(parents=True, exist_ok=True)
    libro.save(percorso)


def main() -> None:
    analisi = argparse.ArgumentParser(prog="python -m prove.confronto", description=__doc__.splitlines()[0])
    analisi.add_argument("cartella", type=Path, help="cartella dell'ente, fuori dal repo")
    analisi.add_argument("--mese", default="2026-10")
    analisi.add_argument("--valuta", default=None, help="data di pagamento degli stipendi (AAAA-MM-GG); senza, il 27 del mese")
    analisi.add_argument("--tabellare", choices=("gestionale", "corpus"), default="gestionale")
    analisi.add_argument("--ente", default="1", help="codice dell'ente nel gestionale (1 dipendenti)")
    opzioni = analisi.parse_args()

    mese = Mese.da_testo(opzioni.mese)
    valuta = date.fromisoformat(opzioni.valuta) if opzioni.valuta else date(mese.anno, mese.mese, 27)
    gestionale = opzioni.cartella / "gestionale"
    cedolini = [c for c in leggi_cedolini(next(gestionale.glob(f"E{opzioni.ente} *edolini*.PDF"))) if c.ente == opzioni.ente]
    anagrafiche = {
        a.matricola: a
        for archivio in sorted((opzioni.cartella / "anagrafiche").glob("*.xls"))
        for a in leggi_anagrafiche(archivio)
        if a.ente == opzioni.ente
    }
    scritture = [s for s in leggi_scritture_f24(next(gestionale.glob("F24EP scritture*.CSV"))) if s.ente == opzioni.ente]

    # Estrazione voci dell'anno: il pagato dei mesi prima per la proiezione del reddito annuo (ADR 0039). Senza, mese isolato.
    estrazione = gestionale / "Estrazione voci.xls"
    pregressi = leggi_imponibili_irpef(estrazione, mese.anno) if estrazione.exists() else None
    giro = gira(cedolini, anagrafiche, mese, valuta, opzioni.tabellare, pregressi)
    per_matricola = {c.matricola: c for c in cedolini}
    righe = [
        riga
        for matricola, risultato in giro.calcolati.items()
        if not risultato.fermo
        for riga in righe_di_confronto(per_matricola[matricola], anagrafiche[matricola], risultato, scritture)
    ]
    parametri = irpef.parametri(valuta)
    fiscali = [
        x
        for matricola, risultato in giro.calcolati.items()
        if not risultato.fermo
        for x in [irpef.scomponi(parametri, per_matricola[matricola], risultato, anagrafiche[matricola], (mese.ultimo_giorno - mese.primo_giorno).days + 1)]
        if x is not None
    ]
    uscita = opzioni.cartella / "confronto" / f"confronto-{mese}-tabellare-{opzioni.tabellare}.xlsx"
    _scrivi(uscita, mese, valuta, opzioni.tabellare, cedolini, anagrafiche, giro, righe, fiscali)

    calcolate = [r for r in righe if r.origine == "calcolato"]
    print(f"cedolini {len(cedolini)}, al calcolo {len(giro.calcolati)}, fuori dal primo giro {len(giro.esclusi)}")
    print(f"voci calcolate {len(calcolate)}: uguali {sum(1 for r in calcolate if r.esito == 'uguale')}, "
          f"diverse {sum(1 for r in calcolate if r.esito == 'diverso')}, manca da un lato {sum(1 for r in calcolate if r.esito == 'manca da un lato')}")
    print(f"scritto {uscita}")


if __name__ == "__main__":
    main()
