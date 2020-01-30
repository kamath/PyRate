def main():
    import json
    import os
    from tqdm import tqdm
    from scraper.genius import Genius
    import re
    from time import sleep

    songs = json.load(open(os.path.join('output', 'billboard.json'), 'r'))

    for key, val in tqdm(songs.items()):
        primary_artist = min(val['credited_artists'], key=lambda x: x['ordinal'])['artist_name']
        title = val['title'].split('/')[0]
        regex = re.compile(".*?\((.*?)\)")
        for a in re.findall(regex, title):
            title = title.replace(a, '').replace('(', '').replace(')', '')
        songs[key]['genius_hits'] = Genius.search(f'{title} {primary_artist}')['response']['hits']
        sleep(.5)

    open(os.path.join('..', 'output', 'billboard_w_genius.json'), 'w').write(json.dumps(songs))

