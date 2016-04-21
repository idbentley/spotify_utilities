import argparse
from datetime import datetime 
import spotipy
import spotipy.util
import spotipy.client
from private_conf import conf

client_id=conf["spotify_client_id"]
client_secret=conf["spotify_client_secret"]

def get_follow_client():
    token = spotipy.util.prompt_for_user_token(args.username, scope="user-follow-read", client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:8888/callback")
    return spotipy.Spotify(auth=token)

def get_write_playlist_client():
    token = spotipy.util.prompt_for_user_token(args.username, scope="playlist-modify-public", client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:8888/callback")
    return spotipy.Spotify(auth=token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that attempts to donwload all songs on a spotify playlist")
    parser.add_argument(dest='since_date', type=str, help="YYYY-MM-DD date.")
    parser.add_argument(dest='username', type=str, help='The owning users id.')
    parser.add_argument(dest='playlist_id', type=str, help='The playlist to put new releases into.')
    args = parser.parse_args()

    playlist_id = args.playlist_id
    since = datetime.strptime(args.since_date, "%Y-%m-%d")

    sp = get_follow_client()

    artists = []
    last_artist = None
    # artist_batch = sp.current_user_followed_artists(after=last_artist)
    # artists = artists + artist_batch["artists"]["items"]
    while True:
        artist_batch = sp.current_user_followed_artists(after=last_artist)
        if len(artist_batch["artists"]["items"]) == 0:
            print(artist_batch)
            break
        artists = artists + artist_batch["artists"]["items"]
        last_artist = artists[-1]["id"]
        print("total artists so far: {}.  Last artist: {}".format(len(artists), last_artist))
    print("total artists: {}".format(len(artists)))
    for artist in artists:
        try:
            album_results = sp.artist_albums(artist["uri"], "album,single")
        except spotipy.client.SpotifyException:
            sp = get_follow_client()
            album_results = sp.artist_albums(artist["uri"], "album,single")
        for album in album_results["items"]:
            try:
                album_details = sp.album(album["id"])
            except spotipy.client.SpotifyException:
                sp = get_follow_client()
                album_details = sp.album(album["id"])
            release_date = album_details["release_date"]
            release_date_obj = None
            try:
                release_date_obj = datetime.strptime(release_date, "%Y-%m-%d")
            except ValueError:
                try:
                    release_date_obj = datetime.strptime(release_date, "%Y-%m")
                except ValueError:
                    try:
                        release_date_obj = datetime.strptime(release_date, "%Y")
                    except ValueError:
                        continue
            if release_date_obj > since:
                artist_names = ""
                for artist in album_details["artists"]:
                    if artist_names != "":
                        artist_names += ", "
                    artist_names += artist["name"] + "/" + artist["id"] 
                print("{}[{}] by {} on {} ({})".format(album_details["name"], album_details["type"], artist_names, release_date_obj, album_details["id"]))
                tracks = []
                for track in album_details["tracks"]["items"]:
                    tracks.append(track["id"])
                get_write_playlist_client().user_playlist_add_tracks(sp.current_user()["id"], playlist_id, tracks)