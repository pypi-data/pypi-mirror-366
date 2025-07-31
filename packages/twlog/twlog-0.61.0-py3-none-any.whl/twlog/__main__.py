#!/home/twinkle/venv/bin/python

######################################################################
# LIBS

from rich.logging import RichHandler

import twlog
import twlog.util

from twlog import *
from twlog.util.Code import *

######################################################################
# MAIN
if __name__ == "__main__":

    # Define True Logger
    #twlog.util.Code.export_global_loglevel(__name__)
    logger = twlog.getLogger(__name__)

    logger.test()

    priny("priny", "priny")
    pixie("pixie", "pixie")
    prain("prain", "prain")
    paint("paint", "paint")
    plume("plume", "plume")
    prank("prank", "prank")
    prown("prown", "prown")
    pinok("pinok", "pinok")
    peach("peach", "peach")
    prism("prism", "prism")

    logger.info('This is test of change title', title='TEST')

    # rich
    bconf = twlog.basicConfig(
        level    = twlog.NOTSET,
        format   = "%(message)s",
        datefmt  = "[%X]",
        handlers = [RichHandler(markup=True, rich_tracebacks=True)]
    )
    richlog = twlog.getLogger("rich", handlers = [RichHandler(rich_tracebacks=True)])
    richlog.info("This is test of rich")
    richlog.test()

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = [""]

""" __DATA__

__END__ """
