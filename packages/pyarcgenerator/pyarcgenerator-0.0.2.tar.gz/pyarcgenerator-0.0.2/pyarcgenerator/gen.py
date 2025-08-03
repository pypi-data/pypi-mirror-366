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

from pyarcscripts import getLang, loopData, loopData2, pathsJoin, createFile, createFolder, removeFile, removeFolder
from .config import DEBUG
from .exception import GenError, ConfigError
from .gen_schema import getLoopchema, getIfchema, getFileSchema, getFolderSchema, getConfigStructElementSchema, getConfigStructSchema, getConfigSchema


def checkIntegrityStruct(
    data: any,
    lang: str = 'fr',
    initialConfig: dict = {},
):
    '''
    Parcourir la structure pour verifier l'integrité des données

        Parameters:
            data (dict): la structure de la configuration
            lang (str): la langue utilisée
            initialConfig (dict): les configurations initiales

        Returns:
            dict: La reponse de la fonction
    '''
    initialConfig = initialConfig if type(initialConfig) == dict else {}
    loopSchema = getLoopchema(lang = lang, strict=True)
    ifSchema = getIfchema(lang, strict=True)
    folderSchema = getFolderSchema(lang = lang, strict=True)
    def checkElement(
        value: any,
        index: int = None,
        key: str = None,
        parent = None,
        parents = [],
    ):
        
        schema = getConfigStructElementSchema(
            lang = lang,
            strict=True,
        )
        validation = schema.validate(value)
        error = validation['error']
        # print("[arc-gen.ts] checkIntegrityStruct | checkElement - value:: ", value)
        # print("[arc-gen.ts] checkIntegrityStruct | checkElement - validation:: ", validation)
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
    def cleanLoopIfElement(
        value: any,
        parent = None,
        parents = [],
    ):
        res = value
        if (
            loopSchema.isValid(res) and
            (
                parents is None or
                not('config' in parents)
            )
        ):
            try:
                confRes = res['config'] if (
                    type(res['config']) == dict
                ) else {}
                confRes = {
                    '_initial_config': initialConfig,
                    **confRes,
                }
                # res['config'] = confRes
                import inspect
                targetFunction  = res['target'] if (
                    callable(res['target']) and 
                    len((inspect.getfullargspec(res['target'])).args) == 1
                ) else (lambda conf: conf)
                target = targetFunction(confRes)
                res['target'] = target
                if not(type(res['target']) in (list, tuple)):
                    raise GenError(
                        ({
                            'fr': f"La valeur cible de l'element LOOP `{JON.cleanField(res)}` n'est pas un tableau",
                            'en': f"The target value of the `{JON.cleanField(res)}` loop element is not an array",
                        })[lang],
                        file = __name__,
                        debug = DEBUG,
                    )
            except Exception as err:
                stack = traceback.format_exc()
                raise GenError(
                    ({
                        'fr': f"La fonction permettant de retourner la valeur cible à parcourir de l'element LOOP `{JON.cleanField(res)}` est invalide\n\n{stack}",
                        'en': f"The function used to return the target value of element loop `{JON.cleanField(res)}` is invalid\n\n{stack}",
                    })[lang],
                    file = __name__,
                    debug = DEBUG,
                )
        elif (
            ifSchema.isValid(res) and
            (
                parents is None or
                not('config' in parents)
            )
        ):
            try:
                confRes = res['config'] if (
                    type(res['config']) == dict
                ) else {}
                confRes = {
                    '_initial_config': initialConfig,
                    **confRes,
                }
                # res['config'] = confRes
                import inspect
                targetFunction  = res['target'] if (
                    callable(res['target']) and 
                    len((inspect.getfullargspec(res['target'])).args) == 1
                ) else (lambda conf: conf)
                target = targetFunction(confRes)
                res['target'] = target
                if not(type(res['target']) == bool):
                    raise GenError(
                        ({
                            'fr': f"La valeur cible de l'element IF `{JON.cleanField(res)}` n'est pas un booleen",
                            'en': f"The target value of the `{JON.cleanField(res)}` IF element is not an boolean",
                        })[lang],
                        file = __name__,
                        debug = DEBUG,
                    )
            except Exception as err:
                stack = traceback.format_exc()
                raise GenError(
                    ({
                        'fr': f"La fonction permettant de retourner la valeur cible à parcourir de l'element IF `{JON.cleanField(res)}` est invalide\n\n{stack}",
                        'en': f"The function used to return the target value of element IF `{JON.cleanField(res)}` is invalid\n\n{stack}",
                    })[lang],
                    file = __name__,
                    debug = DEBUG,
                )
        return res
    def cleanConfigFolderElement(
        value: any,
        parent = None,
        parents = [],
    ):
        res = value
        if (
            folderSchema.isValid(res) and
            (
                parents is None or
                not('config' in parents)
            )
        ):
            confRes = res['config'] if (
                type(res['config']) == dict
            ) else {}
            childrenRes = res['children'] if (
                type(res['children']) in (list, tuple)
            ) else []
            childrenRes = [{
                **child,
                'config': {
                    '_parent': confRes,
                    **child['config'],
                },
            } for keyChild, child in enumerate(childrenRes)]

            res['config'] = confRes
            res['children'] = childrenRes
        return res
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
                    parent=parent,
                    parents=parents,
                )
            res = cleanLoopIfElement(
                res,
                parent = parent,
                parents = parents,
            )
            res = cleanConfigFolderElement(
                res,
                parent = parent,
                parents = parents,
            )
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
                    parent=parent,
                    parents=parents,
                ) for indexValue, value in enumerate(res)]
            # print("[arc-gen.ts] checkIntegrityStruct | mapAction - res:: ", res)
            # print("[arc-gen.ts] checkIntegrityStruct | mapAction - parent:: ", parent)
        return res
    data = loopData(
        data=data,
        mapFnc=mapAction,
        debug=DEBUG,
    )
    return data
def bringOutRealConfigStruct(
    data: any,
    lang: str = 'fr',
    initialConfig: dict = {},
):
    '''
    Ressortir les vrais configurations

        Parameters:
            data (dict): la structure de la configuration
            lang (str): la langue utilisée
            initialConfig (dict): les configurations initiales

        Returns:
            dict: La reponse de la fonction
    '''
    initialConfig = initialConfig if type(initialConfig) == dict else {}
    def mapAction(
        res: any,
        data: any,
        parents: 'list | tuple',
        parent: 'str | int',
        debug = DEBUG,
    ):
        debug = debug if type(debug) == bool else DEBUG
        if type(res) == dict:
            if(
                not('config' in parents)
            ):
                res['config'] = {
                    '_initial_config': (initialConfig if type(initialConfig) else {}),
                    **(res['config'] if (
                        type(res) == dict and
                        'config' in tuple(res.keys())
                    ) else {}),
                }
                # print("[arc-gen.ts] bringOutRealConfigStruct | mapAction - res:: ", res)
        elif type(res) in (tuple, list):
            pass
            # print("[arc-gen.ts] bringOutRealConfigStruct | mapAction - res:: ", res)
            # print("[arc-gen.ts] bringOutRealConfigStruct | mapAction - parent:: ", parent)
        return res
    data = loopData(
        data=data,
        mapFnc=mapAction,
        debug=DEBUG,
    )
    return data
def removeLoopAndIfInStruct(
    data: any,
    lang: str = 'fr',
):
    '''
    Retirer les elements `loop` et `if`

        Parameters:
            data (dict): la structure de la configuration
            lang (str): la langue utilisée

        Returns:
            dict: La reponse de la fonction
    '''
    loopSchema = getLoopchema(lang = lang, strict=True)
    ifSchema = getIfchema(lang, strict=True)
    def mapAction(
        res: any,
        data: any,
        parents: 'list | tuple',
        parent: 'str | int',
        debug = DEBUG,
    ):
        debug = debug if type(debug) == bool else DEBUG
        if type(res) == dict:
            if(
                not('config' in parents)
            ):
                pass
                # print("[arc-gen.ts] removeLoopAndIfInStruct | mapAction - res:: ", res)
        elif type(res) in (tuple, list):
            if(
                not('config' in parents)
            ):
                resF = []
                for index, value in enumerate(res):
                    if loopSchema.isValid(value):
                        targetValue = value['target']
                        configValue = value['config']
                        elementValue = value['element']
                        configElementValue = elementValue['config'] if (
                            type(elementValue) == dict and
                            'config' in tuple(elementValue.keys())
                        ) else {}
                        configElementValue = {
                            **configValue,
                            **configElementValue,
                        }
                        valueArray = [{
                            **elementValue,
                            'config': {
                                **configElementValue,
                                value['index']: indexTarget,
                                value['value']: target,
                            },
                        } for indexTarget, target in enumerate(targetValue)]
                        resF = [
                            *resF,
                            *valueArray,
                        ]
                    elif ifSchema.isValid(value):
                        targetValue = value['target']
                        if targetValue:
                            configValue = value['config']
                            elementValue = value['element']
                            configElementValue = elementValue['config'] if (
                                type(elementValue) == dict and
                                'config' in tuple(elementValue.keys())
                            ) else {}
                            configElementValue = {
                                **configValue,
                                **configElementValue,
                            }
                            valueArray = {
                                **elementValue,
                                'config': configElementValue,
                            }
                            resF = [
                                *resF,
                                valueArray,
                            ]
                    else:
                        resF = [
                            *resF,
                            value
                        ]
                res = resF
                # print("[arc-gen.ts] removeLoopAndIfInStruct | mapAction - res:: ", res)
            # print("[arc-gen.ts] removeLoopAndIfInStruct | mapAction - parent:: ", parent)
        return res
    data = loopData(
        data=data,
        mapFnc=mapAction,
        debug=DEBUG,
    )
    return data
def cleanMethods(
    methods: dict = {}
):
    '''
    Permet de verifier si toutes les methodes declarées sont des méthodes

        Returns:
            dict: La reponse de la fonction
    '''
    methods = methods if type(methods) == dict else {}
    methods = {keyMethod: method for keyMethod, method in methods.items() if (
        callable(method)
    )}

    return methods
def defaultMethods():
    '''
    Permet d'initier toutes les méthodes par defaut du generateur'

        Returns:
            dict: La reponse de la fonction
    '''
    def ToLower(value):
        return str(value).lower()
    def ToUpper(value):
        return str(value).upper()
    def Capitalise(value):
        return str(value).capitalize()
    return {
        'ToLower': ToLower,
        'ToUpper': ToUpper,
        'Capitalise': Capitalise,
    }
def compileContentInStruct(
    data: any,
    lang: str = 'fr',
    methods: dict = defaultMethods(),
    initialConfig: dict = {},
    dest: str = None,
):
    '''
    Permet de compiler le contenu de chaque element de type FILE

        Parameters:
            data (dict): la structure de la configuration
            lang (str): la langue utilisée
            dest (str): la destination des fichiers à migrer
            methods (dict): l'ensemble des méthodes qui seront utiliser pour formatter le contenu des fichiers et des dossiers
            initialConfig (dict): la configuration initiale

        Returns:
            dict: La reponse de la fonction
    '''
    initialConfig = initialConfig if type(initialConfig) == dict else {}
    fileSchema = getFileSchema(lang = lang)
    folderSchema = getFolderSchema(lang = lang)
    methods = cleanMethods(methods)
    dest = dest if (
        type(dest) in (str, int, float)
    ) else ''
    def getFinalNameElement(
        value: any,
        parent = None,
        parents = [],
    ):
        # print("\n-----------------")
        # print("[arc-gen.ts] compileContentInStruct | getFinalNameElement - value:: ", value)
        # print("[arc-gen.ts] compileContentInStruct | getFinalNameElement - parent:: ", parent)
        # print("-----------------\n")
        # print("[arc-gen.ts] compileContentInStruct | getFinalNameElement - dest:: ", dest)
        res = value
        if parent is None and type(res) in (list, tuple):
            # print("\n[arc-gen.ts] compileContentInStruct | getFinalNameElement - value:: ", value, "\n")
            res2 = [pathsJoin(dest, child['name']) for keyChild, child in enumerate(res)]
            res = [{
                **child,
                'name': pathsJoin(dest, child['name'])
            } for keyChild, child in enumerate(res)]
            # print("\n[arc-gen.ts] compileContentInStruct | getFinalNameElement - res FIRST:: ", res, "\n")
            # print("\n[arc-gen.ts] compileContentInStruct | getFinalNameElement - res2 FIRST:: ", res2, "\n")
        if (
            not('config' in parents)
        ):
            if folderSchema.isValid(res):
                res['children'] = [{
                    **child,
                    'name': pathsJoin(dest, res['name'], child['name'])
                } for keyChild, child in enumerate(res['children'])]
        return res
    from jinja2 import Environment, Template
    env = Environment()
    for keyMethod, method in methods.items():
        env.globals[keyMethod] = method
    def cleannerMapAction(
        res: any,
        data: any,
        parents: 'list | tuple',
        parent: 'str | int',
        debug = DEBUG,
    ):
        debug = debug if type(debug) == bool else DEBUG
        res = getFinalNameElement(
            value = res,
            parent = parent,
            parents = parents,
        )
        return res
    def mapAction(
        res: any,
        data: any,
        parents: 'list | tuple',
        parent: 'str | int',
        debug = DEBUG,
    ):
        debug = debug if type(debug) == bool else DEBUG
        if type(res) == dict:
            if(
                (
                    folderSchema.isValid(res) or
                    fileSchema.isValid(res)
                ) and
                not('config' in parents)
            ):
                config = {
                    '_initial_config': (initialConfig if type(initialConfig) else {}),
                    **res['config'],
                }
                res['name'] = (env.from_string(res['name'])).render(**config)
                if fileSchema.isValid(res):
                    res['content'] = (env.from_string(res['content'])).render(**config)
                # print("[arc-gen.ts] compileContentInStruct | mapAction - res:: ", res)
        return res
    data = loopData(
        data=data,
        mapFnc=mapAction,
        debug=DEBUG,
    )
    data = loopData2(
        data=data,
        mapFnc=cleannerMapAction,
        debug=DEBUG,
    )
    return data
def generateElements(
    data: any,
    lang: str = 'fr',
    dest: str = None,
):
    '''
    Permet de generer tous les elements

        Parameters:
            data (dict): la structure de la configuration
            lang (str): la langue utilisée
            dest (str): la destination des fichiers à migrer

        Returns:
            dict: La reponse de la fonction
    '''
    try:
        fileSchema = getFileSchema(lang = lang)
        folderSchema = getFolderSchema(lang = lang)
        dest = dest if (
            type(dest) in (str, int, float)
        ) else ''
        
        def mapAction(
            res: any,
            data: any,
            parents: 'list | tuple',
            parent: 'str | int',
            debug = DEBUG,
        ):
            debug = debug if type(debug) == bool else DEBUG
            if fileSchema.isValid(res):
                createFile(
                    res['name'],
                    content = res['content'],
                    remove = False,
                )
            elif folderSchema.isValid(res):
                createFolder(
                    res['name'],
                    remove = False,
                )
            return res
        def removeFileAndFoldermapAction(
            res: any,
            data: any,
            parents: 'list | tuple',
            parent: 'str | int',
            debug = DEBUG,
        ):
            debug = debug if type(debug) == bool else DEBUG
            if folderSchema.isValid(res):
                removeFolder(
                    res['name'],
                )
            elif fileSchema.isValid(res):
                removeFile(
                    res['name'],
                )
            return res
        loopData(
            data=data,
            mapFnc=removeFileAndFoldermapAction,
            debug=DEBUG,
        )
        loopData2(
            data=data,
            mapFnc=mapAction,
            debug=DEBUG,
        )
    except Exception as err:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]

        error = GenError(
            {
                'fr': f'Echec lors de la generation des elements.\n{stack}',
                'fr': f'Failure to generate elements.\n{stack}',
            }[lang],
            file = __name__,
            debug = DEBUG,
        )
        raise error
    

def arcGen(
    name: str,
    config: List[dict],
    methods: dict = defaultMethods(),
    lang: str = 'fr',
) -> None:
    '''
    Cette fonction permet de demarrer la generation des fichiers
    '''
    try:
        lang = JON.getLang(lang)
        schema = getConfigSchema(lang)
        print({
            'fr': '[*] DEMARRAGE DE LA GENERATION DES FICHIERS',
            'en': '[*] STARTING FILE GENERATION',
        }[lang])
        # print("[arc-gen.ts] initGen | schema.getStruct():: ", schema.getStruct())
        configValidation = schema.validate(config)
        # print("[arc-gen.ts] initGen | configValidation:: ", configValidation)
        if not(configValidation['valid'] == True):
            raise ConfigError(
                configValidation['error'],
                file = __name__,
                debug = DEBUG,
            )
        configsGen = configValidation['data']
        configsGen['struct'] = checkIntegrityStruct(
            configsGen['struct'],
            lang = lang,
            initialConfig = configsGen['config'],
        )
        # configsGen['struct'] = bringOutRealConfigStruct(
        #     configsGen['struct'],
        #     lang = lang,
        #     initialConfig = configsGen['config'],
        # )
        configsGen['struct'] = removeLoopAndIfInStruct(configsGen['struct'], lang = lang)
        configsGen['struct'] = compileContentInStruct(
            configsGen['struct'],
            methods=methods,
            initialConfig = configsGen['config'],
            dest = configsGen['dest'],
            lang = lang,
        )
        # print("[arc-gen.ts] initGen | configsGen:: ", configsGen)
        generateElements(
            configsGen['struct'],
            dest = configsGen['dest'],
            lang = lang,
        )
        print({
            'fr': '[**] SUCCES DE LA GENERATION DE FICHIERS',
            'en': '[**] SUCCESSFUL FILE GENERATION',
        }[lang])
    except Exception as err:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]

        print({
            'fr': '[**] INTERRUPTION ET ECHEC DE LA GENERATION DE FICHIERS',
            'en': '[**] INTERRUPTION AND FAILURE OF FILE GENERATION',
        }[lang])
        error = GenError(
            stack,
            file = __name__,
            debug = DEBUG,
        )
        raise error
    
def genConfigFilePath(
    path: str,
    lang: str = 'fr',
    config: dict = {},
    ignore_patterns: list = ['.git', '__pycache__', '.env', 'node_modules'],
    ignore_regex: list = None,
    ignore_extensions: list = None,
    max_depth: int = 10,
    dest: str = None,
) -> dict:
    '''
    Génère une configuration à partir d'une arborescence de fichiers

    Parameters:
        path (str): le chemin à analyser
        lang (str): la langue utilisée
        config (dict): configuration de base à enrichir
        ignore_patterns (list): motifs de fichiers/dossiers à ignorer (correspondance exacte)
        ignore_regex (list): motifs regex pour ignorer fichiers/dossiers
        ignore_extensions (list): extensions de fichiers à ignorer (ex: ['.log', '.tmp'])
        max_depth (int): profondeur maximale de l'analyse
        dest (str): chemin pour sauvegarder la config générée (optionnel)

    Returns:
        dict: La configuration générée
    '''
    try:
        path = Path(path).absolute()
        if not path.exists():
            raise GenError(
                {
                    'fr': f"Le chemin '{path}' n'existe pas",
                    'en': f"Path '{path}' does not exist"
                }[lang],
                file=__name__,
                debug=DEBUG
            )

        # Compiler les regex en amont pour meilleure performance
        compiled_regex = [re.compile(pattern) for pattern in (ignore_regex or [])]

        def should_ignore(item_name, is_dir=False):
            # Vérifier les motifs exacts
            if any(ignore == item_name for ignore in (ignore_patterns or [])):
                return True
                
            # Vérifier les regex
            if any(regex.search(item_name) for regex in compiled_regex):
                return True
                
            # Vérifier les extensions (uniquement pour les fichiers)
            if not is_dir and ignore_extensions:
                ext = os.path.splitext(item_name)[1].lower()
                if ext in ignore_extensions:
                    return True
                    
            return False

        def process_directory(directory, current_depth=0):
            if current_depth > max_depth:
                return None
                
            dir_name = directory.name
            if should_ignore(dir_name, is_dir=True):
                return None
                
            children = []
            
            for item in directory.iterdir():
                if item.is_dir():
                    child_dir = process_directory(item, current_depth + 1)
                    if child_dir:
                        children.append(child_dir)
                else:
                    if not should_ignore(item.name):
                        try:
                            content = item.read_text(encoding='utf-8')
                        except UnicodeDecodeError:
                            content = f"<binary file: {item.name}>"
                        except Exception as e:
                            content = f"<error reading file: {str(e)}>"
                            
                        children.append({
                            'type': 'file',
                            'name': item.name,
                            'content': content,
                            'config': {}
                        })
            
            return {
                'type': 'folder',
                'name': dir_name,
                'config': {},
                'children': children
            }

        root_structure = process_directory(path)
        
        if not root_structure:
            raise GenError(
                {
                    'fr': "Aucune structure valide trouvée (peut-être due aux filtres)",
                    'en': "No valid structure found (maybe due to filters)"
                }[lang],
                file=__name__,
                debug=DEBUG
            )

        final_config = {
            'name': path.name,
            'dest': str(path.parent),
            'config': config,
            'struct': [root_structure]
        }

        if dest and isinstance(dest, str) and dest.strip():
            try:
                import json
                with open(dest, "w", encoding="utf-8") as f:
                    json.dump(final_config, f, indent=2, ensure_ascii=False)
            except Exception as e:
                raise GenError(
                    {
                        'fr': f"Erreur lors de l'écriture du fichier de configuration: {str(e)}",
                        'en': f"Error while writing config file: {str(e)}"
                    }[lang],
                    file=__name__,
                    debug=DEBUG
                )

        return final_config

    except Exception as err:
        stack = traceback.format_exc()
        raise GenError(
            {
                'fr': f"Erreur lors de la génération de la configuration depuis le chemin\n{stack}",
                'en': f"Error while generating config from path\n{stack}"
            }[lang],
            file=__name__,
            debug=DEBUG
        )
    
def genTreeStructurePath(
    path: str,
    lang: str = 'fr',
    ignore_patterns: list = ['.git', '__pycache__', '.env', 'node_modules'],
    ignore_regex: list = None,
    ignore_extensions: list = None,
    max_depth: int = 10,
    binary_placeholder: str = "<binary>",
    read_errors_placeholder: str = "<error>",
    dest: str = None,
) -> dict:
    '''
    Retourne une arborescence sous forme de dictionnaire plat {chemin: contenu}

    Parameters:
        path (str): le chemin à analyser
        lang (str): la langue utilisée
        ignore_patterns (list): motifs de fichiers/dossiers à ignorer (correspondance exacte)
        ignore_regex (list): motifs regex pour ignorer fichiers/dossiers
        ignore_extensions (list): extensions de fichiers à ignorer
        max_depth (int): profondeur maximale de l'analyse
        binary_placeholder (str): texte pour remplacer le contenu des fichiers binaires
        read_errors_placeholder (str): texte pour les fichiers en erreur de lecture
        dest (str): chemin pour sauvegarder la config générée (optionnel)

    Returns:
        dict: Dictionnaire {chemin_absolu: contenu}
    '''
    try:
        
        path = Path(path).absolute()
        if not path.exists():
            raise GenError(
                {
                    'fr': f"Le chemin '{path}' n'existe pas",
                    'en': f"Path '{path}' does not exist"
                }[lang],
                file=__name__,
                debug=DEBUG
            )

        # Compiler les regex pour meilleure performance
        compiled_regex = [re.compile(pattern) for pattern in (ignore_regex or [])]
        result = {}

        def should_ignore(item_name, is_dir=False):
            # Vérifier les motifs exacts
            if any(ignore == item_name for ignore in (ignore_patterns or [])):
                return True
                
            # Vérifier les regex
            if any(regex.search(item_name) for regex in compiled_regex):
                return True
                
            # Vérifier les extensions (uniquement pour les fichiers)
            if not is_dir and ignore_extensions:
                ext = os.path.splitext(item_name)[1].lower()
                if ext in ignore_extensions:
                    return True
                    
            return False

        def process_item(item, current_depth=0):
            if current_depth > max_depth:
                return

            item_name = item.name
            abs_path = str(item.absolute())

            if item.is_dir():
                if should_ignore(item_name, is_dir=True):
                    return
                
                # Pour les dossiers, on stocke None ou une valeur spéciale
                result[abs_path] = None
                
                # Traiter les enfants
                for child in item.iterdir():
                    process_item(child, current_depth + 1)
            else:
                if should_ignore(item_name):
                    return

                try:
                    # Essayer de lire le fichier en texte
                    content = item.read_text(encoding='utf-8')
                    result[abs_path] = content
                except UnicodeDecodeError:
                    # Fichier binaire
                    result[abs_path] = binary_placeholder
                except Exception as e:
                    # Erreur de lecture
                    result[abs_path] = f"{read_errors_placeholder}: {str(e)}"

        # Traiter le path de départ
        if path.is_dir():
            process_item(path)
        else:
            # Si c'est un fichier directement
            if not should_ignore(path.name):
                try:
                    result[str(path.absolute())] = path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    result[str(path.absolute())] = binary_placeholder
                except Exception as e:
                    result[str(path.absolute())] = f"{read_errors_placeholder}: {str(e)}"


        if dest and isinstance(dest, str) and dest.strip():
            try:
                import json
                with open(dest, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            except Exception as e:
                raise GenError(
                    {
                        'fr': f"Erreur lors de l'écriture du fichier d'arborescence: {str(e)}",
                        'en': f"Error writing the tree file: {str(e)}"
                    }[lang],
                    file=__name__,
                    debug=DEBUG
                )

        return result

    except Exception as err:
        stack = traceback.format_exc()
        raise GenError(
            {
                'fr': f"Erreur lors de la création du dictionnaire plat\n{stack}",
                'en': f"Error while creating flat dictionary\n{stack}"
            }[lang],
            file=__name__,
            debug=DEBUG
        )