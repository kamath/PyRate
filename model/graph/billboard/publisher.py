from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph.billboard import Credited
from model.graph.billboard import BillboardNode
from typing import *

class Publisher(BillboardNode):
    '''
    Represents a Publisher from Billboard
    '''
    tracks = RelationshipFrom('model.graph.billboard.track.Track', 'PUBLISHED BY', model=Credited)

    publisher_id = IntegerProperty(unique_index=True)
    publisher_name = StringProperty()

    @classmethod
    def clean(cls, **kwargs) -> Tuple[StructuredNode, Dict[str, dict]]:
        kwargs['publisher_id'] = kwargs.pop('id')
        return cls(**kwargs), {}

    @classmethod
    def exists(cls, identifier):
        return cls.nodes.get_or_none(publisher_id=identifier.get('publisher_id'))

    @classmethod
    def inst(cls, **kwargs):
        tor = cls.build(cls, {'publisher_id': kwargs['id']}, **kwargs)
        return tor