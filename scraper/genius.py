import requests
import json
import os

class Genius:
    BASE_URL = 'https://api.genius.com'

    def __init__(self):
        self.API_TOKEN = json.load(open(os.path.join('config', 'genius_config.json'), 'r'))

    def get(self, endpoint: str) -> json:
        '''
        Gets the JSON value when pinging the Genius API
        :param endpoint: the API endpoint to get data from
        :return: the JSON value returned from the API call
        '''
        return requests.get(f'{self.BASE_URL}/{endpoint}', headers=self.API_TOKEN).json()

    @classmethod
    def search(cls, search_str: str) -> json:
        '''
        Searches for a song on Genius and fetches the results
        :param search_str: the string to search for
        :return: the json value containing the search results
        '''
        return cls().get(f'search?q={search_str}')