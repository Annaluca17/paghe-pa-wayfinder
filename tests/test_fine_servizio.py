"""Contribuzione TFS ex INADEL (ticket #33, parte 1).

Due gruppi di test. Il primo prova i meccanismi nuovi del motore con un corpus fittizio: una
regola di cassa condizionata da un codice e un fermo che scatta solo per un valore. Il secondo
prova il corpus reale. Gli importi attesi sono ricalcolati a mano dalle fonti: art. 11
L. 152/1968 (6,10% sull'80%, ente 3,60, iscritto 2,50) e art. 33 c. 3 CCNL 22/01/2004.
Arrotondamenti come la CPDEL (nota di prassi 3). Persone e rapporti sono di fantasia.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Corpus, Mese, TipoEsito, calcola, calcola_denuncia, differenze, emetti_esito, spiega
from paghe.errori import CasoNonModellato, ErroreCorpus

R = "RAPPORTO-1"
CF = "RSSMRA80A01H501U"


def paga(registro, orologio, righe, giorno):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(R, esito.id, giorno)
    orologio.avanza()
    return esito


def importi(periodo):
    return {riga.istituto: riga.valore for riga in (*periodo.basi, *periodo.contributi)}


# --- Meccanismi del motore, corpus fittizio ---

FITTIZIO = """
[periodo_dichiarato]
servizio = "tipo_impiego"
fatti = ["regime"]

[[fermo]]
fatto = "regime"
codice = "2"
caso = "regime 2 non modellato"
ambito = "denuncia"
riferimento = "fittizio:fermo-regime-2"

[[base]]
nome = "pens"
riferimento = "fittizio:base-pens"

[[base]]
nome = "fs"
riferimento = "fittizio:base-fs"

[[parametro]]
nome = "mensile"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "1000"
riferimento = "fittizio:mensile"

[[parametro]]
nome = "d"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "26"
riferimento = "fittizio:d"

[[parametro]]
nome = "aliquota_fs"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "0.05"
riferimento = "fittizio:aliquota-fs"

[[regola]]
istituto = "stipendio"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:stipendio"
formula = "parametro.mensile"
maturazione = "giorni"
applica_se = "tipo_impiego"
conteggio = "lun_sab"
divisore = "d"
decimali = 2

[[regola]]
istituto = "contributo_fs"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:contributo-fs"
formula = "arrotonda(base.fs * parametro.aliquota_fs, 2)"
maturazione = "periodo"
applica_se = "regime=3"

[[concorso]]
istituto = "stipendio"
basi = ["pens", "fs"]
misura = "intero"
dal = 2020-01-01
riferimento = "fittizio:concorso"
"""


@pytest.fixture
def fittizio():
    return Corpus.da_toml(FITTIZIO)


def assumi(registro, regime=None, dal=date(2026, 1, 1), al=None):
    fatti = [
        registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1980, 1, 1)),
        registro.collega_rapporto(R, "PERSONA-1", dal),
        registro.registra_codice(R, "tipo_impiego", "1", dal, al),
    ]
    if regime is not None:
        fatti.append(registro.registra_codice(R, "regime", regime, dal, al))
    return fatti


def test_regola_di_cassa_condizionata_dal_codice(registro, fittizio, orologio):
    assumi(registro, regime="3")
    paga(registro, orologio, calcola(registro, fittizio, R, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, fittizio, R, Mese(2026, 11)).periodi
    assert importi(periodo)["contributo_fs"] == Decimal("50.00")
    contributo = next(riga for riga in periodo.contributi if riga.istituto == "contributo_fs")
    assert [fatto.tipo for fatto in contributo.derivazione.fatti] == ["regime"]


@pytest.mark.parametrize("regime", ["1", None])
def test_con_un_altro_codice_o_senza_la_regola_di_cassa_non_si_applica(registro, fittizio, orologio, regime):
    assumi(registro, regime=regime)
    paga(registro, orologio, calcola(registro, fittizio, R, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, fittizio, R, Mese(2026, 11)).periodi
    assert importi(periodo) == {"base.pens": Decimal("1000.00"), "base.fs": Decimal("1000.00")}


def test_fuori_servizio_la_condizione_si_legge_sull_ultimo_giorno_di_servizio(registro, fittizio, orologio):
    """Un recupero su cessato segue il regime che aveva il servizio, anche se il fatto è chiuso."""
    assumi(registro, regime="3", al=date(2026, 10, 15))
    arretrato = calcola(registro, fittizio, R, Mese(2026, 10))
    paga(registro, orologio, arretrato, date(2026, 11, 20))
    periodo, = calcola_denuncia(registro, fittizio, R, Mese(2026, 11)).periodi
    assert not periodo.in_servizio
    assert importi(periodo)["contributo_fs"] == Decimal("25.00")  # 500,00 x 5%


def test_il_fermo_con_codice_scatta_solo_per_quel_valore(registro, fittizio, orologio):
    assumi(registro, regime="2")
    paga(registro, orologio, calcola(registro, fittizio, R, Mese(2026, 11)), date(2026, 11, 27))
    with pytest.raises(CasoNonModellato, match="regime 2 non modellato"):
        calcola_denuncia(registro, fittizio, R, Mese(2026, 11))


def test_il_fermo_con_codice_non_scatta_per_un_altro_valore(registro, fittizio, orologio):
    assumi(registro, regime="3")
    paga(registro, orologio, calcola(registro, fittizio, R, Mese(2026, 11)), date(2026, 11, 27))
    assert calcola_denuncia(registro, fittizio, R, Mese(2026, 11)).periodi


def test_il_codice_del_fermo_cambia_la_versione_del_corpus():
    altro = Corpus.da_toml(FITTIZIO.replace('codice = "2"', 'codice = "1"'))
    assert altro.versione != Corpus.da_toml(FITTIZIO).versione


def test_codice_del_fermo_vuoto_rifiutato():
    with pytest.raises(ErroreCorpus, match="codice"):
        Corpus.da_toml(FITTIZIO.replace('codice = "2"', 'codice = " "'))


# --- Corpus reale ---

CORPUS = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def dipendente(registro, area, regime, dal=date(2026, 1, 1), al=None):
    fatti = [
        registro.registra_codice_persona("PERSONA-1", "codice_fiscale", CF, date(1980, 1, 1)),
        registro.collega_rapporto(R, "PERSONA-1", dal),
        registro.registra_codice(R, "tipo_impiego", "1", dal, al),
        registro.registra_codice(R, "area", area, dal, al),
    ]
    if regime is not None:
        fatti.append(registro.registra_codice(R, "regime_fine_servizio", regime, dal, al))
    return fatti


def stipendi(registro, corpus, *mesi):
    return [riga for mese in mesi for riga in calcola(registro, corpus, R, mese)]


def test_tfs_di_un_mese_intero(registro, reale, orologio):
    dipendente(registro, "istruttori", "3")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    valori = importi(periodo)
    assert valori["base.cpdel"] == Decimal("2051.69")
    assert valori["base.tfs"] == Decimal("2019.63")  # solo il tabellare: il comparto è escluso
    assert valori["imponibile_tfs"] == Decimal("1615.70")  # 2.019,63 x 80%
    assert valori["tfs_totale"] == Decimal("98.56")  # x 6,10%
    assert valori["tfs_lavoratore"] == Decimal("40.39")  # x 2,50%
    assert valori["tfs_ente"] == Decimal("58.17")  # per differenza, pari a 3,60%


def test_tfs_assunto_ad_agosto_e_pagato_a_settembre(registro, reale, orologio):
    dipendente(registro, "funzionari", "3", dal=date(2026, 8, 24))
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 9)).periodi
    valori = importi(periodo)
    assert valori["base.tfs"] == Decimal("2782.18")  # 590,16 + 2.192,02
    assert valori["imponibile_tfs"] == Decimal("2225.74")
    assert valori["tfs_totale"] == Decimal("135.77")
    assert valori["tfs_lavoratore"] == Decimal("55.64")
    assert valori["tfs_ente"] == Decimal("80.13")


def test_il_comparto_e_dichiarato_escluso_dalla_base_tfs(registro, reale, orologio):
    dipendente(registro, "istruttori", "3")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    base = periodo.base("tfs")
    assert [riga.istituto for riga in base.derivazione.importi] == ["tabellare_istruttori"]
    escluso, = [c for c in base.derivazione.concorsi if c.misura == "escluso"]
    assert escluso.istituto == "comparto_istruttori"
    assert escluso.riferimento.startswith("ccnl:S105:2004-01-22~art33-com3")


def test_il_contributo_tfs_cita_la_legge_152_del_1968(registro, reale, orologio):
    dipendente(registro, "istruttori", "3")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    totale = next(riga for riga in periodo.contributi if riga.istituto == "tfs_totale")
    testo = spiega(totale)
    assert "urn:nir:stato:legge:1968-03-08;152~art11" in testo
    assert "regime_fine_servizio" in testo


@pytest.mark.parametrize("regime", ["1", None])
def test_senza_regime_tfs_la_base_c_e_ma_il_contributo_no(registro, reale, orologio, regime):
    """Il TFR arriva con la parte 2; senza regime la vista chiede il dato (ADR 0008)."""
    dipendente(registro, "istruttori", regime)
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    valori = importi(periodo)
    assert valori["base.tfs"] == Decimal("2019.63")
    assert not {"imponibile_tfs", "tfs_totale", "tfs_lavoratore", "tfs_ente"} & valori.keys()


def test_l_optante_ferma_la_denuncia(registro, reale, orologio):
    dipendente(registro, "istruttori", "2")
    righe = stipendi(registro, reale, Mese(2026, 11))
    assert righe
    paga(registro, orologio, righe, date(2026, 11, 27))
    with pytest.raises(CasoNonModellato, match="optante"):
        calcola_denuncia(registro, reale, R, Mese(2026, 11))


def test_recupero_su_cessato_recupera_anche_il_tfs(registro, reale, orologio):
    fatti = dipendente(registro, "istruttori", "3")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 10)), date(2026, 10, 27))

    orologio.vai(11, 3)
    for fatto in fatti[2:]:  # dopo il codice fiscale e il legame con la persona
        registro.annulla_fatto(fatto.id, "cessazione comunicata in ritardo")
    for tipo, codice in (("tipo_impiego", "1"), ("area", "istruttori"), ("regime_fine_servizio", "3")):
        registro.registra_codice(R, tipo, codice, date(2026, 1, 1), date(2026, 10, 15))
    registro.registra_codice(R, "cessazione", "1", date(2026, 10, 16))  # dal giorno dopo l'ultimo di servizio
    recupero = [voce.importo() for voce in differenze(registro, reale, R, Mese(2026, 10), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 11, 20))

    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    assert not periodo.in_servizio
    valori = importi(periodo)
    assert valori["base.tfs"] == Decimal("-1009.81")
    assert valori["imponibile_tfs"] == Decimal("-807.85")
    assert valori["tfs_totale"] == Decimal("-49.28")
    assert valori["tfs_lavoratore"] == Decimal("-20.20")
    assert valori["tfs_ente"] == Decimal("-29.08")


def test_il_regime_non_rende_piu_la_lista_una_bozza(reale):
    """Parte 3: GestPrevidenziale è esposta, il fermo con ambito vista è tolto. Resta l'optante."""
    fermi = {(f.fatto, f.codice, f.ambito) for f in reale.fermi}
    assert not any(ambito == "vista" for _, _, ambito in fermi)
    assert ("regime_fine_servizio", "2", "denuncia") in fermi


# --- TFR (ticket #33, parte 2) ---
# Fonti: DPCM 20/12/1999 art. 1 c. 2, 3 e 7; msg INPS 2440/2019; Circ. INPS 185/2021 § 2.2.1.


def test_riferimento_al_dpcm_ammesso():
    from paghe.riferimento import motivo_rifiuto

    assert motivo_rifiuto("urn:nir:presidente.consiglio.ministri:decreto:1999-12-20~art1-com3") is None
    assert "tipo" in motivo_rifiuto("urn:nir:presidente.consiglio.ministri:legge:1999-12-20")


def test_tfr_riduzione_del_lordo_per_competenza(registro, reale):
    dipendente(registro, "istruttori", "1")
    righe = {riga.istituto: riga.valore for riga in calcola(registro, reale, R, Mese(2026, 11))}
    assert righe == {
        "tabellare_istruttori": Decimal("2019.63"),
        "comparto_istruttori": Decimal("32.06"),
        "riduzione_tfr": Decimal("-40.39"),  # 2,50% di 1.615,70, l'80% del tabellare
    }


def test_tfr_la_riduzione_del_lordo_e_reddito_negativo_di_lavoro_dipendente(registro, reale):
    """DPCM 20/12/1999 art. 1 c. 2-3, ADR 0037: l'imponibile fiscale e' il lordo meno la riduzione, 2.051,69 - 40,39."""
    from paghe import attribuisci_reddito

    dipendente(registro, "istruttori", "1")
    attribuite = attribuisci_reddito(reale, calcola(registro, reale, R, Mese(2026, 11)), date(2026, 11, 27))
    riduzione = next(riga for riga in attribuite if riga.istituto == "riduzione_tfr")
    assert (riduzione.categoria_reddito, riduzione.anno_imposta) == ("lavoro_dipendente", 2026)
    assert sum(riga.valore for riga in attribuite if riga.categoria_reddito == "lavoro_dipendente") == Decimal("2011.30")


@pytest.mark.parametrize("regime", ["3", None])
def test_senza_regime_tfr_nessuna_riduzione(registro, reale, regime):
    dipendente(registro, "istruttori", regime)
    assert "riduzione_tfr" not in {riga.istituto for riga in calcola(registro, reale, R, Mese(2026, 11))}


def test_tfr_di_un_mese_intero(registro, reale, orologio):
    dipendente(registro, "istruttori", "1")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    valori = importi(periodo)
    # La riduzione non entra in nessuna base: è l'incremento figurativo del c. 3.
    assert valori["base.cpdel"] == Decimal("2051.69")
    assert valori["base.fondo_credito"] == Decimal("2051.69")
    assert valori["base.tfs"] == Decimal("2019.63")
    assert valori["imponibile_tfr"] == Decimal("1615.70")
    assert valori["contributo_tfr"] == Decimal("98.56")  # 6,10%, tutto a carico dell'ente
    assert valori["retribuzione_valutabile_tfr"] == Decimal("2019.63")
    assert not {"imponibile_tfs", "tfs_totale", "contributo_tfr_ulteriori"} & valori.keys()


def test_tfr_assunto_ad_agosto_e_pagato_a_settembre(registro, reale, orologio):
    dipendente(registro, "funzionari", "1", dal=date(2026, 8, 24))
    agosto = {riga.istituto: riga.valore for riga in calcola(registro, reale, R, Mese(2026, 8))}
    assert agosto["riduzione_tfr"] == Decimal("-11.80")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 9)).periodi
    valori = importi(periodo)
    assert valori["base.tfs"] == Decimal("2782.18")
    assert valori["imponibile_tfr"] == Decimal("2225.74")
    assert valori["contributo_tfr"] == Decimal("135.77")
    assert valori["retribuzione_valutabile_tfr"] == Decimal("2782.18")


def test_con_il_tfs_nessun_contributo_tfr(registro, reale, orologio):
    dipendente(registro, "istruttori", "3")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    assert not {"imponibile_tfr", "contributo_tfr", "retribuzione_valutabile_tfr"} & importi(periodo).keys()


def test_il_contributo_tfr_cita_il_dpcm(registro, reale, orologio):
    dipendente(registro, "istruttori", "1")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    contributo = next(riga for riga in periodo.contributi if riga.istituto == "contributo_tfr")
    assert "urn:nir:presidente.consiglio.ministri:decreto:1999-12-20~art1-com7" in spiega(contributo)


def test_recupero_su_cessato_in_tfr(registro, reale, orologio):
    fatti = dipendente(registro, "istruttori", "1")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 10)), date(2026, 10, 27))

    orologio.vai(11, 3)
    for fatto in fatti[2:]:  # dopo il codice fiscale e il legame con la persona
        registro.annulla_fatto(fatto.id, "cessazione comunicata in ritardo")
    for tipo, codice in (("tipo_impiego", "1"), ("area", "istruttori"), ("regime_fine_servizio", "1")):
        registro.registra_codice(R, tipo, codice, date(2026, 1, 1), date(2026, 10, 15))
    registro.registra_codice(R, "cessazione", "1", date(2026, 10, 16))  # dal giorno dopo l'ultimo di servizio
    recupero = [voce.importo() for voce in differenze(registro, reale, R, Mese(2026, 10), TipoEsito.PAGATO)]
    assert {riga.istituto: riga.valore for riga in recupero}["riduzione_tfr"] == Decimal("20.19")
    paga(registro, orologio, recupero, date(2026, 11, 20))

    periodo, = calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    valori = importi(periodo)
    assert valori["base.tfs"] == Decimal("-1009.81")
    assert valori["imponibile_tfr"] == Decimal("-807.85")
    assert valori["contributo_tfr"] == Decimal("-49.28")
    assert valori["retribuzione_valutabile_tfr"] == Decimal("-1009.81")


def test_la_riduzione_legge_le_voci_che_concorrono_alla_base_tfs(reale):
    """La formula elenca gli istituti: deve restare allineata alle dichiarazioni di concorso.

    Le tredicesime hanno la loro riduzione annuale, `riduzione_tfr_tredicesima` (ADR 0038)."""
    from paghe.formula import riferimenti
    from paghe.tempo import Periodo

    giorno = Periodo(date(2026, 11, 1), date(2026, 11, 1))
    letti = riferimenti(reale.regola_per("riduzione_tfr", giorno).formula).importi
    interi = {
        istituto
        for istituto in reale.istituti()
        if (concorso := reale.concorso(istituto, "tfs", date(2026, 11, 1))) and concorso.misura == "intero"
    }
    annuali = riferimenti(reale.regola_per("riduzione_tfr_tredicesima", giorno).formula).importi
    assert letti == interi - annuali


def test_ulteriori_elementi_tfr_al_6_91(reale):
    """Nessun istituto del corpus è oggi un ulteriore elemento: la base resta vuota (Pensione-2.0, art. 49 CCNL 2000)."""
    assert reale.parametro("aliquota_tfr_ulteriori").vigenze[-1].valore == Decimal("6.91")
    assert not any(
        (c := reale.concorso(istituto, "tfr_ulteriori", date(2026, 11, 1))) and c.misura == "intero"
        for istituto in reale.istituti()
    )
