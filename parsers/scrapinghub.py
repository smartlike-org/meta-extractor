import sys
import os
import threading
import extruct
from extruct import SYNTAXES
import datetime
from dateutil.parser import parse
import json
from parsers import general
from parsers import oembed
import logging


def convert_string(s):
    if isinstance(s, str):
        return s.replace(u"\u2018", "'").replace(u"\u2019", "'")
    else:
        return ''


def parse_json_ld_node(d, meta, authors_meta):
    if 'headline' in d:
        meta['title'] = convert_string(d['headline'])
    if 'description' in d:
        meta['description'] = convert_string(d['description'])
    if 'image' in d and len(d['image']) > 0:
        if isinstance(d['image'], str):
            meta['image'] = convert_string(d['image'])
        elif isinstance(d['image'], list) and len(d['image']):

            if isinstance(d['image'][0], str):
                meta['image'] = convert_string(d['image'][0])
            elif 'url' in d['image'][0]:
                meta['image'] = convert_string(d['image'][0]['url'])
    if 'inLanguage' in d:
        meta['language'] = convert_string(d['inLanguage'])
    if 'datePublished' in d:
        dt = parse(d['datePublished'])
        meta['pub_date'] = int(dt.timestamp())
    if 'author' in d:
        if isinstance(d['author'], list) and len(meta['author']) == 0:
            if len(d['author']):
                if 'name' in d['author'][0]:
                    meta['author'] = convert_string(d['author'][0]['name'])
                    if meta['author'] not in authors_meta:
                        authors_meta[meta['author']] = {
                            'title': meta['author'], 'home': '', 'avatar': ''}
                    if 'url' in d['author'][0] and len(d['author'][0]['url']):
                        authors_meta[meta['author']
                                     ]['home'] = d['author'][0]['url']
        elif 'name' in d['author'] and len(meta['author']) == 0:
            meta['author'] = convert_string(d['author']['name'])
            if meta['author'] not in authors_meta:
                authors_meta[meta['author']] = {
                    'title': meta['author'], 'home': '', 'avatar': ''}
            if 'url' in d['author'] and len(d['author']['url']):
                authors_meta[meta['author']]['home'] = d['author']['url']
        else:
            meta['author'] = convert_string(d['author'])
    if 'keywords' in d:
        if isinstance(d['keywords'], list):
            meta['tags'] = d['keywords']
    if 'articleBody' in d and isinstance(d['articleBody'], str) and len(d['articleBody']):
        meta['text'] = d['articleBody']
    if 'keywords' in d and isinstance(d['keywords'], str) and len(d['keywords']):
        meta['tags'] = [item.strip() for item in d['keywords'].split(',')]
    if 'datePublished' in d and isinstance(d['datePublished'], str):
        try:
            meta['pub_date'] = int(datetime.datetime.strptime(
                d['datePublished'], '%Y-%m-%dT%H:%M:%S.%f').timestamp())
        except:
            pass
    if 'inLanguage' in d and isinstance(d['inLanguage'], str):
        parse_lc(d['inLanguage'], meta)


def get_meta(host, url, page, header, meta, authors, verbose, read_from_files):
    authors_meta = dict()
    if read_from_files == False:
        #print('loading %s' % url)
        if host.find('facebook.') == 0:
            os.system("wget --header='Accept: text/html' --user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3187.0 Safari/537.36' --timeout=10 --tries=3 '%s' -O %s" % (url, page))
        else:
            os.system("wget -S --timeout=10 --tries=3 '%s' -O %s > %s 2>&1" %
                      (url, page, header))
    with open(page, 'rb') as f:
        html = f.read()
        try:
            data = extruct.extract(html, base_url=url, syntaxes=[
                'microdata', 'json-ld', 'opengraph', 'microformat'])
            if verbose:
                logging.info(json.dumps(data, indent=2, sort_keys=True))

            if 'json-ld' in data and len(data['json-ld']) > 0:
                for d in data['json-ld']:
                    parse_json_ld_node(d, meta, authors_meta)
                    if 'video' in d:
                        parse_json_ld_node(d['video'], meta, authors_meta)
                    elif 'mainEntity' in d:
                        parse_json_ld_node(d['mainEntity'], meta, authors_meta)

            collect_tags = len(meta['tags']) == 0
            if 'opengraph' in data and len(data['opengraph']) > 0 and 'properties' in data['opengraph'][0]:
                for p in data['opengraph'][0]['properties']:
                    if p[0] == 'article:author' and len(meta['author']) == 0:
                        meta['author'] = convert_string(p[1])
                    elif p[0] == 'og:title' and len(meta['title']) == 0:
                        meta['title'] = convert_string(p[1])
                    elif p[0] == 'og:image' and len(meta['image']) == 0:
                        meta['image'] = convert_string(p[1])
                    elif p[0] == 'og:description' and len(meta['description']) == 0:
                        meta['description'] = convert_string(p[1])
                    elif p[0] == 'article:tag' and collect_tags:
                        for t in convert_string(p[1]).split(','):
                            meta['tags'].append(t)
                    elif p[0] == 'article:published_time':
                        dt = parse(p[1])
                        meta['pub_date'] = int(dt.timestamp())
                    elif p[0] == 'og:locale':
                        parse_lc(p[1], meta)
                    elif p[0] == 'og:site_name':
                        meta['site_name'] = convert_string(p[1])

            collect_tags = len(meta['tags']) == 0
            if 'microdata' in data and len(data['microdata']) > 0:
                for d in data['microdata']:
                    # and 'type' in d and d['type'] == 'https://schema.org/WebPage':
                    if 'properties' in d:
                        p = d['properties']
                        if 'articleBody' in p and len(meta['text']) == 0:
                            meta['text'] = p['articleBody']
                        if 'text' in p and len(meta['text']) == 0:
                            meta['text'] = p['text']
                        if 'headline' in p and isinstance(p['headline'], str):
                            meta['title'] = p['headline']
                        if 'author' in p:
                            if isinstance(p['author'], list):
                                meta['author'] = ",".join(p['author'])
                            elif 'properties' in p['author'] and 'name' in p['author']['properties']:
                                author_name = convert_string(
                                    p['author']['properties']['name'])
                                if len(meta['author']) == 0:
                                    meta['author'] = author_name
                                if author_name not in authors_meta:
                                    authors_meta[author_name] = {
                                        'title': author_name, 'home': '', 'avatar': ''}
                                if 'url' in p['author']['properties'] and len(p['author']['properties']['url']):
                                    authors_meta[author_name]['home'] = p['author']['properties']['url']
                                if 'image' in p['author']['properties'] and len(p['author']['properties']['image']):
                                    authors_meta[author_name]['avatar'] = p['author']['properties']['image']
                            else:
                                meta['author'] = p['author']
                        if 'name' in p and 'type' in d and d['type'] == 'http://schema.org/Person' and len(meta['author']) == 0:
                            meta['author'] = convert_string(p['name'])

                        if 'keywords' in p and len(p['keywords']) > 0 and collect_tags:

                            if isinstance(p['keywords'], str):
                                meta['tags'] = [item.strip()
                                                for item in p['keywords'].split(',')]
                            else:
                                for k in p['keywords']:
                                    meta['tags'].append(convert_string(k))
                        if 'dateModified' in p and meta['pub_date'] == 0:
                            dt = parse(p['dateModified'])
                            meta['pub_date'] = int(dt.timestamp())

                        if 'mainEntity' in p and 'properties' in p['mainEntity']:
                            pp = p['mainEntity']['properties']
                            if 'author' in pp and 'properties' in pp['author'] and 'name' in pp['author']['properties']:
                                meta['author'] = convert_string(
                                    pp['author']['properties']['name'])

            if meta['author'] in authors_meta:
                meta['authorHome'] = authors_meta[meta['author']]['home']
                meta['authorAvatar'] = authors_meta[meta['author']]['avatar']

            if len(meta['author']):
                meta['authorTitle'] = meta['author']
            meta["status"] = "ok"

        except:
            logging.info("Failed to extract metadata")

    if len(meta['tags']) == 0:
        # print(json.dumps(meta))
        logging.info("trying alternative meta data")
        try:
            image = meta['image']
            alt = general.get_meta(
                host, url, page, header, meta, authors_meta, verbose, True)
            if len(alt['tags']):
                meta['tags'] = alt['tags']
            if len(image):
                meta['image'] = image
        except:
            logging.info("failed to fetch alternative meta data")

    if len(meta['author']) == 0:
        try:
            if host in oembed.end_points:
                alt = oembed.get_meta(
                    host, url, page, header, meta, authors_meta, verbose, False)
        except:
            logging.info("failed to fetch alternative meta data")

    return meta


def parse_lc(code, meta):
    parts = code.split('_')
    if len(parts) == 2:
        meta['language'] = parts[0]
        meta['country'] = parts[1]
    else:
        parts = code.split('-')
        if len(parts) == 2:
            meta['language'] = parts[0]
            meta['country'] = parts[1]
