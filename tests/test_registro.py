import sqlite3
from datetime import date, datetime
from decimal import Decimal

import pytest

from paghe import Atto, Mese, Registro, TipoEsito, calcola, emetti_esito
from paghe.errori import ErroreRegistro, ValiditaNonUniforme

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
