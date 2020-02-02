from datetime import datetime

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, JSONProperty, \
    ArrayProperty, RelationshipFrom, DateProperty

class Annotation(StructuredNode):
    '''
    Represents annotation data from Genius.com
    '''

    # TODO: Make objects for these properties
    authors = ArrayProperty()
    verified_by = JSONProperty()
    referent = JSONProperty()

    genius_id = IntegerProperty(unique_index=True)

    api_path = StringProperty()
    body = StringProperty()
    comment_count = IntegerProperty()
    community = BooleanProperty()
    custom_preview = StringProperty()
    has_voters = BooleanProperty()
    pinned = BooleanProperty()
    share_url = StringProperty(unique_index=True)
    source = StringProperty()
    state = StringProperty()
    url = StringProperty()
    verified = BooleanProperty()
    votes_total = IntegerProperty()
    cosigned_by = ArrayProperty()
    rejection_comment = StringProperty()

    @classmethod
    def inst(cls, **kwargs):
        e = exists(cls, kwargs.get('id'))
        if e:
            return e

        del kwargs['current_user_metadata']
        kwargs['genius_id'] = kwargs.pop('id')
        kwargs['body'] = kwargs['body']['plain']
        kwargs.pop('current_user_metadata')

        # TODO: clean this shit

        raise NotImplementedError('Not fully implemented yet')