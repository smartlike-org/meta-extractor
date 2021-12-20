import os
import json

end_points = {"play.acast.com": "https://oembed.acast.com/v1/embed-player",
              "audioboom.com": "https://audioboom.com/publishing/oembed/v4.json",
              "dailymotion.com": "https://www.dailymotion.com/services/oembed",
              "hearthis.at": "https://hearthis.at/oembed/?format=json",
              "mixcloud.com": "https://www.mixcloud.com/oembed/",
              "mastodon.social": "https://mastodon.social/api/oembed",
              "soundcloud.com": "https://soundcloud.com/oembed",
              "ted.com": "https://www.ted.com/services/v1/oembed.json",
              "tiktok.com": "https://www.tiktok.com/oembed"}

cors_list = {
    "audioboom.com",
    "hearthis.at",
    "play.acast.com"
}


def get_meta(host, url, page, header, meta, authors_meta, verbose, read_from_files):
    if host in end_points:
        print("trying oembed, ", host)
        print("trying oembed ", end_points[host])
        if read_from_files == False:
            if end_points[host].find('?') == -1:
                embed = end_points[host] + "?url="
            else:
                embed = end_points[host] + "&url="
            print("wget -S --timeout=10 --tries=3 '%s%s' -O %s > %s 2>&1" %
                  (embed, url, page, header))
            os.system("wget -S --timeout=10 --tries=3 '%s%s' -O %s > %s 2>&1" %
                      (embed, url, page, header))
            with open(header, 'r') as f:
                h = f.read()
                if h.find('Content-Encoding: gzip') != -1:
                    os.system(
                        "wget --timeout=10 --tries=3 -O - --header='Accept-Encoding: gzip' '%s%s' | gunzip > %s" % (embed, url, page))

        with open(page, 'r') as myfile:
            data = myfile.read()
            if len(data) > 0:
                print(data)
                j = json.loads(data)

                if 'title' in j:
                    meta['title'] = j['title']
                if 'author_name' in j:
                    meta['authorTitle'] = meta['author'] = j['author_name']
                if 'author_url' in j:
                    meta['authorHome'] = j['author_url']
                if ('image' not in j or len(meta['image']) == 0) and 'thumbnail_url' in j:
                    meta['image'] = j['thumbnail_url']
                if host in cors_list and 'html' in j:
                    meta['embed'] = j['html']

                meta["status"] = "ok"

    return meta
