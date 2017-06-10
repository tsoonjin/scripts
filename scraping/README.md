## Scraping

extract_urls.py
---------------
Extracts direct video url from embedded Openload video

1. Generate links with `base url` in a plain text file
```shell
python extract_urls.py www.google.com
```
2. Generate direct video urls given list of websites
```shell
python extract_urls.py links.txt
```

extract_avgle.py
---------------
Extracting `m3u8` playlist from website

1. Obtain list of videos based on channel id
```shell
python3 extract_avgle.py 13 links.txt
```

2. Generate m3u8 links
```shell
python3 extract_avgle.py links.txt
```

3. Downloading using livestreamer with GNU Parallel
```shell
parallel -a links.txt livestreamer {} best -o {#}.mp4
```



