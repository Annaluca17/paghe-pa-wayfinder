"""Materiale comune ai test della versione di proposta e degli eventi di ritorno. Dati esclusivamente fittizi.

Numeri scelti per tornare a mano. Stipendio mensile di 1500:
  contributo del lavoratore 8%  = 120,00     contributo a carico dell'ente 24% = 360,00
  ritenuta: franchigia annua 12000, ragguagliata al mese 1000; 20% sul resto = (1500 - 1000) * 0,20 = 100,00
  netto = 1500 - 120 - 100 = 1280,00 (il contributo a carico dell'ente non ha effetto sul netto).
"""

from datetime import date

import pytest

from paghe import Corpus, Mese, calcola
from paghe.proposta import conferma_versione, emetti_versione, registra_pagamento_eseguito

CF = "RSSMRA80A01H501U"
IBAN = "IT00X0000000000000000000000"  # IBAN di prova, non valido
P = "PERSONA-1"
P2 = "PERSONA-2"
R = "RAPPORTO-1"
R2 = "RAPPORTO-2"
R3 = "RAPPORTO-3"

PARAMETRI = {
    "aliquota_lavoratore": "0.08",
    "aliquota_ente": "0.24",
    "aliquota_irpef": "0.20",
    "franchigia": "12000",
}

CORPUS_PROPOSTA = (
    "".join(
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
    + """
[periodo_dichiarato]
servizio = "tipo_impiego"

[[base]]
nome = "pens"
riferimento = "fittizio:base-pens"

[[regola]]
istituto = "stipendio"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio"
formula = "fatto.mensile"
maturazione = "evento"
applica_se = "mensile"

[[regola]]
istituto = "gettone"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:gettone"
formula = "fatto.gettone"
maturazione = "evento"
applica_se = "gettone"

[[regola]]
istituto = "contributo_lavoratore"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:contributo-lavoratore"
formula = "arrotonda(base.pens * parametro.aliquota_lavoratore, 2)"
maturazione = "periodo"

[[regola]]
istituto = "contributo_ente"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:contributo-ente"
formula = "arrotonda(base.pens * parametro.aliquota_ente, 2)"
maturazione = "periodo"

[[concorso]]
istituto = "stipendio"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-stipendio"

[[concorso]]
istituto = "gettone"
basi = ["pens"]
misura = "escluso"
dal = 2020-01-01
riferimento = "fittizio:concorso-gettone"

[[categoria_reddito]]
nome = "lavoro_dipendente"
[[categoria_reddito.cassa_allargata]]
dal = 2020-01-01
vale = true
riferimento = "fittizio:cassa-lavoro"

[[categoria_reddito]]
nome = "carica_elettiva"
[[categoria_reddito.cassa_allargata]]
dal = 2020-01-01
vale = false
riferimento = "fittizio:cassa-carica"

[[reddito]]
istituto = "stipendio"
categoria = "lavoro_dipendente"
dal = 2020-01-01
riferimento = "fittizio:reddito-stipendio"

[[reddito]]
istituto = "gettone"
categoria = "carica_elettiva"
dal = 2020-01-01
riferimento = "fittizio:reddito-gettone"

[[ritenuta]]
istituto = "ritenuta_irpef"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:ritenuta"
categorie = ["lavoro_dipendente"]
detrazione_richiesta = "lavoro_dipendente"
imposta = "arrotonda(max(0, fisco.imponibile - parametro.franchigia / fisco.periodi) * parametro.aliquota_irpef, 2)"
detrazione = "0"

[[conguaglio]]
istituto = "conguaglio_irpef"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:conguaglio"

[[composizione]]
istituto = "stipendio"
dal = 2020-01-01
riferimento = "fittizio:comp-stipendio"
natura = "retribuzione"
effetto = "piu"
destinatario = "beneficiario"
canale = "accredito"

[[composizione]]
istituto = "gettone"
dal = 2020-01-01
riferimento = "fittizio:comp-gettone"
natura = "retribuzione"
effetto = "piu"
destinatario = "beneficiario"
canale = "accredito"

[[composizione]]
istituto = "contributo_lavoratore"
dal = 2020-01-01
riferimento = "fittizio:comp-contributo-lavoratore"
natura = "contributo_lavoratore"
effetto = "meno"
destinatario = "terzo"
canale = "f24ep"

[[composizione]]
istituto = "contributo_ente"
dal = 2020-01-01
riferimento = "fittizio:comp-contributo-ente"
natura = "contributo_ente"
effetto = "nessuno"
destinatario = "terzo"
canale = "f24ep"

[[composizione]]
istituto = "ritenuta_irpef"
dal = 2020-01-01
riferimento = "fittizio:comp-ritenuta"
natura = "ritenuta"
effetto = "meno"
destinatario = "terzo"
canale = "f24ep"

[[composizione]]
istituto = "conguaglio_irpef"
dal = 2020-01-01
riferimento = "fittizio:comp-conguaglio"
natura = "ritenuta"
effetto = "meno"
destinatario = "terzo"
canale = "f24ep"
"""
)


def corpus_proposta(**modifiche: str) -> Corpus:
    """Il corpus di prova, con eventuali parametri cambiati: `corpus_proposta(aliquota_lavoratore="0.95")`."""
    testo = CORPUS_PROPOSTA
    for nome, valore in modifiche.items():
        testo = _cambia(testo, nome, valore)
    return Corpus.da_toml(testo)


def _cambia(testo: str, nome: str, valore: str) -> str:
    inizio = testo.index(f'nome = "{nome}"')
    vecchio = f'valore = "{PARAMETRI[nome]}"'
    posizione = testo.index(vecchio, inizio)
    return testo[:posizione] + f'valore = "{valore}"' + testo[posizione + len(vecchio):]


@pytest.fixture
def corpus_p():
    return corpus_proposta()


def assumi(registro, rapporto=R, persona=P, iban=True, dal=date(2026, 1, 1)):
    if not registro.fatti_persona_noti(persona, "codice_fiscale", registro.adesso()):
        registro.registra_codice_persona(persona, "codice_fiscale", CF, date(1980, 1, 1))
        if iban:
            registro.registra_iban_persona(persona, IBAN, date(2026, 1, 1))
    registro.collega_rapporto(rapporto, persona, dal)
    registro.registra_codice(rapporto, "tipo_impiego", "1", dal)


def stipendio(registro, corpus, mese, importo="1500", rapporto=R):
    """Gli importi calcolati del mese: uno stipendio, da pagare."""
    registro.registra_fatto(rapporto, "mensile", importo, mese.primo_giorno, mese.ultimo_giorno)
    return [riga for riga in calcola(registro, corpus, rapporto, mese) if riga.istituto == "stipendio"]


def gettone(registro, corpus, mese, importo="100", rapporto=R3):
    registro.registra_fatto(rapporto, "gettone", importo, mese.primo_giorno, mese.ultimo_giorno)
    return [riga for riga in calcola(registro, corpus, rapporto, mese) if riga.istituto == "gettone"]


def per_istituto(righe):
    return {riga.istituto: riga for riga in righe}


def paga(registro, corpus, orologio, importi, valuta, chiave, rapporti=None):
    """Il ciclo fino al denaro: versione, conferma ed evento di pagamento eseguito alla valuta prevista."""
    orologio.vai(valuta.month, valuta.day, valuta.year)
    versione = emetti_versione(registro, corpus, valuta, importi)
    conferma_versione(registro, versione.id)
    registra_pagamento_eseguito(registro, corpus, chiave, "adattatore-prova", versione.id, valuta, rapporti or versione.rapporti)
    orologio.avanza()
    return versione
