from datetime import date

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty
from model.graph.genius import GeniusNode
from model.graph.spotify.track import Track as SpotifyTrack
from scraper.spotify import Spotify
from typing import *

class Track(GeniusNode):
    '''
    Represents track data from Genius.com
    '''
    spotify = RelationshipFrom('model.graph.spotify.track.Track', 'ON GENIUS AS')

    primary_artist = JSONProperty()
    featured_artists = JSONProperty()
    album = JSONProperty()
    producer_artists = JSONProperty()
    song_relationships = JSONProperty()
    verified_annotations_by = JSONProperty()
    verified_contributors = JSONProperty()
    verified_lyrics_by = JSONProperty()
    writer_artists = JSONProperty()

    genius_id = IntegerProperty(unique_index=True)

    annotation_count = IntegerProperty()
    api_path = StringProperty(unique_index=True)
    apple_music_id = StringProperty(unique_index=True)
    apple_music_player_url = StringProperty(unique_index=True)
    description = StringProperty()
    embed_content = StringProperty()
    featured_video = BooleanProperty()
    full_title = StringProperty()
    header_image_thumbnail_url = StringProperty()
    header_image_url = StringProperty()
    lyrics_owner_id = IntegerProperty()
    lyrics_state = StringProperty()
    path = StringProperty(unique_index=True)
    pyongs_count = IntegerProperty()
    recording_location = StringProperty()
    release_date = DateProperty()
    release_date_for_display = StringProperty()
    song_art_image_thumbnail_url = StringProperty()
    song_art_image_url = StringProperty()
    stats = JSONProperty()
    title = StringProperty()
    title_with_featured = StringProperty()
    url = StringProperty(unique_index=True)
    custom_performances = JSONProperty()
    description_annotation = JSONProperty()
    lyrics_marked_complete_by = StringProperty()
    media = JSONProperty()

    @classmethod
    def clean(cls, **kwargs) -> Tuple[StructuredNode, Dict[str, dict]]:
        kwargs['genius_id'] = kwargs.pop('id')
        kwargs['release_date'] = date(*map(int, kwargs['release_date'].split(':')[0].split('-')))
        kwargs.pop('current_user_metadata')

        to_connect = {}
        if 'spotify' in [a['provider'] for a in kwargs['media']]:
            for i, a in enumerate(kwargs['media']):
                if a['provider'] == 'spotify':
                    to_connect['spotify_data'] = Spotify.get_track(kwargs['media'][i]['native_uri'])
                    break
        return cls(**kwargs), to_connect

    @staticmethod
    def post_clean(obj, to_connect: dict) -> StructuredNode:
        # Associate Spotify
        if 'spotify_data' in to_connect:
            spotify: SpotifyTrack = SpotifyTrack.inst(**to_connect['spotify_data'])
            spotify.genius_data.connect(obj)
        return obj

