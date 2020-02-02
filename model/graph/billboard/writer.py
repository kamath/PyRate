from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph import Credited


class Writer(StructuredNode):
    '''
    Represents a Writer from Billboard
    '''
    tracks = RelationshipFrom('model.graph.billboard.track.Track', 'WRITTEN BY', model=Credited)

    writer_id = IntegerProperty(unique_index=True)
    writer_name = StringProperty()
    writer_short_name = StringProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('writer_id'))
        if e:
            return e

        return cls(**kwargs)