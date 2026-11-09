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


# Regola di scadenza e calendario dei festivi

SCADENZA = """
[[scadenza_f24ep]]
dal = 2020-01-01
al = 2026-12-31
giorno = 16
riferimento = "fittizio:scadenza-16"
[scadenza_f24ep.proroga]
mese = 8
dal_giorno = 1
al_giorno = 20
fonte = "prassi"
riferimento = "fittizio:proroga-agosto"

[[calendario_festivi]]
anno = 2026
feste = ["01-01", "12-25"]
lunedi_dell_angelo = true
riferimento = "fittizio:festivi-2026"
"""


def test_la_regola_di_scadenza_dice_giorno_proroga_e_tipo_di_fonte():
    regola = corpus(SCADENZA).regola_scadenza_f24ep(date(2026, 3, 1))
    assert (regola.giorno, regola.riferimento) == (16, "fittizio:scadenza-16")
    proroga = regola.proroga
    assert (proroga.mese, proroga.dal_giorno, proroga.al_giorno, proroga.fonte) == (8, 1, 20, "prassi")


def test_la_regola_di_scadenza_ha_una_vigenza():
    c = corpus(SCADENZA)
    assert c.regola_scadenza_f24ep(date(2026, 12, 31)) is not None
    assert c.regola_scadenza_f24ep(date(2027, 1, 1)) is None


def test_la_proroga_senza_fonte_o_con_fonte_ignota_e_rifiutata():
    with pytest.raises(ErroreCorpus, match="fonte"):
        corpus(SCADENZA.replace('fonte = "prassi"', 'fonte = "voce"'))
    with pytest.raises(ErroreCorpus, match="fonte"):
        corpus(SCADENZA.replace('fonte = "prassi"\n', ""))


def test_la_proroga_ha_un_riferimento_obbligatorio():
    with pytest.raises(ErroreCorpus, match="riferimento"):
        corpus(SCADENZA.replace('riferimento = "fittizio:proroga-agosto"', 'riferimento = ""'))


def test_giorno_e_proroga_incoerenti_sono_rifiutati():
    with pytest.raises(ErroreCorpus, match="giorno"):
        corpus(SCADENZA.replace("giorno = 16", "giorno = 32"))
    with pytest.raises(ErroreCorpus, match="proroga"):
        corpus(SCADENZA.replace("al_giorno = 20", "al_giorno = 0"))


def test_regole_di_scadenza_sovrapposte_sono_rifiutate():
    doppia = SCADENZA + SCADENZA.split("[[calendario_festivi]]")[0].replace("al = 2026-12-31\n", "")
    with pytest.raises(ErroreCorpus, match="sovrapposte"):
        corpus(doppia)


def test_il_calendario_dice_i_festivi_dell_anno_con_il_riferimento_e_calcola_il_lunedi_dell_angelo():
    calendario = corpus(SCADENZA).calendario_festivi(2026)
    assert calendario.giorni == (date(2026, 1, 1), date(2026, 12, 25), date(2026, 4, 6))
    assert calendario.riferimento == "fittizio:festivi-2026"
    assert corpus(SCADENZA).calendario_festivi(2027) is None


def test_senza_lunedi_dell_angelo_dichiarato_i_giorni_sono_solo_le_feste():
    senza = SCADENZA.replace("lunedi_dell_angelo = true", "lunedi_dell_angelo = false")
    assert corpus(senza).calendario_festivi(2026).giorni == (date(2026, 1, 1), date(2026, 12, 25))


def test_il_4_ottobre_dal_2026_e_un_giorno_festivo_anche_di_domenica():
    festa = SCADENZA.replace('"12-25"]', '"10-04", "12-25"]')
    assert date(2026, 10, 4) in corpus(festa).calendario_festivi(2026).giorni  # domenica


def test_una_festa_malformata_o_inesistente_o_ripetuta_e_rifiutata():
    with pytest.raises(ErroreCorpus, match="12-25"):
        corpus(SCADENZA.replace('"12-25"]', '"2026-12-25"]'))
    with pytest.raises(ErroreCorpus, match="02-30"):
        corpus(SCADENZA.replace('"12-25"]', '"02-30"]'))
    with pytest.raises(ErroreCorpus, match="ripetut"):
        corpus(SCADENZA.replace('"12-25"]', '"01-01"]'))


def test_il_riferimento_del_calendario_e_obbligatorio():
    with pytest.raises(ErroreCorpus, match="riferimento"):
        corpus(SCADENZA.replace('riferimento = "fittizio:festivi-2026"', 'riferimento = ""'))


def test_due_calendari_dello_stesso_anno_sono_rifiutati():
    doppio = SCADENZA + '\n[[calendario_festivi]]\nanno = 2026\nfeste = []\nriferimento = "fittizio:altro"\n'
    with pytest.raises(ErroreCorpus, match="2026"):
        corpus(doppio)


def test_scadenza_e_calendario_cambiano_la_versione_del_corpus():
    assert corpus("").versione != corpus(SCADENZA).versione
    assert corpus(SCADENZA).versione != corpus(SCADENZA.replace('"12-25"]', '"12-26"]')).versione


def test_la_natura_irap_e_ammessa_nella_composizione():
    """Serve a riconoscere le righe IRAP, che la delega versa per regione col 380E (ADR 0028)."""
    testo = """
[[parametro]]
nome = "aliquota"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "0.085"
riferimento = "fittizio:aliquota-irap"

[[regola]]
istituto = "irap_acconto"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:irap"
formula = "fatto.base * parametro.aliquota"
maturazione = "evento"
applica_se = "base"

[[composizione]]
istituto = "irap_acconto"
dal = 2020-01-01
riferimento = "fittizio:comp-irap"
natura = "irap"
effetto = "nessuno"
destinatario = "terzo"
canale = "f24ep"
"""
    assert corpus(testo).composizione("irap_acconto", date(2026, 1, 1)).natura == "irap"
