from neomodel import RelationshipTo, RelationshipFrom
from neomodel import StructuredNode, StringProperty, IntegerProperty, JSONProperty, ArrayProperty

from model.spotify import exists


class Album(StructuredNode):
    artists = RelationshipTo('model.spotify.json.artist.Artist', 'BY')

    tracks = RelationshipFrom('model.spotify.json.track.Track', 'FROM')

    available_markets = ArrayProperty()
    images = JSONProperty()

    album_type = StringProperty()
    release_date = StringProperty()
    external_urls = JSONProperty()
    href = StringProperty()
    spotify_id = StringProperty(unique_index=True)
    name = StringProperty()
    release_date_precision = StringProperty()
    total_tracks = IntegerProperty()
    type = StringProperty()
    uri = StringProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e

        artists = kwargs.pop('artists')

        kwargs['spotify_id'] = kwargs.pop('id')

        obj = cls(**kwargs).save()

        from model.spotify.artist import Artist
        artists = [Artist.inst(**a) for a in artists]
        for artist in artists:
            obj.artists.connect(artist)

        return obj