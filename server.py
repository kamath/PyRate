from scraper.spotify import Spotify
from model.graph.spotify.track import Track
from model.graph.spotify.artist import Artist
from model.graph.spotify.playlist import Playlist
from random import randint
from scipy import spatial
from ast import literal_eval as eval
import numpy as np
from time import time
import json

from flask import Flask, render_template, request, redirect
app = Flask(__name__)

def create_cosine_similarity(shoe1, shoe2):
    result = 1 - spatial.distance.cosine(shoe1, shoe2)
    return result

@app.route('/')
def hello_world():
    start = time()
    spotify_data = Spotify.get_currently_playing()
    playlists = Track.get_playlists(spotify_data['item']['id'])

    print('Currently analyzing:', spotify_data['item']['name'])
    playlist_id = spotify_data['context']['uri'].split(':')[-1]
    playlist_tracks = Playlist.get_tracks(playlist_id)
    print('Fetched tracks in playlist')
    print('Time taken:', time() - start)
    arrs = [json.loads(a.zVector)['zVector'] for a in playlist_tracks]
    arrs = np.array(arrs)
    print('Arrs shape:', arrs.shape)

    track = Track.find(uri=spotify_data['item']['uri'])[0]
    ll = []
    for i in arrs:
        ll.append(create_cosine_similarity(track.zVector['zVector'], i))
    tracks = list(sorted(zip(playlist_tracks, ll), key=lambda x: x[1]))
    tracks = tracks[:5] + tracks[-6:-1]
    track_images = Spotify.get_images(*[a[0].uri for a in tracks])
    print('Most similar')
    for a in tracks[:5]:
        print(a[0].name)
    print('Time taken to get similar:', time() - start)

    similar_playlists = Track.get_similar_playlists(spotify_data['item']['id'],
                                            spotify_data['context']['uri'].split(':')[-1])

    similar_playlists = set(similar_playlists)

    associated_artists = Artist.get_associated_artists(spotify_data['item']['artists'][0]['id'])

    if len(associated_artists):
        artist_data = Spotify.get_artists([artist.uri for artist in associated_artists])

        for i in range(len(artist_data)):
            if len(artist_data[i]['images']) == 0:
                artist_data[i]['images'] = [{'url': '/static/stock_anon.png'}]

    else:
        artist_data = []

    print('Total time', time()-start)
    return render_template('home.html', similar_tracks=list(zip(tracks, track_images)), spotify_data=spotify_data, playlists=playlists,
                           similar_playlists=similar_playlists, artist_data=artist_data)

@app.route('/artists')
def combine_artists():
    artists = request.args.get('artists').split(',')
    context = request.args.get('context_uri')
    tracks = Artist.get_tracks_with_multiple_artists(context, *artists)
    print('Common tracks', tracks)
    if len(tracks):
        to_play = randint(0, len(tracks) - 1)
        album = Track.get_album(tracks[to_play].spotify_id)[0]
        print(album.name, tracks[to_play].track_number)
        tor = Spotify.play(context_uri=album.uri, offset={'position':  tracks[to_play].track_number - 1})
    return redirect('/')

@app.route('/play/<context>/<track>')
def play_context(context, track):
    Spotify.play(context_uri=context, offset={"uri": track})
    return redirect('/')

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')