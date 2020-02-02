from model.graph import Node
from typing import *
from neomodel import StructuredNode, StructuredRel, IntegerProperty, FloatProperty

class GeniusNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def inst(cls, **kwargs):
        if 'genius_id' not in kwargs:
            kwargs['genius_id'] = kwargs['id']
        tor = cls.build(cls, {'genius_id': kwargs['genius_id']}, **kwargs)
        return tor

    @classmethod
    def exists(cls, identifier):
        return cls.nodes.get_or_none(genius_id=identifier.get('genius_id'))