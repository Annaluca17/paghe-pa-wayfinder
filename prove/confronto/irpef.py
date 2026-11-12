"""Scomposizione della differenza di IRPEF tra gestionale e nucleo: imposta lorda, detrazione di lavoro, ulteriore detrazione.

Il nucleo espone solo la ritenuta. Qui le sue componenti si ricostruiscono rileggendo parametri e formule del corpus
(art. 11 e 13 TUIR, ulteriore detrazione), e la ricostruzione si controlla contro la ritenuta del nucleo: se non quadra
al centesimo, la riga lo dice. Per il gestionale si ricava il reddito annuo che la sua detrazione di lavoro sottintende.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from .calcolo import CORPUS_REALE

ZERO = Decimal(0)
CENT = Decimal("0.01")


def parametri(valuta: date) -> dict[str, Decimal]:
    dati = tomllib.loads(CORPUS_REALE.read_text(encoding="utf-8"))
    letti = {}
    for parametro in dati["parametro"]:
        nome = parametro["nome"]
        if nome.startswith(("irpef_", "art13_", "ulteriore_")) and "_c5_" not in nome:
            vigenti = [v for v in parametro["vigenza"] if v["dal"] <= valuta]
            if vigenti:
                letti[nome] = Decimal(str(vigenti[-1]["valore"]))
    return letti


def _tronca(valore: Decimal) -> Decimal:
    return valore.quantize(Decimal("0.0001"), rounding=ROUND_DOWN)


def _arrotonda(valore: Decimal) -> Decimal:
    return valore.quantize(CENT, rounding=ROUND_HALF_UP)


def imposta_annua(p: dict, reddito: Decimal) -> Decimal:
    return (
        p["irpef_aliquota_1"] * min(reddito, p["irpef_limite_1"])
        + p["irpef_aliquota_2"] * max(ZERO, min(reddito, p["irpef_limite_2"]) - p["irpef_limite_1"])
        + p["irpef_aliquota_3"] * max(ZERO, reddito - p["irpef_limite_2"])
    )


def detrazione_lavoro_annua(p: dict, reddito: Decimal, tronca: bool = True) -> Decimal:
    """Art. 13 c. 1 per un anno intero di lavoro."""
    t = _tronca if tronca else (lambda x: x)
    if reddito <= p["art13_soglia_a"]:
        return p["art13_importo_a"]
    if reddito <= p["art13_soglia_b"]:
        base = p["art13_importo_b_c"] + p["art13_integrazione_b"] * t((p["art13_soglia_b"] - reddito) / p["art13_divisore_b"])
    elif reddito <= p["art13_soglia_c"]:
        base = p["art13_importo_b_c"] * t((p["art13_soglia_c"] - reddito) / p["art13_divisore_c"])
    else:
        base = ZERO
    if p["art13_aumento_da"] < reddito <= p["art13_aumento_fino_a"]:
        base += p["art13_aumento"]
    return base


def ulteriore_annua(p: dict, reddito: Decimal) -> Decimal:
    if reddito <= p["ulteriore_soglia_1"]:
        return ZERO
    if reddito <= p["ulteriore_soglia_2"]:
        return p["ulteriore_importo"]
    if reddito <= p["ulteriore_soglia_3"]:
        return p["ulteriore_importo"] * (p["ulteriore_soglia_3"] - reddito) / p["ulteriore_divisore"]
    return ZERO


def reddito_implicito(p: dict, detrazione_annua: Decimal) -> Decimal | None:
    """Il reddito annuo per cui la detrazione di lavoro dell'art. 13 vale `detrazione_annua` (ricerca al euro)."""
    migliore, scarto = None, None
    reddito = p["art13_soglia_a"]
    while reddito <= p["art13_soglia_c"]:
        distanza = abs(detrazione_lavoro_annua(p, reddito, tronca=False) - detrazione_annua)
        if scarto is None or distanza < scarto:
            migliore, scarto = reddito, distanza
        reddito += 1
    return migliore if scarto is not None and scarto <= Decimal("1.00") else None


@dataclass(frozen=True)
class Scomposizione:
    matricola: int
    nominativo: str
    imponibile_gestionale: Decimal
    imponibile_prototipo: Decimal
    lorda_gestionale: Decimal
    lorda_prototipo: Decimal
    lavoro_gestionale: Decimal
    lavoro_prototipo: Decimal
    ulteriore_gestionale: Decimal
    ulteriore_prototipo: Decimal
    carichi_gestionale: Decimal
    netta_gestionale: Decimal
    ritenuta_prototipo: Decimal
    reddito_prototipo: Decimal  # reddito annuo proiettato dal nucleo (ADR 0039); senza proiezione, imponibile del mese per 12
    reddito_gestionale: Decimal | None  # quello che la detrazione di lavoro del gestionale sottintende
    giorni_mese: int
    reddito_anno_prima: str
    riduzione_tfr_non_tolta: Decimal = ZERO  # il nucleo calcola la ritenuta senza togliere la riduzione TFR dall'imponibile

    @property
    def quadra(self) -> bool:
        """La ricostruzione delle componenti del nucleo da' la sua ritenuta."""
        return abs(self.lorda_prototipo - self.lavoro_prototipo - self.ulteriore_prototipo - self.ritenuta_prototipo) <= CENT

    @property
    def mensilita(self) -> Decimal | None:
        if self.reddito_gestionale is None or not self.imponibile_gestionale:
            return None
        return (self.reddito_gestionale / self.imponibile_gestionale).quantize(CENT)

    def cause(self) -> str:
        cause = []
        if self.riduzione_tfr_non_tolta:
            cause.append(f"il nucleo non toglie dall'imponibile fiscale la riduzione TFR ({self.riduzione_tfr_non_tolta})")
        if abs(self.imponibile_prototipo - self.riduzione_tfr_non_tolta.copy_abs() - self.imponibile_gestionale) > CENT:
            cause.append("imponibile diverso anche per assenze, riscatto o altre voci non modellate")
        if self.reddito_gestionale is not None and abs(self.reddito_gestionale - self.reddito_prototipo) > 50:
            cause.append(
                f"reddito annuo per le detrazioni: gestionale circa {self.reddito_gestionale:.0f} "
                f"({self.mensilita} volte l'imponibile del mese), nucleo {self.reddito_prototipo:.0f} (proiezione)"
            )
        if self.ulteriore_gestionale == 0 and self.ulteriore_prototipo > 0:
            if self.reddito_gestionale is not None and self.reddito_gestionale > 40000:
                cause.append("ulteriore detrazione: per il gestionale il reddito annuo supera 40.000, per il prototipo no")
            else:
                cause.append("ulteriore detrazione: il gestionale non la applica (scelta del dipendente: nessuna o solo a conguaglio)")
        elif self.ulteriore_gestionale > 0 and self.ulteriore_prototipo == 0:
            cause.append("ulteriore detrazione: per il prototipo il reddito annuo e' sotto 20.000 (spetta la somma esente), per il gestionale sopra")
        elif self.ulteriore_gestionale > 0 and abs(self.ulteriore_gestionale - self.ulteriore_prototipo) > CENT:
            cause.append("ulteriore detrazione diversa: reddito annuo diverso")
        return "; ".join(cause)


def scomponi(p: dict, cedolino, calcolato, anagrafica, giorni_mese: int) -> Scomposizione | None:
    ritenuta = calcolato.valore("ritenuta_irpef")
    if ritenuta is None or cedolino.imponibile_irpef is None:
        return None
    imponibile = calcolato.imponibile_fiscale()
    riduzione = calcolato.valore("riduzione_tfr") or ZERO
    non_tolta = bool(riduzione) and imponibile == calcolato.somma("retribuzione") - riduzione - calcolato.somma("contributo_lavoratore")
    mensile = imponibile * 12  # gli scaglioni dell'imposta lorda restano ragguagliati al mese
    annuo = calcolato.reddito_annuo() or mensile
    quota = Decimal(giorni_mese) / 365
    lavoro = cedolino.detrazioni_dettaglio.get("altre", ZERO)
    carichi = sum((v for k, v in cedolino.detrazioni_dettaglio.items() if k in ("coniuge", "figli", "altri_familiari")), ZERO)
    dichiarata = anagrafica["detr.lav.dip."] != "Nessuna"
    return Scomposizione(
        matricola=cedolino.matricola,
        nominativo=cedolino.nominativo,
        imponibile_gestionale=cedolino.imponibile_irpef,
        imponibile_prototipo=imponibile,
        lorda_gestionale=cedolino.imposta_lorda or ZERO,
        lorda_prototipo=_arrotonda(imposta_annua(p, mensile) / 12),
        lavoro_gestionale=lavoro,
        lavoro_prototipo=_arrotonda(detrazione_lavoro_annua(p, annuo) * quota) if dichiarata else ZERO,
        ulteriore_gestionale=cedolino.somma(("9012",), "base"),
        ulteriore_prototipo=_arrotonda(ulteriore_annua(p, annuo) * quota),
        carichi_gestionale=carichi,
        netta_gestionale=cedolino.imposta_netta or ZERO,
        ritenuta_prototipo=ritenuta,
        reddito_prototipo=annuo,
        reddito_gestionale=reddito_implicito(p, lavoro * 365 / giorni_mese) if lavoro else None,
        giorni_mese=giorni_mese,
        reddito_anno_prima=anagrafica["retr.anno-1"],
        riduzione_tfr_non_tolta=riduzione if non_tolta else ZERO,
    )
