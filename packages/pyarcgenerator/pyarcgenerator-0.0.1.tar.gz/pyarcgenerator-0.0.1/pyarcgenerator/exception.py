import logging
import traceback
from pyarcscripts import Error, InternalError, getLang
from .config import DEBUG


defaultMessageInitial = {
    'fr': "une erreur query interne s'est declenchée",
    'en': "an internal query error has occurred",
}

class GenError(Error):
    '''
    Cette classe est genère une exception en cas d'echec lors de la generation des fichiers
    '''
    logType = logging.CRITICAL
    defaultMessage = {
        'fr': "une erreur query interne s'est declenchée",
        'en': "an internal query error has occurred",
    }

class ConfigError(Error):
    '''
    Cette classe est genère une exception en cas d'echec lors de la validation des configurations
    '''
    logType = logging.CRITICAL
    defaultMessage = {
        'fr': "une erreur query interne s'est declenchée",
        'en': "an internal query error has occurred",
    }


def returnTrueExceptionType(
    exception: InternalError,
    ReturnType: type[InternalError] = InternalError,
    traceback: str = None,
):
    '''
    Cette fonction pernet de retourner la veritable exception

        Parameters:
            exception (Error): l'exception de depart
            ReturnType (type[InternalError]): le type d'erreur final
            traceback (str): le message complet d'erreur

        Returns:
            dict: La reponse de la fonction
    '''
    exceptionF = None
    ReturnType = ReturnType if ReturnType in [
        InternalError,
        GenError,
    ] else InternalError
    if(
        type(exception) in [
            InternalError,
            GenError,
        ]
    ):
        exceptionDatas = exception.getDatas()
        exceptionF = ReturnType(
            exceptionDatas['message'],
            lang = exceptionDatas['lang'],
            file = exceptionDatas['filename'],
            displayMessage = exceptionDatas['displayMessage'],
        )
    elif type(exception) == Exception and type(traceback) == str:
        exceptionF = ReturnType(
            traceback,
        )
    else:
        exceptionF = ReturnType(
            defaultMessageInitial,
        )
    return exceptionF