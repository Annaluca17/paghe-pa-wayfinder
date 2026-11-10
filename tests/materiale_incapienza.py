"""Materiale dei test dell'incapienza del conguaglio (ticket #99, ADR 0034). Dati esclusivamente fittizi.

Sul corpus di materiale_proposta (contributo del lavoratore 8%, aliquota 20%) con la franchigia che cambia a dicembre:
fino al 30 novembre 120000 (ragguagliata al mese 10000: nessuna ritenuta), dal 1° dicembre 1200 (al mese 100).
Ottobre e novembre di 1500, dicembre di 300 con l'ultimo pagamento dell'anno il 18:
  ritenute: 0, 0 e (300 - 100) * 0,20 = 40,00; imposta dell'anno (3300 - 1200) * 0,20 = 420,00
  conguaglio = 420,00 - 40,00 = 380,00 a debito
  netto di dicembre senza il conguaglio = 300 - 24 (contributo 8%) - 40 = 236,00
  si trattengono 236,00 e l'incapienza è 380,00 - 236,00 = 144,00.
"""

from datetime import date
from decimal import Decimal

from paghe import Corpus, Mese
from paghe.proposta import emetti_versione

from materiale_impegni import impegni_capienti
from materiale_proposta import CF, CORPUS_PROPOSTA, IBAN, P, R, assumi, paga, stipendio

D = Decimal
CODICE_DI_PROVA = "199E"  # codice tributo di fantasia dell'interesse: esiste solo nel materiale di test
RIFERIMENTO_INTERESSE = "fittizio:interesse-differimento"

_FRANCHIGIA = """nome = "franchigia"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "12000"
riferimento = "fittizio:franchigia"
"""

_FRANCHIGIA_CHE_SCENDE = """nome = "franchigia"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "120000"
riferimento = "fittizio:franchigia"
[[parametro.vigenza]]
dal = 2026-12-01
valore = "1200"
riferimento = "fittizio:franchigia-dicembre"
"""

PARAMETRO_INTERESSE = f"""
[[parametro]]
nome = "interesse_differimento_mensile"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "0.005"
riferimento = "{RIFERIMENTO_INTERESSE}"
"""

COMPOSIZIONE_RESTO_E_INTERESSE = """
[[composizione]]
istituto = "conguaglio_irpef_resto"
dal = 2020-01-01
riferimento = "fittizio:comp-conguaglio-resto"
natura = "ritenuta"
effetto = "meno"
destinatario = "terzo"
canale = "f24ep"

[[composizione]]
istituto = "conguaglio_irpef_interesse"
dal = 2020-01-01
riferimento = "fittizio:comp-conguaglio-interesse"
natura = "ritenuta"
effetto = "meno"
destinatario = "terzo"
canale = "f24ep"
"""

MAPPATURA_RESTO = """
[[mappatura]]
istituto = "conguaglio_irpef_resto"
sistema = "codice_tributo_f24ep"
codice = "100E"
dal = 2020-01-01
riferimento = "fittizio:mappatura-conguaglio-resto"
"""

MAPPATURA_INTERESSE = f"""
[[mappatura]]
istituto = "conguaglio_irpef_interesse"
sistema = "codice_tributo_f24ep"
codice = "{CODICE_DI_PROVA}"
dal = 2020-01-01
riferimento = "fittizio:mappatura-conguaglio-interesse"
"""


def toml_incapienza(con_interesse=True, con_mappatura=True, base=CORPUS_PROPOSTA, extra="", contributo=None) -> str:
    """Il testo del corpus con la franchigia che scende a dicembre.

    Senza `con_interesse` manca il parametro; senza `con_mappatura` manca il codice tributo dell'interesse.
    """
    assert _FRANCHIGIA in base
    testo = base.replace(_FRANCHIGIA, _FRANCHIGIA_CHE_SCENDE)
    if contributo is not None:
        marca = 'nome = "aliquota_lavoratore"\n[[parametro.vigenza]]\ndal = 2020-01-01\nvalore = "0.08"'
        assert marca in testo
        testo = testo.replace(marca, marca.replace("0.08", contributo))
    testo += COMPOSIZIONE_RESTO_E_INTERESSE + MAPPATURA_RESTO
    if con_interesse:
        testo += PARAMETRO_INTERESSE
    if con_mappatura:
        testo += MAPPATURA_INTERESSE
    return testo + extra


def corpus_incapienza(**kwargs) -> Corpus:
    return Corpus.da_toml(toml_incapienza(**kwargs))


def assumi_fino_al(registro, al):
    """Il rapporto con il servizio fino al `al` compreso: dopo, la persona è cessata."""
    registro.registra_codice_persona(P, "codice_fiscale", CF, date(1980, 1, 1))
    registro.registra_iban_persona(P, IBAN, date(2026, 1, 1))
    registro.collega_rapporto(R, P, date(2026, 1, 1))
    registro.registra_codice(R, "tipo_impiego", "1", date(2026, 1, 1), al)
    registro.registra_programma_rapporto(R, "01.02", date(2026, 1, 1))
    for esercizio in (2026, 2027):
        impegni_capienti(registro, esercizio, 1, data=date(esercizio, 1, 1))


def fino_a_dicembre(registro, orologio, corpus, dicembre="300", ultimo=True, servizio_fino_al=None):
    """Ottobre e novembre pagati; gli importi di dicembre, con l'ultimo pagamento dell'anno il 18."""
    if servizio_fino_al is None:
        assumi(registro)
    else:
        assumi_fino_al(registro, servizio_fino_al)
    paga(registro, corpus, orologio, stipendio(registro, corpus, Mese(2026, 10), "1500"), date(2026, 10, 27), "pag-ott")
    paga(registro, corpus, orologio, stipendio(registro, corpus, Mese(2026, 11), "1500"), date(2026, 11, 27), "pag-nov")
    if ultimo:
        registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    importi = stipendio(registro, corpus, Mese(2026, 12), dicembre)
    orologio.vai(12, 10)
    return importi


def versione_di_dicembre(registro, orologio, corpus, **kwargs):
    importi = fino_a_dicembre(registro, orologio, corpus, **kwargs)
    return emetti_versione(registro, corpus, date(2026, 12, 18), importi)


def paga_dicembre(registro, orologio, corpus, **kwargs):
    """Il pagamento di dicembre (con il conguaglio incapiente) eseguito il 18."""
    importi = fino_a_dicembre(registro, orologio, corpus, **kwargs)
    return paga(registro, corpus, orologio, importi, date(2026, 12, 18), "pag-dic")


def paga_mese(registro, orologio, corpus, anno, mese, giorno=27, importo="1500", ultimo=None):
    """Lo stipendio del mese pagato il `giorno`: versione, conferma ed esito pagato."""
    if ultimo is not None:
        registro.registra_ultimo_pagamento(anno, ultimo)
    importi = stipendio(registro, corpus, Mese(anno, mese), importo)
    return paga(registro, corpus, orologio, importi, date(anno, mese, giorno), f"pag-{anno}-{mese}")


def netto_di(versione, rapporto=R):
    return {n.rapporto: n.netto for n in versione.netti}[rapporto]


def righe_del(versione, istituto):
    return [riga.importo for riga in versione.righe if riga.istituto == istituto]
