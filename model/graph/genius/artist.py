from datetime import datetime

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty

class Artist(StructuredNode):
    '''
    Represents artist data from Genius.com
    '''
    spotify = RelationshipFrom('model.graph.spotify.artist.Artist', 'ON GENIUS AS')

    genius_id = IntegerProperty(unique_index=True)

    alternate_names = ArrayProperty()
    api_path = StringProperty(unique_index=True)
    description = StringProperty()
    facebook_name = StringProperty()
    followers_count = IntegerProperty()
    header_image_url = StringProperty()
    image_url = StringProperty()
    instagram_name = StringProperty()
    is_meme_verified = BooleanProperty()
    is_verified = BooleanProperty()
    name = StringProperty()
    translation_artist = BooleanProperty()
    twitter_name = StringProperty()
    url = StringProperty(unique_index=True)
    iq = IntegerProperty()
    user = JSONProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e

        del kwargs['current_user_metadata']
        kwargs['genius_id'] = kwargs.pop('id')
        kwargs['description'] = kwargs['description']['plain']
        kwargs.pop('current_user_metadata')

        # TODO: clean this shit

        raise NotImplementedError('Not fully implemented yet')