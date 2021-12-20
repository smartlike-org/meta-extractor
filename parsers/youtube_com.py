import threading
import os
from os import getenv
from urllib import parse
import threading
import json
import datetime


def get_meta(youtube_api_key, host, url, page, header, meta, authors_meta, verbose, read_from_files):
    request = ""
    channel_id = ""
    if url.find("youtube.com/channel/") == -1:
        pars = dict(parse.parse_qsl(parse.urlsplit(url).query))
        if 'v' not in pars:
            return meta
        request = f"wget -S --timeout=10 --tries=3 'https://www.googleapis.com/youtube/v3/videos?id={pars['v']}&key={youtube_api_key}&part=snippet' -O {page}"
        image_sizes = ['high', 'medium', 'default']
    else:
        parts = url.split("/")
        if len(parts) == 0:
            return meta
        channel_id = parts[len(parts) - 1]
        request = f"wget -S --timeout=10 --tries=3 'https://www.googleapis.com/youtube/v3/channels?id={channel_id}&key={youtube_api_key}&part=snippet,statistics' -O {page}"
        image_sizes = ['default', 'medium', 'high']

    if read_from_files == False:
        os.system(request)

    with open(page, 'r') as f:
        m = f.read()
        yt_meta = json.loads(m)
        if verbose:
            print(yt_meta)
        if 'items' in yt_meta and len(yt_meta['items']) and 'snippet' in yt_meta['items'][0]:
            i = yt_meta['items'][0]['snippet']
            image = ''
            target = 640
            best_diff = 100000

            for t in i['thumbnails']:
                diff = abs(i['thumbnails'][t]['width'] - target)
                if diff < best_diff:
                    best_diff = diff
                    image = i['thumbnails'][t]['url']
                else:
                    break

            meta['title'] = i['title']
            meta['description'] = i['description']
            meta['image'] = image
            meta['icon'] = image

            if 'channelId' in i:
                meta['author'] = i['channelId']
            if 'channelTitle' in i:
                meta['authorTitle'] = i['channelTitle']

            if len(channel_id) > 0:
                meta['url'] = url

            if 'tags' in i:
                meta['tags'] = i['tags']

            if 'defaultAudioLanguage' in i:
                meta['language'] = i['defaultAudioLanguage']

            if 'publishedAt' in i:
                # 2020-06-13T16:03:26Z
                meta['pub_date'] = int(datetime.datetime.strptime(
                    i['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').timestamp())

            if 'statistics' in yt_meta['items'][0] and 'subscriberCount' in yt_meta['items'][0]['statistics']:
                meta['subscriber_count'] = int(
                    yt_meta['items'][0]['statistics']['subscriberCount'])
            else:
                meta['subscriber_count'] = 0

            meta['status'] = 'ok'
        return meta
