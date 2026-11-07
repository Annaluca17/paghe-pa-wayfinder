"""Invarianti del ciclo proposta, esito e denuncia (ADR 0025). Dati fittizi."""

from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal

from paghe import Mese, TipoEsito, calcola, calcola_denuncia, differenze
from paghe.proposta import (
    ScostamentoContributi,
    emetti_versione,
    leggi_versione,
    registra_pagamento_eseguito,
    segnala_scostamento_contributi,
    stato_versione,
    conferma_versione,
)

from materiale_proposta import R, assumi, corpus_p, corpus_proposta, paga, stipendio

FEB = Mese(2026, 2)
VALUTA = date(2026, 2, 27)


def test_i_contributi_e_le_righe_a_carico_ente_nell_esito_non_cambiano_le_basi_della_denuncia(registro, corpus_p, orologio):
    assumi(registro)
    versione = paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, FEB), VALUTA, "pag-1")
    (esito,) = registro.esiti(TipoEsito.PAGATO, orologio())
    assert {r.istituto for r in esito.righe} >= {"contributo_lavoratore", "contributo_ente", "ritenuta_irpef"}
    (periodo,) = calcola_denuncia(registro, corpus_p, R, FEB).periodi
    assert periodo.base("pens").valore == Decimal("1500")  # solo lo stipendio, non i 480 di contributi
    contributi = {riga.istituto: riga.valore for riga in periodo.contributi}
    nella_versione = {r.istituto: r.importo.valore for r in versione.righe if r.istituto.startswith("contributo")}
    assert contributi == nella_versione


def test_la_denuncia_non_cambia_aggiungendo_l_esito_dei_contributi(registro, corpus_p, orologio):
    """Con gli stessi importi pagati, la denuncia prima e dopo la nascita dell'esito con i contributi coincide nelle basi."""
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    simulata = calcola_denuncia(
        registro, corpus_p, R, FEB, ipotetiche=[replace(i, data_pagamento=VALUTA) for i in importi]
    )
    paga(registro, corpus_p, orologio, importi, VALUTA, "pag-1")
    reale = calcola_denuncia(registro, corpus_p, R, FEB)
    assert [p.base("pens").valore for p in simulata.periodi] == [p.base("pens").valore for p in reale.periodi]
    assert [(c.istituto, c.valore) for c in simulata.periodi[0].contributi] == [
        (c.istituto, c.valore) for c in reale.periodi[0].contributi
    ]


def test_due_pagamenti_dello_stesso_mese_nascono_senza_rompere_il_controllo_dei_doppi(registro, corpus_p, orologio):
    assumi(registro)
    registro.registra_fatto(R, "mensile", "1000", FEB.primo_giorno, FEB.ultimo_giorno)
    paga(registro, corpus_p, orologio, [r for r in calcola(registro, corpus_p, R, FEB) if r.istituto == "stipendio"], date(2026, 2, 20), "pag-1")
    registro.registra_fatto(R, "mensile", "1500", FEB.primo_giorno, FEB.ultimo_giorno)
    (arretrato,) = differenze(registro, corpus_p, R, FEB, TipoEsito.PAGATO)
    paga(registro, corpus_p, orologio, [arretrato.importo()], date(2026, 2, 27), "pag-2")
    primo, secondo = registro.esiti(TipoEsito.PAGATO, orologio())
    contributi = lambda esito: sum(r.valore for r in esito.righe if r.istituto.startswith("contributo"))
    assert (contributi(primo), contributi(secondo)) == (Decimal("320.00"), Decimal("160.00"))
    # la somma dei due esiti è il contributo dovuto sul mese intero: 480 su 1500 pagati
    assert contributi(primo) + contributi(secondo) == Decimal("480.00")
    assert segnala_scostamento_contributi(registro, corpus_p, R, FEB) == ()


# Denuncia e contributi trattenuti: il modello segnala e non corregge

def test_se_la_denuncia_coincide_con_i_contributi_trattenuti_non_segnala_nulla(registro, corpus_p, orologio):
    assumi(registro)
    paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, FEB), VALUTA, "pag-1")
    assert segnala_scostamento_contributi(registro, corpus_p, R, FEB) == ()


def test_se_la_denuncia_non_coincide_la_funzione_lo_segnala_e_non_corregge(registro, corpus_p, orologio):
    assumi(registro)
    paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, FEB), VALUTA, "pag-1")
    esiti_prima = registro.esiti(TipoEsito.PAGATO, orologio())
    nuovo = corpus_proposta(aliquota_lavoratore="0.09")  # un'aliquota diversa da quella con cui si è trattenuto
    scostamenti = segnala_scostamento_contributi(registro, nuovo, R, FEB)
    assert scostamenti == (
        ScostamentoContributi(R, FEB, "contributo_lavoratore", Decimal("135.00"), Decimal("120.00")),
    )
    assert registro.esiti(TipoEsito.PAGATO, orologio()) == esiti_prima  # non corregge
    assert len(registro.eventi("pagamento_eseguito", orologio())) == 1


def test_lo_scostamento_si_legge_a_un_istante(registro, corpus_p, orologio):
    assumi(registro)
    paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, FEB), VALUTA, "pag-1")
    orologio.avanza(3600)
    nuovo = corpus_proposta(aliquota_lavoratore="0.09")
    assert segnala_scostamento_contributi(registro, nuovo, R, FEB, noto_al=orologio())
    # prima del pagamento non c'è nulla di trattenuto né di pagato: nulla da segnalare
    prima = datetime(2026, 1, 2, tzinfo=UTC)
    assert segnala_scostamento_contributi(registro, nuovo, R, FEB, noto_al=prima) == ()


# Lettura bitemporale coerente per versioni, eventi e fatti sull'ente

def test_la_lettura_nel_tempo_e_coerente_per_versioni_eventi_e_fatti_sull_ente(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    prima_di_tutto = orologio()
    orologio.avanza(60)
    registro.registra_codice_ente("denominazione", "Ente di prova", date(2026, 1, 1))
    dopo_il_fatto = orologio()
    orologio.avanza(60)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    dopo_la_versione = orologio()
    orologio.avanza(60)
    conferma_versione(registro, versione.id)
    dopo_la_conferma = orologio()
    orologio.avanza(60)
    registra_pagamento_eseguito(registro, corpus_p, "pag-1", "adattatore-prova", versione.id, VALUTA, [R])
    dopo_il_pagamento = orologio()

    def quadro(noto_al):
        return (
            [f.valore for f in registro.fatti_ente_noti("denominazione", noto_al)],
            registro.versioni_registrate(noto_al),
            [e.chiave for e in registro.eventi("pagamento_eseguito", noto_al)],
            [e.id for e in registro.esiti(TipoEsito.PAGATO, noto_al)],
            list(registro.pagamenti(R, noto_al)),
        )

    assert quadro(prima_di_tutto) == ([], [], [], [], [])
    assert quadro(dopo_il_fatto) == (["Ente di prova"], [], [], [], [])
    assert quadro(dopo_la_versione) == (["Ente di prova"], [versione.id], [], [], [])
    assert quadro(dopo_la_conferma) == (["Ente di prova"], [versione.id], [], [], [])
    assert quadro(dopo_il_pagamento) == (["Ente di prova"], [versione.id], ["pag-1"], [1], [1])
    assert str(stato_versione(registro, versione.id, dopo_la_versione)) == "inviata"
    assert str(stato_versione(registro, versione.id, dopo_la_conferma)) == "confermata"
    assert leggi_versione(registro, versione.id) == versione
