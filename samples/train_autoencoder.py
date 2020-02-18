def main():
    from model.conv_autoencoder import Autoencoder
    import pandas as pd
    import os

    df = pd.read_json(os.path.join('input', 'sample_analysis.json'))

    # Segment analysis
    def segment_to_vector(segment):
        return list(map(abs, [segment['duration'], segment['loudness_start'], segment['loudness_max_time'],
                              segment['loudness_max']] \
                        + segment['pitches'] + segment['timbre']))

    arrs = [list(map(segment_to_vector, sample['segments'])) for sample in df['analysis']]

    auto = Autoencoder(model_name='segment_analysis', arrs=arrs, to_pad=800) # Trains model

    # Pre-trained model
    # arrs = Autoencoder.pad_and_normalize(arrs, to_pad=800)
    # auto = Autoencoder(model_name='segment_analysis', input_shape = arrs.shape[1:], train=False)

    df = auto.store_zVectors(arrs, df)
    print('Stored df', df)
    ind = 0
    similar = auto.get_similar(df, ind=ind)
    names = []
    artists = []
    for i, row in similar.iterrows():
        names.append(row['track']['name'])
        artists.append('; '.join([a['name'] for a in row['track']['artists']]))
    similar['name'] = names
    similar['artists'] = artists
    print('Target:', similar['name'][ind], 'by', similar['artists'][ind])
    print('Similar', similar[['name', 'artists', 'similarity']])
