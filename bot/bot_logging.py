import logging
from bot.bot_config import *

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', filename = LOG_PATH)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
logging.info("LOG INIT")

