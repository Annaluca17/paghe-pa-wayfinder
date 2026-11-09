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
    controlla_completezza,
    denuncia_aziendale,
    denuncia_individuale,
    costruisci_delega,
    lista_collaboratori,
    differenze,
    emetti_versione,
    lista_pos_pa,
    prospetto_paga,
    registra_messa_a_disposizione,
    registra_pagamento_eseguito,
    registra_ricevuta_delega,
    rapporti_della_vista,
    registra_versamento_delega,
    rimborso_730_4,
    segnala_scostamento_contributi,
    situazione_delega,
    stato_delega,
    trasmetti_delega,
)
from paghe import delega as modulo_delega
from paghe.blocco_pagamenti import registra_esito_verifica, registra_richiesta_verifica
from paghe.errori import ErrorePaghe, VistaFerma
from paghe.proposta import _costruisci
from paghe.impegni import registra_impegno
from paghe.part_time import registra_programmazione
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
    "prospetto_paga",
    "denuncia",
    "lista_pos_pa",
    "lista_collaboratori",
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
    "prospetto_paga": "Prospetto paga",
    "denuncia": "Denuncia",
    "lista_pos_pa": "ListaPosPA",
    "lista_collaboratori": "Lista collaboratori",
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

    def familiare_a_carico(self, persona, relazione, codice_fiscale, nascita, percentuale, dal, atto):
        self._conta_fatto(f"persona {persona}: familiare a carico")
        return self.registro.registra_familiare_a_carico(persona, relazione, codice_fiscale, nascita, percentuale, dal, None, atto)

    def domicilio_fiscale(self, persona, comune, regione, dal, atto):
        self._conta_fatto(f"persona {persona}: domicilio fiscale")
        return self.registro.registra_domicilio_fiscale(persona, comune, regione, dal, atto=atto)

    def reddito_anno_precedente(self, persona, anno, reddito, atto):
        self._conta_fatto(f"persona {persona}: reddito dell'anno precedente")
        return self.registro.registra_reddito_anno_precedente(persona, anno, reddito, atto)

    def collega(self, rapporto, persona, dal):
        self._conta_fatto(f"rapporto {rapporto}: legame con la persona")
        return self.registro.collega_rapporto(rapporto, persona, dal)

    def programma(self, rapporto, programma, dal):
        self._conta_fatto(f"rapporto {rapporto}: programma")
        return self.registro.registra_programma_rapporto(rapporto, programma, dal)

    def codice(self, rapporto, tipo, valore, dal, al=None, atto=None):
        self._conta_fatto(f"rapporto {rapporto}: {tipo}")
        return self.registro.registra_codice(rapporto, tipo, valore, dal, al, atto)

    def fatto(self, rapporto, tipo, valore, dal, al=None, atto=None):
        self._conta_fatto(f"rapporto {rapporto}: {tipo}")
        return self.registro.registra_fatto(rapporto, tipo, valore, dal, al, atto)

    def programmazione_part_time(self, rapporto, ore_per_giorno, atto):
        """Un atto, un passaggio: l'Ufficio fissa la programmazione di un periodo, un fatto per giorno nel registro."""
        self.conta(self._categoria, self._quando, f"rapporto {rapporto}: programmazione del part-time")
        registra_programmazione(self.registro, rapporto, ore_per_giorno, atto)

    def esito_730_4(self, persona, rimborso, anno_redditi, dal, atto):
        self._conta_fatto(f"persona {persona}: esito 730-4")
        return self.registro.registra_esito_730_4(persona, rimborso, anno_redditi, dal, atto)

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
    denunce_individuali: dict = field(default_factory=dict)  # (mese, rapporto) -> DenunciaIndividuale dei tempi determinati
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
    def __init__(self, uscita: Path | None, corpus_extra: str = "") -> None:
        reale = CORPUS_REALE.read_text(encoding="utf-8")
        fittizio = CORPUS_FITTIZIO.read_text(encoding="utf-8")
        # Il corpus reale rifiuta i riferimenti `fittizio:`: l'unione e' un corpus NON reale (ADR 0003).
        self.corpus = Corpus.da_toml(reale + "\n" + fittizio + "\n" + corpus_extra, reale=False)
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
        ("regione", S.REGIONE_ENTE),
    ):
        c.ufficio.codice_ente(tipo, valore, date(2026, 1, 1))


def _registra_impegni(c: _Contesto) -> None:
    """Fatti contabili simulati: un impegno automatico del 2026 per ogni codice di spesa e programma in uso, capiente."""
    numero = 0
    for piano in S.PIANI_DI_SPESA:
        for programma in S.PROGRAMMI_IN_USO:
            numero += 1
            missione, _, voce = programma.partition(".")
            registra_impegno(
                c.registro, f"impegno-2026-{numero}", ADATTATORE, numero, 2026, piano, missione, voce,
                S.DISPONIBILITA_IMPEGNO, date(2026, 1, 1),
            )


def _registra_rapporto(c: _Contesto, r: S.Rapporto) -> dict[str, object]:
    """Anagrafica e inquadramento di un rapporto; per sindaco e co.co.co. i fatti del loro regime (`_registra_regime`)."""
    u = c.ufficio
    u.codice_persona(r.persona, "codice_fiscale", r.cf, r.nascita)
    u.codice_persona(r.persona, "cognome", r.cognome, r.nascita)
    u.codice_persona(r.persona, "nome", r.nome, r.nascita)
    u.iban_persona(r.persona, S.IBAN_PERSONE, date(2026, 1, 1))
    u.domicilio_fiscale(r.persona, S.COMUNE_DOMICILIO, S.REGIONE_DOMICILIO, date(2026, 1, 1), S.ATTO_DOMICILIO)
    if r.id == "R01":
        u.reddito_anno_precedente(r.persona, 2025, S.REDDITO_2025_P01, S.ATTO_CU_2025)
    if r.dipendente and r.detrazioni:
        u.dichiarazione_sostituito(r.persona, "lavoro_dipendente", date(2026, 1, 1), S.ATTO_DETRAZIONI)
        if r.id == "R01":
            u.familiare_a_carico(
                r.persona, "figlio", S.CF_FIGLIO_R01, S.NASCITA_FIGLIO_R01, S.PERCENTUALE_FIGLIO_R01,
                date(2026, 1, 1), S.ATTO_FAMILIARE,
            )
    u.collega(r.id, r.persona, r.dal)
    u.programma(r.id, S.PROGRAMMA_PER_TITOLO[r.titolo], r.dal)
    fatti: dict[str, object] = {}
    if r.dipendente:
        u.codice(r.id, "comune_sede_lavoro", S.COMUNE_SEDE, r.dal)
        u.codice(r.id, "cap_sede_lavoro", S.CAP_SEDE, r.dal)
        for tipo, valore in S.fatti_inquadramento(r).items():
            fatti[tipo] = u.codice(r.id, tipo, valore, r.dal, r.al)
        if r.fascia is not None:
            u.codice(r.id, "fascia_segretario", r.fascia, r.dal, atto=S.ATTO_FASCIA_SEGRETARIO)
        if r.posizione is not None:
            atto = S.ATTO_POSIZIONE_DIRIGENTE if r.titolo == "dirigente" else S.ATTO_POSIZIONE_SEGRETARIO
            u.fatto(r.id, S.FATTO_POSIZIONE[r.titolo], r.posizione, r.dal, atto=atto)
    else:
        _registra_regime(c, r)
    return fatti


def _registra_regime(c: _Contesto, r: S.Rapporto) -> None:
    """I fatti di un mandato di sindaco o di un piano di rate: carica, condizione e posizione datate, misura e rate da atto."""
    u = c.ufficio
    if r.titolo == "sindaco":
        u.codice(r.id, "carica", "sindaco", r.dal, atto=S.ATTO_MANDATO)
        u.codice(r.id, "condizione_lavorativa", "non_dipendente", r.dal, atto=S.ATTO_MANDATO)
        u.codice(r.id, "posizione_previdenziale", "gestione_separata", r.dal, atto=S.ATTO_MANDATO)
        u.fatto(r.id, "misura_indennita_funzione", S.MISURA_INDENNITA_SINDACO, date(2026, 1, 1), atto=S.ATTO_MISURA_INDENNITA)
    else:
        u.codice(r.id, "posizione_previdenziale", "gestione_separata", r.dal, atto=S.ATTO_PIANO_DI_RATE)
        for giorno in (S.RATA_DI_MARZO, S.RATA_DI_DICEMBRE):
            u.fatto(r.id, "rata_collaborazione", S.RATA_COCOCO, giorno, giorno, atto=S.ATTO_PIANO_DI_RATE)


def _fatti_di_avvio(c: _Contesto) -> dict[str, dict[str, object]]:
    c.vai(date(2026, 1, 12))
    fatti = {}
    with c.ufficio.fase("avvio", "avvio"):
        _registra_ente(c)
        _registra_impegni(c)
        for r in S.RAPPORTI:
            if r.id == "R06":
                continue  # assunto a marzo
            fatti[r.id] = _registra_rapporto(c, r)
        c.ufficio.fatto("R04", "part_time", S.PART_TIME_PERCENTUALE, date(2026, 1, 1))
        c.ufficio.codice("R04", "tipo_part_time", S.PART_TIME_TIPO, date(2026, 1, 1))
        c.ufficio.programmazione_part_time("R04", S.programmazione_part_time_2026(), S.ATTO_PROGRAMMAZIONE)
        c.ufficio.fatto("R12", "part_time", S.TD_PERCENTUALE, date(2026, 1, 1))
        c.ufficio.codice("R12", "tipo_part_time", S.TD_TIPO_PART_TIME, date(2026, 1, 1))
        c.ufficio.codice("R12", "qualifica_inps", S.TD_QUALIFICA_INPS, date(2026, 1, 1))
        c.ufficio.codice("R12", "termine_per_sostituzione", S.TD_TERMINE_PER_SOSTITUZIONE, date(2026, 1, 1))
        c.ufficio.codice("R12", "prima_iscrizione_dal_1996", S.TD_PRIMA_ISCRIZIONE_DAL_1996, date(2026, 1, 1))
        c.ufficio.programmazione_part_time("R12", S.programmazione_td_2026(), S.ATTO_PROGRAMMAZIONE_TD)
    return fatti


# Un ciclo mensile

def _fuori_servizio(r: S.Rapporto, mese: Mese) -> bool:
    return (r.al is not None and r.al < mese.primo_giorno) or r.dal > mese.ultimo_giorno


def _importi_del_mese(c: _Contesto, mese: Mese, tag: str, passo: Passo, arrivi: dict, valuta: date) -> dict[str, list]:
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
            rimborso = rimborso_730_4(reg, corpus, r.id, valuta)
            if rimborso is not None:
                righe.append(rimborso)
                dettagli.append(
                    f"rimborso del 730-4: {_soldi(rimborso.valore)}, anno dei redditi dichiarati {rimborso.anno_imposta}"
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
        if not righe and r.dipendente and _fuori_servizio(r, mese):
            passo.note.append(f"{r.id}: non in servizio nel mese, nessun importo")
            arrivi[r.id] = "fuori servizio"
            continue
        if not righe:
            passo.note.append(f"{r.id}: nessun importo nel mese")
            arrivi[r.id] = "fuori servizio"
            continue
        importi[r.id] = righe
        lordo = sum((i.valore for i in righe if i.derivazione.maturazione not in ("periodo", "mese", "cassa", "onere")), Decimal(0))
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
        # Cessato prima del pagamento: un contratto che finisce dopo la valuta (R12, 31/12) non e' una cessazione a meta' anno.
        if r.al is not None and r.al < versione.valuta_prevista and not any(riga.istituto == "conguaglio_irpef" for riga in righe):
            esecuzione.difetto(
                "Il conguaglio fiscale alla cessazione non c'e'",
                f"{r.id} cessa il {r.al}: il suo ultimo pagamento ({versione.valuta_prevista}) ha solo la ritenuta e un "
                "avviso di proiezione del conguaglio. Il nucleo riconosce l'ultimo pagamento solo dalla data scelta "
                "dall'ente per l'anno (`registra_ultimo_pagamento`); il CONTEXT dice che il conguaglio si fa anche "
                "sull'ultimo pagamento alla cessazione, e a dicembre la persona e' assente dal pagamento.",
            )


_NETTO_DA_COMUNICARE = re.compile(r"Rapporto (\S+): verifica 48-bis mancante, netto da comunicare (\S+)")


def _verifiche_48bis(c: _Contesto, tag: str, valuta: date, elenco: list, passo) -> None:
    """Prima dell'invio l'ufficio chiede la verifica per i netti sopra soglia; AdER risponde non inadempiente (ADR 0034)."""
    bozza = _costruisci(c.registro, c.corpus, valuta, tuple(elenco), (), c.registro.adesso(), con_proposta=False)
    persone = {r.id: r.persona for r in S.RAPPORTI}
    for fermo in bozza.fermi:
        trovato = _NETTO_DA_COMUNICARE.match(fermo.motivo)
        if trovato is None:
            continue
        rapporto, netto = trovato.group(1), Decimal(trovato.group(2))
        c.ufficio.conta("comando", tag, f"richiesta di verifica 48-bis per {rapporto}")
        chiave = f"verifica-48bis-{tag}-{rapporto}"
        registra_richiesta_verifica(c.registro, chiave, "prova", persone[rapporto], valuta - timedelta(days=10), netto, valuta)
        registra_esito_verifica(c.registro, f"{chiave}-esito", "prova", chiave, valuta - timedelta(days=8), "non_inadempiente")
        passo.fittizio.append(f"esito della verifica 48-bis di {rapporto} simulato: non inadempiente")


def _versione(c: _Contesto, tag: str, valuta: date, importi: dict[str, list], arrivi: dict):
    passo = c.passo(tag, "versione")
    c.comando(tag, f"emissione della versione di proposta ({tag})")
    c.ufficio.conta("scelta", tag, f"valuta prevista della versione ({valuta})")
    elenco = [i for righe in importi.values() for i in righe]
    _verifiche_48bis(c, tag, valuta, elenco, passo)
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
    if versione.righe_proposta:
        passo.riuscito.append(
            f"righe di proposta ({len(versione.righe_proposta)}): "
            + "; ".join(
                f"{r.piano_dei_conti} {r.missione}.{r.programma} imp {'/'.join(map(str, r.impegno)) if r.impegno else '-'} "
                f"{_soldi(r.totale)}"
                for r in versione.righe_proposta
            )
        )
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
    for rapporto in sorted(set(importi) - set(versione.rapporti)):
        if rapporto in arrivi:
            continue
        motivi = [e.motivo for e in versione.esclusi if e.importo.rapporto == rapporto]
        motivo = motivi[0] if motivi else "nessun importo in versione"
        passo.fermi.append(Fermo(tag, "versione", (rapporto,), causa_di(motivo), motivo))
        arrivi[rapporto] = "versione"
    conguagli = [(r.rapporto, r.importo.valore) for r in versione.righe if r.istituto == "conguaglio_irpef"]
    if conguagli:
        passo.riuscito.append(
            "conguaglio fiscale sull'ultimo pagamento: " + ", ".join(f"{r} {_soldi(v)}" for r, v in sorted(conguagli))
        )
    passo.fittizio.append("gli impegni automatici sono fatti contabili simulati dal percorso, con disponibilita' molto alta")
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
    if tag != PREPARAZIONE:
        _prospetti(c, tag, esito, valuta, versione.rapporti)


def _prospetti(c: _Contesto, tag: str, esito, valuta: date, rapporti) -> None:
    """Un prospetto per ogni rapporto pagato dell'esito: si mette a disposizione solo se consegnabile, e non ferma altri passi."""
    passo = c.passo(tag, "prospetto_paga")
    avvisi: dict[str, list[str]] = {}
    for rapporto in sorted(rapporti):
        try:
            prospetto = prospetto_paga(c.registro, c.corpus, rapporto, esito.id)
        except ErrorePaghe as errore:
            passo.fermi.append(Fermo(tag, "prospetto_paga", (rapporto,), f"prospetto paga: {causa_di(str(errore))}", str(errore)))
            continue
        for fermo in prospetto.fermi:
            passo.fermi.append(Fermo(tag, "prospetto_paga", (rapporto,), f"prospetto paga: {causa_di(fermo)}", fermo))
        for dato in prospetto.mancanti:
            passo.fermi.append(
                Fermo(tag, "prospetto_paga", (rapporto,), f"prospetto paga: dato mancante {dato}", f"dato mancante {dato}")
            )
        riga = (
            f"{rapporto}: prospetto del pagamento del {prospetto.data_pagamento} (esito {esito.id}), posizione "
            f"{prospetto.posizione or '-'}, {len(prospetto.righe_sul_netto)} righe sul netto, netto {_soldi(prospetto.netto)}, "
            f"{len(prospetto.senza_effetto)} senza effetto sul netto"
        )
        if prospetto.consegnabile:
            c.vai(valuta + timedelta(days=1))
            messa = registra_messa_a_disposizione(
                c.registro, c.corpus, rapporto, esito.id, f"prospetto-{tag}-{rapporto}-{esito.id}", valuta + timedelta(days=1),
                f"area-riservata:{tag}-{rapporto}", ADATTATORE,
            )
            c.ufficio.conta("evento", tag, "messa a disposizione del prospetto paga")
            c.orologio.avanza()
            riga += f"; consegnato, esito dichiarato {messa.esito.id}"
        passo.riuscito.append(riga)
        for dato in prospetto.avvisi:
            avvisi.setdefault(dato, []).append(rapporto)
    passo.note.extend(f"avviso {dato}: {', '.join(chi)}" for dato, chi in sorted(avvisi.items()))
    passo.fittizio.append(
        "la messa a disposizione e' simulata dal percorso (giorno dopo il pagamento, riferimento di canale di fantasia); "
        "la posizione di sindaco e collaboratori e la composizione sono dichiarate dal corpus fittizio"
    )


def _ente_e_mittente() -> tuple[Ente, Mittente]:
    firmatario = codice_fiscale("PROVA", "FIRMA", 1960, 1, 1)
    mittente = codice_fiscale("PROVA", "MITTENTE", 1961, 2, 2)
    ente = Ente(S.CF_ENTE, S.DENOMINAZIONE_ENTE, "00000", firmatario)
    return ente, Mittente(mittente, "UFFICIO PERSONALE DI PROVA", S.CF_ENTE, "98765432103", "1")


def _denuncia_individuale(c: _Contesto, tag: str, mese: Mese, rapporto: str, passo: Passo, individuali: list) -> None:
    """La DenunciaIndividuale dei tempi determinati, nel passo della ListaPosPA che accompagna (ADR 0027)."""
    try:
        vista = denuncia_individuale(c.registro, c.corpus, rapporto, mese)
    except ErrorePaghe as errore:
        passo.fermi.append(Fermo(tag, "lista_pos_pa", (rapporto,), causa_di(str(errore)), str(errore)))
        return
    if vista is None:
        return
    c.esecuzione.denunce_individuali[(tag, rapporto)] = vista
    individuali.append(vista)
    passo.riuscito.append(
        f"{rapporto}: DenunciaIndividuale {vista.tipo_contribuzione} {vista.qualifica1}/{vista.qualifica2}/{vista.qualifica3}, "
        f"imponibile {vista.imponibile}, contributo {_soldi(vista.contributo) if vista.contributo is not None else '-'}, "
        f"PercPartTime {vista.perc_part_time}, PercPartTimeMese {vista.perc_part_time_mese}, "
        f"{len(vista.settimane)} settimane ({sum(1 for s in vista.settimane if s.copertura == 'D')} D), "
        f"{sum(1 for g in vista.giorni if g.lavorato == 'S')} giorni lavorati su {len(vista.giorni)}"
        + ("" if vista.trasmissibile else " (non trasmissibile)")
    )
    for fermo in vista.fermi:
        passo.fermi.append(Fermo(tag, "lista_pos_pa", (rapporto,), "DenunciaIndividuale non prodotta", fermo.motivo))
    for dato in vista.mancanti:
        passo.fermi.append(Fermo(tag, "lista_pos_pa", (rapporto,), f"DenunciaIndividuale: dato mancante {dato.fatto}", str(dato)))
    for motivo in vista.bozza:
        passo.fermi.append(Fermo(tag, "lista_pos_pa", (rapporto,), "DenunciaIndividuale: bozza non trasmissibile", motivo))


def _lista_collaboratori(c: _Contesto, tag: str, mese: Mese, rapporto: str, passo: Passo, arrivi: dict) -> None:
    """La lista collaboratori di un rapporto che il regime le assegna: senza i codici del tracciato e' una bozza."""
    try:
        vista = lista_collaboratori(c.registro, c.corpus, rapporto, mese)
    except ErrorePaghe as errore:
        passo.fermi.append(Fermo(tag, "lista_collaboratori", (rapporto,), causa_di(str(errore)), str(errore)))
        arrivi.setdefault(rapporto, "lista_collaboratori")
        return
    righe = "; ".join(
        (
            f"quota forfettaria {_soldi(r.contributo)} a carico dell'ente"
            if r.forfettaria
            else f"imponibile {_soldi(r.imponibile)}, contributo {_soldi(r.contributo)} "
            f"(collaboratore {_soldi(r.quota_collaboratore)}, ente {_soldi(r.quota_ente)})"
        )
        for r in vista.righe
    )
    passo.riuscito.append(
        f"{rapporto}: mese di erogazione {vista.mese_erogazione}, {len(vista.righe)} righe: {righe}"
        + ("" if vista.trasmissibile else " (non trasmissibile)")
    )
    for dato in vista.mancanti:
        passo.fermi.append(Fermo(tag, "lista_collaboratori", (rapporto,), f"dato mancante {dato}", dato))
    for motivo in vista.bozza:
        passo.fermi.append(Fermo(tag, "lista_collaboratori", (rapporto,), causa_di(motivo), motivo))
    if not vista.trasmissibile:
        arrivi.setdefault(rapporto, "lista_collaboratori")


def _denuncia_e_lista(c: _Contesto, tag: str, mese: Mese, giorno: date, versione, arrivi: dict) -> None:
    pd = c.passo(tag, "denuncia")
    pl = c.passo(tag, "lista_pos_pa")
    pc = c.passo(tag, "lista_collaboratori")
    c.vai(giorno)
    c.comando(tag, f"produzione della denuncia e della ListaPosPA ({tag})")
    pos_pa = rapporti_della_vista(c.registro, c.corpus, "lista_pos_pa", mese, versione.rapporti)
    collaboratori = rapporti_della_vista(c.registro, c.corpus, "lista_collaboratori", mese, versione.rapporti)
    pl.note.append("rapporti che il regime assegna alla ListaPosPA: " + (", ".join(pos_pa) or "nessuno"))
    pc.note.append("rapporti che il regime assegna alla lista collaboratori: " + (", ".join(collaboratori) or "nessuno"))
    viste_ok = []
    individuali = []
    for rapporto in versione.rapporti:
        try:
            scostamenti = segnala_scostamento_contributi(c.registro, c.corpus, rapporto, mese)
            vista = lista_pos_pa(c.registro, c.corpus, rapporto, mese) if rapporto in pos_pa else None
        except ErrorePaghe as errore:
            pd.fermi.append(Fermo(tag, "denuncia", (rapporto,), causa_di(str(errore)), str(errore)))
            arrivi[rapporto] = "denuncia"
            continue
        if vista is None:
            pd.riuscito.append(
                f"{rapporto}: "
                + (
                    "contributi trattenuti uguali ai dovuti"
                    if not scostamenti
                    else "scostamento tra trattenuti e dovuti per " + ", ".join(s.istituto for s in scostamenti)
                )
            )
        else:
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
        if vista is None:
            if rapporto in collaboratori:
                _lista_collaboratori(c, tag, mese, rapporto, pc, arrivi)
            continue
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
        _denuncia_individuale(c, tag, mese, rapporto, pl, individuali)
        if rapporto in collaboratori:
            _lista_collaboratori(c, tag, mese, rapporto, pc, arrivi)
    if individuali:
        quadratura = denuncia_aziendale(individuali)
        pl.riuscito.append(
            f"DenunciaAziendale {mese}: NumDenIndiv {quadratura.num_den_indiv}, TotaleADebito {quadratura.totale_a_debito}"
        )
        assenze = controlla_completezza(c.registro, c.corpus, mese)
        pl.riuscito.append(
            "controllo di completezza della DenunciaIndividuale: " + ("nessuna assenza" if not assenze else f"{len(assenze)} assenze")
        )
        for assenza in assenze:
            pl.fermi.append(Fermo(tag, "lista_pos_pa", (assenza.rapporto,), "assenza dalla DenunciaIndividuale", assenza.motivo))
        pl.fittizio.append("mappature della DenunciaIndividuale e calendario dei festivi: le prime sono del corpus reale, il calendario e' fittizio")
    if viste_ok:
        ente, mittente = _ente_e_mittente()
        nome = c.scrivi(f"lista-pos-pa-{mese}.xml", in_xml(viste_ok, ente, mittente, mese))
        pl.riuscito.append(
            f"file {nome}: {len(viste_ok)} rapporti trasmissibili su {len(pos_pa)} della ListaPosPA "
            "(in produzione la fornitura e' un blocco solo; qui contiene i soli rapporti trasmissibili)"
        )
    pd.fittizio.append("basi, concorsi e contributi del corpus reale; concorsi della performance e del rimborso 730 fittizi")
    pl.fittizio.append("ente dichiarante, mittente e codici fiscali dei firmatari di fantasia")
    pc.fittizio.append("nessun dato fittizio oltre ai rapporti: il tracciato della lista collaboratori non e' dichiarato")


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
    # Una riga a debito negativa deve fermare la delega (caso `debito_negativo`): il difetto e' che risulti pronta.
    negative = [riga for riga in delega.righe if riga.debito < 0] if delega.pronta else []
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


def esegui(
    uscita: Path | None = None, tieni_aperto: bool = False, denuncia_di_dicembre: bool = False, corpus_extra: str = ""
) -> Esecuzione:
    """Fa girare il mese. Con `tieni_aperto` il registro resta leggibile in `Esecuzione.registro`: chi lo chiede lo chiude.

    Di dicembre la denuncia e la ListaPosPA girano solo con `denuncia_di_dicembre`: per i cumuli del mese di conguaglio
    il nucleo ricalcola la denuncia di tutti i mesi dell'anno per ogni rapporto, e il test deve restare veloce.

    `corpus_extra` e' testo TOML aggiunto in coda al corpus: serve a un test per provare il percorso con una dichiarazione
    che il corpus non ha (per esempio la causale della gestione separata, di cui nessuna fonte dice il codice).
    """
    c = _Contesto(uscita, corpus_extra)
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
        c.vai(date(2026, 3, 17))
        u.codice("R11", "attestazione_prestazione", "si", S.RATA_DI_MARZO, S.RATA_DI_MARZO, S.ATTO_ATTESTAZIONE_MARZO)
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
    importi = _importi_del_mese(c, S.MARZO, "2026-03", c.passo("2026-03", "calcolo"), arrivi, date(2026, 3, 27))
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
        u.esito_730_4("P07", Decimal(S.RIMBORSO_730), S.ANNO_REDDITI_730, S.ATTO_RIMBORSO.data, S.ATTO_RIMBORSO)
    arrivi = {}
    c.vai(date(2026, 12, 10))
    importi = _importi_del_mese(c, S.DICEMBRE, "2026-12", c.passo("2026-12", "calcolo"), arrivi, S.ULTIMO_PAGAMENTO_2026)
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
