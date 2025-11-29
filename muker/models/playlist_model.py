"""Playlist data model."""

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class RepeatMode(Enum):
    """Repeat mode enumeration."""
    OFF = "off"
    ONE = "one"
    ALL = "all"


@dataclass
class PlaylistModel:
    """Represents a playlist with its metadata."""

    name: str
    tracks: List[str] = field(default_factory=list)  # List of file paths
    shuffle: bool = False
    repeat: RepeatMode = RepeatMode.OFF
    created_at: str = ""
    modified_at: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> 'PlaylistModel':
        """Create a PlaylistModel from a dictionary.

        Args:
            data: Dictionary containing playlist data

        Returns:
            PlaylistModel instance
        """
        repeat_mode = data.get('repeat', 'off')
        if isinstance(repeat_mode, str):
            try:
                repeat_mode = RepeatMode(repeat_mode)
            except ValueError:
                repeat_mode = RepeatMode.OFF

        return cls(
            name=data.get('name', 'Untitled Playlist'),
            tracks=data.get('tracks', []),
            shuffle=data.get('shuffle', False),
            repeat=repeat_mode,
            created_at=data.get('created_at', ''),
            modified_at=data.get('modified_at', '')
        )

    def to_dict(self) -> dict:
        """Convert PlaylistModel to dictionary for serialization.

        Returns:
            Dictionary representation of the playlist
        """
        return {
            'name': self.name,
            'tracks': self.tracks,
            'shuffle': self.shuffle,
            'repeat': self.repeat.value,
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }
