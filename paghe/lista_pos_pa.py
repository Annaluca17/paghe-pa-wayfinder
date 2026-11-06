"""Vista ListaPosPA di un rapporto nel mese (ADR 0005 e 0008, nota di prassi 2).

Legge la denuncia calcolata e la dispone nei quadri della prima fetta: E0 per i periodi in
servizio, V1 causale 5 solo giuridico per un mese di servizio pagato più tardi, V1 causale 1 per
un arretrato pagato a un cessato o a un sospeso. Le altre variazioni non producono un quadro: la
vista si ferma, indica quello necessario e conserva gli importi. Un dato obbligatorio del
tracciato che manca nel registro viene chiesto, non stimato. La vista non arrotonda né formatta:
la serializzazione è in `paghe.uniemens`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from .corpus import Corpus
from .denuncia import Denuncia, PeriodoDenuncia, SU_CESSATO, _denuncia, calcola_denuncia, periodi_in_servizio, righe_pagate
from .modello import Importo
from .registro import Registro
from .tempo import Mese, Periodo, in_utc

ANAGRAFICA = ("codice_fiscale", "cognome", "nome", "comune_sede_lavoro", "cap_sede_lavoro")
INQUADRAMENTO = ("tipo_impiego", "tipo_servizio", "contratto", "qualifica", "regime_fine_servizio")
CODICE_CESSAZIONE = "codice_cessazione"

# Codici del tracciato, Allegato tecnico UniEmens 4.33.1, appendice B.
GESTIONE_CPDEL = "2"  # CodGestione, p. 245
GESTIONE_CREDITO = "9"
TIPO_CONTRIBUTO_CREDITO = "9"  # TipoContributo, p. 251
TIPO_CONTRIBUTO_1_PER_CENTO = "5"  # «Eccedenza con contributo maggiorato dell'1%»: da verificare
ALIQUOTA_DI_CASSA = "2"  # Aliquota, p. 256
# TipoContributo 1, p. 251: tempo pieno o part-time, per questi tipi impiego.
TIPO_CONTRIBUTO_ORDINARIO = (
    "1",
    {"1", "2", "5", "6", "8", "9", "10", "13", "14", "17", "18", "38", "39", "40", "41", "42", "43", "44", "46", "47", "48", "49", "50", "51", "52", "53"},
)
V1_RECUPERO_SU_CESSATO = "V1 causale 7, codice motivo 7"


@dataclass(frozen=True)
class Lavoratore:
    codice_fiscale: str | None
    cognome: str | None
    nome: str | None
    comune_sede_lavoro: str | None
    cap_sede_lavoro: str | None


@dataclass(frozen=True)
class Inquadramento:
    tipo_impiego: str | None
    tipo_servizio: str | None
    contratto: str | None
    qualifica: str | None
    regime_fine_servizio: str | None


@dataclass(frozen=True)
class Gestione:
    imponibile: Decimal
    contributo: Decimal


@dataclass(frozen=True)
class EnteVersante:
    """Terna del V1: l'ente dichiarante, con il mese in cui la somma è stata pagata."""

    tipo_contributo: str
    imponibile: Decimal | None
    contributo: Decimal
    anno_mese_erogazione: Mese
    aliquota: str = ALIQUOTA_DI_CASSA


@dataclass(frozen=True)
class Quadro:
    tipo: str  # "E0" o "V1"
    causale: str | None
    periodo: Periodo
    inquadramento: Inquadramento
    pensionistica: Gestione | None = None
    contrib_1_per_cento: Decimal | None = None
    credito: Gestione | None = None
    codice_cessazione: str | None = None
    enti_versanti: tuple[EnteVersante, ...] = ()
    importi: tuple[Importo, ...] = ()


@dataclass(frozen=True)
class QuadroFermo:
    """Quadro necessario ma non prodotto: gli importi restano calcolati e tracciati."""

    quadro: str
    periodo: Periodo
    motivo: str
    importi: tuple[Importo, ...] = ()


@dataclass(frozen=True)
class DatoMancante:
    """Dato obbligatorio del tracciato assente nel registro: la vista lo chiede."""

    fatto: str
    periodo: Periodo | None = None

    def __str__(self) -> str:
        return f"{self.fatto} (periodo {self.periodo})" if self.periodo else self.fatto


@dataclass(frozen=True)
class ListaPosPA:
    rapporto: str
    mese: Mese
    lavoratore: Lavoratore
    quadri: tuple[Quadro, ...]
    fermi: tuple[QuadroFermo, ...] = ()
    mancanti: tuple[DatoMancante, ...] = ()
    bozza: tuple[str, ...] = ()
    avvisi: tuple[str, ...] = ()

    @property
    def trasmissibile(self) -> bool:
        return not (self.fermi or self.mancanti or self.bozza)


def _giorno(giorno) -> Periodo:
    return Periodo(giorno, giorno)


class _Vista:
    def __init__(self, registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime):
        self.registro = registro
        self.corpus = corpus
        self.rapporto = rapporto
        self.mese = mese
        self.istante = istante
        self.mancanti: list[DatoMancante] = []
        self.avvisi: list[str] = []
        self.fermi: list[QuadroFermo] = []

    def _chiedi(self, fatto: str, periodo: Periodo | None = None) -> None:
        dato = DatoMancante(fatto, periodo)
        if dato not in self.mancanti:
            self.mancanti.append(dato)

    def codice(self, tipo: str, giorno) -> str | None:
        fatto = self.registro.vigenti_per_giorno(self.rapporto, tipo, _giorno(giorno), self.istante)[0]
        return str(fatto.valore) if fatto is not None else None

    def _in_servizio(self, giorno) -> bool:
        return self.codice(self.corpus.fatto_servizio, giorno) is not None

    def lavoratore(self) -> Lavoratore:
        """Il dato vigente a fine mese, altrimenti l'ultimo iniziato prima: un cessato resta lo stesso."""
        valori = {}
        for tipo in ANAGRAFICA:
            noti = [f for f in self.registro.fatti_noti(self.rapporto, tipo, self.istante) if f.valido_dal <= self.mese.ultimo_giorno]
            vigente = next((f for f in reversed(noti) if f.copre(self.mese.ultimo_giorno)), noti[-1] if noti else None)
            valori[tipo] = str(vigente.valore) if vigente is not None else None
            if vigente is None:
                self._chiedi(tipo)
        return Lavoratore(**valori)

    def inquadramento(self, periodo: Periodo) -> Inquadramento:
        """I codici aprono i periodi dichiarati: dentro un periodo sono uniformi."""
        valori = {tipo: self.codice(tipo, periodo.dal) for tipo in INQUADRAMENTO}
        for tipo, valore in valori.items():
            if valore is None:
                self._chiedi(tipo, periodo)
        return Inquadramento(**valori)

    def codice_cessazione(self, periodo: Periodo) -> str | None:
        """Se il servizio finisce con il periodo, il quadro porta il codice di cessazione o sospensione."""
        if not self._in_servizio(periodo.al) or self._in_servizio(periodo.al + timedelta(days=1)):
            return None
        codice = self.codice(CODICE_CESSAZIONE, periodo.al)
        if codice is None:
            self._chiedi(CODICE_CESSAZIONE, periodo)
        return codice

    # --- Quadri ---

    def e0(self, periodo: PeriodoDenuncia) -> Quadro | None:
        if not periodo.basi:
            self.avvisi.append(
                f"Periodo {periodo.periodo} in servizio senza importi pagati: andrà nel V1 causale 5 "
                "della denuncia del primo pagamento (nota di prassi 2)"
            )
            return None
        return Quadro(
            tipo="E0",
            causale=None,
            periodo=periodo.periodo,
            inquadramento=self.inquadramento(periodo.periodo),
            codice_cessazione=self.codice_cessazione(periodo.periodo),
            **_gestioni(periodo),
        )

    def giuridici(self, denuncia: Denuncia) -> list[Quadro]:
        """V1 causale 5 solo giuridico per i mesi di servizio pagati per la prima volta in questo mese."""
        competenze = sorted(
            {
                Mese(riga.periodo.dal.year, riga.periodo.dal.month)
                for periodo in denuncia.periodi
                if periodo.in_servizio
                for base in periodo.basi
                for riga in base.derivazione.importi
                if riga.periodo.dal < self.mese.primo_giorno
            }
        )
        quadri = []
        for mese in competenze:
            if any(periodo.basi for periodo in _denuncia(self.registro, self.corpus, self.rapporto, mese, self.istante).periodi):
                continue  # il mese ha il suo E0: l'arretrato sta nell'E0 di questo mese, per cassa
            if self._pagato_prima(mese):
                continue
            for periodo in periodi_in_servizio(self.registro, self.corpus, self.rapporto, mese, self.istante):
                quadri.append(
                    Quadro(
                        tipo="V1",
                        causale="5",
                        periodo=periodo,
                        inquadramento=self.inquadramento(periodo),
                        codice_cessazione=self.codice_cessazione(periodo),
                    )
                )
        return quadri

    def _pagato_prima(self, competenza: Mese) -> bool:
        """Una competenza già pagata in un mese precedente ha avuto lì il suo V1 causale 5."""
        mese = competenza
        while mese < self.mese:
            if any(
                riga.periodo.dal.year == competenza.anno and riga.periodo.dal.month == competenza.mese
                for riga in righe_pagate(self.registro, self.rapporto, mese, self.istante)
            ):
                return True
            mese = _successivo(mese)
        return False

    def fuori_servizio(self, periodo: PeriodoDenuncia) -> Quadro | None:
        """Mese senza servizio con importi pagati: V1 causale 1, oppure il quadro che servirebbe."""
        importi = periodo.basi + periodo.contributi
        if any(recupero.caso == SU_CESSATO for recupero in periodo.recuperi):
            self.fermi.append(
                QuadroFermo(
                    V1_RECUPERO_SU_CESSATO,
                    periodo.periodo,
                    "Recupero su cessato: quadro non prodotto dalla prima fetta (ADR 0008). Codice motivo 7 "
                    "«Recupero competenze dipendente cessato» (Allegato tecnico 4.33.1, p. 254); periodo da "
                    "valorizzare e codice cessazione 32 da verificare",
                    importi,
                )
            )
            return None
        ultimo = self._ultimo_periodo_di_servizio()
        if ultimo is None:
            self.fermi.append(
                QuadroFermo("da stabilire", periodo.periodo, "Importi pagati fuori servizio senza un servizio precedente", importi)
            )
            return None
        inquadramento = self.inquadramento(ultimo)
        gestioni = _gestioni(periodo)
        tipo_contributo, ammessi = TIPO_CONTRIBUTO_ORDINARIO
        if inquadramento.tipo_impiego is not None and inquadramento.tipo_impiego not in ammessi:
            self.fermi.append(
                QuadroFermo(
                    "V1 causale 1",
                    ultimo,
                    f"Tipo impiego {inquadramento.tipo_impiego}: tipo contributo dell'Ente Versante non modellato",
                    importi,
                )
            )
            return None
        terne = []
        if gestioni["pensionistica"] is not None:
            p = gestioni["pensionistica"]
            terne.append(EnteVersante(tipo_contributo, p.imponibile, p.contributo, self.mese))
        if gestioni["contrib_1_per_cento"] is not None:
            terne.append(EnteVersante(TIPO_CONTRIBUTO_1_PER_CENTO, None, gestioni["contrib_1_per_cento"], self.mese))
        if gestioni["credito"] is not None:
            c = gestioni["credito"]
            terne.append(EnteVersante(TIPO_CONTRIBUTO_CREDITO, c.imponibile, c.contributo, self.mese))
        return Quadro(
            tipo="V1",
            causale="1",
            periodo=ultimo,
            inquadramento=inquadramento,
            enti_versanti=tuple(terne),
            **gestioni,
        )

    def _ultimo_periodo_di_servizio(self) -> Periodo | None:
        """Ultimo periodo dichiarato di servizio prima del mese: lì si integra l'arretrato (da verificare)."""
        servizio = self.registro.fatti_noti(self.rapporto, self.corpus.fatto_servizio, self.istante)
        prima = self.mese.primo_giorno - timedelta(days=1)
        candidati = [min(f.valido_al or prima, prima) for f in servizio if f.valido_dal <= prima]
        for giorno in sorted(set(candidati), reverse=True):
            if not self._in_servizio(giorno):
                continue
            mese = Mese(giorno.year, giorno.month)
            periodi = [p for p in periodi_in_servizio(self.registro, self.corpus, self.rapporto, mese, self.istante) if p.dal <= giorno]
            if periodi:
                return periodi[-1]
        return None

    def bozza(self, quadri: list[Quadro]) -> list[str]:
        """Fermi del corpus con ambito `vista`: il quadro esce, ma la lista non si trasmette."""
        motivi = []
        for fermo in self.corpus.fermi:
            if fermo.ambito != "vista":
                continue
            if any(
                any(self.registro.vigenti_per_giorno(self.rapporto, fermo.fatto, quadro.periodo, self.istante))
                for quadro in quadri
            ):
                motivi.append(f"{fermo.caso}: bozza non trasmissibile ({fermo.riferimento})")
        return motivi


def _successivo(mese: Mese) -> Mese:
    return Mese(mese.anno + 1, 1) if mese.mese == 12 else Mese(mese.anno, mese.mese + 1)


def _gestioni(periodo: PeriodoDenuncia) -> dict:
    """CPDEL e credito; l'1% a parte, mai nel contributo (Circ. INPS 6/2026 § 5)."""
    contributi = {riga.istituto: riga.valore for riga in periodo.contributi}
    cpdel = periodo.base("cpdel")
    credito = periodo.base("fondo_credito")
    aggiuntivo = contributi.get("contributo_aggiuntivo")
    return {
        "pensionistica": Gestione(cpdel.valore, contributi.get("cpdel_totale", Decimal(0))) if cpdel else None,
        # Solo se diverso da zero: un 1% a zero non si espone (prassi-interpretazione).
        "contrib_1_per_cento": aggiuntivo if aggiuntivo else None,
        "credito": Gestione(credito.valore, contributi.get("fondo_credito", Decimal(0))) if credito else None,
        "importi": periodo.basi + periodo.contributi,
    }


def lista_pos_pa(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    mese: Mese,
    noto_al: datetime | None = None,
) -> ListaPosPA:
    """ListaPosPA del rapporto nel mese; funzione pura di registro, corpus e istante."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    denuncia = calcola_denuncia(registro, corpus, rapporto, mese, istante)
    vista = _Vista(registro, corpus, rapporto, mese, istante)
    lavoratore = vista.lavoratore()

    correnti: list[Quadro] = []
    precedenti: list[Quadro] = []
    for periodo in denuncia.periodi:
        if periodo.in_servizio:
            quadro = vista.e0(periodo)
            if quadro is not None:
                correnti.append(quadro)
        else:
            quadro = vista.fuori_servizio(periodo)
            if quadro is not None:
                precedenti.append(quadro)
    if not denuncia.periodi:
        for periodo in periodi_in_servizio(registro, corpus, rapporto, mese, istante):
            vista.avvisi.append(
                f"Periodo {periodo} in servizio senza importi pagati: andrà nel V1 causale 5 "
                "della denuncia del primo pagamento (nota di prassi 2)"
            )
    precedenti = vista.giuridici(denuncia) + precedenti
    quadri = correnti + sorted(precedenti, key=lambda quadro: quadro.periodo)
    return ListaPosPA(
        rapporto=rapporto,
        mese=mese,
        lavoratore=lavoratore,
        quadri=tuple(quadri),
        fermi=tuple(vista.fermi),
        mancanti=tuple(vista.mancanti),
        bozza=tuple(vista.bozza(quadri)),
        avvisi=tuple(vista.avvisi),
    )
