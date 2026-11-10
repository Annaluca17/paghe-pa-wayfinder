"""Sostitutiva sull'accessorio nel pagamento del mese (ticket #96, ADR 0035). Valori e fonti fittizi.

Numeri di materiale_sostitutiva.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto, Corpus, Mese, attribuisci_reddito, calcola, calcola_fiscale
from paghe.errori import CasoNonModellato, ErroreRegistro

from materiale_sostitutiva import ACCESSORIO, BASE, PREMIO, parametri_sostitutiva, sostitutiva, IMPOSTA, corpus_sostitutiva, della_sostitutiva, mese_con_premio
from test_fiscale import P, R, assumi

D = Decimal


def test_l_accessorio_va_a_sostitutiva_e_non_entra_nella_ritenuta_ordinaria(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    _, fiscale = mese_con_premio(registro, orologio, corpus, 1, premio="500")
    assert della_sostitutiva(fiscale, BASE).valore == D("500.00")
    imposta = della_sostitutiva(fiscale, IMPOSTA)
    assert imposta.valore == D("75.00") and imposta.anno_imposta == 2026
    assert imposta.derivazione.riferimento == "fittizio:sostitutiva"
    # la ritenuta e' quella del solo stipendio di 1000
    assert fiscale.ritenuta.valore == D("116.67")


def test_senza_accessorio_non_c_e_sostitutiva(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    _, fiscale = mese_con_premio(registro, orologio, corpus, 1)
    assert fiscale.sostitutiva == ()


def test_un_istituto_non_dichiarato_accessorio_resta_in_tassazione_ordinaria(registro, orologio):
    corpus = corpus_sostitutiva(accessorio="")
    assumi(registro)
    _, fiscale = mese_con_premio(registro, orologio, corpus, 1, premio="500")
    assert fiscale.sostitutiva == ()
    # 1500 ordinari: imposta 216,67 (vedi test_fiscale)
    assert fiscale.ritenuta.valore == D("216.67")


def test_il_tetto_e_per_persona_e_nell_anno_e_si_esaurisce_sui_pagamenti_successivi(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    mese_con_premio(registro, orologio, corpus, 1, premio="600")
    _, febbraio = mese_con_premio(registro, orologio, corpus, 2, premio="500")
    # restano 200 sugli 800; imposta sul cumulato 800 * 0,15 = 120,00 meno i 90,00 gia' trattenuti
    assert della_sostitutiva(febbraio, BASE).valore == D("200.00")
    assert della_sostitutiva(febbraio, IMPOSTA).valore == D("30.00")
    _, marzo = mese_con_premio(registro, orologio, corpus, 3, premio="100")
    assert marzo.sostitutiva == ()


def test_il_tetto_somma_i_rapporti_della_persona(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    assumi(registro, "RAPPORTO-2")
    mese_con_premio(registro, orologio, corpus, 1, premio="600")
    _, altro = mese_con_premio(registro, orologio, corpus, 2, premio="500", rapporto="RAPPORTO-2")
    assert della_sostitutiva(altro, BASE).valore == D("200.00")
    assert della_sostitutiva(altro, BASE).rapporto == "RAPPORTO-2"


def test_oltre_il_limite_di_reddito_stimato_il_mese_non_ha_sostitutiva(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    # (1000 + 5000) * 365 / 31 = 70645,16 sopra 50.000: l'accessorio resta ordinario
    _, fiscale = mese_con_premio(registro, orologio, corpus, 1, premio="5000")
    assert fiscale.sostitutiva == ()


def test_il_limite_conta_anche_l_accessorio_gia_a_sostitutiva(registro, orologio):
    corpus = corpus_sostitutiva(parametri={"sost_limite": "15000"})
    assumi(registro)
    # gennaio: (600 + 500) * 365 / 31 = 12951,61, dentro
    _, gennaio = mese_con_premio(registro, orologio, corpus, 1, stipendio="600", premio="500")
    assert della_sostitutiva(gennaio, BASE).valore == D("500.00")
    # febbraio: pagato 1100 + 1400 = 2500 * 365 / 59 = 15466,10 sopra 15000; senza i 500 gia' a sostitutiva sarebbe 12372,88
    _, febbraio = mese_con_premio(registro, orologio, corpus, 2, premio="400")
    assert febbraio.sostitutiva == ()


def test_il_dirigente_e_escluso(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    registro.registra_codice(R, "area", "dirigente", date(2026, 1, 1))
    _, fiscale = mese_con_premio(registro, orologio, corpus, 1, premio="500")
    assert fiscale.sostitutiva == ()


def test_il_segretario_con_accessorio_ferma_il_calcolo_con_il_nome_del_caso(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    registro.registra_codice(R, "area", "segretario", date(2026, 1, 1))
    with pytest.raises(CasoNonModellato, match="segretario comunale"):
        mese_con_premio(registro, orologio, corpus, 1, premio="500")


def test_il_segretario_senza_accessorio_non_si_ferma(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    registro.registra_codice(R, "area", "segretario", date(2026, 1, 1))
    _, fiscale = mese_con_premio(registro, orologio, corpus, 1)
    assert fiscale.sostitutiva == ()


def rinuncia(registro, dal, al=None):
    return registro.registra_rinuncia_sostitutiva(P, dal, al, Atto("ente:c_x000:modulo:2026-01-30;1", date(2026, 1, 30)))


def test_dopo_la_rinuncia_l_accessorio_va_a_tassazione_ordinaria_e_i_pagamenti_precedenti_restano(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    _, gennaio = mese_con_premio(registro, orologio, corpus, 1, premio="500")
    rinuncia(registro, date(2026, 2, 1))
    _, febbraio = mese_con_premio(registro, orologio, corpus, 2, premio="500")
    assert della_sostitutiva(gennaio, BASE).valore == D("500.00")
    assert febbraio.sostitutiva == ()


def test_la_rinuncia_ha_una_validita_e_vuole_il_documento_di_origine(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    with pytest.raises(ErroreRegistro, match="documento di origine"):
        registro.registra_rinuncia_sostitutiva(P, date(2026, 2, 1), None, None)
    rinuncia(registro, date(2026, 2, 1), date(2026, 2, 28))  # revocata a marzo
    mese_con_premio(registro, orologio, corpus, 1, premio="100")
    _, febbraio = mese_con_premio(registro, orologio, corpus, 2, premio="100")
    _, marzo = mese_con_premio(registro, orologio, corpus, 3, premio="100")
    assert febbraio.sostitutiva == ()
    assert della_sostitutiva(marzo, BASE).valore == D("100.00")


def test_fuori_dal_2026_non_c_e_sostitutiva(registro, orologio):
    corpus = corpus_sostitutiva()
    assumi(registro)
    _, fiscale = mese_con_premio(registro, orologio, corpus, 6, premio="500", anno=2027)
    assert fiscale.sostitutiva == ()


def test_l_accessorio_a_sostitutiva_e_al_netto_dei_contributi_del_lavoratore(registro, orologio):
    from test_deduzione_fiscale import CONTRIBUTO, DEDUZIONE, contributo
    from test_fiscale import TESTO

    corpus = Corpus.da_toml(
        TESTO + PREMIO + CONTRIBUTO + DEDUZIONE + parametri_sostitutiva() + ACCESSORIO + sostitutiva()
    )
    assumi(registro)
    giorno = date(2026, 1, 27)
    registro.registra_fatto(R, "mensile", "1000", date(2026, 1, 1), date(2026, 1, 31))
    registro.registra_fatto(R, "premio", "500", date(2026, 1, 1), date(2026, 1, 31))
    righe = attribuisci_reddito(corpus, [r for r in calcola(registro, corpus, R, Mese(2026, 1)) if r.istituto != "contributo_lavoratore"], giorno)
    # contributi 150 su 1500 di reddito: la quota del premio e' 500 - 150 * 500 / 1500 = 450,00
    fiscale = calcola_fiscale(registro, corpus, R, [*righe, contributo(righe[0], "150")], giorno)
    assert della_sostitutiva(fiscale, BASE).valore == D("450.00")
    assert della_sostitutiva(fiscale, IMPOSTA).valore == D("67.50")
    # imponibile ordinario 1500 - 150 - 450 = 900, sotto la prima fascia mensile di 833,33 + 66,67 al 20%
    assert fiscale.ritenuta.valore == D("96.67")
