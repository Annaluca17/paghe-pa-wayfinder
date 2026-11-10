"""Il resoconto del mese di prova, in Markdown e deterministico: nessun istante reale, nessun percorso assoluto."""

from __future__ import annotations

import re
from collections import Counter

from paghe import Mese

from . import scenario as S
from .percorso import (
    CATEGORIE,
    CONSEGUENZA,
    NOMI_CATEGORIE,
    NOMI_PASSI,
    PASSI,
    Esecuzione,
    Fermo,
    Passo,
)

MESI = {"2026-03": "Marzo 2026", "2026-12": "Dicembre 2026 (conguaglio)"}
COLONNE = (("avvio", "Avvio"), ("2026-02", "Preparazione di febbraio"), ("2026-03", "Marzo"), ("2026-12", "Dicembre"))


def _elenco(voci: list[str], rientro: str = "  ") -> list[str]:
    return [f"{rientro}- {voce}" for voce in voci]


def _passo(passo: Passo) -> list[str]:
    righe = [f"**{NOMI_PASSI[passo.nome]}**", ""]
    if not (passo.riuscito or passo.fermi or passo.fittizio):
        righe.append("- Non eseguito in questa prova:")
        righe += _elenco(passo.note)
        righe.append("")
        return righe
    righe.append("- Riuscito:" if passo.riuscito else "- Riuscito: niente")
    righe += _elenco(passo.riuscito)
    if passo.fermi:
        righe.append("- Fermi:")
        raggruppati: dict[tuple, list[Fermo]] = {}
        for fermo in passo.fermi:
            raggruppati.setdefault((fermo.causa, fermo.dettaglio if fermo.causa == CONSEGUENZA else ""), []).append(fermo)
        for fermo in passo.fermi:
            if fermo.causa == CONSEGUENZA:
                righe.append(f"  - {', '.join(fermo.rapporti)}: non eseguito, la delega del mese non e' trasmessa")
            else:
                chi = ", ".join(fermo.rapporti)
                caso = f" ({fermo.caso})" if fermo.caso and fermo.caso not in fermo.causa else ""
                dettaglio = re.sub(r"^Rapporto R\d+( \([^)]*\))?: ", "", fermo.dettaglio)
                righe.append(f"  - {chi}{caso}: {dettaglio}")
    else:
        righe.append("- Fermi: nessuno")
    righe.append("- Su dati fittizi:")
    righe += _elenco(passo.fittizio)
    if passo.note:
        righe.append("- Note:")
        righe += _elenco(passo.note)
    righe.append("")
    return righe


def _corpus(esecuzione: Esecuzione) -> list[str]:
    reale, unione = esecuzione.corpus_reale_voci, esecuzione.corpus_fittizio_voci
    nomi = [
        ("istituti", "istituti con regola"),
        ("basi", "basi imponibili"),
        ("fermi", "fermi dichiarati"),
        ("categorie_reddito", "categorie di reddito"),
        ("ritenute", "regole di ritenuta"),
        ("conguagli", "regole di conguaglio"),
        ("pagamenti_fisiologici", "dichiarazioni di pagamento fisiologico"),
        ("composizioni", "dichiarazioni di composizione"),
        ("mappature", "mappature verso codici esterni"),
        ("codici_f24ep", "codici nel catalogo F24EP"),
        ("scadenze_f24ep", "regole di scadenza F24EP"),
        ("calendari_festivi", "calendari dei festivi"),
    ]
    righe = ["| Voce | Corpus reale | Aggiunta fittizia | Unione usata |", "|---|---:|---:|---:|"]
    for chiave, nome in nomi:
        righe.append(f"| {nome} | {reale[chiave]} | {unione[chiave] - reale[chiave]} | {unione[chiave]} |")
    return righe


def _scenario() -> list[str]:
    righe = ["| Rapporto | Titolo | Area | Regime di fine servizio | Caso |", "|---|---|---|---|---|"]
    for r in S.RAPPORTI:
        righe.append(f"| {r.id} | {r.titolo} | {r.area or '-'} | {r.regime or '-'} | {r.caso} |")
    return righe


def _mappa(esecuzione: Esecuzione) -> list[str]:
    righe = ["| Rapporto | Marzo 2026 | Dicembre 2026 |", "|---|---|---|"]
    fermi = {(f.mese, r, f.passo): f for f in esecuzione.fermi if f.causa != CONSEGUENZA for r in f.chi_blocca()}

    def stato(mese: str, rapporto: str) -> str:
        arrivo = esecuzione.arrivi[(mese, rapporto)]
        if arrivo == "completo":
            return "completo, fino all'esito versato" if mese == "2026-03" else "completo, fino al pagamento e alla ListaPosPA"
        if arrivo == "fuori servizio":
            return "fuori servizio"
        causa = next((f.causa for (m, r, p), f in sorted(fermi.items()) if (m, r) == (mese, rapporto) and p == arrivo), "")
        return f"si ferma al passo «{NOMI_PASSI[arrivo]}»: {causa}"

    for r in S.RAPPORTI:
        righe.append(f"| {r.id} | {stato('2026-03', r.id)} | {stato('2026-12', r.id)} |")
    return righe


def _chi(descrizione: str) -> str:
    if descrizione.startswith("ente"):
        return "ente"
    for prefisso in ("persona P", "rapporto R"):
        if descrizione.startswith(prefisso):
            return "R" + descrizione[len(prefisso): len(prefisso) + 2]
    return "ente"


def _passaggi(esecuzione: Esecuzione) -> list[str]:
    conteggi = Counter((p.categoria, p.quando) for p in esecuzione.passaggi)
    righe = ["| Categoria | " + " | ".join(nome for _, nome in COLONNE) + " |", "|---|" + "---:|" * len(COLONNE)]
    for categoria in CATEGORIE:
        celle = [str(conteggi.get((categoria, quando), 0)) for quando, _ in COLONNE]
        righe.append(f"| {NOMI_CATEGORIE[categoria]} | " + " | ".join(celle) + " |")
    dati = [c for c in CATEGORIE if c != "comando"]
    totali = [str(sum(conteggi.get((c, quando), 0) for c in dati)) for quando, _ in COLONNE]
    righe.append("| **Totale senza i comandi** | " + " | ".join(f"**{t}**" for t in totali) + " |")
    righe.append("")
    righe.append(
        "La preparazione di febbraio e' il pagamento che precede il mese, scritto solo perche' l'arretrato di R02 e' una "
        "differenza rispetto a un esito pagato: non fa parte del mese e non e' nel totale di marzo."
    )
    righe.append("")
    avvio = Counter(_chi(p.descrizione) for p in esecuzione.passaggi if p.categoria == "avvio" and p.quando == "avvio")
    righe.append("Fatti di avvio per soggetto: " + ", ".join(f"{chi} {n}" for chi, n in sorted(avvio.items())) + ".")
    assunzione = Counter(_chi(p.descrizione) for p in esecuzione.passaggi if p.categoria == "avvio" and p.quando == "2026-03")
    righe.append(
        "Assunzione di marzo (avvio di un rapporto nuovo): " + ", ".join(f"{chi} {n}" for chi, n in sorted(assunzione.items())) + "."
    )
    for quando, titolo in (("2026-03", "Marzo"), ("2026-12", "Dicembre")):
        righe.append("")
        righe.append(f"Dettaglio di {titolo}, escluso l'avvio:")
        righe.append("")
        voci = Counter((p.categoria, p.descrizione) for p in esecuzione.passaggi if p.quando == quando and p.categoria != "avvio")
        ordine = {c: i for i, c in enumerate(CATEGORIE)}
        for (categoria, descrizione), n in sorted(voci.items(), key=lambda kv: (ordine[kv[0][0]], kv[0][1])):
            righe.append(f"- [{categoria}] {n} x {descrizione}")
    righe.append("")
    cessazione = sum(1 for p in esecuzione.passaggi if p.quando == "2026-03" and p.categoria == "ricorrente" and "R05" in p.descrizione)
    righe.append(
        f"Nota: la cessazione di R05 costa {cessazione} scritture a mano. Il nucleo non ha un fatto di cessazione: i fatti "
        "sono immutabili e il servizio di un rapporto finisce solo se si annullano i sei fatti di inquadramento aperti e "
        "si riscrivono con una fine (piu' il codice di cessazione)."
    )
    return righe


def cause_ordinate(esecuzione: Esecuzione) -> list[dict]:
    """I fermi raggruppati per causa, ordinati per quanti rapporti bloccano e poi per quanti passi."""
    gruppi: dict[str, dict] = {}
    visti: set[tuple] = set()
    for fermo in esecuzione.fermi:
        if fermo.causa == CONSEGUENZA:
            continue
        gruppo = gruppi.setdefault(fermo.causa, {"bloccati": set(), "passi": 0, "casi": {}, "mesi": set(), "passo": fermo.passo})
        gruppo["mesi"].add(fermo.mese)
        for rapporto in fermo.chi_blocca():
            if (fermo.causa, fermo.mese, rapporto, fermo.passo) in visti:
                continue
            visti.add((fermo.causa, fermo.mese, rapporto, fermo.passo))
            gruppo["bloccati"].add(rapporto)
            # Il prospetto paga e' una vista a lato: il suo fermo chiude solo se' stesso, non i passi dopo.
            gruppo["passi"] += 1 if fermo.passo == "prospetto_paga" else len(PASSI) - PASSI.index(fermo.passo)
        for rapporto in fermo.rapporti:
            gruppo["casi"].setdefault(rapporto, fermo.caso)
    elenco = [{"causa": causa, **gruppo} for causa, gruppo in gruppi.items()]
    return sorted(elenco, key=lambda g: (-len(g["bloccati"]), -g["passi"], g["causa"]))


def _cosa_manca(esecuzione: Esecuzione) -> list[str]:
    righe = [
        "I fermi del mese, raggruppati per causa. L'ordine e' per quanti rapporti bloccano e poi per quanti passi del "
        "percorso (calcolo, versione, conferma, pagamento, prospetto paga, denuncia, ListaPosPA, lista collaboratori, delega, file, ricevute, esito versato) "
        "restano chiusi, sommati su marzo e dicembre.",
        "",
    ]
    for numero, gruppo in enumerate(cause_ordinate(esecuzione), start=1):
        mesi = " e ".join(MESI[m].split(" ")[0].lower() for m in sorted(gruppo["mesi"]))
        casi = ", ".join(
            f"{rapporto} ({caso})" if caso and caso not in gruppo["causa"] else rapporto
            for rapporto, caso in sorted(gruppo["casi"].items())
        )
        righe.append(
            f"{numero}. **{gruppo['causa']}**: {len(gruppo['bloccati'])} "
            f"{'rapporto bloccato' if len(gruppo['bloccati']) == 1 else 'rapporti bloccati'}, {gruppo['passi']} passi, "
            f"al passo «{NOMI_PASSI[gruppo['passo']]}», in {mesi}. Casi: {casi}."
        )
    if len(righe) == 2:
        righe.append("Nessun fermo.")
    return righe


def _difetti(esecuzione: Esecuzione) -> list[str]:
    if not esecuzione.difetti:
        return ["Nessuno trovato."]
    righe = []
    for numero, difetto in enumerate(esecuzione.difetti, start=1):
        righe.append(f"{numero}. **{difetto.titolo}.** {difetto.esempio}")
    return righe


def _non_esercitato(esecuzione: Esecuzione) -> list[str]:
    istituti = esecuzione.corpus.istituti()
    voci = []
    if not any("tredicesima" in i for i in istituti):
        voci.append(
            "La tredicesima non e' un istituto del corpus: il pagamento di dicembre non la contiene, anche se il tabellare "
            "annuo del corpus e' per dodici mensilita' piu' la tredicesima."
        )
    voci.append(
        "Le addizionali regionale e comunale sono calcolate al conguaglio di dicembre sul domicilio fiscale delle persone "
        "(comune e regione di fantasia) e trattenute a rate dal 2027: nel mese di prova si vede solo l'acconto comunale di "
        "R01, che ha il reddito 2025 dalla CU (le rate del saldo, la cessazione e la restituzione a credito sono nei test). "
        "Per le altre persone, senza conguaglio 2025 ne' CU, niente acconto e un avviso. 381E, 384E, 385E, 160E e 161E "
        "hanno nel catalogo fittizio una forma assunta, da verificare."
    )
    if esecuzione.uno_per_cento:
        voci.append("Il contributo aggiuntivo dell'1% scatta in almeno un quadro, e non ha una causale nel catalogo.")
    else:
        voci.append(
            "Il contributo aggiuntivo dell'1% non scatta in nessun quadro del mese (nessun rapporto supera la prima "
            "fascia) e non ha una causale nel catalogo: se scattasse, la delega si fermerebbe per mappatura mancante "
            "(la ricerca non trova una causale dedicata)."
        )
    voci.append(
        "L'acconto IRAP e' calcolato all'8,5% sulla base di ogni pagamento e versato col 380E, una riga per regione. Nessun "
        "rapporto del mese ha una sede di lavoro: vale la regione dell'ente, un fatto dell'ente. Il codice regione e' del corpus "
        "reale, da riscontrare sulla tabella AdE. Comando e convenzione: l'IRAP segue l'ente che utilizza il dipendente, sul "
        "rimborso versato; i rimborsi tra enti non sono modellati (la convenzione di segreteria ferma gia' il calcolo del "
        "rapporto)."
    )
    return [f"- {v}" for v in voci]


def scrivi(esecuzione: Esecuzione) -> str:
    righe = [
        "# Mese di prova: resoconto",
        "",
        "> **Dati e corpus fittizi.** Ente, persone, codici fiscali, IBAN e atti sono di fantasia; nessun valore di "
        "questo resoconto e' un importo vero. Il percorso gira su un corpus **non reale**: l'unione del corpus reale "
        "(`corpus/funzioni-locali-cpdel.toml`, che non cambia) e di un'aggiunta fittizia "
        "(`prove/mese_di_prova/corpus_fittizio.toml`, tutti i riferimenti `fittizio:`). Il corpus reale rifiuta i "
        "riferimenti fittizi (ADR 0003): per questo l'unione si carica come corpus non reale.",
        "",
        "Il resoconto e' generato da `python -m prove.mese_di_prova` e fissato da `tests/test_mese_di_prova.py`: ogni "
        "ticket futuro lo cambia nel punto che sblocca.",
        "",
        "## Corpus",
        "",
        *_corpus(esecuzione),
        "",
        "## Scenario",
        "",
        f"Ente fittizio in una sola regione, con i fatti sull'ente della delega (codice fiscale, denominazione, e-mail, "
        f"IBAN di tesoreria, sigla di provincia) e l'ultimo pagamento del 2026 al {S.ULTIMO_PAGAMENTO_2026}. "
        "Mese: marzo 2026, piu' dicembre 2026 per il conguaglio. Dodici rapporti, ognuno per un caso:",
        "",
        *_scenario(),
        "",
        "## Dove arriva ogni rapporto",
        "",
        *_mappa(esecuzione),
        "",
        "## Cosa manca per un mese completo",
        "",
        *_cosa_manca(esecuzione),
        "",
        "## Passaggi manuali",
        "",
        *_passaggi(esecuzione),
        "",
        "## Il percorso, passo per passo",
        "",
    ]
    for tag in ("2026-03", "2026-12"):
        righe += [f"### {MESI[tag]}", ""]
        for passo in (p for p in esecuzione.passi if p.mese == tag):
            righe += _passo(passo)
    righe += ["## Difetti del nucleo trovati", "", *_difetti(esecuzione), ""]
    righe += ["## Non esercitato dal mese", "", *_non_esercitato(esecuzione), ""]
    righe += [
        "## File prodotti",
        "",
        *[f"- `{nome}`" for nome in sorted(esecuzione.file_prodotti)],
        "",
    ]
    return "\n".join(righe)
