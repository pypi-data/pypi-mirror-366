import logging
from pyarcscripts import DEBUG, GetLogger, RandomStr

print(f"[tests -> string.py] __name__:: ", __name__)
log = GetLogger(__name__, debug = DEBUG)
log.setLevel(logging.DEBUG)

valRdm = randomString = RandomStr(
    typeStr = 'alphanumeric-insensitive',
    lengthStr=15,
)
msg = {
    'fr': f"la chaine de caractères generée est:: {valRdm}",
    'en': f"the character string generated is:: {valRdm}",
}['en']

print(f"[tests -> string.py] randomString:: ", randomString)
log.debug(msg)