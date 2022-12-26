

class LogPrinter(object):
    def __init__(self, output=None):
        self._output = output

    def __print(self, value, br):
        if br:
            value = '\r\n%s' % value
        if self._output is None:
            print(value)
        else:
            self._output.print(value)

    def empty(self, value, br=True):
        self.__print(value, br)

    def debug(self, value, br=True):
        value = '[DEBUG]: %s' % value
        self.__print(value, br)

    def info(self, value, br=True):
        value = '[INFO]: %s' % value
        self.__print(value, br)

    def warning(self, value, br=True):
        value = '[WARNING]: %s' % value
        self.__print(value, br)

    def error(self, value, br=True):
        value = '\r\n[ERROR]: %s\r\n' % value
        self.__print(value, br)


logger = LogPrinter()
