"""File scanner utility for finding music files."""

import asyncio
from pathlib import Path
from typing import List, Set
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

    @staticmethod
    def is_supported(file_path: Path) -> bool:
        """Check if a file is a supported audio format.

        Args:
            file_path: Path to check

        Returns:
            True if file is supported
        """
        return file_path.suffix.lower() in FileScanner.SUPPORTED_EXTENSIONS

    @staticmethod
    def extract_metadata(file_path: Path) -> Track:
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

            # Get duration
            if hasattr(audio.info, 'length'):
                duration = float(audio.info.length)

            return Track(
                file_path=str(file_path),
                title=title,
                artist=artist,
                album=album,
                duration=duration,
                track_number=track_number,
                year=year,
                genre=genre
            )

        except Exception as e:
            # If metadata extraction fails, return basic track info
            return Track(
                file_path=str(file_path),
                title=file_path.stem
            )

    @staticmethod
    async def scan_directory(directory: Path, recursive: bool = True) -> List[Track]:
        """Scan a directory for music files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories recursively

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
                if file_path.is_file() and FileScanner.is_supported(file_path):
                    track = FileScanner.extract_metadata(file_path)
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
