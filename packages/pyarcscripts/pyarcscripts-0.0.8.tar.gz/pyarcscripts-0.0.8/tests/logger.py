import logging
from pyarcscripts import DEBUG, GetLogger


log = GetLogger(__name__, debug = DEBUG)
log.setLevel(logging.DEBUG)

infoMsg = {
    'fr': "Exemple de log generé",
    'en': "MIGRATIONS COMPLETED SUCCESSFULLY",
}['en']
log.debug(infoMsg)