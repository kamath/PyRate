from neomodel import RelationshipFrom
from neomodel import StructuredNode, StringProperty, JSONProperty

from model.graph.spotify import SpotifyNode

class User(SpotifyNode):
    '''
    Represents a user on Spotify as per Spotify API
    '''

    playlists = RelationshipFrom('model.graph.spotify.playlist.Playlist', 'OWNED BY')

    display_name = StringProperty()
    external_urls = JSONProperty()
    href = StringProperty()
    spotify_id = StringProperty(unique_index=True)
    type = StringProperty()
    uri = StringProperty()

    @classmethod
    def clean(cls, **kwargs):
        if 'id' in kwargs:
            kwargs['spotify_id'] = kwargs.pop('id')
        return cls(**kwargs), {}