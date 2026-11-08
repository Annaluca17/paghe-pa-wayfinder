"""Addizionali al conguaglio dell'anno (ticket #85, ADR 0029): regionale e comunale sull'imponibile fiscale. Dati fittizi.

Numeri nel materiale: su 18000 di imponibile, comune X001 99,00 e regione 98 240,00.
"""

from datetime import date
from decimal import Decimal

import pytest

from paghe.errori import FattoMancante, ParametroMancante

from materiale_addizionali import anno_di_paghe, assumi_a, corpus_addizionali, domicilio, per_istituto
from materiale_proposta import P

D = Decimal


@pytest.fixture
def corpus():
    return corpus_addizionali()


def dovute(fiscale):
    """Le addizionali dovute dell'anno, portate dal conguaglio."""
    return per_istituto(
        d for d in fiscale.conguaglio.derivazione.importi if d.derivazione.maturazione == "addizionale"
    )


def test_il_conguaglio_calcola_le_addizionali_dell_anno_sull_imponibile_fiscale(registro, orologio, corpus):
    assumi_a(registro)
    ultimo = anno_di_paghe(registro, orologio, corpus)[-1]
    d = dovute(ultimo)
    assert d["addizionale_regionale_dovuta"].valore == D("240.00")
    assert d["addizionale_comunale_dovuta"].valore == D("99.00")
    assert {i.anno_imposta for i in d.values()} == {2026}


def test_l_addizionale_dovuta_dice_da_dove_viene(registro, orologio, corpus):
    assumi_a(registro)
    comunale = dovute(anno_di_paghe(registro, orologio, corpus)[-1])["addizionale_comunale_dovuta"]
    derivazione = comunale.derivazione
    assert derivazione.riferimento == "fittizio:addizionali + fittizio:aliquota-comune-x001-2026"
    assert [f.tipo for f in derivazione.fatti] == ["domicilio_fiscale"]
    letti = {p.nome: p for p in derivazione.parametri}
    assert letti["addizionale_comunale.X001.2026.fascia_1.aliquota"].valore == D("0.005")
    assert letti["addizionale_comunale.X001.2026.fascia_2.aliquota"].valore == D("0.008")
    assert letti["addizionale_comunale.X001.2026.fascia_1.fino_a"].riferimento == "fittizio:aliquota-comune-x001-2026"


def test_sopra_la_soglia_l_addizionale_comunale_e_su_tutto_il_reddito(registro, orologio, corpus):
    assumi_a(registro, "X002", "97")
    d = dovute(anno_di_paghe(registro, orologio, corpus)[-1])
    assert (d["addizionale_comunale_dovuta"].valore, d["addizionale_regionale_dovuta"].valore) == (D("108.00"), D("180.00"))


def test_fino_alla_soglia_l_addizionale_comunale_e_zero_e_oltre_e_su_tutto_il_reddito(registro, orologio):
    corpus = corpus_addizionali(franchigia="6000")  # l'IRPEF e' dovuta anche con un reddito basso
    assumi_a(registro, "X002", "97")
    d = dovute(anno_di_paghe(registro, orologio, corpus, importo="1000")[-1])  # reddito 12000: la soglia non e' superata
    assert (d["addizionale_comunale_dovuta"].valore, d["addizionale_regionale_dovuta"].valore) == (D("0.00"), D("120.00"))


def test_appena_sopra_la_soglia_l_addizionale_comunale_si_applica_a_tutto_il_reddito(registro, orologio):
    corpus = corpus_addizionali(franchigia="6000")
    assumi_a(registro, "X002", "97")
    d = dovute(anno_di_paghe(registro, orologio, corpus, importo="1001")[-1])  # reddito 12012: 0,6% = 72,072
    assert d["addizionale_comunale_dovuta"].valore == D("72.07")


def test_senza_domicilio_fiscale_il_calcolo_delle_addizionali_si_ferma_e_lo_nomina(registro, orologio, corpus):
    assumi_a(registro, comune=None)
    with pytest.raises(FattoMancante, match=f"domicilio fiscale.*{P}.*2026"):
        anno_di_paghe(registro, orologio, corpus)


def test_conta_il_domicilio_al_1_gennaio_dell_anno_d_imposta(registro, orologio, corpus):
    assumi_a(registro, comune=None)
    domicilio(registro, dal=date(2026, 6, 1))  # da giugno: al 1° gennaio non c'era
    with pytest.raises(FattoMancante, match="domicilio fiscale"):
        anno_di_paghe(registro, orologio, corpus)


def test_senza_le_aliquote_dell_anno_il_calcolo_si_ferma_e_nomina_comune_e_anno(registro, orologio, corpus):
    assumi_a(registro, "X009", "98")
    with pytest.raises(ParametroMancante, match="comune X009.*2026"):
        anno_di_paghe(registro, orologio, corpus)


def test_se_l_irpef_dell_anno_non_e_dovuta_le_addizionali_sono_zero(registro, orologio, corpus):
    assumi_a(registro)
    d = dovute(anno_di_paghe(registro, orologio, corpus, importo="900")[-1])  # reddito 10800 < franchigia: nessuna IRPEF
    assert (d["addizionale_comunale_dovuta"].valore, d["addizionale_regionale_dovuta"].valore) == (D("0"), D("0"))


def test_senza_la_regola_delle_addizionali_il_conguaglio_resta_quello_di_prima(registro, orologio):
    corpus = corpus_addizionali(con_regola=False)
    assumi_a(registro, comune=None)
    ultimo = anno_di_paghe(registro, orologio, corpus)[-1]
    assert dovute(ultimo) == {} and ultimo.addizionali == ()
