import tweepy
import sys
import os
import json
from random import randint
import time
from urllib import parse
import json


def get_meta(config, host, url, page, header, meta, authors_meta, verbose, read_from_files):
    id = ''
    parts = url.split('/')
    for i in range(0, len(parts)):
        if parts[i] == 'twitter.com' and i < len(parts) - 2 and parts[i + 2] == 'status':
            pp = parts[i + 3].split('?')
            if len(pp):
                id = pp[0]
                break

    if len(id) == 0:
        return meta

    auth = tweepy.OAuthHandler(
        config["twitter_consumer_key"], config["twitter_consumer_secret"])
    auth.set_access_token(
        config["twitter_access_token_key"], config["twitter_access_token_secret"])
    api = tweepy.API(auth)

    tweet = api.get_status(id)._json

    oembed = api.get_oembed(id, omit_script=True, dnt=True, maxwidth=640)
    embed = oembed['html'].strip()
    print(oembed['html'].strip())

    meta['text'] = tweet['text']
    meta['author'] = tweet['user']['screen_name']
    meta['authorTitle'] = tweet['user']['name']
    meta['authorDescription'] = tweet['user']['description']
    meta['subscriber_count'] = tweet['user']['followers_count']
    if 'url' in tweet['user']:
        meta['authorHome'] = tweet['user']['url']
    meta['authorAvatar'] = tweet['user']['profile_image_url_https']
    meta['language'] = tweet['lang']
    meta['confidence'] = 10
    meta['embed'] = embed

    meta['status'] = 'ok'
    return meta
