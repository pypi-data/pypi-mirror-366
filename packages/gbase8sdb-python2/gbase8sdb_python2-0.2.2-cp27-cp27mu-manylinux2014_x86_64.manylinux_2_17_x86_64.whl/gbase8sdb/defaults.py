# coding: utf-8

from . import driver
from . import __name__ as MODULE_NAME


class Defaults(object):
    __module__ = MODULE_NAME

    def __init__(self):
        self._cyobj = driver.DEFAULTS

    @property
    def arraysize(self):
        return self._cyobj.arraysize

    @arraysize.setter
    def arraysize(self, value):
        self._cyobj.arraysize = value

    @property
    def fetch_lobs(self):
        return self._cyobj.fetch_lobs

    @fetch_lobs.setter
    def fetch_lobs(self, value):
        self._cyobj.fetch_lobs = value

    @property
    def fetch_decimals(self):
        return self._cyobj.fetch_decimals

    @fetch_decimals.setter
    def fetch_decimals(self, value):
        self._cyobj.fetch_decimals = value

    @property
    def prefetchrows(self):
        return self._cyobj.prefetchrows

    @prefetchrows.setter
    def prefetchrows(self, value):
        self._cyobj.prefetchrows = value


defaults = Defaults()
