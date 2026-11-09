"""Vista DenunciaIndividuale dei tempi determinati con pensione in CPDEL (ADR 0027, ticket #77).

Legge la stessa denuncia calcolata della ListaPosPA (`calcola_denuncia`) e la dispone negli elementi della
DenunciaIndividuale della gestione privata INPS. Non serializza: nessun XML in questa vista. Un dato che manca si
chiede (`DatoMancante`), un caso che il tracciato non determina è una bozza, un caso fuori perimetro ferma la vista:
mai un valore di ripiego.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from .calendario import TIPO_PATRONO, e_lavorativo
from .corpus import Corpus
from .denuncia import calcola_denuncia, periodi_in_servizio
from .errori import ErroreCalcolo, ErroreRegistro, VistaFerma
from .lista_pos_pa import TIPI_PART_TIME, DatoMancante, QuadroFermo
from .modello import (
    FATTO_PART_TIME,
    FATTO_PRIMA_ISCRIZIONE_DAL_1996,
    FATTO_QUALIFICA_INPS,
    FATTO_TERMINE_PER_SOSTITUZIONE,
    FATTO_TIPO_PART_TIME,
    Importo,
    TipoEsito,
)
from .part_time import TIPO_PROGRAMMAZIONE, programmazione_del_mese
from .registro import Registro
from .tempo import Mese, Periodo, in_utc

TIPO_INVIO = "denuncia_individuale_inviata"  # tipo dell'evento che registra l'invio

# TipoImpiego della ListaPosPA (Allegato tecnico 4.33.1, pp. 235-236).
IMPIEGHI_TEMPO_DETERMINATO = {"17", "18"}
IMPIEGHI_PART_TIME = {"18"}
IMPIEGHI_FUORI_PERIMETRO = {
    "48": "CFL nella pubblica amministrazione (art. 3-ter D.L. 44/2023)",
    "49": "apprendistato nella pubblica amministrazione (art. 3-ter D.L. 44/2023)",
    "52": "contratto di ricerca",
    "53": "contratto di ricerca",
}
VISTA = "DenunciaIndividuale"
SISTEMA = "uniemens.denuncia_individuale"  # il sistema delle mappature del corpus
# TipoContribuzione 71: «solo contributo DS» per le amministrazioni non soggette a CUAF (Allegato tecnico 4.33.1, p. 111).
TIPO_CONTRIBUZIONE = "71"
QUALIFICA2_TEMPO_PIENO = "F"  # Allegato tecnico 4.33.1, p. 110
ORARIO_SETTIMANALE = "orario_settimanale_tempo_pieno"  # parametri del corpus: ore e giorni della settimana a tempo pieno
GIORNI_SETTIMANA = "giorni_settimana_tempo_pieno"
PART_TIME_CON_PERCENTUALE_DEL_MESE = {"V", "M"}  # PercPartTimeMese: obbligatoria solo per verticale e misto (DT p. 45)
TIPO_LAV_STAT_MESE_NON_LAVORATO = "DR00"
ALIQUOTE_NASPI = ("aliquota_naspi_ordinaria", "aliquota_naspi_integrativa")


@dataclass(frozen=True)
class Settimana:
    """Settimana (domenica-sabato) di rapporto del mese: `id` progressivo nell'anno, `copertura` X o D (DT p. 74)."""

    id: int
    copertura: str


@dataclass(frozen=True)
class Giorno:
    """Giorno di rapporto: `lavorato` S con prestazione, N senza, qualunque sia la durata (DT p. 75; circ. INPS 74/2021 § 3)."""

    giorno: date
    lavorato: str


@dataclass(frozen=True)
class DenunciaIndividuale:
    """Gli elementi della DenunciaIndividuale del mese; importi e percentuali nelle unità del tracciato.

    `imponibile` è in euro interi, `contributo` in euro con due decimali, percentuali in centesimi (100% = 10000),
    `ore_contribuite` in centesimi di ora, `settimane_utili` in centesimi di settimana (DT pp. 31, 45, 52, 56).
    """

    rapporto: str
    mese: Mese
    tipo_contribuzione: str | None = None
    imponibile: int | None = None
    contributo: Decimal | None = None
    qualifica1: str | None = None
    qualifica2: str | None = None
    qualifica3: str | None = None
    regime_post95: str | None = None
    codice_contratto: str | None = None
    tipo_codice_contratto: str | None = None
    perc_part_time: int | None = None
    perc_part_time_mese: int | None = None
    ore_contribuite: int | None = None
    settimane_utili: int | None = None
    tipo_lav_stat: str | None = None
    settimane: tuple[Settimana, ...] = ()
    giorni: tuple[Giorno, ...] = ()
    fermi: tuple[QuadroFermo, ...] = ()
    mancanti: tuple[DatoMancante, ...] = ()
    bozza: tuple[str, ...] = ()

    @property
    def trasmissibile(self) -> bool:
        return not (self.fermi or self.mancanti or self.bozza)


@dataclass(frozen=True)
class _PartTime:
    qualifica2: str | None
    perc: int | None = None
    perc_mese: int | None = None
    ore_contribuite: int | None = None
    settimane_utili: int | None = None
    ore: Mapping[date, Decimal] | None = None  # la programmazione dei giorni di rapporto, se completa


class _Vista:
    """Legge i fatti del rapporto nel mese; ciò che manca si chiede, mai un valore di ripiego."""

    def __init__(
        self, registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime, giorni: list[date]
    ):
        self.registro, self.corpus, self.rapporto, self.mese, self.istante = registro, corpus, rapporto, mese, istante
        self.giorni = giorni  # i giorni di rapporto del mese, in ordine
        self.primo = giorni[0]  # i codici aprono i periodi: dentro il mese si leggono al primo giorno
        self.mancanti: list[DatoMancante] = []
        self.motivi_bozza: list[str] = []
        self.fermi: list[QuadroFermo] = []

    def _chiedi(self, fatto: str) -> None:
        dato = DatoMancante(fatto)
        if dato not in self.mancanti:
            self.mancanti.append(dato)

    def _motivo_bozza(self, motivo: str) -> None:
        testo = f"{motivo}: bozza non trasmissibile"
        if testo not in self.motivi_bozza:
            self.motivi_bozza.append(testo)

    def fatto(self, tipo: str):
        """Il fatto vigente al primo giorno di rapporto del mese; None se manca (e allora si chiede).

        Se il valore cambia dentro il mese la vista si ferma: per l'ordine dei criteri di univocità (Qualifica1-3,
        TipoContribuzione, DT p. 23) servirebbero due denunce individuali, che il modello non produce.
        """
        periodo = Periodo(self.giorni[0], self.giorni[-1])
        per_giorno = dict(zip(periodo.giorni(), self.registro.vigenti_per_giorno(self.rapporto, tipo, periodo, self.istante)))
        vigenti = [per_giorno[giorno] for giorno in self.giorni]
        vigente = vigenti[0]
        if vigente is None:
            self._chiedi(tipo)
        elif len({str(f.valore) if f is not None else None for f in vigenti}) > 1:
            motivo = (
                f"Il fatto {tipo} cambia nel mese: serve più di una DenunciaIndividuale (criteri di univocità, DT p. 23), "
                "non modellato"
            )
            if all(f.motivo != motivo for f in self.fermi):
                self.fermi.append(QuadroFermo(VISTA, self.mese.periodo, motivo))
        return vigente

    def parametro(self, nome: str) -> Decimal:
        return self.corpus.parametro(nome).vigenza_per(self.mese).valore

    def codice(self, elemento: str, fatto: str) -> str | None:
        """Codice dell'elemento: la mappatura datata del corpus per il valore che il fatto ha nel mese."""
        vigente = self.fatto(fatto)
        if vigente is None:
            return None
        valore = str(vigente.valore)
        mappatura = self.corpus.mappatura_di_fatto(SISTEMA, elemento, fatto, valore, self.primo)
        if mappatura is None:
            self._chiedi(f"mappatura {elemento} ({fatto}={valore})")
            return None
        return mappatura.codice

    def part_time(self, impiego: str) -> _PartTime:
        """Qualifica2, percentuale del contratto e, dalla programmazione, ore e settimane utili (ADR 0026)."""
        if impiego not in IMPIEGHI_PART_TIME:
            return _PartTime(QUALIFICA2_TEMPO_PIENO)
        percentuale, tipo = self.fatto(FATTO_PART_TIME), self.fatto(FATTO_TIPO_PART_TIME)
        if percentuale is None or tipo is None:
            return _PartTime(None)
        qualifica2 = TIPI_PART_TIME.get(str(tipo.valore))
        if qualifica2 is None:
            self._motivo_bozza(
                f"Tipo part-time {tipo.valore!r} non riconosciuto (ammessi {', '.join(sorted(TIPI_PART_TIME))})"
            )
            return _PartTime(None)
        centesimi = percentuale.valore * 100
        perc = int(centesimi) if centesimi == centesimi.to_integral_value() and 0 < centesimi < 10000 else None
        if perc is None:
            self._motivo_bozza(
                f"Part-time al {percentuale.valore}%: PercPartTime deve essere un numero intero di centesimi "
                "maggiore di 0 e minore di 10000"
            )
        programmate = self.ore_programmate()
        if programmate is None:
            return _PartTime(qualifica2, perc)
        ore = sum(programmate.values(), Decimal(0))
        orario = self.parametro(ORARIO_SETTIMANALE)
        return _PartTime(
            qualifica2,
            perc,
            self.perc_del_mese(ore) if qualifica2 in PART_TIME_CON_PERCENTUALE_DEL_MESE else None,
            ore_contribuite=int((ore * 100).to_integral_value(ROUND_HALF_UP)),
            settimane_utili=int((ore / orario * 100).to_integral_value(ROUND_DOWN)),
            ore=programmate,
        )

    def perc_del_mese(self, ore: Decimal) -> int | None:
        """Ore programmate del mese su ore lavorabili del tempo pieno nello stesso mese, in centesimi (ADR 0027)."""
        lavorabili = self.ore_lavorabili_tempo_pieno()
        if lavorabili is None:
            return None
        if lavorabili == 0:
            self._motivo_bozza("Nessuna ora lavorabile del tempo pieno nel periodo di rapporto del mese: PercPartTimeMese indeterminata")
            return None
        perc = int((ore / lavorabili * 10000).to_integral_value(ROUND_HALF_UP))
        if perc > 10000:
            self._motivo_bozza(
                f"Ore programmate oltre le ore lavorabili del tempo pieno nel mese ({ore} su {lavorabili}): "
                "PercPartTimeMese oltre il 100%"
            )
            return None
        return perc

    def ore_lavorabili_tempo_pieno(self) -> Decimal | None:
        """Giorni lavorativi (lun-ven non festivi) del periodo di rapporto per l'orario giornaliero del tempo pieno."""
        lavorativi = self.giorni_lavorativi()
        if lavorativi is None:
            return None
        return len(lavorativi) * self.parametro(ORARIO_SETTIMANALE) / self.parametro(GIORNI_SETTIMANA)

    def giorni_lavorativi(self) -> list[date] | None:
        """Giorni di rapporto da lunedì a venerdì non festivi: calendario del corpus e patrono della sede (#106).

        Senza calendario si chiede. Il patrono è il fatto `patrono_sede_lavoro` che copre ciascun giorno; senza fatto
        non c'è nessun giorno in più e nessuna domanda. Se c'è ma il corpus non ne dichiara il riferimento, si chiede.
        """
        calendario = self.corpus.calendario_festivi(self.mese.anno)
        if calendario is None:
            self._chiedi(f"calendario_festivi {self.mese.anno}")
            return None
        periodo = Periodo(self.giorni[0], self.giorni[-1])
        vigenti = dict(zip(periodo.giorni(), self.registro.vigenti_per_giorno(self.rapporto, TIPO_PATRONO, periodo, self.istante)))
        patroni = {giorno: str(vigenti[giorno].valore) for giorno in self.giorni if vigenti[giorno] is not None}
        if patroni and self.corpus.riferimento_patrono is None:
            self._chiedi("patrono (riferimento nel corpus)")
            return None
        return [giorno for giorno in self.giorni if e_lavorativo(calendario, giorno, patroni.get(giorno))]

    def lavorati(self, part_time: _PartTime) -> tuple[Giorno, ...]:
        """S se il giorno ha ore programmate (a tempo pieno: è lavorativo), altrimenti N."""
        if part_time.qualifica2 is None:
            return ()
        if part_time.qualifica2 == QUALIFICA2_TEMPO_PIENO:
            lavorativi = self.giorni_lavorativi()
            if lavorativi is None:
                return ()
            con_prestazione = set(lavorativi)
        elif part_time.ore is None:
            return ()  # la programmazione manca: già chiesta
        else:
            con_prestazione = {giorno for giorno, ore in part_time.ore.items() if ore > 0}
        return tuple(Giorno(giorno, "S" if giorno in con_prestazione else "N") for giorno in self.giorni)

    def settimane(self, part_time: _PartTime) -> tuple[Settimana, ...]:
        """Le settimane di rapporto del mese; a cavallo di mese solo per i giorni di rapporto (DT p. 74)."""
        per_settimana: dict[date, list[date]] = {}
        for giorno in self.giorni:
            per_settimana.setdefault(_domenica(giorno), []).append(giorno)
        senza_ore = part_time.qualifica2 in PART_TIME_CON_PERCENTUALE_DEL_MESE
        if senza_ore and part_time.ore is None:
            return ()  # la programmazione manca: già chiesta
        ore = dict(part_time.ore or {})
        if senza_ore:
            # La copertura è della settimana intera: a cavallo di mese, se i giorni del mese sono senza ore, contano
            # anche i giorni di rapporto dell'altro mese, perché la stessa settimana non sia D in un mese e X nell'altro.
            a_cavallo = [
                d
                for d, giorni in per_settimana.items()
                if (d < self.mese.primo_giorno or d + timedelta(days=6) > self.mese.ultimo_giorno)
                and all(ore[g] == 0 for g in giorni)
            ]
            fuori = self.ore_fuori_mese(a_cavallo)
            if fuori is None:
                return ()
            ore.update(fuori)
        return tuple(
            Settimana(
                _id_settimana(domenica, self.mese.anno),
                "D"
                if senza_ore and all(v == 0 for g, v in ore.items() if domenica <= g <= domenica + timedelta(days=6))
                else "X",
            )
            for domenica in per_settimana
        )

    def ore_fuori_mese(self, domeniche: list[date]) -> dict[date, Decimal] | None:
        """Ore programmate dei giorni di rapporto fuori dal mese nelle settimane a cavallo; se mancano si chiedono."""
        ore: dict[date, Decimal] = {}
        for domenica in domeniche:
            esterni = [domenica + timedelta(days=i) for i in range(7)]
            esterni = [g for g in esterni if not (self.mese.primo_giorno <= g <= self.mese.ultimo_giorno)]
            for altro in {Mese(g.year, g.month) for g in esterni}:
                in_servizio = {
                    g for p in periodi_in_servizio(self.registro, self.corpus, self.rapporto, altro, self.istante) for g in p.giorni()
                }
                programmazione = programmazione_del_mese(self.registro, self.rapporto, altro, self.istante)
                for giorno in (g for g in esterni if g in in_servizio):
                    if giorno not in programmazione.ore:
                        self._chiedi(TIPO_PROGRAMMAZIONE)
                        return None
                    ore[giorno] = programmazione.ore[giorno]
        return ore

    def ore_programmate(self) -> Mapping[date, Decimal] | None:
        """Ore programmate nei giorni di rapporto del mese; se un giorno non è programmato, il dato si chiede."""
        programmazione = programmazione_del_mese(self.registro, self.rapporto, self.mese, self.istante)
        if any(giorno not in programmazione.ore for giorno in self.giorni):
            self._chiedi(TIPO_PROGRAMMAZIONE)
            return None
        return {giorno: programmazione.ore[giorno] for giorno in self.giorni}


CAMPI_SEMPLICI = (
    "tipo_contribuzione",
    "imponibile",
    "qualifica1",
    "qualifica2",
    "qualifica3",
    "regime_post95",
    "codice_contratto",
    "tipo_codice_contratto",
    "perc_part_time",
    "perc_part_time_mese",
    "ore_contribuite",
    "settimane_utili",
    "tipo_lav_stat",
)


def _tipo_lav_stat(part_time: _PartTime) -> str | None:
    """DR00: part-time verticale o misto senza alcuna ora programmata nel mese (Allegato tecnico 4.33.1, p. 133)."""
    if part_time.qualifica2 in PART_TIME_CON_PERCENTUALE_DEL_MESE and part_time.ore is not None:
        if all(ore == 0 for ore in part_time.ore.values()):
            return TIPO_LAV_STAT_MESE_NON_LAVORATO
    return None


def _domenica(giorno: date) -> date:
    """La domenica che apre la settimana (domenica-sabato) del giorno."""
    return giorno - timedelta(days=(giorno.weekday() + 1) % 7)


def _id_settimana(domenica: date, anno: int) -> int:
    """Progressivo nell'anno: la prima settimana è quella che contiene il 1° gennaio (DT p. 74)."""
    prima = _domenica(date(anno, 1, 1))
    return (domenica - prima).days // 7 + 1


def denuncia_individuale(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, noto_al: datetime | None = None
) -> DenunciaIndividuale | None:
    """DenunciaIndividuale del rapporto nel mese; None se il rapporto non è un tempo determinato."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    return _vista_e_righe(registro, corpus, rapporto, mese, istante)[0]


def _vista_e_righe(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, istante: datetime
) -> tuple[DenunciaIndividuale | None, tuple[Importo, ...]]:
    """La vista e le righe pagate che compongono il suo Imponibile (la base CPDEL dei periodi in servizio)."""
    periodi = periodi_in_servizio(registro, corpus, rapporto, mese, istante)
    if not periodi:
        return None, ()
    giorni = sorted({g for p in periodi for g in p.giorni()})
    tutto = Periodo(giorni[0], giorni[-1])
    per_giorno = dict(zip(tutto.giorni(), registro.vigenti_per_giorno(rapporto, "tipo_impiego", tutto, istante)))
    impieghi = {str(per_giorno[g].valore) for g in giorni if per_giorno[g] is not None}
    if len(impieghi) > 1 and impieghi & (IMPIEGHI_TEMPO_DETERMINATO | set(IMPIEGHI_FUORI_PERIMETRO)):
        # Un tempo determinato stabilizzato o assunto nel mese: l'Imponibile NASpI vale solo per una parte del mese.
        motivo = (
            f"Il fatto tipo_impiego cambia nel mese ({', '.join(sorted(impieghi))}): la DenunciaIndividuale "
            "di una parte del mese non è modellata"
        )
        return DenunciaIndividuale(rapporto, mese, fermi=(QuadroFermo(VISTA, mese.periodo, motivo),)), ()
    impiego = impieghi.pop() if impieghi else None
    if impiego in IMPIEGHI_FUORI_PERIMETRO:
        motivo = f"Tipo impiego {impiego}, {IMPIEGHI_FUORI_PERIMETRO[impiego]}: fuori dal perimetro della vista (ADR 0027)"
        return DenunciaIndividuale(rapporto, mese, fermi=(QuadroFermo(VISTA, mese.periodo, motivo),)), ()
    if impiego not in IMPIEGHI_TEMPO_DETERMINATO:
        return None, ()
    denuncia = calcola_denuncia(registro, corpus, rapporto, mese, istante)
    pagati = [periodo for periodo in denuncia.periodi if periodo.in_servizio and periodo.basi]
    if pagati and not any(periodo.base("cpdel") for periodo in pagati):
        motivo = (
            f"Tempo determinato con tipo impiego {impiego} e pensione non in CPDEL (nessuna base cpdel nel mese): "
            "fuori dal perimetro della vista (ADR 0027)"
        )
        return DenunciaIndividuale(rapporto, mese, fermi=(QuadroFermo(VISTA, mese.periodo, motivo),)), ()
    vista = _Vista(registro, corpus, rapporto, mese, istante, giorni)
    qualifica1 = vista.codice("Qualifica1", FATTO_QUALIFICA_INPS)
    qualifica3 = vista.codice("Qualifica3", FATTO_TERMINE_PER_SOSTITUZIONE)
    regime_post95 = vista.codice("RegimePost95", FATTO_PRIMA_ISCRIZIONE_DAL_1996)
    codice_contratto = vista.codice("CodiceContratto", "contratto")
    tipo_codice_contratto = vista.codice("TipoCodiceContratto", "contratto")
    part_time = vista.part_time(impiego)
    basi = [periodo.base("cpdel") for periodo in pagati if periodo.base("cpdel")]
    cpdel = [base.valore for base in basi]
    righe = {riga.chiave: riga for base in basi for riga in base.derivazione.importi}
    # Senza importi pagati l'Imponibile manca, e con lui il Contributo (obbligatorio solo se c'è l'Imponibile, DT p. 52).
    imponibile = int(sum(cpdel, Decimal(0)).to_integral_value(ROUND_HALF_UP)) if cpdel else None
    finale = DenunciaIndividuale(
        rapporto,
        mese,
        tipo_contribuzione=TIPO_CONTRIBUZIONE,
        imponibile=imponibile,
        contributo=_contributo(corpus, mese, imponibile) if imponibile is not None else None,
        qualifica1=qualifica1,
        qualifica2=part_time.qualifica2,
        qualifica3=qualifica3,
        regime_post95=regime_post95,
        codice_contratto=codice_contratto,
        tipo_codice_contratto=tipo_codice_contratto,
        perc_part_time=part_time.perc,
        perc_part_time_mese=part_time.perc_mese,
        ore_contribuite=part_time.ore_contribuite,
        settimane_utili=part_time.settimane_utili,
        tipo_lav_stat=_tipo_lav_stat(part_time),
        settimane=vista.settimane(part_time),
        giorni=vista.lavorati(part_time),
        fermi=tuple(vista.fermi),
        mancanti=tuple(vista.mancanti),
        bozza=tuple(vista.motivi_bozza),
    )
    return finale, tuple(righe[chiave] for chiave in sorted(righe, key=lambda c: (c[2].dal, c[1])))


def _contributo(corpus: Corpus, mese: Mese, imponibile: int) -> Decimal:
    """Imponibile dichiarato (intero) per l'aliquota NASpI, al centesimo: i millesimi da 5 a 9 salgono (DT p. 31)."""
    aliquota = sum((corpus.parametro(nome).vigenza_per(mese).valore for nome in ALIQUOTE_NASPI), Decimal(0))
    return (imponibile * aliquota / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)


@dataclass(frozen=True)
class DenunciaAziendale:
    """Quadratura della posizione nel mese: numero delle denunce individuali e totale a debito, intero (DT pp. 156, 171)."""

    mese: Mese
    num_den_indiv: int
    totale_a_debito: int


def denuncia_aziendale(viste: list[DenunciaIndividuale]) -> DenunciaAziendale:
    """NumDenIndiv e TotaleADebito delle denunce individuali dello stesso mese."""
    mesi = {vista.mese for vista in viste}
    if len(mesi) > 1:
        raise ErroreCalcolo("La denuncia aziendale quadra denunce individuali dello stesso mese, non di mesi diversi")
    totale = sum((vista.contributo for vista in viste if vista.contributo is not None), Decimal(0))
    return DenunciaAziendale(
        mese=next(iter(mesi)) if mesi else None,
        num_den_indiv=len(viste),
        totale_a_debito=int(totale.to_integral_value(ROUND_HALF_UP)),
    )


# --- Esito dichiarato (ADR 0027; come la delega F24EP, ADR 0023) ---


@dataclass(frozen=True)
class InvioDenunciaIndividuale:
    """La denuncia individuale com'è stata inviata: un esito dichiarato che non cambia più. Si rilegge dal registro.

    `esito_id` è l'esito dichiarato con le righe pagate dell'Imponibile; è assente se il mese non ha imponibile.
    """

    id: str
    rapporto: str
    mese: Mese
    vista: DenunciaIndividuale
    esito_id: int | None
    evento_id: int


def _chiave_invio(invio_id: str) -> str:
    return f"denuncia_individuale:{invio_id}"


def _in_dizionario(vista: DenunciaIndividuale) -> dict:
    """Gli elementi dichiarati della vista, come testo: ciò che l'invio fissa."""
    dichiarati = {campo: getattr(vista, campo) for campo in CAMPI_SEMPLICI}
    dichiarati["contributo"] = str(vista.contributo) if vista.contributo is not None else None
    dichiarati["settimane"] = [[s.id, s.copertura] for s in vista.settimane]
    dichiarati["giorni"] = [[g.giorno.isoformat(), g.lavorato] for g in vista.giorni]
    return dichiarati


def _da_dizionario(rapporto: str, mese: Mese, dati: dict) -> DenunciaIndividuale:
    contributo = dati["contributo"]
    return DenunciaIndividuale(
        rapporto,
        mese,
        **{campo: dati[campo] for campo in CAMPI_SEMPLICI},
        contributo=Decimal(contributo) if contributo is not None else None,
        settimane=tuple(Settimana(i, copertura) for i, copertura in dati["settimane"]),
        giorni=tuple(Giorno(date.fromisoformat(g), lavorato) for g, lavorato in dati["giorni"]),
    )


def _contenuto_dell_invio(invio_id: str, vista: DenunciaIndividuale) -> dict:
    return {"id": invio_id, "rapporto": vista.rapporto, "mese": str(vista.mese), "vista": _in_dizionario(vista)}


def _invio_dal_evento(evento) -> InvioDenunciaIndividuale:
    dati = evento.contenuto
    mese = Mese.da_testo(dati["mese"])
    return InvioDenunciaIndividuale(
        dati["id"], dati["rapporto"], mese, _da_dizionario(dati["rapporto"], mese, dati["vista"]), evento.esito_id, evento.id
    )


def invia_denuncia_individuale(
    registro: Registro, corpus: Corpus, invio_id: str, adattatore: str, rapporto: str, mese: Mese
) -> InvioDenunciaIndividuale:
    """Invia la denuncia individuale del mese: l'esito dichiarato nasce qui e non cambia più.

    Con lo stesso identificativo e la stessa vista non ha effetto; con una vista diversa è un errore: la correzione
    è un nuovo invio, con un altro identificativo. Una vista con dati mancanti, bozza o fermi non si invia.
    """
    if not isinstance(invio_id, str) or not invio_id.strip():
        raise ErroreRegistro("L'invio ha un identificativo")
    chiave = _chiave_invio(invio_id)
    istante = registro.adesso()
    vista, righe = _vista_e_righe(registro, corpus, rapporto, mese, istante)
    gia = registro.evento(chiave)
    if gia is not None:
        nuovo = _contenuto_dell_invio(invio_id, vista) if vista is not None and vista.trasmissibile else None
        if nuovo is None or nuovo != gia.contenuto:
            raise ErroreRegistro(f"Evento {chiave}: stesso identificativo con contenuto diverso, rifiutato")
        return _invio_dal_evento(gia)
    if vista is None:
        raise VistaFerma(f"Denuncia individuale {invio_id}: il rapporto {rapporto} non è un tempo determinato in servizio in {mese}")
    if not vista.trasmissibile:
        ragioni = [f.motivo for f in vista.fermi] + [f"dato mancante {d}" for d in vista.mancanti] + list(vista.bozza)
        raise VistaFerma(f"Denuncia individuale {invio_id} non inviabile: " + "; ".join(ragioni))
    assenze = controlla_completezza(registro, corpus, mese, istante)
    if assenze:
        raise VistaFerma(
            f"Denuncia individuale {invio_id} non inviabile, la fornitura di {mese} non è completa: "
            + "; ".join(f"{a.rapporto}: {a.motivo}" for a in assenze)
        )
    with registro.atomico():
        esito = registro.registra_esito(TipoEsito.DICHIARATO, istante.date(), righe) if righe else None
        evento = registro.registra_evento(
            chiave, TIPO_INVIO, _contenuto_dell_invio(invio_id, vista), adattatore, esito_id=esito.id if esito else None
        )
    return _invio_dal_evento(evento)


def leggi_invio_denuncia_individuale(registro: Registro, invio_id: str) -> InvioDenunciaIndividuale:
    evento = registro.evento(_chiave_invio(invio_id))
    if evento is None or evento.tipo != TIPO_INVIO:
        raise ErroreRegistro(f"Invio {invio_id}: inesistente")
    return _invio_dal_evento(evento)


@dataclass(frozen=True)
class ScostamentoInvio:
    """Un elemento della vista di oggi che differisce da quello dell'ultimo invio."""

    campo: str
    inviato: object
    attuale: object


def segnala_scostamento_invio(
    registro: Registro, corpus: Corpus, rapporto: str, mese: Mese, noto_al: datetime | None = None
) -> tuple[ScostamentoInvio, ...]:
    """Differenza tra la vista di oggi e l'ultimo invio del rapporto nel mese; vuota se nessun invio o nessuna differenza.

    Non corregge nulla: la correzione è un nuovo invio (ADR 0027).
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    invii = [
        e for e in registro.eventi(TIPO_INVIO, istante) if e.contenuto["rapporto"] == rapporto and e.contenuto["mese"] == str(mese)
    ]
    if not invii:
        return ()
    inviato = invii[-1].contenuto["vista"]
    vista, _ = _vista_e_righe(registro, corpus, rapporto, mese, istante)
    attuale = _in_dizionario(vista) if vista is not None else {campo: None for campo in inviato}
    return tuple(
        ScostamentoInvio(campo, inviato[campo], attuale.get(campo)) for campo in inviato if inviato[campo] != attuale.get(campo)
    )


# --- Controllo di completezza degli output (ADR 0015, 0022) ---


@dataclass(frozen=True)
class Assenza:
    """Un tempo determinato o una sua base CPDEL che la DenunciaIndividuale del mese non comprende."""

    rapporto: str
    motivo: str


def _rapporti_a_tempo_determinato(registro: Registro, istante: datetime) -> list[str]:
    return sorted({r for impiego in IMPIEGHI_TEMPO_DETERMINATO for r in registro.rapporti_con_codice("tipo_impiego", impiego, istante)})


def controlla_completezza(
    registro: Registro, corpus: Corpus, mese: Mese, noto_al: datetime | None = None
) -> tuple[Assenza, ...]:
    """Ogni base CPDEL pagata a un tempo determinato finisce nell'Imponibile della sua denuncia; ogni tempo
    determinato in servizio ha la sua. Un'assenza ferma l'invio di questo output, non il calcolo.

    Il modello non ha una dichiarazione esplicita di esclusione per questo output: ogni assenza ferma l'invio.
    """
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    assenze = []
    for rapporto in _rapporti_a_tempo_determinato(registro, istante):
        vista, _ = _vista_e_righe(registro, corpus, rapporto, mese, istante)
        pagata = sum(
            (periodo.base("cpdel").valore for periodo in calcola_denuncia(registro, corpus, rapporto, mese, istante).periodi if periodo.base("cpdel")),
            Decimal(0),
        )
        if vista is None:
            if pagata:
                assenze.append(
                    Assenza(
                        rapporto,
                        f"base cpdel {pagata} pagata in {mese} a un tempo determinato non in servizio nel mese: "
                        "nessuna DenunciaIndividuale la comprende",
                    )
                )
        elif vista.fermi:
            assenze.append(
                Assenza(rapporto, "tempo determinato in servizio senza DenunciaIndividuale: " + "; ".join(f.motivo for f in vista.fermi))
            )
        elif pagata and vista.imponibile != int(pagata.to_integral_value(ROUND_HALF_UP)):
            assenze.append(
                Assenza(rapporto, f"base cpdel {pagata} pagata in {mese}: non è nell'Imponibile {vista.imponibile} della denuncia")
            )
    return tuple(assenze)
