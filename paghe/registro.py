"""Registro append-only di fatti ed esiti, su SQLite.

L'immutabilità è imposta anche dal database: i trigger rifiutano UPDATE e DELETE.
Il tempo di registrazione viene dall'orologio del registro, mai dal chiamante.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, Iterable

from .errori import ErroreRegistro, ValiditaNonUniforme
from .modello import Atto, Esito, Fatto, Importo, TipoEsito
from .riferimento import data_atto, motivo_rifiuto
from .tempo import Mese, Periodo, in_utc, istante_in_testo

SCHEMA = """
CREATE TABLE IF NOT EXISTS fatti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rapporto TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valore TEXT NOT NULL,
    valido_dal TEXT NOT NULL,
    valido_al TEXT,
    registrato_il TEXT NOT NULL,
    atto_riferimento TEXT,
    atto_data TEXT,
    categoriale INTEGER NOT NULL DEFAULT 0,
    CHECK ((atto_riferimento IS NULL) = (atto_data IS NULL))
);
CREATE INDEX IF NOT EXISTS fatti_per_rapporto ON fatti (rapporto, tipo);

CREATE TABLE IF NOT EXISTS annullamenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fatto_id INTEGER NOT NULL UNIQUE REFERENCES fatti (id),
    motivo TEXT NOT NULL,
    registrato_il TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS esiti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    data TEXT NOT NULL,
    registrato_il TEXT NOT NULL,
    righe TEXT NOT NULL
);
"""

TABELLE = ("fatti", "annullamenti", "esiti")
TIPO_DATA_PAGAMENTO = "data_pagamento"


def _trigger_immutabilita(tabella: str) -> str:
    return f"""
    CREATE TRIGGER IF NOT EXISTS {tabella}_no_update BEFORE UPDATE ON {tabella}
    BEGIN SELECT RAISE(ABORT, '{tabella}: registro immutabile'); END;
    CREATE TRIGGER IF NOT EXISTS {tabella}_no_delete BEFORE DELETE ON {tabella}
    BEGIN SELECT RAISE(ABORT, '{tabella}: registro immutabile'); END;
    """


def _in_decimale(valore: Decimal | int | str) -> Decimal:
    if isinstance(valore, (bool, float)):
        raise ErroreRegistro(f"Valore non ammesso: {valore!r}; usare Decimal o testo")
    try:
        risultato = Decimal(valore)
    except (InvalidOperation, TypeError, ValueError) as errore:
        raise ErroreRegistro(f"Valore non numerico: {valore!r}") from errore
    if not risultato.is_finite():
        raise ErroreRegistro(f"Valore non finito: {valore!r}")
    return risultato


def _controlla_atto(atto: Atto) -> None:
    """Solo in scrittura: i fatti già registrati restano leggibili anche se la sintassi evolve."""
    motivo = motivo_rifiuto(atto.riferimento)
    if motivo:
        raise ErroreRegistro(f"Atto non valido: {motivo}")
    citata = data_atto(atto.riferimento)
    if citata is not None and citata != atto.data:
        raise ErroreRegistro(f"La data dell'atto {atto.data} non coincide con il riferimento {atto.riferimento!r}")


class Registro:
    def __init__(self, percorso: str = ":memory:", orologio: Callable[[], datetime] | None = None):
        self._orologio = orologio or (lambda: datetime.now(UTC))
        self._db = sqlite3.connect(percorso)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.executescript(SCHEMA + "".join(_trigger_immutabilita(t) for t in TABELLE))
        self._aggiorna_schema()
        self._ultimo = self._ultimo_istante()

    def _aggiorna_schema(self) -> None:
        """Un registro creato prima dei codici riceve la colonna: i dati non cambiano."""
        colonne = {riga["name"] for riga in self._db.execute("PRAGMA table_info(fatti)")}
        if "categoriale" not in colonne:
            with self._db:
                self._db.execute("ALTER TABLE fatti ADD COLUMN categoriale INTEGER NOT NULL DEFAULT 0")

    def _ultimo_istante(self) -> datetime | None:
        unione = " UNION ALL ".join(f"SELECT registrato_il AS r FROM {t}" for t in TABELLE)
        riga = self._db.execute(f"SELECT MAX(r) FROM ({unione})").fetchone()[0]
        return datetime.fromisoformat(riga) if riga else None

    def adesso(self) -> datetime:
        """Istante corrente; il tempo di registrazione non può tornare indietro."""
        istante = in_utc(self._orologio())
        if self._ultimo is not None and istante < self._ultimo:
            raise ErroreRegistro(f"Orologio indietro: {istante} precede {self._ultimo}")
        return istante

    def _registra(self, istante: datetime) -> str:
        self._ultimo = istante
        return istante_in_testo(istante)

    def registra_fatto(
        self,
        rapporto: str,
        tipo: str,
        valore: Decimal | int | str,
        valido_dal: date,
        valido_al: date | None = None,
        atto: Atto | None = None,
    ) -> Fatto:
        return self._inserisci_fatto(rapporto, tipo, _in_decimale(valore), False, valido_dal, valido_al, atto)

    def registra_codice(
        self,
        rapporto: str,
        tipo: str,
        codice: str,
        valido_dal: date,
        valido_al: date | None = None,
        atto: Atto | None = None,
    ) -> Fatto:
        """Fatto categoriale, come contratto o qualifica: il codice resta testo e una formula non lo legge."""
        if not isinstance(codice, str) or not codice.strip():
            raise ErroreRegistro(f"Codice non valido: {codice!r}")
        return self._inserisci_fatto(rapporto, tipo, codice, True, valido_dal, valido_al, atto)

    def registra_pagamento(self, rapporto: str, esito_id: int, data: date, atto: Atto | None = None) -> Fatto:
        """Valuta dell'accredito di un esito pagato (ADR 0006). Un nuovo fatto corregge il precedente."""
        esito = self.esito(esito_id)
        if esito.tipo is not TipoEsito.PAGATO:
            raise ErroreRegistro(f"La data di pagamento vale solo per un esito pagato, non per l'esito {esito_id}")
        if not any(riga.rapporto == rapporto for riga in esito.righe):
            raise ErroreRegistro(f"L'esito {esito_id} non contiene il rapporto {rapporto}")
        return self._inserisci_fatto(rapporto, TIPO_DATA_PAGAMENTO, Decimal(esito_id), False, data, data, atto)

    def pagamenti(self, rapporto: str, noto_al: datetime) -> dict[int, Fatto]:
        """Per ogni esito pagato del rapporto, l'ultima data di pagamento registrata e non annullata."""
        return {int(fatto.valore): fatto for fatto in self.fatti_noti(rapporto, TIPO_DATA_PAGAMENTO, noto_al)}

    def _inserisci_fatto(
        self,
        rapporto: str,
        tipo: str,
        valore: Decimal | str,
        categoriale: bool,
        valido_dal: date,
        valido_al: date | None,
        atto: Atto | None,
    ) -> Fatto:
        if not rapporto or not tipo:
            raise ErroreRegistro("Rapporto e tipo sono obbligatori")
        if valido_al is not None and valido_al < valido_dal:
            raise ErroreRegistro("Validità invertita")
        if atto is not None:
            _controlla_atto(atto)
        istante = self.adesso()
        with self._db:
            cursore = self._db.execute(
                "INSERT INTO fatti (rapporto, tipo, valore, valido_dal, valido_al, registrato_il,"
                " atto_riferimento, atto_data, categoriale) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    rapporto,
                    tipo,
                    str(valore),
                    valido_dal.isoformat(),
                    valido_al.isoformat() if valido_al else None,
                    istante_in_testo(istante),
                    atto.riferimento if atto else None,
                    atto.data.isoformat() if atto else None,
                    int(categoriale),
                ),
            )
        self._registra(istante)
        return Fatto(cursore.lastrowid, rapporto, tipo, valore, valido_dal, valido_al, istante, atto, categoriale)

    def annulla_fatto(self, fatto_id: int, motivo: str) -> None:
        """Un fatto errato senza sostituto si neutralizza con una nuova registrazione."""
        if not motivo or not motivo.strip():
            raise ErroreRegistro("Il motivo dell'annullamento è obbligatorio")
        istante = self.adesso()
        try:
            with self._db:
                self._db.execute(
                    "INSERT INTO annullamenti (fatto_id, motivo, registrato_il) VALUES (?, ?, ?)",
                    (fatto_id, motivo, istante_in_testo(istante)),
                )
        except sqlite3.IntegrityError as errore:
            raise ErroreRegistro(f"Fatto {fatto_id} inesistente o già annullato") from errore
        self._registra(istante)

    def fatti_noti(self, rapporto: str, tipo: str, noto_al: datetime) -> list[Fatto]:
        """Fatti registrati e non annullati all'istante indicato, in ordine di registrazione."""
        limite = istante_in_testo(noto_al)
        righe = self._db.execute(
            """
            SELECT * FROM fatti AS f
            WHERE f.rapporto = ? AND f.tipo = ? AND f.registrato_il <= ?
              AND NOT EXISTS (
                  SELECT 1 FROM annullamenti AS a WHERE a.fatto_id = f.id AND a.registrato_il <= ?
              )
            ORDER BY f.id
            """,
            (rapporto, tipo, limite, limite),
        ).fetchall()
        return [_fatto_da_riga(riga) for riga in righe]

    def rapporti_con_codice(self, tipo: str, codice: str, noto_al: datetime) -> list[str]:
        """Rapporti con un fatto categoriale di quel codice, come il codice fiscale della persona."""
        limite = istante_in_testo(noto_al)
        righe = self._db.execute(
            """
            SELECT DISTINCT f.rapporto FROM fatti AS f
            WHERE f.tipo = ? AND f.valore = ? AND f.categoriale = 1 AND f.registrato_il <= ?
              AND NOT EXISTS (
                  SELECT 1 FROM annullamenti AS a WHERE a.fatto_id = f.id AND a.registrato_il <= ?
              )
            ORDER BY f.rapporto
            """,
            (tipo, codice, limite, limite),
        ).fetchall()
        return [riga[0] for riga in righe]

    def vigenti_per_giorno(self, rapporto: str, tipo: str, periodo: Mese | Periodo, noto_al: datetime) -> list[Fatto | None]:
        """Per ogni giorno del periodo vale l'ultimo fatto registrato che lo copre."""
        noti = self.fatti_noti(rapporto, tipo, noto_al)
        return [
            next((fatto for fatto in reversed(noti) if fatto.copre(giorno)), None)
            for giorno in periodo.giorni()
        ]

    def fatto_nel_periodo(self, rapporto: str, tipo: str, competenza: Mese | Periodo, noto_al: datetime) -> Fatto | None:
        """Fatto in vigore per tutto il periodo; se cambia dentro il periodo il calcolo si ferma."""
        vigenti = self.vigenti_per_giorno(rapporto, tipo, competenza, noto_al)
        distinti = {fatto.id for fatto in vigenti if fatto is not None}
        if not distinti:
            return None
        if len(distinti) > 1 or any(fatto is None for fatto in vigenti):
            raise ValiditaNonUniforme(
                f"Rapporto {rapporto}, fatto {tipo}: non uniforme in {competenza}; "
                "serve un periodo uniforme"
            )
        return vigenti[0]

    fatto_nel_mese = fatto_nel_periodo

    def registra_esito(self, tipo: TipoEsito, data: date, righe: Iterable[Importo]) -> Esito:
        elenco = tuple(righe)
        if not elenco:
            raise ErroreRegistro("Un esito deve contenere almeno un importo")
        chiavi = [riga.chiave for riga in elenco]
        if len(set(chiavi)) != len(chiavi):
            raise ErroreRegistro("Un esito non può contenere due volte lo stesso importo")
        istante = self.adesso()
        testo = json.dumps([riga.in_dizionario() for riga in elenco], ensure_ascii=False, sort_keys=True)
        with self._db:
            cursore = self._db.execute(
                "INSERT INTO esiti (tipo, data, registrato_il, righe) VALUES (?, ?, ?, ?)",
                (tipo.value, data.isoformat(), istante_in_testo(istante), testo),
            )
        self._registra(istante)
        return self.esito(cursore.lastrowid)

    def esito(self, esito_id: int) -> Esito:
        riga = self._db.execute("SELECT * FROM esiti WHERE id = ?", (esito_id,)).fetchone()
        if riga is None:
            raise ErroreRegistro(f"Esito {esito_id} inesistente")
        return _esito_da_riga(riga)

    def esiti(self, tipo: TipoEsito, noti_al: datetime) -> list[Esito]:
        righe = self._db.execute(
            "SELECT * FROM esiti WHERE tipo = ? AND registrato_il <= ? ORDER BY id",
            (tipo.value, istante_in_testo(noti_al)),
        ).fetchall()
        return [_esito_da_riga(riga) for riga in righe]

    def chiudi(self) -> None:
        self._db.close()


def _fatto_da_riga(riga: sqlite3.Row) -> Fatto:
    categoriale = bool(riga["categoriale"])
    return Fatto(
        id=riga["id"],
        rapporto=riga["rapporto"],
        tipo=riga["tipo"],
        valore=riga["valore"] if categoriale else Decimal(riga["valore"]),
        valido_dal=date.fromisoformat(riga["valido_dal"]),
        valido_al=date.fromisoformat(riga["valido_al"]) if riga["valido_al"] else None,
        registrato_il=datetime.fromisoformat(riga["registrato_il"]),
        atto=Atto(riga["atto_riferimento"], date.fromisoformat(riga["atto_data"])) if riga["atto_data"] else None,
        categoriale=categoriale,
    )


def _esito_da_riga(riga: sqlite3.Row) -> Esito:
    return Esito(
        id=riga["id"],
        tipo=TipoEsito(riga["tipo"]),
        data=date.fromisoformat(riga["data"]),
        registrato_il=datetime.fromisoformat(riga["registrato_il"]),
        righe=tuple(Importo.da_dizionario(voce) for voce in json.loads(riga["righe"])),
    )
