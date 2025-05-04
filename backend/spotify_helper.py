def get_music_taste():
    return ""


def parse_songs(song_info):
    songs = [entry["song_title"] for entry in song_info]
    artists = [entry["artist"] for entry in song_info]
    explanations = [entry["explanation"] for entry in song_info]
    return songs, artists, explanations


def create_playlist(songs):
    return True
