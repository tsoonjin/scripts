""" Extract urls with given base url """
#!/usr/bin/env python
import sys
import requests
import re
import urllib2
import multiprocessing as mp

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

OPENLOAD_PREFIX = 'https://openload.co/stream/'

def analyze_openload(url, driver):
    driver.get(url)
    # Wait for 10 seconds
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "mediaspace_wrapper")))
    src = driver.page_source
    soup = BeautifulSoup(src, 'html.parser')
    video_url = soup.find('span', {'id': 'streamurl'}).contents[0]
    download_url = '{}{}'.format(OPENLOAD_PREFIX, video_url.encode('ascii', 'ignore'))
    return download_url


def analyze_url(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    src = opener.open(url[1])
    soup = BeautifulSoup(src, 'html.parser')
    iframe_url = soup.find('iframe')['src']
    openload = analyze_openload(iframe_url, driver)
    driver.quit()
    print(openload)
    return openload


def analyze_urls(path, out='links.txt'):
    video_urls = []
    pool = mp.Pool(5)
    with open(path) as f, open(out, 'w') as o:
        urls = f.readlines()
        urls = [(i, url) for i, url in enumerate(urls)]
        video_urls = pool.map(analyze_url, urls)
        pool.close()
        pool.join()
        o.write('\n'.join(video_urls))

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage: extract_urls.py <test.html> <www.youtube.com>")
        exit()

    elif len(sys.argv) == 2:
        analyze_urls(sys.argv[1])

    else:
        with open(sys.argv[1]) as f, open('{}.txt'.format(sys.argv[2]), 'w') as o:
            pattern = sys.argv[2].replace('.', '\.')
            print('Pattern: {}'.format(pattern))
            soup = BeautifulSoup(f.read(), 'html.parser')
            data = soup.find_all('a', href=re.compile(pattern))
            urls = '\n'.join([i['href'] for i in data])
            o.write(urls)
