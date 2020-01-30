from neomodel import RelationshipTo, RelationshipFrom
from neomodel import StructuredNode, StringProperty, BooleanProperty, JSONProperty

from model.graph import exists
from model.graph.spotify.user import User


class Playlist(StructuredNode):
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

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e

        if 'tracks' in kwargs:
            del kwargs['tracks']

        owner = kwargs.pop('owner')
        kwargs['spotify_id'] = kwargs.pop('id')

        obj = cls(**kwargs).save()

        owner = User.inst(**owner)
        obj.owner.connect(owner)

        return obj

