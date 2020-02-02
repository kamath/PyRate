from neomodel import RelationshipFrom
from neomodel import StructuredNode, StringProperty, JSONProperty, IntegerProperty, FloatProperty

from model.graph import Credited
from model.graph.spotify import SpotifyNode

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

    billboard_tracks = RelationshipFrom('model.graph.billboard.track.Track', 'BY', model=Credited)

    billboard_slug = StringProperty(unique_index=True)
    billboard_type = StringProperty()
    billboard_id = IntegerProperty(unique_index=True)
    billboard_name = StringProperty()
    billboard_vevo_id = FloatProperty(unique_index=True)
    billboard_brightcove_id = FloatProperty()
    billboard_content_url = StringProperty()
    billboard_images = JSONProperty()
    billboard_brightcove_data = JSONProperty()
    billboard_url = StringProperty(unique_index=True)

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