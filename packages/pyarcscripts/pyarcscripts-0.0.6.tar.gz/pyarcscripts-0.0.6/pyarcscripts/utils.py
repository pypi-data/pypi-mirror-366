from typing import *
import logging
import datetime
import pytz
from random import *
import re

from .config import langs, langCodes, DEBUG, NODEENV

log = logging.getLogger(__name__)


def getLang(lang, debug = DEBUG):
    result = lang
    result = result if result in langs else 'fr'
    return result
def getLangCode(lang):
    return langCodes[getLang(lang)]

def CleanName(
    value: str,
    sep: str = '_',
    regExp: str = r"[^a-zA-Z0-9_]",
    debug = DEBUG,
) -> str:
    '''
    Cette fonction permet de nettoyer un string en enlevant tous les caracteres non-alphanumeriques

        Args:
            value (str): element à nettoyer
            sep (str): separateur

        Returns:
            JON.Object: La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    if(not(
        type(value) in (str, int, float) and
        type(sep) in (str, int, float)
    )):
        return None
    value = str(value)
    sep = str(sep)
    res = sep.join(
        list(
            filter(
                lambda x: len(x) > 0,
                re.sub(
                    re.compile(regExp, re.MULTILINE),
                    sep,
                    value,
                ).split(sep),
            )
        )
    ) if len(value) > 0 else None
    return res

def preMapLoopData(
    data: any,
    parents: 'list | tuple',
    parent: 'str | int',
    debug = DEBUG,
):
    '''
    Cette fonction permet de prémapper la donnée qui devra ensuite être mappée ou pour un objet ou une liste des attributs enfants

        Args:
            data (any): donnée à mapé
            parents ('list | tuple'): l'ensemble des clés des parents de l'element
            parent ('str | int'): la clé du parent direct de l'element

        Returns:
            'any | list | dict': La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    return data
def mapLoopData(
    res: any,
    data: any,
    parents: 'list | tuple',
    parent: 'str | int',
    debug = DEBUG,
):
    '''
    Cette fonction permet de mapper la donnée ou pour un objet ou une liste des attributs enfants

        Args:
            data (any): donnée à parcourir
            parents ('list | tuple'): l'ensemble des clés des parents de l'element
            parent ('str | int'): la clé du parent direct de l'element

        Returns:
            'any | list | dict': La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    return res

def loopData(
    data: any,
    parents: 'list | tuple' = None,
    mapFnc = mapLoopData,
    preMapFnc = preMapLoopData,
    debug = DEBUG,
):
    '''
    Cette fonction permet de parcourir une variable et d'appliquer des actions en fonction du type

        Args:
            data (any): donnée à parcourir
            parents ('list | tuple'): l'ensemble des clés des parents de l'element
            mapFnc (def): la fontion de mappage de la donnée ou pour un objet ou une liste des attributs enfants
            preMapFnc (def): la fontion de prémappage de la donnée qui devra ensuite être mappée ou pour un objet ou une liste des attributs enfants

        Returns:
            'any | list | dict': La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    preMapFnc = preMapFnc if(preMapFnc is not None and callable(preMapFnc)) else preMapLoopData
    mapFnc = mapFnc if(mapFnc is not None and callable(mapFnc)) else mapLoopData

    if(type(data) in (list, tuple, dict, int, float, bool, str) or data is None):
        parents = parents if type(parents) in (list, tuple) else []
        parent = parents[len(parents) - 1] if len(parents) > 0 else None

        data = preMapFnc(
            data = data,
            parents = parents,
            parent = parent,
        )

        if(type(data) in (list, tuple)):
            res = []
            dataAction2 = [*data]
            dataAction2Keys = [*range(0, len(dataAction2), 1)]
            i = 0
            while True:
                if(not(i < len(dataAction2))):
                    break
                indexAction2 = i
                valueAction2 = dataAction2[indexAction2]

                newParents = [
                    *parents,
                    indexAction2,
                ]
                newValue = loopData(
                    data = valueAction2,
                    parents = newParents,
                    mapFnc = mapFnc,
                    preMapFnc = preMapFnc,
                    debug=debug,
                )
                res.append(newValue)

                i = i + 1
        elif(type(data) == dict):
            res = {}
            dataAction1 = {**data}
            dataAction1Keys = tuple(dataAction1.keys())
            i = 0
            while True:
                if(not(i < len(dataAction1Keys))):
                    break
                keyAction1 = dataAction1Keys[i]
                indexAction1 = i
                valueAction1 = dataAction1[keyAction1]

                newParents = [
                    *parents,
                    keyAction1,
                ]
                newValue = loopData(
                    data = valueAction1,
                    parents = newParents,
                    mapFnc = mapFnc,
                    preMapFnc = preMapFnc,
                    debug=debug,
                )
                res[keyAction1] = newValue

                i = i + 1
        else :
            res = mapFnc(
                res = data,
                data = data,
                parents = parents,
                parent = parent,
            )

        if(NODEENV == 'debug'):
            print('\n')
            print('>-- utils | loopData - parents:: ', parents)
            print('>-- utils | loopData - parent:: ', parent)
            print('>-- utils | loopData - data:: ', data)
            print('>-- utils | loopData - res:: ', res)
            print('\n')

        res = mapFnc(
            res = res,
            data = data,
            parents = parents,
            parent = parent,
        )

        return res
    return data
def loopData2(
    data: any,
    parents: 'list | tuple' = None,
    mapFnc = mapLoopData,
    preMapFnc = preMapLoopData,
    debug = DEBUG,
):
    '''
    Cette fonction permet de parcourir une variable et d'appliquer des actions en fonction du type

        Args:
            data (any): donnée à parcourir
            parents ('list | tuple'): l'ensemble des clés des parents de l'element
            mapFnc (def): la fontion de mappage de la donnée ou pour un objet ou une liste des attributs enfants
            preMapFnc (def): la fontion de prémappage de la donnée qui devra ensuite être mappée ou pour un objet ou une liste des attributs enfants

        Returns:
            'any | list | dict': La reponse de la fonction
    '''
    debug = debug if type(debug) == bool else DEBUG
    preMapFnc = preMapFnc if(preMapFnc is not None and callable(preMapFnc)) else preMapLoopData
    mapFnc = mapFnc if(mapFnc is not None and callable(mapFnc)) else mapLoopData

    if(type(data) in (list, tuple, dict, int, float, bool, str) or data is None):
        parents = parents if type(parents) in (list, tuple) else []
        parent = parents[len(parents) - 1] if len(parents) > 0 else None

        data = preMapFnc(
            data = data,
            parents = parents,
            parent = parent,
        )

        if(type(data) in (list, tuple)):
            res = []
            dataAction2 = [*data]
            dataAction2Keys = [*range(0, len(dataAction2), 1)]
            i = 0
            while True:
                if(not(i < len(dataAction2))):
                    break
                indexAction2 = i
                valueAction2 = dataAction2[indexAction2]

                newParents = [
                    *parents,
                    indexAction2,
                ]
                newValue = loopData2(
                    data = valueAction2,
                    parents = newParents,
                    mapFnc = mapFnc,
                    preMapFnc = preMapFnc,
                    debug=debug,
                )
                if(not(type(newValue) in (list, tuple, dict))):
                    newValue = mapFnc(
                        res = newValue,
                        data = valueAction2,
                        parents = parents,
                        parent = parent,
                    )
                    if(NODEENV == 'debug'):
                        print('>-- utils | loopData - newValue (array):: ', newValue)
                res.append(newValue)

                i = i + 1
        elif(type(data) == dict):
            res = {}
            dataAction1 = {**data}
            dataAction1Keys = tuple(dataAction1.keys())
            i = 0
            while True:
                if(not(i < len(dataAction1Keys))):
                    break
                keyAction1 = dataAction1Keys[i]
                indexAction1 = i
                valueAction1 = dataAction1[keyAction1]

                newParents = [
                    *parents,
                    keyAction1,
                ]
                newValue = loopData2(
                    data = valueAction1,
                    parents = newParents,
                    mapFnc = mapFnc,
                    preMapFnc = preMapFnc,
                    debug=debug,
                )
                
                if(not(type(newValue) in (list, tuple, dict))):
                    newValue = mapFnc(
                        res = newValue,
                        data = valueAction1,
                        parents = parents,
                        parent = parent,
                    )
                    if(NODEENV == 'debug'):
                        print('>-- utils | loopData - newValue (dict):: ', newValue)
                res[keyAction1] = newValue

                i = i + 1
        else :
            res = mapFnc(
                res = data,
                data = data,
                parents = parents,
                parent = parent,
            )
            

        if(type(res) in (list, tuple, dict)):
            res = mapFnc(
                res = res,
                data = data,
                parents = parents,
                parent = parent,
            )

        if(NODEENV == 'debug'):
            print('\n')
            print('>-- utils | loopData - parents:: ', parents)
            print('>-- utils | loopData - parent:: ', parent)
            print('>-- utils | loopData - data:: ', data)
            print('>-- utils | loopData - res:: ', res)
            print('\n')

        return res
    return data

