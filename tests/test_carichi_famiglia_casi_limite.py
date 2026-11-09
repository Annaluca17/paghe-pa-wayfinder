"""Casi limite dei carichi di famiglia (ADR 0032, ticket #98), scritti nella rilettura. Dati di fantasia."""

from datetime import date
from decimal import Decimal

from paghe import Mese
from test_carichi_famiglia import CF_FIGLIO, con_carichi, figlio
from test_fiscale import assumi, paga, stipendio

D = Decimal
P2, R2 = "PERSONA-2", "RAPPORTO-2"
CF_2 = "VRDLGU80A01H501Q"


def _secondo_semestre(registro, orologio, corpus):
    """Due persone assunte il 01/07/2026 con lo stesso stipendio: la prima ha un figlio a carico tutto l'anno."""
    conguagli = {}
    for numero in range(7, 13):
        orologio.vai(numero, 1)
        for rapporto in ("RAPPORTO-1", R2):
            righe = stipendio(registro, corpus, Mese(2026, numero), rapporto=rapporto)
            _, fiscale = paga(registro, orologio, corpus, righe, date(2026, numero, 27 if rapporto == "RAPPORTO-1" else 28), rapporto=rapporto, ultimo=numero == 12)
            conguagli[rapporto] = fiscale.conguaglio
    return conguagli


def test_al_conguaglio_contano_solo_i_mesi_con_servizio(registro, orologio):
    corpus = con_carichi()
    assumi(registro, dal=date(2026, 7, 1))
    registro.registra_codice_persona(P2, "codice_fiscale", CF_2, date(1980, 1, 1))
    assumi(registro, rapporto=R2, persona=P2, dal=date(2026, 7, 1))
    figlio(registro, nascita=date(2004, 8, 15), dal=date(2026, 1, 1))  # a carico tutto l'anno, servizio da luglio
    conguagli = _secondo_semestre(registro, orologio, corpus)
    # Ritenute: 50 euro al mese di carichi per sei mesi. Conguaglio: 600 * 6 / 12 = 300, non 600: stesso saldo
    # della persona senza figli, al centesimo.
    assert abs(conguagli["RAPPORTO-1"].valore - conguagli[R2].valore) <= D("0.05")


def test_il_figlio_che_compie_30_anni_esce_dal_mese_del_compleanno(registro, orologio):
    corpus = con_carichi()
    assumi(registro)
    figlio(registro, cf=CF_FIGLIO, nascita=date(1996, 6, 30))  # 30 anni il 30/06/2026: ultimo mese maggio
    ritenute = {}
    for numero in (5, 6):
        orologio.vai(numero, 1)
        righe = stipendio(registro, corpus, Mese(2026, numero))
        _, fiscale = paga(registro, orologio, corpus, righe, date(2026, numero, 27))
        ritenute[numero] = fiscale
    assert ritenute[6].ritenuta.valore - ritenute[5].ritenuta.valore == D("50.00")
    assert ritenute[6].avvisi_di("familiare_fuori_eta")
    assert not ritenute[5].avvisi_di("familiare_fuori_eta")
