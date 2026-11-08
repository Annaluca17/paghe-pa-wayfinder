"""Abbinamento delle righe di proposta agli impegni, regola dell'ADR 0031. Dati fittizi.

Stipendio 1500 e contributo a carico ente 360 (24%) sul corpus di prova: la riga dello stipendio e' 1500, quella del
contributo 360.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese
from paghe.errori import ErroreRegistro
from paghe.impegni import AttoPresupposto
from paghe.proposta import emetti_versione

from materiale_impegni import PIANO, PIANO_ENTE, impegni_capienti, impegno
from materiale_proposta import R, R2, P2, assumi_senza_impegni, corpus_p, stipendio

VALUTA = date(2026, 2, 27)
FEB = Mese(2026, 2)


def emetti(registro, corpus, importi, valuta=VALUTA):
    return emetti_versione(registro, corpus, valuta, importi)


def per_piano(versione):
    return {riga.piano_dei_conti: riga for riga in versione.righe_proposta}


def test_l_impegno_automatico_e_quello_dell_esercizio_della_valuta_con_la_stessa_classificazione(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    impegni_capienti(registro, 2026, 5)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti(registro, corpus_p, importi)
    assert per_piano(versione)[PIANO].impegno == (2026, 5)
    assert per_piano(versione)[PIANO_ENTE].impegno == (2026, 1005)
    assert not [d for d in versione.dati_mancanti if d.tipo == "impegno"]


def test_nello_stesso_esercizio_vince_il_numero_piu_basso(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-9", 9, 2026)
    impegno(registro, "I-3", 3, 2026)
    impegno(registro, "I-7", 7, 2026)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    assert per_piano(emetti(registro, corpus_p, importi))[PIANO].impegno == (2026, 3)


def test_un_impegno_incapiente_cede_il_posto_al_primo_capiente(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-1", 1, 2026, disponibilita="1499.99")  # un centesimo in meno dello stipendio
    impegno(registro, "I-2", 2, 2026, disponibilita="1500")
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    assert per_piano(emetti(registro, corpus_p, importi))[PIANO].impegno == (2026, 2)


def test_un_impegno_con_un_altro_esercizio_non_va_per_l_origine_automatica(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-25", 1, 2025)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti(registro, corpus_p, importi)
    assert per_piano(versione)[PIANO].impegno is None
    (mancante,) = [d for d in versione.dati_mancanti if d.tipo == "impegno" and PIANO in d.soggetto]
    assert mancante.soggetto == f"{PIANO} 01.02"


def test_un_impegno_con_atto_non_va_per_l_origine_automatica(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-A", 1, 2026, atto=AttoPresupposto("sottoscrizione_integrativo", "ente:e:contratto:2026-01-05;1"))
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    assert per_piano(emetti(registro, corpus_p, importi))[PIANO].impegno is None


def test_la_classificazione_deve_essere_completa_anche_nel_programma(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-P", 1, 2026, programma="03")
    impegno(registro, "I-M", 2, 2026, missione="04")
    impegno(registro, "I-C", 3, 2026, piano="U.1.01.01.01.006")
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    assert per_piano(emetti(registro, corpus_p, importi))[PIANO].impegno is None


def test_senza_nessun_impegno_noto_l_impegno_e_un_dato_mancante_e_nessun_rapporto_si_ferma(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    versione = emetti(registro, corpus_p, importi)
    assert versione.fermi == ()
    assert {d.soggetto for d in versione.dati_mancanti if d.tipo == "impegno"} == {f"{PIANO} 01.02", f"{PIANO_ENTE} 01.02"}
    assert versione.rapporti == (R,)


# Capienza e fermi

def test_la_capienza_si_controlla_sulla_riga_intera_e_non_si_spezza_su_due_impegni(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    assumi_senza_impegni(registro, R2, P2)
    impegno(registro, "I-1", 1, 2026, disponibilita="1200")
    impegno(registro, "I-2", 2, 2026, disponibilita="1200")  # 2400 in tutto, ma la riga e' 2000: non basta nessuno dei due
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    with pytest.raises(ErroreRegistro, match="Nessun rapporto da portare"):
        emetti(registro, corpus_p, importi)  # entrambi i rapporti sono nella riga incapiente


def test_se_nessun_impegno_adatto_e_capiente_i_rapporti_della_riga_sono_fermi_col_motivo(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    assumi_senza_impegni(registro, R2, P2, programma="04.06")  # un'altra classificazione: il suo impegno basta
    impegno(registro, "I-1", 1, 2026, disponibilita="1000")
    impegno(registro, "I-2", 2, 2026, disponibilita="100000", missione="04", programma="06")
    impegno(registro, "I-3", 3, 2026, disponibilita="100000", missione="04", programma="06", piano=PIANO_ENTE)
    impegno(registro, "I-4", 4, 2026, disponibilita="100000", piano=PIANO_ENTE)
    importi = stipendio(registro, corpus_p, FEB) + stipendio(registro, corpus_p, FEB, "500", R2)
    orologio.vai(2, 20)
    versione = emetti(registro, corpus_p, importi)
    (fermo,) = versione.fermi
    assert fermo.rapporto == R
    assert PIANO in fermo.motivo and "01.02" in fermo.motivo and "mancano 500" in fermo.motivo
    # il rapporto fermo esce da righe, netti e righe di proposta; l'altro prosegue
    assert versione.rapporti == (R2,)
    assert {riga.rapporto for riga in versione.righe} == {R2}
    assert {(r.missione, r.programma, r.impegno) for r in versione.righe_proposta} == {("04", "06", (2026, 2)), ("04", "06", (2026, 3))}
    assert sum(r.totale for r in per_piano(versione).values()) == Decimal("620.00")  # 500 + 120 di contributo ente


def test_l_importo_mancante_e_quello_dell_impegno_meno_incapiente(registro, corpus_p, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-1", 1, 2026, disponibilita="1000")
    impegno(registro, "I-2", 2, 2026, disponibilita="1400")
    impegno(registro, "I-3", 3, 2026, disponibilita="100000", piano=PIANO_ENTE)
    importi = stipendio(registro, corpus_p, FEB)
    orologio.vai(2, 20)
    with pytest.raises(ErroreRegistro, match="mancano 100"):  # 1500 - 1400
        emetti(registro, corpus_p, importi)


# Origine da atto

TIPO = "sottoscrizione_integrativo"


def atto(tipo=TIPO):
    return AttoPresupposto(tipo, "ente:ente_di_prova:contratto:2026-01-05;1")


@pytest.fixture
def corpus_atto():
    from materiale_proposta import CORPUS_PROPOSTA

    testo = CORPUS_PROPOSTA.replace(
        'piano_dei_conti = "U.1.01.01.01.002"\norigine_impegno = "automatico"',
        f'piano_dei_conti = "U.1.01.01.01.002"\norigine_impegno = "{TIPO}"',
    )
    assert testo != CORPUS_PROPOSTA
    return Corpus.da_toml(testo)


def test_un_impegno_da_atto_vuole_l_atto_di_quel_tipo(registro, corpus_atto, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-0", 1, 2026)  # senza atto: non va
    impegno(registro, "I-1", 2, 2026, atto=atto("altro_tipo"))  # atto di un altro tipo: non va
    impegno(registro, "I-2", 3, 2026, atto=atto())
    importi = stipendio(registro, corpus_atto, FEB)
    orologio.vai(2, 20)
    assert per_piano(emetti(registro, corpus_atto, importi))[PIANO].impegno == (2026, 3)


def test_l_esercizio_della_valuta_precede_i_residui_anche_con_un_numero_piu_alto(registro, corpus_atto, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-25", 1, 2025, atto=atto())
    impegno(registro, "I-26", 90, 2026, atto=atto())
    importi = stipendio(registro, corpus_atto, FEB)
    orologio.vai(2, 20)
    assert per_piano(emetti(registro, corpus_atto, importi))[PIANO].impegno == (2026, 90)


def test_i_residui_si_scorrono_dal_piu_vecchio(registro, corpus_atto, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-25", 1, 2025, atto=atto(), data=date(2025, 6, 1))
    impegno(registro, "I-24", 8, 2024, atto=atto(), data=date(2024, 6, 1))
    impegno(registro, "I-26", 3, 2026, atto=atto(), disponibilita="10")  # l'esercizio della valuta non e' capiente
    importi = stipendio(registro, corpus_atto, FEB)
    orologio.vai(2, 20)
    assert per_piano(emetti(registro, corpus_atto, importi))[PIANO].impegno == (2024, 8)


def test_un_residuo_incapiente_cede_al_residuo_successivo(registro, corpus_atto, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-24", 8, 2024, atto=atto(), disponibilita="100", data=date(2024, 6, 1))
    impegno(registro, "I-25", 1, 2025, atto=atto(), data=date(2025, 6, 1))
    importi = stipendio(registro, corpus_atto, FEB)
    orologio.vai(2, 20)
    assert per_piano(emetti(registro, corpus_atto, importi))[PIANO].impegno == (2025, 1)


def test_un_esercizio_successivo_alla_valuta_non_e_adatto(registro, corpus_atto, orologio):
    assumi_senza_impegni(registro)
    impegno(registro, "I-27", 1, 2027, atto=atto())
    importi = stipendio(registro, corpus_atto, FEB)
    orologio.vai(2, 20)
    versione = emetti(registro, corpus_atto, importi)
    assert per_piano(versione)[PIANO].impegno is None
    assert any(d.tipo == "impegno" and PIANO in d.soggetto for d in versione.dati_mancanti)
