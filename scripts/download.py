import argparse
import spotipy
import spotipy.util 
import soundcloud
import requests

import youtube

from private_conf import conf

client_id=conf["spotify_client_id"]
client_secret=conf["spotify_client_secret"]
soundcloud_client_id=conf["soundcloud_client_id"]
soundcloud_client_secret=conf["soundcloud_client_secret"]

def youtube_search(artist, track):
    r = youtube.youtube_search(artist, track)
    # print("{} {}".format(r, dir(r)))

def soundcloud_search(artist, track, soundcloud_client):
    results = soundcloud_client.get('/tracks', q="{} {}".format(artist, track['name']))
    for t in results:
        if artist in t.title and (track['name'] in t.title or track['name'] in t.description) :
            print("Found soundcloud: {} http://soundcloud.com/{}/{}".format(t.title, t.user["permalink"], t.permalink))
            if t.downloadable:
                print("Download link: {} {}".format(t.download_url, t.download_url[26:]))
                # soundcloud_client.get(t.download_url[26:])

def attempt_tracks(results, soundcloud_client):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        artist = track['artists'][0]['name']

        print("   {} {} {}".format(i, artist, track['name']))
        soundcloud_search(artist, track, soundcloud_client)
 #       youtube_search(artist, track)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that attempts to donwload all songs on a spotify playlist")
    parser.add_argument(dest='playlist_id', type=str, help="The playlist id.")
    parser.add_argument(dest='username', type=str, help='The owning users id.')
    args = parser.parse_args()

    token = spotipy.util.prompt_for_user_token(args.username, client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:8888/callback")
    sp = spotipy.Spotify(auth=token)
    results = sp.user_playlist(args.playlist_id, args.username,
                               fields="tracks,next")
    soundcloud_client = soundcloud.Client(client_id=soundcloud_client_id)
    tracks = results['tracks']
    attempt_tracks(tracks, soundcloud_client)
    while tracks['next']:
        tracks = sp.next(tracks)
        attempt_tracks(tracks, soundcloud_client)
