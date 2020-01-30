def main():
    import pandas as pd
    import os
    from ast import literal_eval
    from scraper.genius import Genius
    from scraper.spotify import Spotify

    BILLBOARD_DIR = os.path.join('output', 'billboard')
    weeks = os.listdir(BILLBOARD_DIR)
    weeks.sort(reverse=True)
    for week in weeks:
        df = pd.read_csv(os.path.join(BILLBOARD_DIR, week, 'main.csv'))
        for i, row in df.iterrows():
            # Sort artists by appearance in the title
            artists = ', '.join(list(map(lambda x: x['artist_name'],
                               sorted(literal_eval(row['credited_artists']), key=lambda x: x['ordinal']))))
            search_str = row['title'] + ' ' + artists
            genius_resp = Genius.search(search_str)
            print('\n\nSearching for:', search_str)

            if genius_resp['meta']['status'] != 200:
                raise ValueError('Probably exceeded Genius limits or invalid search')

            genius_resp = genius_resp['response']['hits']
            for hit in genius_resp:
                hit = hit['result']
                song_data = Genius.get_song(hit['id'])['response']['song']
                if 'spotify' in [a['provider'] for a in song_data['media']]:
                    print('Spotify exists!')
                    for i, a in enumerate(song_data['media']):
                        print(a)
                        if a['provider'] == 'spotify':
                            print('Spotify Exists -', song_data['full_title'])
                            spotify_data = Spotify.get_track(song_data['media'][i]['native_uri'])
                            print(spotify_data)
                            break
        quit()
    print(weeks)