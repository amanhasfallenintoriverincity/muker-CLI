"""Track data model."""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class Track:
    """Represents a music track with metadata."""

    file_path: str
    title: str
    artist: str = "Unknown Artist"
    album: str = "Unknown Album"
    duration: float = 0.0
    track_number: Optional[int] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    bitrate: Optional[int] = None  # in kbps
    sample_rate: Optional[int] = None  # in Hz
    channels: Optional[int] = None  # 1=mono, 2=stereo
    spotify_track_id: Optional[str] = None  # Spotify track ID for lyrics
    lyrics: Optional[dict] = None  # Lyrics data from Spotify

    @classmethod
    def from_dict(cls, data: dict) -> 'Track':
        """Create a Track instance from a dictionary.

        Args:
            data: Dictionary containing track data

        Returns:
            Track instance
        """
        return cls(
            file_path=data.get('path', data.get('file_path', '')),
            title=data.get('title', 'Unknown Title'),
            artist=data.get('artist', 'Unknown Artist'),
            album=data.get('album', 'Unknown Album'),
            duration=data.get('duration', 0.0),
            track_number=data.get('track_number'),
            year=data.get('year'),
            genre=data.get('genre'),
            bitrate=data.get('bitrate'),
            sample_rate=data.get('sample_rate'),
            channels=data.get('channels'),
            spotify_track_id=data.get('spotify_track_id'),
            lyrics=data.get('lyrics')
        )

    def to_dict(self) -> dict:
        """Convert Track to dictionary for serialization.

        Returns:
            Dictionary representation of the track
        """
        return {
            'path': self.file_path,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'track_number': self.track_number,
            'year': self.year,
            'genre': self.genre,
            'bitrate': self.bitrate,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'spotify_track_id': self.spotify_track_id,
            'lyrics': self.lyrics
        }

    @property
    def filename(self) -> str:
        """Get the filename without path."""
        return Path(self.file_path).name

    @property
    def extension(self) -> str:
        """Get the file extension."""
        return Path(self.file_path).suffix.lower()

    def format_duration(self) -> str:
        """Format duration as MM:SS.

        Returns:
            Formatted duration string
        """
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def format_bitrate(self) -> str:
        """Format bitrate in kbps.

        Returns:
            Formatted bitrate string
        """
        if self.bitrate:
            return f"{self.bitrate} kbps"
        return "N/A"

    def format_sample_rate(self) -> str:
        """Format sample rate.

        Returns:
            Formatted sample rate string
        """
        if self.sample_rate:
            if self.sample_rate >= 1000:
                return f"{self.sample_rate / 1000:.1f} kHz"
            return f"{self.sample_rate} Hz"
        return "N/A"

    def format_channels(self) -> str:
        """Format channel information.

        Returns:
            Formatted channel string
        """
        if self.channels == 1:
            return "Mono"
        elif self.channels == 2:
            return "Stereo"
        elif self.channels:
            return f"{self.channels} channels"
        return "N/A"

    def get_detailed_info(self) -> str:
        """Get detailed track information as formatted string.

        Returns:
            Multi-line formatted track information
        """
        info_lines = []
        info_lines.append(f"Title: {self.title}")
        info_lines.append(f"Artist: {self.artist}")

        if self.album and self.album != "Unknown Album":
            album_str = self.album
            if self.track_number:
                album_str += f" (Track {self.track_number})"
            info_lines.append(f"Album: {album_str}")

        if self.year:
            info_lines.append(f"Year: {self.year}")

        if self.genre:
            info_lines.append(f"Genre: {self.genre}")

        info_lines.append(f"Duration: {self.format_duration()}")
        info_lines.append(f"Format: {self.extension.upper()}")

        if self.bitrate:
            info_lines.append(f"Bitrate: {self.format_bitrate()}")

        if self.sample_rate:
            info_lines.append(f"Sample Rate: {self.format_sample_rate()}")

        if self.channels:
            info_lines.append(f"Channels: {self.format_channels()}")

        return "\n".join(info_lines)

    def __str__(self) -> str:
        """String representation of the track."""
        return f"{self.artist} - {self.title}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Track(title='{self.title}', artist='{self.artist}', duration={self.duration})"
