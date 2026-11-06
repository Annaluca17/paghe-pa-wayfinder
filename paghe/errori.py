"""Errori del modello. Il calcolo si ferma invece di stimare un importo."""


class ErrorePaghe(Exception):
    """Base di tutti gli errori del modello."""


class ErroreFormula(ErrorePaghe):
    """Formula non ammessa dalla grammatica o non valutabile."""


class ErroreCorpus(ErrorePaghe):
    """Corpus di regole e parametri non valido."""


class ErroreRegistro(ErrorePaghe):
    """Operazione non ammessa sul registro."""


class ErroreCalcolo(ErrorePaghe):
    """Un importo non è determinabile con fatti, regole e parametri disponibili."""


class FattoMancante(ErroreCalcolo):
    """La formula legge un fatto che non esiste nel periodo."""


class ParametroMancante(ErroreCalcolo):
    """Il parametro non ha una vigenza nel periodo."""


class ValiditaNonUniforme(ErroreCalcolo):
    """Un fatto, una regola o un parametro cambia dentro il periodo di competenza."""


class ConcorsoMancante(ErroreCalcolo):
    """Un istituto pagato non dichiara se concorre a una base imponibile."""


class ConcorsoParziale(ErroreCalcolo):
    """Un istituto concorre in parte a una base: il caso non è ancora modellato."""
