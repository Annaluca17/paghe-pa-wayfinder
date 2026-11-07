"""Versione di proposta: composizione del pagamento, netto per rapporto, contributi, fisco (ADR 0025). Dati fittizi."""

import sqlite3
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, Periodo, TipoEsito, differenze
from paghe.errori import ComposizioneMancante, ErroreRegistro
from paghe.proposta import (
    AVVISO_PERSONA_ASSENTE,
    Escluso,
    MOTIVO_GIA_PAGATO,
    emetti_versione,
    leggi_versione,
)

from materiale_proposta import (
    CORPUS_PROPOSTA,
    IBAN,
    P,
    P2,
    R,
    R2,
    R3,
    assumi,
    corpus_p,
    corpus_proposta,
    gettone,
    paga,
    per_istituto,
    stipendio,
)

VALUTA = date(2026, 2, 27)
FEB = Mese(2026, 2)


# Righe di composizione

def test_la_versione_porta_righe_collegate_agli_importi_con_la_dichiarazione(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    righe = per_istituto(versione.righe)
    assert set(righe) == {"stipendio", "contributo_lavoratore", "contributo_ente", "ritenuta_irpef"}
    stipendio_riga = righe["stipendio"].importo  # collegata all'importo, mai con un valore riscritto
    assert (stipendio_riga.chiave, stipendio_riga.valore, stipendio_riga.derivazione) == (
        importi[0].chiave, importi[0].valore, importi[0].derivazione
    )
    assert (righe["stipendio"].natura, righe["stipendio"].effetto) == ("retribuzione", "piu")
    assert (righe["stipendio"].destinatario, righe["stipendio"].canale) == ("beneficiario", "accredito")
    assert righe["stipendio"].riferimento == "fittizio:comp-stipendio"
    assert (righe["contributo_lavoratore"].natura, righe["contributo_lavoratore"].effetto) == ("contributo_lavoratore", "meno")
    assert (righe["contributo_lavoratore"].destinatario, righe["contributo_lavoratore"].canale) == ("terzo", "f24ep")
    assert righe["contributo_ente"].effetto == "nessuno"
    assert righe["ritenuta_irpef"].natura == "ritenuta"


def test_gli_importi_di_contributi_e_ritenuta_sono_calcolati_alla_valuta_prevista(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    righe = per_istituto(emetti_versione(registro, corpus_p, VALUTA, importi).righe)
    assert righe["contributo_lavoratore"].importo.valore == Decimal("120.00")
    assert righe["contributo_ente"].importo.valore == Decimal("360.00")
    assert righe["ritenuta_irpef"].importo.valore == Decimal("100.00")
    assert righe["ritenuta_irpef"].importo.anno_imposta == 2026
    assert righe["ritenuta_irpef"].importo.periodo.dal == date(2026, 2, 1)


def test_il_netto_e_per_rapporto_e_il_contributo_a_carico_ente_non_lo_cambia(registro, corpus_p, orologio):
    assumi(registro)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    assert {n.rapporto: n.netto for n in versione.netti} == {R: Decimal("1280"), R2: Decimal("460")}
    assert versione.rapporti == (R, R2)


def test_un_istituto_intermedio_non_entra_nelle_righe(registro, orologio):
    corpus = Corpus.da_toml(
        CORPUS_PROPOSTA.replace(
            '''riferimento = "fittizio:comp-contributo-ente"
natura = "contributo_ente"
effetto = "nessuno"
destinatario = "terzo"
canale = "f24ep"''',
            'riferimento = "fittizio:comp-contributo-ente"\nintermedio = true',
        )
    )
    assumi(registro)
    importi = stipendio(registro, corpus, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert "contributo_ente" not in per_istituto(versione.righe)


def test_la_dichiarazione_assente_ferma_la_proposta_nominando_l_istituto_non_il_calcolo(registro, orologio):
    corpus = Corpus.da_toml(
        CORPUS_PROPOSTA.replace('istituto = "contributo_lavoratore"\ndal = 2020-01-01\nriferimento = "fittizio:comp-', 'istituto = "contributo_lavoratore"\ndal = 2030-01-01\nriferimento = "fittizio:comp-')
    )
    assumi(registro)
    importi = stipendio(registro, corpus, FEB)  # il calcolo non si ferma
    assert importi
    orologio.vai(2, 20)
    with pytest.raises(ComposizioneMancante, match="contributo_lavoratore"):
        emetti_versione(registro, corpus, VALUTA, importi)
    assert registro.versioni_registrate(orologio()) == []


def test_la_dichiarazione_si_sceglie_alla_valuta_prevista(registro, orologio):
    corpus = Corpus.da_toml(
        CORPUS_PROPOSTA.replace(
            'istituto = "stipendio"\ndal = 2020-01-01\nriferimento = "fittizio:comp-stipendio"',
            'istituto = "stipendio"\ndal = 2020-01-01\nal = 2026-02-26\nriferimento = "fittizio:comp-stipendio"',
        )
    )
    assumi(registro)
    importi = stipendio(registro, corpus, FEB)
    orologio.vai(2, 20)
    with pytest.raises(ComposizioneMancante, match="stipendio"):
        emetti_versione(registro, corpus, VALUTA, importi)
    assert emetti_versione(registro, corpus, date(2026, 2, 26), importi)


# Fisco: ritenuta, conguaglio e ultimo pagamento dell'anno

def test_la_ritenuta_usa_l_anno_d_imposta_della_valuta_prevista(registro, corpus_p, orologio):
    """Stipendio di dicembre pagato il 10 gennaio: con la cassa allargata è dell'anno d'imposta prima."""
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(1, 5, 2027)
    righe = per_istituto(emetti_versione(registro, corpus_p, date(2027, 1, 10), importi).righe)
    assert righe["stipendio"].importo.anno_imposta == 2026
    assert righe["ritenuta_irpef"].importo.anno_imposta == 2026
    assert righe["ritenuta_irpef"].importo.periodo.dal == date(2027, 1, 1)


def test_senza_il_fatto_dell_ente_il_conguaglio_resta_una_proiezione(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 6))
    orologio.vai(6, 20)
    versione = emetti_versione(registro, corpus_p, date(2026, 6, 27), importi)
    assert "conguaglio_irpef" not in per_istituto(versione.righe)
    assert [a.tipo for a in versione.avvisi if a.tipo == "proiezione_conguaglio"] == ["proiezione_conguaglio"]
    assert versione.dati_mancanti == ()


def test_la_valuta_uguale_o_successiva_all_ultimo_pagamento_porta_il_conguaglio(registro, corpus_p, orologio):
    assumi(registro)
    paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, Mese(2026, 1), "3000"), date(2026, 1, 27), "pag-gen")
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 18), importi)
    righe = per_istituto(versione.righe)
    # imponibile dell'anno 4500, sotto la franchigia: nessuna imposta; già operato 400 + 100 = 500
    assert righe["conguaglio_irpef"].importo.valore == Decimal("-500.00")
    assert righe["conguaglio_irpef"].importo.periodo == Periodo(date(2026, 1, 1), date(2026, 12, 31))
    assert {n.rapporto: n.netto for n in versione.netti}[R] == Decimal("1780")


def test_una_valuta_successiva_all_ultimo_pagamento_porta_ancora_il_conguaglio(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 28), importi)
    assert "conguaglio_irpef" in per_istituto(versione.righe)


def test_una_valuta_precedente_all_ultimo_pagamento_non_porta_il_conguaglio(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 28))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 18), importi)
    assert "conguaglio_irpef" not in per_istituto(versione.righe)


def test_l_ultimo_pagamento_e_quello_dell_anno_d_imposta_non_di_un_altro(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 6))
    registro.registra_ultimo_pagamento(2025, date(2025, 6, 1))  # fatto di un altro anno d'imposta
    orologio.vai(6, 20)
    versione = emetti_versione(registro, corpus_p, date(2026, 6, 27), importi)
    assert "conguaglio_irpef" not in per_istituto(versione.righe)


def test_la_persona_assente_dall_ultimo_pagamento_riceve_un_avviso(registro, corpus_p, orologio):
    assumi(registro)
    assumi(registro, R2, P2)
    paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, Mese(2026, 1), "1500", R2), date(2026, 1, 27), "pag-p2")
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 18), importi)
    assenti = [a for a in versione.avvisi if a.tipo == AVVISO_PERSONA_ASSENTE]
    assert [(a.persona, a.anno) for a in assenti] == [(P2, 2026)]


def test_nessun_avviso_di_assenza_se_il_pagamento_non_e_l_ultimo(registro, corpus_p, orologio):
    assumi(registro)
    assumi(registro, R2, P2)
    paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, Mese(2026, 1), "1500", R2), date(2026, 1, 27), "pag-p2")
    importi = stipendio(registro, corpus_p, Mese(2026, 6))
    orologio.vai(6, 20)
    versione = emetti_versione(registro, corpus_p, date(2026, 6, 27), importi)
    assert [a for a in versione.avvisi if a.tipo == AVVISO_PERSONA_ASSENTE] == []


@pytest.mark.parametrize("valuta", [date(2026, 12, 1), date(2026, 12, 31), date(2027, 1, 12)])
def test_senza_il_fatto_dell_ente_tra_il_1_dicembre_e_il_12_gennaio_manca_un_dato(registro, corpus_p, orologio, valuta):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(11, 30, 2026) if valuta.year == 2026 else orologio.vai(1, 5, 2027)
    versione = emetti_versione(registro, corpus_p, valuta, importi)
    (mancante,) = versione.dati_mancanti
    assert mancante.tipo == "ultimo_pagamento_dell_anno"
    assert "2026" in mancante.motivo


def test_il_fatto_dell_ente_toglie_il_dato_mancante(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    orologio.vai(12, 10)
    assert emetti_versione(registro, corpus_p, date(2026, 12, 18), importi).dati_mancanti == ()


def test_fuori_dalla_finestra_di_dicembre_il_fatto_dell_ente_non_serve(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 11))
    orologio.vai(11, 20)
    assert emetti_versione(registro, corpus_p, date(2026, 11, 27), importi).dati_mancanti == ()


# IBAN del beneficiario

def test_senza_iban_il_beneficiario_e_un_dato_mancante(registro, corpus_p, orologio):
    assumi(registro, iban=False)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    (mancante,) = versione.dati_mancanti
    assert (mancante.tipo, mancante.soggetto) == ("iban_beneficiario", P)
    assert versione.righe  # la versione c'è: si invia solo con l'avvertenza


def test_con_l_iban_alla_valuta_prevista_non_manca_nulla(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    assert emetti_versione(registro, corpus_p, VALUTA, importi).dati_mancanti == ()


def test_un_iban_che_vale_dopo_la_valuta_prevista_non_basta(registro, corpus_p, orologio):
    assumi(registro, iban=False)
    registro.registra_iban_persona(P, IBAN, date(2026, 3, 1))
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    assert [m.tipo for m in emetti_versione(registro, corpus_p, VALUTA, importi).dati_mancanti] == ["iban_beneficiario"]


# Netto negativo e fermi per rapporto

def test_il_netto_negativo_ferma_quel_rapporto_e_non_gli_altri(registro, orologio):
    corpus = corpus_proposta(aliquota_lavoratore="0.95")
    assumi(registro)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus, FEB) + stipendio(registro, corpus, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert versione.rapporti == (R2,)
    assert {r.rapporto for r in versione.righe} == {R2}
    (fermo,) = versione.fermi
    assert fermo.rapporto == R
    assert "netto negativo" in fermo.motivo and "-25" in fermo.motivo


def test_se_tutti_i_rapporti_sono_fermi_non_c_e_una_versione(registro, orologio):
    corpus = corpus_proposta(aliquota_lavoratore="0.95")
    assumi(registro)
    importi = stipendio(registro, corpus, FEB)
    orologio.vai(2, 20)
    with pytest.raises(ErroreRegistro, match="netto negativo"):
        emetti_versione(registro, corpus, VALUTA, importi)
    assert registro.versioni_registrate(orologio()) == []


def test_un_caso_non_modellato_del_fisco_ferma_il_rapporto_e_lo_nomina(registro, corpus_p, orologio):
    assumi(registro)
    assumi(registro, R3, "PERSONA-3")
    importi = stipendio(registro, corpus_p, FEB) + gettone(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    assert versione.rapporti == (R,)
    (fermo,) = versione.fermi
    assert fermo.rapporto == R3 and "carica_elettiva" in fermo.motivo


def test_un_rapporto_senza_legame_con_la_persona_e_fermo(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "800", "RAPPORTO-9")
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    (fermo,) = versione.fermi
    assert fermo.rapporto == "RAPPORTO-9" and "legame con la persona" in fermo.motivo


def test_due_rapporti_della_stessa_persona_nella_stessa_versione_fermano_il_calcolo_fiscale(registro, corpus_p, orologio):
    """La ritenuta è per persona e per pagamento: sommare i due rapporti non è ancora modellato."""
    assumi(registro)
    assumi(registro, R2, P)
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    with pytest.raises(ErroreRegistro, match="più rapporti della stessa persona"):
        emetti_versione(registro, corpus_p, VALUTA, importi)


# Esclusi e importi già pagati

def test_gli_esclusi_restano_visibili_con_il_motivo(registro, corpus_p, orologio):
    assumi(registro)
    assumi(registro, R2, P2)
    importi = stipendio(registro, corpus_p, FEB)
    in_attesa = stipendio(registro, corpus_p, FEB, "900", R2)[0]
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi, esclusi=[Escluso(in_attesa, "in attesa d'atto")])
    assert versione.rapporti == (R,)
    (escluso,) = versione.esclusi
    assert (escluso.importo, escluso.motivo) == (in_attesa, "in attesa d'atto")


def test_un_importo_gia_in_un_esito_pagato_non_entra_e_resta_tra_gli_esclusi(registro, corpus_p, orologio):
    assumi(registro)
    febbraio = stipendio(registro, corpus_p, FEB)
    paga(registro, corpus_p, orologio, febbraio, VALUTA, "pag-feb")
    marzo = stipendio(registro, corpus_p, Mese(2026, 3))
    orologio.vai(3, 20)
    versione = emetti_versione(registro, corpus_p, date(2026, 3, 27), febbraio + marzo)
    assert {r.importo.periodo.dal.month for r in versione.righe if r.istituto == "stipendio"} == {3}
    (escluso,) = versione.esclusi
    assert escluso.importo == febbraio[0] and escluso.motivo == MOTIVO_GIA_PAGATO


def test_la_differenza_su_un_importo_gia_pagato_entra(registro, corpus_p, orologio):
    assumi(registro)
    paga(registro, corpus_p, orologio, stipendio(registro, corpus_p, FEB), VALUTA, "pag-feb")
    registro.registra_fatto(R, "mensile", "1600", FEB.primo_giorno, FEB.ultimo_giorno)
    (arretrato,) = differenze(registro, corpus_p, R, FEB, TipoEsito.PAGATO)
    orologio.vai(3, 20)
    versione = emetti_versione(registro, corpus_p, date(2026, 3, 27), [arretrato.importo()])
    assert versione.esclusi == ()
    assert per_istituto(versione.righe)["stipendio"].importo.valore == Decimal("100")


# Contributi per differenza

def test_il_secondo_pagamento_dello_stesso_mese_porta_i_contributi_per_differenza(registro, corpus_p, orologio):
    assumi(registro)
    registro.registra_fatto(R, "mensile", "1000", FEB.primo_giorno, FEB.ultimo_giorno)
    primo = paga(registro, corpus_p, orologio, [r for r in _calcola(registro, corpus_p)], date(2026, 2, 20), "pag-1")
    esito_primo = registro.eventi("pagamento_eseguito", orologio())[0].esito_id
    registro.registra_fatto(R, "mensile", "1500", FEB.primo_giorno, FEB.ultimo_giorno)
    (arretrato,) = differenze(registro, corpus_p, R, FEB, TipoEsito.PAGATO)
    orologio.vai(2, 25)
    secondo = emetti_versione(registro, corpus_p, VALUTA, [arretrato.importo()])
    righe = per_istituto(secondo.righe)
    assert righe["contributo_lavoratore"].importo.valore == Decimal("40.00")  # 120 dovuti - 80 già compresi
    assert righe["contributo_ente"].importo.valore == Decimal("120.00")  # 360 dovuti - 240 già compresi
    assert righe["contributo_lavoratore"].importo.esiti_confrontati == (esito_primo,)
    assert primo.righe  # la prima versione porta i contributi interi
    assert per_istituto(primo.righe)["contributo_lavoratore"].importo.valore == Decimal("80.00")


def test_la_ritenuta_del_secondo_pagamento_confronta_l_esito_del_primo(registro, corpus_p, orologio):
    assumi(registro)
    registro.registra_fatto(R, "mensile", "1000", FEB.primo_giorno, FEB.ultimo_giorno)
    paga(registro, corpus_p, orologio, _calcola(registro, corpus_p), date(2026, 2, 20), "pag-1")
    esito_primo = registro.eventi("pagamento_eseguito", orologio())[0].esito_id
    registro.registra_fatto(R, "mensile", "1500", FEB.primo_giorno, FEB.ultimo_giorno)
    (arretrato,) = differenze(registro, corpus_p, R, FEB, TipoEsito.PAGATO)
    orologio.vai(2, 25)
    ritenuta = per_istituto(emetti_versione(registro, corpus_p, VALUTA, [arretrato.importo()]).righe)["ritenuta_irpef"]
    assert ritenuta.importo.valore == Decimal("100.00")  # (1500 - 1000) * 0,20 meno 0 già operato
    assert ritenuta.importo.esiti_confrontati == (esito_primo,)


def test_il_primo_pagamento_del_mese_non_confronta_nessun_esito(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    righe = emetti_versione(registro, corpus_p, VALUTA, importi).righe
    assert all(r.importo.esiti_confrontati == () for r in righe)


def _calcola(registro, corpus):
    from paghe import calcola

    return [r for r in calcola(registro, corpus, R, FEB) if r.istituto == "stipendio"]


# Senza basi nel corpus non ci sono contributi

def test_un_corpus_senza_basi_non_ha_contributi_e_la_versione_si_emette(registro, orologio):
    from conftest import CORPUS_BASE

    corpus = Corpus.da_toml(
        CORPUS_BASE
        + """
[[categoria_reddito]]
nome = "lavoro"
[[categoria_reddito.cassa_allargata]]
dal = 2020-01-01
vale = true
riferimento = "fittizio:cassa"

[[reddito]]
istituto = "compenso"
categoria = "lavoro"
dal = 2020-01-01
riferimento = "fittizio:reddito"

[[ritenuta]]
istituto = "ritenuta_irpef"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:ritenuta"
categorie = ["lavoro"]
detrazione_richiesta = "lavoro"
imposta = "arrotonda(fisco.imponibile * parametro.aliquota, 2)"
detrazione = "0"

[[conguaglio]]
istituto = "conguaglio_irpef"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:conguaglio"

[[composizione]]
istituto = "compenso"
dal = 2020-01-01
riferimento = "fittizio:comp-compenso"
natura = "retribuzione"
effetto = "piu"
destinatario = "beneficiario"
canale = "accredito"

[[composizione]]
istituto = "ritenuta_irpef"
dal = 2020-01-01
riferimento = "fittizio:comp-ritenuta"
natura = "ritenuta"
effetto = "meno"
destinatario = "terzo"
canale = "f24ep"
"""
    )
    assumi(registro)
    registro.registra_fatto(R, "compenso_mensile", "1000", date(2026, 1, 1))
    from paghe import calcola

    importi = [r for r in calcola(registro, corpus, R, FEB) if r.istituto == "compenso"]
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus, VALUTA, importi)
    assert set(per_istituto(versione.righe)) == {"compenso", "ritenuta_irpef"}


# Persistenza append-only e lettura nel tempo

def test_la_versione_si_rilegge_identica(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    assert leggi_versione(registro, versione.id) == versione


def test_una_versione_inesistente_e_un_errore(registro):
    with pytest.raises(ErroreRegistro, match="inesistente"):
        leggi_versione(registro, 99)


def test_le_versioni_sono_immutabili_nel_database(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    from paghe.proposta import conferma_versione

    conferma_versione(registro, versione.id)
    registro.registra_evento("evento-prova", "pagamento_eseguito", {"x": 1}, "adattatore-prova")
    for istruzione in (
        "UPDATE versioni_proposta SET contenuto = '{}'",
        "DELETE FROM versioni_proposta",
        "UPDATE stati_versione SET stato = 'respinta'",
        "DELETE FROM stati_versione",
        "UPDATE eventi_ritorno SET contenuto = '{}'",
        "DELETE FROM eventi_ritorno",
    ):
        with pytest.raises(sqlite3.IntegrityError, match="immutabile"):
            registro._db.execute(istruzione)


def test_una_versione_non_e_nota_prima_di_essere_emessa(registro, corpus_p, orologio):
    assumi(registro)
    importi = stipendio(registro, corpus_p, FEB)
    prima = orologio.vai(2, 10)
    orologio.vai(2, 20)
    versione = emetti_versione(registro, corpus_p, VALUTA, importi)
    assert registro.versioni_registrate(prima) == []
    assert registro.versioni_registrate(orologio()) == [versione.id]


def test_la_versione_legge_i_fatti_noti_all_emissione_non_quelli_successivi(registro, corpus_p, orologio):
    """Il fatto dell'ente registrato dopo l'invio non cambia la versione già emessa."""
    assumi(registro)
    importi = stipendio(registro, corpus_p, Mese(2026, 12))
    orologio.vai(12, 10)
    versione = emetti_versione(registro, corpus_p, date(2026, 12, 18), importi)
    orologio.vai(12, 11)
    registro.registra_ultimo_pagamento(2026, date(2026, 12, 18))
    assert leggi_versione(registro, versione.id).dati_mancanti == versione.dati_mancanti != ()
