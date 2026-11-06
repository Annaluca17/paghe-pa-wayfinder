"""Nucleo del modello alternativo di elaborazione paghe per Enti Locali (ADR 0001)."""

from .calcolo import Differenza, calcola, calcola_annuale, differenze, emetti_esito, spiega
from .corpus import (
    Base,
    Concorso,
    Corpus,
    Fermo,
    Massimale,
    Parametro,
    Regola,
    RegoleDenuncia,
    VigenzaParametro,
)
from .denuncia import Denuncia, PeriodoDenuncia, Recupero, calcola_denuncia
from .modello import Atto, ConcorsoLetto, Derivazione, Esito, Fatto, Importo, Quota, TipoEsito
from .registro import Registro
from .tempo import Mese, Periodo

__all__ = [
    "Atto",
    "Base",
    "Concorso",
    "ConcorsoLetto",
    "Corpus",
    "Denuncia",
    "Derivazione",
    "Differenza",
    "Esito",
    "Fermo",
    "Fatto",
    "Importo",
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
    "spiega",
]
