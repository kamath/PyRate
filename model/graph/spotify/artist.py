from neomodel import RelationshipFrom, db
from neomodel import StructuredNode, StringProperty, JSONProperty, IntegerProperty, FloatProperty

from model.graph.spotify import SpotifyNode
from model.graph import connection_url

class Artist(SpotifyNode):
    '''
    Represents an artist on Spotify as per Spotify API
    '''

    tracks = RelationshipFrom('model.graph.spotify.track.Track', 'BY')
    albums = RelationshipFrom('model.graph.spotify.album.Album', 'BY')

    external_urls = JSONProperty()
    href = StringProperty()
    spotify_id = StringProperty(unique_index=True)
    name = StringProperty()
    type = StringProperty()
    uri = StringProperty()

    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def clean(cls, **kwargs):
        if 'id' in kwargs:
            kwargs['spotify_id'] = kwargs.pop('id')
        obj = cls(**kwargs)
        return obj, {}

    @classmethod
    def add_billboard(cls, **kwargs):
        kwargs = {key.replace('artist_', 'billboard_'): val for key, val in kwargs.items()}
        raise NotImplementedError

    @classmethod
    def get_associated_artists(cls, artist_id):
        '''
        Gets artists associated with the given artist

        :param artist_id: the Spotify ID of the given artist
        :return: the list of associated artists
        '''
        db.set_connection(connection_url())
        results, meta = db.cypher_query('''
        MATCH (a: Artist {spotify_id: "%s"}) <-[r1: BY]- 
            (t: Track) -[r2: BY]-> 
            (similar_artists: Artist)
        RETURN similar_artists
        ''' % artist_id)

        return set([cls.inflate(artist[0]) for artist in results])

    @classmethod
    def get_tracks_with_multiple_artists(cls, *artist_ids):
        '''
        Gets tracks with multiple artists on it

        :param artist_ids: the given
        :return:
        '''
        artists = ','.join(["(a%s:Artist { uri: '%s' })" % (i, a) for i, a in enumerate(artist_ids)])
        query_constructor = f'''MATCH {artists}, 
        p = allShortestPaths((a0)-[*]-(a1))
        RETURN nodes(p)
        '''
        from model.graph.spotify.track import Track
        db.set_connection(connection_url())
        results, meta = db.cypher_query(query_constructor)
        return [Track.inflate(result[0][1]) for result in results]