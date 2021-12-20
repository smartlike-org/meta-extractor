import sys
import os
import json
from random import randint
import time
from urllib import parse
import json


def get_meta(host, url, page, header, meta, authors_meta, verbose, read_from_files):
    if read_from_files == False:
        os.system("wget --header='Accept: text/html' --user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3187.0 Safari/537.36' --timeout=10 --tries=3 'https://api.instagram.com/oembed/?url=%s' -O %s" % (url, page))

    with open(page, 'r') as f:
        embed = f.read()
        post = json.loads(embed)
        meta['author'] = post['author_name']
        meta['authorTitle'] = post['author_name']
        meta['authorHome'] = post['author_url']
        meta['title'] = post['title']
        meta['confidence'] = 10

    meta['status'] = 'ok'
    return meta
