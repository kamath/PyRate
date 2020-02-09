from typing import *

def main():
    from neomodel import config, db

    from scraper.genius import Genius

    from model.graph import connection_url
    from model.graph.spotify.track import Track
    from model.graph.spotify.album import Album

    config.DATABASE_URL = connection_url()

    db.set_connection(connection_url())

    tracks: List[Track] = Track.paginate(5)
    for track in tracks:
        print(track.uri)

    # results, meta = db.cypher_query('MATCH (n: Track) RETURN n LIMIT 5')
    # people = [Track.inflate(row[0]) for row in results]
    # print(len(people))
    #
    # for t in people:
    #     print(t.name)