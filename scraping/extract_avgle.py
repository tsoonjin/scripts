import time
import ast
import sys
import json
import math
import requests
import re
import multiprocessing as mp

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import quote, urlsplit, urlunsplit

AVGLE_CATEGORIES_API_URL = 'https://api.avgle.com/v1/categories'
AVGLE_LIST_VIDEOS_API_URL = 'https://api.avgle.com/v1/videos/{}?c={}&limit={}'
AVGLE_SEARCH_VIDEOS_API_URL = 'https://api.avgle.com/v1/tw/{}/{}?limit={}'

def extractJSON(script):
    res = None
    affiliates = re.findall('var videoInfo = (.*?);\s*$', script.text, re.M)
    if affiliates:
        res = affiliates[0]
    return res


def get_videos(chid, output='links.txt', limit=250):
    """ Extract videos with given parameters
        @param chid: filter only videos from given category
        @param limit: maximum number of videos per page
    """
    videos = []
    i = 1
    url = AVGLE_LIST_VIDEOS_API_URL.format(0, chid, limit)
    response = json.loads(urlopen(url).read().decode())

    while response['success']:
        vids = response['response']['videos']
        vids = [v['video_url'] for v in vids]
        videos.extend(vids)
        if response['response']['has_more']:
            url = AVGLE_LIST_VIDEOS_API_URL.format(i, chid, limit)
            response = json.loads(urlopen(url).read().decode())
            i += 1
        else:
            break

    with open(output, 'w') as o:
        o.write('\n'.join(videos))



def build_url(info):
    hasSD = re.findall('var hasSD = (.*?);\s*$', info.text, re.M)[0]
    res = 'sd' if hasSD == 'true' else 'hd'
    info = extractJSON(info)
    info = ast.literal_eval(info)
    s2 = info['s2'].replace("\\", "")
    final = 'hls://{}://{}.qooqlevideo.com/{}/{}/{}/stream.m3u8'.format(
        info['scheme'], info['s1'], s2, info['vid'], res)
    return final

def analyze_url(url):
    download_url = ''
    try:
        url = url.rstrip()
        url = list(urlsplit(url))
        url[2] = quote(url[2])
        url = urlunsplit(url)
        query = Request(url)
        query.add_header('User-Agent', 'Mozilla/5.0')
        src = urlopen(query).read()
        soup = BeautifulSoup(src, 'html.parser')
        soup.prettify()
        content = soup.find_all('script', {'type': 'text/javascript'})
        info = [s for s in content if extractJSON(s) is not None]
        download_url = build_url(info[0])
        print(download_url)
    except Exception as e:
        time.sleep(5)
        analyze_url(url)
    finally:
        return download_url


if __name__ == '__main__':
    response = json.loads(urlopen(AVGLE_CATEGORIES_API_URL).read().decode())
    if response['success']:
        categories = response['response']['categories']
        names = [c['name'].split('・')[0] for c in categories]
        ids = {n: c['CHID'] for n, c in zip(names, categories)}
    if len(sys.argv) < 2:
        print("Usage: extract_avgle.py <text file> OR \nextract_avgle.py <channel id> <output>")
    elif len(sys.argv) == 3:
        get_videos(sys.argv[1], sys.argv[2])
    else:
        filename = sys.argv[1].rsplit('.', 1)[0]
        print(filename)
        with open(sys.argv[1], encoding='utf-8') as f, open('{}links.txt'.format(filename), 'w') as w:
            results = []
            urls = f.readlines()
            pool = mp.Pool()
            results = pool.map(analyze_url, urls)
            results = filter(lambda x: x != '', results)
            w.write('\n'.join(results))
