import sys
import os
import json
from random import randint
import time
from os import getenv
from urllib import parse
import json
import threading


def get_meta(host, url, page, header, meta, authors_meta, verbose, read_from_files):
    if read_from_files == False:
        embed = "https://noembed.com/embed?url="
        os.system("wget -S --timeout=10 --tries=3 '%s%s' -O %s > %s 2>&1" %
                  (embed, url, page, header))
        with open(header, 'r') as f:
            h = f.read()
            if h.find('Content-Encoding: gzip') != -1:
                os.system(
                    "wget --timeout=10 --tries=3 -O - --header='Accept-Encoding: gzip' '%s%s' | gunzip > %s" % (embed, url, page))

    with open(page, 'r') as myfile:
        lines = myfile.readlines()
        if len(lines) > 0:
            print(lines[0])
            j = json.loads(lines[0])

            if 'author_name' in j != 0:
                meta['authorTitle'] = meta['author'] = j['author_name']

    return meta
