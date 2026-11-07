"""Il percorso del mese di prova: dai fatti ai file, raccogliendo ogni fermo e ogni passaggio manuale.

Non c'e' nessuna regola qui. Dove il nucleo si ferma, il percorso registra il fermo, con il caso nominato e il
rapporto, e prosegue con i rapporti che possono proseguire. Le funzioni di comodo che il nucleo non ha (elencare i
rapporti, contare i passaggi manuali, ripetere un ciclo mensile, riconoscere la causa di un fermo) stanno in questo
file e non in `paghe/`.
"""

from __future__ import annotations

import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from paghe import (
    Corpus,
    Mese,
    Registro,
    TipoEsito,
    calcola,
    conferma_versione,
    costruisci_delega,
    differenze,
    emetti_versione,
    lista_pos_pa,
    registra_pagamento_eseguito,
    registra_ricevuta_delega,
    registra_versamento_delega,
    segnala_scostamento_contributi,
    situazione_delega,
    stato_delega,
    trasmetti_delega,
)
from paghe import delega as modulo_delega
from paghe.errori import ErrorePaghe, VistaFerma
from paghe.uniemens import Ente, Mittente, in_xml

from . import scenario as S
from .codici import codice_fiscale

RADICE = Path(__file__).resolve().parents[2]
CORPUS_REALE = RADICE / "corpus" / "funzioni-locali-cpdel.toml"
CORPUS_FITTIZIO = Path(__file__).resolve().parent / "corpus_fittizio.toml"
ADATTATORE = "adattatore-prova"
PREPARAZIONE = "2026-02"  # il pagamento che precede il mese, solo per l'arretrato: non fa parte del resoconto dei passi

# L'ordine dei passi del percorso, per contare quanti ne blocca un fermo.
PASSI = (
    "calcolo",
    "versione",
    "conferma",
    "pagamento",
    "denuncia",
    "lista_pos_pa",
    "delega",
    "file_telematico",
    "ricevute",
    "versato",
)
NOMI_PASSI = {
    "fatti": "Fatti",
    "calcolo": "Calcolo",
    "versione": "Versione di proposta",
    "conferma": "Conferma della Ragioneria",
    "pagamento": "Pagamento eseguito",
    "denuncia": "Denuncia",
    "lista_pos_pa": "ListaPosPA",
    "delega": "Delega F24EP",
    "file_telematico": "File telematico",
    "ricevute": "Ricevute della delega",
    "versato": "Esito versato",
}
CONSEGUENZA = "delega non trasmessa"  # i passi dopo una delega ferma: conseguenze, non cause


class Orologio:
    """Orologio fittizio: il tempo di registrazione e' sempre quello dello scenario, mai quello reale."""

    def __init__(self) -> None:
        self.ora = datetime(2026, 1, 12, 9, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.ora

    def vai(self, giorno: date, ore: int = 9) -> None:
        self.ora = datetime(giorno.year, giorno.month, giorno.day, ore, 0, tzinfo=UTC)

    def avanza(self) -> None:
        self.ora += timedelta(minutes=1)


# Passaggi manuali

CATEGORIE = ("avvio", "ricorrente", "conferma", "scelta", "evento", "comando")
NOMI_CATEGORIE = {
    "avvio": "Fatti di avvio, una tantum (anagrafica, assunzioni, inquadramento)",
    "ricorrente": "Fatti ricorrenti del mese (atti, variazioni, cessazioni, 730)",
    "conferma": "Conferme della Ragioneria",
    "scelta": "Scelte (valuta prevista, data di versamento, ultimo pagamento)",
    "evento": "Eventi che oggi nessun adattatore porta (pagamento, ricevute, versamento)",
    "comando": "Comandi di avvio (non sono dati: emissione, produzione dei file, trasmissione)",
}


@dataclass(frozen=True)
class Passaggio:
    categoria: str
    quando: str  # "avvio", "2026-02", "2026-03", "2026-12"
    descrizione: str


class Ufficio:
    """Le scritture dell'Ufficio personale sul registro, ognuna contata come un passaggio manuale."""

    def __init__(self, registro: Registro) -> None:
        self.registro = registro
        self.passaggi: list[Passaggio] = []
        self._categoria = "avvio"
        self._quando = "avvio"

    @contextmanager
    def fase(self, categoria: str, quando: str):
        precedente = (self._categoria, self._quando)
        self._categoria, self._quando = categoria, quando
        try:
            yield
        finally:
            self._categoria, self._quando = precedente

    def conta(self, categoria: str, quando: str, descrizione: str) -> None:
        self.passaggi.append(Passaggio(categoria, quando, descrizione))

    def _conta_fatto(self, descrizione: str) -> None:
        self.conta(self._categoria, self._quando, descrizione)

    def codice_persona(self, persona, tipo, valore, dal):
        self._conta_fatto(f"persona {persona}: {tipo}")
        return self.registro.registra_codice_persona(persona, tipo, valore, dal)

    def iban_persona(self, persona, iban, dal):
        self._conta_fatto(f"persona {persona}: iban")
        return self.registro.registra_iban_persona(persona, iban, dal)

    def dichiarazione_sostituito(self, persona, detrazioni, dal, atto):
        self._conta_fatto(f"persona {persona}: dichiarazione del sostituito")
        return self.registro.registra_dichiarazione_sostituito(persona, detrazioni, dal, None, atto)

    def collega(self, rapporto, persona, dal):
        self._conta_fatto(f"rapporto {rapporto}: legame con la persona")
        return self.registro.collega_rapporto(rapporto, persona, dal)

    def codice(self, rapporto, tipo, valore, dal, al=None, atto=None):
        self._conta_fatto(f"rapporto {rapporto}: {tipo}")
        return self.registro.registra_codice(rapporto, tipo, valore, dal, al, atto)

    def fatto(self, rapporto, tipo, valore, dal, al=None, atto=None):
        self._conta_fatto(f"rapporto {rapporto}: {tipo}")
        return self.registro.registra_fatto(rapporto, tipo, valore, dal, al, atto)

    def annulla(self, rapporto, fatto_id, tipo, motivo):
        self._conta_fatto(f"rapporto {rapporto}: annullamento di {tipo}")
        self.registro.annulla_fatto(fatto_id, motivo)

    def codice_ente(self, tipo, valore, dal):
        self._conta_fatto(f"ente: {tipo}")
        return self.registro.registra_codice_ente(tipo, valore, dal)

    def ultimo_pagamento(self, anno, data):
        self.conta("scelta", self._quando, f"ente: ultimo pagamento dell'anno {anno}")
        return self.registro.registra_ultimo_pagamento(anno, data)

    def data_versamento(self, mese, data):
        self.conta("scelta", self._quando, f"ente: data di versamento dei pagamenti di {mese}")
        return self.registro.registra_data_versamento(mese, data)


# Fermi, difetti e passi

@dataclass(frozen=True)
class Fermo:
    """Un punto in cui il percorso si ferma: il caso e' nominato, `rapporti` sono quelli che lo causano.

    `bloccati` sono i rapporti che non proseguono per questo fermo (di piu' dei `rapporti` se il fermo e' di una
    delega, che si trasmette tutta o niente).
    """

    mese: str
    passo: str
    rapporti: tuple[str, ...]
    causa: str
    dettaglio: str
    caso: str = ""
    bloccati: tuple[str, ...] = ()

    def chi_blocca(self) -> tuple[str, ...]:
        return self.bloccati or self.rapporti


@dataclass(frozen=True)
class Difetto:
    """Qualcosa che il nucleo fa e non dovrebbe, o non fa e dovrebbe, trovato mentre il mese girava."""

    titolo: str
    esempio: str


@dataclass
class Passo:
    mese: str
    nome: str
    riuscito: list[str] = field(default_factory=list)
    fermi: list[Fermo] = field(default_factory=list)
    fittizio: list[str] = field(default_factory=list)
    note: list[str] = field(default_factory=list)


@dataclass
class Esecuzione:
    corpus_reale_voci: dict
    corpus_fittizio_voci: dict
    passi: list[Passo] = field(default_factory=list)
    passaggi: list[Passaggio] = field(default_factory=list)
    difetti: list[Difetto] = field(default_factory=list)
    file_prodotti: list[str] = field(default_factory=list)
    uno_per_cento: bool = False  # almeno un quadro porta il contributo aggiuntivo dell'1%
    arrivi: dict = field(default_factory=dict)  # (mese, rapporto) -> passo in cui il rapporto si ferma, o "completo"
    registro: Registro | None = None
    corpus: Corpus | None = None

    @property
    def fermi(self) -> list[Fermo]:
        return [fermo for passo in self.passi for fermo in passo.fermi]

    def difetto(self, titolo: str, esempio: str) -> None:
        if all(d.titolo != titolo for d in self.difetti):
            self.difetti.append(Difetto(titolo, esempio))


def causa_di(testo: str) -> str:
    """La causa di un fermo senza i dettagli variabili (rapporto, istituto, date): serve a raggruppare."""
    if "caso non modellato, " in testo:
        testo = testo.split("caso non modellato, ", 1)[1]
    testo = re.sub(r"\s*\(.*", "", testo)
    testo = re.sub(r"\b(Rapporto|Persona|rapporto|persona) [A-Z]\d+\b:? ?", "", testo)
    testo = re.sub(r"\bIstituto \w+:? ?", "", testo)
    testo = re.sub(r"\b\d{4}-\d{2}-\d{2}(/\d{4}-\d{2}-\d{2})?\b", "<data>", testo)
    testo = re.sub(r"\bnetto negativo di -?[\d.]+", "netto negativo", testo)
    return testo.strip(" :,.")


def _soldi(valore: Decimal) -> str:
    return f"{valore:.2f}"


def _voci(corpus: Corpus) -> dict:
    fiscale = corpus.fiscale
    return {
        "istituti": len(corpus.istituti()),
        "basi": len(corpus.basi()),
        "fermi": len(corpus.fermi),
        "categorie_reddito": len(fiscale.categorie),
        "ritenute": len(fiscale.ritenute),
        "conguagli": len(fiscale.conguagli),
        "pagamenti_fisiologici": len(fiscale.fisiologici),
        "composizioni": len(corpus._composizioni),
        "mappature": len(corpus._mappature),
        "codici_f24ep": len(corpus._codici_f24ep),
        "scadenze_f24ep": len(corpus._scadenze_f24ep),
        "calendari_festivi": len(corpus._calendari_festivi),
    }


# Il percorso

class _Contesto:
    def __init__(self, uscita: Path | None) -> None:
        reale = CORPUS_REALE.read_text(encoding="utf-8")
        fittizio = CORPUS_FITTIZIO.read_text(encoding="utf-8")
        # Il corpus reale rifiuta i riferimenti `fittizio:`: l'unione e' un corpus NON reale (ADR 0003).
        self.corpus = Corpus.da_toml(reale + "\n" + fittizio, reale=False)
        solo_reale = Corpus.da_toml(reale, reale=True)
        self.orologio = Orologio()
        self.registro = Registro(orologio=self.orologio)
        self.ufficio = Ufficio(self.registro)
        self.uscita = uscita
        self.esecuzione = Esecuzione(_voci(solo_reale), _voci(self.corpus))

    def vai(self, giorno: date) -> None:
        self.orologio.vai(giorno)

    def passo(self, tag: str, nome: str) -> Passo:
        passo = Passo(tag, nome)
        if tag != PREPARAZIONE:
            self.esecuzione.passi.append(passo)
        return passo

    def comando(self, quando: str, descrizione: str) -> None:
        self.ufficio.conta("comando", quando, descrizione)

    def scrivi(self, nome: str, contenuto: bytes | str) -> str:
        if self.uscita is not None:
            self.uscita.mkdir(parents=True, exist_ok=True)
            dati = contenuto.encode("utf-8") if isinstance(contenuto, str) else contenuto
            (self.uscita / nome).write_bytes(dati)
        self.esecuzione.file_prodotti.append(nome)
        return nome


# Fatti

def _registra_ente(c: _Contesto) -> None:
    for tipo, valore in (
        ("codice_fiscale", S.CF_ENTE),
        ("denominazione", S.DENOMINAZIONE_ENTE),
        ("email", S.EMAIL_ENTE),
        ("iban_tesoreria", S.IBAN_TESORERIA),
        ("sigla_provincia", S.SIGLA_PROVINCIA),
    ):
        c.ufficio.codice_ente(tipo, valore, date(2026, 1, 1))


def _registra_rapporto(c: _Contesto, r: S.Rapporto) -> dict[str, object]:
    """Anagrafica e inquadramento di un rapporto. Per i titoli senza regime c'e' solo il compenso: nessun lettore."""
    u = c.ufficio
    u.codice_persona(r.persona, "codice_fiscale", r.cf, r.nascita)
    u.codice_persona(r.persona, "cognome", r.cognome, r.nascita)
    u.codice_persona(r.persona, "nome", r.nome, r.nascita)
    u.iban_persona(r.persona, S.IBAN_PERSONE, date(2026, 1, 1))
    if r.comparto and r.detrazioni:
        u.dichiarazione_sostituito(r.persona, "lavoro_dipendente", date(2026, 1, 1), S.ATTO_DETRAZIONI)
    u.collega(r.id, r.persona, r.dal)
    fatti: dict[str, object] = {}
    if r.comparto:
        u.codice(r.id, "comune_sede_lavoro", S.COMUNE_SEDE, r.dal)
        u.codice(r.id, "cap_sede_lavoro", S.CAP_SEDE, r.dal)
        for tipo, valore in S.fatti_inquadramento(r).items():
            fatti[tipo] = u.codice(r.id, tipo, valore, r.dal, r.al)
    else:
        u.fatto(r.id, "compenso_mensile", S.COMPENSI_SENZA_REGIME[r.id], r.dal)
    return fatti


def _fatti_di_avvio(c: _Contesto) -> dict[str, dict[str, object]]:
    c.vai(date(2026, 1, 12))
    fatti = {}
    with c.ufficio.fase("avvio", "avvio"):
        _registra_ente(c)
        for r in S.RAPPORTI:
            if r.id == "R06":
                continue  # assunto a marzo
            fatti[r.id] = _registra_rapporto(c, r)
        c.ufficio.fatto("R04", "part_time", S.PART_TIME_PERCENTUALE, date(2026, 1, 1))
    return fatti


# Un ciclo mensile

def _fuori_servizio(r: S.Rapporto, mese: Mese) -> bool:
    return (r.al is not None and r.al < mese.primo_giorno) or r.dal > mese.ultimo_giorno


def _importi_del_mese(c: _Contesto, mese: Mese, tag: str, passo: Passo, arrivi: dict) -> dict[str, list]:
    """Il calcolo di ogni rapporto: un errore del nucleo ferma quel rapporto e non gli altri."""
    reg, corpus = c.registro, c.corpus
    importi: dict[str, list] = {}
    for r in S.RAPPORTI:
        dettagli: list[str] = []
        try:
            righe = list(calcola(reg, corpus, r.id, mese))
            if tag == "2026-03" and r.id == "R02":
                arretrato = [d.importo() for d in differenze(reg, corpus, r.id, S.FEBBRAIO, TipoEsito.PAGATO)]
                righe += arretrato
                dettagli.append(
                    f"arretrato su febbraio, differenza rispetto all'esito pagato: {len(arretrato)} righe, netto "
                    f"{_soldi(sum((i.valore for i in arretrato), Decimal(0)))}"
                )
            if tag == "2026-03" and r.id == "R03":
                performance = [i for i in calcola(reg, corpus, r.id, Mese(2025, 12)) if i.istituto == "performance"]
                righe += performance
                dettagli.append(
                    f"performance di competenza {performance[0].periodo.dal.year}: {_soldi(performance[0].valore)}, "
                    "pagamento fisiologico dichiarato dal corpus fittizio"
                )
        except ErrorePaghe as errore:
            passo.fermi.append(Fermo(tag, "calcolo", (r.id,), causa_di(str(errore)), str(errore), caso=causa_di(str(errore))))
            arrivi[r.id] = "calcolo"
            continue
        if not righe and r.comparto and _fuori_servizio(r, mese):
            passo.note.append(f"{r.id}: non in servizio nel mese, nessun importo")
            arrivi[r.id] = "fuori servizio"
            continue
        if not righe:
            passo.fermi.append(
                Fermo(
                    tag,
                    "calcolo",
                    (r.id,),
                    "regime del titolo assente nel corpus",
                    f"Rapporto {r.id} ({r.titolo}): nessun importo; il fatto compenso_mensile registrato dall'Ufficio "
                    "personale non e' letto da nessuna regola del corpus",
                    caso=r.titolo,
                )
            )
            arrivi[r.id] = "calcolo"
            continue
        importi[r.id] = righe
        lordo = sum((i.valore for i in righe if i.derivazione.maturazione not in ("periodo", "mese", "cassa")), Decimal(0))
        passo.riuscito.append(f"{r.id}: {len(righe)} importi, lordo {_soldi(lordo)}")
        passo.riuscito.extend(f"{r.id}: {dettaglio}" for dettaglio in dettagli)
    fittizi = sorted({i.istituto for righe in importi.values() for i in righe if "fittizio:" in i.derivazione.riferimento})
    passo.fittizio.append(
        "tabelle e parametri del corpus reale"
        + (f"; regole del corpus fittizio per: {', '.join(fittizi)}" if fittizi else "")
    )
    return importi


def _controlla_fiscale(c: _Contesto, versione) -> None:
    """Confronta cio' che la ritenuta legge con cio' che e' nella composizione: segnala, non corregge."""
    esecuzione = c.esecuzione
    for r in S.RAPPORTI:
        if r.id not in versione.rapporti:
            continue
        righe = versione.righe_del_rapporto(r.id)
        ritenuta = next((riga.importo for riga in righe if riga.istituto == "ritenuta_irpef"), None)
        if ritenuta is None:
            continue
        lette = {i.istituto for i in ritenuta.derivazione.importi}
        contributi = sum((riga.importo.valore for riga in righe if riga.natura == "contributo_lavoratore"), Decimal(0))
        imponibile = sum((i.valore for i in ritenuta.derivazione.importi if i.istituto != "ritenuta_irpef"), Decimal(0))
        if contributi > 0 and not any(riga.natura == "contributo_lavoratore" and riga.istituto in lette for riga in righe):
            esecuzione.difetto(
                "L'imponibile fiscale non e' ridotto dai contributi del lavoratore",
                f"{r.id}, {versione.valuta_prevista}: la ritenuta si calcola su {_soldi(imponibile)} (somma degli importi "
                f"retributivi), mentre nello stesso pagamento il lavoratore versa {_soldi(contributi)} di contributi "
                "(CPDEL, Fondo Credito, TFS). La formula della ritenuta legge solo `fisco.imponibile`: non puo' "
                "dedurli. Da confermare con chi conosce il fisco: se l'imponibile IRPEF e' al netto dei contributi "
                "obbligatori, la ritenuta e' calcolata troppo alta.",
            )
        riduzione = next((riga.importo for riga in righe if riga.istituto == "riduzione_tfr"), None)
        if riduzione is not None and riduzione.istituto not in lette:
            esecuzione.difetto(
                "La riduzione del lordo TFR non riduce l'imponibile fiscale",
                f"{r.id}, {versione.valuta_prevista}: la riduzione {_soldi(riduzione.valore)} abbassa il netto ma la ritenuta "
                f"e' calcolata su {_soldi(imponibile)}, il lordo prima della riduzione: la riduzione ha maturazione "
                "`periodo`, derivata, e quindi non e' reddito.",
            )
        for riga in righe:
            if riga.natura == "rimborso_730" and riga.effetto == "nessuno":
                netto = next(n.netto for n in versione.netti if n.rapporto == r.id)
                esecuzione.difetto(
                    "Il rimborso 730 non puo' essere insieme nel netto e a credito nella delega",
                    f"{r.id}, {versione.valuta_prevista}: il rimborso {_soldi(riga.importo.valore)} e' una riga con un solo "
                    f"effetto. Dichiarato a credito F24EP (effetto nessuno sul netto), il netto resta {_soldi(netto)} e "
                    "il lavoratore non lo riceve; dichiarato sul netto, il sostituto non avrebbe il credito da "
                    "compensare. Servirebbero due righe dallo stesso importo, e la struttura ne ammette una.",
                )
        if r.al is not None and not any(riga.istituto == "conguaglio_irpef" for riga in righe):
            esecuzione.difetto(
                "Il conguaglio fiscale alla cessazione non c'e'",
                f"{r.id} cessa il {r.al}: il suo ultimo pagamento ({versione.valuta_prevista}) ha solo la ritenuta e un "
                "avviso di proiezione del conguaglio. Il nucleo riconosce l'ultimo pagamento solo dalla data scelta "
                "dall'ente per l'anno (`registra_ultimo_pagamento`); il CONTEXT dice che il conguaglio si fa anche "
                "sull'ultimo pagamento alla cessazione, e a dicembre la persona e' assente dal pagamento.",
            )


def _versione(c: _Contesto, tag: str, valuta: date, importi: dict[str, list], arrivi: dict):
    passo = c.passo(tag, "versione")
    c.comando(tag, f"emissione della versione di proposta ({tag})")
    c.ufficio.conta("scelta", tag, f"valuta prevista della versione ({valuta})")
    elenco = [i for righe in importi.values() for i in righe]
    try:
        versione = emetti_versione(c.registro, c.corpus, valuta, elenco)
    except ErrorePaghe as errore:
        passo.fermi.append(Fermo(tag, "versione", tuple(importi), causa_di(str(errore)), str(errore), bloccati=tuple(importi)))
        for rapporto in importi:
            arrivi[rapporto] = "versione"
        return None
    persone = {r.id: r.persona for r in S.RAPPORTI}
    passo.riuscito.append(
        f"versione {versione.id}: {len(versione.righe)} righe di composizione, valuta prevista {valuta}, "
        f"{len(versione.rapporti)} rapporti"
    )
    for netto in versione.netti:
        passo.riuscito.append(f"netto {netto.rapporto}: {_soldi(netto.netto)}")
    for fermo in versione.fermi:
        passo.fermi.append(Fermo(tag, "versione", (fermo.rapporto,), causa_di(fermo.motivo), fermo.motivo))
        arrivi[fermo.rapporto] = "versione"
    for dato in versione.dati_mancanti:
        rapporti = tuple(sorted(r for r, p in persone.items() if p == dato.soggetto)) or tuple(versione.rapporti)
        passo.fermi.append(Fermo(tag, "versione", rapporti, f"dato mancante {dato.tipo}", dato.motivo))
    per_tipo: dict[str, list[str]] = {}
    for avviso in versione.avvisi:
        rapporto = next((r for r, p in persone.items() if p == avviso.persona), avviso.persona)
        per_tipo.setdefault(avviso.tipo, []).append(rapporto)
    for tipo in sorted(per_tipo):
        passo.note.append(f"avviso {tipo}: {', '.join(sorted(set(per_tipo[tipo])))}")
    for escluso in versione.esclusi:
        passo.note.append(f"escluso {escluso.importo.istituto} di {escluso.importo.rapporto}: {escluso.motivo}")
    conguagli = [(r.rapporto, r.importo.valore) for r in versione.righe if r.istituto == "conguaglio_irpef"]
    if conguagli:
        passo.riuscito.append(
            "conguaglio fiscale sull'ultimo pagamento: " + ", ".join(f"{r} {_soldi(v)}" for r, v in sorted(conguagli))
        )
    passo.fittizio.append(
        "categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio "
        "(valori fiscali finti)"
    )
    if tag != PREPARAZIONE:
        _controlla_fiscale(c, versione)
    return versione


def _conferma_e_pagamento(c: _Contesto, tag: str, versione, valuta: date, giorno_conferma: date) -> None:
    passo = c.passo(tag, "conferma")
    c.vai(giorno_conferma)
    conferma_versione(c.registro, versione.id)
    c.ufficio.conta("conferma", tag, f"conferma della versione {versione.id}")
    passo.riuscito.append(f"versione {versione.id} confermata ({len(versione.rapporti)} rapporti)")
    passo.fittizio.append("la conferma e' una chiamata del percorso: nessun adattatore verso la Ragioneria")
    passo = c.passo(tag, "pagamento")
    c.vai(valuta)
    risultato = registra_pagamento_eseguito(
        c.registro, c.corpus, f"pagamento-{tag}", ADATTATORE, versione.id, valuta, versione.rapporti
    )
    c.ufficio.conta("evento", tag, f"pagamento eseguito della versione {versione.id}")
    c.orologio.avanza()
    esito = risultato.esito
    passo.riuscito.append(f"esito pagato {esito.id}: {len(esito.righe)} righe, valuta {valuta}")
    passo.fittizio.append("l'evento di pagamento eseguito e' simulato dal percorso, con valuta uguale alla prevista")
    persone = {r.id: r.persona for r in S.RAPPORTI}
    for avviso in risultato.avvisi:
        rapporto = next((r for r, p in persone.items() if p == avviso.persona), avviso.persona)
        passo.note.append(f"avviso {avviso.tipo}: {rapporto}")


def _ente_e_mittente() -> tuple[Ente, Mittente]:
    firmatario = codice_fiscale("PROVA", "FIRMA", 1960, 1, 1)
    mittente = codice_fiscale("PROVA", "MITTENTE", 1961, 2, 2)
    ente = Ente(S.CF_ENTE, S.DENOMINAZIONE_ENTE, "00000", firmatario)
    return ente, Mittente(mittente, "UFFICIO PERSONALE DI PROVA", S.CF_ENTE, "98765432103", "1")


def _denuncia_e_lista(c: _Contesto, tag: str, mese: Mese, giorno: date, versione, arrivi: dict) -> None:
    pd = c.passo(tag, "denuncia")
    pl = c.passo(tag, "lista_pos_pa")
    c.vai(giorno)
    c.comando(tag, f"produzione della denuncia e della ListaPosPA ({tag})")
    viste_ok = []
    for rapporto in versione.rapporti:
        try:
            scostamenti = segnala_scostamento_contributi(c.registro, c.corpus, rapporto, mese)
            vista = lista_pos_pa(c.registro, c.corpus, rapporto, mese)
        except ErrorePaghe as errore:
            pd.fermi.append(Fermo(tag, "denuncia", (rapporto,), causa_di(str(errore)), str(errore)))
            arrivi[rapporto] = "denuncia"
            continue
        contributi = sum(
            (i.valore for q in vista.quadri for i in q.importi if i.istituto in ("cpdel_totale", "tfs_totale", "contributo_tfr")),
            Decimal(0),
        )
        pd.riuscito.append(
            f"{rapporto}: {len(vista.quadri)} quadri, contributi nei quadri {_soldi(contributi)}; "
            + (
                "contributi trattenuti uguali ai dovuti"
                if not scostamenti
                else "scostamento tra trattenuti e dovuti per " + ", ".join(s.istituto for s in scostamenti)
            )
        )
        for scostamento in scostamenti:
            pd.fermi.append(
                Fermo(tag, "denuncia", (rapporto,), f"scostamento contributi {scostamento.istituto}",
                      f"{scostamento.istituto}: denuncia {scostamento.denuncia}, trattenuto {scostamento.trattenuto}")
            )
        pl.riuscito.append(
            f"{rapporto}: "
            + ", ".join(f"{q.tipo}{(' causale ' + q.causale) if q.causale else ''} {q.periodo}" for q in vista.quadri)
            + ("" if vista.trasmissibile else " (non trasmissibile)")
        )
        for fermo in vista.fermi:
            pl.fermi.append(Fermo(tag, "lista_pos_pa", (rapporto,), f"quadro {fermo.quadro} non prodotto", fermo.motivo))
        for dato in vista.mancanti:
            pl.fermi.append(Fermo(tag, "lista_pos_pa", (rapporto,), f"dato mancante {dato.fatto}", str(dato)))
        for motivo in vista.bozza:
            pl.fermi.append(Fermo(tag, "lista_pos_pa", (rapporto,), "bozza non trasmissibile", motivo))
        for avviso in vista.avvisi:
            pl.note.append(f"{rapporto}: {avviso}")
        if any(q.contrib_1_per_cento for q in vista.quadri):
            c.esecuzione.uno_per_cento = True
        if vista.trasmissibile:
            viste_ok.append(vista)
        else:
            arrivi.setdefault(rapporto, "lista_pos_pa")
    if viste_ok:
        ente, mittente = _ente_e_mittente()
        nome = c.scrivi(f"lista-pos-pa-{mese}.xml", in_xml(viste_ok, ente, mittente, mese))
        pl.riuscito.append(
            f"file {nome}: {len(viste_ok)} rapporti trasmissibili su {len(versione.rapporti)} pagati "
            "(in produzione la fornitura e' un blocco solo; qui contiene i soli rapporti trasmissibili)"
        )
    pd.fittizio.append("basi, concorsi e contributi del corpus reale; concorsi della performance e del rimborso 730 fittizi")
    pl.fittizio.append("ente dichiarante, mittente e codici fiscali dei firmatari di fantasia")


def _delega(c: _Contesto, tag: str, mese: Mese, versione, giorni: dict, arrivi: dict) -> None:
    pd = c.passo(tag, "delega")
    pf = c.passo(tag, "file_telematico")
    pr = c.passo(tag, "ricevute")
    pv = c.passo(tag, "versato")
    c.vai(giorni["scelta"])
    with c.ufficio.fase("scelta", tag):
        c.ufficio.data_versamento(mese, giorni["versamento"])
    c.vai(giorni["invio"])
    delega = costruisci_delega(c.registro, c.corpus, mese)
    per_istituto: dict[str, set[str]] = {}
    for riga in versione.righe:
        if riga.canale == "f24ep":
            per_istituto.setdefault(riga.istituto, set()).add(riga.rapporto)
    in_delega = tuple(sorted({rapporto for rapporti in per_istituto.values() for rapporto in rapporti}))
    pd.fittizio.append("mappatura dei codici, catalogo dei codici F24EP, scadenza e festivi del corpus fittizio")
    if delega.scadenza is not None:
        pd.riuscito.append(f"scadenza {delega.scadenza.data}, data di versamento scelta {giorni['versamento']}")
    fermi = []
    for fermo in delega.fermi:
        istituto = next((i for i in per_istituto if f"Istituto {i}" in fermo.motivo), None)
        origine = tuple(sorted(per_istituto.get(istituto, ()))) or in_delega
        fermi.append(
            Fermo(tag, "delega", origine, f"{fermo.caso}: {causa_di(fermo.motivo)}", fermo.motivo,
                  caso=istituto or fermo.caso, bloccati=in_delega)
        )
    for dato in delega.dati_mancanti:
        fermi.append(Fermo(tag, "delega", in_delega, f"dato mancante {dato.tipo}", dato.motivo, bloccati=in_delega))
    negative = [riga for riga in delega.righe if riga.debito < 0]
    for riga in negative:
        try:
            modulo_delega._file_telematico(delega.ente, giorni["versamento"], delega.righe)
            rifiuto = "il serializzatore la accetta"
        except ErrorePaghe as errore:
            rifiuto = f"il serializzatore la rifiuta ({errore})"
        c.esecuzione.difetto(
            "Una delega con un debito negativo risulta pronta",
            f"{tag}: la riga {riga.sezione} {riga.tributo} ha debito {_soldi(riga.debito)}. I conguagli a credito dei "
            "lavoratori (ritenuta con segno meno nella composizione) superano le ritenute del mese e la somma per codice "
            "va sotto zero; `costruisci_delega` non lo segnala e " + rifiuto + ". "
            "L'esempio nasce dall'anno fittizio con soli due pagamenti, ma il caso e' raggiungibile.",
        )
    for avviso in delega.avvisi:
        pd.note.append(f"avviso {avviso.tipo}")
    pronta = delega.pronta and not fermi
    if not pronta:
        pd.fermi.extend(fermi)
        for passo in (pf, pr, pv):
            passo.fermi.append(Fermo(tag, passo.nome, in_delega, CONSEGUENZA, "la delega del mese non e' trasmissibile"))
        for rapporto in in_delega:
            arrivi.setdefault(rapporto, "delega")
        if delega.righe:
            pd.note.append(
                "righe costruite ma non trasmissibili: "
                + ", ".join(f"{r.tributo} {_soldi(r.debito - r.credito)}" for r in delega.righe)
            )
        return
    for riga in delega.righe:
        pd.riuscito.append(f"riga {riga.sezione} {riga.tributo}: debito {_soldi(riga.debito)}, credito {_soldi(riga.credito)}")
    pd.riuscito.append(f"saldo {_soldi(delega.saldo)}")
    c.comando(tag, f"trasmissione della delega ({tag})")
    trasmessa = trasmetti_delega(c.registro, c.corpus, f"DELEGA-{tag}", ADATTATORE, mese)
    pd.riuscito.append(f"delega {trasmessa.id} trasmessa il {giorni['invio']}")
    nome = c.scrivi(f"f24ep-{mese}.txt", trasmessa.file)
    pf.riuscito.append(f"file {nome}: {len(trasmessa.file.split(b'\r\n')) - 1} record")
    pf.fittizio.append("dati dell'ente (codice fiscale, denominazione, IBAN di tesoreria) di fantasia")
    for numero, fase in enumerate(("controlli_formali", "controllo_crediti", "addebito")):
        c.vai(giorni["ricevute"][numero])
        registra_ricevuta_delega(c.registro, f"ricevuta-{tag}-{numero}", ADATTATORE, trasmessa.id, fase, "positivo")
        c.ufficio.conta("evento", tag, f"ricevuta della delega: {fase}")
    pr.riuscito.append(f"stato della delega: {stato_delega(c.registro, trasmessa.id).value}")
    pr.fittizio.append("le tre ricevute (controlli formali, controllo dei crediti, addebito) sono simulate, tutte positive")
    esito = registra_versamento_delega(c.registro, f"versamento-{tag}", ADATTATORE, trasmessa.id, giorni["ricevute"][2])
    c.ufficio.conta("evento", tag, "versamento eseguito della delega")
    situazione = situazione_delega(c.registro, trasmessa.id)
    pv.fittizio.append("l'addebito e' simulato dal percorso, alla data di versamento scelta")
    pv.riuscito.append(
        f"esito versato {esito.id}: {len(esito.righe)} righe, {_soldi(sum((r.valore for r in esito.righe), Decimal(0)))} "
        f"versati il {situazione.versata_il}"
    )
    pv.riuscito.append(f"righe ancora da versare nel mese: {len(costruisci_delega(c.registro, c.corpus, mese).righe)}")


def _chiudi_arrivi(esecuzione: Esecuzione, tag: str, arrivi: dict) -> None:
    for r in S.RAPPORTI:
        esecuzione.arrivi[(tag, r.id)] = arrivi.get(r.id, "completo")


def esegui(uscita: Path | None = None, tieni_aperto: bool = False, denuncia_di_dicembre: bool = False) -> Esecuzione:
    """Fa girare il mese. Con `tieni_aperto` il registro resta leggibile in `Esecuzione.registro`: chi lo chiede lo chiude.

    Di dicembre la denuncia e la ListaPosPA girano solo con `denuncia_di_dicembre`: per i cumuli del mese di conguaglio
    il nucleo ricalcola la denuncia di tutti i mesi dell'anno per ogni rapporto, e il test deve restare veloce.
    """
    c = _Contesto(uscita)
    esecuzione, reg, u = c.esecuzione, c.registro, c.ufficio
    fatti = _fatti_di_avvio(c)

    # Febbraio: il pagamento che precede, solo per il rapporto dell'arretrato (preparazione, fuori dal mese)
    c.vai(date(2026, 2, 20))
    versione_feb = _versione(c, PREPARAZIONE, date(2026, 2, 27), {"R02": list(calcola(reg, c.corpus, "R02", S.FEBBRAIO))}, {})
    _conferma_e_pagamento(c, PREPARAZIONE, versione_feb, date(2026, 2, 27), date(2026, 2, 21))

    # Marzo: i fatti del mese
    passo_fatti = c.passo("2026-03", "fatti")
    c.vai(date(2026, 3, 5))
    with u.fase("ricorrente", "2026-03"):
        u.fatto("R03", "performance", S.PERFORMANCE_2025, date(2025, 1, 1), date(2025, 12, 31), S.ATTO_PERFORMANCE)
        c.vai(date(2026, 3, 6))
        u.codice("R02", "area", "funzionari", date(2026, 2, 1), None, S.ATTO_PROGRESSIONE)
        u.codice("R02", "qualifica", S.QUALIFICHE["funzionari"], date(2026, 2, 1), None, S.ATTO_PROGRESSIONE)
        c.vai(date(2026, 3, 16))
        r05 = S.PER_ID["R05"]
        for tipo, fatto in fatti["R05"].items():
            u.annulla("R05", fatto.id, tipo, "cessazione al 14/03")
        for tipo, valore in S.fatti_inquadramento(r05).items():
            u.codice("R05", tipo, valore, r05.dal, r05.al)
        u.codice("R05", "codice_cessazione", "1", r05.al, r05.al)
    with u.fase("avvio", "2026-03"):
        c.vai(date(2026, 3, 18))
        _registra_rapporto(c, S.PER_ID["R06"])
    avvio = sum(1 for p in u.passaggi if p.categoria == "avvio")
    ricorrenti = sum(1 for p in u.passaggi if p.categoria == "ricorrente" and p.quando == "2026-03")
    passo_fatti.riuscito.append(f"{avvio} fatti di avvio (ente, persone, rapporti, assunzione di R06) registrati nel registro")
    passo_fatti.riuscito.append(f"{ricorrenti} fatti del mese: performance, progressione, cessazione")
    passo_fatti.fittizio.append("tutti: ente, persone e rapporti sono di fantasia")

    arrivi: dict = {}
    c.vai(date(2026, 3, 19))
    importi = _importi_del_mese(c, S.MARZO, "2026-03", c.passo("2026-03", "calcolo"), arrivi)
    versione = _versione(c, "2026-03", date(2026, 3, 27), importi, arrivi)
    if versione is not None:
        _conferma_e_pagamento(c, "2026-03", versione, date(2026, 3, 27), date(2026, 3, 20))
        _denuncia_e_lista(c, "2026-03", S.MARZO, date(2026, 4, 2), versione, arrivi)
        _delega(
            c, "2026-03", S.MARZO, versione,
            {"scelta": date(2026, 4, 2), "versamento": date(2026, 4, 16), "invio": date(2026, 4, 8),
             "ricevute": (date(2026, 4, 9), date(2026, 4, 10), date(2026, 4, 16))},
            arrivi,
        )
    _chiudi_arrivi(esecuzione, "2026-03", arrivi)

    # Dicembre: l'ultimo pagamento dell'anno e il conguaglio
    c.vai(date(2026, 11, 20))
    with u.fase("scelta", "2026-12"):
        u.ultimo_pagamento(2026, S.ULTIMO_PAGAMENTO_2026)
    c.vai(date(2026, 12, 2))
    with u.fase("ricorrente", "2026-12"):
        u.fatto("R07", "rimborso_irpef_730", S.RIMBORSO_730, S.DICEMBRE.primo_giorno, S.DICEMBRE.ultimo_giorno, S.ATTO_RIMBORSO)
    arrivi = {}
    c.vai(date(2026, 12, 10))
    importi = _importi_del_mese(c, S.DICEMBRE, "2026-12", c.passo("2026-12", "calcolo"), arrivi)
    versione = _versione(c, "2026-12", S.ULTIMO_PAGAMENTO_2026, importi, arrivi)
    if versione is not None:
        _conferma_e_pagamento(c, "2026-12", versione, S.ULTIMO_PAGAMENTO_2026, date(2026, 12, 11))
        if denuncia_di_dicembre:
            _denuncia_e_lista(c, "2026-12", S.DICEMBRE, date(2027, 1, 7), versione, arrivi)
        else:
            for nome in ("denuncia", "lista_pos_pa"):
                c.passo("2026-12", nome).note.append(
                    "con `--denuncia-di-dicembre` gira e non ha fermi nuovi rispetto a marzo; qui non e' eseguita perche' "
                    "per i cumuli del mese di conguaglio il nucleo ricalcola la denuncia di tutti i mesi dell'anno per ogni "
                    "rapporto: alcuni secondi, troppi per il test"
                )
        _delega(
            c, "2026-12", S.DICEMBRE, versione,
            {"scelta": date(2027, 1, 7), "versamento": date(2027, 1, 18), "invio": date(2027, 1, 12),
             "ricevute": (date(2027, 1, 13), date(2027, 1, 14), date(2027, 1, 18))},
            arrivi,
        )
    _chiudi_arrivi(esecuzione, "2026-12", arrivi)

    esecuzione.passaggi = list(u.passaggi)
    esecuzione.corpus = c.corpus
    if tieni_aperto:
        esecuzione.registro = reg
    else:
        reg.chiudi()
    return esecuzione
