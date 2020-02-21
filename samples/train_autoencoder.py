from typing import *

def main():
    from model.conv_autoencoder import Autoencoder

    from neomodel import config, db
    import pandas as pd
    import os
    import numpy as np
    from ast import literal_eval as eval
    from tqdm import tqdm

    from model.graph import connection_url
    from model.graph.spotify.track import Track
    from model.graph.spotify.playlist import Playlist

    config.DATABASE_URL = connection_url()
    db.set_connection(connection_url())

    # Segment analysis
    def segment_to_vector(segment):
        return list(map(abs, [segment['duration'], segment['loudness_start'], segment['loudness_max_time'],
                              segment['loudness_max']] \
                        + segment['pitches'] + segment['timbre']))

    stopval = len(Track.nodes)
    print('Number of tracks:', stopval)
    print('Number of playlists:', len(Playlist.nodes))

    def get_minibatches(stopval, offset=0, interval=500):
        while offset < stopval:
            to_analyze: List[Track] = Track.get_songs_not_in_playlists(interval, offset=offset)
            yield to_analyze

            offset += len(to_analyze)
            print(f'{offset}/{stopval}')

    for i, x in enumerate(get_minibatches(stopval)):
        tracks = x
        X = [a.analysis['segments'] for a in x if a.analysis]
        arrs = [list(map(segment_to_vector, sample)) for sample in X]
        print(tracks)
        latest = list(filter(lambda x: 'segment_analysis' in x, os.listdir('models')))
        if latest:
            latest = os.path.join('models', max(latest))
        else:
            latest = None

        to_pad = 800
        arrs = Autoencoder.pad_and_normalize(arrs, to_pad=to_pad)
        auto = Autoencoder.train('segment_analysis', arrs,
                                 weights_path=latest, epochs=10)
        df = pd.DataFrame({'uri': [a.uri for a in tracks]})
        df = Autoencoder.store_zVectors(auto, arrs, df)
        for i, row in tqdm(df.iterrows()):
            track = Track.add_zVector(row['uri'], row['zVector'].tolist())
            # print('new zVector for', track.name, '-', track.zVector)
        # print('DataFrame', df)