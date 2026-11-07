"""Serializzatore del file telematico F24EP, scritto sull'Allegato 2 delle specifiche AdE (dicembre 2016).

Una fornitura è una sequenza di record a lunghezza fissa di 1.900 caratteri (1.898 più CR e LF): un
record A di testa, da 1 a 999 sequenze di un record M (dati dell'ente) seguito da 1 a 999 record V
(dati contabili, una pagina del modello, fino a 22 righe) e un record Z di coda. Posizioni e lunghezze
sono quelle delle tabelle dell'Allegato 2.

Quello che l'Allegato 2 rimanda ad altre tabelle (codici tributo, causali INPS, sedi INAIL, uffici, atti)
non si controlla qui: si controlla la forma. Le sezioni di cui il modello non legge ancora le regole
(INPS, INAIL, fondi pensione, IMU/TASI, INPGI, TARI) sono rifiutate con il loro nome.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .errori import VistaFerma

LUNGHEZZA_RECORD = 1898
CRLF = b"\r\n"
RIGHE_PER_MODULO = 22
LUNGHEZZA_RIGA = 71
PRIMA_RIGA = 123  # posizione 1-based della prima riga del record V
MASSIMO_MODELLI = 999
MASSIMO_MODULI = 999
ABI_BANCA_D_ITALIA = "01000"
CAB_BANCA_D_ITALIA = "03245"
SEZIONI_MODELLATE = ("F", "R", "S", "Q")
SEZIONI_DELLA_SPECIFICA = {
    "F": "Erario", "I": "INPS", "R": "Regioni", "S": "Enti Locali", "N": "INAIL",
    "Q": "INPDAP", "W": "Fondi Pensione", "G": "IMU/TASI", "P": "INPGI", "5": "TARES/TARI",
}


@dataclass(frozen=True)
class RigaF24EP:
    """Riga di un modulo: sezione (tipo riga), codice tributo o causale, codice, estremi, riferimenti A e B, importi in euro."""

    sezione: str
    tributo: str
    codice: str = ""
    estremi: str = ""
    rif_a: str = ""
    rif_b: str = ""
    debito: Decimal = Decimal(0)
    credito: Decimal = Decimal(0)


@dataclass(frozen=True)
class ModuloF24EP:
    """Un record V: una pagina del modello, con il proprio saldo, che non può essere negativo."""

    righe: tuple[RigaF24EP, ...]

    @property
    def totale_debito(self) -> Decimal:
        return sum((riga.debito for riga in self.righe), Decimal(0))

    @property
    def totale_credito(self) -> Decimal:
        return sum((riga.credito for riga in self.righe), Decimal(0))

    @property
    def saldo(self) -> Decimal:
        return self.totale_debito - self.totale_credito


@dataclass(frozen=True)
class ModelloF24EP:
    """Un record M con i suoi record V: l'ente, il conto di addebito e la data di versamento."""

    cf_ente: str
    denominazione: str
    email: str
    iban: str
    data_versamento: date
    moduli: tuple[ModuloF24EP, ...]

    @property
    def saldo(self) -> Decimal:
        return sum((modulo.saldo for modulo in self.moduli), Decimal(0))


@dataclass(frozen=True)
class FornituraF24EP:
    """Il file: l'ente invia direttamente, quindi il fornitore del record A è l'ente dei record M."""

    modelli: tuple[ModelloF24EP, ...]
    campo_utente: str = ""


def _ferma(motivo: str):
    raise VistaFerma(f"File F24EP: {motivo}")


def _ascii(testo: str, nome: str) -> None:
    if not isinstance(testo, str) or not testo.isascii() or not testo.isprintable():
        _ferma(f"{nome}: solo caratteri ASCII stampabili (la specifica non dice quale codifica accetta)")


def _alfanumerico(testo: str, lunghezza: int) -> bytes:
    """Allineato a sinistra, riempito a spazi."""
    return testo.ljust(lunghezza).encode("ascii")


def _numerico(valore: int, lunghezza: int) -> bytes:
    """Allineato a destra, riempito a zeri."""
    return str(valore).rjust(lunghezza, "0").encode("ascii")


def _centesimi(importo: Decimal, nome: str) -> int:
    if not isinstance(importo, Decimal) or not importo.is_finite() or importo < 0:
        _ferma(f"{nome}: importo non ammesso, {importo!r}")
    centesimi = importo * 100
    if centesimi != centesimi.to_integral_value() or len(str(int(centesimi))) > 15:
        _ferma(f"{nome}: importo non ammesso, {importo!r} (centesimi interi, al massimo 15 cifre)")
    return int(centesimi)


def _importo_italiano(importo: Decimal, con_migliaia: bool) -> str:
    testo = f"{importo:,.2f}" if con_migliaia else f"{importo:.2f}"
    return testo.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def cf_ente_valido(codice: str) -> bool:
    """Codice fiscale di un ente: 11 cifre, l'ultima di controllo (stesso algoritmo della partita IVA)."""
    if not isinstance(codice, str) or len(codice) != 11 or not codice.isdigit() or not codice.isascii():
        return False
    cifre = [int(c) for c in codice]
    somma = sum(cifre[0:10:2]) + sum(d * 2 - 9 if d * 2 > 9 else d * 2 for d in cifre[1:10:2])
    return (10 - somma % 10) % 10 == cifre[10]


def problemi_iban_tesoreria(iban: str) -> list[str]:
    """Controlli dell'Allegato 2 sul conto di addebito: Banca d'Italia, ABI e CAB fissi, cifre di controllo IBAN."""
    if not isinstance(iban, str) or len(iban) != 27 or not iban.isascii():
        return ["IBAN: servono 27 caratteri"]
    if iban[:2] != "IT":
        return ["IBAN: il codice paese è sempre IT"]
    problemi = []
    if not iban[2:4].isdigit():
        problemi.append("IBAN: le cifre di controllo non sono due cifre")
    if not (iban[4].isalpha() and iban[4].isupper()):
        problemi.append("IBAN: CIN non è una lettera maiuscola")
    if iban[5:10] != ABI_BANCA_D_ITALIA:
        problemi.append(f"IBAN: ABI {iban[5:10]!r} diverso da {ABI_BANCA_D_ITALIA} (Banca d'Italia)")
    if iban[10:15] != CAB_BANCA_D_ITALIA:
        problemi.append(f"IBAN: CAB {iban[10:15]!r} diverso da {CAB_BANCA_D_ITALIA}")
    if not re.fullmatch(r"[0-9A-Z]{12}", iban[15:]):
        problemi.append("IBAN: il numero di conto è di 12 caratteri maiuscoli o cifre")
    if problemi:
        return problemi
    cifre = "".join(str(int(c, 36)) for c in iban[4:] + iban[:4])
    if int(cifre) % 97 != 1:
        return ["IBAN: le cifre di controllo non tornano (modulo 97)"]
    return []


def problemi_dati_ente(cf: str, denominazione: str, email: str, iban: str) -> list[str]:
    problemi = []
    if not cf_ente_valido(cf):
        problemi.append(f"codice fiscale dell'ente {cf!r}: servono 11 cifre con la cifra di controllo valida")
    if not isinstance(denominazione, str) or not denominazione.strip():
        problemi.append("denominazione dell'ente vuota")
    elif len(denominazione) > 55:
        problemi.append(f"denominazione dell'ente di {len(denominazione)} caratteri, al massimo 55")
    elif not denominazione.isascii() or not denominazione.isprintable():
        problemi.append("denominazione dell'ente: solo caratteri ASCII stampabili")
    if not isinstance(email, str) or not email.strip():
        problemi.append("e-mail dell'ente assente")
    elif len(email) > 60 or "@" not in email or not email.isascii() or not email.isprintable() or " " in email:
        problemi.append("e-mail dell'ente non valida: al massimo 60 caratteri ASCII con la chiocciola")
    problemi.extend(problemi_iban_tesoreria(iban))
    return problemi


# Controlli di forma delle righe, per sezione

def _controlla_riga(riga: RigaF24EP, nome: str) -> None:
    if riga.sezione not in SEZIONI_DELLA_SPECIFICA:
        _ferma(f"{nome}: sezione {riga.sezione!r} fuori dall'elenco della specifica")
    if riga.sezione not in SEZIONI_MODELLATE:
        _ferma(
            f"{nome}: sezione {riga.sezione} ({SEZIONI_DELLA_SPECIFICA[riga.sezione]}) non modellata: "
            "le sue regole di compilazione non sono ancora lette"
        )
    for testo, campo, massimo in (
        (riga.tributo, "codice tributo", 6),
        (riga.codice, "codice", 5),
        (riga.estremi, "estremi", 17),
        (riga.rif_a, "riferimento A", 6),
        (riga.rif_b, "riferimento B", 6),
    ):
        _ascii(testo, f"{nome}: {campo}")
        if len(testo) > massimo:
            _ferma(f"{nome}: {campo} {testo!r} oltre {massimo} caratteri")
        if campo in ("codice tributo", "codice") and " " in testo:
            _ferma(f"{nome}: {campo} {testo!r} con spazi")
        if campo.startswith("riferimento") and testo != testo.strip():
            _ferma(f"{nome}: {campo} {testo!r} con spazi ai margini")
        if campo.startswith("riferimento") and " " in testo:
            _ferma(f"{nome}: {campo} {testo!r} con spazi")
    if not riga.tributo:
        _ferma(f"{nome}: codice tributo mancante")
    debito, credito = _centesimi(riga.debito, f"{nome}: importo a debito"), _centesimi(riga.credito, f"{nome}: importo a credito")
    if debito and credito:
        _ferma(f"{nome}: debito e credito entrambi valorizzati")
    if not debito and not credito:
        _ferma(f"{nome}: né debito né credito")
    if riga.sezione == "F":
        if riga.codice:
            _ferma(f"{nome}: sezione Erario, il campo codice non è valorizzabile")
        if riga.estremi:
            _ferma(f"{nome}: sezione Erario, il campo estremi non è valorizzabile")
    elif riga.sezione == "R":
        if not re.fullmatch(r"\d{2}", riga.codice):
            _ferma(f"{nome}: sezione Regioni, il codice è la regione di due cifre, non {riga.codice!r}")
        if riga.estremi:
            _ferma(f"{nome}: sezione Regioni, il campo estremi non è valorizzabile")
    elif riga.sezione == "S":
        if not re.fullmatch(r"[A-Z]\d{3}", riga.codice):
            _ferma(f"{nome}: sezione Enti locali, il codice è il codice catastale di quattro caratteri, non {riga.codice!r}")
        if riga.estremi:
            _ferma(f"{nome}: sezione Enti locali, il campo estremi non è valorizzabile")
    elif riga.sezione == "Q":
        if not re.fullmatch(r"[A-Z]{2}", riga.codice):
            _ferma(f"{nome}: sezione INPDAP, il codice è la sigla di provincia di due lettere, non {riga.codice!r}")


def _controlla(fornitura: FornituraF24EP) -> None:
    if not fornitura.modelli:
        _ferma("serve almeno un modello")
    if len(fornitura.modelli) > MASSIMO_MODELLI:
        _ferma(f"al massimo {MASSIMO_MODELLI} modelli")
    _ascii(fornitura.campo_utente, "campo utente")
    if len(fornitura.campo_utente) > 100:
        _ferma("campo utente oltre 100 caratteri")
    if len({modello.cf_ente for modello in fornitura.modelli}) > 1 or len(
        {modello.denominazione for modello in fornitura.modelli}
    ) > 1:
        _ferma("i modelli di una fornitura sono dello stesso ente: l'invio è diretto, il fornitore è l'ente")
    for numero, modello in enumerate(fornitura.modelli, 1):
        problemi = problemi_dati_ente(modello.cf_ente, modello.denominazione, modello.email, modello.iban)
        if problemi:
            _ferma(f"modello {numero}: {problemi[0]}")
        if not isinstance(modello.data_versamento, date):
            _ferma(f"modello {numero}: data di versamento non valida")
        if not modello.moduli:
            _ferma(f"modello {numero}: serve almeno un modulo")
        if len(modello.moduli) > MASSIMO_MODULI:
            _ferma(f"modello {numero}: al massimo {MASSIMO_MODULI} moduli")
        for posizione, modulo in enumerate(modello.moduli, 1):
            nome = f"modello {numero}, modulo {posizione}"
            if not modulo.righe:
                _ferma(f"{nome}: serve almeno una riga")
            if len(modulo.righe) > RIGHE_PER_MODULO:
                _ferma(f"{nome}: al massimo {RIGHE_PER_MODULO} righe, trovate {len(modulo.righe)}")
            for indice, riga in enumerate(modulo.righe, 1):
                _controlla_riga(riga, f"{nome}, riga {indice}")
            if modulo.saldo < 0:
                _ferma(f"{nome}: saldo negativo ({modulo.saldo}), un modello non può avere un saldo negativo")


# Record

class _Record:
    """Un record di 1.898 caratteri: spazi, con i campi scritti alle posizioni 1-based della specifica."""

    def __init__(self, tipo: str) -> None:
        self._dati = bytearray(b" " * LUNGHEZZA_RECORD)
        self.scrivi(1, tipo.encode("ascii"))
        self.scrivi(1898, b"A")

    def scrivi(self, posizione: int, contenuto: bytes) -> None:
        inizio = posizione - 1
        self._dati[inizio : inizio + len(contenuto)] = contenuto

    def bytes(self) -> bytes:
        assert len(self._dati) == LUNGHEZZA_RECORD
        return bytes(self._dati) + CRLF


def _record_a(fornitura: FornituraF24EP) -> bytes:
    primo = fornitura.modelli[0]
    r = _Record("A")
    r.scrivi(16, b"F24EP")
    r.scrivi(21, b"14")
    r.scrivi(23, _alfanumerico(primo.cf_ente, 16))
    r.scrivi(216, _alfanumerico(primo.denominazione, 60))
    r.scrivi(522, b"001")
    r.scrivi(525, _numerico(len(fornitura.modelli), 3))
    r.scrivi(528, _alfanumerico(fornitura.campo_utente, 100))
    r.scrivi(628, b"1")
    return r.bytes()


def _record_m(modello: ModelloF24EP, progressivo: int) -> bytes:
    r = _Record("M")
    r.scrivi(2, _alfanumerico(modello.cf_ente, 11))
    r.scrivi(18, _numerico(progressivo, 8))
    r.scrivi(91, b"E")
    r.scrivi(518, _alfanumerico(modello.denominazione, 55))
    r.scrivi(1768, b"14")
    r.scrivi(1770, modello.cf_ente.encode("ascii"))
    r.scrivi(1781, b"IT")
    r.scrivi(1783, modello.iban[2:4].encode("ascii"))
    r.scrivi(1785, modello.iban[4].encode("ascii"))
    r.scrivi(1786, modello.iban[5:10].encode("ascii"))
    r.scrivi(1791, modello.iban[10:15].encode("ascii"))
    r.scrivi(1796, modello.iban[15:27].encode("ascii"))
    r.scrivi(1809, _alfanumerico(modello.email, 60))
    r.scrivi(1869, b"EURO")
    saldo = _importo_italiano(modello.saldo, con_migliaia=True)
    if len(saldo) > 15:
        saldo = _importo_italiano(modello.saldo, con_migliaia=False)
    r.scrivi(1873, _alfanumerico(saldo, 15))
    r.scrivi(1888, modello.data_versamento.strftime("%d-%m-%Y").encode("ascii"))
    return r.bytes()


def _riga(riga: RigaF24EP | None) -> bytes:
    if riga is None:
        return b" " * 41 + b"0" * 30
    return (
        riga.sezione.encode("ascii")
        + _alfanumerico(riga.tributo, 6)
        + _alfanumerico(riga.codice, 5)
        + _alfanumerico(riga.estremi, 17)
        + _alfanumerico(riga.rif_a, 6)
        + _alfanumerico(riga.rif_b, 6)
        + _numerico(_centesimi(riga.debito, "debito"), 15)
        + _numerico(_centesimi(riga.credito, "credito"), 15)
    )


def _record_v(modello: ModelloF24EP, modulo: ModuloF24EP, progressivo: int) -> bytes:
    r = _Record("V")
    r.scrivi(2, _alfanumerico(modello.cf_ente, 11))
    r.scrivi(18, _numerico(progressivo, 8))
    r.scrivi(90, b"D")
    r.scrivi(94, b"0" * 11)  # codice atto, numerico: inizializzato a zeri (par. 2.4)
    for posizione in range(RIGHE_PER_MODULO):
        riga = modulo.righe[posizione] if posizione < len(modulo.righe) else None
        r.scrivi(PRIMA_RIGA + posizione * LUNGHEZZA_RIGA, _riga(riga))
    r.scrivi(1743, _numerico(_centesimi(modulo.totale_debito, "totale a debito"), 15))
    r.scrivi(1758, _numerico(_centesimi(modulo.totale_credito, "totale a credito"), 15))
    r.scrivi(1773, b"P")
    r.scrivi(1774, _numerico(_centesimi(modulo.saldo, "saldo"), 15))
    r.scrivi(1793, _numerico(_centesimi(modulo.saldo, "saldo finale"), 15))
    r.scrivi(1808, modello.data_versamento.strftime("%d%m%Y").encode("ascii"))
    return r.bytes()


def _record_z(numero_v: int, numero_m: int) -> bytes:
    r = _Record("Z")
    r.scrivi(16, _numerico(numero_v, 9))
    r.scrivi(25, _numerico(numero_m, 9))
    return r.bytes()


def serializza(fornitura: FornituraF24EP) -> bytes:
    """Il file telematico: record A, per ogni modello un M e i suoi V, record Z; ognuno chiuso da CR e LF."""
    _controlla(fornitura)
    parti = [_record_a(fornitura)]
    numero_v = 0
    for progressivo, modello in enumerate(fornitura.modelli, 1):
        parti.append(_record_m(modello, progressivo))
        for modulo in modello.moduli:
            parti.append(_record_v(modello, modulo, progressivo))
            numero_v += 1
    parti.append(_record_z(numero_v, len(fornitura.modelli)))
    return b"".join(parti)
