"""ListaPosPA di un rapporto in part-time (ADR 0026, ticket #72; ricerca in docs/research/part-time-lista-pos-pa.md).

Corpus reale CPDEL senza il fermo sul part-time e con dichiarazioni di trattamento fittizie: valori e fonti di
prova. Persone e codici fiscali di fantasia.
"""

import re
from datetime import date
from decimal import Decimal

import pytest

from paghe import Atto, Corpus, Mese, Periodo, lista_pos_pa
from paghe.part_time import registra_programmazione
from test_lista_pos_pa import CORPUS, ENTE, MITTENTE, R, assumi, paga, stipendi
from paghe.uniemens import in_xml

NOVEMBRE = Mese(2026, 11)
ISTITUTI_DEL_COMPARTO = [
    f"{nome}_{area}" for nome in ("tabellare", "comparto") for area in ("funzionari", "istruttori", "operatori_esperti", "operatori")
]


@pytest.fixture(scope="module")
def corpus():
    testo = CORPUS.read_text(encoding="utf-8")
    testo = re.sub(r'\[\[fermo\]\]\nfatto = "part_time".*?\n\n', "", testo, flags=re.S)
    dichiarazioni = "".join(
        f'\n[[part_time]]\nistituto = "{istituto}"\ntrattamento = "proporzionale"\ndal = 2026-01-01\n'
        f'riferimento = "fittizio:part-time"\n'
        for istituto in ISTITUTI_DEL_COMPARTO
    )
    return Corpus.da_toml(testo + dichiarazioni)


def in_part_time(registro, orologio, corpus, tipo, percentuale="60", impiego="8"):
    assumi(registro, senza=("tipo_impiego",))
    registro.registra_codice(R, "tipo_impiego", impiego, date(2026, 1, 1))
    if percentuale is not None:
        registro.registra_fatto(R, "part_time", percentuale, date(2026, 1, 1))
    if tipo is not None:
        registro.registra_codice(R, "tipo_part_time", tipo, date(2026, 1, 1))
    paga(registro, orologio, stipendi(registro, corpus, NOVEMBRE), date(2026, 11, 27))
    return lista_pos_pa(registro, corpus, R, NOVEMBRE)


def test_il_part_time_orizzontale_espone_tipo_e_percentuale_in_millesimi(registro, orologio, corpus):
    vista = in_part_time(registro, orologio, corpus, "orizzontale", "60")
    quadro, = vista.quadri
    assert (quadro.inquadramento.part_time.tipo, quadro.inquadramento.part_time.perc) == ("P", 60000)
    assert vista.trasmissibile


def test_il_part_time_entra_nell_xml_dopo_la_qualifica(registro, orologio, corpus):
    vista = in_part_time(registro, orologio, corpus, "orizzontale", "60")
    xml = in_xml([vista], ENTE, MITTENTE, NOVEMBRE)
    assert re.search(
        r"</Qualifica>\s*<PartTimePA>\s*<TipoPartTime>P</TipoPartTime>\s*<PercPartTime>60000</PercPartTime>\s*"
        r"</PartTimePA>\s*<RegimeFineServizio>",
        xml,
    )


def test_il_tipo_impiego_part_time_senza_part_time_chiede_il_dato(registro, orologio, corpus):
    vista = in_part_time(registro, orologio, corpus, None, None, impiego="8")
    assert {d.fatto for d in vista.mancanti} == {"tipo_part_time", "part_time"}
    assert not vista.trasmissibile


def test_un_part_time_senza_tipo_chiede_il_tipo(registro, orologio, corpus):
    vista = in_part_time(registro, orologio, corpus, None, "60")
    assert [d.fatto for d in vista.mancanti] == ["tipo_part_time"]


def test_un_tipo_ignoto_e_una_bozza_che_lo_nomina(registro, orologio, corpus):
    vista = in_part_time(registro, orologio, corpus, "ciclico", "60")
    assert any("ciclico" in motivo for motivo in vista.bozza)
    assert vista.quadri[0].inquadramento.part_time is None


@pytest.mark.parametrize("percentuale", ["100", "0", "33.3333"])
def test_una_percentuale_orizzontale_non_ammessa_dal_tracciato_e_una_bozza(registro, orologio, corpus, percentuale):
    vista = in_part_time(registro, orologio, corpus, "orizzontale", percentuale)
    assert vista.bozza and not vista.trasmissibile
    assert vista.quadri[0].inquadramento.part_time.perc is None


@pytest.mark.parametrize("tipo", ["verticale", "misto"])
def test_verticale_e_misto_senza_programmazione_chiedono_il_dato_e_non_si_trasmettono(registro, orologio, corpus, tipo):
    vista = in_part_time(registro, orologio, corpus, tipo, "60")
    assert [d.fatto for d in vista.mancanti] == ["programmazione_part_time"]
    assert not vista.trasmissibile
    # Il calcolo e il pagamento sono andati avanti.
    assert vista.quadri[0].importi


ATTO = Atto("fittizio:programmazione", date(2026, 10, 20))


def test_il_verticale_con_zero_giorni_lavorativi_nel_periodo_vale_zero(registro, orologio, corpus):
    registra_programmazione(registro, R, {g: 0 for g in NOVEMBRE.giorni()}, ATTO)
    vista = in_part_time(registro, orologio, corpus, "verticale", "60")
    quadro, = vista.quadri
    assert (quadro.inquadramento.part_time.tipo, quadro.inquadramento.part_time.perc) == ("V", 0)
    assert not vista.mancanti and not vista.bozza and vista.trasmissibile


@pytest.mark.parametrize("tipo", ["verticale", "misto"])
def test_con_lavoro_nel_mese_la_percentuale_mensile_resta_una_bozza_che_nomina_il_caso(registro, orologio, corpus, tipo):
    registra_programmazione(registro, R, {g: (6 if g.weekday() < 5 else 0) for g in NOVEMBRE.giorni()}, ATTO)
    vista = in_part_time(registro, orologio, corpus, tipo, "60")
    assert not vista.mancanti
    motivo, = vista.bozza
    assert "percentuale mensile" in motivo and "non determinata" in motivo
    assert vista.quadri[0].inquadramento.part_time.tipo == tipo[0].upper() and vista.quadri[0].inquadramento.part_time.perc is None


def test_un_cambio_di_tipo_a_meta_mese_apre_due_periodi_dichiarati(registro, orologio, corpus):
    assumi(registro, senza=("tipo_impiego",))
    registro.registra_codice(R, "tipo_impiego", "8", date(2026, 1, 1))
    registro.registra_fatto(R, "part_time", "60", date(2026, 1, 1))
    registro.registra_codice(R, "tipo_part_time", "orizzontale", date(2026, 1, 1), date(2026, 11, 15))
    registro.registra_codice(R, "tipo_part_time", "verticale", date(2026, 11, 16))
    paga(registro, orologio, stipendi(registro, corpus, NOVEMBRE), date(2026, 11, 27))
    vista = lista_pos_pa(registro, corpus, R, NOVEMBRE)
    assert [q.periodo for q in vista.quadri] == [
        Periodo(date(2026, 11, 1), date(2026, 11, 15)),
        Periodo(date(2026, 11, 16), date(2026, 11, 30)),
    ]
