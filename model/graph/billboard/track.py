from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty, FloatProperty, RelationshipTo

from model.graph.billboard import Credited
from model.graph.billboard import BillboardNode
from model.graph.billboard.artist import Artist
from model.graph.billboard.producer import Producer
from model.graph.billboard.writer import Writer
from model.graph.billboard.publisher import Publisher
from model.graph.billboard.label import Label

from scraper.genius import Genius
from scraper.spotify import Spotify

from typing import *
from ast import literal_eval

class Track(BillboardNode):
    '''
    Represents a Track from Billboard
    '''
    spotify = RelationshipFrom('model.graph.genius.track.Track', 'RANKED AS')
    # artists = RelationshipTo('model.graph.spotify.artist.Artist', 'BY', model=Credited)

    credited_artists = RelationshipTo('model.graph.billboard.artist.Artist', 'PERFORMED BY', model=Credited)
    credited_writers = RelationshipTo('model.graph.billboard.writer.Writer', 'WRITTEN BY', model=Credited)
    credited_producers = RelationshipTo('model.graph.billboard.producer.Producer', 'PRODUCED BY', model=Credited)
    publishers = RelationshipTo('model.graph.billboard.publisher.Publisher', 'PUBLISHED BY', model=Credited)
    labels = RelationshipTo('model.graph.billboard.label.Label', 'DISTRIBUTED BY', model=Credited)

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
        print(kwargs['awards'])

        to_del = [key for key in kwargs.keys() if 'unnamed' in key.lower() or 'artist_' in key.lower()]

        to_eval = ('history', 'credited_artists', 'credited_writers', 'credited_producers', 'awards', 'title_images',
                   'publishers', 'title_brightcove_data', 'brightcove_data', 'peak_date_formatted', 'labels')

        for val in to_eval:
            kwargs[val] = literal_eval(kwargs[val])

        actually_nodes = ('credited_artists', 'credited_writers', 'credited_producers', 'publishers', 'labels')
        to_connect = {}

        for node in actually_nodes:
            to_connect[node] = kwargs.pop(node)

        return cls(**kwargs), to_connect

    @staticmethod
    def post_clean(obj, to_connect: dict) -> StructuredNode:
        actually_nodes = ('credited_artists', 'credited_writers', 'credited_producers', 'publishers', 'labels')
        node_classes = (Artist, Writer, Producer, Publisher, Label)

        artists = ', '.join(list(map(lambda x: x['artist_name'],
                                     sorted(to_connect['credited_artists'], key=lambda x: x['ordinal']))))

        for cls, node_name in zip(node_classes, actually_nodes):
            node = to_connect[node_name]
            for item in node:
                if 'credit' not in item:
                    item['credit'] = 1
                if 'ordinal' not in item:
                    item['ordinal'] = 1

                if 'seq' in item and 'ordinal' not in item:
                    item['ordinal'] = item['seq']

                print("ITEM", item)

                credit = item.pop('credit')
                ordinal = item.pop('ordinal')

                item = cls.inst(**item)

                if node_name == 'credited_artists':
                    obj.credited_artists.connect(item, {'credit': credit, 'ordinal': ordinal})
                if node_name == 'credited_writers':
                    obj.credited_writers.connect(item, {'credit': credit, 'ordinal': ordinal})
                if node_name == 'credited_producers':
                    obj.credited_producers.connect(item, {'credit': credit, 'ordinal': ordinal})
                if node_name == 'publishers':
                    obj.publishers.connect(item, {'credit': credit, 'ordinal': ordinal})
                if node_name == 'labels':
                    obj.labels.connect(item, {'credit': credit, 'ordinal': ordinal})

        search_str = obj.title + ' ' + artists
        genius_resp = Genius.search(search_str)
        print('\n\nSearching for:', search_str)

        if genius_resp['meta']['status'] != 200:
            raise ValueError('Probably exceeded Genius limits or invalid search')

        genius_resp = genius_resp['response']['hits']
        for hit in genius_resp[:1]:
            hit = hit['result']
            song_data = Genius.get_song(hit['id'])['response']['song']
            print("song data", song_data)
            if 'spotify' in [a['provider'] for a in song_data['media']]:
                print('Spotify exists!')
                for i, a in enumerate(song_data['media']):
                    print(a)
                    if a['provider'] == 'spotify':
                        print('Spotify Exists -', song_data['full_title'])
                        spotify_data = Spotify.get_track(song_data['media'][i]['native_uri'])
                        print(spotify_data)
                        break
        return obj