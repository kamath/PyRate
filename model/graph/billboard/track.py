from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph import Credited
from model.graph.billboard import BillboardNode

from typing import *
from ast import literal_eval

class Track(BillboardNode):
    '''
    Represents a Track from Billboard
    '''
    spotify = RelationshipFrom('model.graph.genius.track.Track', 'RANKED AS')
    # artists = RelationshipTo('model.graph.spotify.artist.Artist', 'BY', model=Credited)

    credited_writers = JSONProperty()
    credited_producers = JSONProperty()
    publishers = JSONProperty()
    labels = JSONProperty()

    rank = IntegerProperty()
    title_id = IntegerProperty(unique_index=True)
    title = StringProperty()

    imprint = StringProperty()
    label = StringProperty()
    feature_code = StringProperty()
    history = JSONProperty()
    bullets = JSONProperty()
    awards = JSONProperty()
    bdssongid = IntegerProperty(unique_index=True)
    title_vevo_id = StringProperty()
    title_brightcove_id = FloatProperty()
    title_content_url = StringProperty()
    title_images = JSONProperty()
    title_brightcove_data = JSONProperty()
    brightcove_data = JSONProperty()
    content_url = StringProperty()
    canonical = StringProperty(unique_index=True)
    peak_date_formatted = JSONProperty()
    peak_date_link = StringProperty()

    @classmethod
    def exists(cls, identifier):
        return cls.nodes.get_or_none(title_id=identifier.get('title_id'))

    @classmethod
    def inst(cls, **kwargs):
        tor = cls.build(cls, {'title_id': kwargs['title_id']}, **kwargs)
        return tor

    @classmethod
    def clean(cls, **kwargs) -> Tuple[StructuredNode, Dict[str, dict]]:
        to_del = [key for key in kwargs.keys() if 'unnamed' in key.lower() or 'artist_' in key.lower()]
        for item in to_del:
            kwargs.pop(item)
        kwargs['history'] = literal_eval(kwargs['history'])
        kwargs['credited_artists'] = literal_eval(kwargs['credited_artists'])
        kwargs['credited_writers'] = literal_eval(kwargs['credited_writers'])
        kwargs['credited_producers'] = literal_eval(kwargs['credited_producers'])
        kwargs['awards'] = literal_eval(kwargs['awards'])
        kwargs['title_images'] = literal_eval(kwargs['title_images'])
        kwargs['publishers'] = literal_eval(kwargs['publishers'])
        kwargs['title_brightcove_data'] = literal_eval(kwargs['title_brightcove_data'])
        kwargs['brightcove_data'] = literal_eval(kwargs['brightcove_data'])
        kwargs['peak_date_formatted'] = literal_eval(kwargs['peak_date_formatted'])
        return cls(**kwargs), {}

    @staticmethod
    def post_clean(obj, to_connect: dict) -> StructuredNode:
        return obj