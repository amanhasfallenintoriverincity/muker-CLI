"""Spotify API service for fetching track metadata."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from muker.models.track import Track
from muker.core.database import DatabaseManager


class SpotifyService:
    """Service for interacting with Spotify Web API."""

    def __init__(self):
        """Initialize Spotify service."""
        self.sp: Optional[spotipy.Spotify] = None
        self.lyrics_api_url: Optional[str] = None
        self._load_env_file()
        self._initialize_client()
        self._initialize_lyrics_api()
        self.db = DatabaseManager()

    def _load_env_file(self):
        """Load environment variables from .env file."""
        try:
            from dotenv import load_dotenv

            # Look for .env file in project root
            env_path = Path(__file__).parent.parent.parent / '.env'

            if env_path.exists():
                load_dotenv(env_path)
                print(f"[INFO] Loaded environment variables from {env_path}")
            else:
                print("[INFO] No .env file found, using system environment variables")

        except ImportError:
            print("[INFO] python-dotenv not installed, using system environment variables only")

    def _initialize_client(self):
        """Initialize Spotify client with credentials."""
        try:
            # Get credentials from environment variables (loaded from .env or system)
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

            if not client_id or not client_secret:
                print("[INFO] Spotify credentials not found. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.")
                return

            # Use Client Credentials Flow (no user login required)
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )

            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            print("[INFO] Spotify API client initialized successfully")

        except Exception as e:
            print(f"[WARNING] Failed to initialize Spotify client: {e}")
            self.sp = None

    def _initialize_lyrics_api(self):
        """Initialize Spotify Lyrics API URL from environment."""
        self.lyrics_api_url = os.getenv('SPOTIFY_LYRICS_API_URL')
        if self.lyrics_api_url:
            print(f"[INFO] Spotify Lyrics API configured: {self.lyrics_api_url}")
        else:
            print("[INFO] Spotify Lyrics API URL not configured. Set SPOTIFY_LYRICS_API_URL to enable lyrics.")

    def is_available(self) -> bool:
        """Check if Spotify API is available.

        Returns:
            True if API client is initialized
        """
        return self.sp is not None

    def search_track(self, artist: str, title: str, album: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search for a track on Spotify.

        Args:
            artist: Artist name
            title: Track title
            album: Album name (optional)

        Returns:
            Track data dict if found, None otherwise
        """
        if not self.is_available():
            return None

        try:
            # Build search query
            query_parts = []
            if artist and artist != "Unknown Artist":
                query_parts.append(f"artist:{artist}")
            if title:
                query_parts.append(f"track:{title}")
            if album and album != "Unknown Album":
                query_parts.append(f"album:{album}")

            query = " ".join(query_parts)

            if not query:
                return None

            # Search on Spotify
            results = self.sp.search(q=query, type='track', limit=1)

            if results and results['tracks']['items']:
                return results['tracks']['items'][0]

            return None

        except Exception as e:
            print(f"[ERROR] Spotify search failed: {e}")
            return None

    def enrich_track(self, track: Track) -> Track:
        """Enrich track metadata with Spotify data.

        Args:
            track: Track to enrich

        Returns:
            Track with enriched metadata
        """
        if not self.is_available():
            return track

        # Search for track on Spotify
        spotify_track = self.search_track(track.artist, track.title, track.album)

        if not spotify_track:
            return track

        # Extract enriched metadata
        try:
            # Store Spotify track ID for lyrics fetching
            if spotify_track.get('id'):
                track.spotify_track_id = spotify_track['id']

            # Artists
            if spotify_track.get('artists'):
                artists = [artist['name'] for artist in spotify_track['artists']]
                track.artist = ", ".join(artists)

            # Album
            if spotify_track.get('album'):
                album = spotify_track['album']
                track.album = album.get('name', track.album)

                # Album release date
                if album.get('release_date'):
                    release_date = album['release_date']
                    if len(release_date) >= 4:
                        try:
                            track.year = int(release_date[:4])
                        except ValueError:
                            pass

            # Track number
            if spotify_track.get('track_number'):
                track.track_number = spotify_track['track_number']

            # Duration (in milliseconds from Spotify)
            if spotify_track.get('duration_ms'):
                track.duration = spotify_track['duration_ms'] / 1000.0

            # Explicit flag (could be stored as genre or separate field)
            if spotify_track.get('explicit'):
                if not track.genre:
                    track.genre = "Explicit"
                elif "Explicit" not in track.genre:
                    track.genre += ", Explicit"

            # Popularity (could be stored in a new field, but we'll skip for now)

            print(f"[INFO] Enriched track from Spotify: {track.artist} - {track.title}")

        except Exception as e:
            print(f"[ERROR] Failed to extract Spotify metadata: {e}")

        return track

    def get_track_audio_features(self, spotify_id: str) -> Optional[Dict[str, Any]]:
        """Get audio features for a track.

        Args:
            spotify_id: Spotify track ID

        Returns:
            Audio features dict if found
        """
        if not self.is_available():
            return None

        try:
            return self.sp.audio_features([spotify_id])[0]
        except Exception as e:
            print(f"[ERROR] Failed to get audio features: {e}")
            return None

    def get_album_art_url(self, artist: str, title: str) -> Optional[str]:
        """Get album art URL for a track.

        Args:
            artist: Artist name
            title: Track title

        Returns:
            Album art URL if found
        """
        if not self.is_available():
            return None

        spotify_track = self.search_track(artist, title)

        if not spotify_track:
            return None

        try:
            album = spotify_track.get('album', {})
            images = album.get('images', [])

            if images:
                # Return the largest image (first in the list)
                return images[0]['url']

        except Exception as e:
            print(f"[ERROR] Failed to get album art: {e}")

        return None

    def get_lyrics(self, track_id: str, format: str = "lrc") -> Optional[Dict[str, Any]]:
        """Fetch lyrics from Spotify Lyrics API.

        Args:
            track_id: Spotify track ID
            format: Lyrics format ('lrc' or 'id3')

        Returns:
            Lyrics data dict if found, None otherwise
        """
        # 1. Check Cache
        cached_lyrics = self.db.get_spotify_lyrics(track_id)
        if cached_lyrics:
            print(f"[INFO] Loaded lyrics for track {track_id} from cache")
            return cached_lyrics

        if not self.lyrics_api_url:
            return None

        try:
            import requests

            # Build API request URL
            url = f"{self.lyrics_api_url}?trackid={track_id}&format={format}"

            # Make request to lyrics API
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            lyrics_data = response.json()
            print(f"[DEBUG-LYRICS-API] Raw response: {lyrics_data}")

            # Check if lyrics were found
            if lyrics_data.get('error'):
                print(f"[WARNING] Lyrics API error: {lyrics_data.get('message', 'Unknown error')}")
                return None

            print(f"[INFO] Fetched lyrics for track {track_id} (format: {format})")
            
            # 2. Save to Cache
            self.db.save_spotify_lyrics(track_id, lyrics_data)
            
            return lyrics_data

        except ImportError:
            print("[ERROR] requests library not installed. Install with: pip install requests")
            return None
        except requests.exceptions.Timeout:
            print("[ERROR] Lyrics API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch lyrics: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error fetching lyrics: {e}")
            return None

    def enrich_track_with_lyrics(self, track: Track, format: str = "lrc") -> Track:
        """Enrich track with lyrics data.

        Args:
            track: Track to enrich with lyrics
            format: Lyrics format ('lrc' or 'id3')

        Returns:
            Track with lyrics data
        """
        if not track.spotify_track_id:
            return track

        lyrics_data = self.get_lyrics(track.spotify_track_id, format)
        if lyrics_data:
            track.lyrics = lyrics_data

        return track
