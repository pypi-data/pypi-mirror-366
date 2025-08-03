import logging
import traceback
from .config import DEBUG
from pyarcscripts import GetLogger, getLang, Error, InternalError, defaultMessageInitial


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
    defaultMessage = defaultMessageInitial

class HashError(Error):
    '''
    Cette classe est genère une exception en cas d'echec lors du hash de chaîne de caractères
    '''
    logType = logging.CRITICAL
    defaultMessage = defaultMessageInitial


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
        HashError,
    ] else InternalError
    if(
        type(exception) in [
            InternalError,
            GenError,
            HashError,
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