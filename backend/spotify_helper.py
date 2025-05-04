import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPES = "user-top-read playlist-modify-public"


def get_spotify_client(access_token):
    return spotipy.Spotify(auth=access_token)


def get_music_taste(access_token):
    sp = get_spotify_client(access_token)

    top_artists = sp.current_user_top_artists(limit=10, time_range='medium_term')
    artist_names = [artist['name'] for artist in top_artists['items']]
    genres = [genre for artist in top_artists['items'] for genre in artist['genres']]

    top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
    track_names = [track['name'] for track in top_tracks['items']]
    artist_names += [track['artists'][0]['name'] for track in top_tracks['items']]

    from collections import Counter
    genre_counts = Counter(genres)
    top_genres = [genre for genre, count in genre_counts.most_common(5)]

    summary = (
        f"Top genres: {', '.join(top_genres)}. "
        f"Favorite artists include: {', '.join(set(artist_names[:5]))}. "
        f"Frequently played tracks: {', '.join(track_names[:5])}."
    )

    return summary


def parse_songs(song_info):
    songs = [entry["song_title"] for entry in song_info]
    artists = [entry["artist"] for entry in song_info]
    explanations = [entry["explanation"] for entry in song_info]
    return songs, artists, explanations


def create_playlist(songs, artists, title, access_token):
    print(f"create_playlist: {access_token}")
    sp = get_spotify_client(access_token)
    track_uris = []

    for song, artist in zip(songs, artists):
        query = f"track:{song} artist:{artist}"
        result = sp.search(q=query, type='track', limit=1)
        tracks = result['tracks']['items']
        if tracks:
            uri = tracks[0]['uri']
            track_uris.append(uri)
        else:
            print(f"Not found: {song} by {artist}")

    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user=user_id, name=title, public=True)
    sp.playlist_add_items(playlist['id'], track_uris)
    return playlist['external_urls']['spotify']
