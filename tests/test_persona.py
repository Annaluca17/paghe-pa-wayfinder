"""La persona come soggetto dei fatti, con il codice fiscale (ADR 0012, conseguenze). Dati fittizi."""

from datetime import date

import pytest

from paghe import Fatto
from paghe.errori import ErroreRegistro

CF = "RSSMRA80A01H501U"
P = "PERSONA-1"
R = "RAPPORTO-1"
ALTRO = "RAPPORTO-2"


def test_il_codice_fiscale_e_un_fatto_della_persona(registro, orologio):
    fatto = registro.registra_codice_persona(P, "codice_fiscale", CF, date(1980, 1, 1))
    assert fatto.soggetto == "persona"
    assert registro.vigente_persona(P, "codice_fiscale", date(2026, 5, 1), orologio()) == fatto


def test_un_fatto_della_persona_non_e_un_fatto_del_rapporto(registro, orologio):
    """Lo stesso identificativo può esistere come persona e come rapporto senza confondersi."""
    registro.registra_codice_persona("X", "codice_fiscale", CF, date(1980, 1, 1))
    registro.registra_codice("X", "area", "bassa", date(2026, 1, 1))
    assert [f.tipo for f in registro.fatti_noti("X", "codice_fiscale", orologio())] == []
    assert [f.tipo for f in registro.fatti_persona_noti("X", "area", orologio())] == []
    assert [f.tipo for f in registro.fatti_noti("X", "area", orologio())] == ["area"]


def test_la_persona_ha_piu_rapporti(registro, orologio):
    registro.collega_rapporto(R, P, date(2026, 1, 1))
    registro.collega_rapporto(ALTRO, P, date(2026, 3, 1))
    registro.collega_rapporto("RAPPORTO-3", "PERSONA-2", date(2026, 1, 1))
    assert registro.persona_del_rapporto(R, orologio()) == P
    assert registro.rapporti_della_persona(P, orologio()) == [R, ALTRO]


def test_un_rapporto_senza_persona_non_ha_persona(registro, orologio):
    assert registro.persona_del_rapporto(R, orologio()) is None


def test_la_persona_del_rapporto_si_conosce_alla_data_di_registrazione(registro, orologio):
    primo = orologio()
    orologio.avanza(60)
    registro.collega_rapporto(R, P, date(2026, 1, 1))
    assert registro.persona_del_rapporto(R, primo) is None
    assert registro.persona_del_rapporto(R, orologio()) == P


def test_una_correzione_del_codice_fiscale_e_un_nuovo_fatto(registro, orologio):
    errato = registro.registra_codice_persona(P, "codice_fiscale", "RSSMRA80A01H501X", date(1980, 1, 1))
    prima = orologio()
    orologio.avanza(60)
    giusto = registro.registra_codice_persona(P, "codice_fiscale", CF, date(1980, 1, 1))
    assert registro.vigente_persona(P, "codice_fiscale", date(2026, 5, 1), prima) == errato
    assert registro.vigente_persona(P, "codice_fiscale", date(2026, 5, 1), orologio()) == giusto


def test_un_fatto_della_persona_si_annulla_con_motivo(registro, orologio):
    fatto = registro.registra_codice_persona(P, "codice_fiscale", CF, date(1980, 1, 1))
    orologio.avanza(60)
    registro.annulla_fatto(fatto.id, "persona sbagliata")
    assert registro.fatti_persona_noti(P, "codice_fiscale", orologio()) == []


def test_il_fatto_della_persona_si_serializza_con_il_soggetto(registro):
    fatto = registro.registra_codice_persona(P, "codice_fiscale", CF, date(1980, 1, 1))
    assert Fatto.da_dizionario(fatto.in_dizionario()) == fatto


def test_un_fatto_di_un_rapporto_resta_del_rapporto(registro):
    fatto = registro.registra_fatto(R, "mensile", "1000", date(2026, 1, 1))
    assert fatto.soggetto == "rapporto"
    assert Fatto.da_dizionario(fatto.in_dizionario()) == fatto


def test_un_registro_precedente_alle_persone_riceve_la_colonna(tmp_path):
    from paghe import Registro
    import sqlite3

    percorso = str(tmp_path / "vecchio.db")
    db = sqlite3.connect(percorso)
    db.executescript(
        """
        CREATE TABLE fatti (id INTEGER PRIMARY KEY AUTOINCREMENT, rapporto TEXT NOT NULL, tipo TEXT NOT NULL,
            valore TEXT NOT NULL, valido_dal TEXT NOT NULL, valido_al TEXT, registrato_il TEXT NOT NULL,
            atto_riferimento TEXT, atto_data TEXT, categoriale INTEGER NOT NULL DEFAULT 0);
        INSERT INTO fatti (rapporto, tipo, valore, valido_dal, registrato_il)
            VALUES ('R', 'mensile', '100', '2026-01-01', '2026-01-01T09:00:00.000000+00:00');
        """
    )
    db.commit()
    db.close()
    registro = Registro(percorso)
    try:
        noti = registro.fatti_noti("R", "mensile", registro.adesso())
        assert [f.soggetto for f in noti] == ["rapporto"]
    finally:
        registro.chiudi()


def test_il_legame_con_la_persona_vuole_un_identificativo(registro):
    with pytest.raises(ErroreRegistro):
        registro.collega_rapporto(R, "", date(2026, 1, 1))
