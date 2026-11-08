"""Versione di proposta, composizione del pagamento ed eventi di ritorno (ADR 0013, 0025).

Una versione di proposta ha una sola valuta prevista e più rapporti. Porta le righe di composizione,
collegate agli importi, il netto per rapporto, ciò che resta fuori (con il motivo), i rapporti fermi,
i dati mancanti e gli avvisi. È un'istantanea immutabile: gli stati (inviata, confermata, respinta,
superata) sono eventi, e un fatto che cambia dopo l'invio rende superata la versione, non la riscrive.

Gli eventi di ritorno (pagamento eseguito, ricevuta della delega, versamento eseguito) hanno un
identificativo stabile: lo stesso identificativo con lo stesso contenuto non ha effetto, con un
contenuto diverso è un errore. Dal pagamento eseguito nasce l'esito pagato; dal versamento eseguito,
una sola volta per versamento, l'esito versato. Il modello segnala, e non corregge, ciò che non torna.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from .calcolo import _somma_righe
from .corpus import Corpus
from .denuncia import MATURAZIONI_DERIVATE, calcola_denuncia
from .errori import CasoNonModellato, ClassificazioneMancante, ComposizioneMancante, ErroreCalcolo, ErroreRegistro, RedditoMancante
from .impegni import AUTOMATICO, Abbinamento, DisponibilitaImpegni
from .fisco import Avviso, _controlla_competenza, anno_imposta, attribuisci_reddito, calcola_fiscale, pagamento_finale
from .modello import Esito, Evento, Importo, TipoEsito
from .registro import TIPO_ANNO_IMPOSTA_DIVERSO, TIPO_IBAN, Registro
from .tempo import Mese, in_utc

# Nature della composizione che diventano spesa del Titolo 1 e quindi righe di proposta (ADR 0031).
NATURE_DI_SPESA = frozenset({"retribuzione", "contributo_ente", "irap"})

MOTIVO_GIA_PAGATO = "già in un esito pagato"
AVVISO_PERSONA_ASSENTE = "persona_assente_dall_ultimo_pagamento"
AVVISO_ALTRO_MESE = "pagamento_in_altro_mese"
AVVISO_ANNO_DIVERSO = "anno_imposta_diverso_dal_previsto"
AVVISO_COMPETENZA_AL_PAGAMENTO = "competenza_non_ammessa_al_pagamento"

TIPO_PAGAMENTO_ESEGUITO = "pagamento_eseguito"
TIPO_RICEVUTA_DELEGA = "ricevuta_delega"
TIPO_VERSAMENTO_ESEGUITO = "versamento_eseguito"

FASI_DELEGA = ("controlli_formali", "controllo_crediti", "addebito")
ESITI_RICEVUTA = ("positivo", "negativo", "sospeso")
CANALI_DI_VERSAMENTO = ("f24ep", "bonifico")
PROVENIENZE_DI_VERSAMENTO = ("addebito", "bonifico", "regolarizzazione")

# Nature che la delega F24EP porta a credito del sostituto, qualunque sia il canale della riga (ADR 0023).
NATURE_A_CREDITO = frozenset({"rimborso_730", "credito_sostituto"})

_SEGNO = {"piu": 1, "meno": -1, "nessuno": 0}


# Dati della versione

@dataclass(frozen=True)
class RigaComposizione:
    """Riga collegata a un importo, mai con un valore riscritto; porta ciò che dichiara l'istituto."""

    importo: Importo
    natura: str
    effetto: str
    destinatario: str
    canale: str
    riferimento: str

    @property
    def rapporto(self) -> str:
        return self.importo.rapporto

    @property
    def istituto(self) -> str:
        return self.importo.istituto

    @property
    def sul_netto(self) -> Decimal:
        """Il valore dell'importo col segno dell'effetto sul netto."""
        return _SEGNO[self.effetto] * self.importo.valore


@dataclass(frozen=True)
class NettoRapporto:
    rapporto: str
    netto: Decimal


@dataclass(frozen=True)
class Escluso:
    """Importo che resta fuori dalla versione, visibile con il motivo."""

    importo: Importo
    motivo: str


@dataclass(frozen=True)
class RapportoFermo:
    """Rapporto che la versione non porta: il motivo nomina il caso. Gli altri rapporti non si fermano."""

    rapporto: str
    motivo: str


@dataclass(frozen=True)
class DatoMancante:
    """Dato che non c'è: la versione si invia solo con l'avvertenza (ADR 0013)."""

    tipo: str
    soggetto: str
    motivo: str


@dataclass(frozen=True)
class RigaProposta:
    """Parte della proposta per una classificazione e un impegno: somma le righe di composizione di spesa (ADR 0031).

    Con il programma del rapporto mancante missione e programma restano vuoti, e senza impegno.
    """

    piano_dei_conti: str
    missione: str
    programma: str
    impegno: tuple[int, int] | None  # (esercizio, numero)
    riferimenti: tuple["RiferimentoRiga", ...]
    totale: Decimal

    @property
    def chiave(self) -> tuple[str, str, str, tuple[int, int] | None]:
        return (self.piano_dei_conti, self.missione, self.programma, self.impegno)


@dataclass(frozen=True)
class ContenutoVersione:
    valuta_prevista: date
    righe: tuple[RigaComposizione, ...]
    netti: tuple[NettoRapporto, ...]
    esclusi: tuple[Escluso, ...]
    fermi: tuple[RapportoFermo, ...]
    dati_mancanti: tuple[DatoMancante, ...]
    avvisi: tuple[Avviso, ...]
    righe_proposta: tuple[RigaProposta, ...] = field(default=(), kw_only=True)


@dataclass(frozen=True)
class VersioneProposta(ContenutoVersione):
    id: int
    registrato_il: datetime

    @property
    def rapporti(self) -> tuple[str, ...]:
        return tuple(netto.rapporto for netto in self.netti)

    def righe_del_rapporto(self, rapporto: str) -> tuple[RigaComposizione, ...]:
        return tuple(riga for riga in self.righe if riga.rapporto == rapporto)

    def riferimento(self, riga: RigaComposizione) -> "RiferimentoRiga":
        return RiferimentoRiga(self.id, riga.rapporto, riga.istituto, str(riga.importo.periodo), riga.importo.esiti_confrontati)


@dataclass(frozen=True)
class RiferimentoRiga:
    """Come un evento indica una riga di composizione: la versione e la chiave dell'importo collegato."""

    versione_id: int
    rapporto: str
    istituto: str
    periodo: str
    esiti_confrontati: tuple[int, ...] = ()

    def in_dizionario(self) -> dict:
        return {
            "versione": self.versione_id,
            "rapporto": self.rapporto,
            "istituto": self.istituto,
            "periodo": self.periodo,
            "esiti_confrontati": list(self.esiti_confrontati),
        }


class StatoVersione(StrEnum):
    INVIATA = "inviata"
    CONFERMATA = "confermata"
    RESPINTA = "respinta"
    SUPERATA = "superata"


# Serializzazione

def _avviso_in_dizionario(avviso: Avviso) -> dict:
    return {
        "tipo": avviso.tipo,
        "messaggio": avviso.messaggio,
        "persona": avviso.persona,
        "anno": avviso.anno,
        "valore": str(avviso.valore) if avviso.valore is not None else None,
    }


def _avviso_da_dizionario(dati: dict) -> Avviso:
    valore = Decimal(dati["valore"]) if dati["valore"] is not None else None
    return Avviso(dati["tipo"], dati["messaggio"], dati["persona"], dati["anno"], valore)


def _in_dizionario(contenuto: ContenutoVersione) -> dict:
    return {
        "righe": [
            {
                "importo": riga.importo.in_dizionario(),
                "natura": riga.natura,
                "effetto": riga.effetto,
                "destinatario": riga.destinatario,
                "canale": riga.canale,
                "riferimento": riga.riferimento,
            }
            for riga in contenuto.righe
        ],
        "netti": [{"rapporto": n.rapporto, "netto": str(n.netto)} for n in contenuto.netti],
        "esclusi": [{"importo": e.importo.in_dizionario(), "motivo": e.motivo} for e in contenuto.esclusi],
        "fermi": [{"rapporto": f.rapporto, "motivo": f.motivo} for f in contenuto.fermi],
        "dati_mancanti": [{"tipo": d.tipo, "soggetto": d.soggetto, "motivo": d.motivo} for d in contenuto.dati_mancanti],
        "avvisi": [_avviso_in_dizionario(a) for a in contenuto.avvisi],
        "righe_proposta": [
            {
                "piano_dei_conti": r.piano_dei_conti,
                "missione": r.missione,
                "programma": r.programma,
                "impegno": list(r.impegno) if r.impegno else None,
                "riferimenti": [
                    {k: v for k, v in rif.in_dizionario().items() if k != "versione"} for rif in r.riferimenti
                ],
                "totale": str(r.totale),
            }
            for r in contenuto.righe_proposta
        ],
    }


def _da_dizionario(versione_id: int, valuta: date, registrato: datetime, dati: dict) -> VersioneProposta:
    return VersioneProposta(
        valuta_prevista=valuta,
        righe=tuple(
            RigaComposizione(
                Importo.da_dizionario(riga["importo"]),
                riga["natura"],
                riga["effetto"],
                riga["destinatario"],
                riga["canale"],
                riga["riferimento"],
            )
            for riga in dati["righe"]
        ),
        netti=tuple(NettoRapporto(n["rapporto"], Decimal(n["netto"])) for n in dati["netti"]),
        esclusi=tuple(Escluso(Importo.da_dizionario(e["importo"]), e["motivo"]) for e in dati["esclusi"]),
        fermi=tuple(RapportoFermo(f["rapporto"], f["motivo"]) for f in dati["fermi"]),
        dati_mancanti=tuple(DatoMancante(d["tipo"], d["soggetto"], d["motivo"]) for d in dati["dati_mancanti"]),
        avvisi=tuple(_avviso_da_dizionario(a) for a in dati["avvisi"]),
        righe_proposta=tuple(
            RigaProposta(
                r["piano_dei_conti"],
                r["missione"],
                r["programma"],
                tuple(r["impegno"]) if r["impegno"] else None,
                tuple(
                    RiferimentoRiga(
                        versione_id, rif["rapporto"], rif["istituto"], rif["periodo"], tuple(rif["esiti_confrontati"])
                    )
                    for rif in r["riferimenti"]
                ),
                Decimal(r["totale"]),
            )
            for r in dati.get("righe_proposta", [])
        ),
        id=versione_id,
        registrato_il=registrato,
    )


def leggi_versione(registro: Registro, versione_id: int) -> VersioneProposta:
    valuta, registrato, dati = registro.versione_registrata(versione_id)
    return _da_dizionario(versione_id, valuta, registrato, dati)


# Costruzione della versione

@dataclass(frozen=True)
class _PerRapporto:
    righe: tuple[RigaComposizione, ...]
    netto: Decimal
    mancanti: tuple[DatoMancante, ...]
    avvisi: tuple[Avviso, ...]
    anno: int
    ultimo_dell_anno: bool


def _e_reddito(importo: Importo) -> bool:
    return importo.derivazione.maturazione not in MATURAZIONI_DERIVATE


def _chiavi_pagate(registro: Registro, istante: datetime) -> set[tuple]:
    return {riga.chiave for esito in registro.esiti(TipoEsito.PAGATO, istante) for riga in esito.righe}


def _esiti_con_la_stessa_chiave(registro: Registro, importo: Importo, istante: datetime) -> tuple[int, ...]:
    """Gli esiti pagati che già comprendono una riga dello stesso istituto e periodo: l'importo nuovo è una differenza."""
    return tuple(
        esito.id
        for esito in registro.esiti(TipoEsito.PAGATO, istante)
        if any(riga.chiave == importo.chiave for riga in esito.righe)
    )


def _ultimo_dell_anno(registro: Registro, anno: int, valuta: date, istante: datetime) -> tuple[bool, bool]:
    """(è l'ultimo pagamento dell'anno, manca il fatto dell'ente): serve la data prevista dell'anno d'imposta."""
    data = registro.ultimo_pagamento_dell_anno(anno, istante)
    if data is not None:
        return valuta >= data, False
    a_dicembre = (valuta.year, valuta.month) == (anno, 12)
    entro_il_12_gennaio = (valuta.year, valuta.month) == (anno + 1, 1) and valuta.day <= 12
    return False, a_dicembre or entro_il_12_gennaio


def _contributi_gia_compresi(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime
) -> tuple[dict[str, Decimal], dict[str, list[int]], dict[str, Importo]]:
    """Contributi già nei pagamenti del rapporto con valuta nel mese: somma, esiti e ultima riga per istituto."""
    pagamenti = registro.pagamenti(rapporto, istante)
    somme: dict[str, Decimal] = {}
    fonti: dict[str, list[int]] = {}
    ultime: dict[str, Importo] = {}
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        fatto = pagamenti.get(esito.id)
        if fatto is None or not mese.primo_giorno <= fatto.valido_dal <= mese.ultimo_giorno:
            continue
        for riga in esito.righe:
            if riga.rapporto == rapporto and riga.istituto in corpus.istituti_di_cassa:
                somme[riga.istituto] = somme.get(riga.istituto, Decimal(0)) + riga.valore
                if esito.id not in fonti.setdefault(riga.istituto, []):
                    fonti[riga.istituto].append(esito.id)
                ultime[riga.istituto] = riga
    return somme, fonti, ultime


def _contributi_per_differenza(
    registro: Registro, corpus: Corpus, rapporto: str, valuta: date, reddito: list[Importo], istante: datetime
) -> tuple[Importo, ...]:
    """Contributi della denuncia in simulazione alla valuta prevista, meno quelli già compresi nel mese."""
    if not corpus.basi():
        return ()
    mese = Mese(valuta.year, valuta.month)
    ipotetiche = tuple(replace(importo, data_pagamento=valuta) for importo in reddito)
    denuncia = calcola_denuncia(registro, corpus, rapporto, mese, istante, ipotetiche)
    dovuti: dict[str, list[Importo]] = {}
    for periodo in denuncia.periodi:
        for riga in periodo.contributi:
            dovuti.setdefault(riga.istituto, []).append(riga)
    gia, fonti, ultime = _contributi_gia_compresi(registro, corpus, rapporto, mese, istante)
    risultato = []
    for istituto in sorted(dovuti.keys() | gia.keys()):
        righe = dovuti.get(istituto, [])
        differenza = sum((riga.valore for riga in righe), Decimal(0)) - gia.get(istituto, Decimal(0))
        if differenza == 0:
            continue
        base = _somma_righe(righe) if righe else ultime[istituto]
        risultato.append(replace(base, valore=differenza, esiti_confrontati=tuple(fonti.get(istituto, ()))))
    return tuple(risultato)


def _righe_di_composizione(corpus: Corpus, importi, valuta: date) -> tuple[RigaComposizione, ...]:
    """Una dichiarazione assente ferma la proposta nominando l'istituto; un istituto intermedio non entra."""
    righe = []
    for importo in importi:
        dichiarazione = corpus.composizione(importo.istituto, valuta)
        if dichiarazione is None:
            raise ComposizioneMancante(
                f"Istituto {importo.istituto}: nessuna dichiarazione di composizione per un pagamento del {valuta}"
            )
        if dichiarazione.intermedio:
            continue
        righe.append(
            RigaComposizione(
                importo,
                dichiarazione.natura,
                dichiarazione.effetto,
                dichiarazione.destinatario,
                dichiarazione.canale,
                dichiarazione.riferimento,
            )
        )
    return tuple(righe)


@dataclass(frozen=True)
class _VoceDiSpesa:
    """Una riga di composizione di spesa con la sua classificazione e l'origine dell'impegno del suo istituto."""

    riga: RigaComposizione
    piano_dei_conti: str
    missione: str
    programma: str
    origine: str

    @property
    def gruppo(self) -> tuple[str, str, str, str]:
        return (self.piano_dei_conti, self.missione, self.programma, self.origine)


def _voci_di_spesa(
    registro: Registro, corpus: Corpus, righe, valuta: date, istante: datetime
) -> tuple[list[_VoceDiSpesa], dict[tuple[str, str], DatoMancante]]:
    """Le righe di spesa del Titolo 1 con la classificazione dell'istituto e il programma del rapporto (ADR 0031).

    Un istituto di spesa senza classificazione valida alla valuta ferma la proposta nominandolo. Senza il
    programma del rapporto missione e programma restano vuoti, e il dato manca.
    """
    voci: list[_VoceDiSpesa] = []
    mancanti: dict[tuple[str, str], DatoMancante] = {}
    for riga in righe:
        if riga.natura not in NATURE_DI_SPESA:
            continue
        classificazione = corpus.classificazione(riga.istituto, valuta)
        if classificazione is None:
            raise ClassificazioneMancante(
                f"Istituto {riga.istituto}: nessuna dichiarazione di classificazione per un pagamento del {valuta}"
            )
        programma = registro.programma_del_rapporto(riga.rapporto, valuta, istante)
        if programma is None:
            mancanti.setdefault(
                ("programma_rapporto", riga.rapporto),
                DatoMancante(
                    "programma_rapporto",
                    riga.rapporto,
                    f"manca il programma del rapporto {riga.rapporto} per un pagamento del {valuta}",
                ),
            )
        missione, _, voce = (programma or "").partition(".")
        voci.append(_VoceDiSpesa(riga, classificazione.piano_dei_conti, missione, voce, classificazione.origine_impegno))
    return voci, mancanti


def _nome_classificazione(piano: str, missione: str, programma: str) -> str:
    return f"{piano} {missione}.{programma}"


def _righe_di_proposta(voci: list[_VoceDiSpesa], decisioni: dict) -> tuple[RigaProposta, ...]:
    """Una riga per classificazione e impegno: i riferimenti alle righe di composizione e il totale."""
    righe: dict[tuple, tuple[list[RiferimentoRiga], Decimal]] = {}
    for voce in voci:
        impegno = decisioni[voce.gruppo].impegno if voce.gruppo in decisioni else None
        chiave = (voce.piano_dei_conti, voce.missione, voce.programma, impegno.chiave if impegno else None)
        riferimenti, totale = righe.setdefault(chiave, ([], Decimal(0)))
        importo = voce.riga.importo
        riferimenti.append(RiferimentoRiga(0, importo.rapporto, importo.istituto, str(importo.periodo), importo.esiti_confrontati))
        righe[chiave] = (riferimenti, totale + importo.valore)
    return tuple(
        RigaProposta(piano, missione, programma, impegno, tuple(riferimenti), totale)
        for (piano, missione, programma, impegno), (riferimenti, totale) in sorted(
            righe.items(), key=lambda voce: (voce[0][:3], voce[0][3] or (0, 0))
        )
    )


def _proposta(
    registro: Registro, corpus: Corpus, righe, valuta: date, istante: datetime
) -> tuple[tuple[RigaProposta, ...], dict[tuple[str, str], DatoMancante], list[RapportoFermo]]:
    """Righe di proposta, dati mancanti e rapporti fermi dalla regola di abbinamento (ADR 0031).

    Si decide una volta sola, sulla riga intera di ogni classificazione. Se gli impegni adatti non sono
    capienti, i rapporti con importi in quella riga restano tra i fermi e le righe si ricostruiscono senza
    di loro, sugli stessi impegni: gli altri rapporti proseguono.
    """
    voci, mancanti = _voci_di_spesa(registro, corpus, righe, valuta, istante)
    disponibilita = DisponibilitaImpegni(registro, istante)
    totali: dict[tuple[str, str, str, str], Decimal] = {}
    for voce in voci:
        totali[voce.gruppo] = totali.get(voce.gruppo, Decimal(0)) + voce.riga.importo.valore
    decisioni: dict[tuple[str, str, str, str], Abbinamento] = {}
    motivi: dict[str, list[str]] = {}
    for gruppo in sorted(totali):
        piano, missione, programma, origine = gruppo
        if not missione:
            continue  # senza programma del rapporto la riga resta senza impegno: il dato manca già
        decisione = disponibilita.abbina(piano, missione, programma, origine, valuta.year, totali[gruppo])
        decisioni[gruppo] = decisione
        if decisione.impegno is None and decisione.adatti:
            motivo = (
                f"classificazione {_nome_classificazione(piano, missione, programma)}: nessun impegno capiente per "
                f"{totali[gruppo]}, mancano {decisione.mancante}"
            )
            for voce in voci:
                if voce.gruppo == gruppo:
                    motivi.setdefault(voce.riga.rapporto, []).append(motivo)
    fermi = [RapportoFermo(rapporto, "; ".join(dict.fromkeys(m))) for rapporto, m in sorted(motivi.items())]
    if fermi:
        voci = [voce for voce in voci if voce.riga.rapporto not in motivi]
        mancanti = {
            chiave: dato
            for chiave, dato in mancanti.items()
            if dato.tipo != "programma_rapporto" or dato.soggetto not in motivi
        }
    for gruppo in sorted({voce.gruppo for voce in voci}):
        piano, missione, programma, origine = gruppo
        if missione and decisioni[gruppo].adatti == 0:
            nome = _nome_classificazione(piano, missione, programma)
            quale = "senza atto" if origine == AUTOMATICO else f"con atto {origine}"
            mancanti.setdefault(
                ("impegno", nome),
                DatoMancante(
                    "impegno", nome, f"nessun impegno noto per la classificazione {nome}, {quale}, per un pagamento del {valuta}"
                ),
            )
    return _righe_di_proposta(voci, decisioni), mancanti, fermi


def _rapporto(
    registro: Registro, corpus: Corpus, rapporto: str, importi: list[Importo], valuta: date, istante: datetime
) -> _PerRapporto:
    """Fisco, contributi, righe e netto di un rapporto; ogni ErroreCalcolo ferma questo rapporto e non gli altri."""
    attribuiti = attribuisci_reddito(corpus, importi, valuta)
    reddito = [importo for importo in attribuiti if _e_reddito(importo)]
    if not reddito:
        raise ErroreCalcolo(f"Rapporto {rapporto}: nessun importo da tassare nel pagamento")
    anni = {importo.anno_imposta for importo in reddito}
    if len(anni) > 1:
        raise CasoNonModellato(f"Rapporto {rapporto}: caso non modellato, un pagamento con più anni d'imposta")
    (anno,) = anni

    ultimo, manca_ultimo = _ultimo_dell_anno(registro, anno, valuta, istante)
    # I contributi leggono solo le basi previdenziali, mai la ritenuta: si calcolano prima, perché la ritenuta li deduce.
    contributi = _contributi_per_differenza(registro, corpus, rapporto, valuta, reddito, istante)
    persona = registro.persona_del_rapporto(rapporto, istante)
    finale = persona is not None and pagamento_finale(registro, corpus, persona, anno, valuta, istante)
    manca_ultimo = manca_ultimo and not finale
    fiscale = calcola_fiscale(registro, corpus, rapporto, [*attribuiti, *contributi], valuta, ultimo or finale, istante)
    fiscali = [fiscale.ritenuta] + ([fiscale.conguaglio] if fiscale.conguaglio is not None else [])
    fiscali = [replace(i, esiti_confrontati=_esiti_con_la_stessa_chiave(registro, i, istante)) for i in fiscali]

    righe = _righe_di_composizione(corpus, [*attribuiti, *fiscali, *fiscale.addizionali, *contributi], valuta)
    netto = sum((riga.sul_netto for riga in righe), Decimal(0))
    if netto < 0:
        raise CasoNonModellato(f"Rapporto {rapporto}: caso non modellato, netto negativo di {netto} nel pagamento del {valuta}")

    mancanti = []
    if manca_ultimo:
        mancanti.append(
            DatoMancante(
                "ultimo_pagamento_dell_anno",
                "ente",
                f"manca il fatto dell'ente per l'anno d'imposta {anno}: la valuta prevista {valuta} cade "
                "tra il 1° dicembre e il 12 gennaio",
            )
        )
    if any(riga.destinatario == "beneficiario" and riga.canale == "accredito" for riga in righe):
        persona = registro.persona_del_rapporto(rapporto, istante)
        if registro.vigente_persona(persona, TIPO_IBAN, valuta, istante) is None:
            mancanti.append(
                DatoMancante("iban_beneficiario", persona, f"manca l'IBAN della persona {persona} per un pagamento del {valuta}")
            )
    return _PerRapporto(righe, netto, tuple(mancanti), fiscale.avvisi, anno, ultimo)


def _persone_assenti(registro: Registro, anno: int, presenti: set[str], istante: datetime) -> list[Avviso]:
    """Chi ha già redditi pagati nell'anno d'imposta ma non è in questo ultimo pagamento: niente conguaglio per lui."""
    pagate: set[str] = set()
    conguagliate: set[str] = set()
    for esito in registro.esiti(TipoEsito.PAGATO, istante):
        for riga in esito.righe:
            persona = registro.persona_del_rapporto(riga.rapporto, istante)
            if persona is None or riga.anno_imposta != anno:
                continue
            if _e_reddito(riga):
                pagate.add(persona)
            elif riga.derivazione.maturazione == "conguaglio":
                conguagliate.add(persona)  # già conguagliata, per esempio alla cessazione: non è assente
    return [
        Avviso(
            AVVISO_PERSONA_ASSENTE,
            f"Persona {persona}: assente dall'ultimo pagamento dell'anno d'imposta {anno}, "
            "in questo pagamento non ha il conguaglio",
            persona,
            anno,
        )
        for persona in sorted(pagate - presenti - conguagliate)
    ]


def _condizione_mancante(registro: Registro, corpus: Corpus, importo: Importo, valuta: date, istante: datetime) -> str | None:
    """Il motivo per cui l'importo non entra in una versione: il fatto che il corpus richiede manca nel suo periodo."""
    condizione = corpus.condizione_di_proposta(importo.istituto, valuta)
    if condizione is None:
        return None
    vigenti = registro.vigenti_per_giorno(importo.rapporto, condizione.fatto, importo.periodo, istante)
    if all(fatto is not None for fatto in vigenti):
        return None
    return (
        f"manca il fatto {condizione.fatto} per {importo.periodo}: l'importo resta calcolato ma non entra in una "
        f"versione di proposta ({condizione.riferimento})"
    )


def _costruisci(
    registro: Registro, corpus: Corpus, valuta: date, importi, esclusi, istante: datetime, con_proposta: bool = True
) -> ContenutoVersione:
    """Funzione pura di registro, corpus e istante: non scrive nulla.

    `con_proposta` falso salta righe di proposta e abbinamento: il ricalcolo che cerca una versione superata
    confronta le righe di composizione, e la versione stessa conterebbe nella disponibilità degli impegni.
    """
    elenco_esclusi = list(esclusi)
    gia_pagati = _chiavi_pagate(registro, istante)
    per_rapporto: dict[str, list[Importo]] = {}
    for importo in importi:
        if not importo.esiti_confrontati and importo.chiave in gia_pagati:
            elenco_esclusi.append(Escluso(importo, MOTIVO_GIA_PAGATO))
            continue
        motivo = _condizione_mancante(registro, corpus, importo, valuta, istante)
        if motivo is not None:
            elenco_esclusi.append(Escluso(importo, motivo))
            continue
        per_rapporto.setdefault(importo.rapporto, []).append(importo)
    persone = {rapporto: registro.persona_del_rapporto(rapporto, istante) for rapporto in per_rapporto}

    righe: list[RigaComposizione] = []
    netti: list[NettoRapporto] = []
    fermi: list[RapportoFermo] = []
    mancanti: dict[tuple[str, str], DatoMancante] = {}
    avvisi: list[Avviso] = []
    anni_con_ultimo: set[int] = set()
    for rapporto in sorted(per_rapporto):
        try:
            altri = sorted(r for r, p in persone.items() if p is not None and p == persone[rapporto] and r != rapporto)
            if altri:
                raise CasoNonModellato(
                    f"Rapporto {rapporto}: caso non modellato, più rapporti della stessa persona nella stessa versione "
                    f"(anche {altri[0]}): la ritenuta è per persona e per pagamento"
                )
            dati = _rapporto(registro, corpus, rapporto, per_rapporto[rapporto], valuta, istante)
        except ErroreCalcolo as errore:
            fermi.append(RapportoFermo(rapporto, str(errore)))
            continue
        righe.extend(dati.righe)
        netti.append(NettoRapporto(rapporto, dati.netto))
        avvisi.extend(dati.avvisi)
        for dato in dati.mancanti:
            mancanti.setdefault((dato.tipo, dato.soggetto), dato)
        if dati.ultimo_dell_anno:
            anni_con_ultimo.add(dati.anno)
    for anno in sorted(anni_con_ultimo):
        avvisi.extend(_persone_assenti(registro, anno, {p for p in persone.values() if p is not None}, istante))
    righe_proposta: tuple[RigaProposta, ...] = ()
    if con_proposta:
        righe_proposta, mancanti_proposta, fermi_proposta = _proposta(registro, corpus, righe, valuta, istante)
        mancanti.update(mancanti_proposta)
        if fermi_proposta:
            fermi.extend(fermi_proposta)
            fuori = {fermo.rapporto for fermo in fermi_proposta}
            righe = [riga for riga in righe if riga.rapporto not in fuori]
            netti = [netto for netto in netti if netto.rapporto not in fuori]
    return ContenutoVersione(
        valuta_prevista=valuta,
        righe=tuple(righe),
        netti=tuple(netti),
        esclusi=tuple(elenco_esclusi),
        fermi=tuple(fermi),
        dati_mancanti=tuple(mancanti.values()),
        avvisi=tuple(avvisi),
        righe_proposta=righe_proposta,
    )


def emetti_versione(
    registro: Registro, corpus: Corpus, valuta_prevista: date, importi, esclusi=()
) -> VersioneProposta:
    """Emette una versione di proposta per gli `importi` calcolati, con una sola valuta prevista.

    Gli importi sono quelli di `calcola`, `calcola_annuale` o `differenze`; quelli già in un esito
    pagato restano fuori, con il motivo, a meno che siano una differenza. `esclusi` sono gli importi
    che il chiamante lascia fuori, per esempio perché in attesa d'atto: restano visibili col motivo.
    Una dichiarazione di composizione assente ferma la proposta; un rapporto che non si può comporre,
    o ha il netto negativo, resta tra i `fermi` senza fermare gli altri.
    """
    istante = registro.adesso()
    contenuto = _costruisci(registro, corpus, valuta_prevista, tuple(importi), tuple(esclusi), istante)
    if not contenuto.righe:
        motivi = "; ".join(f.motivo for f in contenuto.fermi) or "nessun importo da pagare"
        raise ErroreRegistro(f"Nessun rapporto da portare nella versione: {motivi}")
    versione_id, registrato = registro.registra_versione(valuta_prevista, _in_dizionario(contenuto))
    return _da_dizionario(versione_id, valuta_prevista, registrato, _in_dizionario(contenuto))


# Stati della versione

def stato_versione(registro: Registro, versione_id: int, noto_al: datetime | None = None) -> StatoVersione:
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    stati = registro.stati_versione(versione_id, istante)
    if not stati:
        raise ErroreRegistro(f"Versione di proposta {versione_id} inesistente o non ancora nota al {istante}")
    return StatoVersione(stati[-1][0])


def _da_inviata(registro: Registro, versione_id: int, azione: str) -> None:
    stato = stato_versione(registro, versione_id)
    if stato is not StatoVersione.INVIATA:
        raise ErroreRegistro(f"Versione {versione_id}: non si {azione} una versione {stato}")


def conferma_versione(registro: Registro, versione_id: int) -> None:
    """La Ragioneria accetta la versione. Non corregge mai un importo: l'importo si corregge solo con un fatto."""
    _da_inviata(registro, versione_id, "conferma")
    registro.registra_stato_versione(versione_id, StatoVersione.CONFERMATA)


def respingi_versione(registro: Registro, versione_id: int, motivo: str) -> None:
    if not motivo or not motivo.strip():
        raise ErroreRegistro("Il motivo del rifiuto è obbligatorio")
    _da_inviata(registro, versione_id, "respinge")
    registro.registra_stato_versione(versione_id, StatoVersione.RESPINTA, motivo)


def _firme(righe) -> frozenset:
    """Ciò che una riga dice, senza l'istante in cui è stata calcolata."""
    return frozenset(
        (
            riga.importo.chiave,
            riga.importo.esiti_confrontati,
            riga.importo.valore,
            riga.importo.anno_imposta,
            riga.importo.categoria_reddito,
            riga.natura,
            riga.effetto,
            riga.destinatario,
            riga.canale,
        )
        for riga in righe
    )


def _eventi_della_versione(registro: Registro, tipo: str, versione_id: int, istante: datetime) -> list[Evento]:
    return [evento for evento in registro.eventi(tipo, istante) if evento.versione_id == versione_id]


def controlla_superata(
    registro: Registro, corpus: Corpus, versione_id: int, importi, esclusi=(), noto_al: datetime | None = None
) -> bool:
    """Confronta le righe della versione con un ricalcolo all'istante `noto_al`; se differiscono, la versione è superata.

    Gli `importi` sono quelli ricalcolati dal chiamante, come per l'emissione. Vale anche per una
    versione già confermata, finché non c'è un evento di pagamento: dopo, il denaro reale ha già deciso.
    La Ragioneria non corregge importi: una versione superata si sostituisce con una nuova.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    stato = stato_versione(registro, versione_id, istante)
    if stato is StatoVersione.SUPERATA:
        return True
    if stato is StatoVersione.RESPINTA:
        raise ErroreRegistro(f"Versione {versione_id}: respinta, non c'è altro da ricalcolare")
    if _eventi_della_versione(registro, TIPO_PAGAMENTO_ESEGUITO, versione_id, istante):
        return False
    versione = leggi_versione(registro, versione_id)
    ricalcolo = _costruisci(
        registro, corpus, versione.valuta_prevista, tuple(importi), tuple(esclusi), istante, con_proposta=False
    )
    if _firme(ricalcolo.righe) == _firme(versione.righe):
        return False
    registro.registra_stato_versione(
        versione_id, StatoVersione.SUPERATA, f"le righe differiscono dal ricalcolo noto al {istante:%Y-%m-%d %H:%M}"
    )
    return True


# Eventi di ritorno

def _evento_gia_noto(registro: Registro, chiave: str, tipo: str, contenuto: dict) -> Evento | None:
    """Stesso identificativo e stesso contenuto: nessun effetto. Contenuto diverso: errore, nessun fatto nuovo."""
    return registro.evento_identico(chiave, tipo, contenuto)


@dataclass(frozen=True)
class PagamentoEseguito:
    esito: Esito
    avvisi: tuple[Avviso, ...] = ()


def _effetti_della_valuta(
    registro: Registro, corpus: Corpus, versione: VersioneProposta, valuta: date, rapporti, istante: datetime
) -> tuple[list[Avviso], set[str]]:
    """Valuta reale diversa dalla prevista: avvisi, e le persone il cui anno d'imposta non è più quello previsto."""
    avvisi: list[Avviso] = []
    ferme: set[str] = set()
    previsto = versione.valuta_prevista
    for rapporto in rapporti:
        persona = registro.persona_del_rapporto(rapporto, istante)
        anno_diverso = False
        competenza_ko: str | None = None
        for riga in versione.righe_del_rapporto(rapporto):
            importo = riga.importo
            if not _e_reddito(importo):
                continue
            try:
                reale = anno_imposta(corpus, importo.categoria_reddito, valuta)
            except RedditoMancante:
                reale = None
            anno_diverso = anno_diverso or reale != importo.anno_imposta
            if not anno_diverso and competenza_ko is None:
                try:  # ADR 0018: il controllo della competenza si ripete al pagamento eseguito
                    _controlla_competenza(corpus, importo, reale, valuta)
                except CasoNonModellato as errore:
                    competenza_ko = str(errore)
        if competenza_ko is not None and not anno_diverso:
            if persona is not None:
                ferme.add(persona)
            avvisi.append(
                Avviso(
                    AVVISO_COMPETENZA_AL_PAGAMENTO,
                    f"Rapporto {rapporto}: alla valuta reale {valuta} la competenza non è più ammessa ({competenza_ko}): "
                    "il calcolo fiscale della persona si ferma",
                    persona or rapporto,
                )
            )
        elif anno_diverso:
            if persona is not None:
                ferme.add(persona)
            avvisi.append(
                Avviso(
                    AVVISO_ANNO_DIVERSO,
                    f"Rapporto {rapporto}: pagato il {valuta}, in un anno d'imposta diverso dal previsto per la "
                    f"valuta {previsto}: il calcolo fiscale della persona si ferma",
                    persona or rapporto,
                )
            )
        elif (valuta.year, valuta.month) != (previsto.year, previsto.month):
            avvisi.append(
                Avviso(
                    AVVISO_ALTRO_MESE,
                    f"Rapporto {rapporto}: pagato il {valuta} invece del {previsto}, in un altro mese: "
                    "le differenze su ritenute e contributi si regolano sul pagamento successivo",
                    persona or rapporto,
                )
            )
    return avvisi, ferme


def registra_pagamento_eseguito(
    registro: Registro,
    corpus: Corpus,
    chiave: str,
    adattatore: str,
    versione_id: int,
    valuta: date,
    rapporti,
) -> PagamentoEseguito:
    """Evento di ritorno: i `rapporti` pagati della versione, con la valuta reale.

    Crea l'esito pagato con tutte le righe di composizione dei soli rapporti pagati, e per ognuno la
    data di pagamento. Il denaro reale vince: vale anche su una versione superata. Se l'anno d'imposta
    sulla valuta reale non è quello previsto, l'esito resta com'era e il calcolo fiscale della persona
    si ferma (fatto della persona, ricavabile dal registro).
    """
    elenco = tuple(sorted(set(rapporti)))
    contenuto = {"versione": versione_id, "valuta": valuta.isoformat(), "rapporti": list(elenco)}
    istante = registro.adesso()
    versione = leggi_versione(registro, versione_id)
    gia = _evento_gia_noto(registro, chiave, TIPO_PAGAMENTO_ESEGUITO, contenuto)
    if gia is not None:
        avvisi, _ = _effetti_della_valuta(registro, corpus, versione, valuta, elenco, istante)
        return PagamentoEseguito(registro.esito(gia.esito_id), tuple(avvisi))

    if not elenco:
        raise ErroreRegistro("Un evento di pagamento elenca almeno un rapporto")
    fuori = [rapporto for rapporto in elenco if rapporto not in versione.rapporti]
    if fuori:
        raise ErroreRegistro(f"Versione {versione_id}: i rapporti {fuori} non sono tra quelli portati dalla versione")
    if not any(stato == StatoVersione.CONFERMATA for stato, _, _ in registro.stati_versione(versione_id, istante)):
        raise ErroreRegistro(f"Versione {versione_id}: il pagamento vale per una versione confermata, questa non lo è mai stata")
    for evento in _eventi_della_versione(registro, TIPO_PAGAMENTO_ESEGUITO, versione_id, istante):
        doppi = sorted(set(evento.contenuto["rapporti"]) & set(elenco))
        if doppi:
            raise ErroreRegistro(
                f"Versione {versione_id}: i rapporti {doppi} risultano già pagati dall'evento {evento.chiave}"
            )

    avvisi, ferme = _effetti_della_valuta(registro, corpus, versione, valuta, elenco, istante)
    righe = [riga.importo for rapporto in elenco for riga in versione.righe_del_rapporto(rapporto)]
    with registro.atomico():
        esito = registro.registra_esito(TipoEsito.PAGATO, valuta, righe)
        for rapporto in elenco:
            registro.registra_pagamento(rapporto, esito.id, valuta)
        for persona in sorted(ferme):
            registro.registra_fatto_persona(persona, TIPO_ANNO_IMPOSTA_DIVERSO, Decimal(esito.id), valuta, valuta)
        registro.registra_evento(chiave, TIPO_PAGAMENTO_ESEGUITO, contenuto, adattatore, versione_id, esito.id)
    return PagamentoEseguito(esito, tuple(avvisi))


class StatoDelega(StrEnum):
    TRASMESSA = "trasmessa"
    ACCETTATA = "accettata"
    SOSPESA = "sospesa"
    ADDEBITATA = "addebitata"
    SCARTATA = "scartata"


def registra_ricevuta_delega(
    registro: Registro, chiave: str, adattatore: str, versamento: str, fase: str, esito: str
) -> Evento:
    """Ricevuta di una fase della delega. La delega non esiste ancora nel modello (#54): il versamento è un identificativo opaco."""
    if not versamento or not versamento.strip():
        raise ErroreRegistro("La ricevuta indica il versamento")
    if fase not in FASI_DELEGA:
        raise ErroreRegistro(f"Fase {fase!r} non ammessa; ammesse {list(FASI_DELEGA)}")
    if esito not in ESITI_RICEVUTA:
        raise ErroreRegistro(f"Esito {esito!r} non ammesso; ammessi {list(ESITI_RICEVUTA)}")
    contenuto = {"versamento": versamento, "fase": fase, "esito": esito}
    gia = _evento_gia_noto(registro, chiave, TIPO_RICEVUTA_DELEGA, contenuto)
    return gia or registro.registra_evento(chiave, TIPO_RICEVUTA_DELEGA, contenuto, adattatore)


def stato_delega(registro: Registro, versamento: str, noto_al: datetime | None = None) -> StatoDelega:
    """Vista delle ricevute: per ogni fase vale l'ultima. Una negativa scarta la delega; senza ricevute è trasmessa."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    per_fase: dict[str, str] = {}
    for evento in registro.eventi(TIPO_RICEVUTA_DELEGA, istante):
        if evento.contenuto["versamento"] == versamento:
            per_fase[evento.contenuto["fase"]] = evento.contenuto["esito"]
    esiti = set(per_fase.values())
    if "negativo" in esiti:
        return StatoDelega.SCARTATA
    if "sospeso" in esiti:
        return StatoDelega.SOSPESA
    if per_fase.get("addebito") == "positivo":
        return StatoDelega.ADDEBITATA
    if "positivo" in esiti:
        return StatoDelega.ACCETTATA
    return StatoDelega.TRASMESSA


def _riga_riferita(registro: Registro, riferimento: RiferimentoRiga, canale: str, istante: datetime) -> Importo:
    """La riga di composizione indicata, ammessa solo se è a un terzo, sul canale giusto, di un rapporto pagato.

    Sul canale F24EP e' ammessa anche una riga a credito del sostituto (rimborso 730, credito), anche se e' sul netto
    verso il beneficiario: la delega la compensa, e' la stessa riga che il lavoratore incassa (ADR 0023).
    """
    versione = leggi_versione(registro, riferimento.versione_id)
    trovata = next(
        (r for r in versione.righe if versione.riferimento(r) == riferimento),
        None,
    )
    if trovata is None:
        raise ErroreRegistro(f"La riga {riferimento.in_dizionario()} non è nella versione {riferimento.versione_id}")
    a_credito = canale == "f24ep" and trovata.natura in NATURE_A_CREDITO
    if not a_credito and (trovata.destinatario != "terzo" or trovata.canale != canale):
        raise ErroreRegistro(
            f"La riga {trovata.istituto} del rapporto {trovata.rapporto} non è un versamento a un terzo sul canale {canale}"
        )
    pagati = {
        rapporto
        for evento in _eventi_della_versione(registro, TIPO_PAGAMENTO_ESEGUITO, riferimento.versione_id, istante)
        for rapporto in evento.contenuto["rapporti"]
    }
    if trovata.rapporto not in pagati:
        raise ErroreRegistro(f"Il rapporto {trovata.rapporto} non risulta pagato nella versione {riferimento.versione_id}")
    return trovata.importo


def registra_versamento_eseguito(
    registro: Registro,
    chiave: str,
    adattatore: str,
    versamento: str,
    data: date,
    righe,
    canale: str,
    provenienza: str,
) -> Esito:
    """Evento di versamento eseguito: le `righe` di composizione versate ai terzi, alla data reale.

    Crea l'esito versato una sola volta per versamento. Una regolarizzazione successiva è registrata e
    non crea un secondo esito; da sola vale come versamento eseguito, e la provenienza lo dice.
    Un addebito o un bonifico dopo che l'esito è già nato (da una regolarizzazione) è un caso non modellato.
    """
    if not versamento or not versamento.strip():
        raise ErroreRegistro("Il versamento va indicato")
    if canale not in CANALI_DI_VERSAMENTO:
        raise ErroreRegistro(f"Canale {canale!r} non ammesso per un versamento; ammessi {list(CANALI_DI_VERSAMENTO)}")
    if provenienza not in PROVENIENZE_DI_VERSAMENTO:
        raise ErroreRegistro(f"Provenienza {provenienza!r} non ammessa; ammesse {list(PROVENIENZE_DI_VERSAMENTO)}")
    riferimenti = sorted(
        (r.in_dizionario() for r in righe), key=lambda d: (d["versione"], d["rapporto"], d["istituto"], d["periodo"])
    )
    if not riferimenti:
        raise ErroreRegistro("Un versamento elenca almeno una riga")
    contenuto = {
        "versamento": versamento,
        "data": data.isoformat(),
        "righe": riferimenti,
        "canale": canale,
        "provenienza": provenienza,
    }
    gia = _evento_gia_noto(registro, chiave, TIPO_VERSAMENTO_ESEGUITO, contenuto)
    if gia is not None:
        return registro.esito(gia.esito_id)

    istante = registro.adesso()
    if canale == "f24ep" and stato_delega(registro, versamento, istante) is StatoDelega.SCARTATA:
        raise ErroreRegistro(f"Versamento {versamento}: la delega è scartata, gli importi vanno versati con una nuova")
    for evento in registro.eventi(TIPO_VERSAMENTO_ESEGUITO, istante):
        if evento.contenuto["versamento"] != versamento and any(r in evento.contenuto["righe"] for r in riferimenti):
            raise ErroreRegistro(f"Versamento {versamento}: una riga è già versata dal versamento {evento.contenuto['versamento']}")
    importi = [
        _riga_riferita(
            registro,
            RiferimentoRiga(
                d["versione"], d["rapporto"], d["istituto"], d["periodo"], tuple(d["esiti_confrontati"])
            ),
            canale,
            istante,
        )
        for d in riferimenti
    ]
    precedente = next(
        (e for e in registro.eventi(TIPO_VERSAMENTO_ESEGUITO, istante) if e.contenuto["versamento"] == versamento),
        None,
    )
    with registro.atomico():
        if precedente is None:
            esito = registro.registra_esito(TipoEsito.VERSATO, data, importi)
        elif provenienza == "regolarizzazione":
            esito = registro.esito(precedente.esito_id)
        else:
            raise ErroreRegistro(
                f"Versamento {versamento}: l'esito versato {precedente.esito_id} esiste già "
                f"(provenienza {precedente.contenuto['provenienza']}, evento {precedente.chiave}): caso non modellato"
            )
        registro.registra_evento(chiave, TIPO_VERSAMENTO_ESEGUITO, contenuto, adattatore, esito_id=esito.id)
    return esito


# Contributi trattenuti e denuncia

@dataclass(frozen=True)
class ScostamentoContributi:
    rapporto: str
    mese: Mese
    istituto: str
    denuncia: Decimal
    trattenuto: Decimal


def segnala_scostamento_contributi(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, noto_al: datetime | None = None
) -> tuple[ScostamentoContributi, ...]:
    """Dove la denuncia del mese non coincide con i contributi compresi negli esiti pagati. Segnala, non corregge."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    denuncia = calcola_denuncia(registro, corpus, rapporto, mese, istante)
    dovuti: dict[str, Decimal] = {}
    for periodo in denuncia.periodi:
        for riga in periodo.contributi:
            dichiarazione = corpus.composizione(riga.istituto, mese.ultimo_giorno)
            if dichiarazione is not None and dichiarazione.intermedio:
                continue  # non entra in nessun esito: non c'è nulla con cui confrontarlo
            dovuti[riga.istituto] = dovuti.get(riga.istituto, Decimal(0)) + riga.valore
    trattenuti, _, _ = _contributi_gia_compresi(registro, corpus, rapporto, mese, istante)
    return tuple(
        ScostamentoContributi(rapporto, mese, istituto, dovuti.get(istituto, Decimal(0)), trattenuti.get(istituto, Decimal(0)))
        for istituto in sorted(dovuti.keys() | trattenuti.keys())
        if dovuti.get(istituto, Decimal(0)) != trattenuti.get(istituto, Decimal(0))
    )
