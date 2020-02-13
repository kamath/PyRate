from neomodel import StructuredNode, StringProperty, IntegerProperty, FloatProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipTo, db

from model.graph import connection_url
from model.graph.spotify.album import Album
from model.graph.spotify.artist import Artist
from model.graph.spotify.playlist import Playlist

from scraper.spotify import Spotify
from model.graph.spotify import SpotifyNode

from ast import literal_eval as eval

from typing import *

class Track(SpotifyNode):
    '''
    Represents a Track on Spotify
    '''
    album = RelationshipTo('model.graph.spotify.album.Album', 'FROM')
    artists = RelationshipTo('model.graph.spotify.artist.Artist', 'BY')
    playlists = RelationshipTo('model.graph.spotify.playlist.Playlist', 'FEATURED IN')

    # billboard_data = RelationshipTo('model.graph.billboard.track.Track', 'RANKED AS')
    genius_data = RelationshipTo('model.graph.genius.track.Track', 'ON GENIUS AS')

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

    def get_song_features(self, as_list=False):
        '''
        Gets the song features as a dictionary

        :param as_list: whether to return a list or dictionary
        :return: the song features
        '''
        cols = ['key', 'mode', 'time_signature', 'acousticness', 'danceability', 'energy', 'instrumentalness',
            'liveness', 'loudness', 'speechiness', 'valence', 'tempo', 'popularity']
        tor = self.get_features(cols)
        for key, val in tor.items():
            if val is None:
                tor[key] = 0
        if as_list:
            return [tor[a] for a in cols]
        return tor

    @classmethod
    def get_songs_in_playlists(cls, limit, offset=0):
        '''
        Gets only songs that appear in playlists

        :return: the query to do that
        '''
        query = '''
        MATCH (t: Track)-[r:`FEATURED IN`]->(p: Playlist)
        WITH t, count(r) as playlist_count
        WHERE playlist_count > 0
        RETURN t
        '''
        return cls.paginate(limit, offset, query)

    @staticmethod
    def get_playlists(spotify_id) -> List[Playlist]:
        '''
        Gets playlists the given track appears in
        :param spotify_id: the Spotify ID of the track
        :return: the list of playlists that the track appears in
        '''
        db.set_connection(connection_url())
        results, meta = db.cypher_query('MATCH (t:Track {spotify_id: "%s"})-[:`FEATURED IN`]->(p:Playlist) RETURN p'
                                        % spotify_id)
        return [Playlist.inflate(row[0]) for row in results]

    @staticmethod
    def get_similar_playlists(track_id: str, playlist_id: str) -> List[Playlist]:
        '''
        Gets similar playlists to the given playlist
        :param track_id: the Spotify ID of the track currently playing
        :param playlist_id: the Spotify ID of the playlist currently playing
        :return: a list of similar playlists
        '''
        query = '''
        match 
            (t: Track {spotify_id: "%s"}) -[r1:`FEATURED IN`]-> 
            (p: Playlist {spotify_id: "%s"}) <-[r2:`FEATURED IN`]- 
            (other_tracks: Track) -[r3:`FEATURED IN`]-> 
            (similar_playlists: Playlist)  
        return similar_playlists
        ''' % (track_id, playlist_id)
        db.set_connection(connection_url())
        results, meta = db.cypher_query(query=query)
        return [Playlist.inflate(playlist[0]) for playlist in results]

    @staticmethod
    def get_album(track_id: str):
        '''
        Gets the album given the Spotify ID
        :param track_id: the Spotify ID of the track
        :return: the album it's on
        '''
        db.set_connection(connection_url())
        results, meta = db.cypher_query(query='''
        MATCH(t: Track {spotify_id: "%s"})-[:FROM]->(a: Album) RETURN a
        ''' % (track_id))
        return [Album.inflate(album[0]) for album in results]