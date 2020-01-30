from scraper.billboard import Billboard
import json

'''
Collates Billboard, Spotify, and Genius data into one song object
'''
class Song:
    @staticmethod
    def only_one_arg(*args) -> bool:
        '''
        Only allow one argument to not be None.

        :param args: the list of args
        :return: True if only one argument is not None
        '''
        args = list(filter(lambda x: x is not None, args))
        return len(args) == 1

    def from_billboard(self, data:json):
        raise NotImplementedError

    def from_spotify(self, data:json):
        raise NotImplementedError

    def from_genius(self, data:json):
        raise NotImplementedError

    def __init__(self, genius_data:json=None, billboard_data:json=None, spotify_data:json=None):
        '''
        Creates a song from one source of data. Only allows one argument though, not multiple.

        :param genius_data:
        :param billboard_data:
        :param spotify_data:
        '''
        if not Song.only_one_arg(genius_data, billboard_data, spotify_data):
            raise ValueError('Only pass in one argument!')

