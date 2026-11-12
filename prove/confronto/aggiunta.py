"""L'aggiunta di confronto al corpus reale: cio' che il corpus non ha ancora e che, per confrontare, si prende dal gestionale.

Nessuna voce di questa aggiunta e' una regola verificata sulla norma: tutti i riferimenti sono `fittizio:da-gestionale-...`.
Sono di due tipi, e il resoconto li elenca:

- **istituti letti**: voci fisse che il corpus non calcola (vacanza contrattuale, differenziali, indennita'...). L'importo
  mensile si legge dal cedolino e il nucleo lo tratta come misura mensile da atto: lo rapporta ai giorni, lo mette nelle
  basi e nel reddito. I concorsi alle basi sono quelli osservati sul gestionale, non letti sulla norma.
- **tabellare sostituito**: il corpus ha solo il tabellare del CCNL del 28/10/2026, con decorrenza 01/01/2026. Un pagamento
  di ottobre fatto prima della firma usa il tabellare precedente piu' la vacanza contrattuale. Per confrontare il resto
  (contributi, fisco, netto) sullo stesso lordo, il tabellare del 2026 si sostituisce con quello letto dai cedolini.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class IstitutoLetto:
    voce: str  # nome della voce fissa nel cedolino
    istituto: str
    tfs: bool = True  # concorre alla base TFS (osservato: tutto tranne indennita' di comparto e posizione)
    tfr_ulteriori: bool = False  # «ulteriori elementi TFR»: la retribuzione di posizione


ISTITUTI_LETTI = (
    IstitutoLetto("IND.VACANZA CONT.", "ente_vacanza_contrattuale"),
    IstitutoLetto("ASS.AD PERSONAM", "ente_assegno_ad_personam"),
    IstitutoLetto("IND.DI VIGILANZA", "ente_indennita_vigilanza"),
    IstitutoLetto("DIFF.STIPENDIALE", "ente_differenziale_stipendiale"),
    IstitutoLetto("DIFF.STORICO", "ente_differenziale_storico"),
    IstitutoLetto("VARIE PENSION.", "ente_varie_pensionabili"),
    IstitutoLetto("IND.SPECIFICA", "ente_indennita_specifica"),
    IstitutoLetto("RETR.POSIZ.N.DIR.", "ente_posizione_eq", tfs=False, tfr_ulteriori=True),
)
PER_VOCE = {i.voce: i for i in ISTITUTI_LETTI}

# Voci fisse che il corpus calcola da se', per area: (sigla del gestionale) -> area del corpus.
AREE = {"FUN": "funzionari", "IST": "istruttori", "OE": "operatori_esperti", "OP": "operatori"}
VOCE_TABELLARE = "STIPENDIO BASE"
VOCE_COMPARTO = "IND.COMPARTO Q.F."


def _dichiarazioni(i: IstitutoLetto) -> str:
    rif = f"fittizio:da-gestionale-{i.istituto.replace('_', '-')}"
    blocchi = [
        f'''[[regola]]
istituto = "{i.istituto}"
versione = 1
dal = 2026-01-01
riferimento = "{rif}"
formula = "fatto.{i.istituto}"
maturazione = "giorni"
applica_se = "{i.istituto}"
conteggio = "lun_sab"
divisore = "divisore_giornaliero"
decimali = 2
''',
        f'''[[reddito]]
istituto = "{i.istituto}"
categoria = "lavoro_dipendente"
dal = 2026-01-01
riferimento = "{rif}-reddito"
''',
        f'''[[composizione]]
istituto = "{i.istituto}"
dal = 2026-01-01
riferimento = "{rif}-composizione"
natura = "retribuzione"
effetto = "piu"
destinatario = "beneficiario"
canale = "accredito"
''',
        f'''[[classificazione]]
istituto = "{i.istituto}"
dal = 2026-01-01
riferimento = "{rif}-classificazione"
piano_dei_conti = "U.1.01.01.01.002"
origine_impegno = "automatico"
''',
        f'''[[part_time]]
istituto = "{i.istituto}"
trattamento = "proporzionale"
dal = 2026-01-01
riferimento = "{rif}-part-time"
''',
    ]
    concorsi = (
        (("cpdel", "fondo_credito"), True),
        (("tfs",), i.tfs),
        (("tfr_ulteriori",), i.tfr_ulteriori),
        (("gestione_separata",), False),
        (("irap",), True),
    )
    for basi, intero in concorsi:
        elenco = ", ".join(f'"{b}"' for b in basi)
        blocchi.append(
            f'''[[concorso]]
istituto = "{i.istituto}"
basi = [{elenco}]
misura = "{"intero" if intero else "escluso"}"
dal = 2026-01-01
riferimento = "{rif}-concorso-{basi[0].replace('_', '-')}"
'''
        )
    return "\n".join(blocchi)


# Il pagato dei mesi prima, letto dall'estrazione voci (imponibile IRPEF): reddito per la proiezione, fuori da ogni base.
PREGRESSO = "ente_pagato_pregresso"
_PREGRESSO = f'''[[regola]]
istituto = "{PREGRESSO}"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:da-gestionale-pagato-pregresso"
formula = "fatto.{PREGRESSO}"
maturazione = "evento"
applica_se = "{PREGRESSO}"

[[reddito]]
istituto = "{PREGRESSO}"
categoria = "lavoro_dipendente"
dal = 2026-01-01
riferimento = "fittizio:da-gestionale-pagato-pregresso-reddito"

[[concorso]]
istituto = "{PREGRESSO}"
basi = ["cpdel", "fondo_credito", "tfs", "tfr_ulteriori", "gestione_separata", "irap"]
misura = "escluso"
dal = 2026-01-01
riferimento = "fittizio:da-gestionale-pagato-pregresso-concorso"
'''


def testo_aggiunta() -> str:
    return "\n".join([*(_dichiarazioni(i) for i in ISTITUTI_LETTI), _PREGRESSO])


def sostituisci_tabellari(corpus_reale: str, annui: dict[str, Decimal]) -> tuple[str, dict[str, tuple[Decimal, Decimal]]]:
    """Sostituisce la vigenza 2026 del tabellare annuo di ogni area. Restituisce il testo e, per area, (valore del corpus, valore usato)."""
    cambi = {}
    for area, annuo in annui.items():
        modello = re.compile(
            rf'(nome = "tabellare_annuo_{area}"\s*\[\[parametro\.vigenza\]\]\s*dal = 2026-01-01\s*valore = ")([\d.]+)(")'
        )
        trovato = modello.search(corpus_reale)
        if trovato is None:
            raise ValueError(f"tabellare_annuo_{area}: vigenza 2026 non trovata nel corpus")
        cambi[area] = (Decimal(trovato.group(2)), annuo)
        corpus_reale = modello.sub(rf"\g<1>{annuo}\g<3>", corpus_reale, count=1)
    return corpus_reale, cambi


def estendi_riduzione_tfr(corpus_reale: str) -> str:
    """La riduzione TFR del corpus elenca le voci utili al TFS: vi aggiunge gli istituti letti che concorrono alla base tfs."""
    aggiunti = " + ".join(f"importo.{i.istituto}" for i in ISTITUTI_LETTI if i.tfs)
    righe = corpus_reale.splitlines()
    for n, riga in enumerate(righe):
        if riga.startswith('formula = "-arrotonda(arrotonda((') and n >= 5 and any('istituto = "riduzione_tfr"' in r for r in righe[n - 5 : n]):
            if "importo.tabellare_funzionari" not in riga:
                break
            righe[n] = riga.replace("importo.tabellare_funzionari", f"importo.tabellare_funzionari + {aggiunti}", 1)
            return chr(10).join(righe)
    raise ValueError("riduzione_tfr: formula non trovata nel corpus")
