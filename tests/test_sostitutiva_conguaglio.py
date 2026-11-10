"""Sostitutiva sull'accessorio al conguaglio (ticket #96, ADR 0035). Valori e fonti fittizi, numeri di materiale_sostitutiva.

Il conguaglio ricalcola sul reddito vero dell'anno, accessorio compreso. Sopra il limite tutto l'accessorio torna
nell'imponibile ordinario e la sostitutiva gia' trattenuta si scomputa dall'IRPEF dovuta, senza credito.
"""

from decimal import Decimal

from materiale_sostitutiva import BASE, IMPOSTA, corpus_sostitutiva, della_sostitutiva, mese_con_premio
from test_fiscale import assumi

D = Decimal


def anno(registro, orologio, corpus, premi, ultimo_stipendio="1000", stipendi=None):
    """Dodici mesi di stipendio con i premi indicati per mese; l'ultimo pagamento porta il conguaglio."""
    ritenute, fiscali = [], []
    for numero in range(1, 13):
        stipendio = (stipendi or {}).get(numero, ultimo_stipendio if numero == 12 else "1000")
        _, fiscale = mese_con_premio(
            registro, orologio, corpus, numero, stipendio=stipendio, premio=premi.get(numero, "0"), ultimo=numero == 12
        )
        ritenute.append(fiscale.ritenuta.valore)
        fiscali.append(fiscale)
    return fiscali, sum(ritenute, D(0))


def test_sopra_il_limite_l_accessorio_torna_ordinario_e_la_sostitutiva_si_scomputa_dall_irpef(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    # gennaio: 100 di premio a sostitutiva (imposta 15,00); dicembre: 60000 di premio, il reddito vero e' 72100
    fiscali, ritenute = anno(registro, orologio, corpus, {1: "100", 12: "60000"})
    dicembre = fiscali[-1]
    assert della_sostitutiva(fiscali[0], IMPOSTA).valore == D("15.00")
    assert dicembre.sostitutiva[0].istituto == BASE and dicembre.sostitutiva[0].valore == D("-100.00")
    assert [riga.istituto for riga in dicembre.sostitutiva] == [BASE]  # nessun credito sull'imposta
    # IRPEF su 72100: 1000 + 4000 + 0,30 * 42100 = 17630,00; meno ritenute operate e meno i 15,00 di sostitutiva
    assert dicembre.conguaglio.valore == D("17630.00") - ritenute - D("15.00")


def test_sotto_il_limite_la_sostitutiva_spetta_anche_se_il_mese_era_sopra(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    # gennaio: (5000 + 700) * 365 / 31 = 67112,90 sopra il limite, nessuna sostitutiva; reddito vero 5700 + 11000 = 16700
    fiscali, ritenute = anno(registro, orologio, corpus, {1: "700"}, stipendi={1: "5000"})
    assert fiscali[0].sostitutiva == ()
    dicembre = fiscali[-1]
    assert della_sostitutiva(dicembre, BASE).valore == D("700.00")
    assert della_sostitutiva(dicembre, IMPOSTA).valore == D("105.00")
    # imponibile ordinario 16000: 1000 + 0,20 * 6000 = 2200,00
    assert dicembre.conguaglio.valore == D("2200.00") - ritenute


def test_il_conguaglio_applica_il_tetto_sull_accessorio_dell_anno(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    # gennaio sopra il limite per lo stipendio, poi due premi da 600 in giugno e luglio: 800 a sostitutiva
    fiscali, _ = anno(registro, orologio, corpus, {1: "700", 6: "600", 7: "600"}, stipendi={1: "5000"})
    totale_base = sum((riga.valore for f in fiscali for riga in f.sostitutiva if riga.istituto == BASE), D(0))
    totale_imposta = sum((riga.valore for f in fiscali for riga in f.sostitutiva if riga.istituto == IMPOSTA), D(0))
    assert (totale_base, totale_imposta) == (D("800.00"), D("120.00"))


def test_senza_differenza_il_conguaglio_non_aggiunge_righe(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    fiscali, ritenute = anno(registro, orologio, corpus, {1: "500"})
    assert fiscali[-1].sostitutiva == ()
    # imponibile ordinario 12000 (il premio e' a sostitutiva): 1000 + 0,20 * 2000 = 1400,00, senza detrazione
    assert fiscali[-1].conguaglio.valore == D("1400.00") - ritenute


def test_la_rinuncia_non_toglie_la_sostitutiva_gia_applicata_ai_pagamenti_precedenti(registro, orologio):
    from datetime import date

    from paghe import Atto
    from test_fiscale import P

    corpus = corpus_sostitutiva()
    assumi(registro)
    mese_con_premio(registro, orologio, corpus, 1, premio="500")
    registro.registra_rinuncia_sostitutiva(P, date(2026, 2, 1), None, Atto("ente:c_x000:modulo:2026-01-30;1", date(2026, 1, 30)))
    for numero in range(2, 12):
        mese_con_premio(registro, orologio, corpus, numero, premio="500" if numero == 2 else "0")
    _, dicembre = mese_con_premio(registro, orologio, corpus, 12, ultimo=True)
    # l'accessorio dell'anno ammesso e' solo quello di gennaio (500), gia' a sostitutiva: nulla da rettificare
    assert dicembre.sostitutiva == ()
