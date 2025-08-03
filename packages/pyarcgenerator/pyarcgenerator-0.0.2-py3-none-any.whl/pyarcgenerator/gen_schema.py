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


def getLoopchema(
    lang: str,
    strict: bool = False,
):
    '''
    Retourne le schema l'element de parcours de la structure de la configuration du generateur

        Parameters:
            lang (str): la langue utilisée
            strict (bool): respecter de manière stricte les types de données à fournir

        Returns:
            JON.Object: La reponse de la fonction
    '''
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
        'type': JON.String(lang).enum('loop').required(),
        'target': JON.AnyType(lang).required(),
        'index': JON.String(lang).required().min(1),
        'value': JON.String(lang).required().min(1),
        'config': JON.Object(lang).default({}),
        'element': elementSchema,
    }).required().label('loop')
def getIfchema(
    lang: str,
    strict: bool = False,
):
    '''
    Retourne le schema l'element conditionnel de la structure de la configuration du generateur

        Parameters:
            lang (str): la langue utilisée
            strict (bool): respecter de manière stricte les types de données à fournir

        Returns:
            JON.Object: La reponse de la fonction
    '''
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
        'type': JON.String(lang).enum('if').required(),
        'target': JON.AnyType(lang).required(),
        'config': JON.Object(lang).default({}),
        'element': elementSchema,
    }).required().label('if')
def getFileSchema(
    lang: str
):
    '''
    Retourne le schema du fichier de la structure de la configuration du generateur

        Parameters:
            lang (str): la langue utilisée

        Returns:
            JON.Object: La reponse de la fonction
    '''
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
        'type': JON.String(lang).enum('file').required(),
        'name': JON.String(lang).required(),
        'path': JON.String(lang),
        'content': JON.String(lang),
        'config': JON.Object(lang).default({}),
    }).required().label('file').applyApp(
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
    '''
    Retourne le schema du dossier de la structure de la configuration du generateur

        Parameters:
            lang (str): la langue utilisée
            strict (bool): respecter de manière stricte les types de données à fournir

        Returns:
            JON.Object: La reponse de la fonction
    '''
    strict = strict if type(strict) == bool else False
    childrenSchema = JON.Array(lang).min(1)
    if strict == True:
        childrenSchema = childrenSchema.types(
            getIfchema(lang=lang, strict=True),
            getFolderSchema(lang, strict=False),
            getFileSchema(lang),
        ).default([])
    else:
        childrenSchema = childrenSchema.types(
            JON.Object(lang).required(),
        )
    return JON.Object(lang).struct({
        'type': JON.String(lang).enum('folder').required(),
        'name': JON.String(lang).required(),
        'config': JON.Object(lang).default({}),
        'children': childrenSchema,
    }).required().label('folder')
def getConfigStructElementSchema(
    lang: str,
    strict: bool = False,
):
    '''
    Retourne le schema d'un element de la structure de la configuration du generateur

        Parameters:
            lang (str): la langue utilisée
            strict (bool): respecter de manière stricte les types de données à fournir

        Returns:
            JON.ChosenType: La reponse de la fonction
    '''
    strict = strict if type(strict) == bool else False
    fileSchema = getFileSchema(lang)
    folderSchema = getFolderSchema(lang, strict=strict)
    loopSchema = getLoopchema(lang, strict=strict)
    ifSchema = getIfchema(lang, strict=strict)
    structSchema = JON.ChosenType(lang).choices(
        fileSchema,
        folderSchema,
        loopSchema,
        ifSchema,
    ).label('structElement')

    return structSchema
def getConfigStructSchema(
    lang: str,
    strict: bool = False,
):
    '''
    Retourne le schema de la structure de la configuration du generateur

        Parameters:
            lang (str): la langue utilisée
            strict (bool): respecter de manière stricte les types de données à fournir

        Returns:
            JON.Array: La reponse de la fonction
    '''
    strict = strict if type(strict) == bool else False
    fileSchema = getFileSchema(lang)
    loopSchema = getLoopchema(lang, strict=strict)
    ifSchema = getIfchema(lang, strict=strict)
    folderSchema = getFolderSchema(lang, strict=strict)
    structSchema = JON.Array(lang).types(
        folderSchema,
        fileSchema,
        loopSchema,
        ifSchema,
    ).min(1).default([])

    return structSchema
def getConfigSchema(
    lang: str,
    strict: bool = False,
):
    '''
    Retourne le schema de la configuration du generateur

        Parameters:
            lang (str): la langue utilisée
            strict (bool): respecter de manière stricte les types de données à fournir

        Returns:
            JON.Object: La reponse de la fonction
    '''
    strict = strict if type(strict) == bool else False
    structSchema = getConfigStructSchema(
        lang=lang,
        strict=strict,
    )
    
    def destPathFileRule(data: any):
        return (
            'dest' in tuple(data.keys()) and
            data['dest'] is not None and
            os.path.isdir(data['dest']) == True
        )
    return JON.Object(lang).struct({
        'name': JON.String(lang).required(),
        'config': JON.Object(lang).default({}),
        'dest': JON.String(lang).required().default(''),
        'struct': structSchema,
    }).label('config').applyApp(
        rule = destPathFileRule,
        exception={
            'fr': 'chemin de destination est introuvable',
            'en': 'destination path cannot be found',
        }[lang]
    )
