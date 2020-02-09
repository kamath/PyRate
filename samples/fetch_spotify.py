def main():
    '''
    1) Hits Spotify API to get all of a user's playlists
    2) Converts playlist JSON to playlist nodes
    3) Goes through all the tracks in each playlist and converts them to track objects
    4) Connects the tracks to the playlist
    5) Gets the album for each track
    6) Goes through all the tracks in the album/creates track objects
    7) Connects these tracks to the album
    '''

    from scraper.spotify import Spotify

    from model.spotify.playlist import Playlist
    from model.spotify.track import Track

    from time import sleep
    from tqdm import tqdm

    from neomodel import config
    import json
    import os

    def helper(track):
        track = track['track']
        track_obj = Track.inst(**track)
        for album in track_obj.album:
            for t in Spotify.get_album_tracks(album.uri):
                t['album'] = track['album']
                t = Track.inst(**t)
                t.album.connect(album)
            track_obj.playlists.connect(p)

    neo4j_vars = json.load(open(os.path.join('config', 'neo4j.json'), 'r'))
    user = neo4j_vars['user']
    pw = neo4j_vars['pass']
    dns = neo4j_vars['dns']
    port = neo4j_vars['bolt_port']
    config.DATABASE_URL = f"bolt://{user}:{pw}@{dns}:{port}"

    playlists = Spotify.get_user_playlists()
    user_id = Spotify.get_current_user()['id']

    # Limit to just my playlists and playlists created by Spotify
    playlists = [Playlist.inst(**a) for a in playlists if a['owner']['id'] in (user_id)]#, 'spotify', 'spotifycharts')]

    offset = 0
    for i, p in enumerate(playlists[offset:]):
        print(i + offset, len(playlists))
        sleep_time = .5
        while True:
            try:
                tracks = Spotify.get_playlist_tracks(p.spotify_id)
                break
            except KeyError:
                sleep(sleep_time)
                sleep_time *= 2

        for track in tqdm(tracks):
            if 'spotify:local:' not in track['track']['uri']:
                sleep_time = .5
                while True:
                    try:
                        helper(track)
                        break
                    except KeyError:
                        print(track['track'])
                        print(sleep_time)
                        sleep(sleep_time)
                        sleep_time *= 2
                        if sleep_time > 100:
                            break
            else:
                print("NOT FOUND", track['track'])
