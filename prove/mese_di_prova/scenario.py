"""Lo scenario del mese di prova: un ente fittizio e undici rapporti, ognuno per un caso diverso.

Dati esclusivamente fittizi: nomi, codici fiscali (con il carattere di controllo calcolato, vedi `codici`), IBAN di
prova, nessun ente reale. Lo scenario dice cosa l'Ufficio personale registra e quando; non calcola nulla.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

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

    @property
    def cognome(self) -> str:
        return "PROVA"

    @property
    def cf(self) -> str:
        return codice_fiscale(self.cognome, self.nome, self.nascita.year, self.nascita.month, self.nascita.day)

    @property
    def comparto(self) -> bool:
        return self.area is not None


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
    Rapporto("R08", "P08", "TETA", "dirigente", "dirigente",
             date(1970, 4, 14), date(2019, 1, 1)),
    Rapporto("R09", "P09", "IOTA", "segretario", "segretario comunale",
             date(1968, 6, 21), date(2019, 1, 1)),
    Rapporto("R10", "P10", "KAPPA", "sindaco", "sindaco, mandato di amministratore",
             date(1972, 10, 9), date(2024, 6, 10)),
    Rapporto("R11", "P11", "LAMBDA", "co.co.co.", "collaboratore coordinato e continuativo",
             date(1988, 1, 27), date(2026, 1, 1)),
)

PER_ID = {r.id: r for r in RAPPORTI}

# Importi di fantasia dei fatti che l'Ufficio personale registra: nessuno e' una norma.
COMPENSI_SENZA_REGIME = {"R08": "5000.00", "R09": "4000.00", "R10": "3000.00", "R11": "1500.00"}
PERFORMANCE_2025 = "600.00"
RIMBORSO_730 = "150.00"
PART_TIME_PERCENTUALE = "60"

# Atti di fantasia: riferimento nel formato ente:<ente>:<tipo>:<data>;<numero>
ATTO_PERFORMANCE = Atto("ente:ente_di_prova:determina:2026-03-04;41", date(2026, 3, 4))
ATTO_PROGRESSIONE = Atto("ente:ente_di_prova:determina:2026-03-05;42", date(2026, 3, 5))
ATTO_RIMBORSO = Atto("ente:ente_di_prova:comunicazione.730:2026-11-30;7304", date(2026, 11, 30))
ATTO_DETRAZIONI = Atto("ente:ente_di_prova:dichiarazione.detrazioni:2026-01-09;1", date(2026, 1, 9))


def fatti_inquadramento(r: Rapporto) -> dict[str, str]:
    """I sei fatti che dicono servizio e inquadramento di un rapporto del comparto."""
    return {
        "tipo_impiego": "1",
        "tipo_servizio": "4",
        "contratto": "RALN",
        "qualifica": QUALIFICHE[r.area],
        "area": r.area,
        "regime_fine_servizio": r.regime,
    }
