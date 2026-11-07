"""Vista ListaPosPA di un rapporto nel mese (ADR 0005, 0008 e 0011, nota di prassi 2).

Legge la denuncia calcolata e la dispone nei quadri della prima fetta: E0 per i periodi in
servizio, V1 causale 5 solo giuridico per un mese di servizio pagato più tardi, V1 causale 1 per
un arretrato pagato a un cessato o a un sospeso. Le altre variazioni non producono un quadro: la
vista si ferma, indica quello necessario e conserva gli importi. Un dato obbligatorio del
tracciato che manca nel registro viene chiesto, non stimato. La vista non arrotonda né formatta:
la serializzazione è in `paghe.uniemens`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from .calcolo import calcola
from .corpus import Corpus
from .denuncia import Denuncia, PeriodoDenuncia, SU_CESSATO, _denuncia, calcola_denuncia, periodi_in_servizio, righe_pagate
from .modello import FATTO_PART_TIME, FATTO_TIPO_PART_TIME, Importo
from .part_time import TIPO_PROGRAMMAZIONE, programmazione_del_mese
from .registro import Registro
from .tempo import Mese, Periodo, in_utc

ANAGRAFICA = ("codice_fiscale", "cognome", "nome", "comune_sede_lavoro", "cap_sede_lavoro")
# Codice fiscale, cognome e nome sono fatti della persona (ADR 0012, ticket #61); la sede resta sul rapporto.
# Il rapporto non li porta più: nessuna seconda via di lettura.
ANAGRAFICA_DELLA_PERSONA = ("codice_fiscale", "cognome", "nome")
INQUADRAMENTO = ("tipo_impiego", "tipo_servizio", "contratto", "qualifica", "regime_fine_servizio")
CODICE_CESSAZIONE = "codice_cessazione"

# Codici del tracciato, Allegato tecnico UniEmens 4.33.1, appendice B.
GESTIONE_CPDEL = "2"  # CodGestione, p. 245
GESTIONE_CREDITO = "9"
GESTIONE_PREVIDENZIALE = "6"  # I.N.A.D.E.L., p. 245: TFS e TFR degli enti locali
TIPO_CONTRIBUTO_TFS = "7"  # p. 252
TIPO_CONTRIBUTO_TFR = "8"
REGIMI_TFR = {"1", "2"}  # RetribTeoricaTabellareTFR e RetribValutabileTFR: DT 4.33, p. 183
BASI_UTILI_TFR = ("tfs", "tfr_ulteriori")  # voci comuni al TFS e ulteriori elementi
TIPO_CONTRIBUTO_CREDITO = "9"  # TipoContributo, p. 251
TIPO_CONTRIBUTO_1_PER_CENTO = "5"  # «Eccedenza con contributo maggiorato dell'1%»: da verificare
ALIQUOTA_DI_CASSA = "2"  # Aliquota, p. 256
# TipoContributo 1, p. 251: tempo pieno o part-time, per questi tipi impiego.
TIPO_CONTRIBUTO_ORDINARIO = (
    "1",
    {"1", "2", "5", "6", "8", "9", "10", "13", "14", "17", "18", "38", "39", "40", "41", "42", "43", "44", "46", "47", "48", "49", "50", "51", "52", "53"},
)
V1_RECUPERO_SU_CESSATO = "V1 causale 7, codice motivo 7"
# PartTimePA (DT 4.33, p. 185; AT 4.33.1, p. 244; ricerca in docs/research/part-time-lista-pos-pa.md).
IMPIEGHI_PART_TIME = {"8", "18"}  # TipoImpiego che rendono obbligatorio TipoPartTime
TIPI_PART_TIME = {"orizzontale": "P", "verticale": "V", "misto": "M"}
MILLESIMI_TEMPO_PIENO = 100000  # PercPartTime «espresso in millesimi», massimo 100000


@dataclass(frozen=True)
class Lavoratore:
    codice_fiscale: str | None
    cognome: str | None
    nome: str | None
    comune_sede_lavoro: str | None
    cap_sede_lavoro: str | None


@dataclass(frozen=True)
class PartTimePA:
    """Elemento PartTimePA: `perc` è PercPartTime in millesimi; None se il tracciato non la determina (bozza)."""

    tipo: str
    perc: int | None


@dataclass(frozen=True)
class Inquadramento:
    tipo_impiego: str | None
    tipo_servizio: str | None
    contratto: str | None
    qualifica: str | None
    regime_fine_servizio: str | None
    part_time: PartTimePA | None = None


@dataclass(frozen=True)
class Gestione:
    imponibile: Decimal
    contributo: Decimal


@dataclass(frozen=True)
class Previdenziale:
    """GestPrevidenziale: TFS con il regime 3, TFR con il regime 1 (DT 4.33, p. 191-193)."""

    imponibile_tfr: Decimal | None = None
    contributo_tfr: Decimal | None = None
    imponibile_tfr_ulteriori: Decimal | None = None
    contributo_tfr_ulteriori: Decimal | None = None
    imponibile_tfs: Decimal | None = None
    contributo_tfs: Decimal | None = None
    cod_gestione: str = GESTIONE_PREVIDENZIALE


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
    previdenziale: Previdenziale | None = None
    codice_cessazione: str | None = None
    retrib_teorica_tfr: Decimal | None = None
    retrib_valutabile_tfr: Decimal | None = None
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
        self.motivi_bozza: list[str] = []

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
        persona = self.registro.persona_del_rapporto(self.rapporto, self.istante)
        for tipo in ANAGRAFICA:
            if tipo in ANAGRAFICA_DELLA_PERSONA:
                noti = self.registro.fatti_persona_noti(persona, tipo, self.istante) if persona else []
            else:
                noti = self.registro.fatti_noti(self.rapporto, tipo, self.istante)
            noti = [f for f in noti if f.valido_dal <= self.mese.ultimo_giorno]
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
        return Inquadramento(**valori, part_time=self.part_time(periodo, valori["tipo_impiego"]))

    def _motivo_bozza(self, motivo: str) -> None:
        testo = f"{motivo}: bozza non trasmissibile"
        if testo not in self.motivi_bozza:
            self.motivi_bozza.append(testo)

    def part_time(self, periodo: Periodo, tipo_impiego: str | None) -> PartTimePA | None:
        """TipoPartTime e PercPartTime del periodo; ciò che il tracciato non determina resta bozza o dato mancante."""
        percentuale, tipo = (
            self.registro.vigenti_per_giorno(self.rapporto, fatto, _giorno(periodo.dal), self.istante)[0]
            for fatto in (FATTO_PART_TIME, FATTO_TIPO_PART_TIME)
        )
        if percentuale is None and tipo is None and tipo_impiego not in IMPIEGHI_PART_TIME:
            return None
        for fatto, assente in ((FATTO_TIPO_PART_TIME, tipo is None), (FATTO_PART_TIME, percentuale is None)):
            if assente:
                self._chiedi(fatto, periodo)
        if percentuale is None or tipo is None:
            return None
        codice = TIPI_PART_TIME.get(str(tipo.valore))
        if codice is None:
            self._motivo_bozza(
                f"Tipo part-time {tipo.valore!r} dal {tipo.valido_dal} non riconosciuto "
                f"(ammessi {', '.join(sorted(TIPI_PART_TIME))})"
            )
            return None
        return PartTimePA(codice, self._perc_part_time(codice, percentuale.valore, periodo))

    def _perc_part_time(self, codice: str, percentuale: Decimal, periodo: Periodo) -> int | None:
        if codice == "P":
            millesimi = percentuale * 1000
            if millesimi != millesimi.to_integral_value() or not 0 < millesimi < MILLESIMI_TEMPO_PIENO:
                self._motivo_bozza(
                    f"Part-time orizzontale al {percentuale}% dal {periodo.dal}: PercPartTime deve essere un numero "
                    f"intero di millesimi maggiore di 0 e minore di {MILLESIMI_TEMPO_PIENO}"
                )
                return None
            return int(millesimi)
        # Verticale e misto: la percentuale del mese dipende dalla programmazione (ADR 0026).
        mese = Mese(periodo.dal.year, periodo.dal.month)
        programmazione = programmazione_del_mese(self.registro, self.rapporto, mese, self.istante)
        if not programmazione.completa:
            self._chiedi(TIPO_PROGRAMMAZIONE, periodo)
            return None
        if codice == "V" and all(programmazione.ore[giorno] == 0 for giorno in periodo.giorni()):
            return 0  # «Da indicare 0 nel caso di part time verticale con assenza di attività lavorativa» (DT 4.33, p. 185)
        self._motivo_bozza(
            f"Part-time {'verticale' if codice == 'V' else 'misto'} dal {periodo.dal}: percentuale mensile "
            "(PercPartTime) non determinata dal documento tecnico INPS per un periodo lavorato in parte "
            "(docs/research/part-time-lista-pos-pa.md)"
        )
        return None

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
        inquadramento = self.inquadramento(periodo.periodo)
        return Quadro(
            tipo="E0",
            causale=None,
            periodo=periodo.periodo,
            inquadramento=inquadramento,
            codice_cessazione=self.codice_cessazione(periodo.periodo),
            retrib_teorica_tfr=self.retrib_teorica_tfr(periodo.periodo, inquadramento),
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
                inquadramento = self.inquadramento(periodo)
                quadri.append(
                    Quadro(
                        tipo="V1",
                        causale="5",
                        periodo=periodo,
                        inquadramento=inquadramento,
                        codice_cessazione=self.codice_cessazione(periodo),
                        # «Sempre valorizzata» (Circ. INPS 185/2021 § 2.2.1), anche senza gestioni.
                        retrib_teorica_tfr=self.retrib_teorica_tfr(periodo, inquadramento),
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
        previdenziale = gestioni["previdenziale"]
        if previdenziale is not None and previdenziale.imponibile_tfr_ulteriori is not None:
            self.fermi.append(
                QuadroFermo(
                    "V1 causale 1",
                    ultimo,
                    "Ulteriori elementi TFR in un arretrato: l'Allegato tecnico 4.33.1 non dà un tipo contributo "
                    "per l'Ente Versante (ticket #33)",
                    importi,
                )
            )
            return None
        if previdenziale is not None and previdenziale.imponibile_tfs is not None:
            terne.append(
                EnteVersante(TIPO_CONTRIBUTO_TFS, previdenziale.imponibile_tfs, previdenziale.contributo_tfs, self.mese)
            )
        if previdenziale is not None and previdenziale.imponibile_tfr is not None:
            terne.append(
                EnteVersante(TIPO_CONTRIBUTO_TFR, previdenziale.imponibile_tfr, previdenziale.contributo_tfr, self.mese)
            )
        if gestioni["credito"] is not None:
            c = gestioni["credito"]
            terne.append(EnteVersante(TIPO_CONTRIBUTO_CREDITO, c.imponibile, c.contributo, self.mese))
        return Quadro(
            tipo="V1",
            causale="1",
            periodo=ultimo,
            inquadramento=inquadramento,
            retrib_teorica_tfr=self.retrib_teorica_tfr(ultimo, inquadramento),
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

    def retrib_teorica_tfr(self, periodo: Periodo, inquadramento: Inquadramento) -> Decimal | None:
        """Mensile intero delle voci fisse utili al TFR, senza tredicesima (Circ. INPS 185/2021 § 2.2.1).

        Le voci fisse sono le regole a giorni che concorrono per intero alla base `tfs` o
        `tfr_ulteriori`; il mensile è quello della formula, prima della quota del mese parziale.
        Decisione di Luca, ticket #33: intera anche nel mese parziale (nota di prassi 6, ADR 0011).
        """
        if inquadramento.regime_fine_servizio not in REGIMI_TFR:
            return None
        mensili: dict[str, Decimal] = {}
        for riga in calcola(self.registro, self.corpus, self.rapporto, Mese(periodo.dal.year, periodo.dal.month), self.istante):
            derivazione = riga.derivazione
            if derivazione.maturazione != "giorni" or not periodo.contiene(riga.periodo):
                continue
            if not any(
                (concorso := self.corpus.concorso(riga.istituto, base, periodo.al)) and concorso.misura == "intero"
                for base in BASI_UTILI_TFR
            ):
                continue
            mensili[riga.istituto] = derivazione.quota.base if derivazione.quota else riga.valore
        if not mensili:
            self._chiedi("retribuzione teorica tabellare TFR", periodo)
            return None
        return sum(mensili.values(), Decimal(0))

    def cambio_di_regime(self) -> None:
        """Più regimi nell'anno: la tredicesima chiede un quadro non modellato (ticket #33, domanda 8)."""
        anno = Periodo(date(self.mese.anno, 1, 1), self.mese.ultimo_giorno)
        regimi = {
            str(fatto.valore)
            for fatto in self.registro.vigenti_per_giorno(self.rapporto, "regime_fine_servizio", anno, self.istante)
            if fatto is not None
        }
        if len(regimi) > 1:
            self.fermi.append(
                QuadroFermo(
                    "V1 con IdentAtto codice 2",
                    anno,
                    f"Cambio del regime di fine servizio nell'anno ({', '.join(sorted(regimi))}): la tredicesima "
                    "va dichiarata con il codice 2 di IdentAtto (Allegato tecnico 4.33.1, p. 255; msg INPS "
                    "1974/2018 e 2918/2018), non modellato",
                )
            )

    def bozza(self, quadri: list[Quadro]) -> list[str]:
        """Fermi del corpus con ambito `vista`: il quadro esce, ma la lista non si trasmette."""
        motivi = []
        for fermo in self.corpus.fermi:
            if fermo.ambito != "vista":
                continue
            if any(
                fatto is not None and (fermo.codice is None or str(fatto.valore) == fermo.codice)
                for quadro in quadri
                for fatto in self.registro.vigenti_per_giorno(self.rapporto, fermo.fatto, quadro.periodo, self.istante)
            ):
                motivi.append(f"{fermo.caso}: bozza non trasmissibile ({fermo.riferimento})")
        return motivi


def _successivo(mese: Mese) -> Mese:
    return Mese(mese.anno + 1, 1) if mese.mese == 12 else Mese(mese.anno, mese.mese + 1)


def _previdenziale(periodo: PeriodoDenuncia, contributi: dict[str, Decimal]) -> Previdenziale | None:
    """TFS o TFR dagli importi della denuncia: le regole si applicano già solo al regime giusto."""
    ulteriori = periodo.base("tfr_ulteriori")
    valori = {
        "imponibile_tfr": contributi.get("imponibile_tfr"),
        "contributo_tfr": contributi.get("contributo_tfr"),
        "imponibile_tfr_ulteriori": ulteriori.valore if ulteriori and "contributo_tfr_ulteriori" in contributi else None,
        "contributo_tfr_ulteriori": contributi.get("contributo_tfr_ulteriori"),
        "imponibile_tfs": contributi.get("imponibile_tfs"),
        "contributo_tfs": contributi.get("tfs_totale"),
    }
    return Previdenziale(**valori) if any(valore is not None for valore in valori.values()) else None


def _gestioni(periodo: PeriodoDenuncia) -> dict:
    """CPDEL, TFS o TFR e credito; l'1% a parte, mai nel contributo (Circ. INPS 6/2026 § 5)."""
    contributi = {riga.istituto: riga.valore for riga in periodo.contributi}
    cpdel = periodo.base("cpdel")
    credito = periodo.base("fondo_credito")
    aggiuntivo = contributi.get("contributo_aggiuntivo")
    return {
        "previdenziale": _previdenziale(periodo, contributi),
        "retrib_valutabile_tfr": contributi.get("retribuzione_valutabile_tfr"),
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
    vista.cambio_di_regime()

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
        bozza=tuple(vista.bozza(quadri) + vista.motivi_bozza),
        avvisi=tuple(vista.avvisi),
    )
