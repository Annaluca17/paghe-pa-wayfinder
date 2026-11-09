"""Materiale dei test di somma esente e trattamento integrativo (ticket #95, ADR 0019). Valori e fonti fittizi.

Sul corpus fiscale di test_fiscale (10% fino a 10000, 20% fino a 30000; detrazione 1200 ridotta in proporzione fino a
40000). Somma esente: 7% fino a 8500, 5% fino a 15000, 4% fino a 20000, zero oltre. Trattamento integrativo: 1200 se il
reddito non supera 15000 e l'imposta lorda supera la detrazione meno 75; da 15000 a 28000 la differenza fra detrazioni
e imposta lorda, al massimo 1200. Recuperi: soglia 60, otto rate per l'integrativo, dieci per la somma esente.

Stipendio di 1000 al mese, un pagamento il 27 di ogni mese:
  imposta del mese 116,67; detrazione dell'art. 13 del mese 1200 * (40000 - 12000) / 40000 / 12 = 70,00
  integrativo del mese 1200 / 12 = 100,00 (116,67 supera 70,00 - 6,25); somma esente 5% di 1000 = 50,00.
"""

from paghe import Corpus

from test_fiscale import TESTO

PARAMETRI_BENEFICI = {
    "se_soglia_1": "8500",
    "se_soglia_2": "15000",
    "se_soglia_3": "20000",
    "se_percentuale_1": "0.07",
    "se_percentuale_2": "0.05",
    "se_percentuale_3": "0.04",
    "ti_importo": "1200",
    "ti_soglia_1": "15000",
    "ti_soglia_2": "28000",
    "ti_riduzione": "75",
    "recupero_soglia": "60",
    "recupero_rate_ti": "8",
    "recupero_rate_se": "10",
}

SOMMA_ESENTE = """arrotonda(
    se(fisco.reddito_stimato <= parametro.se_soglia_1, parametro.se_percentuale_1,
       se(fisco.reddito_stimato <= parametro.se_soglia_2, parametro.se_percentuale_2,
          se(fisco.reddito_stimato <= parametro.se_soglia_3, parametro.se_percentuale_3, 0))) * fisco.reddito_dipendente, 2)"""

INTEGRATIVO = """arrotonda(
    se(fisco.reddito_stimato <= parametro.ti_soglia_1,
       se(fisco.imposta > fisco.detrazione - parametro.ti_riduzione / fisco.periodi,
          parametro.ti_importo * fisco.giorni / fisco.giorni_anno / fisco.periodi, 0),
       se(fisco.reddito_stimato <= parametro.ti_soglia_2,
          min(parametro.ti_importo * fisco.giorni / fisco.giorni_anno / fisco.periodi,
              max(0, fisco.detrazione + fisco.oneri / fisco.periodi - fisco.imposta)), 0)), 2)"""


# Ulteriore detrazione di prova, come la norma reale: 1000 da 20000 a 32000, poi decrescente fino a 40000. Per la soglia cumulata.
PARAMETRI_ULTERIORE = {
    "ulteriore_importo": "1000",
    "ulteriore_soglia_1": "20000",
    "ulteriore_soglia_2": "32000",
    "ulteriore_soglia_3": "40000",
    "ulteriore_divisore": "8000",
}
ULTERIORE = """arrotonda(
    se((fisco.imponibile * fisco.periodi) > parametro.ulteriore_soglia_1,
       se((fisco.imponibile * fisco.periodi) <= parametro.ulteriore_soglia_2,
          parametro.ulteriore_importo,
          se((fisco.imponibile * fisco.periodi) <= parametro.ulteriore_soglia_3,
             parametro.ulteriore_importo * (parametro.ulteriore_soglia_3 - (fisco.imponibile * fisco.periodi)) / parametro.ulteriore_divisore,
             0)),
       0) * fisco.giorni / fisco.giorni_anno / fisco.periodi, 2)"""


def parametri_benefici(sovrascrivi=None) -> str:
    valori = {**PARAMETRI_BENEFICI, **PARAMETRI_ULTERIORE, **(sovrascrivi or {})}
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


def beneficio(somma=SOMMA_ESENTE, integrativo=INTEGRATIVO, categorie_se='["lavoro_dipendente"]',
              categorie_ti='["lavoro_dipendente"]', extra="", versione=1, dal="2020-01-01"):
    return f"""
[[beneficio]]
versione = {versione}
dal = {dal}
riferimento = "fittizio:beneficio"
categorie_somma_esente = {categorie_se}
categorie_trattamento_integrativo = {categorie_ti}
somma_esente = '''{somma}'''
trattamento_integrativo = '''{integrativo}'''
istituto_somma_esente = "somma_esente"
istituto_trattamento_integrativo = "trattamento_integrativo"
recupero_somma_esente = "somma_esente_recupero"
recupero_trattamento_integrativo = "trattamento_integrativo_recupero"
soglia_recupero = "recupero_soglia"
rate_somma_esente = "recupero_rate_se"
rate_trattamento_integrativo = "recupero_rate_ti"
{extra}"""


# Composizione e codici dei quattro istituti: i riconosciuti sono crediti del sostituto sul netto, i recuperi debiti F24EP.
COMPOSIZIONE_BENEFICI = (
    ("somma_esente", "credito_sostituto", "piu", "beneficiario", "accredito", "175E"),
    ("trattamento_integrativo", "credito_sostituto", "piu", "beneficiario", "accredito", "170E"),
    ("somma_esente_recupero", "trattenuta_terzi", "meno", "terzo", "f24ep", "175E"),
    ("trattamento_integrativo_recupero", "trattenuta_terzi", "meno", "terzo", "f24ep", "170E"),
)


def composizione_benefici() -> str:
    testo = ""
    for istituto, natura, effetto, destinatario, canale, codice in COMPOSIZIONE_BENEFICI:
        nome = istituto.replace("_", "-")
        testo += f'''
[[composizione]]
istituto = "{istituto}"
dal = 2020-01-01
riferimento = "fittizio:comp-{nome}"
natura = "{natura}"
effetto = "{effetto}"
destinatario = "{destinatario}"
canale = "{canale}"

[[mappatura]]
istituto = "{istituto}"
sistema = "codice_tributo_f24ep"
codice = "{codice}"
dal = 2020-01-01
riferimento = "fittizio:mappatura-{nome}"
'''
    return testo


TESTO_BENEFICI = TESTO + parametri_benefici() + beneficio()


def con_ulteriore_detrazione(testo: str) -> str:
    marca = 'detrazione_richiesta = "lavoro_dipendente"\n'
    assert marca in testo
    return testo.replace(marca, marca + "detrazione_automatica = '''" + ULTERIORE + "'''\n")


def corpus_benefici(parametri=None, **modifiche) -> Corpus:
    return Corpus.da_toml(con_ulteriore_detrazione(TESTO) + parametri_benefici(parametri) + beneficio(**modifiche))



# Pagamenti di prova con i benefici dentro l'esito pagato

from datetime import date  # noqa: E402

from paghe import Mese, TipoEsito, attribuisci_reddito, calcola_fiscale, emetti_esito  # noqa: E402

from test_fiscale import R, assumi, stipendio  # noqa: E402,F401


def paga_con_benefici(registro, orologio, corpus, righe, giorno, rapporto=R, ultimo=False):
    """Come `paga` di test_fiscale, ma l'esito pagato porta anche i benefici e i recuperi."""
    orologio.vai(giorno.month, giorno.day, giorno.year)
    attribuite = attribuisci_reddito(corpus, righe, giorno)
    fiscale = calcola_fiscale(registro, corpus, rapporto, attribuite, giorno, ultimo_dell_anno=ultimo)
    contenuto = [*attribuite, fiscale.ritenuta, *([fiscale.conguaglio] if fiscale.conguaglio else []), *fiscale.benefici]
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, contenuto)
    registro.registra_pagamento(rapporto, esito.id, giorno)
    orologio.avanza()
    return esito, fiscale


def mese_pagato(registro, orologio, corpus, numero, importo="1000", anno=2026, ultimo=False, rapporto=R):
    """Stipendio del mese pagato il 27."""
    orologio.vai(numero, 1, anno)
    righe = stipendio(registro, corpus, Mese(anno, numero), importo, rapporto)
    return paga_con_benefici(registro, orologio, corpus, righe, date(anno, numero, 27), rapporto, ultimo)


def del_beneficio(fiscale, istituto):
    trovati = [i for i in fiscale.benefici if i.istituto == istituto]
    assert len(trovati) == 1, [i.istituto for i in fiscale.benefici]
    return trovati[0]


def assumi_fino_al(registro, al, rapporto=R, persona="PERSONA-1", dal=date(2026, 1, 1)):
    """Un rapporto con il servizio dal `dal` fino al `al` compreso: dopo, la persona e' cessata."""
    from test_fiscale import CF

    if not registro.fatti_persona_noti(persona, "codice_fiscale", registro.adesso()):
        registro.registra_codice_persona(persona, "codice_fiscale", CF, date(1980, 1, 1))
    registro.collega_rapporto(rapporto, persona, dal)
    registro.registra_codice(rapporto, "tipo_impiego", "1", dal, al)
