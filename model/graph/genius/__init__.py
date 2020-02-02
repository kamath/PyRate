from model.graph import Node
from typing import *
from neomodel import StructuredNode, StructuredRel, IntegerProperty, FloatProperty

class GeniusNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def inst(cls, **kwargs):
        tor = cls.build(cls, {'genius_id': kwargs['genius_id']}, **kwargs)
        return tor