import json
import requests
import base64
from datetime import datetime, timedelta
from typing import *
import os

class Spotify:
    @classmethod
    def refresh_token(cls) -> json:
        '''
        Refreshes the access token

        :return: the new data
        '''

        access = json.load(open(os.path.join('config', 'spotify.json'), 'r'))
        CLIENT_ID = access['CLIENT_ID']
        CLIENT_SECRET = access['CLIENT_SECRET']
        auth_str = bytes('{}:{}'.format(CLIENT_ID, CLIENT_SECRET), 'utf-8')
        b64_auth_str = base64.b64encode(auth_str).decode('utf-8')

        response = requests.post('https://accounts.spotify.com/api/token',
                                 headers={'Authorization': f'Basic {b64_auth_str}'},
                                 data={"grant_type": "refresh_token",
                                       'refresh_token': access['REFRESH_TOKEN']})
        data = json.loads(response.text)
        data['CLIENT_ID'] = CLIENT_ID
        data['CLIENT_SECRET'] = CLIENT_SECRET
        data['EXPIRES'] = str(datetime.now() + timedelta(seconds=3600))
        data['REFRESH_TOKEN'] = access['REFRESH_TOKEN']

        # Saves the new access data
        open(os.path.join('config', 'spotify.json'), 'w').write(json.dumps(data))
        return data

    def __init__(self):
        '''
        Initializes the Spotify class. Every method aims to be a class object that initializes this every time so
        if the access token expires, the constructor automatically updates the access token using the refresh token
        '''
        access = json.load(open(os.path.join('config', 'spotify.json'), 'r'))
        expires = datetime.strptime(access['EXPIRES'], "%Y-%m-%d %H:%M:%S.%f")
        if datetime.now() > expires:
            self.data = self.refresh_token()
        else:
            self.data = access

    def _ping_spotify(self, endpoint: str, **data):
        ACCESS_TOKEN=self.data['access_token']
        resp = requests.get(f'https://api.spotify.com/v1/{endpoint}', headers=
            {'Authorization': f'Bearer {ACCESS_TOKEN}'})
        return resp.json()

    @staticmethod
    def track_id(spotify_uri: str):
        '''
        Gets the track ID given the Spotify URI

        :param spotify_uri: the Spotify URI to get the ID of
        :return: the track ID (split at colon and alst value)
        '''
        return spotify_uri.split(':')[-1]

    @staticmethod
    def user_endpoint(user_uri: str=None):
        if user_uri:
            user_uri = f'users/{Spotify.track_id(user_uri)}'
        else:
            user_uri = 'me'
        return user_uri

    @classmethod
    def get_all(cls, endpoint: str) -> List[dict]:
        '''
        Get all data when involving lists (get all playlists, get all tracks in a playlist, etc.)

        :param endpoint: the endpoint to fetch
        :return: the resulting json
        '''
        fetched = 0
        items = []
        offset = 0
        while True:
            data = cls()._ping_spotify(f'{endpoint}?offset={offset}')
            items += data['items']
            fetched += len(data['items'])
            next_item = data['next']
            if next_item:
                offset = int(data['next'].split('?')[-1].split('&')[0].split('=')[-1])
            else:
                break
            # Don't abuse rate limits
        return items

    @classmethod
    def get_audio_features(cls, spotify_uri: str) -> json:
        '''
        Gets the audio features for the given track

        :param spotify_uri: the Spotify URI to fetch details for
        :return: the resulting json data
        '''
        spotify_id = Spotify.track_id(spotify_uri)
        return cls()._ping_spotify(f'audio-features/{spotify_id}')

    @classmethod
    def get_audio_analysis(cls, spotify_uri: str) -> json:
        '''
        Gets the audio analysis for the given track

        :param spotify_uri: the Spotify URI to fetch details for
        :return: the resulting json data
        '''
        spotify_id = Spotify.track_id(spotify_uri)
        return cls()._ping_spotify(f'audio-analysis/{spotify_id}')

    @classmethod
    def get_playlist_tracks(cls, playlist_uri: str) -> List[dict]:
        '''
        Gets the tracks in the given playlist from Spotify

        :param playlist_uri: the playlist URI
        :param offset: the offset
        :return: the resulting json data
        '''
        playlist_id = Spotify.track_id(playlist_uri)
        return Spotify.get_all(f'playlists/{playlist_id}/tracks')

    @classmethod
    def analyze_playlist(cls, playlist_uri: str) -> List[dict]:
        '''
        Gets the audio analyses and features for each song in a given playlist

        :param playlist_uri: the playlist uri
        :return: the resulting json data
        '''
        return Spotify.get_playlist_tracks(playlist_uri)

    @classmethod
    def get_user_playlists(cls, user_uri:str=None) -> List[dict]:
        '''
        Gets all of a user's playlists. Defaults to current user if user_uri not provided

        :param user_uri: the user URI to fetch playlists of (default /me)
        :return: the resulting JSON
        '''
        user_uri = Spotify.user_endpoint(user_uri)
        return Spotify.get_all(f'{user_uri}/playlists')

    @classmethod
    def get_features_for_tracks(cls, *track_uris) -> List[dict]:
        '''
        Gets the audio features for several tracks

        :param track_uris: the Spotify URIs of multiple tracks
        :return: the resulting JSON
        '''
        ids = list(map(Spotify.track_id, track_uris))
        ids = '%2C'.join(ids)
        d = cls()._ping_spotify(f'audio-features?ids={ids}')
        return d['audio_features']

    @classmethod
    def get_current_user(cls) -> json:
        '''
        Gets the current user's Spotify user data

        :return: the resulting JSON
        '''
        return cls()._ping_spotify('me')

    @classmethod
    def get_album_tracks(cls, spotify_uri: str) -> List[dict]:
        '''
        Gets the tracks in a given album

        :param spotify_uri: the Spotify URI of the album
        :return: the tracks in the album
        '''
        return cls().get_all(f'albums/{cls.track_id(spotify_uri)}/tracks')

    @classmethod
    def get_track(cls, spotify_uri: str) -> json:
        '''
        Gets track info given spotify_uri
        :param spotify_uri: the Spotify URI of the track
        :return: the resulting json
        '''
        return cls()._ping_spotify(f'tracks/{cls.track_id(spotify_uri)}')

    @classmethod
    def get_currently_playing(cls) -> json:
        '''
        Gets currently playing data
        :return: the currently playing data
        '''
        return cls()._ping_spotify('me/player/currently-playing')

    @classmethod
    def get_artists(cls, uris: List[str]) -> json:
        '''
        Gets artist data given the Spotify URI

        :param uris: the list of Spotify URIs of the artists
        :return: the resulting JSON data
        '''
        tor = cls()._ping_spotify('artists?ids='+'%2C'.join(list(map(cls.track_id, uris))[:45]))
        return tor['artists']

    @classmethod
    def play(cls, **data):
        access_token = cls().data['access_token']
        response = requests.put('https://api.spotify.com/v1/me/player/play',
                                headers={'Authorization': f'Bearer {access_token}'}, data=json.dumps(data))
        return response