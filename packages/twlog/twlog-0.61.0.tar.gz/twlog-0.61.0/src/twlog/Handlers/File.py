#!/home/twinkle/venv/bin/python

import os
import sys

import locale

######################################################################
# LIBS

from twlog.util.Code import *
from twlog.Handlers import Handler

######################################################################
# Classes - handlers

class FileHandler(Handler):
    # Initialization
    def __init__(self, level=INFO, filename=None, mode='a', encoding=None, delay=False, errors=None) -> None:
        super(FileHandler, self).__init__(level=level)
        self.filename = str(filename) if filename is not None else 'sys.stdout'
        self.mode = str(mode) if mode is not None else 'a'
        self.encoding = str(encoding) if encoding is not None else locale.getpreferrerdencoding()
        self.delay = bool(delay) if delay is not None else False
        self.errors = str(errors) if errors is not None else None
        if self.filename == 'sys.stdout':
            self.f = sys.stdout
        elif delay is False:
            self.f = open(self.filename, mode=self.mode, encoding=self.encoding, buffering=self.delay, errors=self.errors)
        else:
            self.f = None
    def emit(self, record):
        # Format
        record = self.format(record)
        # ^^;
        if delay is True:
            with open(self.filename, mode=self.mode, encoding=self.encoding, buffering=self.delay, errors=self.errors):
                print(record.message, file=self.f)
        # ^^;
        else:
            print(record.message, file=self.f)
    def flush(self):
        if delay is False:
            self.f.flush()
    def close(self):
        if self.filename != 'sys.stdout' and delay is False:
            close(self.f)

class BufferedFileHandler(Handler):
    # Initialization
    def __init__(self, level=INFO, filename=None, mode='a', encoding=None, delay=False, errors=None) -> None:
        super(FileHandler, self).__init__(level=level)
        self.filename = str(filename) if filename is not None else 'sys.stdout'
        self.mode = str(mode) if mode is not None else 'a'
        self.encoding = str(encoding) if encoding is not None else locale.getpreferrerdencoding()
        self.delay = bool(delay) if delay is not None else False
        self.errors = str(errors) if errors is not None else None
        # Binder
        self.binder = []
        # Stdout?
        if self.filename == 'sys.stdout':
            self.f = sys.stdout
        else:
            self.f = None
    def getBinder(self):
        return self.binder.copy()
    def emit(self, record):
        # Format
        record = self.format(record)
        # ^^;
        self.binder.appends(record.message + "\n")
    def flush(self):
        with open(self.filename, mode=self.mode, encoding=self.encoding, buffering=False, errors=self.errors):
            print(self.binder, file=self.f)
        self.binder.clear()
    def __del__(self):
        self.flush()

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["FileHandler", "BufferedFileHandler"]

""" __DATA__

__END__ """
