from neomodel import RelationshipFrom
from neomodel import StructuredNode, StringProperty, JSONProperty

from model.spotify import exists


class Artist(StructuredNode):
    '''
    Represents an artist on Spotify as per Spotify API
    '''

    tracks = RelationshipFrom('model.spotify.track.Track', 'BY')
    albums = RelationshipFrom('model.spotify.album.Album', 'BY')

    external_urls = JSONProperty()
    href = StringProperty()
    spotify_id = StringProperty(unique_index=True)
    name = StringProperty()
    type = StringProperty()
    uri = StringProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e
        kwargs['spotify_id'] = kwargs.pop('id')
        return cls(**kwargs).save()