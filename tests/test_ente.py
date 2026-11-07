"""L'ente come soggetto dei fatti (ADR 0025) e l'IBAN del beneficiario. Dati fittizi."""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Fatto
from paghe.errori import ErroreRegistro

IBAN = "IT00X0000000000000000000000"  # IBAN di prova, non valido
IBAN_NUOVO = "IT00Y0000000000000000000000"
CF_ENTE = "00000000000"  # codice fiscale di fantasia dell'ente
P = "PERSONA-1"


def test_un_fatto_categoriale_dell_ente_si_legge_a_una_data(registro, orologio):
    fatto = registro.registra_codice_ente("denominazione", "Ente di prova", date(2026, 1, 1))
    assert fatto.soggetto == "ente"
    assert registro.vigente_ente("denominazione", date(2026, 5, 1), orologio()) == fatto
    assert registro.vigente_ente("denominazione", date(2025, 12, 31), orologio()) is None


def test_i_tipi_categoriali_dell_ente(registro, orologio):
    for tipo, valore in [
        ("codice_fiscale", CF_ENTE),
        ("denominazione", "Ente di prova"),
        ("email", "paghe@ente.example"),
        ("iban_tesoreria", IBAN),
        ("sigla_provincia", "XX"),
    ]:
        registro.registra_codice_ente(tipo, valore, date(2026, 1, 1))
        assert registro.vigente_ente(tipo, date(2026, 1, 1), orologio()).valore == valore


def test_un_tipo_non_dichiarato_per_l_ente_e_rifiutato(registro):
    with pytest.raises(ErroreRegistro, match="tipo"):
        registro.registra_codice_ente("colore_preferito", "blu", date(2026, 1, 1))
    with pytest.raises(ErroreRegistro, match="tipo"):
        registro.registra_fatto_ente("denominazione", "1", date(2026, 1, 1))
    with pytest.raises(ErroreRegistro, match="tipo"):
        registro.registra_codice_ente("ultimo_pagamento_anno", "2026", date(2026, 1, 1))


def test_un_fatto_numerico_dell_ente_si_legge_come_numero(registro, orologio):
    registro.registra_fatto_ente("ultimo_pagamento_anno", 2026, date(2026, 12, 20), date(2026, 12, 20))
    fatto = registro.vigente_ente("ultimo_pagamento_anno", date(2026, 12, 20), orologio())
    assert fatto.valore == Decimal(2026)
    assert not fatto.categoriale


def test_un_fatto_dell_ente_non_e_letto_come_fatto_di_un_rapporto(registro, orologio):
    """L'identificativo interno dell'ente non si confonde con un rapporto che abbia lo stesso nome."""
    registro.registra_codice_ente("denominazione", "Ente di prova", date(2026, 1, 1))
    registro.registra_codice("ente", "denominazione", "di un rapporto", date(2026, 1, 1))
    ente = registro.fatti_ente_noti("denominazione", orologio())
    rapporto = registro.fatti_noti("ente", "denominazione", orologio())
    assert [f.valore for f in ente] == ["Ente di prova"]
    assert [f.valore for f in rapporto] == ["di un rapporto"]
    assert registro.rapporti_con_codice("denominazione", "Ente di prova", orologio()) == []


def test_un_fatto_dell_ente_non_e_letto_come_fatto_della_persona(registro, orologio):
    registro.registra_codice_ente("denominazione", "Ente di prova", date(2026, 1, 1))
    assert registro.fatti_persona_noti("ente", "denominazione", orologio()) == []


def test_una_correzione_dell_ente_e_un_nuovo_fatto_e_si_legge_a_un_istante(registro, orologio):
    errato = registro.registra_codice_ente("email", "sbagliata@ente.example", date(2026, 1, 1))
    prima = orologio()
    orologio.avanza(60)
    giusto = registro.registra_codice_ente("email", "giusta@ente.example", date(2026, 1, 1))
    assert registro.vigente_ente("email", date(2026, 5, 1), prima) == errato
    assert registro.vigente_ente("email", date(2026, 5, 1), orologio()) == giusto


def test_un_fatto_dell_ente_non_e_noto_prima_di_essere_registrato(registro, orologio):
    prima = orologio()
    orologio.avanza(60)
    registro.registra_codice_ente("sigla_provincia", "XX", date(2026, 1, 1))
    assert registro.fatti_ente_noti("sigla_provincia", prima) == []


def test_un_fatto_dell_ente_si_annulla_con_motivo(registro, orologio):
    fatto = registro.registra_codice_ente("sigla_provincia", "XX", date(2026, 1, 1))
    orologio.avanza(60)
    registro.annulla_fatto(fatto.id, "ente sbagliato")
    assert registro.fatti_ente_noti("sigla_provincia", orologio()) == []


def test_il_fatto_dell_ente_si_serializza_con_il_soggetto(registro):
    fatto = registro.registra_codice_ente("denominazione", "Ente di prova", date(2026, 1, 1))
    assert Fatto.da_dizionario(fatto.in_dizionario()) == fatto


def test_il_codice_dell_ente_vuole_un_valore(registro):
    with pytest.raises(ErroreRegistro):
        registro.registra_codice_ente("denominazione", " ", date(2026, 1, 1))


# Ultimo pagamento dell'anno: uno per anno d'imposta, con la data prevista

def test_l_ultimo_pagamento_e_uno_per_anno_d_imposta(registro, orologio):
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    registro.registra_ultimo_pagamento(2027, date(2027, 12, 17))
    assert registro.ultimo_pagamento_dell_anno(2026, orologio()) == date(2026, 12, 18)
    assert registro.ultimo_pagamento_dell_anno(2027, orologio()) == date(2027, 12, 17)
    assert registro.ultimo_pagamento_dell_anno(2028, orologio()) is None


def test_la_data_dell_ultimo_pagamento_si_corregge_con_un_nuovo_fatto(registro, orologio):
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    prima = orologio()
    orologio.avanza(60)
    registro.registra_ultimo_pagamento(2026, date(2027, 1, 8))
    assert registro.ultimo_pagamento_dell_anno(2026, prima) == date(2026, 12, 18)
    assert registro.ultimo_pagamento_dell_anno(2026, orologio()) == date(2027, 1, 8)


def test_l_ultimo_pagamento_annullato_non_conta(registro, orologio):
    fatto = registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    orologio.avanza(60)
    registro.annulla_fatto(fatto.id, "data errata")
    assert registro.ultimo_pagamento_dell_anno(2026, orologio()) is None


def test_l_ultimo_pagamento_cade_nell_anno_d_imposta_o_entro_il_12_gennaio_dopo(registro):
    registro.registra_ultimo_pagamento(2026, date(2027, 1, 12))
    with pytest.raises(ErroreRegistro, match="anno d'imposta"):
        registro.registra_ultimo_pagamento(2026, date(2027, 1, 13))
    with pytest.raises(ErroreRegistro, match="anno d'imposta"):
        registro.registra_ultimo_pagamento(2026, date(2025, 12, 31))


# IBAN del beneficiario: fatto datato della persona

def test_l_iban_e_un_fatto_datato_della_persona(registro, orologio):
    fatto = registro.registra_iban_persona(P, IBAN, date(2026, 1, 1))
    assert fatto.soggetto == "persona"
    assert registro.vigente_persona(P, "iban", date(2026, 5, 1), orologio()).valore == IBAN
    assert registro.vigente_persona(P, "iban", date(2025, 5, 1), orologio()) is None


def test_un_nuovo_iban_sostituisce_il_precedente_dalla_sua_data(registro, orologio):
    registro.registra_iban_persona(P, IBAN, date(2026, 1, 1), date(2026, 6, 30))
    registro.registra_iban_persona(P, IBAN_NUOVO, date(2026, 7, 1))
    assert registro.vigente_persona(P, "iban", date(2026, 6, 30), orologio()).valore == IBAN
    assert registro.vigente_persona(P, "iban", date(2026, 7, 1), orologio()).valore == IBAN_NUOVO


def test_l_iban_vuoto_e_rifiutato(registro):
    with pytest.raises(ErroreRegistro):
        registro.registra_iban_persona(P, "", date(2026, 1, 1))
