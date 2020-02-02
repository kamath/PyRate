from neomodel import RelationshipTo, RelationshipFrom
from neomodel import StringProperty, IntegerProperty, JSONProperty, ArrayProperty

from model.graph.spotify import SpotifyNode


class Album(SpotifyNode):
    artists = RelationshipTo('model.graph.spotify.artist.Artist', 'BY')

    tracks = RelationshipFrom('model.graph.spotify.track.Track', 'FROM')

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

    @staticmethod
    def post_clean(obj, to_connect: dict):
        from model.graph.spotify.artist import Artist

        artists = [Artist.inst(**a) for a in to_connect['artists']]
        for artist in artists:
            obj.artists.connect(artist)

        return obj

    @classmethod
    def clean(cls, **kwargs):
        to_connect = {'artists': kwargs.pop('artists')}
        if 'id' in kwargs:
            kwargs['spotify_id'] = kwargs.pop('id')
        obj = cls(**kwargs)
        return obj, to_connect