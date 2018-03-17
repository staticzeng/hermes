import logging
import logging.handlers
from comm import *

def ansi(color, msg):
    return "\x1b[%sm%s\x1b[m" % (color, msg)

class ClouDTLogger(object):
    def __init__(self):
        self.log = logging.getLogger("Vtrans")
        formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
        #file_handler = logging.FileHandler("/var/log/vtrans.log")
        file_handler = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=LOG_MAXBYTES*1024, backupCount=LOG_BACKUPCOUNT)
        file_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)
        self.log.setLevel(logging.DEBUG)
        #self.log.setLevel(logging.INFO)


    def debug(self, msg):
        #print msg
        self.log.debug(ansi(32, msg))

    def info(self, msg):
        #print msg
        self.log.info(ansi(32, msg))

    def error(self, msg):
        #print msg
        self.log.error(ansi(31, msg))

    def warning(self, msg):
        #print msg
        self.log.warning(ansi(31, msg))

log = ClouDTLogger()
