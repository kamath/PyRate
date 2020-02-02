from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph import Credited


class Track(StructuredNode):
    '''
    Represents a Track from Billboard
    '''
    spotify = RelationshipFrom('model.graph.spotify.track.Track', 'RANKED AS')
    artists = RelationshipTo('model.graph.spotify.artist.Artist', 'BY', model=Credited)

    credited_writers = ArrayProperty()
    credited_producers = ArrayProperty()
    publishers = ArrayProperty()
    labels = ArrayProperty()

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
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e
        raise NotImplementedError('Not fully implemented yet')