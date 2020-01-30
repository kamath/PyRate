def main():
    import os
    from tqdm import tqdm
    import pandas as pd
    import json
    from ast import literal_eval

    # Assumes all billboard data is in the output/ subdirectory
    billboard_dir = os.path.join('output', 'billboard')
    weeks = os.listdir(billboard_dir)

    # Do it in chronological order
    weeks.sort()
    to_concat = []

    print('Fetching all billboard data')
    for week in tqdm(weeks):
        new = pd.read_csv(os.path.join(billboard_dir, week, 'main.csv'))
        new['week'] = [week for _ in new.iterrows()]
        to_concat.append(new)

    print('Concatenating dataframes...')
    df = pd.concat(to_concat)
    # df.to_csv('output/bigass_billboard.csv')

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')].reset_index()

    final_dict = {}
    changing = {'awards', 'rank', 'week'}
    df_dict = df.drop_duplicates(subset='title_id', keep="last").set_index('title_id').to_dict('index')

    # How many unique songs are on here?
    unique_titles = df['title_id'].unique()

    print('Converting dataframe to JSON')
    for title in tqdm(unique_titles):
        final_dict[title] = {}
        for col in df.columns:
            if col not in changing and col != 'title_id':
                final_dict[title][col] = df_dict[title][col]
            else:
                final_dict[title][col] = list(df.loc[df['title_id'] == title][col])

    print('Converting strings to Python objects')
    for i in tqdm(final_dict.keys()):
        for key, val in final_dict[i].items():
            # Convert dicts and lists represented as strings into their respective objects
            if isinstance(val, str) and len(val) >= 2 and val[0] in ('[', '{') and val[-1] in {']', '}'}:
                val = literal_eval(val)
                final_dict[i][key] = val

            # What if we have a list of dicts? eval() converts this into a list of strings, so we need to make these dicts
            if isinstance(val, list) and len(list(filter(lambda x: isinstance(x, str), val))) > 0:
                try:
                    val = list(map(literal_eval, val))
                    final_dict[i][key] = val
                except KeyError:
                    pass

    print('Grouping duplicated fields')
    # Group changing data by week
    for key, val in tqdm(final_dict.items()):
        for k, v in val['history'].items():
            final_dict[key][k] = v

        final_dict[key]['charts'] = {}
        for week, awards, ranks in zip(val['week'], val['awards'], val['rank']):
            final_dict[key]['charts'][week] = {}
            final_dict[key]['charts'][week]['awards'] = awards
            final_dict[key]['charts'][week]['rank'] = ranks

        del final_dict[key]['awards']
        del final_dict[key]['rank']
        del final_dict[key]['history']
        del final_dict[key]['week']

    print('Saving final JSON file')
    # NumPy int64 isn't valid, so you have to convert to regular Python ints
    final_dict = {int(key): val for key, val in final_dict.items()}
    open(os.path.join('output', 'billboard.json'), 'w').write(json.dumps(final_dict))