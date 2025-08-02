from typing import List, Optional, Callable, Any, Union
import inspect
import asyncio
import logging
import traceback
import sys
import re
import os
import json
from pathlib import Path
import jon as JON

from .config import DEBUG
from .utils import getLang, loopData
from .exception import GenError, ConfigError


def getLoopchema(
    lang: str,
    strict: bool = False,
):
    strict = strict if type(strict) == bool else False
    elementSchema = JON.ChosenType(lang)
    if strict == True:
        elementSchema = elementSchema.choices(
            getFolderSchema(lang, strict=False),
            getFileSchema(lang),
        ).required()
    else:
        elementSchema = JON.Object(lang).required()
    return JON.Object(lang).struct({
        'type': JON.Enum(lang).choices('loop').required(),
        'target': JON.String(lang).required(),
        'index': JON.String(lang).required(),
        'value': JON.String(lang).required(),
        'config': JON.Object(lang).default({}),
        'element': elementSchema,
    }).required().label('loop')
def getFileSchema(
    lang: str
):
    def pathFileRule(data: any):
        checker1 = (
            (
                'content' in tuple(data.keys()) and
                data['content'] is not None
            ) or (
                'path' in tuple(data.keys()) and
                data['path'] is not None
            )
        )
        if not(checker1 == True):
            return checker1
        checker2 = (
            'path' in tuple(data.keys()) and
            data['path'] is not None and
            not(os.path.isfile(data['path']) == True)
        )
        if checker2 == True:
            return False

        return checker1
    def sanitizeRule(data: any):
        if(
            'path' in tuple(data.keys()) and
            data['path'] is not None and
            os.path.isfile(data['path'])
        ):
            data['content'] = Path(data['path']).read_text(encoding='utf-8')
        return data

    return JON.Object(lang).struct({
        'type': JON.Enum(lang).choices('file').required(),
        'name': JON.String(lang).required(),
        'path': JON.String(lang),
        'content': JON.String(lang),
        'config': JON.Object(lang).default({}),
    }).required().label('file').applyApp(
        name='pathFileRule',
        rule = pathFileRule,
        sanitize = sanitizeRule,
        exception={
            'fr': 'chemin du fichier inexistant ou contenu null',
            'en': 'file path does not exist or null content',
        }[lang]
    )
def getFolderSchema(
    lang: str,
    strict: bool = False,
):
    strict = strict if type(strict) == bool else False
    childrenSchema = JON.Array(lang).min(1)
    if strict == True:
        childrenSchema = childrenSchema.types(
            getFolderSchema(lang, strict=False),
            getFileSchema(lang),
        ).default([])
    else:
        childrenSchema = childrenSchema.types(
            JON.Object(lang).required(),
        )
    return JON.Object(lang).struct({
        'type': JON.Enum(lang).choices('folder').required(),
        'name': JON.String(lang).required(),
        'config': JON.Object(lang).default({}),
        'children': childrenSchema,
    }).required().label('folder')
def getConfigStructElementSchema(
    lang: str,
    strict: bool = False,
):
    strict = strict if type(strict) == bool else False
    fileSchema = getFileSchema(lang)
    folderSchema = getFolderSchema(lang, strict=False)
    loopSchema = getLoopchema(lang, strict=False)
    structSchema = JON.ChosenType(lang).choices(
        loopSchema,
        fileSchema,
        folderSchema,
    )

    return structSchema
def getConfigStructSchema(
    lang: str,
    strict: bool = False,
):
    strict = strict if type(strict) == bool else False
    fileSchema = getFileSchema(lang)
    folderSchema = getFolderSchema(lang, strict=False)
    loopSchema = getLoopchema(lang, strict=False)
    structSchema = JON.Array(lang).types(
        loopSchema,
        fileSchema,
        folderSchema,
    ).min(1).default([])

    return structSchema
def getConfigSchema(
    lang: str,
    strict: bool = False,
):
    strict = strict if type(strict) == bool else False
    structSchema = getConfigStructSchema(
        lang=lang,
        strict=strict,
    )
    return JON.Object(lang).struct({
        'name': JON.String(lang).required(),
        'config': JON.Object(lang).default({}),
        'dest': JON.String(lang).required().default(''),
        'struct': structSchema,
    }).required().label('config')

def checkIntegrityParams(
    data: any,
    lang: str = 'fr',
):
    '''
    Parcourir la structure pour verifier l'integrité des données
    '''
    def checkElement(
        value: any,
        index: int = None,
        key: str = None,
    ):
        schema = getConfigStructElementSchema(
            lang = lang,
            strict=True,
        )
        validation = schema.validate(value)
        error = validation['error']
        # print("[arc-gen.ts] checkIntegrityParams | checkElement - value:: ", value)
        # print("[arc-gen.ts] checkIntegrityParams | checkElement - validation:: ", validation)
        # print("[arc-gen.ts] checkIntegrityParams | checkElement - error:: ", error)
        if error is not None:
            raise GenError(
                ({
                    'fr': f"Erreur au niveau de l'element {str(value)}\n\n{error}",
                    'en': f"Error in the {str(value)} element\n\n{error}",
                })[lang],
                file = __name__,
                debug = DEBUG,
            )
        return value
    def mapAction(
        res: any,
        data: any,
        parents: 'list | tuple',
        parent: 'str | int',
        debug = DEBUG,
    ):
        debug = debug if type(debug) == bool else DEBUG
        if type(res) == dict:
            if (
                parent == 'element' and
                (
                    parents is None or
                    not('config' in parents)
                )
            ):
                res = checkElement(
                    value={keyValue: value for keyValue, value in res.items()},
                )
                res = {keyValue: value for keyValue, value in res.items()}
        elif type(res) in (tuple, list):
            if (
                parent is None or (
                    parent == 'children' and
                    (
                        parents is None or
                        not('config' in parents)
                    )
                )
            ):
                res = [checkElement(
                    value=value,
                    index=indexValue,
                ) for indexValue, value in enumerate(res)]
            # print("[arc-gen.ts] checkIntegrityParams | mapAction - res:: ", res)
            # print("[arc-gen.ts] checkIntegrityParams | mapAction - parent:: ", parent)
        return res
    data = loopData(
        data=data,
        mapFnc=mapAction,
        debug=DEBUG,
    )
    return data

def arcGen(
    name: str,
    config: List[dict],
    lang: str = 'fr',
) -> None:
    '''
    Cette fonction permet de demarrer la generation des fichiers
    '''
    try:
        schema = getConfigSchema(lang)
        print("[arc-gen.ts] initGen | schema.getStruct():: ", schema.getStruct())
        configValidation = schema.validate(config)
        print("[arc-gen.ts] initGen | configValidation:: ", configValidation)
        if not(configValidation['valid'] == True):
            raise ConfigError(
                configValidation['error'],
                file = __name__,
                debug = DEBUG,
            )
        configsGen = configValidation['data']
        # configsGen['struct'] = checkIntegrityParams(configsGen['struct'])
        # print("[arc-gen.ts] initGen | configsGen:: ", configsGen)
    except Exception as err:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]

        error = GenError(
            stack,
            file = __name__,
            debug = DEBUG,
        )
        raise error