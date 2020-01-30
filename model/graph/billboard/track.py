from neomodel import StructuredNode, StringProperty, IntegerProperty, FloatProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipTo, RelationshipFrom, db
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

        if 'analysis' not in kwargs:
            kwargs['analysis'] = Spotify.get_audio_analysis(kwargs['uri'])
        if 'features' not in kwargs:
            kwargs['features'] = Spotify.get_audio_features(kwargs['uri'])

        kwargs['features'].pop('id')
        kwargs['features'].pop('uri')
        kwargs['features'].pop('type')
        kwargs['features'].pop('track_href')

        for key, val in kwargs['features'].items():
            kwargs[key] = val

        kwargs.pop('features')

        kwargs['spotify_id'] = kwargs.pop('id')

        album = kwargs.pop('album')
        artists = kwargs.pop('artists')

        obj = cls(**kwargs).save()

        album = Album.inst(**album)
        obj.album.connect(album)

        artists = [Artist.inst(**a) for a in artists]
        for artist in artists:
            obj.artists.connect(artist)

        return obj

    @classmethod
    @db.transaction
    def add_genius(cls, uri, data):
        track = cls.nodes.get_or_none(uri=uri)
        if track:
            track.genius_data = data
            track.save()