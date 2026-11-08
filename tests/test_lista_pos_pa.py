"""Vista ListaPosPA sul corpus reale CPDEL (ticket #29, parte 3; ADR 0008).

Persone, enti e codici fiscali sono di fantasia, con carattere di controllo valido. Gli importi
attesi sono quelli già ricalcolati a mano in test_corpus_reale.py. Lo schema XSD 4.33.1 e
l'Appendice G v15 non sono nel repo (diritti riservati INPS): i test che li usano li cercano nelle
variabili d'ambiente PAGHE_XSD_UNIEMENS e PAGHE_APPENDICE_G e vengono saltati se mancano.
"""

import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from paghe import Corpus, Mese, Periodo, TipoEsito, calcola, calcola_denuncia, differenze, emetti_esito, lista_pos_pa
from paghe.errori import ErrorePaghe, VistaFerma
from paghe.uniemens import Ente, Mittente, importo_in_testo, in_xml

CORPUS = Path(__file__).resolve().parent.parent / "corpus" / "funzioni-locali-cpdel.toml"
R = "RAPPORTO-1"
CF = "RSSMRA80A01H501U"
ENTE = Ente(
    cf_azienda="01234567897",
    ragione_sociale="COMUNE DI FANTASIA",
    prg_azienda="00000",
    cf_rappresentante_firmatario="BNCGNN70C03L219U",
)
MITTENTE = Mittente(
    cf_persona="VRDLGU75B12F205B",
    ragione_sociale="UFFICIO PERSONALE DI FANTASIA",
    cf_mittente="01234567897",
    cf_softwarehouse="98765432103",
    tipo="1",
)
CODICI_AREA = {
    "funzionari": "0FZEQF",
    "istruttori": "0IR000",
    "operatori_esperti": "0OEESP",
    "operatori": "0OP000",
}


@pytest.fixture(scope="module")
def reale():
    return Corpus.carica(CORPUS, reale=True)


def assumi(registro, area="istruttori", dal=date(2026, 1, 1), al=None, regime="3", senza=()):
    """Rapporto completo per la ListaPosPA; `senza` toglie i fatti indicati. Codice fiscale, cognome e nome sono della persona."""
    fatti = {
        "comune_sede_lavoro": ("H501", None),
        "cap_sede_lavoro": ("00100", None),
        "tipo_impiego": ("1", al),
        "tipo_servizio": ("4", al),
        "contratto": ("RALN", al),
        "qualifica": (CODICI_AREA[area], al),
        "area": (area, al),
    }
    if regime is not None:
        fatti["regime_fine_servizio"] = (regime, al)
    for tipo, valore in {"codice_fiscale": CF, "cognome": "ROSSI", "nome": "MARIO"}.items():
        if tipo not in senza:
            registro.registra_codice_persona("PERSONA-1", tipo, valore, date(1980, 1, 1))
    registro.collega_rapporto(R, "PERSONA-1", dal)
    return {
        tipo: registro.registra_codice(R, tipo, valore, dal, fine)
        for tipo, (valore, fine) in fatti.items()
        if tipo not in senza
    }


def stipendi(registro, corpus, *mesi):
    return [riga for mese in mesi for riga in calcola(registro, corpus, R, mese)]


def paga(registro, orologio, righe, giorno):
    orologio.vai(giorno.month, giorno.day, giorno.year)
    esito = emetti_esito(registro, TipoEsito.PAGATO, giorno, righe)
    registro.registra_pagamento(R, esito.id, giorno)
    orologio.avanza()
    return esito


def schema():
    percorso = os.environ.get("PAGHE_XSD_UNIEMENS")
    if not percorso or not Path(percorso).is_file():
        pytest.skip("Schema XSD UniEmens 4.33.1 non disponibile (PAGHE_XSD_UNIEMENS)")
    etree = pytest.importorskip("lxml.etree")
    return etree.XMLSchema(etree.parse(percorso)), etree


def valida(xml):
    xsd, etree = schema()
    documento = etree.fromstring(xml.encode("utf-8"))
    assert xsd.validate(documento), xsd.error_log
    return documento


# --- Importi nel tracciato -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("valore", "testo"),
    [
        ("2051.69", "2051,69"),
        ("0.5", "0,50"),
        ("7", "7,00"),
        ("0", "0,00"),
        ("-334.94", "-334,94"),
        ("0.05", "0,05"),
    ],
)
def test_importo_con_virgola_e_due_decimali(valore, testo):
    assert importo_in_testo(Decimal(valore)) == testo


def test_importo_con_piu_di_due_decimali_rifiutato():
    """La serializzazione non arrotonda: un importo non arrotondato è un errore del calcolo."""
    with pytest.raises(ErrorePaghe, match="decimali"):
        importo_in_testo(Decimal("1.005"))


# --- E0 ----------------------------------------------------------------------------------------


def test_e0_di_un_mese_intero(registro, reale, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))

    assert vista.lavoratore.codice_fiscale == CF
    assert vista.lavoratore.cognome == "ROSSI"
    quadro, = vista.quadri
    assert quadro.tipo == "E0"
    assert quadro.causale is None
    assert quadro.periodo == Periodo(date(2026, 11, 1), date(2026, 11, 30))
    assert quadro.inquadramento.tipo_impiego == "1"
    assert quadro.inquadramento.tipo_servizio == "4"
    assert quadro.inquadramento.contratto == "RALN"
    assert quadro.inquadramento.qualifica == "0IR000"
    assert quadro.inquadramento.regime_fine_servizio == "3"
    assert quadro.pensionistica.imponibile == Decimal("2051.69")
    assert quadro.pensionistica.contributo == Decimal("669.88")
    assert quadro.contrib_1_per_cento is None
    assert quadro.credito.imponibile == Decimal("2051.69")
    assert quadro.credito.contributo == Decimal("7.18")
    assert quadro.codice_cessazione is None
    assert quadro.enti_versanti == ()
    assert vista.mancanti == ()
    assert vista.fermi == ()


def test_l_1_per_cento_va_in_contrib1percento_e_non_nel_contributo(registro, reale, orologio):
    """Circ. INPS 6/2026 § 5: il contributo aggiuntivo si espone a parte."""
    assumi(registro, "operatori_esperti")
    mesi = (Mese(2026, 9), Mese(2026, 10), Mese(2026, 11))
    paga(registro, orologio, stipendi(registro, reale, *mesi), date(2026, 11, 27))
    quadro, settembre, ottobre = lista_pos_pa(registro, reale, R, Mese(2026, 11)).quadri
    assert quadro.tipo == "E0"
    assert quadro.pensionistica.imponibile == Decimal("5472.36")
    assert quadro.pensionistica.contributo == Decimal("1786.73")
    assert quadro.contrib_1_per_cento == Decimal("7.87")
    # Settembre e ottobre, pagati a novembre, si dichiarano solo giuridici (nota di prassi 2).
    assert [(q.tipo, q.causale, q.periodo) for q in (settembre, ottobre)] == [
        ("V1", "5", Mese(2026, 9).periodo),
        ("V1", "5", Mese(2026, 10).periodo),
    ]


def test_i_quadri_portano_gli_importi_da_cui_derivano(registro, reale, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    quadro, = lista_pos_pa(registro, reale, R, Mese(2026, 11)).quadri
    assert {riga.istituto for riga in quadro.importi} >= {"base.cpdel", "cpdel_totale", "base.fondo_credito", "fondo_credito"}


# --- Dati obbligatori da chiedere --------------------------------------------------------------


@pytest.mark.parametrize(
    "fatto",
    ["tipo_servizio", "contratto", "qualifica", "regime_fine_servizio", "cognome", "nome", "comune_sede_lavoro"],
)
def test_un_dato_obbligatorio_mancante_viene_chiesto(registro, reale, orologio, fatto):
    assumi(registro, senza=(fatto,), regime=None if fatto == "regime_fine_servizio" else "3")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    assert fatto in {dato.fatto for dato in vista.mancanti}
    assert not vista.trasmissibile
    with pytest.raises(VistaFerma, match=fatto):
        in_xml([vista], ENTE, MITTENTE, mese=Mese(2026, 11), bozza=True)


def test_senza_regime_la_denuncia_si_calcola_e_la_vista_lo_chiede(registro, reale, orologio):
    assumi(registro, regime=None)
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    assert calcola_denuncia(registro, reale, R, Mese(2026, 11)).periodi
    mancante, = lista_pos_pa(registro, reale, R, Mese(2026, 11)).mancanti
    assert mancante.fatto == "regime_fine_servizio"


# --- TFS e TFR: GestPrevidenziale (ticket #33, parte 3) ---------------------------------------
# CodGestione 6 ex INADEL (Allegato tecnico 4.33.1, p. 245); elementi del DT 4.33, p. 183 e 191-193;
# retribuzioni TFR dalla Circ. INPS 185/2021 § 2.2.1. Importi ricalcolati in test_fine_servizio.py.


def test_con_il_tfs_la_lista_e_trasmissibile(registro, reale, orologio):
    assumi(registro, regime="3")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    quadro, = vista.quadri
    assert quadro.previdenziale.cod_gestione == "6"
    assert quadro.previdenziale.imponibile_tfs == Decimal("1615.70")
    assert quadro.previdenziale.contributo_tfs == Decimal("98.56")
    assert quadro.previdenziale.imponibile_tfr is None
    assert quadro.retrib_teorica_tfr is None
    assert quadro.retrib_valutabile_tfr is None
    assert vista.bozza == ()
    assert vista.trasmissibile
    xml = in_xml([vista], ENTE, MITTENTE, mese=Mese(2026, 11))
    assert "BOZZA" not in xml
    assert "<ImponibileTFS>1615,70</ImponibileTFS>" in xml
    assert "<ContributoTFS>98,56</ContributoTFS>" in xml


def test_con_il_tfr_gestione_e_retribuzioni_tfr(registro, reale, orologio):
    assumi(registro, regime="1")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    quadro, = vista.quadri
    assert quadro.pensionistica.imponibile == Decimal("2051.69")  # la riduzione TFR non entra
    assert quadro.previdenziale.cod_gestione == "6"
    assert quadro.previdenziale.imponibile_tfr == Decimal("1615.70")
    assert quadro.previdenziale.contributo_tfr == Decimal("98.56")
    assert quadro.previdenziale.imponibile_tfr_ulteriori is None
    assert quadro.previdenziale.imponibile_tfs is None
    assert quadro.retrib_teorica_tfr == Decimal("2019.63")
    assert quadro.retrib_valutabile_tfr == Decimal("2019.63")
    assert vista.trasmissibile


def test_tfr_nel_mese_parziale_la_teorica_e_intera(registro, reale, orologio):
    assumi(registro, "funzionari", dal=date(2026, 8, 24), regime="1")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25))
    e0, v1 = lista_pos_pa(registro, reale, R, Mese(2026, 9)).quadri
    assert e0.previdenziale.imponibile_tfr == Decimal("2225.74")
    assert e0.previdenziale.contributo_tfr == Decimal("135.77")
    assert e0.retrib_valutabile_tfr == Decimal("2782.18")
    assert e0.retrib_teorica_tfr == Decimal("2192.02")
    # Il V1 causale 5 solo giuridico porta la teorica, intera, senza gestioni né valutabile.
    assert (v1.tipo, v1.causale) == ("V1", "5")
    assert v1.previdenziale is None
    assert v1.retrib_teorica_tfr == Decimal("2192.02")
    assert v1.retrib_valutabile_tfr is None


def test_cambio_di_regime_nell_anno_ferma_la_vista(registro, reale, orologio):
    assumi(registro, regime=None)
    registro.registra_codice(R, "regime_fine_servizio", "3", date(2026, 1, 1), date(2026, 6, 30))
    registro.registra_codice(R, "regime_fine_servizio", "1", date(2026, 7, 1))
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    fermo, = vista.fermi
    assert "regime" in fermo.motivo
    assert not vista.trasmissibile


def test_nel_mese_di_cessazione_la_teorica_e_intera(registro, reale, orologio):
    """Cessato il 15/10 in TFR: valutabile per i giorni pagati, teorica sul mese intero."""
    assumi(registro, al=date(2026, 10, 15), regime="1")
    registro.registra_codice(R, "codice_cessazione", "1", date(2026, 10, 15), date(2026, 10, 15))
    ottobre = stipendi(registro, reale, Mese(2026, 10))
    paga(registro, orologio, ottobre, date(2026, 10, 27))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 10))
    quadro, = vista.quadri
    assert quadro.retrib_teorica_tfr == Decimal("2019.63")  # il tabellare intero, non i 15 giorni
    assert quadro.retrib_valutabile_tfr == Decimal("1009.82")


# --- V1 causale 5 solo giuridico ---------------------------------------------------------------


def test_assunzione_a_fine_agosto_pagata_a_settembre(registro, reale, orologio):
    assumi(registro, "funzionari", dal=date(2026, 8, 24))
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25))

    agosto = lista_pos_pa(registro, reale, R, Mese(2026, 8))
    assert agosto.quadri == ()

    settembre = lista_pos_pa(registro, reale, R, Mese(2026, 9))
    e0, v1 = settembre.quadri
    assert e0.tipo == "E0"
    assert e0.periodo == Periodo(date(2026, 9, 1), date(2026, 9, 30))
    assert e0.pensionistica.imponibile == Decimal("2828.29")
    assert e0.pensionistica.contributo == Decimal("923.44")
    assert e0.credito.contributo == Decimal("9.90")

    assert (v1.tipo, v1.causale) == ("V1", "5")
    assert v1.periodo == Periodo(date(2026, 8, 24), date(2026, 8, 31))
    assert v1.inquadramento.qualifica == "0FZEQF"
    assert v1.pensionistica is None
    assert v1.credito is None
    assert v1.enti_versanti == ()


def test_mese_in_servizio_non_ancora_pagato_resta_un_avviso(registro, reale, orologio):
    assumi(registro, dal=date(2026, 8, 24))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 8))
    assert vista.quadri == ()
    assert any("V1 causale 5" in avviso for avviso in vista.avvisi)


# --- Cessazione e V1 causale 1 -----------------------------------------------------------------


def cessato_a_meta_ottobre(registro, reale, orologio, codice_cessazione=True):
    """Servizio fino al 15/10; a ottobre si paga il tabellare, il comparto a novembre."""
    assumi(registro, al=date(2026, 10, 15))
    if codice_cessazione:
        registro.registra_codice(R, "codice_cessazione", "1", date(2026, 10, 15), date(2026, 10, 15))
    ottobre = stipendi(registro, reale, Mese(2026, 10))
    paga(registro, orologio, [r for r in ottobre if r.istituto.startswith("tabellare")], date(2026, 10, 27))
    paga(registro, orologio, [r for r in ottobre if r.istituto.startswith("comparto")], date(2026, 11, 20))


def test_l_e0_del_mese_di_cessazione_porta_il_codice(registro, reale, orologio):
    cessato_a_meta_ottobre(registro, reale, orologio)
    quadro, = lista_pos_pa(registro, reale, R, Mese(2026, 10)).quadri
    assert quadro.periodo == Periodo(date(2026, 10, 1), date(2026, 10, 15))
    assert quadro.codice_cessazione == "1"


def test_senza_codice_di_cessazione_la_vista_lo_chiede(registro, reale, orologio):
    cessato_a_meta_ottobre(registro, reale, orologio, codice_cessazione=False)
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 10))
    assert "codice_cessazione" in {dato.fatto for dato in vista.mancanti}


def test_arretrato_a_un_cessato_va_nel_v1_causale_1(registro, reale, orologio):
    cessato_a_meta_ottobre(registro, reale, orologio)
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    quadro, = vista.quadri
    assert (quadro.tipo, quadro.causale) == ("V1", "1")
    assert quadro.periodo == Periodo(date(2026, 10, 1), date(2026, 10, 15))
    assert quadro.inquadramento.qualifica == "0IR000"
    assert quadro.pensionistica.imponibile == Decimal("16.03")
    assert quadro.pensionistica.contributo == Decimal("5.23")
    assert quadro.credito.imponibile == Decimal("16.03")
    assert quadro.credito.contributo == Decimal("0.06")
    assert quadro.codice_cessazione is None
    terne = {(ev.tipo_contributo, ev.imponibile, ev.contributo, ev.anno_mese_erogazione, ev.aliquota) for ev in quadro.enti_versanti}
    assert terne == {
        ("1", Decimal("16.03"), Decimal("5.23"), Mese(2026, 11), "2"),
        ("9", Decimal("16.03"), Decimal("0.06"), Mese(2026, 11), "2"),
    }
    assert vista.fermi == ()


# --- Altre variazioni: la vista si ferma e indica il quadro -----------------------------------


def test_recupero_su_cessato_indica_il_v1_causale_7_codice_motivo_7(registro, reale, orologio):
    fatti = assumi(registro)
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 10)), date(2026, 10, 27))

    orologio.vai(11, 3)
    for tipo in ("tipo_impiego", "tipo_servizio", "contratto", "qualifica", "area", "regime_fine_servizio"):
        registro.annulla_fatto(fatti[tipo].id, "cessazione comunicata in ritardo")
        registro.registra_codice(R, tipo, fatti[tipo].valore, date(2026, 1, 1), date(2026, 10, 15))
    registro.registra_codice(R, "cessazione", "1", date(2026, 10, 16))  # dal giorno dopo l'ultimo di servizio
    recupero = [voce.importo() for voce in differenze(registro, reale, R, Mese(2026, 10), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 11, 20))

    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    assert vista.quadri == ()
    fermo, = vista.fermi
    assert fermo.quadro == "V1 causale 7, codice motivo 7"
    assert {riga.valore for riga in fermo.importi if riga.istituto == "base.cpdel"} == {Decimal("-1025.84")}
    assert not vista.trasmissibile
    with pytest.raises(VistaFerma, match="causale 7"):
        in_xml([vista], ENTE, MITTENTE, mese=Mese(2026, 11), bozza=True)


def test_recupero_da_sospeso_non_indica_piu_il_v1_causale_7(registro, reale, orologio):
    fatti = assumi(registro)
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 10)), date(2026, 10, 27))

    orologio.vai(11, 3)
    for tipo in ("tipo_impiego", "tipo_servizio", "contratto", "qualifica", "area", "regime_fine_servizio"):
        registro.annulla_fatto(fatti[tipo].id, "sospensione comunicata in ritardo")
        registro.registra_codice(R, tipo, fatti[tipo].valore, date(2026, 1, 1), date(2026, 10, 15))
    registro.registra_codice(R, "sospensione", "1", date(2026, 10, 16))
    recupero = [voce.importo() for voce in differenze(registro, reale, R, Mese(2026, 10), TipoEsito.PAGATO)]
    paga(registro, orologio, recupero, date(2026, 11, 20))

    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    assert vista.quadri == ()
    assert vista.fermi == ()


# --- Serializzazione e validazione --------------------------------------------------------------


def test_serializzazione_separata_dal_calcolo(registro, reale, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    xml = in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 11))], ENTE, MITTENTE, mese=Mese(2026, 11), bozza=True)
    assert "<AnnoMeseDenuncia>2026-11</AnnoMeseDenuncia>" in xml
    assert "<Imponibile>2051,69</Imponibile>" in xml
    assert "<Contributo>669,88</Contributo>" in xml
    assert "<Contrib1PerCento>" not in xml
    assert "<RegimeFineServizio>3</RegimeFineServizio>" in xml


def test_una_vista_di_un_altro_mese_rifiutata(registro, reale, orologio):
    assumi(registro)
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    with pytest.raises(VistaFerma, match="mese"):
        in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 11))], ENTE, MITTENTE, mese=Mese(2026, 10), bozza=True)


def test_xml_di_un_mese_intero_valido_per_lo_schema(registro, reale, orologio):
    assumi(registro, "operatori_esperti")
    mesi = (Mese(2026, 9), Mese(2026, 10), Mese(2026, 11))
    paga(registro, orologio, stipendi(registro, reale, *mesi), date(2026, 11, 27))
    documento = valida(in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 11))], ENTE, MITTENTE, mese=Mese(2026, 11), bozza=True))
    pensionistica = documento.find(".//E0_PeriodoNelMese/Gestioni/GestPensionistica")
    assert pensionistica.findtext("Contributo") == "1786,73"
    assert pensionistica.findtext("Contrib1PerCento") == "7,87"


def test_xml_con_v1_causale_5_valido_per_lo_schema(registro, reale, orologio):
    assumi(registro, "funzionari", dal=date(2026, 8, 24))
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25))
    documento = valida(in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 9))], ENTE, MITTENTE, mese=Mese(2026, 9), bozza=True))
    v1 = documento.find(".//V1_PeriodoPrecedente")
    assert v1.get("CausaleVariazione") == "5"
    assert v1.find("Gestioni") is None


def cessato_con_tabellare_a_novembre(registro, reale, orologio, regime):
    """Servizio fino al 15/10; a ottobre si paga il comparto, il tabellare a novembre."""
    assumi(registro, al=date(2026, 10, 15), regime=regime)
    registro.registra_codice(R, "codice_cessazione", "1", date(2026, 10, 15), date(2026, 10, 15))
    ottobre = stipendi(registro, reale, Mese(2026, 10))
    paga(registro, orologio, [r for r in ottobre if r.istituto.startswith("comparto")], date(2026, 10, 27))
    paga(registro, orologio, [r for r in ottobre if r.istituto.startswith("tabellare")], date(2026, 11, 20))


def test_arretrato_tfs_a_un_cessato_nella_terna_7(registro, reale, orologio):
    cessato_con_tabellare_a_novembre(registro, reale, orologio, "3")
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    quadro, = vista.quadri
    assert (quadro.tipo, quadro.causale) == ("V1", "1")
    assert quadro.previdenziale.imponibile_tfs == Decimal("807.86")
    assert quadro.previdenziale.contributo_tfs == Decimal("49.28")
    terne = {(ev.tipo_contributo, ev.imponibile, ev.contributo) for ev in quadro.enti_versanti}
    assert ("7", Decimal("807.86"), Decimal("49.28")) in terne
    assert vista.trasmissibile


def test_arretrato_tfr_a_un_cessato_nella_terna_8(registro, reale, orologio):
    cessato_con_tabellare_a_novembre(registro, reale, orologio, "1")
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    quadro, = vista.quadri
    assert quadro.previdenziale.imponibile_tfr == Decimal("807.86")
    assert quadro.retrib_valutabile_tfr == Decimal("1009.82")
    assert quadro.retrib_teorica_tfr == Decimal("2019.63")
    terne = {(ev.tipo_contributo, ev.imponibile, ev.contributo) for ev in quadro.enti_versanti}
    assert ("8", Decimal("807.86"), Decimal("49.28")) in terne
    documento = valida(in_xml([vista], ENTE, MITTENTE, mese=Mese(2026, 11)))
    v1 = documento.find(".//V1_PeriodoPrecedente")
    assert v1.findtext("Gestioni/GestPrevidenziale/ContributoTFR") == "49,28"
    assert v1.findtext("RetribValutabileTFR") == "1009,82"


def test_xml_con_tfs_valido_per_lo_schema(registro, reale, orologio):
    assumi(registro, regime="3")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    documento = valida(in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 11))], ENTE, MITTENTE, mese=Mese(2026, 11)))
    previdenziale = documento.find(".//E0_PeriodoNelMese/Gestioni/GestPrevidenziale")
    assert [figlio.tag for figlio in previdenziale] == ["CodGestione", "ImponibileTFS", "ContributoTFS"]


def test_xml_con_tfr_valido_per_lo_schema(registro, reale, orologio):
    assumi(registro, "funzionari", dal=date(2026, 8, 24), regime="1")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25))
    documento = valida(in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 9))], ENTE, MITTENTE, mese=Mese(2026, 9)))
    e0 = documento.find(".//E0_PeriodoNelMese")
    assert [f.tag for f in e0.find("Gestioni/GestPrevidenziale")] == ["CodGestione", "ImponibileTFR", "ContributoTFR"]
    assert e0.findtext("RetribTeoricaTabellareTFR") == "2192,02"
    assert e0.findtext("RetribValutabileTFR") == "2782,18"
    assert documento.findtext(".//V1_PeriodoPrecedente/RetribTeoricaTabellareTFR") == "2192,02"


ESEMPIO = Path(__file__).resolve().parent.parent / "docs" / "esempi" / "lista-pos-pa-2026-09.xml"


def test_l_esempio_in_docs_e_quello_prodotto_dalla_vista(registro, reale, orologio):
    """Assunto il 24/08 in regime TFR, pagato a settembre: E0 di settembre e V1 causale 5 di agosto."""
    assumi(registro, "funzionari", dal=date(2026, 8, 24), regime="1")
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 8), Mese(2026, 9)), date(2026, 9, 25))
    xml = in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 9))], ENTE, MITTENTE, mese=Mese(2026, 9))
    assert ESEMPIO.read_text(encoding="utf-8") == xml


def test_xml_con_v1_causale_1_valido_per_lo_schema(registro, reale, orologio):
    cessato_a_meta_ottobre(registro, reale, orologio)
    documento = valida(in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 11))], ENTE, MITTENTE, mese=Mese(2026, 11), bozza=True))
    v1 = documento.find(".//V1_PeriodoPrecedente")
    assert v1.get("CausaleVariazione") == "1"
    assert [ev.findtext("AnnoMeseErogazione") for ev in v1.findall("EnteVersante")] == ["2026-11", "2026-11"]


def test_xml_del_mese_di_cessazione_valido_per_lo_schema(registro, reale, orologio):
    cessato_a_meta_ottobre(registro, reale, orologio)
    documento = valida(in_xml([lista_pos_pa(registro, reale, R, Mese(2026, 10))], ENTE, MITTENTE, mese=Mese(2026, 10), bozza=True))
    assert documento.findtext(".//E0_PeriodoNelMese/CodiceCessazione") == "1"


# --- Correlazioni qualifica-contratto, Appendice G v15 ------------------------------------------


def correlazioni():
    percorso = os.environ.get("PAGHE_APPENDICE_G")
    if not percorso or not Path(percorso).is_file():
        pytest.skip("Appendice G v15 non disponibile (PAGHE_APPENDICE_G)")
    openpyxl = pytest.importorskip("openpyxl")
    foglio = openpyxl.load_workbook(percorso, read_only=True)["CorrelazioniQualificaContratto"]

    def data(valore):
        if isinstance(valore, datetime):
            return valore.date()
        try:
            return datetime.strptime(str(valore).strip(), "%d/%m/%Y").date()
        except ValueError:
            return None  # "-" e simili: nessuna data di fine

    return [
        (contratto, qualifica, data(inizio), data(fine))
        for contratto, _, qualifica, _, inizio, fine, *_ in foglio.iter_rows(min_row=2, values_only=True)
        if contratto
    ]


@pytest.mark.parametrize("area", sorted(CODICI_AREA))
def test_contratto_e_qualifica_correlati_nell_appendice_g(area):
    giorno = date(2026, 11, 1)
    assert any(
        contratto == "RALN" and qualifica == CODICI_AREA[area] and inizio <= giorno and (fine is None or giorno <= fine)
        for contratto, qualifica, inizio, fine in correlazioni()
    )


def test_un_fermo_con_ambito_vista_rende_ancora_la_lista_una_bozza(registro, orologio):
    """Il corpus reale non ne ha più, ma il meccanismo resta (ADR 0008): corpus reale più un fermo fittizio."""
    corpus = Corpus.da_toml(
        CORPUS.read_text(encoding="utf-8")
        + '\n[[fermo]]\nfatto = "tipo_servizio"\ncaso = "caso di prova"\nambito = "vista"\nriferimento = "fittizio:prova"\n'
    )
    assumi(registro, regime="3")
    paga(registro, orologio, stipendi(registro, corpus, Mese(2026, 11)), date(2026, 11, 27))
    vista = lista_pos_pa(registro, corpus, R, Mese(2026, 11))
    motivo, = vista.bozza
    assert "caso di prova" in motivo
    with pytest.raises(VistaFerma, match="bozza"):
        in_xml([vista], ENTE, MITTENTE, mese=Mese(2026, 11))
    assert "<!-- BOZZA NON TRASMISSIBILE" in in_xml([vista], ENTE, MITTENTE, mese=Mese(2026, 11), bozza=True)


# --- Cognome e nome sono fatti della persona (ticket #61, ADR 0012) -------------------------------


def test_cognome_e_nome_si_leggono_dalla_persona_del_rapporto(registro, reale, orologio):
    assumi(registro, senza=("cognome", "nome"))
    registro.registra_codice_persona("PERSONA-1", "cognome", "ROSSI", date(1980, 1, 1))
    registro.registra_codice_persona("PERSONA-1", "nome", "MARIO", date(1980, 1, 1))
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    assert (vista.lavoratore.cognome, vista.lavoratore.nome) == ("ROSSI", "MARIO")
    assert vista.mancanti == ()


def test_cognome_e_nome_scritti_sul_rapporto_non_si_leggono_piu(registro, reale, orologio):
    """Nessuna doppia via: sul rapporto non sono fatti del modello, e la vista li chiede alla persona."""
    assumi(registro, senza=("cognome", "nome"))
    registro.registra_codice(R, "cognome", "ROSSI", date(2026, 1, 1))
    registro.registra_codice(R, "nome", "MARIO", date(2026, 1, 1))
    paga(registro, orologio, stipendi(registro, reale, Mese(2026, 11)), date(2026, 11, 27))
    vista = lista_pos_pa(registro, reale, R, Mese(2026, 11))
    assert (vista.lavoratore.cognome, vista.lavoratore.nome) == (None, None)
    assert {"cognome", "nome"} <= {dato.fatto for dato in vista.mancanti}
    assert not vista.trasmissibile


ALTRI_FATTI = {
    "tipo_impiego": "1", "tipo_servizio": "4", "contratto": "RALN", "qualifica": "0IR000", "area": "istruttori",
    "regime_fine_servizio": "3", "comune_sede_lavoro": "H501", "cap_sede_lavoro": "00100",
}


def _senza_cumuli_per_persona():
    """Il corpus reale senza `[denuncia].persona`: due rapporti nello stesso anno non fermano la denuncia."""
    testo = CORPUS.read_text(encoding="utf-8").replace('persona = "codice_fiscale"' + chr(10), "", 1)
    return Corpus.da_toml(testo, reale=True)


def test_una_persona_con_due_rapporti_e_un_solo_nome_lo_porta_su_entrambe_le_viste(registro, orologio):
    """Con il corpus reale due rapporti in servizio nello stesso anno fermano la denuncia (cumuli per persona)."""
    corpus = _senza_cumuli_per_persona()
    assumi(registro)
    altro = "RAPPORTO-2"
    registro.collega_rapporto(altro, "PERSONA-1", date(2026, 1, 1))
    for tipo, valore in ALTRI_FATTI.items():
        registro.registra_codice(altro, tipo, valore, date(2026, 1, 1))
    registro.registra_fatto(altro, "mensile", "1500", date(2026, 11, 1), date(2026, 11, 30))
    paga(registro, orologio, stipendi(registro, corpus, Mese(2026, 11)), date(2026, 11, 27))
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 11, 27), calcola(registro, corpus, altro, Mese(2026, 11)))
    registro.registra_pagamento(altro, esito.id, date(2026, 11, 27))
    primo = lista_pos_pa(registro, corpus, R, Mese(2026, 11))
    secondo = lista_pos_pa(registro, corpus, altro, Mese(2026, 11))
    assert (primo.lavoratore.cognome, primo.lavoratore.nome) == ("ROSSI", "MARIO")
    assert (secondo.lavoratore.cognome, secondo.lavoratore.nome) == ("ROSSI", "MARIO")
    assert not [dato for dato in secondo.mancanti if dato.fatto in {"cognome", "nome", "codice_fiscale"}]


def _rapporto_scollegato(registro, reale, orologio, corpus):
    scollegato = "RAPPORTO-9"
    for tipo, valore in ALTRI_FATTI.items():
        registro.registra_codice(scollegato, tipo, valore, date(2026, 1, 1))
    registro.registra_fatto(scollegato, "mensile", "1500", date(2026, 11, 1), date(2026, 11, 30))
    righe = calcola(registro, corpus, scollegato, Mese(2026, 11))
    orologio.vai(11, 27, 2026)
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 11, 27), righe)
    registro.registra_pagamento(scollegato, esito.id, date(2026, 11, 27))
    return scollegato


def test_un_rapporto_senza_persona_collegata_ferma_la_denuncia_come_prima(registro, reale, orologio):
    """Con il corpus reale la denuncia chiede il legame per i cumuli per persona: la vista non nasce."""
    scollegato = _rapporto_scollegato(registro, reale, orologio, reale)
    with pytest.raises(ErrorePaghe, match="legame con la persona"):
        lista_pos_pa(registro, reale, scollegato, Mese(2026, 11))


def test_un_rapporto_senza_persona_collegata_chiede_codice_fiscale_cognome_e_nome(registro, orologio):
    """Senza i cumuli per persona la vista nasce, e i dati della persona sono dati mancanti, mai stimati."""
    testo = CORPUS.read_text(encoding="utf-8").replace('persona = "codice_fiscale"' + chr(10), "", 1)
    senza_cumuli = Corpus.da_toml(testo, reale=True)
    scollegato = _rapporto_scollegato(registro, senza_cumuli, orologio, senza_cumuli)
    vista = lista_pos_pa(registro, senza_cumuli, scollegato, Mese(2026, 11))
    assert (vista.lavoratore.codice_fiscale, vista.lavoratore.cognome, vista.lavoratore.nome) == (None, None, None)
    assert {"codice_fiscale", "cognome", "nome"} <= {dato.fatto for dato in vista.mancanti}
    assert not vista.trasmissibile
