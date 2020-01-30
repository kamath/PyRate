from neomodel import StructuredNode, RelationshipFrom

from model.graph import exists


class Billboard(StructuredNode):
    '''
    Represents a Track from Billboard
    '''
    spotify = RelationshipFrom('model.graph.track.Track', 'RANKED AS')


    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e
        raise NotImplementedError('Not fully implemented yet')