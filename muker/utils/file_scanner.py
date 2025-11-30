"""File scanner utility for finding music files."""

import asyncio
from pathlib import Path
from typing import List, Set, Optional, Any
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE

from muker.models.track import Track


class FileScanner:
    """Scans directories for music files and extracts metadata."""

    # Supported audio file extensions
    SUPPORTED_EXTENSIONS: Set[str] = {'.mp3', '.wav', '.flac', '.ogg'}

    # Spotify service instance (shared across scans)
    _spotify_service: Optional[Any] = None

    @classmethod
    def set_spotify_service(cls, service):
        """Set Spotify service for metadata enrichment.

        Args:
            service: SpotifyService instance
        """
        cls._spotify_service = service

    @staticmethod
    def is_supported(file_path: Path) -> bool:
        """Check if a file is a supported audio format.

        Args:
            file_path: Path to check

        Returns:
            True if file is supported
        """
        return file_path.suffix.lower() in FileScanner.SUPPORTED_EXTENSIONS

    @classmethod
    def extract_metadata(cls, file_path: Path, enrich_with_spotify: bool = False) -> Track:
        """Extract metadata from an audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Track object with metadata
        """
        try:
            audio = MutagenFile(str(file_path), easy=True)

            if audio is None:
                # Fallback to basic track info
                return Track(
                    file_path=str(file_path),
                    title=file_path.stem
                )

            # Extract common metadata
            title = file_path.stem
            artist = "Unknown Artist"
            album = "Unknown Album"
            duration = 0.0
            track_number = None
            year = None
            genre = None
            bitrate = None
            sample_rate = None
            channels = None

            # Try to get metadata from tags
            if hasattr(audio, 'tags') and audio.tags:
                title = audio.tags.get('title', [title])[0] if 'title' in audio.tags else title
                artist = audio.tags.get('artist', [artist])[0] if 'artist' in audio.tags else artist
                album = audio.tags.get('album', [album])[0] if 'album' in audio.tags else album

                if 'tracknumber' in audio.tags:
                    try:
                        track_num_str = str(audio.tags['tracknumber'][0])
                        # Handle formats like "1/12"
                        if '/' in track_num_str:
                            track_num_str = track_num_str.split('/')[0]
                        track_number = int(track_num_str)
                    except (ValueError, IndexError):
                        pass

                if 'date' in audio.tags:
                    try:
                        year_str = str(audio.tags['date'][0])[:4]
                        year = int(year_str)
                    except (ValueError, IndexError):
                        pass

                if 'genre' in audio.tags:
                    genre = audio.tags['genre'][0]

            # Get audio info (duration, bitrate, sample rate, channels)
            if hasattr(audio, 'info'):
                info = audio.info

                # Duration
                if hasattr(info, 'length'):
                    duration = float(info.length)

                # Bitrate (in kbps)
                if hasattr(info, 'bitrate'):
                    bitrate = int(info.bitrate / 1000)  # Convert to kbps

                # Sample rate (in Hz)
                if hasattr(info, 'sample_rate'):
                    sample_rate = int(info.sample_rate)

                # Channels
                if hasattr(info, 'channels'):
                    channels = int(info.channels)

            track = Track(
                file_path=str(file_path),
                title=title,
                artist=artist,
                album=album,
                duration=duration,
                track_number=track_number,
                year=year,
                genre=genre,
                bitrate=bitrate,
                sample_rate=sample_rate,
                channels=channels
            )

            # Enrich with Spotify if requested and service is available
            if enrich_with_spotify and cls._spotify_service and cls._spotify_service.is_available():
                # Enrich all tracks that have artist and title
                if artist != "Unknown Artist" and title:
                    track = cls._spotify_service.enrich_track(track)

            return track

        except Exception as e:
            # If metadata extraction fails, return basic track info
            print(f"[WARNING] Metadata extraction failed for {file_path}: {e}")
            return Track(
                file_path=str(file_path),
                title=file_path.stem
            )

    @classmethod
    async def scan_directory(cls, directory: Path, recursive: bool = True, enrich_with_spotify: bool = False) -> List[Track]:
        """Scan a directory for music files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories recursively
            enrich_with_spotify: Whether to enrich metadata with Spotify

        Returns:
            List of Track objects
        """
        tracks: List[Track] = []

        if not directory.exists() or not directory.is_dir():
            return tracks

        # Use asyncio to scan files
        def scan_sync():
            found_tracks = []
            pattern = '**/*' if recursive else '*'

            for file_path in directory.glob(pattern):
                if file_path.is_file() and cls.is_supported(file_path):
                    track = cls.extract_metadata(file_path, enrich_with_spotify=enrich_with_spotify)
                    found_tracks.append(track)

            return found_tracks

        # Run in executor to avoid blocking
        tracks = await asyncio.to_thread(scan_sync)

        # Sort by artist, then album, then track number
        tracks.sort(key=lambda t: (
            t.artist.lower(),
            t.album.lower(),
            t.track_number if t.track_number is not None else 9999
        ))

        return tracks

    @staticmethod
    async def scan_files(file_paths: List[Path]) -> List[Track]:
        """Extract metadata from a list of files.

        Args:
            file_paths: List of file paths

        Returns:
            List of Track objects
        """
        def scan_sync():
            return [
                FileScanner.extract_metadata(fp)
                for fp in file_paths
                if fp.is_file() and FileScanner.is_supported(fp)
            ]

        tracks = await asyncio.to_thread(scan_sync)
        return tracks
