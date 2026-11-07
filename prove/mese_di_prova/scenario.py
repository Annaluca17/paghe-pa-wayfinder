"""Lo scenario del mese di prova: un ente fittizio e dodici rapporti, ognuno per un caso diverso.

Dati esclusivamente fittizi: nomi, codici fiscali (con il carattere di controllo calcolato, vedi `codici`), IBAN di
prova, nessun ente reale. Lo scenario dice cosa l'Ufficio personale registra e quando; non calcola nulla.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from paghe import Atto, Mese

from .codici import codice_fiscale

DENOMINAZIONE_ENTE = "ENTE DI PROVA"
CF_ENTE = "01234567897"  # codice fiscale di fantasia dell'ente, cifra di controllo valida
IBAN_TESORERIA = "IT76X0100003245TEST00000001"  # IBAN di prova, conto evidentemente finto
IBAN_PERSONE = "IT76X0100003245TEST00000002"  # idem, per i beneficiari
EMAIL_ENTE = "paghe@ente.example"
SIGLA_PROVINCIA = "RM"
COMUNE_SEDE = "H501"
CAP_SEDE = "00100"

MARZO = Mese(2026, 3)
FEBBRAIO = Mese(2026, 2)
DICEMBRE = Mese(2026, 12)
ULTIMO_PAGAMENTO_2026 = date(2026, 12, 18)

QUALIFICHE = {"funzionari": "0FZEQF", "istruttori": "0IR000", "operatori_esperti": "0OEESP", "operatori": "0OP000"}
# Dirigente e segretario: nessun codice di qualifica ne' di contratto e' stato letto sul tracciato (ticket #73): non si inventano,
# il rapporto non li registra e la ListaPosPA li chiede come dati mancanti.
CONTRATTO_COMPARTO = "RALN"
FATTO_POSIZIONE = {"dirigente": "posizione_annua_dirigente", "segretario": "posizione_annua_segretario"}


@dataclass(frozen=True)
class Rapporto:
    id: str
    persona: str
    nome: str
    titolo: str
    caso: str
    nascita: date
    dal: date
    area: str | None = None
    regime: str | None = None
    al: date | None = None
    detrazioni: bool = True
    impiego: str = "1"  # TipoImpiego della ListaPosPA: 1 tempo pieno indeterminato, 18 tempo determinato part-time
    posizione: str | None = None  # posizione annua deliberata dall'ente (dirigente e segretario): importo di fantasia, nessuna norma
    fascia: str | None = None  # fascia del segretario (A, B, C), da atto

    @property
    def cognome(self) -> str:
        return "PROVA"

    @property
    def cf(self) -> str:
        return codice_fiscale(self.cognome, self.nome, self.nascita.year, self.nascita.month, self.nascita.day)

    @property
    def dipendente(self) -> bool:
        """Lavoro dipendente con un inquadramento nel registro: comparto, dirigente, segretario."""
        return self.area is not None

    @property
    def comparto(self) -> bool:
        return self.titolo == "comparto"


POSIZIONE_DIRIGENTE = "20000.00"  # posizione annua di fantasia, non una norma
POSIZIONE_SEGRETARIO = "12000.00"

RAPPORTI = (
    Rapporto("R01", "P01", "ALFA", "comparto", "funzionario a tempo pieno, mese intero (il caso base)",
             date(1975, 3, 12), date(2019, 1, 1), "funzionari", "3"),
    Rapporto("R02", "P02", "BETA", "comparto", "arretrato: progressione ad area funzionari con decorrenza dal 01/02, atto di marzo",
             date(1982, 7, 5), date(2019, 1, 1), "istruttori", "3"),
    Rapporto("R03", "P03", "GAMMA", "comparto", "performance 2025 di competenza dell'anno prima, pagata a marzo",
             date(1979, 11, 23), date(2019, 1, 1), "operatori_esperti", "3"),
    Rapporto("R04", "P04", "DELTA", "comparto", "tempo parziale (60%)",
             date(1986, 2, 17), date(2019, 1, 1), "operatori", "3", detrazioni=False),
    Rapporto("R05", "P05", "EPSILON", "comparto", "cessa il 14/03, a meta' mese",
             date(1965, 9, 30), date(2019, 1, 1), "istruttori", "3", al=date(2026, 3, 14)),
    Rapporto("R06", "P06", "ZETA", "comparto", "assunto il 16/03, regime TFR",
             date(1996, 5, 8), date(2026, 3, 16), "operatori_esperti", "1", detrazioni=False),
    Rapporto("R07", "P07", "ETA", "comparto", "rimborso 730 a dicembre (730-4 dal primo pagamento utile da luglio)",
             date(1990, 12, 2), date(2019, 1, 1), "istruttori", "3"),
    Rapporto("R08", "P08", "TETA", "dirigente", "dirigente a tempo pieno, tabellare su 13 mensilita' e posizione da atto",
             date(1970, 4, 14), date(2019, 1, 1), "dirigente", "1", posizione=POSIZIONE_DIRIGENTE),
    Rapporto("R09", "P09", "IOTA", "segretario", "segretario comunale in fascia B, posizione da atto",
             date(1968, 6, 21), date(2019, 1, 1), "segretario", "1", posizione=POSIZIONE_SEGRETARIO, fascia="B"),
    Rapporto("R10", "P10", "KAPPA", "sindaco",
             "sindaco, lavoratore autonomo iscritto alla gestione separata senza altra cassa: indennita' e quota dell'art. 86",
             date(1972, 10, 9), date(2024, 6, 10)),
    Rapporto("R11", "P11", "LAMBDA", "co.co.co.",
             "collaboratore coordinato e continuativo, senza altra cassa: rata di marzo attestata, rata di dicembre no",
             date(1988, 1, 27), date(2026, 1, 1)),
    Rapporto("R12", "P12", "OMICRON", "comparto", "tempo determinato part-time verticale 50% in sostituzione (tipo impiego 18)",
             date(1991, 5, 19), date(2026, 1, 1), "operatori", "1", al=date(2026, 12, 31), detrazioni=False, impiego="18"),
)

PER_ID = {r.id: r for r in RAPPORTI}

# Importi di fantasia dei fatti che l'Ufficio personale registra: nessuno e' una norma.
MISURA_INDENNITA_SINDACO = "3000.00"  # misura mensile piena dell'indennita' di funzione, deliberata dall'ente
RATA_COCOCO = "1500.00"  # rata del piano di collaborazione
RATA_DI_MARZO = date(2026, 3, 20)  # attestata dal responsabile
RATA_DI_DICEMBRE = date(2026, 12, 10)  # senza attestazione: resta calcolata ma fuori dalla versione
PERFORMANCE_2025 = "600.00"
RIMBORSO_730 = "150.00"
ANNO_REDDITI_730 = 2025  # i redditi dichiarati nel 730 il cui esito (730-4) porta il rimborso
PART_TIME_PERCENTUALE = "60"
PART_TIME_TIPO = "verticale"  # tre giornate su cinque a orario pieno: lunedi', martedi', mercoledi'
TD_PERCENTUALE = "50"
TD_TIPO_PART_TIME = "verticale"  # lunedi', martedi' e mercoledi', tranne una settimana di marzo
TD_SETTIMANA_NON_LAVORATA = (date(2026, 3, 15), date(2026, 3, 21))  # domenica-sabato: interamente senza ore (TipoCopertura D)
TD_TERMINE_PER_SOSTITUZIONE = "si"
TD_PRIMA_ISCRIZIONE_DAL_1996 = "no"
ORE_GIORNATA_PIENA = Decimal("7.2")  # 36 ore settimanali su cinque giorni

# Atti di fantasia: riferimento nel formato ente:<ente>:<tipo>:<data>;<numero>
ATTO_PERFORMANCE = Atto("ente:ente_di_prova:determina:2026-03-04;41", date(2026, 3, 4))
ATTO_PROGRESSIONE = Atto("ente:ente_di_prova:determina:2026-03-05;42", date(2026, 3, 5))
ATTO_RIMBORSO = Atto("ente:ente_di_prova:comunicazione.730:2026-11-30;7304", date(2026, 11, 30))
ATTO_PROGRAMMAZIONE = Atto("ente:ente_di_prova:determina:2026-01-09;43", date(2026, 1, 9))
ATTO_PROGRAMMAZIONE_TD = Atto("ente:ente_di_prova:determina:2026-01-09;44", date(2026, 1, 9))
ATTO_POSIZIONE_DIRIGENTE = Atto("ente:ente_di_prova:determina:2026-01-09;45", date(2026, 1, 9))
ATTO_POSIZIONE_SEGRETARIO = Atto("ente:ente_di_prova:decreto:2026-01-09;46", date(2026, 1, 9))
ATTO_FASCIA_SEGRETARIO = Atto("ente:ente_di_prova:decreto:2026-01-09;47", date(2026, 1, 9))
ATTO_MISURA_INDENNITA = Atto("ente:ente_di_prova:delibera:2026-01-09;48", date(2026, 1, 9))
ATTO_MANDATO = Atto("ente:ente_di_prova:verbale:2024-06-10;1", date(2024, 6, 10))
ATTO_PIANO_DI_RATE = Atto("ente:ente_di_prova:contratto:2026-01-09;49", date(2026, 1, 9))
ATTO_ATTESTAZIONE_MARZO = Atto("ente:ente_di_prova:attestazione:2026-03-17;50", date(2026, 3, 17))
ATTO_DETRAZIONI = Atto("ente:ente_di_prova:dichiarazione.detrazioni:2026-01-09;1", date(2026, 1, 9))


def fatti_inquadramento(r: Rapporto) -> dict[str, str]:
    """I fatti che dicono servizio e inquadramento di un rapporto dipendente (sei per il comparto, meno per dirigente e segretario)."""
    fatti = {
        "tipo_impiego": r.impiego,
        "tipo_servizio": "4",
        "contratto": CONTRATTO_COMPARTO if r.comparto else None,
        "qualifica": QUALIFICHE.get(r.area),
        "area": r.area,
        "regime_fine_servizio": r.regime,
    }
    return {tipo: valore for tipo, valore in fatti.items() if valore is not None}


def programmazione_part_time_2026() -> dict[date, Decimal]:
    """La programmazione annuale di R04: ore per ogni giorno del 2026, zero nei giorni non lavorativi."""
    giorno, fine, ore = date(2026, 1, 1), date(2026, 12, 31), {}
    while giorno <= fine:
        ore[giorno] = ORE_GIORNATA_PIENA if giorno.weekday() < 3 else Decimal(0)
        giorno += timedelta(days=1)
    return ore


def programmazione_td_2026() -> dict[date, Decimal]:
    """La programmazione annuale di R12: tre giorni a settimana a orario pieno, la settimana del 15-21 marzo senza ore."""
    giorno, fine, ore = date(2026, 1, 1), date(2026, 12, 31), {}
    dal, al = TD_SETTIMANA_NON_LAVORATA
    while giorno <= fine:
        lavora = giorno.weekday() < 3 and not dal <= giorno <= al
        ore[giorno] = ORE_GIORNATA_PIENA if lavora else Decimal(0)
        giorno += timedelta(days=1)
    return ore
