import logging
import sys

class Logger:

    def __new__(self, appName):
        self = logging.getLogger(appName)
        self.setLevel(logging.DEBUG)
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

    def __exit__(self):
        for handler in self.handlers:
            handler.close()
            self.removeFilter(handler)
        