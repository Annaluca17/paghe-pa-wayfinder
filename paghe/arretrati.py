"""Arretrati automatici del rinnovo del CCNL (ADR 0041, ticket #126).

Un importo del CCNL ha una decorrenza e una data di applicabilità (`applicabile_dal` nel corpus). Dal giorno in cui
diventa applicabile, il primo pagamento che lo usa porta anche gli arretrati: per ogni mese di competenza già pagato,
il dovuto alla data di pagamento meno quanto risulta dagli esiti. La vacanza contrattuale già pagata si toglie da sé,
perché il suo importo nel corpus si azzera alla stessa data (art. 35 c. 3 CCNL 28/10/2026) e la sua differenza è
negativa. Una volta pagati gli arretrati le differenze sono zero: il secondo pagamento non li ripete.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .calcolo import Differenza, differenze
from .corpus import Corpus
from .denuncia import CESSAZIONE, _fine_del_servizio, _ultimo_giorno_fino_a
from .modello import Importo, TipoEsito
from .registro import Registro
from .tempo import Mese, in_utc


@dataclass(frozen=True)
class ArretratiCcnl:
    rapporto: str
    valuta: date
    differenze: tuple[Differenza, ...]
    cessazione: date | None  # ultimo giorno di servizio, se il rapporto è cessato alla valuta
    scaglionamenti: tuple[date, ...]  # decorrenze maturate alla cessazione (art. 36 c. 2: contano per TFS e TFR)

    @property
    def cessato(self) -> bool:
        return self.cessazione is not None

    @property
    def totale(self) -> Decimal:
        return sum((d.valore for d in self.differenze), Decimal(0))

    @property
    def pagamento_a_parte(self) -> bool:
        """Per un cessato gli arretrati escono in un pagamento a parte, nella prima elaborazione dopo la firma."""
        return self.cessato and bool(self.differenze)

    @property
    def ricalcolo_fine_servizio(self) -> bool:
        """Segnalazione: la base di TFS o TFR cambia. Il nucleo non rifà la liquidazione."""
        return self.cessato and any(d.valore != 0 for d in self.differenze)

    def importi(self) -> list[Importo]:
        """Le differenze come importi da portare in un esito, una riga per istituto e mese di competenza."""
        return [d.importo() for d in self.differenze]


def arretrati_ccnl(
    registro: Registro,
    corpus: Corpus,
    rapporto: str,
    valuta: date,
    tipo: TipoEsito = TipoEsito.PAGATO,
    noto_al=None,
) -> ArretratiCcnl:
    """Gli arretrati del rapporto da portare nel pagamento di `valuta`: differenza per istituto e mese già pagato."""
    istante = in_utc(noto_al) if noto_al is not None else registro.adesso()
    decorrenze = corpus.decorrenze_con_applicabilita(valuta)
    trovate: list[Differenza] = []
    if decorrenze:
        mese = Mese(decorrenze[0].year, decorrenze[0].month)
        ultimo = Mese(valuta.year, valuta.month)
        while (mese.anno, mese.mese) <= (ultimo.anno, ultimo.mese):
            del_mese = differenze(registro, corpus, rapporto, mese, tipo, istante, valuta)
            # Un mese senza esiti non è un arretrato: è un pagamento ordinario, ancora da fare.
            if any(d.esiti for d in del_mese):
                trovate.extend(del_mese)
            mese = Mese(mese.anno + (mese.mese == 12), mese.mese % 12 + 1)
    cessazione = None
    fine = _ultimo_giorno_fino_a(registro, corpus, rapporto, valuta, istante)
    if fine is not None and fine < valuta:  # il servizio non arriva alla valuta: cessazione o sospensione
        fine, come = _fine_del_servizio(registro, corpus, rapporto, valuta, istante)
        cessazione = fine if come == CESSAZIONE else None
    scaglionamenti = tuple(d for d in decorrenze if cessazione is not None and d <= cessazione)
    return ArretratiCcnl(rapporto, valuta, tuple(trovate), cessazione, scaglionamenti)
