#!/home/twinkle/venv/bin/python

import re

######################################################################
# CLASS

class ansi:
    # start (0x1b), reset
    start = "\x1b["
    reset = "\x1b[0m"
    # foreground color
    fore_black  = "30"
    fore_red    = "31"
    fore_green  = "32"
    fore_yellow = "33"
    fore_blue   = "34"
    fore_purple = "35"
    fore_cyan   = "36"
    fore_white  = "37"
    # foreground light color
    fore_light_gray    = "90"
    fore_light_red     = "91"
    fore_light_green   = "92"
    fore_light_yellow  = "93"
    fore_light_blue    = "94"
    fore_light_magenta = "95"
    fore_light_cyan    = "96"
    fore_light_white   = "97"
    # background color
    back_black  = "40"
    back_red    = "41"
    back_green  = "42"
    back_yellow = "43"
    back_blue   = "44"
    back_purple = "45"
    back_cyan   = "46"
    back_white  = "47"
    # background light color
    back_light_gray    = "100"
    back_light_red     = "101"
    back_light_green   = "102"
    back_light_yellow  = "103"
    back_light_blue    = "104"
    back_light_magenta = "105"
    back_light_cyan    = "106"
    back_light_white   = "107"
    # bold, italic, underline, blink, invert
    text_on_bold       = "1"
    text_off_bold      = "22"
    text_on_italic     = "3"
    text_off_italic    = "23"
    text_on_underline  = "4"
    text_off_underline = "24"
    text_on_blink      = "5"
    text_off_blink     = "25"
    text_on_reverse    = "7"
    text_off_r4everse  = "27"

######################################################################
# DEFS

# ANSI Counter
def ansilen(msg):
   mall = re.findall("\x1b\[[0-9;]*m", msg)
   if mall is None:
       return 0
   mstr = ''.join(mall)
   mlen = len(mstr)
   return mlen
# Ignore ANSI Counter
def strlen(msg):
   slen = len(msg)
   mlen = ansilen(msg)
   return slen - mlen

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["ansi", "ansilen", "strlen"]

""" __DATA__

__END__ """
