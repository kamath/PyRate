from neomodel import StructuredNode, StringProperty, IntegerProperty, FloatProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipTo, db

from model.graph import connection_url
from model.graph.spotify.album import Album
from model.graph.spotify.artist import Artist
from model.graph.spotify.playlist import Playlist

from scraper.spotify import Spotify
from model.graph.spotify import SpotifyNode

from ast import literal_eval as eval
import json

from typing import *

class SmallTrack(SpotifyNode):
    '''
    Doesn't load all the heavy shit to speed up queries
    '''
    uri = StringProperty(unique_index=True)
    # Property for z-Vectors - lists of lists aren't allowed, so it's stored as a JSON with key 'zVector'
    zVector = JSONProperty()
    spotify_id = StringProperty(unique_index=True)
    name = StringProperty()

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

    @classmethod
    def find(cls, uri: str):
        '''
        Finds a track given Spotify URI
        :param uri: the Spotify URI
        :return: the track
        '''
        db.set_connection(connection_url())
        results, meta = db.cypher_query(query='''
                    MATCH(t: Track {uri: "%s"}) RETURN t
                    ''' % (uri))
        return [cls.inflate(track[0]) for track in results]

class Track(SmallTrack):
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
    is_local = BooleanProperty()
    preview_url = StringProperty()
    track_number = IntegerProperty()
    type = StringProperty()

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
    popularity = IntegerProperty()


    @classmethod
    @db.transaction
    def add_genius(cls, uri, data):
        '''
        Updates a node to add Genius data

        :param uri: the Spotify URI of the track
        :param data: the genius data
        :return: the updated node
        '''
        track = cls.nodes.get_or_none(uri=uri)
        if track:
            track.genius_data = data
            track.save()
        return track

    @classmethod
    def add_zVector(cls, uri, data: List[List[float]]):
        '''
        Adds zVector data to the track

        :param uri: the Spotify URI of the track
        :param data: the zVector data as a list of lists, not a numpy array
        :return: the updated node
        '''
        # print(uri)
        db.set_connection(connection_url())
        # query = 'MATCH (n: Track {uri: "%s"}) RETURN n LIMIT 1' % (uri)
        # results, meta = db.cypher_query(query=query)
        # track = [cls.inflate(row[0]) for row in results]
        #
        # if track:
        #     track = track[0]
        # print(track.name)
        # print('Please save', track)

        # fuck neomodel ffs
        data = json.dumps({'zVector': data})

        query = '''
            MATCH (t:Track {uri:'%s'})
            WITH t, properties(t) as snapshot
            SET t.zVector = '%s'
            RETURN snapshot
            ''' % (uri, data)
        # print(query)
        track = db.cypher_query(query)
        return track

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

    @classmethod
    def get_songs_not_in_playlists(cls, limit, offset=0):
        '''
        Gets only songs that appear in playlists

        :return: the query to do that
        '''
        query = '''
                MATCH (t: Track) WHERE NOT EXISTS (t.zVector) RETURN t
                '''
        return cls.paginate(limit, offset, query)