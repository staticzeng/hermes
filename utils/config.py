from ConfigParser import ConfigParser

class VtransConfigParser(object):
    def __init__(self):
        from comm import CONF_FILE
        self.conf = CONF_FILE
        self._config = ConfigParser()
        self._config.read(self.conf)

    def get(self, section, option, default=""):
        try:
            return self._config.get(section, option)
        except:
            return default

    def get_int(self, section, option, default=-1):
        try:
            return self._config.getint(section, option)
        except:
            return default

    def write(self):
        with open(self.conf, 'w') as fd:
            self._config.write(fd)

