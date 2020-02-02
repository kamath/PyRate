from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph.billboard import Credited
from model.graph.billboard import BillboardNode
from typing import *

class Artist(BillboardNode):
    '''
    Represents an Artist from Billboard
    '''
    tracks = RelationshipFrom('model.graph.billboard.track.Track', 'PERFORMED BY', model=Credited)

    artist_id = IntegerProperty(unique_index=True)
    artist_name = StringProperty()
    artist_slug = StringProperty(unique_index=True)

    @classmethod
    def exists(cls, identifier):
        return cls.nodes.get_or_none(artist_id=identifier.get('artist_id'))

    @classmethod
    def inst(cls, **kwargs):
        tor = cls.build(cls, {'artist_id': kwargs['artist_id']}, **kwargs)
        return tor