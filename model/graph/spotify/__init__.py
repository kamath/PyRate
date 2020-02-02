from model.graph import Node

class SpotifyNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def exists(cls, identifier):
        return cls.nodes.get_or_none(spotify_id=identifier.get('spotify_id'))

    @classmethod
    def inst(cls, **kwargs):
        if 'id' in kwargs:
            kwargs['spotify_id'] = kwargs.pop('id')
        tor = Node.build(cls, {'spotify_id': kwargs.get('spotify_id')}, **kwargs)
        return tor