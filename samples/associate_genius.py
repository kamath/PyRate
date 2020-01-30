def main():
    '''
    Gets all the albums in the database, loops through associated tracks, and searches Genius
        - if Spotify URI is included in Genius data, the node is updated to include Genius data
    :return:
    '''
    from time import sleep

    from neomodel import config

    from scraper.genius import Genius

    from model.graph import connection_url
    from model.graph.spotify.track import Track
    from model.graph.spotify.album import Album

    config.DATABASE_URL = connection_url()
    print(len(Album.nodes))
    for i, node in enumerate(Album.nodes):
        if i > 5:
            break

        print('\n\nCurrent Album:', node.name)
        for track in node.tracks:
            to_search = f'{track.name} {track.artists[0].name}'
            print('\nSearching for', to_search)
            resp = Genius.search(to_search)
            print(resp)
            if resp['meta']['status'] == 200:
                resp = resp['response']
                if 'hits' in resp:
                    for hit in resp['hits']:
                        song_data = Genius.get_song(hit['result']['id'])['response']['song']
                        print(song_data['media'])
                        if 'spotify' in [a['provider'] for a in song_data['media']]:
                            print('Spotify exists!')
                            for i, a in enumerate(song_data['media']):
                                print(a)
                                if a['provider'] == 'spotify':
                                    in_db = Track.nodes.get_or_none(uri=song_data['media'][i]['native_uri'])
                                    if in_db:
                                        print('Track exists:', in_db.name)
                                    else:
                                        print('Track is not in database')
                                    Track.add_genius(song_data['media'][i]['native_uri'], song_data)
                                    new_track = Track.nodes.get_or_none(uri=song_data['media'][i]['native_uri'])
                                    if new_track:
                                        print('Track updated', new_track.genius_data)
                                    else:
                                        print('Track not updated', new_track)
                        sleep(1)