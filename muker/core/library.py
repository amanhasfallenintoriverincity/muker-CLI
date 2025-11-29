"""Music library management module."""

from pathlib import Path
from typing import List, Optional
from muker.models.track import Track
from muker.utils.file_scanner import FileScanner


class MusicLibrary:
    """Manages music library and track scanning."""

    def __init__(self):
        """Initialize music library."""
        self.tracks: List[Track] = []
        self.current_directory: Optional[Path] = None

    async def scan_directory(self, directory: Path, recursive: bool = True) -> List[Track]:
        """Scan a directory for music files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of found tracks
        """
        self.current_directory = directory
        self.tracks = await FileScanner.scan_directory(directory, recursive)
        return self.tracks

    def get_tracks(self) -> List[Track]:
        """Get all tracks in the library.

        Returns:
            List of tracks
        """
        return self.tracks

    def search_tracks(self, query: str) -> List[Track]:
        """Search tracks by title, artist, or album.

        Args:
            query: Search query string

        Returns:
            List of matching tracks
        """
        query_lower = query.lower()
        results = []

        for track in self.tracks:
            if (query_lower in track.title.lower() or
                query_lower in track.artist.lower() or
                query_lower in track.album.lower()):
                results.append(track)

        return results

    def filter_by_artist(self, artist: str) -> List[Track]:
        """Filter tracks by artist name.

        Args:
            artist: Artist name

        Returns:
            List of tracks by the artist
        """
        artist_lower = artist.lower()
        return [track for track in self.tracks if artist_lower in track.artist.lower()]

    def filter_by_album(self, album: str) -> List[Track]:
        """Filter tracks by album name.

        Args:
            album: Album name

        Returns:
            List of tracks from the album
        """
        album_lower = album.lower()
        return [track for track in self.tracks if album_lower in track.album.lower()]

    def filter_by_genre(self, genre: str) -> List[Track]:
        """Filter tracks by genre.

        Args:
            genre: Genre name

        Returns:
            List of tracks in the genre
        """
        genre_lower = genre.lower()
        return [
            track for track in self.tracks
            if track.genre and genre_lower in track.genre.lower()
        ]

    def get_all_artists(self) -> List[str]:
        """Get list of all unique artists.

        Returns:
            Sorted list of artist names
        """
        artists = set(track.artist for track in self.tracks)
        return sorted(artists)

    def get_all_albums(self) -> List[str]:
        """Get list of all unique albums.

        Returns:
            Sorted list of album names
        """
        albums = set(track.album for track in self.tracks)
        return sorted(albums)

    def get_all_genres(self) -> List[str]:
        """Get list of all unique genres.

        Returns:
            Sorted list of genre names
        """
        genres = set(track.genre for track in self.tracks if track.genre)
        return sorted(genres)

    def get_track_by_path(self, file_path: str) -> Optional[Track]:
        """Get a track by its file path.

        Args:
            file_path: File path to search for

        Returns:
            Track if found, None otherwise
        """
        for track in self.tracks:
            if track.file_path == file_path:
                return track
        return None

    def clear(self):
        """Clear all tracks from the library."""
        self.tracks.clear()
        self.current_directory = None

    def get_track_count(self) -> int:
        """Get number of tracks in the library.

        Returns:
            Track count
        """
        return len(self.tracks)

    def get_total_duration(self) -> float:
        """Get total duration of all tracks in the library.

        Returns:
            Total duration in seconds
        """
        return sum(track.duration for track in self.tracks)
