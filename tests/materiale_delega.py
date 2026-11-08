"""Materiale comune ai test della delega F24EP (ticket #54). Dati e riferimenti esclusivamente fittizi.

I codici tributo e le causali degli esempi sono quelli confermati dalla ricerca (`docs/research/versamenti-f24ep.md`):
100E, 104E (ritenute), P201 (CPDEL), 150E, 170E, 175E (crediti), 384E, 380E (con codice catastale o regione).
"""

from datetime import UTC, date, datetime
from decimal import Decimal

from paghe import Corpus, Periodo, Registro, leggi_versione
from paghe.delega import SISTEMA_F24EP
from paghe.modello import Derivazione, Importo
from paghe.proposta import (
    ContenutoVersione,
    NettoRapporto,
    RigaComposizione,
    _in_dizionario,
    conferma_versione,
    registra_pagamento_eseguito,
)

from materiale_proposta import CORPUS_PROPOSTA, R, R2  # noqa: F401  (riesportati ai test)

CF_ENTE = "00000000000"  # codice fiscale di fantasia dell'ente, cifra di controllo valida
IBAN_TESORERIA = "IT76X0100003245TEST00000001"  # IBAN di prova: conto evidentemente finto
SIGLA = "RM"
ADATTATORE = "adattatore-prova"

# Festivi del calendario di prova: i fissi e il lunedì di Pasqua (5 aprile 2026, 28 marzo 2027, 16 aprile 2028).
FESTIVI_FISSI = ("01-01", "01-06", "04-25", "05-01", "06-02", "08-15", "11-01", "12-08", "12-25", "12-26")
PASQUETTA = {2026: "2026-04-06", 2027: "2027-03-29", 2028: "2028-04-17"}


def _calendario(anno: int, extra: tuple[str, ...] = ()) -> str:
    giorni = [f"{anno}-{fisso}" for fisso in FESTIVI_FISSI] + [PASQUETTA[anno], *[e for e in extra if e.startswith(str(anno))]]
    return f'''
[[calendario_festivi]]
anno = {anno}
giorni = [{", ".join(sorted(giorni))}]
riferimento = "fittizio:festivi-{anno}"
'''


SCADENZE = '''
[[scadenza_f24ep]]
dal = 2020-01-01
al = 2026-12-31
giorno = 16
riferimento = "fittizio:scadenza-2026"
[scadenza_f24ep.proroga]
mese = 8
dal_giorno = 1
al_giorno = 20
fonte = "prassi"
riferimento = "fittizio:proroga-2026"

[[scadenza_f24ep]]
dal = 2027-01-01
giorno = 16
riferimento = "fittizio:scadenza-2027"
[scadenza_f24ep.proroga]
mese = 8
dal_giorno = 1
al_giorno = 20
fonte = "prassi"
riferimento = "fittizio:proroga-2027"
'''


def toml_scadenza(extra_festivi: tuple[str, ...] = ()) -> str:
    return SCADENZE + "".join(_calendario(anno, extra_festivi) for anno in (2026, 2027, 2028))


def corpus_scadenza(extra_festivi: tuple[str, ...] = ()) -> Corpus:
    return Corpus.da_toml(toml_scadenza(extra_festivi))


# Catalogo, mappature e istituti di prova

def _codice(codice, sezione, campo, estremi, rif_a, rif_b, modalita, limite=None):
    riga_limite = f'limite_credito = "{limite}"\n' if limite else ""
    return f'''
[[codice_f24ep]]
codice = "{codice}"
sezione = "{sezione}"
codice_campo = "{campo}"
estremi = "{estremi}"
rif_a = "{rif_a}"
rif_b = "{rif_b}"
modalita = "{modalita}"
{riga_limite}dal = 2020-01-01
riferimento = "fittizio:codice-{codice.lower()}"
'''


CATALOGO = "".join(
    [
        _codice("100E", "F", "nessuno", "nessuno", "mese_pagamento", "anno_pagamento", "debito"),
        _codice("104E", "F", "nessuno", "nessuno", "mese_pagamento", "anno_pagamento", "debito"),
        _codice("P201", "Q", "provincia", "facoltativo", "periodo_inizio", "periodo_fine", "debito"),
        _codice("150E", "F", "nessuno", "nessuno", "nessuno", "anno_imposta", "debito_credito"),
        _codice("170E", "F", "nessuno", "nessuno", "mese_pagamento", "anno_pagamento", "debito_credito"),
        _codice("175E", "F", "nessuno", "nessuno", "mese_pagamento", "anno_pagamento", "debito_credito", "non_modellato"),
        _codice("384E", "S", "catastale", "nessuno", "mese_pagamento", "anno_pagamento", "debito"),
        _codice("380E", "R", "regione", "nessuno", "mese_pagamento", "anno_pagamento", "debito"),
    ]
)

# Istituti di prova per le righe fatte a mano: (istituto, natura, effetto, destinatario, canale, codice tributo o None)
ISTITUTI_A_MANO = (
    ("ritenuta_arretrati", "ritenuta", "meno", "terzo", "f24ep", "104E"),
    ("rimborso_irpef_730", "rimborso_730", "nessuno", "terzo", "f24ep", "150E"),
    ("rimborso_730_sul_netto", "rimborso_730", "piu", "beneficiario", "accredito", "150E"),
    ("credito_integrativo", "credito_sostituto", "nessuno", "terzo", "f24ep", "170E"),
    ("credito_somma_175", "credito_sostituto", "nessuno", "terzo", "f24ep", "175E"),
    ("credito_senza_codice", "credito_sostituto", "nessuno", "terzo", "f24ep", None),
    ("credito_su_codice_a_debito", "credito_sostituto", "nessuno", "terzo", "f24ep", "100E"),
    ("debito_senza_codice", "trattenuta_terzi", "meno", "terzo", "f24ep", None),
    ("debito_codice_ignoto", "trattenuta_terzi", "meno", "terzo", "f24ep", "999E"),
    ("addizionale_comunale", "addizionale", "meno", "terzo", "f24ep", "384E"),
    ("irap_acconto", "irap", "nessuno", "terzo", "f24ep", "380E"),
    ("pignoramento", "trattenuta_terzi", "meno", "terzo", "bonifico", None),
)


def _mappatura(istituto, codice):
    return f'''
[[mappatura]]
istituto = "{istituto}"
sistema = "{SISTEMA_F24EP}"
codice = "{codice}"
dal = 2020-01-01
riferimento = "fittizio:mappatura-{istituto.replace("_", "-")}"
'''


def _istituto_a_mano(istituto, natura, effetto, destinatario, canale, codice):
    nome = istituto.replace("_", "-")
    testo = f'''
[[regola]]
istituto = "{istituto}"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:{nome}"
formula = "fatto.{istituto}"
maturazione = "evento"
applica_se = "{istituto}"

[[composizione]]
istituto = "{istituto}"
dal = 2020-01-01
riferimento = "fittizio:comp-{nome}"
natura = "{natura}"
effetto = "{effetto}"
destinatario = "{destinatario}"
canale = "{canale}"
'''
    return testo + (_mappatura(istituto, codice) if codice else "")


MAPPATURE_DEL_CICLO = "".join(
    _mappatura(istituto, codice)
    for istituto, codice in (
        ("contributo_lavoratore", "P201"),
        ("contributo_ente", "P201"),
        ("ritenuta_irpef", "100E"),
        ("conguaglio_irpef", "100E"),
    )
)


def _regione(nome, codice):
    return f'''
[[mappatura_fatto]]
sistema = "f24ep.codice_regione"
elemento = "codice_regione"
fatto = "sede_lavoro"
valore = "{nome}"
codice = "{codice}"
dal = 2020-01-01
riferimento = "fittizio:regione-{nome}"
'''


# Codici regione di prova: solo i due che i test usano.
REGIONI = "".join(_regione(nome, codice) for nome, codice in (("lazio", "08"), ("lombardia", "10")))


def toml_delega(extra_festivi: tuple[str, ...] = ()) -> str:
    return (
        CORPUS_PROPOSTA
        + REGIONI
        + MAPPATURE_DEL_CICLO
        + "".join(_istituto_a_mano(*voce) for voce in ISTITUTI_A_MANO)
        + CATALOGO
        + toml_scadenza(extra_festivi)
    )


def corpus_delega(extra_festivi: tuple[str, ...] = ()) -> Corpus:
    return Corpus.da_toml(toml_delega(extra_festivi))


def dati_ente(registro: Registro, dal=date(2026, 1, 1), **modifiche) -> None:
    """I fatti sull'ente che la delega legge; `modifiche` con None toglie quel fatto."""
    dati = {
        "codice_fiscale": CF_ENTE,
        "denominazione": "ENTE DI PROVA",
        "email": "paghe@ente.example",
        "iban_tesoreria": IBAN_TESORERIA,
        "sigla_provincia": SIGLA,
        "regione": "lazio",
    }
    dati.update(modifiche)
    for tipo, valore in dati.items():
        if valore is not None:
            registro.registra_codice_ente(tipo, valore, dal)


# Righe fatte a mano: versioni e pagamenti di prova che non passano dal calcolo

def importo(istituto, valore, rapporto=R, periodo=Periodo(date(2026, 2, 1), date(2026, 2, 28)), anno_imposta=None):
    """Un importo già calcolato, di prova: derivato, così non è tassato né attribuito a un anno."""
    derivazione = Derivazione(
        istituto, "periodo", 1, "fittizio:prova", "0", "corpus-di-prova", datetime(2026, 1, 1, tzinfo=UTC), (), (), ()
    )
    return Importo(rapporto, istituto, periodo, Decimal(valore), derivazione, anno_imposta=anno_imposta)


def riga_a_mano(corpus, valuta, istituto, valore, **kwargs):
    dichiarazione = corpus.composizione(istituto, valuta)
    return RigaComposizione(
        importo(istituto, valore, **kwargs),
        dichiarazione.natura,
        dichiarazione.effetto,
        dichiarazione.destinatario,
        dichiarazione.canale,
        dichiarazione.riferimento,
    )


def paga_a_mano(registro, corpus, orologio, valuta, righe, chiave="pag-mano", rapporti=None):
    """Versione scritta a mano, confermata e pagata alla `valuta`: restituisce la versione."""
    elenco = tuple(righe)
    ordinati = sorted({r.rapporto for r in elenco})
    contenuto = ContenutoVersione(
        valuta_prevista=valuta,
        righe=elenco,
        netti=tuple(NettoRapporto(rapporto, Decimal(0)) for rapporto in ordinati),
        esclusi=(),
        fermi=(),
        dati_mancanti=(),
        avvisi=(),
    )
    orologio.vai(valuta.month, valuta.day, valuta.year)
    versione_id, _ = registro.registra_versione(valuta, _in_dizionario(contenuto))
    conferma_versione(registro, versione_id)
    registra_pagamento_eseguito(registro, corpus, chiave, ADATTATORE, versione_id, valuta, rapporti or ordinati)
    orologio.avanza()
    return leggi_versione(registro, versione_id)
