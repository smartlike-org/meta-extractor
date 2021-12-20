import sys
import os
import json
from random import randint
import time
from os import getenv
from urllib import parse
import json
import threading
from bs4 import BeautifulSoup
import logging


def get_meta(host, url, page, header, meta, authors_meta, verbose, read_from_files):
    if read_from_files == False:
        if host.find('facebook.') == 0:
            os.system("wget --header='Accept: text/html' --user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3187.0 Safari/537.36' --timeout=10 --tries=3 '%s' -O %s" % (url, page))
        else:
            os.system("wget -S --timeout=10 --tries=3 '%s' -O %s > %s 2>&1" %
                      (url, page, header))
            with open(header, 'r') as f:
                h = f.read()
                if h.find('Content-Encoding: gzip') != -1:
                    os.system(
                        "wget --timeout=10 --tries=3 -O - --header='Accept-Encoding: gzip' '%s' | gunzip > %s" % (url, page))

    charset = ''
    with open(page, 'r') as myfile:
        genre = ''
        tags = list()
        section = ''
        content_image = ''

        try:
            soup = BeautifulSoup(myfile, "html.parser")
        except:
            logging.info('failed to parse html')
            return meta

        if verbose:
            logging.info(soup.originalEncoding)
        html = soup.find("html")

        if len(meta['icon']) == 0:
            icons = soup.findAll("link", {"rel": "icon"})
            for i in icons:
                meta['icon'] = i.get("href", '')
                break

        icons = soup.findAll("link", {"rel": "apple-touch-icon"})
        for i in icons:
            content_image = i.get("href", '')

        if len(content_image) == 0:
            icons = soup.findAll(
                "link", {"rel": "apple-touch-icon-precomposed"})
            for i in icons:
                content_image = i.get("href", '')

        metadata = soup.findAll("meta")

        for tag in metadata:
            property = tag.get("property", '').lower()
            if property != '':
                if property == "og:image" and len(meta['image']) == 0:
                    meta['image'] = tag.get("content", '')
                elif property == "mediator_author" and len(meta['author']) == 0:
                    meta['author'] = tag.get("content", '')

        for tag in metadata:
            name = tag.get("name", '').lower()
            itemprop = tag.get("itemprop", '').lower()
            if len(meta['image']) == 0 and (name == "twitter:image" or itemprop == "image"):
                meta['image'] = tag.get("content", '')
            elif name == "genre":
                genre = tag.get("content", '')
            elif name == "keywords":
                tags = tags + \
                    list(set(tag.get("content", '').split(',')) - set(tags))
                #tags.append(tag.get("content", '').split(','))
            elif name == "msApplication-TileImage" and len(content_image) == 0:
                content_image = tag.get("content", '')
            elif name == "parsely-author" or name == "sailthru.author":
                meta['author'] = tag.get("content", '')
            elif name == "parsely-page":
                try:
                    j = json.loads(tag.get("content", ''))
                    if 'title' in j:
                        meta['title'] = j['title']
                    if 'author' in j:
                        meta['author'] = j['author']
                    if 'image_url' in j:
                        meta['image'] = j['image_url']
                except:
                    pass

            if name == "author":
                meta['author'] = tag.get("content", '')
            elif name == "description" or itemprop == "description":
                meta['description'] = tag.get("content", '')

            if len(meta['language']) == 0 and tag.get("http-equiv", '') == "content-language":
                meta['language'] = tag.get("content", '')

        for tag in metadata:
            property = tag.get("property", '').lower()
            if property != '':
                # or tag.get("itemprop", None) == "name":
                if property == "og:title":
                    meta['title'] = tag.get("content", '')
                elif property == "og:image" and len(meta['image']) == 0:
                    meta['image'] = tag.get("content", '')
                elif property == "og:description" and len(meta['description']) == 0:
                    meta['description'] = tag.get("content", '')
                # elif property == "og:type":
                #	type = tag.get("content", '')
                elif property == "article:author" and len(meta['author']) == 0:
                    meta['author'] = tag.get("content", '')
                elif property == "og:locale":
                    meta['language'] = tag.get("content", '')
                elif property == "article:tag" or property == "og:video:tag":
                    tags = tags + \
                        list(set(tag.get("content", '').split(',')) - set(tags))
                    #tags.append(tag.get("content", '').split(','))
                elif property == "article:section":
                    section = tag.get("content", '')
                elif property == "twitter:author" and len(meta['author']) == 0:
                    meta['author'] = tag.get("content", '')

        scripts = soup.findAll("script", {"type": "application/ld+json"})
        for s in scripts:
            try:
                j = json.loads(s.next)
                if len(meta['title']) == 0 and 'headline' in j:
                    meta['title'] = j['headline']
                if 'author' in j:
                    if len(j['author']):
                        meta['author'] = j['author'][0]['name']
                break
            except:
                logging.info('failed to parse %s' % name)

        if len(meta['title']) == 0:
            t = soup.find("title")
            if t:
                meta['title'] = t.text

        if len(meta['image']) == 0:
            if len(content_image):
                meta['image'] = content_image
            elif len(meta['icon']) != 0:
                meta['image'] = meta['icon']

        if meta['image'].find('/') == 0 and meta['image'].find("//") != 0:
            if host.find('.') == host.rfind('.'):
                meta['image'] = "http://www." + host + meta['image']
            else:
                meta['image'] = "http://" + host + meta['image']

        if host == 'youtube.com':
            with open(page, 'r') as f:
                data = f.read().replace('\n', '').replace("\\", "")
                ap = data.find('"author":"')
                if ap != -1:
                    d = data[ap + 10:]
                    ap_ = d.find('"')
                    if ap_ != -1 and ap_ < 200:
                        meta['author'] = d[:ap_]

        meta['title'] = ' '.join(meta['title'].split())
        meta['author'] = ' '.join(meta['author'].split())
        meta['description'] = ' '.join(meta['description'].split())

        if len(meta['language']) > 2:
            meta['language'] = meta['language'][0:2]

        for t in tags:
            meta['tags'].append(t.strip())  # ",".join(tags).strip().lower()

        if host == 'youtube.com':
            with open(page, 'r') as f:
                data = f.read().replace('\n', '').replace("\\", "")
                ap = data.find('"author":"')
                if ap != -1:
                    d = data[ap + 10:]
                    ap_ = d.find('"')
                    if ap_ != -1 and ap_ < 200:
                        meta['author'] = d[:ap_]
                        if verbose:
                            logging.info(
                                "youtube authour found - " + meta['author'])

    meta["status"] = "ok"
    return meta
