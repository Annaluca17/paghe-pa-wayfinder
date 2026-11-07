"""Catalogo dei codici F24EP, regola di scadenza e calendario dei festivi nel corpus (ticket #54). Dati fittizi."""

from datetime import date

import pytest

from paghe import Corpus
from paghe.errori import ErroreCorpus

CODICE_100E = """
[[codice_f24ep]]
codice = "100E"
sezione = "F"
codice_campo = "nessuno"
estremi = "nessuno"
rif_a = "mese_pagamento"
rif_b = "anno_pagamento"
modalita = "debito"
dal = 2020-01-01
riferimento = "fittizio:cod-100e"
"""


def corpus(testo: str) -> Corpus:
    return Corpus.da_toml(testo)


def test_il_catalogo_dice_sezione_formato_dei_riferimenti_e_modalita():
    c = corpus(CODICE_100E).codice_f24ep("100E", date(2026, 3, 1))
    assert (c.codice, c.sezione, c.codice_campo, c.estremi) == ("100E", "F", "nessuno", "nessuno")
    assert (c.rif_a, c.rif_b, c.modalita, c.limite_credito) == ("mese_pagamento", "anno_pagamento", "debito", "nessuno")


def test_un_codice_fuori_catalogo_non_ha_voce():
    assert corpus(CODICE_100E).codice_f24ep("999E", date(2026, 3, 1)) is None


def test_la_voce_del_catalogo_ha_una_vigenza():
    c = corpus(CODICE_100E.replace("dal = 2020-01-01", "dal = 2026-01-01\nal = 2026-12-31"))
    assert c.codice_f24ep("100E", date(2025, 12, 31)) is None
    assert c.codice_f24ep("100E", date(2026, 12, 31)) is not None
    assert c.codice_f24ep("100E", date(2027, 1, 1)) is None


def test_vigenze_sovrapposte_dello_stesso_codice_sono_rifiutate():
    with pytest.raises(ErroreCorpus, match="sovrapposte"):
        corpus(CODICE_100E + CODICE_100E)


@pytest.mark.parametrize(
    "campo, valore",
    [
        ("sezione", "Z"),
        ("codice_campo", "boh"),
        ("estremi", "obbligatorio"),
        ("rif_a", "oggi"),
        ("rif_b", "domani"),
        ("modalita", "credito"),
    ],
)
def test_un_valore_fuori_elenco_e_rifiutato(campo, valore):
    riga = next(r for r in CODICE_100E.splitlines() if r.startswith(campo + " "))
    with pytest.raises(ErroreCorpus, match=campo):
        corpus(CODICE_100E.replace(riga, f'{campo} = "{valore}"'))


def test_il_riferimento_del_catalogo_e_obbligatorio():
    with pytest.raises(ErroreCorpus, match="riferimento"):
        corpus(CODICE_100E.replace('riferimento = "fittizio:cod-100e"', 'riferimento = ""'))


def test_il_limite_del_credito_vale_solo_per_un_codice_usabile_a_credito():
    errato = CODICE_100E.replace('modalita = "debito"', 'modalita = "debito"\nlimite_credito = "non_modellato"')
    with pytest.raises(ErroreCorpus, match="limite_credito"):
        corpus(errato)
    giusto = CODICE_100E.replace('modalita = "debito"', 'modalita = "debito_credito"\nlimite_credito = "non_modellato"')
    assert corpus(giusto).codice_f24ep("100E", date(2026, 1, 1)).limite_credito == "non_modellato"


def test_il_catalogo_cambia_la_versione_del_corpus_solo_se_c_e():
    assert corpus("").versione != corpus(CODICE_100E).versione
    assert corpus("").versione == Corpus.da_toml("").versione


def test_un_corpus_reale_non_ammette_un_riferimento_fittizio_nel_catalogo():
    with pytest.raises(ErroreCorpus, match="fittizio"):
        Corpus.da_toml(CODICE_100E, reale=True)
