"""Controlli bloccanti sul file F24EP, riscritti per i test dall'Allegato 2 delle specifiche AdE (dicembre 2016).

Replicano i controlli del validatore di F24EP-editor (`tools/valida_f24ep.py`, letto in sola lettura) senza
dipendere dal tool. Posizioni e lunghezze (1-based) sono quelle delle tabelle dei record A, M, V e Z.
"""

from __future__ import annotations

import re
from decimal import Decimal

LUNGHEZZA = 1898  # 1900 con CR e LF

A = {"tipo": (1, 1), "filler1": (2, 14), "codice_fornitura": (16, 5), "tipo_fornitore": (21, 2),
     "cf_fornitore": (23, 16), "filler2": (39, 177), "denominazione": (216, 60), "filler3": (276, 164),
     "flag_origine": (440, 1), "riservato1": (441, 14), "filler4": (455, 67), "progressivo_invio": (522, 3),
     "numero_invii": (525, 3), "campo_utente": (528, 100), "flag_accettazione": (628, 1), "riservato2": (629, 1269)}
M = {"tipo": (1, 1), "cf_ente": (2, 11), "filler1": (13, 5), "progressivo_modulo": (18, 8), "utente1": (26, 3),
     "filler2": (29, 25), "utente2": (54, 20), "filler3": (74, 16), "filler4": (90, 1), "valuta": (91, 1),
     "filler5": (92, 426), "denominazione": (518, 55), "codice_identificativo": (573, 2), "cf_terzo": (575, 16),
     "riservato": (591, 60), "filler6": (651, 1117), "tipo_titolare": (1768, 2), "cf_titolare": (1770, 11),
     "paese": (1781, 2), "controllo": (1783, 2), "cin": (1785, 1), "abi": (1786, 5), "cab": (1791, 5),
     "conto": (1796, 12), "filler7": (1808, 1), "email": (1809, 60), "valuta_riepilogo": (1869, 4),
     "saldo_debito": (1873, 15), "data_versamento": (1888, 10)}
V = {"tipo": (1, 1), "cf_ente": (2, 11), "filler1": (13, 5), "progressivo_modulo": (18, 8), "utente1": (26, 3),
     "filler2": (29, 25), "utente2": (54, 20), "filler3": (74, 16), "tipo_modello": (90, 1),
     "totale_debito": (1743, 15), "totale_credito": (1758, 15), "segno": (1773, 1), "saldo": (1774, 15),
     "filler4": (1789, 4), "saldo_finale": (1793, 15), "data_versamento": (1808, 8), "filler5": (1816, 82)}
Z = {"tipo": (1, 1), "filler1": (2, 14), "numero_v": (16, 9), "numero_m": (25, 9), "filler2": (34, 1864)}

PRIMA_RIGA, RIGHE_PER_V, LUNGHEZZA_RIGA = 123, 22, 71
RIGA = {"tipo": (0, 1), "tributo": (1, 6), "codice": (7, 5), "estremi": (12, 17), "rif_a": (29, 6),
        "rif_b": (35, 6), "debito": (41, 15), "credito": (56, 15)}
TIPI_RIGA = "FIRSNQWGP5"


def campo(record: str, voce: tuple[int, int]) -> str:
    inizio, lunghezza = voce
    return record[inizio - 1 : inizio - 1 + lunghezza]


def campo_riga(riga: str, voce: tuple[int, int]) -> str:
    inizio, lunghezza = voce
    return riga[inizio : inizio + lunghezza]


def righe_del_record(record: str) -> list[str]:
    return [
        record[PRIMA_RIGA - 1 + k * LUNGHEZZA_RIGA : PRIMA_RIGA - 1 + (k + 1) * LUNGHEZZA_RIGA] for k in range(RIGHE_PER_V)
    ]


def euro(testo: str) -> Decimal:
    return Decimal(testo) / 100


def importo_italiano(valore: Decimal) -> str:
    return "{:,.2f}".format(valore).replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def controlla(grezzo: bytes) -> tuple[list[str], list[str]]:
    """(errori bloccanti, divergenze dalla specifica) del file."""
    errori: list[str] = []
    divergenze: list[str] = []
    if b"\r\n" not in grezzo:
        errori.append("terminatori CRLF assenti")
    righe = grezzo.split(b"\r\n")
    while righe and righe[-1] == b"":
        righe.pop()
    record = [riga.decode("latin-1") for riga in righe]
    for numero, r in enumerate(record, 1):
        if len(r) != LUNGHEZZA:
            errori.append(f"record {numero}: lunghezza {len(r)}, attesa {LUNGHEZZA}")
        if r[1897:1898] != "A":
            errori.append(f"record {numero}: posizione 1898 diversa da 'A'")
    sequenza = "".join(r[0] for r in record)
    if not re.fullmatch(r"A(MV+)+Z", sequenza):
        errori.append(f"sequenza dei record anomala: {sequenza}")
        return errori, divergenze
    testa, coda = record[0], record[-1]
    modelli = [r for r in record if r[0] == "M"]
    contabili = [r for r in record if r[0] == "V"]

    if campo(testa, A["codice_fornitura"]) != "F24EP":
        errori.append("A: codice fornitura diverso da F24EP")
    if campo(testa, A["tipo_fornitore"]) != "14":
        errori.append("A: tipo fornitore diverso da 14")
    if campo(testa, A["flag_origine"]) != " ":
        errori.append("A: flag di origine diverso da spazio")
    if campo(testa, A["progressivo_invio"]) != "001":
        errori.append("A: progressivo invio diverso da 001")
    if campo(testa, A["flag_accettazione"]) != "1":
        errori.append("A: flag di accettazione diverso da 1")
    if int(campo(testa, A["numero_invii"])) != len(modelli):
        errori.append("A: numero degli invii diverso dai record M")
    if not campo(testa, A["cf_fornitore"]).strip():
        errori.append("A: codice fiscale del fornitore assente")
    if not campo(testa, A["denominazione"]).strip():
        errori.append("A: denominazione del fornitore assente")
    for nome in ("filler1", "filler2", "filler3", "filler4", "riservato1", "riservato2"):
        if campo(testa, A[nome]).strip():
            errori.append(f"A: {nome} non a spazi")

    for m in modelli:
        if campo(m, M["valuta"]) != "E":
            errori.append("M: valuta della delega diversa da E")
        if campo(m, M["valuta_riepilogo"]) != "EURO":
            errori.append("M: valuta del riepilogo diversa da EURO")
        if campo(m, M["tipo_titolare"]) != "14":
            errori.append("M: tipo titolare del conto diverso da 14")
        if campo(m, M["paese"]) != "IT":
            errori.append("M: codice paese diverso da IT")
        if campo(m, M["abi"]) != "01000":
            errori.append("M: ABI diverso da 01000")
        if campo(m, M["cab"]) != "03245":
            divergenze.append(f"M: CAB {campo(m, M['cab'])!r} invece di 03245")
        if not (campo(m, M["cin"]).isalpha() and campo(m, M["cin"]).isupper()):
            errori.append("M: CIN non è una lettera maiuscola")
        if campo(m, M["cf_titolare"]) != campo(m, M["cf_ente"]):
            errori.append("M: codice fiscale del titolare diverso da quello dell'ente")
        if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", campo(m, M["data_versamento"])):
            errori.append("M: data di versamento non nel formato GG-MM-AAAA")
        if not campo(m, M["denominazione"]).strip():
            errori.append("M: denominazione vuota")
        if not campo(m, M["email"]).strip():
            errori.append("M: e-mail assente")
        identificativo, terzo = campo(m, M["codice_identificativo"]).strip(), campo(m, M["cf_terzo"]).strip()
        if bool(identificativo) != bool(terzo):
            errori.append("M: campi 13 e 14 non coerenti")
        suoi = [
            v for v in contabili
            if campo(v, V["cf_ente"]) == campo(m, M["cf_ente"])
            and campo(v, V["progressivo_modulo"]) == campo(m, M["progressivo_modulo"])
        ]
        somma = sum((euro(campo(v, V["saldo_finale"])) for v in suoi), Decimal(0))
        if campo(m, M["saldo_debito"]).strip() != importo_italiano(somma) and campo(m, M["saldo_debito"]).strip() != (
            importo_italiano(somma).replace(".", "")
        ):
            errori.append("M: saldo totale a debito diverso dalla somma dei saldi dei record V")

    for numero, v in enumerate(contabili, 1):
        if campo(v, V["tipo_modello"]) != "D":
            errori.append(f"V{numero}: tipo modello diverso da D")
        if campo(v, V["segno"]) != "P":
            errori.append(f"V{numero}: segno del saldo diverso da P")
        if campo(v, (1685, 58)) != " " * 58:
            divergenze.append("V: filler 1685-1742 non a spazi")
        debiti = crediti = Decimal(0)
        for posizione, riga in enumerate(righe_del_record(v), 1):
            tipo = campo_riga(riga, RIGA["tipo"])
            tributo = campo_riga(riga, RIGA["tributo"]).strip()
            d, c = euro(campo_riga(riga, RIGA["debito"])), euro(campo_riga(riga, RIGA["credito"]))
            if tipo == " " and not tributo:
                if d or c:
                    errori.append(f"V{numero} riga {posizione}: importi su una riga senza tipo")
                continue
            debiti += d
            crediti += c
            if tipo not in TIPI_RIGA:
                errori.append(f"V{numero} riga {posizione}: tipo riga {tipo!r} non previsto")
            if d and c:
                errori.append(f"V{numero} riga {posizione}: debito e credito entrambi valorizzati")
            if not d and not c:
                errori.append(f"V{numero} riga {posizione}: né debito né credito")
        totale_d, totale_c = euro(campo(v, V["totale_debito"])), euro(campo(v, V["totale_credito"]))
        saldo, finale = euro(campo(v, V["saldo"])), euro(campo(v, V["saldo_finale"]))
        if debiti != totale_d:
            errori.append(f"V{numero}: totale a debito diverso dalla somma delle righe")
        if crediti != totale_c:
            errori.append(f"V{numero}: totale a credito diverso dalla somma delle righe")
        if saldo != totale_d - totale_c:
            errori.append(f"V{numero}: saldo diverso da debito meno credito")
        if saldo < 0:
            errori.append(f"V{numero}: saldo negativo")
        if finale != saldo:
            errori.append(f"V{numero}: saldo finale diverso dal saldo")
        data = campo(v, V["data_versamento"])
        if not re.fullmatch(r"\d{8}", data):
            errori.append(f"V{numero}: data di versamento non nel formato GGMMAAAA")
        sua = [m for m in modelli if campo(m, M["progressivo_modulo"]) == campo(v, V["progressivo_modulo"])]
        if sua and data != campo(sua[0], M["data_versamento"]).replace("-", ""):
            errori.append(f"V{numero}: data di versamento incongruente con il record M")

    if int(campo(coda, Z["numero_v"])) != len(contabili):
        errori.append("Z: numero dei record V dichiarato diverso dal reale")
    if int(campo(coda, Z["numero_m"])) != len(modelli):
        errori.append("Z: numero dei record M dichiarato diverso dal reale")
    return errori, divergenze
