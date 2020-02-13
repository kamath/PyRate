from typing import *

def main():
    from neomodel import config, db

    from model.graph import connection_url
    from model.graph.spotify.track import Track
    from model.graph.spotify.playlist import Playlist

    from sklearn.neural_network import MLPClassifier
    from sklearn.linear_model import Perceptron, SGDClassifier
    from sklearn.multioutput import MultiOutputClassifier
    from sklearn.preprocessing import MultiLabelBinarizer
    from sklearn.preprocessing import normalize
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.datasets import make_multilabel_classification

    from joblib import dump, load
    from tqdm import tqdm
    import numpy as np
    from math import log10
    import os

    config.DATABASE_URL = connection_url()

    db.set_connection(connection_url())

    stopval = len(Track.nodes)
    print(stopval)

    print('Playlists', len(Playlist.nodes))
    playlists = Playlist.get_all()
    num_playlists = len(playlists)
    playlists = {node.uri: ind for ind, node in enumerate(playlists)}

    def get_minibatches(stopval, count=0, interval=20):
        while count < stopval:
            to_analyze: List[Track] = Track.get_songs_in_playlists(interval, count)

            X = [a.get_song_features(as_list=True) for a in to_analyze]
            y = [[playlists[x.uri] for x in Track.get_playlists(a.spotify_id)] for a in to_analyze]
            print(count, interval)
            yield np.array(list(map(lambda x: list(map(abs, x)), X))), MultiLabelBinarizer().fit_transform(y)
            count += len(to_analyze)

    lda = LatentDirichletAllocation(n_components=num_playlists)
    startval = 0
    if len(os.listdir('trained_models')) > 0:
        startval = max(os.listdir('trained_models'))
        lda = load(os.path.join('trained_models',
                startval))

    startval = int(startval.split('.')[0])
    interval = 20
    # get_minibatches(stopval, count=startval * interval)
    for i, val in enumerate(tqdm(get_minibatches(stopval, count=startval * interval))):
        i += startval + 1
        X, y = val
        lda.partial_fit(X)
        dump(lda, os.path.join('trained_models',
            f'{str(i).zfill(int(log10(stopval) + 1))}.joblib'))
        os.remove(os.path.join('trained_models',
            f'{str(i - 1).zfill(int(log10(stopval) + 1))}.joblib'))