"""La delega F24EP si usa dal pacchetto, come il resto del nucleo (ticket #54)."""

import paghe

NOMI = (
    "CodiceF24EP", "RegolaScadenzaF24EP", "CalendarioFestivi", "Delega", "DelegaTrasmessa", "RigaDelega",
    "calcola_scadenza", "costruisci_delega", "trasmetti_delega", "annulla_delega", "delega_attiva",
    "leggi_delega_trasmessa", "registra_versamento_delega", "situazione_delega", "crediti_riportati",
    "serializza_f24ep",
)


def test_i_nomi_della_delega_sono_nel_pacchetto():
    for nome in NOMI:
        assert hasattr(paghe, nome), nome
        assert nome in paghe.__all__, nome
