from datetime import date
from decimal import Decimal

import pytest

from conftest import CORPUS_BASE
from paghe import Atto, Corpus, Mese, TipoEsito, calcola, differenze, emetti_esito, spiega
from paghe.__main__ import main
from paghe.errori import ErroreCalcolo, ErroreRegistro, FattoMancante, ParametroMancante

R = "RAPPORTO-1"
FEB = Mese(2026, 2)


def per_istituto(importi):
    return {importo.istituto: importo.valore for importo in importi}


def diff(voci):
    return {voce.istituto: voce.valore for voce in voci}


@pytest.fixture
def pagato_febbraio(registro, corpus, orologio):
    """Compenso 1000 dal 01/01, febbraio pagato il 27/02."""
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    orologio.vai(2, 27)
    return emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), calcola(registro, corpus, R, FEB))


def aumento_retroattivo(registro, orologio):
    orologio.vai(3, 15)
    return registro.registra_fatto(
        R,
        "compenso_mensile",
        "1100.00",
        date(2026, 2, 1),
        atto=Atto("FITTIZIO: determina 1", date(2026, 3, 10)),
    )


def test_calcolo_con_dipendenza_tra_importi(registro, corpus):
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    assert per_istituto(calcola(registro, corpus, R, FEB)) == {
        "compenso": Decimal("1000.00"),
        "ritenuta": Decimal("100.00"),
    }


def test_calcolo_riproducibile(registro, corpus):
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    istante = registro.adesso()
    assert calcola(registro, corpus, R, FEB, istante) == calcola(registro, corpus, R, FEB, istante)


def test_rapporti_indipendenti_per_la_stessa_persona(registro, corpus):
    registro.registra_fatto("RAPPORTO-A", "compenso_mensile", "1000", date(2026, 1, 1))
    registro.registra_fatto("RAPPORTO-B", "compenso_mensile", "200", date(2026, 1, 1))
    assert per_istituto(calcola(registro, corpus, "RAPPORTO-B", FEB))["compenso"] == 200


def test_derivazione_fino_a_norma_parametri_e_fatti(registro, corpus):
    fatto = registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    importi = {i.istituto: i for i in calcola(registro, corpus, R, FEB)}
    d = importi["ritenuta"].derivazione

    assert d.riferimento == "FITTIZIO: art. 2"
    assert d.versione_corpus == corpus.versione
    assert d.regola_versione == 1
    assert [p.riferimento for p in d.parametri] == ["FITTIZIO: fonte aliquota"]
    assert [i.istituto for i in d.importi] == ["compenso"]
    assert d.importi[0].derivazione.fatti == (fatto,)


def test_come_risultava_e_dovuto_oggi(registro, corpus, orologio, pagato_febbraio):
    al_pagamento = orologio.ora
    aumento_retroattivo(registro, orologio)
    assert per_istituto(calcola(registro, corpus, R, FEB))["compenso"] == Decimal("1100.00")
    assert per_istituto(calcola(registro, corpus, R, FEB, al_pagamento))["compenso"] == Decimal("1000.00")
    assert per_istituto(calcola(registro, corpus, R, Mese(2026, 1)))["compenso"] == Decimal("1000.00")


def test_arretrato_per_differenza_si_azzera_dopo_il_pagamento(registro, corpus, orologio, pagato_febbraio):
    aumento_retroattivo(registro, orologio)
    voci = differenze(registro, corpus, R, FEB, TipoEsito.PAGATO)
    assert diff(voci) == {"compenso": Decimal("100.00"), "ritenuta": Decimal("10.00")}
    assert all(voce.esiti == (pagato_febbraio.id,) for voce in voci)

    orologio.vai(3, 27)
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 3, 27), [voce.importo() for voce in voci])
    assert esito.righe[0].esiti_confrontati == (pagato_febbraio.id,)
    assert differenze(registro, corpus, R, FEB, TipoEsito.PAGATO) == ()


def test_differenze_come_risultavano_ignorano_esiti_e_fatti_successivi(registro, corpus, orologio, pagato_febbraio):
    al_pagamento = orologio.ora
    aumento_retroattivo(registro, orologio)
    orologio.avanza()
    assert differenze(registro, corpus, R, FEB, TipoEsito.PAGATO, al_pagamento) == ()


def test_dichiarazione_si_sostituisce_e_non_si_somma(registro, corpus, orologio):
    registro.registra_fatto(R, "compenso_mensile", "1000.00", date(2026, 1, 1))
    orologio.vai(2, 27)
    emetti_esito(registro, TipoEsito.DICHIARATO, date(2026, 3, 16), calcola(registro, corpus, R, FEB))
    aumento_retroattivo(registro, orologio)
    assert diff(differenze(registro, corpus, R, FEB, TipoEsito.DICHIARATO))["compenso"] == Decimal("100.00")

    orologio.vai(4, 16)
    nuova = emetti_esito(registro, TipoEsito.DICHIARATO, date(2026, 4, 16), calcola(registro, corpus, R, FEB))
    assert per_istituto(nuova.righe)["compenso"] == Decimal("1100.00")
    assert differenze(registro, corpus, R, FEB, TipoEsito.DICHIARATO) == ()


def test_tipi_di_esito_separati(registro, corpus, orologio, pagato_febbraio):
    voci = differenze(registro, corpus, R, FEB, TipoEsito.DICHIARATO)
    assert diff(voci) == {"compenso": Decimal("1000.00"), "ritenuta": Decimal("100.00")}
    assert differenze(registro, corpus, R, FEB, TipoEsito.PAGATO) == ()


def test_esito_conserva_corpus_regole_e_tempo_dei_fatti(registro, corpus, orologio, pagato_febbraio):
    assert pagato_febbraio.versioni_corpus == {corpus.versione}
    assert pagato_febbraio.versioni_regole == {"compenso": 1, "ritenuta": 1}
    assert pagato_febbraio.noti_al == {orologio.ora}
    assert registro.esito(pagato_febbraio.id) == pagato_febbraio


def test_correzione_di_regola_produce_differenza_senza_toccare_l_esito(registro, corpus, orologio, pagato_febbraio):
    corretto = Corpus.da_toml(
        CORPUS_BASE.replace('"0.10"', '"0.12"').replace(
            'versione = 1\ndal = 2026-01-01\nriferimento = "FITTIZIO: art. 2"',
            'versione = 2\ndal = 2026-01-01\nriferimento = "FITTIZIO: art. 2"',
        )
    )
    assert corretto.versione != corpus.versione
    assert diff(differenze(registro, corretto, R, FEB, TipoEsito.PAGATO)) == {"ritenuta": Decimal("20.00")}

    conservato = registro.esito(pagato_febbraio.id)
    assert conservato.versioni_corpus == {corpus.versione}
    assert conservato.versioni_regole["ritenuta"] == 1
    assert per_istituto(conservato.righe)["ritenuta"] == Decimal("100.00")


def test_nuova_vigenza_non_tocca_i_periodi_precedenti(registro, orologio, pagato_febbraio):
    base = CORPUS_BASE.replace(
        'formula = "arrotonda(importo.compenso * parametro.aliquota, 2)"',
        'formula = "arrotonda(importo.compenso * parametro.aliquota, 2)"\nal = 2026-03-31',
    )
    con_vigenza = Corpus.da_toml(
        base
        + """
[[regola]]
istituto = "ritenuta"
versione = 1
dal = 2026-04-01
riferimento = "FITTIZIO: art. 2 nuovo testo"
formula = "arrotonda(importo.compenso / 2, 2)"
"""
    )
    assert differenze(registro, con_vigenza, R, FEB, TipoEsito.PAGATO) == ()
    assert per_istituto(calcola(registro, con_vigenza, R, Mese(2026, 4)))["ritenuta"] == Decimal("500.00")


def test_fatto_annullato_produce_differenza_negativa_tracciabile(registro, corpus, orologio):
    fatto = registro.registra_fatto(R, "premio", "50", date(2026, 2, 1), date(2026, 2, 28))
    testo = """
[[regola]]
istituto = "premio_prova"
versione = 1
dal = 2026-01-01
riferimento = "FITTIZIO: art. 3"
formula = "fatto.premio"
applica_se = "premio"
"""
    con_premio = Corpus.da_toml(testo)
    orologio.vai(2, 27)
    esito = emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), calcola(registro, con_premio, R, FEB))
    orologio.vai(3, 1)
    registro.annulla_fatto(fatto.id, "attribuito per errore")

    voci = differenze(registro, con_premio, R, FEB, TipoEsito.PAGATO)
    assert diff(voci) == {"premio_prova": Decimal("-50")}
    rettifica = voci[0].importo()
    assert rettifica.valore == Decimal("-50")
    assert rettifica.esiti_confrontati == (esito.id,)
    assert rettifica.derivazione.riferimento == "FITTIZIO: art. 3"


def test_applica_se_esclude_il_rapporto_e_vale_zero_come_dipendenza(registro):
    corpus = Corpus.da_toml(
        """
[[regola]]
istituto = "base"
versione = 1
dal = 2026-01-01
riferimento = "FITTIZIO"
formula = "fatto.compenso"

[[regola]]
istituto = "opzionale"
versione = 1
dal = 2026-01-01
riferimento = "FITTIZIO"
formula = "fatto.extra"
applica_se = "extra"

[[regola]]
istituto = "totale"
versione = 1
dal = 2026-01-01
riferimento = "FITTIZIO"
formula = "importo.base + importo.opzionale"
"""
    )
    registro.registra_fatto(R, "compenso", "100", date(2026, 1, 1))
    assert per_istituto(calcola(registro, corpus, R, FEB)) == {"base": 100, "totale": 100}

    registro.registra_fatto(R, "extra", "5", date(2026, 2, 1), date(2026, 2, 28))
    assert per_istituto(calcola(registro, corpus, R, FEB)) == {"base": 100, "opzionale": 5, "totale": 105}


def test_fatto_mancante_ferma_il_calcolo(registro, corpus):
    with pytest.raises(FattoMancante, match="compenso_mensile"):
        calcola(registro, corpus, R, FEB)


def test_parametro_senza_vigenza_ferma_il_calcolo(registro, corpus):
    registro.registra_fatto(R, "compenso_mensile", "1000", date(2025, 1, 1))
    corpus_senza_regola_limite = Corpus.da_toml(CORPUS_BASE.replace("dal = 2026-01-01\nriferimento", "dal = 2025-01-01\nriferimento"))
    with pytest.raises(ParametroMancante):
        calcola(registro, corpus_senza_regola_limite, R, Mese(2025, 6))


def test_dipendenza_senza_regola_vigente_ferma_il_calcolo(registro):
    corpus = Corpus.da_toml(
        """
[[regola]]
istituto = "a"
versione = 1
dal = 2026-01-01
al = 2026-01-31
riferimento = "FITTIZIO"
formula = "1"

[[regola]]
istituto = "b"
versione = 1
dal = 2026-01-01
riferimento = "FITTIZIO"
formula = "importo.a"
"""
    )
    with pytest.raises(ErroreCalcolo, match="nessuna regola vigente"):
        calcola(registro, corpus, R, FEB)


def test_esito_vuoto_o_con_duplicati_rifiutato(registro, corpus):
    with pytest.raises(ErroreRegistro):
        emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), [])
    registro.registra_fatto(R, "compenso_mensile", "1000", date(2026, 1, 1))
    importo = calcola(registro, corpus, R, FEB)[0]
    with pytest.raises(ErroreRegistro):
        emetti_esito(registro, TipoEsito.PAGATO, date(2026, 2, 27), [importo, importo])


def test_spiegazione_arriva_a_norma_parametro_fatto_e_atto(registro, corpus, orologio, pagato_febbraio):
    aumento_retroattivo(registro, orologio)
    ritenuta = next(i for i in calcola(registro, corpus, R, FEB) if i.istituto == "ritenuta")
    testo = spiega(ritenuta)
    for atteso in (
        "FITTIZIO: art. 2",
        "FITTIZIO: fonte aliquota",
        "FITTIZIO: art. 1",
        "FITTIZIO: determina 1 del 2026-03-10",
        "compenso_mensile = 1100.00",
    ):
        assert atteso in testo


def test_dimostrazione_eseguibile(capsys):
    main()
    uscita = capsys.readouterr().out
    assert "DATI FITTIZI" in uscita
    assert "compenso_prova: dovuto 1100.00 - esitato 1000.00 = 100.00" in uscita
    assert "nessuna differenza" in uscita
    assert "ritenuta_prova: dovuto 132.00 - esitato 110.00 = 22.00" in uscita
