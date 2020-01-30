# you can ignore all this for now

# from datetime import datetime, timedelta
# from scraper.billboard import Billboard
# import json
#
# from scraper.genius import Genius
# GENIUS_API = json.loads(open('input/genius_config.json', 'r').read())
#
# # Latest available Billboard data for template constructor
# today = datetime(2018, 12, 22)
#
# for i in range(104):
#     # They have rate limits so I'm prob gonna try implementing a sleep so it's not triggered
#     try:
#         # Fetch Billboard data, test constructor, and store it in the output by week
#         Billboard(today)
#     except TypeError:
#         open('output/wrong_logs.txt', 'a').write(f'{today}\n')
#     today = today - timedelta(days=7)