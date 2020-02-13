from scraper.spotify import Spotify
from model.graph.spotify.track import Track
from model.graph.spotify.artist import Artist
from random import randint

from flask import Flask, render_template, request, redirect
app = Flask(__name__)

@app.route('/')
def hello_world():
    spotify_data = Spotify.get_currently_playing()

    playlists = Track.get_playlists(spotify_data['item']['id'])

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

    return render_template('home.html', spotify_data=spotify_data, playlists=playlists,
                           similar_playlists=similar_playlists, artist_data=artist_data)

@app.route('/artists')
def combine_artists():
    artists = request.args.get('artists').split(',')
    tracks = Artist.get_tracks_with_multiple_artists(*artists)
    if len(tracks):
        to_play = randint(0, len(tracks) - 1)
        album = Track.get_album(tracks[to_play].spotify_id)[0]
        print(album.name, tracks[to_play].track_number)
        tor = Spotify.play(context_uri=album.uri, offset={'position':  tracks[to_play].track_number - 1})
    return redirect('/')

@app.route('/play/<context>')
def play_context(context):
    Spotify.play(context_uri=context)
    return redirect('/')

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')