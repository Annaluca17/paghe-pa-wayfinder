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

from .corpus import Corpus
from .denuncia import calcola_denuncia, periodi_in_servizio
from .lista_pos_pa import TIPI_PART_TIME, DatoMancante, QuadroFermo
from .modello import (
    FATTO_PART_TIME,
    FATTO_PRIMA_ISCRIZIONE_DAL_1996,
    FATTO_TERMINE_PER_SOSTITUZIONE,
    FATTO_TIPO_PART_TIME,
)
from .part_time import TIPO_PROGRAMMAZIONE, programmazione_del_mese
from .registro import Registro
from .tempo import Mese, Periodo, in_utc

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

    def _chiedi(self, fatto: str) -> None:
        dato = DatoMancante(fatto)
        if dato not in self.mancanti:
            self.mancanti.append(dato)

    def _motivo_bozza(self, motivo: str) -> None:
        testo = f"{motivo}: bozza non trasmissibile"
        if testo not in self.motivi_bozza:
            self.motivi_bozza.append(testo)

    def fatto(self, tipo: str):
        """Il fatto vigente al primo giorno di rapporto del mese; None se manca (e allora si chiede)."""
        vigente = self.registro.vigenti_per_giorno(self.rapporto, tipo, Periodo(self.primo, self.primo), self.istante)[0]
        if vigente is None:
            self._chiedi(tipo)
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
        return int((ore / lavorabili * 10000).to_integral_value(ROUND_HALF_UP))

    def ore_lavorabili_tempo_pieno(self) -> Decimal | None:
        """Giorni lavorativi (lun-ven non festivi) del periodo di rapporto per l'orario giornaliero del tempo pieno."""
        lavorativi = self.giorni_lavorativi()
        if lavorativi is None:
            return None
        return len(lavorativi) * self.parametro(ORARIO_SETTIMANALE) / self.parametro(GIORNI_SETTIMANA)

    def giorni_lavorativi(self) -> list[date] | None:
        """Giorni di rapporto da lunedì a venerdì non festivi, dal calendario del corpus; senza calendario si chiede."""
        calendario = self.corpus.calendario_festivi(self.mese.anno)
        if calendario is None:
            self._chiedi(f"calendario_festivi {self.mese.anno}")
            return None
        return [giorno for giorno in self.giorni if giorno.weekday() < 5 and giorno not in calendario.giorni]

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
        return tuple(
            Settimana(
                _id_settimana(domenica, self.mese.anno),
                "D" if senza_ore and all(part_time.ore[g] == 0 for g in giorni) else "X",
            )
            for domenica, giorni in per_settimana.items()
        )

    def ore_programmate(self) -> Mapping[date, Decimal] | None:
        """Ore programmate nei giorni di rapporto del mese; se un giorno non è programmato, il dato si chiede."""
        programmazione = programmazione_del_mese(self.registro, self.rapporto, self.mese, self.istante)
        if any(giorno not in programmazione.ore for giorno in self.giorni):
            self._chiedi(TIPO_PROGRAMMAZIONE)
            return None
        return {giorno: programmazione.ore[giorno] for giorno in self.giorni}


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
    periodi = periodi_in_servizio(registro, corpus, rapporto, mese, istante)
    if not periodi:
        return None
    primo = periodi[0].dal
    fatto = registro.vigenti_per_giorno(rapporto, "tipo_impiego", Periodo(primo, primo), istante)[0]
    impiego = str(fatto.valore)
    if impiego in IMPIEGHI_FUORI_PERIMETRO:
        motivo = f"Tipo impiego {impiego}, {IMPIEGHI_FUORI_PERIMETRO[impiego]}: fuori dal perimetro della vista (ADR 0027)"
        return DenunciaIndividuale(rapporto, mese, fermi=(QuadroFermo(VISTA, mese.periodo, motivo),))
    if impiego not in IMPIEGHI_TEMPO_DETERMINATO:
        return None
    denuncia = calcola_denuncia(registro, corpus, rapporto, mese, istante)
    pagati = [periodo for periodo in denuncia.periodi if periodo.in_servizio and periodo.basi]
    if pagati and not any(periodo.base("cpdel") for periodo in pagati):
        motivo = (
            f"Tempo determinato con tipo impiego {impiego} e pensione non in CPDEL (nessuna base cpdel nel mese): "
            "fuori dal perimetro della vista (ADR 0027)"
        )
        return DenunciaIndividuale(rapporto, mese, fermi=(QuadroFermo(VISTA, mese.periodo, motivo),))
    vista = _Vista(registro, corpus, rapporto, mese, istante, sorted({g for p in periodi for g in p.giorni()}))
    qualifica1 = vista.codice("Qualifica1", "area")
    qualifica3 = vista.codice("Qualifica3", FATTO_TERMINE_PER_SOSTITUZIONE)
    regime_post95 = vista.codice("RegimePost95", FATTO_PRIMA_ISCRIZIONE_DAL_1996)
    codice_contratto = vista.codice("CodiceContratto", "contratto")
    tipo_codice_contratto = vista.codice("TipoCodiceContratto", "contratto")
    part_time = vista.part_time(impiego)
    cpdel = [periodo.base("cpdel").valore for periodo in pagati if periodo.base("cpdel")]
    # Senza importi pagati l'Imponibile manca, e con lui il Contributo (obbligatorio solo se c'è l'Imponibile, DT p. 52).
    imponibile = int(sum(cpdel, Decimal(0)).to_integral_value(ROUND_HALF_UP)) if cpdel else None
    return DenunciaIndividuale(
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
        mancanti=tuple(vista.mancanti),
        bozza=tuple(vista.motivi_bozza),
    )


def _contributo(corpus: Corpus, mese: Mese, imponibile: int) -> Decimal:
    """Imponibile dichiarato (intero) per l'aliquota NASpI, al centesimo: i millesimi da 5 a 9 salgono (DT p. 31)."""
    aliquota = sum((corpus.parametro(nome).vigenza_per(mese).valore for nome in ALIQUOTE_NASPI), Decimal(0))
    return (imponibile * aliquota / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
