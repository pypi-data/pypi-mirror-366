#!/home/twinkle/venv/bin/python

import os
import re
import json
import argparse

import urllib.parse

######################################################################
# LIBS

from sdgp import sdgp
from sdgp.gtk import *
from sdgp.gtk.dialog import dialog
#from sdgpp.gtk.txview import txview

######################################################################
# ArgParse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True)
    args = parser.parse_args()

    path = args.i

    path = re.sub('^file://', '', path)
    path = urllib.parse.unquote(path)

    hako = sdgp(path)

    if hako is not None:

        prmp = hako.pop("prompt").replace("<", "&lt;")
        prmp = prmp.replace(">", "&gt;")
        prmp = prmp.replace("\x22", "&quot;")
        prmp = prmp.replace("|", "\\|")
        prmp = re.sub("[\r\n]$", "", prmp)

        ngtv = hako.pop("negativePrompt").replace("<", "&lt;")
        ngtv = ngtv.replace(">", "&gt;")
        ngtv = ngtv.replace("\x22", "&quot;")
        ngtv = ngtv.replace("|", "\\|")
        prmp = re.sub("[\r\n]$", "", prmp)

        hall = f"Prompt: {prmp}\n\nNegative Prompt: {ngtv}\n\n" #json.dumps(hako, indent=4)

        for k in hako.keys():
            hall = hall + f"{k}: {hako[k]}, "

        dialog(hall, 'Stable Diffusion Creation Info', 'sd-get-prompt', GTK_MESSAGE_INFO, GTK_BUTTONS_OK)

######################################################################
# MAIN
if __name__ == "__main__":
    main()

""" __DATA__

__END__ """
