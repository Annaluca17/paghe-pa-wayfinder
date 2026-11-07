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


class RedditoMancante(ErroreCalcolo):
    """Manca la categoria di reddito o l'anno d'imposta di un importo: il calcolo fiscale si ferma (ADR 0015, 0019)."""


class VistaFerma(ErrorePaghe):
    """La vista non si serializza: mancano dati, serve un quadro non prodotto o è una bozza (ADR 0008)."""


class CasoNonModellato(ErroreCalcolo):
    """Situazione reale non ancora modellata come caso: il calcolo si ferma e la nomina (ADR 0005)."""


class ComposizioneMancante(ErrorePaghe):
    """L'istituto di un importo non ha una dichiarazione di composizione: la proposta si ferma, non il calcolo (ADR 0025)."""
