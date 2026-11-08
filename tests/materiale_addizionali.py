"""Materiale comune ai test delle addizionali (ticket #85, ADR 0029). Dati, comuni e regioni esclusivamente fittizi.

Sopra il corpus di materiale_proposta (stipendio 1500 al mese, franchigia annua 12000, 20%): su dodici stipendi il reddito
e' 18000, l'IRPEF dell'anno 1200 e le dodici ritenute di 100 la pareggiano: conguaglio zero.

Comune X001 (0,5% fino a 15000, 0,8% oltre): su 18000, 75,00 + 24,00 = 99,00.
Regione 98 (1,2% fino a 15000, 2% oltre): su 18000, 180,00 + 60,00 = 240,00.
Comune X002: soglia 12000 e 0,6% unico: su 18000, 108,00. Regione 97: 1% unico: su 18000, 180,00.
"""

from datetime import date
from decimal import Decimal

from paghe import Atto, Corpus, Mese, TipoEsito, attribuisci_reddito, calcola, calcola_fiscale, emetti_esito

from materiale_proposta import CORPUS_PROPOSTA, P, R, _cambia, assumi, stipendio

D = Decimal
ATTO_DOMICILIO = Atto("ente:ente_di_prova:comunicazione.domicilio:2025-12-10;1", date(2025, 12, 10))

PARAMETRI = {
    "addizionale_acconto_percentuale": "0.30",
    "addizionale_mese_prima_rata_acconto": "3",
    "addizionale_mese_ultima_rata": "11",
}

ISTITUTI = {
    "regionale_dovuta": "addizionale_regionale_dovuta",
    "comunale_dovuta": "addizionale_comunale_dovuta",
    "regionale": "addizionale_regionale",
    "comunale_saldo": "addizionale_comunale_saldo",
    "comunale_acconto": "addizionale_comunale_acconto",
    "regionale_credito": "addizionale_regionale_credito",
    "comunale_credito": "addizionale_comunale_credito",
}


def _parametri() -> str:
    return "".join(
        f'''
[[parametro]]
nome = "{nome}"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "{valore}"
riferimento = "fittizio:{nome.replace('_', '-')}"
'''
        for nome, valore in PARAMETRI.items()
    )


def _aliquota(ente, codice, anno, fasce, soglia=None):
    riga_soglia = f'soglia = "{soglia}"\n' if soglia else ""
    righe = f'''
[[aliquota_addizionale]]
ente = "{ente}"
codice = "{codice}"
anno = {anno}
{riga_soglia}riferimento = "fittizio:aliquota-{ente}-{codice.lower()}-{anno}"
'''
    for fino_a, aliquota in fasce:
        righe += "[[aliquota_addizionale.fascia]]\n" + (f'fino_a = "{fino_a}"\n' if fino_a else "") + f'aliquota = "{aliquota}"\n'
    return righe


ALIQUOTE = (
    "".join(
        _aliquota("comune", "X001", anno, [("15000", "0.005"), (None, "0.008")])
        + _aliquota("regione", "98", anno, [("15000", "0.012"), (None, "0.02")])
        for anno in (2025, 2026, 2027)
    )
    + _aliquota("comune", "X002", 2026, [(None, "0.006")], soglia="12000")
    + _aliquota("regione", "97", 2026, [(None, "0.01")])
)

_RUOLI = "\n".join(f'{ruolo} = "{istituto}"' for ruolo, istituto in ISTITUTI.items())

REGOLA = f'''
[[addizionale]]
versione = 1
dal = 2020-01-01
riferimento = "fittizio:addizionali"
percentuale_acconto = "addizionale_acconto_percentuale"
mese_prima_rata_acconto = "addizionale_mese_prima_rata_acconto"
mese_ultima_rata = "addizionale_mese_ultima_rata"
{_RUOLI}
'''


def _composizione(istituto, natura, effetto, destinatario, canale):
    return f'''
[[composizione]]
istituto = "{istituto}"
dal = 2020-01-01
riferimento = "fittizio:comp-{istituto.replace('_', '-')}"
natura = "{natura}"
effetto = "{effetto}"
destinatario = "{destinatario}"
canale = "{canale}"
'''


COMPOSIZIONI = "".join(
    _composizione(ISTITUTI[ruolo], "addizionale", "meno", "terzo", "f24ep")
    for ruolo in ("regionale", "comunale_saldo", "comunale_acconto")
) + "".join(
    _composizione(ISTITUTI[ruolo], "credito_sostituto", "piu", "beneficiario", "accredito")
    for ruolo in ("regionale_credito", "comunale_credito")
)

def testo(franchigia: str | None = None, con_regola: bool = True) -> str:
    """Il corpus di prova; con `franchigia` cambia quella della ritenuta, con `con_regola` falso toglie la regola."""
    base = _cambia(CORPUS_PROPOSTA, "franchigia", franchigia) if franchigia else CORPUS_PROPOSTA
    return base + _parametri() + ALIQUOTE + ((REGOLA + COMPOSIZIONI) if con_regola else "")


TESTO = testo()


def corpus_addizionali(**opzioni) -> Corpus:
    return Corpus.da_toml(testo(**opzioni))


def domicilio(registro, comune="X001", regione="98", dal=date(2025, 6, 1), persona=P):
    return registro.registra_domicilio_fiscale(persona, comune, regione, dal, atto=ATTO_DOMICILIO)


def assumi_a(registro, comune="X001", regione="98", rapporto=R, persona=P):
    """Un dipendente in servizio dal 2026 con il suo domicilio fiscale (se `comune` non e' None)."""
    assumi(registro, rapporto, persona)
    if comune is not None:
        domicilio(registro, comune, regione, persona=persona)


def paga(registro, orologio, corpus, giorno, importo="1500", ultimo=False, rapporto=R, fino_al=None):
    """Un pagamento dello stipendio: attribuzione, fiscale (ritenuta, conguaglio, addizionali) ed esito pagato.

    Restituisce il `FiscaleDelPagamento`.
    """
    orologio.vai(giorno.month, giorno.day, giorno.year)
    mese = Mese(giorno.year, giorno.month)
    if fino_al is None:
        righe = stipendio(registro, corpus, mese, importo, rapporto)
    else:  # rapporto cessato in `fino_al`: lo stipendio dura fino alla cessazione
        registro.registra_fatto(rapporto, "mensile", importo, mese.primo_giorno, fino_al)
        righe = [r for r in calcola(registro, corpus, rapporto, mese) if r.istituto == "stipendio"]
    attribuite = attribuisci_reddito(corpus, righe, giorno)
    fiscale = calcola_fiscale(registro, corpus, rapporto, attribuite, giorno, ultimo_dell_anno=ultimo)
    contenuto = [
        *attribuite,
        fiscale.ritenuta,
        *([fiscale.conguaglio] if fiscale.conguaglio else []),
        *fiscale.addizionali,
    ]
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, contenuto)
    registro.registra_pagamento(rapporto, esito.id, giorno)
    orologio.avanza()
    return fiscale


def anno_di_paghe(registro, orologio, corpus, anno=2026, rapporto=R, importo="1500", fino_a=12):
    """Pagamenti il 27 di ogni mese fino a `fino_a`; quello di dicembre porta il conguaglio. Restituisce i fiscali."""
    return [
        paga(registro, orologio, corpus, date(anno, mese, 27), importo, ultimo=mese == 12, rapporto=rapporto)
        for mese in range(1, fino_a + 1)
    ]


def per_istituto(importi):
    return {importo.istituto: importo for importo in importi}


def assumi_fino_al(registro, al, comune="X001", regione="98", rapporto=R, persona=P):
    """Come `assumi_a`, ma il servizio finisce in `al`: l'ultimo pagamento e' finale (ADR 0019)."""
    registro.registra_codice_persona(persona, "codice_fiscale", "RSSMRA80A01H501U", date(1980, 1, 1))
    registro.collega_rapporto(rapporto, persona, date(2026, 1, 1))
    registro.registra_codice(rapporto, "tipo_impiego", "1", date(2026, 1, 1), al)
    domicilio(registro, comune, regione, persona=persona)
