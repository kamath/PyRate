from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph.billboard import Credited
from model.graph.billboard import BillboardNode
from typing import *

class Producer(BillboardNode):
    '''
    Represents a Producer from Billboard
    '''
    tracks = RelationshipFrom('model.graph.billboard.track.Track', 'PRODUCED BY', model=Credited)

    producer_id = IntegerProperty(unique_index=True)
    producer_name = StringProperty()
    producer_short_name = StringProperty()

    @classmethod
    def inst(cls, **kwargs):
        tor = cls.build(cls, {'producer_id': kwargs['producer_id']}, **kwargs)
        return tor

    @classmethod
    def exists(cls, identifier):
        return cls.nodes.get_or_none(producer_id=identifier.get('producer_id'))