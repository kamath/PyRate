from datetime import datetime

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty

class Track(StructuredNode):
    '''
    Represents track data from Genius.com
    '''
    spotify = RelationshipFrom('model.graph.spotify.track.Track', 'ON GENIUS AS')

    primary_artist = JSONProperty()
    featured_artists = ArrayProperty()
    album = JSONProperty()
    producer_artists = ArrayProperty()
    song_relationships = ArrayProperty()
    verified_annotations_by = ArrayProperty()
    verified_contributors = ArrayProperty()
    verified_lyrics_by = ArrayProperty()
    writer_artists = ArrayProperty()

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
    custom_performances = ArrayProperty()
    description_annotation = JSONProperty()
    lyrics_marked_complete_by = StringProperty()
    media = JSONProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e

        kwargs['genius_id'] = kwargs.pop('id')
        kwargs['release_date'] = datetime(*map(int, kwargs['release_date'].split('-')))
        kwargs.pop('current_user_metadata')

        # TODO: clean this shit

        raise NotImplementedError('Not fully implemented yet')