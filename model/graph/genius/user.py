from datetime import datetime

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty

class User(StructuredNode):
    '''
    Represents user data from Genius.com
    '''

    genius_id = IntegerProperty()

    # TODO: Build connections with annotations
    api_path = StringProperty(unique_index=True)
    avatar = JSONProperty()
    header_image_url = StringProperty()
    human_readable_role_for_display = StringProperty()
    iq = IntegerProperty()
    login = StringProperty(unique_index=True)
    name = StringProperty()
    role_for_display = StringProperty()
    url = StringProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e

        kwargs['genius_id'] = kwargs.pop('id')
        kwargs.pop('current_user_metadata')

        # TODO: clean this shit

        raise NotImplementedError('Not fully implemented yet')