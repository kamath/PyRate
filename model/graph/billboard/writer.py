from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph.billboard import Credited
from model.graph.billboard import BillboardNode
from typing import *

class Writer(BillboardNode):
    '''
    Represents a Writer from Billboard
    '''
    tracks = RelationshipFrom('model.graph.billboard.track.Track', 'WRITTEN BY', model=Credited)

    writer_id = IntegerProperty(unique_index=True)
    writer_name = StringProperty()
    writer_short_name = StringProperty()

    @classmethod
    def exists(cls, identifier):
        return cls.nodes.get_or_none(writer_id=identifier.get('writer_id'))

    @classmethod
    def inst(cls, **kwargs):
        tor = cls.build(cls, {'writer_id': kwargs['writer_id']}, **kwargs)
        return tor