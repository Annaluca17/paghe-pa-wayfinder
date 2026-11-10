"""Materiale dei test della sostitutiva sull'accessorio (ticket #96, ADR 0035). Valori e fonti fittizi.

Sul corpus fiscale di test_fiscale (10% fino a 10000, 20% fino a 30000, 30% oltre; nessuna detrazione senza dichiarazione).
Istituto accessorio: `premio`. Sostitutiva: 15%, tetto 800, limite 50000. Stipendio di 1000 al mese, un pagamento il 27.

Gennaio con 500 di premio: reddito annuo stimato (1500 * 365 / 31) = 17661,29, sotto il limite; quota a sostitutiva 500,
imposta 75,00; imponibile ordinario 1000, ritenuta 116,67 (come lo stipendio da solo).
"""

from datetime import date
from decimal import Decimal

from paghe import Corpus, Mese, TipoEsito, attribuisci_reddito, calcola, calcola_fiscale, emetti_esito

from test_fiscale import R, TESTO, assumi  # noqa: F401

D = Decimal

PARAMETRI_SOSTITUTIVA = {"sost_aliquota": "0.15", "sost_tetto": "800", "sost_limite": "50000"}

PREMIO = """
[[regola]]
istituto = "premio"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:premio"
formula = "fatto.premio"
maturazione = "evento"
applica_se = "premio"

[[reddito]]
istituto = "premio"
categoria = "lavoro_dipendente"
dal = 2020-01-01
riferimento = "fittizio:reddito-premio"

[[concorso]]
istituto = "premio"
basi = ["pens"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso-premio"
"""


def parametri_sostitutiva(sovrascrivi=None) -> str:
    valori = {**PARAMETRI_SOSTITUTIVA, **(sovrascrivi or {})}
    return "".join(
        f'''
[[parametro]]
nome = "{nome}"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "{valore}"
riferimento = "fittizio:{nome.replace('_', '-')}"
'''
        for nome, valore in valori.items()
    )


def sostitutiva(extra="", versione=1, dal="2020-01-01", al="2026-12-31"):
    return f"""
[[sostitutiva]]
versione = {versione}
dal = {dal}
al = {al}
riferimento = "fittizio:sostitutiva"
aliquota = "sost_aliquota"
tetto = "sost_tetto"
limite = "sost_limite"
istituto = "sostitutiva_accessorio"
istituto_base = "sostitutiva_accessorio_base"
{extra}"""


ACCESSORIO = """
[[accessorio]]
istituto = "premio"
dal = 2020-01-01
riferimento = "fittizio:accessorio-premio"
"""

# Composizione e codice 179E (ris. AdE 4/E/2026, forma assunta nel catalogo di prova): l'imposta e' una trattenuta a debito.
COMPOSIZIONE_SOSTITUTIVA = """
[[composizione]]
istituto = "sostitutiva_accessorio_base"
dal = 2020-01-01
riferimento = "fittizio:comp-sostitutiva-base"
natura = "imponibile_sostitutivo"
effetto = "nessuno"

[[composizione]]
istituto = "sostitutiva_accessorio"
dal = 2020-01-01
riferimento = "fittizio:comp-sostitutiva"
natura = "trattenuta_terzi"
effetto = "meno"
destinatario = "terzo"
canale = "f24ep"

[[mappatura]]
istituto = "sostitutiva_accessorio"
sistema = "codice_tributo_f24ep"
codice = "179E"
dal = 2020-01-01
riferimento = "fittizio:mappatura-sostitutiva"
"""

CODICE_179E = """
[[codice_f24ep]]
codice = "179E"
sezione = "F"
codice_campo = "nessuno"
estremi = "nessuno"
rif_a = "mese_pagamento"
rif_b = "anno_pagamento"
modalita = "debito"
dal = 2020-01-01
riferimento = "fittizio:codice-179e"
"""

TESTO_SOSTITUTIVA = TESTO + PREMIO + parametri_sostitutiva() + ACCESSORIO + sostitutiva()


def corpus_sostitutiva(parametri=None, accessorio=ACCESSORIO, **modifiche) -> Corpus:
    return Corpus.da_toml(TESTO + PREMIO + parametri_sostitutiva(parametri) + accessorio + sostitutiva(**modifiche))


def paga_con_sostitutiva(registro, orologio, corpus, righe, giorno, rapporto=R, ultimo=False):
    """Come `paga` di test_fiscale, ma l'esito pagato porta anche la quota a sostitutiva e la sua imposta."""
    orologio.vai(giorno.month, giorno.day, giorno.year)
    attribuite = attribuisci_reddito(corpus, righe, giorno)
    fiscale = calcola_fiscale(registro, corpus, rapporto, attribuite, giorno, ultimo_dell_anno=ultimo)
    contenuto = [*attribuite, fiscale.ritenuta, *([fiscale.conguaglio] if fiscale.conguaglio else []), *fiscale.sostitutiva]
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, contenuto)
    registro.registra_pagamento(rapporto, esito.id, giorno)
    orologio.avanza()
    return esito, fiscale


def mese_con_premio(registro, orologio, corpus, numero, stipendio="1000", premio="0", anno=2026, ultimo=False, rapporto=R):
    """Stipendio e premio del mese, pagati il 27."""
    orologio.vai(numero, 1, anno)
    mese = Mese(anno, numero)
    registro.registra_fatto(rapporto, "mensile", stipendio, mese.primo_giorno, mese.ultimo_giorno)
    if D(premio):
        registro.registra_fatto(rapporto, "premio", premio, mese.primo_giorno, mese.ultimo_giorno)
    righe = calcola(registro, corpus, rapporto, mese)
    return paga_con_sostitutiva(registro, orologio, corpus, righe, date(anno, numero, 27), rapporto, ultimo)


def della_sostitutiva(fiscale, istituto):
    trovati = [i for i in fiscale.sostitutiva if i.istituto == istituto]
    assert len(trovati) == 1, [i.istituto for i in fiscale.sostitutiva]
    return trovati[0]


BASE = "sostitutiva_accessorio_base"
IMPOSTA = "sostitutiva_accessorio"
