from neomodel import RelationshipFrom
from neomodel import StructuredNode, StringProperty, JSONProperty

from model.graph import exists


class User(StructuredNode):
    '''
    Represents a user on Spotify as per Spotify API
    '''

    playlists = RelationshipFrom('model.graph.playlist.Playlist', 'OWNED BY')

    display_name = StringProperty()
    external_urls = JSONProperty()
    href = StringProperty()
    spotify_id = StringProperty(unique_index=True)
    type = StringProperty()
    uri = StringProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e

        kwargs['spotify_id'] = kwargs.pop('id')
        return cls(**kwargs).save()