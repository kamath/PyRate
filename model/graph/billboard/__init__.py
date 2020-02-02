from model.graph import Node
from typing import *
from neomodel import StructuredNode, StructuredRel, IntegerProperty, FloatProperty

class BillboardNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Credited(StructuredRel):
    ordinal = IntegerProperty()
    credit = FloatProperty()