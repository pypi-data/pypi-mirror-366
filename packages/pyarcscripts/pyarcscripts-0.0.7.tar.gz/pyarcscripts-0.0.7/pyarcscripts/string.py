from random import *
from typing import *
import asyncio
import logging
import traceback
import sys
import re
from copy import deepcopy
import json

from .config import tabNumerique, tabAlphabetique, tabAlphanumerique, tabAlphabetiqueInsensitive, tabAlphanumeriqueInsensitive

log = logging.getLogger(__name__)


allLetters = r"[^abcdefghijklmnopqrstuvwxyz]"
allVowels = r"[^aeiouy]"
allConsonants = r"[^bcdfghjklmnpqrstvwxz]"


def ucFirst(value: str):
    try:
        value = str(value)
        return value[0].upper() + value[1:].lower()
    except Exception as err:
        code = str(type(err))
        msg = str(err)
        stack = str(traceback.format_exc())
        log.error(stack)
def RandomStr(typeStr = 'alphanumeric', lengthStr = 20, variationState = False, mapF = lambda data: data) :
    mapF = mapF if callable(mapF) else (lambda data: data)
    typesStr = ['alphanumeric', 'alphabetical', 'alphanumeric-insensitive', 'alphabetical-insensitive', 'numeric']
    typesStr_tab = {
        'alphanumeric': tabAlphanumerique,
        'alphabetical': tabAlphabetique,
        'alphanumeric-insensitive': tabAlphanumeriqueInsensitive,
        'alphabetical-insensitive': tabAlphabetiqueInsensitive,
        'numeric': tabNumerique,
    }
    typeStr = typeStr if typeStr in typesStr else typesStr[0]

    tabSelected = typesStr_tab[typeStr] if typeStr in list(typesStr_tab.keys()) else typesStr_tab[typesStr[0]]
    # print("> String - RandomStr | tabSelected:: ", tabSelected)
    # print("> String - RandomStr | typesStr:: ", typesStr)
    variationState = variationState if type(variationState) == bool else False
    lengthStr = randint(1, lengthStr) if variationState else lengthStr
    result = list(
        range(1, lengthStr + 1, 1)
    )
    result = ''.join(
        list(
            map(lambda x: choice(tabSelected), result)
        )
    )
    if type(result) in (int, float, str):
        result = mapF(result)

    return result