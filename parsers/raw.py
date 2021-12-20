import sys
import os
import json
from random import randint
import time
from urllib import parse


def get_meta(host, url, page, header, meta, authors_meta, verbose, read_from_files):
    if read_from_files == False:
        os.system("wget --header='Accept: text/html' --user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3187.0 Safari/537.36' --timeout=10 --tries=3 '%s' -O %s" % (url, page))

    meta['raw'] = ''
    with open(page, 'r') as f:
        meta['raw'] = f.read()

    meta['status'] = 'ok'
    return meta
