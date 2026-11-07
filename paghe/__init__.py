"""Nucleo del modello alternativo di elaborazione paghe per Enti Locali (ADR 0001)."""

from .calcolo import Differenza, calcola, calcola_annuale, differenze, emetti_esito, spiega
from .corpus import (
    Base,
    Concorso,
    Corpus,
    DichiarazioneComposizione,
    Fermo,
    MappaturaEsterna,
    Massimale,
    Parametro,
    Regola,
    RegoleDenuncia,
    VigenzaParametro,
)
from .fisco import (
    Avviso,
    FiscaleDelPagamento,
    ImponibileFiscale,
    anno_imposta,
    attribuisci_reddito,
    calcola_fiscale,
    conguaglio_per_differenza,
    imponibile_fiscale,
    proiezione_conguaglio,
)
from .denuncia import Denuncia, PeriodoDenuncia, Recupero, calcola_denuncia
from .lista_pos_pa import ListaPosPA, lista_pos_pa
from .modello import Atto, ConcorsoLetto, Derivazione, Esito, Fatto, Importo, Quota, TipoEsito
from .registro import Registro
from .tempo import Mese, Periodo

__all__ = [
    "Atto",
    "Avviso",
    "FiscaleDelPagamento",
    "ImponibileFiscale",
    "anno_imposta",
    "attribuisci_reddito",
    "calcola_fiscale",
    "conguaglio_per_differenza",
    "imponibile_fiscale",
    "proiezione_conguaglio",
    "Base",
    "Concorso",
    "ConcorsoLetto",
    "Corpus",
    "Denuncia",
    "DichiarazioneComposizione",
    "Derivazione",
    "Differenza",
    "Esito",
    "Fermo",
    "Fatto",
    "Importo",
    "ListaPosPA",
    "MappaturaEsterna",
    "Massimale",
    "Mese",
    "Parametro",
    "Periodo",
    "PeriodoDenuncia",
    "Quota",
    "Recupero",
    "Registro",
    "Regola",
    "RegoleDenuncia",
    "TipoEsito",
    "VigenzaParametro",
    "calcola",
    "calcola_annuale",
    "calcola_denuncia",
    "differenze",
    "emetti_esito",
    "lista_pos_pa",
    "spiega",
]
