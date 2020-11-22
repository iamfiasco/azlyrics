import sys
from scrapy.selector import Selector as sel
import requests
import json
from multiprocessing import Pool

def extract_meta(uri):
    text = requests.get(uri).text
    dom = sel(text=text)
    lyrics = dom.css(".text-center > div").extract()[6]
    title = dom.css(".text-center > b").extract()[0]
    album = dom.css(".songinalbum_title > b").extract()[0]
    print(f"success @ {uri}")
    return {"lyrics": lyrics, "title": title, "album": album}
    
def get_songs_from_uri(uri):
    text = requests.get(uri).text
    dom = sel(text=text)
    temp = dom.css("h1 > strong::text").extract()[0]
    name = temp[:temp.find("Lyrics")-1]
    return {"artist": name}, dom.css(".listalbum-item > a::attr(href)").extract()

base = "https://www.azlyrics.com"
base_uri = sys.argv[1]


def sync(base_uri):
    name, songs = get_songs_from_uri(base_uri)
    songs = [base+song[2:] for song in songs]
    res = [{**extract_meta(i), **name} for i in songs]
    with open(f"{name["artist"]}.json", "w") as f:
        f.write(json.dumps({"results": res}))

def parallel(base_uri, max_parallel):
    name, songs = get_songs_from_uri(base_uri)
    songs = [base+song[2:] for song in songs]
    pool = Pool(max_parallel)
    res = [{**i, **name} for i in pool.map(extract_meta, songs)]
    with open(f"{name["artist"]}.json", "w") as f:
        f.write(json.dumps({"results": res}))

sync(base_uri)
#parallel(base_uri, 4)


