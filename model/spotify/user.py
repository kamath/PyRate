from collections import namedtuple
from typing import *

from neomodel import StructuredNode, StringProperty, IntegerProperty, FloatProperty, BooleanProperty, JSONProperty, ArrayProperty
from neomodel import RelationshipTo, RelationshipFrom, config
from model.spotify import exists

class User(StructuredNode):
    '''
    Represents a user on Spotify as per Spotify API
    '''

    playlists = RelationshipFrom('model.spotify.playlist.Playlist', 'OWNED BY')

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