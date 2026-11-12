"""Detrazioni della ritenuta sul reddito annuo proiettato (ADR 0039, ticket #119). Valori e fonti fittizi.

Scaglioni e detrazione dei test di test_fiscale: 10% fino a 10000, 20% fino a 30000, 30% oltre; detrazione annua
1200 ridotta in proporzione fino a 40000. La detrazione del mese è la detrazione annua per giorni del mese / giorni
dell'anno. Il reddito annuo è: pagato prima del mese + imponibile del mese + imponibile ricorrente per i mesi che
restano + tredicesima non ancora pagata.
Imposta lorda di un mese da 1500: 216,67 (scaglioni ragguagliati a mese, come in test_fiscale).
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from paghe import Corpus, Mese, calcola_annuale

from test_fiscale import R, TESTO, assumi, dichiara, paga, stipendio

DETRAZIONE_ANNUA = """arrotonda(
    parametro.detrazione_annua * max(0, parametro.limite_detrazione - fisco.reddito_annuo)
    / parametro.limite_detrazione * fisco.giorni / fisco.giorni_anno, 2)"""

TREDICESIMA = """
[[parametro]]
nome = "divisore_tredicesima"
[[parametro.vigenza]]
dal = 2020-01-01
valore = "365"
riferimento = "fittizio:divisore-tredicesima"

[[reddito]]
istituto = "tredicesima"
categoria = "lavoro_dipendente"
dal = 2020-01-01
riferimento = "fittizio:reddito-tredicesima"

[[regola]]
istituto = "tredicesima"
versione = 1
dal = 2020-01-01
riferimento = "fittizio:tredicesima"
formula = "fatto.mensile"
maturazione = "annuale"
applica_se = "mensile"
conteggio = "calendario"
divisore = "divisore_tredicesima"
decimali = 2

[[concorso]]
istituto = "tredicesima"
basi = ["pens"]
misura = "escluso"
dal = 2020-01-01
riferimento = "fittizio:concorso-tredicesima"
"""


def _corpus(con_tredicesima=False):
    testo = TESTO.replace('maturazione = "evento"\napplica_se = "mensile"', 'maturazione = "periodo"\napplica_se = "mensile"')
    testo = testo.replace(f"detrazione = '''{_vecchia_detrazione(testo)}'''", f"detrazione = '''{DETRAZIONE_ANNUA}'''")
    assert DETRAZIONE_ANNUA in testo
    return Corpus.da_toml(testo + (TREDICESIMA if con_tredicesima else ""))


def _vecchia_detrazione(testo):
    inizio = testo.index("detrazione = '''") + len("detrazione = '''")
    return testo[inizio : testo.index("'''", inizio)]


def _mese(registro, orologio, corpus, numero, importo="1500", extra=()):
    orologio.vai(numero, 1)
    righe = stipendio(registro, corpus, Mese(2026, numero), importo)
    return paga(registro, orologio, corpus, [*righe, *extra], date(2026, numero, 27))


def _ritenuta(imposta, detrazione_annua, giorni):
    return imposta - (detrazione_annua * giorni / 365).quantize(Decimal("0.01"))


@pytest.fixture
def corpus():
    return _corpus()


def test_a_gennaio_il_reddito_annuo_e_il_mese_per_dodici_e_la_detrazione_e_dei_giorni_del_mese(registro, orologio, corpus):
    assumi(registro)
    dichiara(registro, orologio)
    _, fiscale = _mese(registro, orologio, corpus, 1)
    # reddito annuo 18000: detrazione annua 660, di gennaio 660 * 31 / 365
    assert fiscale.ritenuta.valore == Decimal("216.67") - Decimal("56.05")


def test_in_un_mese_centrale_il_pagato_prima_e_la_proiezione_del_resto_dell_anno(registro, orologio, corpus):
    assumi(registro)
    dichiara(registro, orologio)
    for numero in (1, 2, 3):
        _mese(registro, orologio, corpus, numero, "1000")
    _, fiscale = _mese(registro, orologio, corpus, 4)
    # 3 x 1000 + 1500 + 8 x 1500 = 16500: detrazione annua 705, di aprile 705 * 30 / 365
    assert fiscale.ritenuta.valore == Decimal("216.67") - Decimal("57.95")


def test_l_assunto_in_corso_d_anno_conta_i_mesi_dal_primo_pagamento(registro, orologio, corpus):
    assumi(registro, dal=date(2026, 6, 1))
    dichiara(registro, orologio, dal=date(2026, 6, 1))
    _, fiscale = _mese(registro, orologio, corpus, 6)
    # nessun pagato prima: 1500 + 6 x 1500 = 10500, detrazione annua 885, di giugno 885 * 30 / 365
    assert fiscale.ritenuta.valore == Decimal("216.67") - Decimal("72.74")


def test_un_arretrato_pagato_entra_nel_pagato_ma_non_si_proietta_sui_mesi_che_restano(registro, orologio, corpus):
    assumi(registro)
    dichiara(registro, orologio)
    esito, _ = _mese(registro, orologio, corpus, 1)
    (gennaio,) = [riga for riga in registro.esito(esito.id).righe if riga.istituto == "stipendio"]
    arretrato = replace(gennaio, valore=Decimal("300"))
    orologio.vai(2, 1)
    righe = stipendio(registro, corpus, Mese(2026, 2))
    _, fiscale = paga(registro, orologio, corpus, [*righe, arretrato], date(2026, 2, 27))
    # 1500 + (1500 + 300 di arretrato) + 10 x 1500 = 18300: detrazione annua 651, di febbraio 651 * 28 / 365.
    # Imposta lorda di 1800 in un mese: 276,67
    assert fiscale.ritenuta.valore == Decimal("276.67") - Decimal("49.94")


def test_la_tredicesima_gia_pagata_in_parte_si_toglie_dal_residuo(registro, orologio):
    corpus = _corpus(con_tredicesima=True)
    assumi(registro)
    registro.registra_fatto(R, "mensile", "1500", date(2026, 1, 1))
    dichiara(registro, orologio)
    for numero in (1, 2, 3, 4):
        _mese(registro, orologio, corpus, numero)
    orologio.vai(5, 1)
    (annuale,) = calcola_annuale(registro, corpus, R, 2026)
    assert annuale.valore == Decimal("1500.00")
    acconto = replace(annuale, valore=Decimal("500"))
    _mese(registro, orologio, corpus, 5, extra=(acconto,))
    _, fiscale = _mese(registro, orologio, corpus, 6)
    # pagato 5 x 1500 + 500, giugno 1500, 6 x 1500, residuo 1000: 19500, detrazione annua 615, di giugno 615 * 30 / 365
    assert fiscale.ritenuta.valore == Decimal("216.67") - Decimal("50.55")


def test_la_tredicesima_non_pagata_entra_nel_reddito_annuo_di_tutti_i_mesi(registro, orologio):
    corpus = _corpus(con_tredicesima=True)
    assumi(registro)
    registro.registra_fatto(R, "mensile", "1500", date(2026, 1, 1))
    dichiara(registro, orologio)
    _, fiscale = _mese(registro, orologio, corpus, 1)
    # 12 x 1500 + tredicesima 1500 = 19500, detrazione annua 615, di gennaio 615 * 31 / 365
    assert fiscale.ritenuta.valore == Decimal("216.67") - Decimal("52.23")


def test_a_dicembre_il_reddito_annuo_e_il_vero_reddito_dell_anno(registro, orologio):
    corpus = _corpus(con_tredicesima=True)
    assumi(registro)
    registro.registra_fatto(R, "mensile", "1500", date(2026, 1, 1))
    dichiara(registro, orologio)
    for numero in range(1, 12):
        _mese(registro, orologio, corpus, numero)
    orologio.vai(12, 1)
    (annuale,) = calcola_annuale(registro, corpus, R, 2026)
    righe = [*stipendio(registro, corpus, Mese(2026, 12)), annuale]
    _, fiscale = paga(registro, orologio, corpus, righe, date(2026, 12, 27), ultimo=True)
    # 12 x 1500 + 1500 = 19500; nessun mese che resta; imposta lorda di 3000 in un mese = 566,67
    assert fiscale.ritenuta.valore == Decimal("566.67") - Decimal("52.23")


def test_senza_dichiarazione_resta_la_sola_detrazione_automatica_che_non_c_e_nel_corpus_di_prova(registro, orologio, corpus):
    assumi(registro)
    _, fiscale = _mese(registro, orologio, corpus, 3)
    assert fiscale.ritenuta.valore == Decimal("216.67")


def test_il_pagamento_di_gennaio_per_l_anno_prima_non_ha_mesi_che_restano(registro, orologio, corpus):
    """Caso limite: lo stipendio di dicembre pagato il 10 gennaio è dell'anno d'imposta prima (cassa allargata)."""
    assumi(registro)
    dichiara(registro, orologio)
    orologio.vai(1, 5, 2027)
    righe = stipendio(registro, corpus, Mese(2026, 12))
    _, fiscale = paga(registro, orologio, corpus, righe, date(2027, 1, 10))
    # anno d'imposta 2026, nessun mese che resta: reddito annuo 1500, detrazione annua 1155, di gennaio 1155 * 31 / 365
    assert fiscale.ritenuta.anno_imposta == 2026
    assert fiscale.ritenuta.valore == Decimal("216.67") - Decimal("98.10")
