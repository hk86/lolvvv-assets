import logging
import sys

class Logger(logging.Logger):

    def __new__(self, appName, debug_level=logging.WARN):
        self = logging.getLogger(appName)
        self.setLevel(debug_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

        fh = logging.FileHandler(appName + '.log')
        fh.setLevel(logging.WARNING)
        fh.setFormatter(formatter)
        self.addHandler(fh)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.addHandler(ch)
        return self

    def __del__(self):
        for handler in self.handlers:
            handler.close()
            self.removeFilter(handler)
        