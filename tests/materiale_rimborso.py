"""Materiale dei test del rimborso da 730-4 (ticket #71): il corpus di prova della delega piu' le dichiarazioni del rimborso.

Tutti i riferimenti sono `fittizio:`. Il primo mese utile (luglio) e' un parametro dichiarato dal corpus: nel corpus reale
non c'e', e il rimborso non si calcola.
"""

from datetime import date
from decimal import Decimal

from paghe import Atto, Corpus

from materiale_delega import toml_delega
from materiale_proposta import P, R

ATTO_730_4 = Atto("ente:ente_di_prova:comunicazione.730:2026-06-20;1", date(2026, 6, 20))
ATTO_RETTIFICA = Atto("ente:ente_di_prova:comunicazione.730:2026-07-10;2", date(2026, 7, 10))
LUGLIO = date(2026, 8, 27)  # il pagamento di agosto: dopo il primo mese utile

DICHIARAZIONI_RIMBORSO = '''
[[parametro]]
nome = "rimborso_730_primo_mese"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "7"
riferimento = "fittizio:rimborso-730-primo-mese"

# Il corpus vuole una regola per ogni istituto con una composizione. Questa non scatta mai: l'importo del rimborso
# non nasce da un fatto del rapporto ma dall'esito 730-4 della persona (`rimborso_730_4`).
[[regola]]
istituto = "rimborso_730_4"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:rimborso-730-4"
formula = "fatto.rimborso_730_4_del_rapporto"
maturazione = "periodo"
applica_se = "rimborso_730_4_del_rapporto"

[[composizione]]
istituto = "rimborso_730_4"
dal = 2020-01-01
riferimento = "fittizio:comp-rimborso-730-4"
natura = "rimborso_730"
effetto = "piu"
destinatario = "beneficiario"
canale = "accredito"

[[mappatura]]
istituto = "rimborso_730_4"
sistema = "codice_tributo_f24ep"
codice = "150E"
dal = 2020-01-01
riferimento = "fittizio:mappatura-rimborso-730-4"
'''


def corpus_rimborso(con_parametro: bool = True) -> Corpus:
    testo = toml_delega() + DICHIARAZIONI_RIMBORSO
    if not con_parametro:
        testo = testo.replace('"rimborso_730_primo_mese"', '"altro_parametro"')
    return Corpus.da_toml(testo)
