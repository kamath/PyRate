from neomodel import StructuredNode, StringProperty, IntegerProperty, FloatProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipTo, db

from model.spotify import exists
from model.spotify.album import Album
from model.spotify.artist import Artist

from scraper.spotify import Spotify


class Track(StructuredNode):
    '''
    Represents a Track on Spotify
    '''
    album = RelationshipTo('model.spotify.json.album.Album', 'FROM')
    artists = RelationshipTo('model.spotify.json.artist.Artist', 'BY')
    playlists = RelationshipTo('model.spotify.json.playlist.Playlist', 'FEATURED IN')

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

    genius_data = JSONProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e

        if 'analysis' not in kwargs:
            kwargs['analysis'] = Spotify.get_audio_analysis(kwargs['uri'])
        if 'features' not in kwargs:
            kwargs['features'] = Spotify.get_audio_features(kwargs['uri'])

        kwargs['features'].pop('id')
        kwargs['features'].pop('uri')
        kwargs['features'].pop('type')
        kwargs['features'].pop('track_href')

        for key, val in kwargs['features'].items():
            kwargs[key] = val

        kwargs.pop('features')

        kwargs['spotify_id'] = kwargs.pop('id')

        album = kwargs.pop('album')
        artists = kwargs.pop('artists')

        obj = cls(**kwargs).save()

        album = Album.inst(**album)
        obj.album.connect(album)

        artists = [Artist.inst(**a) for a in artists]
        for artist in artists:
            obj.artists.connect(artist)

        return obj

    @classmethod
    @db.transaction
    def add_genius(cls, uri, data):
        track = cls.nodes.get_or_none(uri=uri)
        if track:
            track.genius_data = data
            track.save()