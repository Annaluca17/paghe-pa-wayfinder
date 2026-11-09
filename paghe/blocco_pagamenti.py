"""Blocco dei pagamenti (art. 48-bis DPR 602/1973, poi art. 144 D.Lgs. 33/2025): verifica e somma sospesa (ADR 0034).

Prima di pagare un netto sopra soglia l'ente verifica presso AdER se il beneficiario ha cartelle non pagate. La
richiesta di verifica e l'esito sono eventi di ritorno della persona (ADR 0025). Questo modulo legge il registro e
il corpus e dice cosa cambia nel pagamento; non scrive nulla. Non conosce la versione di proposta: restituisce
voci che la proposta mette nella composizione.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from datetime import date, datetime, timedelta
from decimal import ROUND_DOWN, Decimal

from .corpus import Corpus, RegolaSommaSospesa, SogliaVerifica
from .errori import ErroreRegistro, ParametroMancante, VerificaMancante
from .modello import MATURAZIONE_ACCANTONAMENTO, TIPO_VERSAMENTO_ESEGUITO, Derivazione, Evento, Importo, TipoEsito
from .registro import Registro
from .tempo import Periodo, in_utc

TIPO_RICHIESTA_VERIFICA = "richiesta_verifica_48bis"
TIPO_ESITO_VERIFICA = "esito_verifica_48bis"

ESITI_VERIFICA = ("non_inadempiente", "inadempiente")

TIPO_ORDINE_VERSAMENTO = "ordine_versamento_48bis"
TIPO_DEBITO_ESTINTO = "debito_estinto_48bis"

ISTITUTO_SOMMA_SOSPESA = "somma_sospesa_48bis"
ISTITUTO_RILASCIO = "rilascio_somma_sospesa_48bis"
NATURA_SOMMA_SOSPESA = "somma_sospesa_48bis"
DESTINATARIO_ENTE = "ente"
CANALE_ACCANTONAMENTO = "accantonamento"

# Nature che concorrono al netto della soglia: lordo meno ritenute fiscali e contributi del lavoratore (ADR 0034).
# Restano fuori rimborsi 730, crediti, rate e trattenute a terzi; le trasferte le dichiara il corpus (`esclusi`).
NATURE_DEL_NETTO = frozenset({"retribuzione", "ritenuta", "addizionale", "contributo_lavoratore"})


def netto_per_la_soglia(righe, esclusi: tuple[str, ...] = ()) -> Decimal:
    """Il netto del singolo pagamento per la soglia: prima di cessioni, delegazioni e pignoramenti."""
    return sum((riga.sul_netto for riga in righe if riga.natura in NATURE_DEL_NETTO and riga.istituto not in esclusi), Decimal(0))


def _soglia(corpus: Corpus, categorie, valuta: date) -> SogliaVerifica | None:
    """La soglia più bassa tra i titoli del pagamento; senza soglia in nessun titolo, nessuna verifica."""
    regole = [corpus.soglia_verifica(categoria, valuta) for categoria in sorted(categorie)]
    return min((r for r in regole if r is not None and r.soglia is not None), key=lambda r: r.soglia, default=None)


def registra_richiesta_verifica(
    registro: Registro, chiave: str, adattatore: str, persona: str, data: date, importo: Decimal, pagamento: date
) -> Evento:
    """Richiesta di verifica ad AdER: la data, il netto comunicato e la valuta del pagamento a cui si riferisce.

    La richiesta vale per quel netto e per quel pagamento (DM 40/2008 art. 2: si indica il numero del pagamento).
    """
    if not persona or not persona.strip():
        raise ErroreRegistro("La richiesta di verifica indica la persona")
    if not isinstance(importo, Decimal) or not importo.is_finite() or importo <= 0:
        raise ErroreRegistro(f"La richiesta di verifica comunica un netto positivo, {importo!r}")
    contenuto = {"persona": persona, "data": data.isoformat(), "importo": str(importo), "pagamento": pagamento.isoformat()}
    return registro.evento_identico(chiave, TIPO_RICHIESTA_VERIFICA, contenuto) or registro.registra_evento(
        chiave, TIPO_RICHIESTA_VERIFICA, contenuto, adattatore
    )


def registra_esito_verifica(
    registro: Registro, chiave: str, adattatore: str, richiesta: str, data: date, esito: str, debito: Decimal | None = None
) -> Evento:
    """Esito della verifica per una richiesta, alla data della comunicazione: non inadempiente, o inadempiente col debito."""
    if esito not in ESITI_VERIFICA:
        raise ErroreRegistro(f"Esito {esito!r} non ammesso; ammessi {list(ESITI_VERIFICA)}")
    origine = registro.evento(richiesta)
    if origine is None or origine.tipo != TIPO_RICHIESTA_VERIFICA:
        raise ErroreRegistro(f"Richiesta di verifica {richiesta!r} sconosciuta")
    if (esito == "inadempiente") != (debito is not None):
        raise ErroreRegistro("L'esito inadempiente porta il debito comunicato, quello non inadempiente no")
    if debito is not None and (not isinstance(debito, Decimal) or not debito.is_finite() or debito <= 0):
        raise ErroreRegistro(f"Il debito comunicato e' un importo positivo, {debito!r}")
    contenuto = {
        "richiesta": richiesta,
        "persona": origine.contenuto["persona"],
        "data": data.isoformat(),
        "esito": esito,
        "debito": str(debito) if debito is not None else None,
    }
    return registro.evento_identico(chiave, TIPO_ESITO_VERIFICA, contenuto) or registro.registra_evento(
        chiave, TIPO_ESITO_VERIFICA, contenuto, adattatore
    )


@dataclass(frozen=True)
class EsitoVerifica:
    """Come si e' risolta la verifica di un pagamento: l'esito comunicato, o il silenzio che vale non inadempiente."""

    inadempiente: bool
    debito: Decimal | None
    comunicato: date | None
    richiesta: str
    netto: Decimal = Decimal(0)


def _e_feriale(corpus: Corpus, giorno: date) -> bool:
    """Non e' domenica ne' festivo del calendario dichiarato per quell'anno (il sabato e' feriale)."""
    calendario = corpus.calendario_festivi(giorno.year)
    if calendario is None:
        raise ParametroMancante(f"Calendario dei festivi {giorno.year}: non dichiarato, i giorni feriali non si contano")
    return giorno.weekday() != 6 and giorno not in calendario.giorni


def _dopo_giorni_feriali(corpus: Corpus, data: date, quanti: int) -> date:
    giorno = data
    while quanti:
        giorno += timedelta(days=1)
        if _e_feriale(corpus, giorno):
            quanti -= 1
    return giorno


def _esito_del_pagamento(
    registro: Registro, corpus: Corpus, persona: str, netto: Decimal, valuta: date, istante: datetime
) -> EsitoVerifica | None:
    """L'esito noto all'istante per la richiesta di questo netto e di questo pagamento; None se non c'e'.

    Senza esito, una richiesta piu' vecchia di `giorni_risposta` giorni feriali alla valuta del pagamento vale come
    non inadempiente (DM 40/2008 art. 3 c. 1).
    """
    for richiesta in registro.eventi(TIPO_RICHIESTA_VERIFICA, istante):
        contenuto = richiesta.contenuto
        if (contenuto["persona"], Decimal(contenuto["importo"]), contenuto["pagamento"]) != (persona, netto, valuta.isoformat()):
            continue
        esiti = [e for e in registro.eventi(TIPO_ESITO_VERIFICA, istante) if e.contenuto["richiesta"] == richiesta.chiave]
        if esiti:
            ultimo = esiti[-1].contenuto
            debito = Decimal(ultimo["debito"]) if ultimo["debito"] is not None else None
            return EsitoVerifica(
                ultimo["esito"] == "inadempiente", debito, date.fromisoformat(ultimo["data"]), richiesta.chiave, netto
            )
        regola = corpus.regola_somma_sospesa(valuta)
        if regola is None:
            raise ParametroMancante(f"Verifica 48-bis: nessuna regola di somma sospesa per un pagamento del {valuta}")
        scadenza = _dopo_giorni_feriali(corpus, date.fromisoformat(contenuto["data"]), regola.giorni_risposta)
        if valuta > scadenza:
            return EsitoVerifica(False, None, None, richiesta.chiave, netto)
    return None


def verifica_del_pagamento(
    registro: Registro, corpus: Corpus, rapporto: str, persona: str, righe, categorie, valuta: date, istante: datetime
) -> EsitoVerifica | None:
    """Il netto per la soglia e' sopra la soglia: serve l'esito. Senza, il rapporto resta fermo.

    Restituisce None se la verifica non serve.
    """
    soglia = _soglia(corpus, categorie, valuta)
    if soglia is None:
        return None
    netto = netto_per_la_soglia(righe, soglia.esclusi)
    if netto <= soglia.soglia:
        return None
    esito = _esito_del_pagamento(registro, corpus, persona, netto, valuta, istante)
    if esito is None:
        raise VerificaMancante(
            f"Rapporto {rapporto}: verifica 48-bis mancante, netto da comunicare {netto} sopra la soglia di "
            f"{soglia.soglia} per un pagamento del {valuta} ({soglia.riferimento})"
        )
    return esito


def importo_sospeso(regola: RegolaSommaSospesa, netto: Decimal, trattenute_a_terzi: Decimal, debito: Decimal) -> Decimal:
    """Il minore tra il debito, la fascia sul netto e quanto resta sotto il tetto dopo le trattenute a terzi (ADR 0034).

    Le trattenute a terzi notificate prima hanno la precedenza: la somma sospesa cede (artt. 2 e 68 DPR 180/1950).
    Il tetto e' arrotondato per difetto al centesimo, come la fascia.
    """
    tetto = (netto * regola.tetto).quantize(Decimal("0.01"), rounding=ROUND_DOWN) - trattenute_a_terzi
    return max(Decimal(0), min(debito, regola.quota_sul_netto(netto), tetto)).quantize(Decimal("0.01"))


def trattenute_per_il_tetto(righe) -> Decimal:
    """Le trattenute a terzi dello stesso pagamento che contano nel tetto: pignoramenti, cessioni, delegazioni.

    I recuperi fiscali (somma esente, trattamento integrativo) hanno natura di trattenuta a terzi ma vanno
    all'erario in F24EP: non sono vincoli sullo stipendio ai sensi del DPR 180/1950.
    """
    return -sum((r.sul_netto for r in righe if r.natura == "trattenuta_terzi" and r.canale != "f24ep"), Decimal(0))


@dataclass(frozen=True)
class VoceDelBlocco:
    """Una riga che il blocco aggiunge alla composizione del pagamento: l'importo e come entra."""

    importo: Importo
    natura: str
    effetto: str
    destinatario: str
    canale: str
    riferimento: str


def _importo_derivato(
    corpus: Corpus, regola: RegolaSommaSospesa, rapporto: str, istituto: str, valuta: date, valore: Decimal,
    formula: str, istante: datetime, esiti_confrontati: tuple[int, ...] = (),
) -> Importo:
    derivazione = Derivazione(
        istituto=istituto,
        maturazione=MATURAZIONE_ACCANTONAMENTO,
        regola_versione=1,
        riferimento=regola.riferimento,
        formula=formula,
        versione_corpus=corpus.versione,
        noto_al=istante,
        parametri=(),
        fatti=(),
        importi=(),
    )
    return Importo(rapporto, istituto, Periodo(valuta, valuta), valore, derivazione, esiti_confrontati=esiti_confrontati)


def voci_del_blocco(
    registro: Registro, corpus: Corpus, rapporto: str, persona: str, righe, categorie, valuta: date, istante: datetime
) -> tuple[VoceDelBlocco, ...]:
    """Le righe da aggiungere alla composizione del rapporto: la somma sospesa e i rilasci pagabili. Puo' fermare il rapporto.

    I rilasci sono le somme sospese di pagamenti precedenti che, alla valuta, tornano pagabili al dipendente: entrano
    nel primo pagamento utile come riga verso il beneficiario, senza nuova tassazione (ADR 0034).
    """
    voci: list[VoceDelBlocco] = []
    esito = verifica_del_pagamento(registro, corpus, rapporto, persona, righe, categorie, valuta, istante)
    if esito is not None and esito.inadempiente:
        regola = corpus.regola_somma_sospesa(valuta)
        if regola is None:
            raise ParametroMancante(f"Rapporto {rapporto}: nessuna regola di somma sospesa per un pagamento del {valuta}")
        terzi = trattenute_per_il_tetto(righe)
        valore = importo_sospeso(regola, esito.netto, terzi, esito.debito)
        if valore > 0:
            formula = (
                f"min(debito {esito.debito}; fascia sul netto {regola.quota_sul_netto(esito.netto)}; "
                f"tetto {regola.tetto} del netto {esito.netto} meno trattenute a terzi {terzi})"
            )
            importo = _importo_derivato(corpus, regola, rapporto, ISTITUTO_SOMMA_SOSPESA, valuta, valore, formula, istante)
            voci.append(VoceDelBlocco(importo, NATURA_SOMMA_SOSPESA, "meno", DESTINATARIO_ENTE, CANALE_ACCANTONAMENTO, regola.riferimento))
    for pagato in registro.esiti(TipoEsito.PAGATO, istante):
        for riga in pagato.righe:
            if riga.rapporto != rapporto or riga.istituto != ISTITUTO_SOMMA_SOSPESA:
                continue
            accantonamento = _accantonamento(registro, corpus, pagato.id, riga, valuta, istante)
            if accantonamento.stato is not StatoAccantonamento.PAGABILE:
                continue
            regola = corpus.regola_somma_sospesa(riga.periodo.dal)
            formula = f"somma sospesa dell'esito pagato {pagato.id}, tornata pagabile al dipendente: {accantonamento.motivo}"
            importo = _importo_derivato(
                corpus, regola, rapporto, ISTITUTO_RILASCIO, valuta, accantonamento.pagabile, formula, istante, (pagato.id,)
            )
            voci.append(VoceDelBlocco(importo, NATURA_SOMMA_SOSPESA, "piu", "beneficiario", "accredito", regola.riferimento))
    return tuple(voci)


# Chiusura dell'accantonamento

class StatoAccantonamento(StrEnum):
    SOSPESA = "sospesa"  # accantonata dall'ente, entro i giorni della sospensione e senza fatti di chiusura
    DA_VERSARE = "da_versare"  # ordine di versamento di AdER: trattenuta a terzi verso AdER, col bonifico
    VERSATA = "versata"  # versata ad AdER: esito versato
    PAGABILE = "pagabile"  # tornata pagabile al dipendente, non ancora in un pagamento
    RILASCIATA = "rilasciata"  # gia' pagata al dipendente in un esito pagato


@dataclass(frozen=True)
class Accantonamento:
    """Lo stato di una somma sospesa 48-bis: l'esito pagato che la porta, l'importo e cosa e' pagabile al dipendente."""

    esito: int
    rapporto: str
    importo: Decimal
    stato: StatoAccantonamento
    pagabile: Decimal
    motivo: str = ""


def _riga_sospesa(registro: Registro, esito_id: int, rapporto: str) -> Importo:
    esito = registro.esito(esito_id)
    riga = next(
        (r for r in esito.righe if r.rapporto == rapporto and r.istituto == ISTITUTO_SOMMA_SOSPESA), None
    ) if esito.tipo is TipoEsito.PAGATO else None
    if riga is None:
        raise ErroreRegistro(f"L'esito {esito_id} non ha una somma sospesa 48-bis pagata per il rapporto {rapporto}")
    return riga


def _evento_di_chiusura(registro: Registro, tipo: str, esito_id: int, rapporto: str, istante: datetime) -> Evento | None:
    eventi = [
        e for e in registro.eventi(tipo, istante)
        if e.contenuto["esito"] == esito_id and e.contenuto["rapporto"] == rapporto
    ]
    return eventi[-1] if eventi else None


def ha_ordine_di_versamento(registro: Registro, esito_id: int, rapporto: str, istante: datetime) -> bool:
    return _evento_di_chiusura(registro, TIPO_ORDINE_VERSAMENTO, esito_id, rapporto, istante) is not None


def _comunicazione_dell_esito(registro: Registro, persona: str | None, pagamento: date, istante: datetime) -> date:
    """La data in cui AdER ha comunicato l'esito inadempiente per il pagamento che porta la somma sospesa."""
    for richiesta in registro.eventi(TIPO_RICHIESTA_VERIFICA, istante):
        if richiesta.contenuto["persona"] != persona or richiesta.contenuto["pagamento"] != pagamento.isoformat():
            continue
        esiti = [
            e for e in registro.eventi(TIPO_ESITO_VERIFICA, istante)
            if e.contenuto["richiesta"] == richiesta.chiave and e.contenuto["esito"] == "inadempiente"
        ]
        if esiti:
            return date.fromisoformat(esiti[-1].contenuto["data"])
    raise ErroreRegistro(f"Persona {persona}: nessun esito inadempiente noto per il pagamento del {pagamento}")


def _accantonamento(
    registro: Registro, corpus: Corpus, esito_id: int, riga: Importo, giorno: date, istante: datetime
) -> Accantonamento:
    """Lo stato alla data `giorno`, per i fatti noti all'istante. Precedenza: rilasciata, versata, debito estinto,
    ordine di versamento, 60 giorni dalla comunicazione dell'esito, sospesa."""
    rapporto = riga.rapporto

    def stato(valore: StatoAccantonamento, pagabile: Decimal = Decimal(0), motivo: str = "") -> Accantonamento:
        return Accantonamento(esito_id, rapporto, riga.valore, valore, pagabile, motivo)

    for pagato in registro.esiti(TipoEsito.PAGATO, istante):
        if any(r.rapporto == rapporto and r.istituto == ISTITUTO_RILASCIO and r.esiti_confrontati == (esito_id,) for r in pagato.righe):
            return stato(StatoAccantonamento.RILASCIATA)
    chiave = {"istituto": ISTITUTO_SOMMA_SOSPESA, "rapporto": rapporto, "periodo": str(riga.periodo)}
    for versamento in registro.eventi(TIPO_VERSAMENTO_ESEGUITO, istante):
        if any(chiave.items() <= r.items() for r in versamento.contenuto["righe"]):
            return stato(StatoAccantonamento.VERSATA)
    estinto = _evento_di_chiusura(registro, TIPO_DEBITO_ESTINTO, esito_id, rapporto, istante)
    if estinto is not None:
        return stato(StatoAccantonamento.PAGABILE, Decimal(estinto.contenuto["importo"]), "debito pagato o ridotto comunicato da AdER")
    if ha_ordine_di_versamento(registro, esito_id, rapporto, istante):
        return stato(StatoAccantonamento.DA_VERSARE)
    regola = corpus.regola_somma_sospesa(riga.periodo.dal)
    if regola is None:
        raise ParametroMancante(f"Somma sospesa 48-bis del {riga.periodo.dal}: nessuna regola vigente")
    persona = registro.persona_del_rapporto(rapporto, istante)
    scadenza = _comunicazione_dell_esito(registro, persona, riga.periodo.dal, istante) + timedelta(days=regola.giorni_sospensione)
    if giorno > scadenza:
        return stato(
            StatoAccantonamento.PAGABILE, riga.valore, f"{regola.giorni_sospensione} giorni dalla comunicazione dell'esito senza ordine"
        )
    return stato(StatoAccantonamento.SOSPESA)


def stato_accantonamento(
    registro: Registro, corpus: Corpus, esito_id: int, rapporto: str, giorno: date, noto_al: datetime | None = None
) -> Accantonamento:
    """Lo stato della somma sospesa del rapporto nell'esito pagato, al `giorno` e per i fatti noti al `noto_al`."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    return _accantonamento(registro, corpus, esito_id, _riga_sospesa(registro, esito_id, rapporto), giorno, istante)


def registra_ordine_versamento(
    registro: Registro, chiave: str, adattatore: str, esito_id: int, rapporto: str, data: date
) -> Evento:
    """Ordine di versamento di AdER (art. 72-bis): la somma sospesa diventa trattenuta a terzi verso AdER, col bonifico."""
    _riga_sospesa(registro, esito_id, rapporto)
    contenuto = {"esito": esito_id, "rapporto": rapporto, "data": data.isoformat()}
    return registro.evento_identico(chiave, TIPO_ORDINE_VERSAMENTO, contenuto) or registro.registra_evento(
        chiave, TIPO_ORDINE_VERSAMENTO, contenuto, adattatore, esito_id=esito_id
    )


def registra_debito_estinto(
    registro: Registro, chiave: str, adattatore: str, esito_id: int, rapporto: str, data: date, importo: Decimal
) -> Evento:
    """Debito pagato o ridotto comunicato da AdER (DM 40/2008 art. 3 c. 5): `importo` e' quanto si paga al dipendente."""
    riga = _riga_sospesa(registro, esito_id, rapporto)
    if not isinstance(importo, Decimal) or not importo.is_finite() or not 0 < importo <= riga.valore:
        raise ErroreRegistro(
            f"L'importo indicato da AdER e' positivo e non supera la somma sospesa di {riga.valore}, {importo!r}"
        )
    contenuto = {"esito": esito_id, "rapporto": rapporto, "data": data.isoformat(), "importo": str(importo)}
    return registro.evento_identico(chiave, TIPO_DEBITO_ESTINTO, contenuto) or registro.registra_evento(
        chiave, TIPO_DEBITO_ESTINTO, contenuto, adattatore, esito_id=esito_id
    )
