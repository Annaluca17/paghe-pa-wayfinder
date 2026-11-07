"""Serializzatore del file telematico F24EP sull'Allegato 2 AdE (dicembre 2016). Dati fittizi.

Le posizioni attese sono lette sulle tabelle dell'Allegato 2 e scritte qui come numeri, non ricavate dal
codice. I controlli del validatore di F24EP-editor sono replicati in `controlli_f24ep.py`.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from paghe.errori import VistaFerma
from paghe.f24ep import FornituraF24EP, ModelloF24EP, ModuloF24EP, RigaF24EP, serializza

from controlli_f24ep import controlla, righe_del_record

CF_ENTE = "00000000000"  # codice fiscale di fantasia, cifra di controllo valida
IBAN = "IT76X0100003245TEST00000001"  # IBAN di prova: ABI e CAB di Banca d'Italia, conto evidentemente finto
D = Decimal


def riga_100e(debito="100.00"):
    return RigaF24EP("F", "100E", rif_a="0003", rif_b="2026", debito=D(debito))


RIGA_P201 = RigaF24EP("Q", "P201", codice="RM", rif_a="032026", rif_b="032026", debito=D("480.00"))
RIGA_170E = RigaF24EP("F", "170E", rif_a="0003", rif_b="2026", credito=D("150.00"))


def modello(*moduli, **modifiche):
    dati = dict(
        cf_ente=CF_ENTE,
        denominazione="ENTE DI PROVA",
        email="paghe@ente.example",
        iban=IBAN,
        data_versamento=date(2026, 4, 16),
        moduli=moduli or (ModuloF24EP((riga_100e(), RIGA_P201, RIGA_170E)),),
    )
    dati.update(modifiche)
    return ModelloF24EP(**dati)


def file(*modelli):
    return serializza(FornituraF24EP(modelli or (modello(),)))


def record(grezzo):
    return [r.decode("latin-1") for r in grezzo.split(b"\r\n") if r]


# Struttura e controlli bloccanti

def test_il_file_e_una_sequenza_di_record_a_lunghezza_fissa_con_crlf():
    grezzo = file()
    assert len(grezzo) == 4 * 1900 and grezzo.endswith(b"\r\n")
    assert "".join(r[0] for r in record(grezzo)) == "AMVZ"
    assert all(len(r) == 1898 and r[1897] == "A" for r in record(grezzo))


def test_il_file_supera_i_controlli_bloccanti_del_validatore():
    errori, divergenze = controlla(file())
    assert errori == [] and divergenze == []


def test_piu_moduli_e_piu_modelli_superano_i_controlli():
    due_moduli = modello(ModuloF24EP((riga_100e(), RIGA_P201)), ModuloF24EP((riga_100e("50.00"),)))
    altro = modello(ModuloF24EP((riga_100e("10.00"),)), data_versamento=date(2026, 4, 17))
    grezzo = file(due_moduli, altro)
    assert "".join(r[0] for r in record(grezzo)) == "AMVVMVZ"
    assert controlla(grezzo) == ([], [])


# Posizioni, una per una, dall'Allegato 2

def test_record_a():
    a = record(file())[0]
    assert a[0] == "A" and a[1:15] == " " * 14
    assert a[15:20] == "F24EP" and a[20:22] == "14"
    assert a[22:38] == CF_ENTE.ljust(16)
    assert a[215:275] == "ENTE DI PROVA".ljust(60)
    assert a[439] == " " and a[521:524] == "001" and a[524:527] == "001"
    assert a[527:627] == " " * 100 and a[627] == "1" and a[628:1897] == " " * 1269


def test_record_m():
    m = record(file())[1]
    assert m[0] == "M" and m[1:12] == CF_ENTE and m[12:17] == " " * 5
    assert m[17:25] == "00000001" and m[25:28] == "   " and m[89] == " " and m[90] == "E"
    assert m[517:572] == "ENTE DI PROVA".ljust(55)
    assert m[572:574] == "  " and m[574:590] == " " * 16
    assert m[1767:1769] == "14" and m[1769:1780] == CF_ENTE and m[1780:1782] == "IT"
    assert m[1782:1784] == "76" and m[1784] == "X" and m[1785:1790] == "01000" and m[1790:1795] == "03245"
    assert m[1795:1807] == "TEST00000001" and m[1807] == " "
    assert m[1808:1868] == "paghe@ente.example".ljust(60)
    assert m[1868:1872] == "EURO" and m[1872:1887] == "430,00".ljust(15) and m[1887:1897] == "16-04-2026"


def test_record_v_testata_e_righe():
    v = record(file())[2]
    assert v[0] == "V" and v[1:12] == CF_ENTE and v[17:25] == "00000001" and v[89] == "D"
    assert v[90:93] == "   " and v[93:104] == "0" * 11 and v[104:122] == " " * 18
    prima, seconda, terza = (v[122 + k * 71 : 122 + (k + 1) * 71] for k in range(3))
    assert prima == "F" + "100E".ljust(6) + " " * 5 + " " * 17 + "0003".ljust(6) + "2026".ljust(6) + "000000000010000" + "0" * 15
    assert seconda == "Q" + "P201".ljust(6) + "RM".ljust(5) + " " * 17 + "032026" + "032026" + "000000000048000" + "0" * 15
    assert terza == "F" + "170E".ljust(6) + " " * 5 + " " * 17 + "0003".ljust(6) + "2026".ljust(6) + "0" * 15 + "000000000015000"


def test_le_righe_non_usate_sono_vuote():
    v = record(file())[2]
    vuota = v[122 + 3 * 71 : 122 + 4 * 71]
    assert vuota == " " * 41 + "0" * 30
    assert len(righe_del_record(v)) == 22 and v[1684:1742] == " " * 58


def test_record_v_riepilogo():
    v = record(file())[2]
    assert v[1742:1757] == "000000000058000" and v[1757:1772] == "000000000015000"
    assert v[1772] == "P" and v[1773:1788] == "000000000043000" and v[1788:1792] == "    "
    assert v[1792:1807] == "000000000043000" and v[1807:1815] == "16042026" and v[1815:1897] == " " * 82


def test_record_z():
    z = record(file())[3]
    assert z[0] == "Z" and z[1:15] == " " * 14 and z[15:24] == "000000001" and z[24:33] == "000000001"
    assert z[33:1897] == " " * 1864


def test_i_progressivi_dei_modelli_crescono_e_legano_m_a_v():
    altro = modello(ModuloF24EP((riga_100e("10.00"),)))
    r = record(file(modello(), altro))
    assert [x[17:25] for x in r if x[0] in "MV"] == ["00000001", "00000001", "00000002", "00000002"]


def test_il_saldo_totale_a_debito_ha_i_separatori_delle_migliaia():
    grande = modello(ModuloF24EP((riga_100e("1234567.89"),)))
    assert record(file(grande))[1][1872:1887] == "1.234.567,89".ljust(15)


def test_il_saldo_che_supera_15_caratteri_omette_i_separatori_delle_migliaia():
    enorme = modello(ModuloF24EP((riga_100e("999999999999.99"),)))
    m = record(file(enorme))[1]
    assert m[1872:1887] == "999999999999,99"
    assert controlla(file(enorme)) == ([], [])


def test_un_saldo_zero_si_scrive_0_00():
    pari = modello(ModuloF24EP((riga_100e("100.00"), RigaF24EP("F", "170E", rif_a="0003", rif_b="2026", credito=D("100.00")))))
    assert record(file(pari))[1][1872:1887] == "0,00".ljust(15)
    assert controlla(file(pari)) == ([], [])


# Sezioni e formati dei campi: dalla tabella «Specifiche di compilazione del record V» e dalla tabella dei codici

def test_il_codice_regione_e_il_codice_catastale_vanno_nel_campo_codice():
    righe = (
        RigaF24EP("R", "380E", codice="08", rif_a="0003", rif_b="2026", debito=D("10.00")),
        RigaF24EP("S", "384E", codice="H501", rif_a="0003", rif_b="2026", debito=D("20.00")),
    )
    v = record(file(modello(ModuloF24EP(righe))))[2]
    assert v[122:193].startswith("R" + "380E".ljust(6) + "08".ljust(5))
    assert v[193:264].startswith("S" + "384E".ljust(6) + "H501".ljust(5))
    assert controlla(file(modello(ModuloF24EP(righe)))) == ([], [])


def errato(**campi_riga):
    base = riga_100e()
    return modello(ModuloF24EP((replace(base, **campi_riga),)))


@pytest.mark.parametrize(
    "campi, motivo",
    [
        (dict(sezione="I"), "sezione"),  # INPS: causali e matricola non modellate
        (dict(sezione="N"), "sezione"),  # INAIL: fuori dal ticket
        (dict(sezione="X"), "sezione"),
        (dict(codice="RM"), "codice"),  # sezione Erario: campo non valorizzabile
        (dict(estremi="123"), "estremi"),  # sezione Erario: campo non valorizzabile
        (dict(tributo=""), "codice tributo"),
        (dict(tributo="TROPPOLUNGO"), "codice tributo"),
        (dict(rif_a="0003 xx"), "riferimento"),
        (dict(debito=D("-1.00")), "importo"),
        (dict(debito=D("1.005")), "importo"),
        (dict(debito=D("0"), credito=D("0")), "né debito né credito"),
        (dict(credito=D("5.00")), "debito e credito"),
        (dict(debito=D("10000000000000.00")), "importo"),
        (dict(tributo="1ÈE"), "ASCII"),
    ],
)
def test_una_riga_fuori_specifica_ferma_il_file(campi, motivo):
    with pytest.raises(VistaFerma, match=motivo):
        file(errato(**campi))


def test_la_sezione_regioni_vuole_un_codice_regione_di_due_cifre():
    with pytest.raises(VistaFerma, match="codice"):
        file(modello(ModuloF24EP((RigaF24EP("R", "380E", codice="RM", rif_a="0003", rif_b="2026", debito=D("1.00")),))))


def test_la_sezione_enti_locali_vuole_un_codice_catastale():
    with pytest.raises(VistaFerma, match="codice"):
        file(modello(ModuloF24EP((RigaF24EP("S", "384E", codice="roma", rif_a="0003", rif_b="2026", debito=D("1.00")),))))


def test_la_sezione_inpdap_vuole_una_sigla_di_provincia():
    with pytest.raises(VistaFerma, match="codice"):
        file(modello(ModuloF24EP((replace(RIGA_P201, codice="12"),))))


# Saldo, dimensioni, dati dell'ente

def test_il_saldo_di_un_modulo_non_puo_essere_negativo():
    negativo = modello(ModuloF24EP((riga_100e("10.00"), RIGA_170E)))
    with pytest.raises(VistaFerma, match="saldo negativo"):
        file(negativo)


def test_il_saldo_e_per_modulo_non_per_modello():
    a_pezzi = modello(ModuloF24EP((riga_100e("500.00"),)), ModuloF24EP((RIGA_170E,)))
    with pytest.raises(VistaFerma, match="saldo negativo"):
        file(a_pezzi)


def test_un_modulo_ha_al_massimo_22_righe_e_almeno_una():
    ventidue = tuple(riga_100e() for _ in range(22))
    assert controlla(file(modello(ModuloF24EP(ventidue)))) == ([], [])
    with pytest.raises(VistaFerma, match="22"):
        file(modello(ModuloF24EP(ventidue + (riga_100e(),))))
    with pytest.raises(VistaFerma, match="almeno una"):
        file(modello(ModuloF24EP(())))


def test_un_modello_ha_almeno_un_modulo_e_una_fornitura_almeno_un_modello():
    with pytest.raises(VistaFerma, match="almeno un"):
        file(modello(moduli=()))
    with pytest.raises(VistaFerma, match="almeno un"):
        serializza(FornituraF24EP(()))


@pytest.mark.parametrize(
    "campi, motivo",
    [
        (dict(cf_ente="0000000001"), "codice fiscale"),  # 10 cifre
        (dict(cf_ente="00000000001"), "codice fiscale"),  # cifra di controllo errata
        (dict(cf_ente="RSSMRA80A01H501U"), "codice fiscale"),  # persona fisica: non è un ente
        (dict(denominazione=""), "denominazione"),
        (dict(denominazione="X" * 56), "denominazione"),
        (dict(denominazione="ENTE DI PROVA È"), "ASCII"),
        (dict(email=""), "e-mail"),
        (dict(email="senza-chiocciola"), "e-mail"),
        (dict(email="a@b.example" + "x" * 60), "e-mail"),
        (dict(iban=""), "IBAN"),
        (dict(iban="IT76X0100003245TEST0000000"), "IBAN"),  # 26 caratteri
        (dict(iban="DE76X0100003245TEST00000001"), "IBAN"),
        (dict(iban="IT77X0100003245TEST00000001"), "IBAN"),  # cifre di controllo errate
        (dict(iban="IT22X0200003245TEST00000001"), "ABI"),  # ABI diverso da Banca d'Italia
        (dict(iban="IT21X0100003246TEST00000001"), "CAB"),
        (dict(iban="IT76x0100003245TEST00000001"), "IBAN"),  # CIN minuscolo
    ],
)
def test_un_dato_dell_ente_fuori_specifica_ferma_il_file(campi, motivo):
    with pytest.raises(VistaFerma, match=motivo):
        file(modello(**campi))


def test_il_campo_utente_e_facoltativo_e_resta_nei_cento_caratteri():
    con = serializza(FornituraF24EP((modello(),), campo_utente="PROVA"))
    assert record(con)[0][527:627] == "PROVA".ljust(100)
    with pytest.raises(VistaFerma, match="utente"):
        serializza(FornituraF24EP((modello(),), campo_utente="X" * 101))


def test_i_modelli_di_enti_diversi_non_stanno_nella_stessa_fornitura():
    with pytest.raises(VistaFerma, match="stesso ente"):
        file(modello(), modello(cf_ente="00000000018"))
