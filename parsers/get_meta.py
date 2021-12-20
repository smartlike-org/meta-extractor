from datetime import datetime
import time
import json
import random
import sys
import os
from os import getenv
import threading
from threading import Thread, Lock
from langdetect import detect
from textblob import TextBlob
import pycld2 as cld2
from urllib import parse
from parsers import youtube_com
from parsers import instagram_com
from parsers import twitter_com
from parsers import pdf
from parsers import general
from parsers import scrapinghub
import textwrap
import logging


def crawl_meta(url, id, config, log_channel, verbose=False, read_from_files=False, remove_files=True):
    meta = init_meta()

    authors_meta = []

    page = "%s.html" % (id)
    header = "%s.txt" % (id)

    try:
        host = get_domain(url)

        if (host == "" and url.find("youtube.com") == 0 and len(url) > len("youtube.com")) or ((host.find('youtube.com') == 0 or host.find('www.youtube.com') == 0 or host.find('music.youtube.com') == 0) and host != url):
            meta = youtube_com.get_meta(config["youtube_api_key"],
                                        host, url, page, header, meta, authors_meta, verbose, read_from_files)
        # elif host == "instagram.com" and host != url:
        #    meta = instagram_com.get_meta(host, url, page, header, meta,
        #                                  authors_meta, verbose, read_from_files)
        elif host == "twitter.com" and host != url:
            meta = twitter_com.get_meta(config, host, url, page, header, meta,
                                        authors_meta, verbose, read_from_files)
        elif url.find(".pdf") == len(url) - 4:
            meta = pdf.get_meta(host, url, page, header, meta,
                                authors_meta, verbose, read_from_files)
        else:
            try:
                meta = scrapinghub.get_meta(
                    host, url, page, header, meta, authors_meta, verbose, read_from_files)
            except:
                logging.error("failed to parse %s with scrapinghub" %
                              url, extra={'channel': log_channel})

            if len(meta['title']) == 0:
                meta = general.get_meta(
                    host, url, page, header, meta, authors_meta, verbose, read_from_files)

            if host == "t.me":
                parts = url.split('/')
                if len(parts) > 3 and parts[2] == "t.me":
                    meta['author'] = parts[3]

        if len(meta['language']) == 0:
            if len(meta['title']) or len(meta['description']):
                meta['language'] = guess_language(
                    meta['title'] + ' ' + meta['description'])
            elif len(meta['text']):
                meta['language'] = guess_language(meta['text'])
        elif len(meta['language']) > 2:
            meta['language'] = meta['language'][0:2]
    except:
        print("failed to fetch meta for %s" % url)
        return meta

    if remove_files:
        try:
            os.remove(page)
        except:
            pass

        try:
            os.remove(header)
        except:
            pass

    if len(meta['author']):
        meta['author'] = meta['author'] + '#' + host

    if len(host) == 0:  # publisher
        host = url

    meta["image"] = expand_url(host, meta["image"])
    meta["icon"] = expand_url(host, meta["icon"])
    meta["title"] = textwrap.shorten(
        meta["title"], width=100, placeholder="...")
    meta["description"] = textwrap.shorten(
        meta["description"], width=256, placeholder="...")

    if len(meta["tags"]) != 0:
        meta["tags"] = [k.lower() for k in meta["tags"] if len(k) < 20]

    return meta


def expand_url(domain, url):
    if len(url) and url[0] == '/':
        return "https://" + domain + url
    else:
        return url


def guess_language(text):
    try:
        isReliable, textBytesFound, details = cld2.detect(text)
        if details is not None:
            return details[0][1]
    except:
        print("failed to decode")
        return ''


def init_meta():
    return {
        'title': '',
        'description': '',
        'image': '',
        'icon': '',
        'creator': '',
        'confidence': 0,
        'author': '',
        'authorTitle': '',
        'authorHome': '',
        'authorAvatar': '',
        'authorDescription': '',
        'subscriber_count': 0,
        'pub_date': 0,
        'language': '',
        'country': '',
        'tags': [],
        'text': '',
        'status': 'failed'
    }


def get_domain(url):
    host = parse.urlsplit(url).netloc
    if host.find('www.') == 0 or host.find('WWW.') == 0:
        host = host[4:]
    return host
