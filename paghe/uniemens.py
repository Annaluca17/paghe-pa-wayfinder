"""Serializzazione UniEmens della ListaPosPA, separata dal calcolo (ADR 0008).

Segue lo schema di validazione UniEmens 4.33.1 e il documento tecnico 4.33: importi con la
virgola e al massimo 2 decimali (tipo `ImportoConDecConSegno`), ordine degli elementi della
sequenza XSD. Non arrotonda: un importo con più di 2 decimali è un errore del calcolo. Si rifiuta
di scrivere una vista con dati mancanti o quadri fermi; una bozza esce solo se chiesta.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from xml.sax.saxutils import escape

from .errori import ErrorePaghe, VistaFerma
from .lista_pos_pa import GESTIONE_CPDEL, GESTIONE_CREDITO, ListaPosPA, Quadro
from .tempo import Mese


@dataclass(frozen=True)
class Ente:
    """Amministrazione dichiarante: argomento della vista, non fatto del registro."""

    cf_azienda: str
    ragione_sociale: str
    prg_azienda: str
    cf_rappresentante_firmatario: str
    istat: str | None = None
    forma_giuridica: str | None = None


@dataclass(frozen=True)
class Mittente:
    cf_persona: str
    ragione_sociale: str
    cf_mittente: str
    cf_softwarehouse: str
    tipo: str  # attributo Tipo di DatiMittente, 1-7: significato da verificare sull'Allegato tecnico
    sede_inps: str | None = None


def importo_in_testo(valore: Decimal) -> str:
    """Virgola decimale e 2 decimali; il segno meno resta (documento tecnico 4.33, p. 31)."""
    centesimi = valore.quantize(Decimal("0.01"))
    if centesimi != valore:
        raise ErrorePaghe(f"Importo {valore} con più di 2 decimali: va arrotondato dal calcolo, non dalla vista")
    return f"{centesimi:.2f}".replace(".", ",")


class _Scrittore:
    def __init__(self) -> None:
        self.righe: list[str] = ['<?xml version="1.0" encoding="UTF-8"?>']
        self.livello = 0

    def apri(self, nome: str, **attributi: str | None) -> None:
        testo = "".join(f' {k}="{escape(v)}"' for k, v in attributi.items() if v is not None)
        self.righe.append(f"{'  ' * self.livello}<{nome}{testo}>")
        self.livello += 1

    def chiudi(self, nome: str) -> None:
        self.livello -= 1
        self.righe.append(f"{'  ' * self.livello}</{nome}>")

    def campo(self, nome: str, valore: str | Decimal | None) -> None:
        if valore is None:
            return
        testo = importo_in_testo(valore) if isinstance(valore, Decimal) else escape(str(valore))
        self.righe.append(f"{'  ' * self.livello}<{nome}>{testo}</{nome}>")

    def commento(self, testo: str) -> None:
        self.righe.append(f"{'  ' * self.livello}<!-- {escape(testo).replace('--', '- -')} -->")

    def testo(self) -> str:
        return "\n".join(self.righe) + "\n"


def _controlla(viste: list[ListaPosPA], mese: Mese, bozza: bool) -> None:
    problemi = []
    for vista in viste:
        chi = f"Rapporto {vista.rapporto}"
        if vista.mese != mese:
            problemi.append(f"{chi}: vista del mese {vista.mese}, denuncia del mese {mese}")
        problemi += [f"{chi}: manca il dato {dato}" for dato in vista.mancanti]
        problemi += [f"{chi}: serve il quadro {f.quadro} per {f.periodo}. {f.motivo}" for f in vista.fermi]
        if not bozza:
            problemi += [f"{chi}: {motivo}" for motivo in vista.bozza]
    if problemi:
        raise VistaFerma("; ".join(problemi))


def _quadro(x: _Scrittore, q: Quadro, ente: Ente) -> None:
    nome = "E0_PeriodoNelMese" if q.tipo == "E0" else "V1_PeriodoPrecedente"
    x.apri(nome, CausaleVariazione=q.causale)
    x.campo("GiornoInizio", q.periodo.dal.isoformat())
    x.campo("GiornoFine", q.periodo.al.isoformat())
    i = q.inquadramento
    x.apri("InquadramentoLavPA")
    x.campo("TipoImpiego", i.tipo_impiego)
    x.campo("TipoServizio", i.tipo_servizio)
    x.campo("Contratto", i.contratto)
    x.campo("Qualifica", i.qualifica)
    x.campo("RegimeFineServizio", i.regime_fine_servizio)
    x.chiudi("InquadramentoLavPA")
    if q.pensionistica or q.credito:
        x.apri("Gestioni")
        if q.pensionistica:
            x.apri("GestPensionistica")
            x.campo("CodGestione", GESTIONE_CPDEL)
            x.campo("Imponibile", q.pensionistica.imponibile)
            x.campo("Contributo", q.pensionistica.contributo)
            x.campo("Contrib1PerCento", q.contrib_1_per_cento)
            x.chiudi("GestPensionistica")
        # GestPrevidenziale (TFS e TFR) non è modellata: la vista con il regime è una bozza.
        if q.credito:
            x.apri("GestCredito")
            x.campo("CodGestione", GESTIONE_CREDITO)
            x.campo("Imponibile", q.credito.imponibile)
            x.campo("Contributo", q.credito.contributo)
            x.chiudi("GestCredito")
        x.chiudi("Gestioni")
    x.campo("CodiceCessazione", q.codice_cessazione)
    for terna in q.enti_versanti:
        x.apri("EnteVersante")
        x.campo("TipoContributo", terna.tipo_contributo)
        x.campo("CFAzienda", ente.cf_azienda)
        x.campo("PRGAZIENDA", ente.prg_azienda)
        x.campo("Imponibile", terna.imponibile)
        x.campo("Contributo", terna.contributo)
        x.campo("AnnoMeseErogazione", str(terna.anno_mese_erogazione))
        x.campo("Aliquota", terna.aliquota)
        x.chiudi("EnteVersante")
    x.chiudi(nome)


def in_xml(viste: list[ListaPosPA], ente: Ente, mittente: Mittente, mese: Mese, bozza: bool = False) -> str:
    """DenunceMensili con la ListaPosPA dell'ente nel mese. `bozza` ammette le viste non trasmissibili."""
    _controlla(viste, mese, bozza)
    x = _Scrittore()
    for vista in viste:
        for motivo in vista.bozza:
            x.commento(f"BOZZA NON TRASMISSIBILE, rapporto {vista.rapporto}: {motivo}")
    x.apri("DenunceMensili")
    x.apri("DatiMittente", Tipo=mittente.tipo)
    x.campo("CFPersonaMittente", mittente.cf_persona)
    x.campo("RagSocMittente", mittente.ragione_sociale)
    x.campo("CFMittente", mittente.cf_mittente)
    x.campo("CFSoftwarehouse", mittente.cf_softwarehouse)
    x.campo("SedeINPS", mittente.sede_inps)
    x.chiudi("DatiMittente")
    x.apri("Azienda")
    x.campo("AnnoMeseDenuncia", str(mese))
    x.campo("CFAzienda", ente.cf_azienda)
    x.campo("RagSocAzienda", ente.ragione_sociale)
    x.apri("ListaPosPA")
    x.campo("PRGAZIENDA", ente.prg_azienda)
    x.campo("CFRappresentanteFirmatario", ente.cf_rappresentante_firmatario)
    x.campo("ISTAT", ente.istat)
    x.campo("FormaGiuridica", ente.forma_giuridica)
    x.apri("PosPA")
    for vista in viste:
        lav = vista.lavoratore
        x.apri("D0_DenunciaIndividuale")
        x.campo("CFLavoratore", lav.codice_fiscale)
        x.campo("Cognome", lav.cognome)
        x.campo("Nome", lav.nome)
        x.apri("DatiSedeLavoro")
        x.campo("CodiceComune", lav.comune_sede_lavoro)
        x.campo("CAP", lav.cap_sede_lavoro)
        x.chiudi("DatiSedeLavoro")
        for quadro in vista.quadri:  # gli E0 precedono i V1, come vuole la sequenza XSD
            _quadro(x, quadro, ente)
        x.chiudi("D0_DenunciaIndividuale")
    x.chiudi("PosPA")
    x.chiudi("ListaPosPA")
    x.chiudi("Azienda")
    x.chiudi("DenunceMensili")
    return x.testo()
