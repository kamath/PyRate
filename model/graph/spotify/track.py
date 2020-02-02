from neomodel import StructuredNode, StringProperty, IntegerProperty, FloatProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipTo, db

from model.graph.spotify.album import Album
from model.graph.spotify.artist import Artist

from scraper.spotify import Spotify
from model.graph.spotify import SpotifyNode

from typing import *

class Track(SpotifyNode):
    '''
    Represents a Track on Spotify
    '''
    album = RelationshipTo('model.graph.spotify.album.Album', 'FROM')
    artists = RelationshipTo('model.graph.spotify.artist.Artist', 'BY')
    playlists = RelationshipTo('model.graph.spotify.playlist.Playlist', 'FEATURED IN')

    # billboard_data = RelationshipTo('model.graph.billboard.track.Track', 'RANKED AS')
    # genius_data = RelationshipTo('model.graph.genius.track.Track', 'ON GENIUS AS')

    available_markets = ArrayProperty()
    disc_number = IntegerProperty()
    duration_ms = IntegerProperty()
    explicit = BooleanProperty()
    external_ids = JSONProperty()
    external_urls = ArrayProperty()
    href = StringProperty()
    spotify_id = StringProperty(unique_index=True)
    is_local = BooleanProperty()
    name = StringProperty()
    popularity = IntegerProperty()
    preview_url = StringProperty()
    track_number = IntegerProperty()
    type = StringProperty()
    uri = StringProperty(unique_index=True)

    # We can worry about analysis at a later point
    analysis = JSONProperty()

    # Features
    key = IntegerProperty()
    mode = IntegerProperty()
    time_signature = IntegerProperty()
    acousticness = FloatProperty()
    danceability = FloatProperty()
    energy = FloatProperty()
    instrumentalness = FloatProperty()
    liveness = FloatProperty()
    loudness = FloatProperty()
    speechiness = FloatProperty()
    valence = FloatProperty()
    tempo = FloatProperty()
    analysis_url = StringProperty()

    @staticmethod
    def post_clean(obj, to_connect):
        album = to_connect['album']
        artists = to_connect['artists']

        album = Album.inst(**album)
        obj.album.connect(album)

        artists = [Artist.inst(**a) for a in artists]
        for artist in artists:
            obj.artists.connect(artist)

        return obj

    @classmethod
    def clean(cls, **kwargs):
        if 'analysis' not in kwargs:
            kwargs['analysis'] = Spotify.get_audio_analysis(kwargs['uri'])
        if 'features' not in kwargs:
            kwargs['features'] = Spotify.get_audio_features(kwargs['uri'])

        if 'id' in kwargs['features']:
            kwargs['features']['spotify_id'] = kwargs['features'].pop('id')

        kwargs['features'].pop('spotify_id')
        kwargs['features'].pop('uri')
        kwargs['features'].pop('type')
        kwargs['features'].pop('track_href')

        for key, val in kwargs['features'].items():
            kwargs[key] = val

        kwargs.pop('features')

        if 'id' in kwargs:
            kwargs['spotify_id'] = kwargs.pop('id')

        to_connect = {}
        to_connect['album'] = kwargs.pop('album')
        to_connect['artists'] = kwargs.pop('artists')

        obj = cls(**kwargs)
        return obj, to_connect

    @classmethod
    @db.transaction
    def add_genius(cls, uri, data):
        track = cls.nodes.get_or_none(uri=uri)
        if track:
            track.genius_data = data
            track.save()