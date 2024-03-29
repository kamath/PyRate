from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph.billboard import Credited
from model.graph.billboard import BillboardNode
from typing import *

class Label(BillboardNode):
    '''
    Represents a Label from Billboard
    '''
    tracks = RelationshipFrom('model.graph.billboard.track.Track', 'DISTRIBUTED BY', model=Credited)

    label_id = IntegerProperty(unique_index=True)
    label_name = StringProperty()

    @classmethod
    def clean(cls, **kwargs) -> Tuple[StructuredNode, Dict[str, dict]]:
        kwargs['label_id'] = kwargs.pop('id')
        return cls(**kwargs), {}

    @classmethod
    def exists(cls, identifier):
        return cls.nodes.get_or_none(label_id=identifier.get('label_id'))

    @classmethod
    def inst(cls, **kwargs):
        tor = cls.build(cls, {'label_id': kwargs['id']}, **kwargs)
        return tor