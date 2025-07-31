#!/home/twinkle/venv/bin/python

import shutil

import inspect
import traceback

from datetime import datetime

######################################################################
# LIBS

from twlog.util.ANSIColor import ansi
from twlog.util.Code import *
from twlog.Formatters import Formatter

######################################################################
# CLASSES - Formatter

class RichFormatter(Formatter):
    def __init__(self, fmt="%(asctime)s %(levelname)s %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]", style='%', validate=True, defaults=None, markup=True, rich_tracebacks=True, *args, **kwargs) -> None:
        super(RichFormatter, self).__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults, *args, **kwargs)
        self.markup = True if markup is True else False
        self.rich_tracebacks = True if rich_tracebacks is True else False
    def formatLevelName(self, record):
        if record.level == DEBUG:
            temp = f"{ansi.start}{ansi.fore_green}m"
        elif record.level == WARN:
            temp = f"{ansi.start}m"
        elif record.level == ERROR:
            temp = f"{ansi.start}{ansi.fore_red};{ansi.text_on_bold}m"
        elif record.level == CRITICAL:
            temp = f"{ansi.start}{ansi.back_light_red};{ansi.text_on_bold};{ansi.fore_black}m"
        elif record.level == NOTICE:
            temp = f"{ansi.start}m"
        elif record.level == ISSUE:
            temp = f"{ansi.start}m"
        elif record.level == MATTER:
            temp = f"{ansi.start}m"
        else: # Defaults (INFO)
            temp = f"{ansi.start}{ansi.fore_blue}m"
        spsp = " " * (8 - len(record.levelname))
        record.levelname = f"{temp}" + record.levelname + f"{spsp}{ansi.reset}"
    def formatMessage(self, record):
        # MarkUp?
        if self.markup is True:
            self.formatLevelName(record)
        # Get Message
        record.message = record.getMessage()
        temp = str(self.fmt)
        rdic = record.__dict__
        rkey = rdic.keys()
        if self.style == '$':
            for key in rkey:
                temp = temp.replace(f"$\x7bkey\x7d", f"{rdic[key]}")
        elif self.style == '{':
            temp = f"{temp}"
        else:
            for key in rkey:
                temp = temp.replace(f"%({key})s", f"{rdic[key]}")
        record.message = temp
        ml = strlen(record.message)
        # filename and lineno
        if record.level >= 30:
            fl = f"({record.filename}:{record.lineno})"
            ml += strlen(fl)
            ts = shutil.get_terminal_size().columns
            df = ts - ml
            if df > 0: record.message += (" " * df)
            record.message += fl
    # datetime
    def fomatTime(self, record, datefmt=None):
        # DateTime
        dt = datetime.now()
        # MarkUp?
        if self.markup is True:
            # Initialize
            if record.level == DEBUG:
                temp = f"{ansi.start}{ansi.fore_white}m"
            elif record.level == WARN:
                temp = f"{ansi.start}{ansi.fore_yellow}m"
            elif record.level == ERROR:
                temp = f"{ansi.start}{ansi.fore_red}m"
            elif record.level == CRITICAL:
                temp = f"{ansi.start}{ansi.fore_red}m"
            elif record.level == NOTICE:
                temp = f"{ansi.start}{ansi.fore_green}m"
            elif record.level == ISSUE:
                temp = f"{ansi.start}{ansi.fore_purple}m"
            elif record.level == MATTER:
                temp = f"{ansi.start}{ansi.fore_white}m"
            else: # Defaults (INFO)
                temp = f"{ansi.start}{ansi.fore_cyan}m"
            # Colorful DateTime
            record.asctime = f"{temp}" + dt.strftime(datefmt) + f"{ansi.reset}"
        else:
            record.asctime = dt.strftime(datefmt)
        return record.asctime
    def formatException(self, exc_info):
        return True
    def formatStack(self, stack_info):
        return stack_info
    def formatHeader(self, records):
        return records
    def formatFooter(self, records):
        return records
    # Gate
    def format(self, record):
        # %(asctime)s
        self.fomatTime(record, datefmt=self.datefmt)
        # %(message)s
        self.formatMessage(record)
        # ^^;
        return record

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["RichFormatter"]

""" __DATA__

__END__ """
