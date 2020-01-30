import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import os

class Billboard:
    @staticmethod
    def get_top100(date:datetime, replace:bool=False, save_csv:bool=True) -> pd.DataFrame:
        '''
        Gets the Billboard top 100 for the given week

        :param replace: whether or not to replace the data if the date directory already exists
        :return: the dataframe of the top 100 for that week
        '''

        def to_drop(main_df: pd.DataFrame, col: str) -> pd.DataFrame:
            '''
            Built this originally so the embedded JSON within the dataframe could be its own dataframe.
            Don't really see a need for that rn since we'd join it anyway

            :param main_df: dataframe to edit
            :param col: column to delete
            :return: original dataframe
            '''

            df = pd.DataFrame(main_df[col])
            main_df = main_df.drop(columns=[col])
            df.to_csv(os.path.join('output', week, f'{col}.csv'))
            return main_df

        lead = lambda x: str(x).zfill(2)
        week = f'{date.year}-{lead(date.month)}-{lead(date.day)}'
        link = f'https://www.billboard.com/charts/hot-100/{week}'
        print(link)
        resp = requests.get(link)
        print(week, resp)
        soup = bs(resp.text).find('div', {'id': 'charts'})

        # For some reason all this fuckin data is in the attribute of an HTML tag lmao
        main_df = pd.DataFrame(json.loads(soup['data-charts']))

        if save_csv:
            if week in os.listdir('output/billboard'):
                if replace:
                    os.system(f'rm -rf output/billboard/{week}')
            else:
                os.system(f'mkdir output/billboard/{week}')

            main_df.to_csv(os.path.join('output', 'billboard', week, 'main.csv'))

        return main_df