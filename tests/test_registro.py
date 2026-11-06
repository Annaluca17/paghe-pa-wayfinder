import sqlite3
from datetime import date, datetime
from decimal import Decimal

import pytest

from paghe import Atto, Corpus, Fatto, Mese, Registro, TipoEsito, calcola, emetti_esito
from paghe.errori import ErroreCalcolo, ErroreRegistro, ValiditaNonUniforme

R = "RAPPORTO-1"
FEB = Mese(2026, 2)


def test_immutabilita_imposta_dal_database(registro, corpus, orologio):
    fatto = registro.registra_fatto(R, "compenso_mensile", "1000", date(2026, 1, 1))
    registro.annulla_fatto(fatto.id, "prova")
    registro.registra_fatto(R, "compenso_mensile", "1000", date(2026, 1, 1))
    emetti_esito(registro, TipoEsito.PAGATO, date(2026, 1, 27), calcola(registro, corpus, R, FEB))
    for istruzione in (
        "UPDATE fatti SET valore = '1'",
        "DELETE FROM fatti",
        "UPDATE annullamenti SET motivo = 'x'",
        "DELETE FROM annullamenti",
        "UPDATE esiti SET righe = '[]'",
        "DELETE FROM esiti",
    ):
        with pytest.raises(sqlite3.IntegrityError, match="immutabile"):
            registro._db.execute(istruzione)


def test_fatto_conserva_atto_e_assi_temporali(registro, orologio):
    orologio.vai(3, 15)
    atto = Atto("fittizio:determina-1", date(2026, 3, 10))
    registrato = registro.registra_fatto(R, "compenso_mensile", "1100", date(2026, 2, 1), atto=atto)
    letto = registro.fatti_noti(R, "compenso_mensile", orologio.ora)[0]
    assert letto == registrato
    assert (letto.atto.data, letto.valido_dal, letto.registrato_il) == (date(2026, 3, 10), date(2026, 2, 1), orologio.ora)


@pytest.mark.parametrize("valore", [0.1, True, "abc", "NaN", "Infinity", None])
def test_valore_non_ammesso(registro, valore):
    with pytest.raises(ErroreRegistro):
        registro.registra_fatto(R, "x", valore, date(2026, 1, 1))


def test_validita_invertita_e_campi_obbligatori(registro):
    with pytest.raises(ErroreRegistro):
        registro.registra_fatto(R, "x", "1", date(2026, 2, 1), date(2026, 1, 1))
    with pytest.raises(ErroreRegistro):
        registro.registra_fatto("", "x", "1", date(2026, 2, 1))


def test_orologio_senza_fuso_o_all_indietro(orologio):
    with pytest.raises(ValueError):
        Registro(orologio=lambda: datetime(2026, 1, 1)).registra_fatto(R, "x", "1", date(2026, 1, 1))

    registro = Registro(orologio=orologio)
    orologio.vai(3, 1)
    registro.registra_fatto(R, "x", "1", date(2026, 1, 1))
    orologio.vai(2, 1)
    with pytest.raises(ErroreRegistro, match="indietro"):
        registro.registra_fatto(R, "x", "2", date(2026, 1, 1))


def test_ultimo_registrato_prevale_giorno_per_giorno(registro, orologio):
    registro.registra_fatto(R, "x", "100", date(2026, 1, 1))
    primo_istante = orologio.ora
    orologio.vai(3, 15)
    registro.registra_fatto(R, "x", "110", date(2026, 2, 1))

    assert registro.fatto_nel_mese(R, "x", Mese(2026, 1), orologio.ora).valore == 100
    assert registro.fatto_nel_mese(R, "x", FEB, orologio.ora).valore == 110
    assert registro.fatto_nel_mese(R, "x", FEB, primo_istante).valore == 100


def test_correzione_di_un_periodo_chiuso_non_estende_oltre(registro, orologio):
    registro.registra_fatto(R, "x", "100", date(2026, 1, 1))
    orologio.avanza()
    registro.registra_fatto(R, "x", "90", date(2026, 2, 1), date(2026, 2, 28))
    assert registro.fatto_nel_mese(R, "x", FEB, orologio.ora).valore == 90
    assert registro.fatto_nel_mese(R, "x", Mese(2026, 3), orologio.ora).valore == 100


@pytest.mark.parametrize(
    ("dal", "al"),
    [(date(2026, 2, 15), None), (date(2026, 1, 1), date(2026, 2, 10))],
)
def test_variazione_o_copertura_parziale_nel_mese_non_viene_stimata(registro, dal, al):
    registro.registra_fatto(R, "x", "100", dal, al)
    with pytest.raises(ValiditaNonUniforme):
        registro.fatto_nel_mese(R, "x", FEB, registro.adesso())


def test_annullamento_vale_dalla_sua_registrazione(registro, orologio):
    fatto = registro.registra_fatto(R, "x", "100", date(2026, 1, 1))
    prima = orologio.ora
    orologio.vai(2, 1)
    registro.annulla_fatto(fatto.id, "inserito per errore")

    assert registro.fatto_nel_mese(R, "x", FEB, orologio.ora) is None
    assert registro.fatto_nel_mese(R, "x", FEB, prima).valore == 100


def test_annullamento_non_valido(registro):
    fatto = registro.registra_fatto(R, "x", "100", date(2026, 1, 1))
    with pytest.raises(ErroreRegistro):
        registro.annulla_fatto(fatto.id, " ")
    with pytest.raises(ErroreRegistro):
        registro.annulla_fatto(999, "inesistente")
    registro.annulla_fatto(fatto.id, "prima volta")
    with pytest.raises(ErroreRegistro):
        registro.annulla_fatto(fatto.id, "seconda volta")


def test_il_registro_sopravvive_alla_chiusura(tmp_path, orologio, corpus):
    percorso = str(tmp_path / "registro.sqlite")
    registro = Registro(percorso, orologio)
    fatto = registro.registra_fatto(R, "compenso_mensile", "1000.50", date(2026, 1, 1))
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), calcola(registro, corpus, R, FEB))
    registro.chiudi()

    riaperto = Registro(percorso, orologio)
    assert riaperto.fatti_noti(R, "compenso_mensile", orologio.ora) == [fatto]
    assert riaperto.esito(esito.id) == esito
    assert riaperto.esito(esito.id).righe[0].valore == Decimal("1000.50")
    orologio.vai(1, 1, anno=2025)
    with pytest.raises(ErroreRegistro, match="indietro"):
        riaperto.registra_fatto(R, "x", "1", date(2026, 1, 1))
    riaperto.chiudi()


# Fatti categoriali e data di pagamento


def test_codice_resta_testo_e_si_rilegge_uguale(registro, orologio):
    fatto = registro.registra_codice(R, "qualifica", "0IR000", date(2026, 1, 1))
    zero = registro.registra_codice(R, "tipo_servizio", "01", date(2026, 1, 1))
    assert fatto.valore == "0IR000"
    assert fatto.categoriale
    assert registro.fatti_noti(R, "tipo_servizio", orologio.ora) == [zero]
    assert registro.fatti_noti(R, "tipo_servizio", orologio.ora)[0].valore == "01"
    assert Fatto.da_dizionario(fatto.in_dizionario()) == fatto


def test_fatto_numerico_non_e_categoriale(registro):
    fatto = registro.registra_fatto(R, "mensile", "1000", date(2026, 1, 1))
    assert not fatto.categoriale
    assert fatto.valore == Decimal(1000)


@pytest.mark.parametrize("codice", ["", "  ", None, 12])
def test_codice_non_valido_rifiutato(registro, codice):
    with pytest.raises(ErroreRegistro, match="odice"):
        registro.registra_codice(R, "qualifica", codice, date(2026, 1, 1))


def test_una_formula_non_legge_un_codice(registro):
    corpus = Corpus.da_toml(
        """
[[regola]]
istituto = "a"
versione = 1
dal = 2026-01-01
riferimento = "fittizio:a"
formula = "fatto.qualifica"
maturazione = "evento"
"""
    )
    registro.registra_codice(R, "qualifica", "0IR000", date(2026, 1, 1))
    with pytest.raises(ErroreCalcolo, match="qualifica"):
        calcola(registro, corpus, R, FEB)


def test_registro_esistente_senza_colonna_dei_codici_si_aggiorna(tmp_path):
    percorso = tmp_path / "vecchio.sqlite"
    db = sqlite3.connect(percorso)
    db.executescript(
        """
        CREATE TABLE fatti (
            id INTEGER PRIMARY KEY AUTOINCREMENT, rapporto TEXT NOT NULL, tipo TEXT NOT NULL,
            valore TEXT NOT NULL, valido_dal TEXT NOT NULL, valido_al TEXT, registrato_il TEXT NOT NULL,
            atto_riferimento TEXT, atto_data TEXT
        );
        INSERT INTO fatti (rapporto, tipo, valore, valido_dal, registrato_il)
        VALUES ('RAPPORTO-1', 'mensile', '1000', '2026-01-01', '2026-01-01T09:00:00.000000+00:00');
        """
    )
    db.close()
    registro = Registro(str(percorso))
    assert registro.fatti_noti(R, "mensile", registro.adesso())[0].valore == Decimal(1000)
    assert registro.registra_codice(R, "qualifica", "0IR000", date(2026, 1, 1)).valore == "0IR000"
    registro.chiudi()


def test_data_di_pagamento_solo_su_esito_pagato_che_contiene_il_rapporto(registro, corpus, orologio):
    registro.registra_fatto(R, "compenso_mensile", "1000", date(2026, 1, 1))
    righe = calcola(registro, corpus, R, FEB)
    pagato = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), righe)
    dichiarato = emetti_esito(registro, TipoEsito.DICHIARATO, date(2026, 3, 16), righe)

    with pytest.raises(ErroreRegistro, match="inesistente"):
        registro.registra_pagamento(R, 999, date(2026, 2, 27))
    with pytest.raises(ErroreRegistro, match="pagato"):
        registro.registra_pagamento(R, dichiarato.id, date(2026, 2, 27))
    with pytest.raises(ErroreRegistro, match="ALTRO"):
        registro.registra_pagamento("ALTRO", pagato.id, date(2026, 2, 27))

    fatto = registro.registra_pagamento(R, pagato.id, date(2026, 2, 27))
    assert fatto.tipo == "data_pagamento"
    assert registro.pagamenti(R, registro.adesso()) == {pagato.id: fatto}


def test_l_ultima_data_registrata_prevale_e_quella_precedente_resta_leggibile(registro, corpus, orologio):
    registro.registra_fatto(R, "compenso_mensile", "1000", date(2026, 1, 1))
    pagato = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), calcola(registro, corpus, R, FEB))
    prima = registro.registra_pagamento(R, pagato.id, date(2026, 2, 27))
    istante = orologio.ora
    orologio.avanza()
    dopo = registro.registra_pagamento(R, pagato.id, date(2026, 3, 1))
    assert registro.pagamenti(R, orologio.ora)[pagato.id] == dopo
    assert registro.pagamenti(R, istante)[pagato.id] == prima
