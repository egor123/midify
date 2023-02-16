import os
import spotipy
import difflib
from dotenv import load_dotenv


class Core:
    def __init__(self, timeout, retries) -> None:
        load_dotenv()
        self.scopes = ["playlist-read-private", "playlist-read-collaborative",
                       "user-read-currently-playing", "user-modify-playback-state",
                       "user-read-playback-state"]
        self.path = os.path.realpath(os.path.dirname(__file__))
        self.cache_path = os.path.join(self.path, ".cache")
        self._sp = spotipy.Spotify(
            requests_timeout=timeout,
            retries=retries,
            auth_manager=spotipy.SpotifyOAuth(
                scope=self.scopes,
                client_id=os.environ["CLIENT_ID"],
                client_secret=os.environ["CLIENT_SECRET"],
                redirect_uri=os.environ["REDIRECT_URI"],
                cache_path=self.cache_path))
        self.playlists = []
        self.__fetch_playlists__()

    @property
    def sp(self):
        return self._sp

    def __fetch_playlists__(self, limit=50, offset=0):
        playlists = self.sp.current_user_playlists(limit, offset)['items']
        self.playlists += playlists
        if (len(playlists) == limit):
            self.__fetch_playlists__(limit, offset + limit)

    def set_uri(self, name: str, is_global: bool = True, type: str = "playlist"):
        print(name)
        if (not is_global):
            uri = sorted(self.playlists, key=lambda p: difflib.SequenceMatcher(
                None, p["name"], name).ratio())[-1]['uri']
            self.sp.start_playback(context_uri=uri)
        elif (type == "track"):
            uri = self.sp.search(name, 1, type=type)[
                'tracks']['items'][0]['uri']
            self.sp.start_playback(uris=[uri])
        elif (type == "album"):
            uri = self.sp.search(name, 1, type=type)[
                'albums']['items'][0]['uri']
            self.sp.start_playback(context_uri=uri)
        else:
            uri = self.sp.search(name, 1, type=type)[
                'playlists']['items'][0]['uri']
            self.sp.start_playback(context_uri=uri)
