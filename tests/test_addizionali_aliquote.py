"""Aliquote delle addizionali nel corpus (ticket #85, ADR 0029): per comune e per regione, per anno, a fasce e con soglia.

Valori, comuni e regioni di fantasia: nessuna delibera reale.
Comune X001, 2026: 0,5% fino a 15.000 e 0,8% oltre. Su 18.000: 75,00 + 24,00 = 99,00.
Comune X002, 2026: soglia 12.000 e aliquota unica 0,6%: a 12.000 zero; a 18.000, su tutto il reddito, 108,00.
"""

from decimal import Decimal

import pytest

from paghe import Corpus
from paghe.errori import ErroreCorpus

D = Decimal

ALIQUOTE = '''
[[aliquota_addizionale]]
ente = "comune"
codice = "X001"
anno = 2026
riferimento = "fittizio:delibera-x001"
[[aliquota_addizionale.fascia]]
fino_a = "15000"
aliquota = "0.005"
[[aliquota_addizionale.fascia]]
aliquota = "0.008"

[[aliquota_addizionale]]
ente = "comune"
codice = "X002"
anno = 2026
soglia = "12000"
riferimento = "fittizio:delibera-x002"
[[aliquota_addizionale.fascia]]
aliquota = "0.006"
'''


@pytest.fixture
def corpus():
    return Corpus.da_toml(ALIQUOTE)


def test_le_aliquote_si_cercano_per_ente_codice_e_anno(corpus):
    aliquota = corpus.aliquota_addizionale("comune", "X001", 2026)
    assert aliquota.riferimento == "fittizio:delibera-x001"
    assert [(f.fino_a, f.aliquota) for f in aliquota.fasce] == [(D("15000"), D("0.005")), (None, D("0.008"))]
    assert corpus.aliquota_addizionale("comune", "X001", 2027) is None
    assert corpus.aliquota_addizionale("regione", "X001", 2026) is None


def test_le_fasce_si_applicano_a_scaglioni(corpus):
    assert corpus.aliquota_addizionale("comune", "X001", 2026).su(D("18000")) == D("99.00")
    assert corpus.aliquota_addizionale("comune", "X001", 2026).su(D("10000")) == D("50.00")


def test_sotto_la_soglia_l_addizionale_e_zero_e_sopra_si_applica_a_tutto_il_reddito(corpus):
    aliquota = corpus.aliquota_addizionale("comune", "X002", 2026)
    assert (aliquota.su(D("12000")), aliquota.su(D("18000"))) == (D("0.00"), D("108.00"))


def test_senza_riferimento_il_corpus_non_si_carica():
    senza = ALIQUOTE.replace('riferimento = "fittizio:delibera-x002"\n', "")
    with pytest.raises(ErroreCorpus):
        Corpus.da_toml(senza)


def test_un_corpus_reale_rifiuta_le_aliquote_con_un_riferimento_fittizio():
    with pytest.raises(ErroreCorpus, match="fittizio"):
        Corpus.da_toml(ALIQUOTE, reale=True)


def test_due_aliquote_dello_stesso_comune_e_anno_sono_rifiutate():
    inizio = ALIQUOTE.index("[[aliquota_addizionale]]", ALIQUOTE.index("X002") - 100)
    with pytest.raises(ErroreCorpus, match="X002"):
        Corpus.da_toml(ALIQUOTE + ALIQUOTE[inizio:])


@pytest.mark.parametrize(
    "vecchio, nuovo",
    [
        ('fino_a = "15000"', 'fino_a = "-1"'),  # fascia che finisce sotto zero
        ('aliquota = "0.008"', 'aliquota = "1.5"'),  # aliquota oltre il 100%
        ('ente = "comune"\ncodice = "X001"', 'ente = "provincia"\ncodice = "X001"'),  # ente ignoto
        ('soglia = "12000"', 'soglia = "-5"'),
    ],
)
def test_aliquote_incoerenti_sono_rifiutate(vecchio, nuovo):
    assert vecchio in ALIQUOTE
    with pytest.raises(ErroreCorpus):
        Corpus.da_toml(ALIQUOTE.replace(vecchio, nuovo, 1))


FASCIA_APERTA = '[[aliquota_addizionale.fascia]]\naliquota = "0.008"'


def test_l_ultima_fascia_e_aperta_e_le_altre_crescono():
    chiusa = ALIQUOTE.replace(FASCIA_APERTA, '[[aliquota_addizionale.fascia]]\nfino_a = "20000"\naliquota = "0.008"')
    with pytest.raises(ErroreCorpus, match="ultima fascia"):
        Corpus.da_toml(chiusa)
    non_crescenti = ALIQUOTE.replace(
        FASCIA_APERTA, '[[aliquota_addizionale.fascia]]\nfino_a = "14000"\naliquota = "0.007"\n' + FASCIA_APERTA
    )
    with pytest.raises(ErroreCorpus, match="crescenti"):
        Corpus.da_toml(non_crescenti)


def test_le_aliquote_cambiano_la_versione_del_corpus(corpus):
    altro = Corpus.da_toml(ALIQUOTE.replace('"0.006"', '"0.007"'))
    assert altro.versione != corpus.versione
