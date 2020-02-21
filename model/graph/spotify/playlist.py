from neomodel import RelationshipTo, RelationshipFrom, db
from neomodel import StructuredNode, StringProperty, BooleanProperty, JSONProperty

from model.graph.spotify import SpotifyNode
from model.graph.spotify.user import User

from time import time

from model.graph import connection_url

class Playlist(SpotifyNode):
    '''
    Represents a Playlist on Spotify
    '''

    owner = RelationshipTo('model.graph.spotify.user.User', 'OWNED BY')

    tracks = RelationshipFrom('model.graph.spotify.track.Track', 'FEATURED IN')

    spotify_id = StringProperty(unique_index=True)
    name = StringProperty()
    collaborative = BooleanProperty()
    description = StringProperty()
    external_urls = JSONProperty()
    href = StringProperty()
    images = JSONProperty()
    primary_color = StringProperty()
    public = BooleanProperty()
    snapshot_id = StringProperty()
    type = StringProperty()
    uri = StringProperty()

    @staticmethod
    def post_clean(obj, to_connect: dict):
        from model.graph.spotify.user import User
        owner = to_connect['owner']
        owner = User.inst(**owner)
        obj.owner.connect(owner)
        return obj

    @classmethod
    def clean(cls, **kwargs):
        if 'tracks' in kwargs:
            del kwargs['tracks']
        if 'id' in kwargs:
            kwargs['spotify_id'] = kwargs.pop('id')

        to_connect = {'owner': kwargs.pop('owner')}
        obj = cls(**kwargs)
        return obj, to_connect

    @classmethod
    def get_tracks(cls, spotify_id):
        s = time()
        from model.graph.spotify.track import SmallTrack
        db.set_connection(connection_url())
        query = '''
        MATCH (p: Playlist {spotify_id: "%s"}) <-[r1: `FEATURED IN`]- (t: Track)
        RETURN t.uri, t.zVector, t.spotify_id, t.name
        ''' % spotify_id
        results, meta = db.cypher_query(query)
        print('Results fetched', time() - s)
        keys = ['uri', 'zVector', 'spotify_id', 'name']
        kwargs = [{keys[i]: val for i, val in enumerate(result)} for result in results]

        return [SmallTrack(**result) for result in kwargs]