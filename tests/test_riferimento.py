from datetime import date

import pytest

from conftest import CORPUS_BASE
from paghe import Atto, Corpus
from paghe.errori import ErroreCorpus, ErroreRegistro
from paghe.riferimento import data_atto, motivo_rifiuto


@pytest.mark.parametrize(
    "riferimento",
    [
        "urn:nir:stato:legge:1995-08-08;335~art2-com18",
        "urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art51-com1",
        "urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art11!vig=2020-01-01",
        "urn:nir:stato:legge:1995-08-08;335~art2@originale",
        "urn:nir:stato:decreto.legislativo:2001-03-30;165~art40bis",
        "urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art51",
        "urn:nir:stato:costituzione:1947-12-27~art36",
        "urn:nir:regione.toscana:legge:2005-02-24;40~art2",
        "ccnl:S105:2022-11-16~art14-com1",
        "ccnl:S105:2022-11-16~tabA",
        "prassi:inps:circolare:2026-01-30;6~par6",
        "prassi:inps:messaggio:2024-02-20;749",
        "prassi:inps:documento.tecnico:2026-09-29;4.33~pag188",
        "prassi:ade:risoluzione:2017-12-13;151-E",
        "prassi:ade:risposta.interpello:2022-09-22;468",
        "prassi:ade:provvedimento:2026-01-15;15707-2026~par1.1",
        "prassi:ade:comunicato.stampa:2026-01-16;sn",
        "ente:c_x000:delibera.cc:2026-03-10;45~art3-com2",
        "ente:c_x000:cci:2025-12-18~art5-com2",
        "fittizio:art-1",
        "prassi:inps:circolare:2026-01-30;6~par6 + urn:nir:stato:legge:1995-08-08;335~art2-com18",
    ],
)
def test_riferimento_valido(riferimento):
    assert motivo_rifiuto(riferimento) is None


@pytest.mark.parametrize(
    "riferimento",
    [
        "",
        " ",
        " fittizio:a",
        "art. 2 L. 335/1995",
        "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1995-08-08;335",
        "urn:nir:stato:legge:1995-13-08;335",
        "urn:nir:stato:legge:1995-08-08",
        "urn:nir:presidente.repubblica:decreto:1986-12-22;917~art11",
        "urn:nir:stato:leggee:1995-08-08;335",
        "urn:nir:stato:legge:1995-08-08;335~art2!vig=2020-13-01",
        "urn:nir:regione.toscana:decreto.legislativo:2005-02-24;40",
        "urn:lex:it:stato:legge:1995-08-08;335",
        "ccnl:S105:2022-11-16~art14!vig=2023-01-01",
        "ccnl:funzioni:2022-11-16",
        "prassi:inps:circolare:2026-01-30",
        "prassi:ade:risoluzione:2017-12-13;151/E",
        "prassi:inail:circolare:2026-01-30;1",
        "prassi:inps:risoluzione:2026-01-30;1",
        "urn:nir:stato:legge:1995-08-08;335~com18-art2",
        "ccnl:S105:2022-11-16~art14-tab1",
        "fittizio:a + testo libero",
        "FITTIZIO: art. 1",
    ],
)
def test_riferimento_rifiutato(riferimento):
    assert motivo_rifiuto(riferimento) is not None


@pytest.mark.parametrize(
    ("riferimento", "attesa"),
    [
        ("ente:c_x000:determina:2026-04-02;118", date(2026, 4, 2)),
        ("ccnl:S105:2022-11-16~art14", date(2022, 11, 16)),
        ("prassi:inps:circolare:2026-01-30;6 + urn:nir:stato:legge:1995-08-08;335", date(2026, 1, 30)),
        ("fittizio:a", None),
    ],
)
def test_data_dell_atto_dalla_prima_citazione(riferimento, attesa):
    assert data_atto(riferimento) == attesa


def test_corpus_rifiuta_riferimento_malformato_su_regola_e_parametro():
    with pytest.raises(ErroreCorpus, match="non valido"):
        Corpus.da_toml(CORPUS_BASE.replace('"fittizio:art-1"', '"art. 1 del contratto"'))
    with pytest.raises(ErroreCorpus, match="non valido"):
        Corpus.da_toml(CORPUS_BASE.replace('"fittizio:fonte-aliquota"', '"https://example.org/x"'))


def test_fatto_rifiuta_atto_malformato_o_con_data_incoerente(registro):
    with pytest.raises(ErroreRegistro, match="non valido"):
        registro.registra_fatto("R", "x", "1", date(2026, 1, 1), atto=Atto("determina 1", date(2026, 1, 1)))
    with pytest.raises(ErroreRegistro, match="non coincide"):
        registro.registra_fatto(
            "R", "x", "1", date(2026, 1, 1), atto=Atto("ente:c_x000:determina:2026-04-02;118", date(2026, 4, 3))
        )
    fatto = registro.registra_fatto(
        "R", "x", "1", date(2026, 1, 1), atto=Atto("ente:c_x000:determina:2026-04-02;118", date(2026, 4, 2))
    )
    assert fatto.atto.riferimento == "ente:c_x000:determina:2026-04-02;118"
