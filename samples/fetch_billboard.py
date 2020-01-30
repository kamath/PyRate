'''
Fetches Billboard data up to a given date
'''

def main():
    from datetime import datetime, timedelta
    from scraper.billboard import Billboard
    import os
    from time import sleep

    if not os.path.exists(os.path.join('output')):
        os.mkdir('output')

    if not os.path.exists(os.path.join('output', 'billboard')):
        os.mkdir(os.path.join('output', 'billboard'))

    # Latest available Billboard data for template constructor
    today = datetime(2018, 12, 22)
    if len(os.listdir(os.path.join('output', 'billboard'))) > 0:
        last = min(os.listdir(os.path.join('output', 'billboard')))
        today = datetime(*map(int, last.split('-')))

    while today > datetime(1958, 8, 4):
        # Basically quit if there's rate limits - I think they have a program to detect if it's repeated calls
        try:
            # Fetch Billboard data and store it in the output by week
            Billboard.get_top100(today, replace=False)
        except TypeError:
            counter = 1
            while True:
                try:
                    Billboard.get_top100(today, replace=False)
                    break
                except TypeError:
                    # Sleep until it fuckin works
                    print(2**counter)
                    sleep(2**counter)
                    counter += 1
        today = today - timedelta(days=7)
