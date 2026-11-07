"""Dichiarazione di composizione e mappatura esterna nel corpus (ADR 0025). Valori e fonti fittizi."""

from datetime import date

import pytest

from paghe import Corpus
from paghe.errori import ErroreCorpus

from conftest import CORPUS_BASE

ALTRI_ISTITUTI = """
[[parametro]]
nome = "aliquota_irpef"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "0.20"
riferimento = "fittizio:aliquota-irpef"

[[regola]]
istituto = "rimborso"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:art-3"
formula = "fatto.spesa"
maturazione = "evento"
applica_se = "spesa"

[[categoria_reddito]]
nome = "lavoro_dipendente"
[[categoria_reddito.cassa_allargata]]
dal = 2020-01-01
vale = true
riferimento = "fittizio:cassa"

[[ritenuta]]
istituto = "ritenuta_irpef"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:ritenuta"
categorie = ["lavoro_dipendente"]
detrazione_richiesta = "lavoro_dipendente"
imposta = "arrotonda(fisco.imponibile * parametro.aliquota_irpef, 2)"
detrazione = "0"

[[conguaglio]]
istituto = "conguaglio_irpef"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:conguaglio"
"""

COMPOSIZIONE_COMPENSO = """
[[composizione]]
istituto = "compenso"
dal = 2020-01-01
riferimento = "fittizio:comp-compenso"
natura = "retribuzione"
effetto = "piu"
destinatario = "beneficiario"
canale = "accredito"
"""


def corpus(extra: str = "", reale: bool = False) -> Corpus:
    return Corpus.da_toml(CORPUS_BASE + ALTRI_ISTITUTI + extra, reale=reale)


# Dichiarazione di composizione

def test_la_dichiarazione_dice_natura_effetto_destinatario_e_canale():
    c = corpus(COMPOSIZIONE_COMPENSO)
    d = c.composizione("compenso", date(2026, 5, 1))
    assert (d.natura, d.effetto, d.destinatario, d.canale) == ("retribuzione", "piu", "beneficiario", "accredito")
    assert d.riferimento == "fittizio:comp-compenso"
    assert not d.intermedio


def test_una_dichiarazione_assente_non_e_una_dichiarazione_vuota():
    assert corpus().composizione("compenso", date(2026, 5, 1)) is None


def test_la_dichiarazione_vale_nelle_sue_date():
    c = corpus(COMPOSIZIONE_COMPENSO.replace("dal = 2020-01-01", "dal = 2026-03-01\nal = 2026-06-30"))
    assert c.composizione("compenso", date(2026, 2, 28)) is None
    assert c.composizione("compenso", date(2026, 3, 1)) is not None
    assert c.composizione("compenso", date(2026, 6, 30)) is not None
    assert c.composizione("compenso", date(2026, 7, 1)) is None


def test_un_istituto_intermedio_non_entra_e_non_dichiara_altro():
    c = corpus(
        '[[composizione]]\nistituto = "ritenuta"\ndal = 2020-01-01\nriferimento = "fittizio:interm"\nintermedio = true\n'
    )
    d = c.composizione("ritenuta", date(2026, 5, 1))
    assert d.intermedio
    assert (d.natura, d.effetto, d.destinatario, d.canale) == (None, None, None, None)


def test_un_intermedio_con_natura_e_incoerente():
    with pytest.raises(ErroreCorpus, match="intermedio"):
        corpus(
            '[[composizione]]\nistituto = "ritenuta"\ndal = 2020-01-01\nriferimento = "fittizio:x"\n'
            'intermedio = true\nnatura = "ritenuta"\n'
        )


@pytest.mark.parametrize("campo", ["natura", "effetto", "destinatario", "canale"])
def test_una_dichiarazione_non_intermedia_vuole_tutti_i_campi(campo):
    senza = "\n".join(riga for riga in COMPOSIZIONE_COMPENSO.splitlines() if not riga.startswith(campo))
    with pytest.raises(ErroreCorpus, match=campo):
        corpus(senza)


@pytest.mark.parametrize(
    "campo, valore", [("natura", "voce_inventata"), ("effetto", "forse"), ("destinatario", "nessuno"), ("canale", "contanti")]
)
def test_un_valore_fuori_elenco_e_rifiutato(campo, valore):
    errata = COMPOSIZIONE_COMPENSO.replace(
        next(r for r in COMPOSIZIONE_COMPENSO.splitlines() if r.startswith(campo)), f'{campo} = "{valore}"'
    )
    with pytest.raises(ErroreCorpus, match=campo):
        corpus(errata)


def test_le_nature_ammesse():
    nature = [
        "retribuzione", "ritenuta", "addizionale", "contributo_lavoratore", "contributo_ente",
        "rata_730", "rimborso_730", "credito_sostituto", "trattenuta_terzi",
    ]
    for natura in nature:
        corpus(COMPOSIZIONE_COMPENSO.replace('natura = "retribuzione"', f'natura = "{natura}"'))


def test_il_riferimento_della_dichiarazione_e_obbligatorio():
    with pytest.raises(ErroreCorpus, match="riferimento"):
        corpus(COMPOSIZIONE_COMPENSO.replace('riferimento = "fittizio:comp-compenso"', 'riferimento = ""'))
    with pytest.raises(ErroreCorpus, match="riferimento"):
        corpus(COMPOSIZIONE_COMPENSO.replace('riferimento = "fittizio:comp-compenso"\n', ""))


def test_le_vigenze_della_stessa_dichiarazione_non_si_sovrappongono():
    doppia = COMPOSIZIONE_COMPENSO + COMPOSIZIONE_COMPENSO.replace("dal = 2020-01-01", "dal = 2026-01-01")
    with pytest.raises(ErroreCorpus, match="sovrapposte"):
        corpus(doppia)


def test_vigenze_contigue_della_stessa_dichiarazione_sono_ammesse():
    prima = COMPOSIZIONE_COMPENSO.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2025-12-31")
    dopo = COMPOSIZIONE_COMPENSO.replace("dal = 2020-01-01", "dal = 2026-01-01").replace('"piu"', '"meno"')
    c = corpus(prima + dopo)
    assert c.composizione("compenso", date(2025, 12, 31)).effetto == "piu"
    assert c.composizione("compenso", date(2026, 1, 1)).effetto == "meno"


def test_l_istituto_della_dichiarazione_deve_essere_noto():
    with pytest.raises(ErroreCorpus, match="istituto"):
        corpus(COMPOSIZIONE_COMPENSO.replace('istituto = "compenso"', 'istituto = "sconosciuto"'))


@pytest.mark.parametrize("istituto", ["ritenuta_irpef", "conguaglio_irpef", "ritenuta", "rimborso"])
def test_sono_noti_gli_istituti_con_regola_e_la_ritenuta_e_il_conguaglio_fiscale(istituto):
    corpus(COMPOSIZIONE_COMPENSO.replace('istituto = "compenso"', f'istituto = "{istituto}"'))


def test_il_corpus_reale_rifiuta_i_riferimenti_fittizi_delle_dichiarazioni():
    with pytest.raises(ErroreCorpus, match="fittizio"):
        corpus(COMPOSIZIONE_COMPENSO, reale=True)


# Mappatura esterna

MAPPATURA = """
[[mappatura]]
istituto = "ritenuta_irpef"
sistema = "codice_tributo"
codice = "1001"
dal = 2020-01-01
riferimento = "fittizio:map-ritenuta"
"""


def test_la_mappatura_da_il_codice_del_sistema_esterno():
    m = corpus(MAPPATURA).mappatura("ritenuta_irpef", "codice_tributo", date(2026, 5, 1))
    assert (m.istituto, m.sistema, m.codice, m.riferimento) == (
        "ritenuta_irpef", "codice_tributo", "1001", "fittizio:map-ritenuta",
    )


def test_una_mappatura_assente_e_none_non_un_errore():
    c = corpus(MAPPATURA)
    assert c.mappatura("ritenuta_irpef", "causale", date(2026, 5, 1)) is None
    assert c.mappatura("conguaglio_irpef", "codice_tributo", date(2026, 5, 1)) is None


def test_piu_istituti_possono_avere_lo_stesso_codice():
    stesso = MAPPATURA + MAPPATURA.replace("ritenuta_irpef", "conguaglio_irpef")
    c = corpus(stesso)
    assert c.mappatura("ritenuta_irpef", "codice_tributo", date(2026, 5, 1)).codice == "1001"
    assert c.mappatura("conguaglio_irpef", "codice_tributo", date(2026, 5, 1)).codice == "1001"


def test_un_istituto_ha_un_solo_codice_per_sistema_alla_stessa_data():
    con_altro_codice = MAPPATURA + MAPPATURA.replace('"1001"', '"1002"')
    with pytest.raises(ErroreCorpus, match="sovrapposte"):
        corpus(con_altro_codice)


def test_lo_stesso_istituto_puo_avere_codici_in_sistemi_diversi():
    c = corpus(MAPPATURA + MAPPATURA.replace("codice_tributo", "causale").replace('"1001"', '"CAU"'))
    assert c.mappatura("ritenuta_irpef", "causale", date(2026, 5, 1)).codice == "CAU"


def test_il_codice_cambia_con_le_date_della_mappatura():
    prima = MAPPATURA.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-12-31")
    dopo = MAPPATURA.replace("dal = 2020-01-01", "dal = 2027-01-01").replace('"1001"', '"1002"')
    c = corpus(prima + dopo)
    assert c.mappatura("ritenuta_irpef", "codice_tributo", date(2026, 12, 31)).codice == "1001"
    assert c.mappatura("ritenuta_irpef", "codice_tributo", date(2027, 1, 1)).codice == "1002"


def test_il_codice_si_sceglie_sull_anno_d_imposta_quando_l_importo_lo_porta():
    """Anno d'imposta 2026: vale la mappatura del 31 dicembre 2026, anche se si paga il 10 gennaio 2027."""
    prima = MAPPATURA.replace("dal = 2020-01-01", "dal = 2020-01-01\nal = 2026-12-31")
    dopo = MAPPATURA.replace("dal = 2020-01-01", "dal = 2027-01-01").replace('"1001"', '"1002"')
    c = corpus(prima + dopo)
    pagamento = date(2027, 1, 10)
    assert c.mappatura("ritenuta_irpef", "codice_tributo", pagamento, anno_imposta=2026).codice == "1001"
    assert c.mappatura("ritenuta_irpef", "codice_tributo", pagamento).codice == "1002"


def test_la_mappatura_vuole_riferimento_sistema_e_codice():
    for tolto in ('riferimento = "fittizio:map-ritenuta"\n', 'sistema = "codice_tributo"\n', 'codice = "1001"\n'):
        with pytest.raises(ErroreCorpus):
            corpus(MAPPATURA.replace(tolto, ""))
    with pytest.raises(ErroreCorpus, match="codice"):
        corpus(MAPPATURA.replace('codice = "1001"', "codice = 1001"))


def test_l_istituto_della_mappatura_deve_essere_noto():
    with pytest.raises(ErroreCorpus, match="istituto"):
        corpus(MAPPATURA.replace("ritenuta_irpef", "sconosciuto"))


def test_il_corpus_reale_rifiuta_i_riferimenti_fittizi_della_mappatura():
    with pytest.raises(ErroreCorpus, match="fittizio"):
        corpus(MAPPATURA, reale=True)


# Versione del corpus

def test_la_versione_dei_corpus_senza_dichiarazioni_non_cambia():
    """L'impronta cambia solo se compaiono composizioni o mappature: il corpus di base ha la versione di prima."""
    assert Corpus.da_toml(CORPUS_BASE).versione == "51a715efce086279"


def test_composizioni_e_mappature_entrano_nell_impronta():
    base = corpus().versione
    con_composizione = corpus(COMPOSIZIONE_COMPENSO).versione
    con_mappatura = corpus(MAPPATURA).versione
    assert len({base, con_composizione, con_mappatura}) == 3
    assert corpus(COMPOSIZIONE_COMPENSO).versione == con_composizione
    assert corpus(COMPOSIZIONE_COMPENSO.replace('"piu"', '"meno"')).versione != con_composizione
