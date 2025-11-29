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
            genre=data.get('genre')
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
            'genre': self.genre
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

    def __str__(self) -> str:
        """String representation of the track."""
        return f"{self.artist} - {self.title}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Track(title='{self.title}', artist='{self.artist}', duration={self.duration})"
