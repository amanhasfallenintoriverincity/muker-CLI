"""Playlist manager module."""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import aiofiles

from muker.models.track import Track
from muker.models.playlist_model import RepeatMode


class PlaylistManager:
    """Manages playlists and playback order."""

    def __init__(self):
        """Initialize playlist manager."""
        self.tracks: List[Track] = []
        self.current_index: int = 0
        self.shuffle_enabled: bool = False
        self.repeat_mode: RepeatMode = RepeatMode.OFF

        # For shuffle mode
        self.shuffle_indices: List[int] = []
        self.shuffle_position: int = 0

    def add_track(self, track: Track):
        """Add a track to the playlist.

        Args:
            track: Track to add
        """
        self.tracks.append(track)
        self._update_shuffle_indices()

    def add_tracks(self, tracks: List[Track]):
        """Add multiple tracks to the playlist.

        Args:
            tracks: List of tracks to add
        """
        self.tracks.extend(tracks)
        self._update_shuffle_indices()

    def remove_track(self, index: int):
        """Remove a track at the given index.

        Args:
            index: Index of track to remove
        """
        if 0 <= index < len(self.tracks):
            self.tracks.pop(index)

            # Adjust current index if necessary
            if self.current_index >= len(self.tracks) and len(self.tracks) > 0:
                self.current_index = len(self.tracks) - 1
            elif len(self.tracks) == 0:
                self.current_index = 0

            self._update_shuffle_indices()

    def clear(self):
        """Clear all tracks from the playlist."""
        self.tracks.clear()
        self.current_index = 0
        self.shuffle_indices.clear()
        self.shuffle_position = 0

    def move_track(self, from_index: int, to_index: int):
        """Move a track from one position to another.

        Args:
            from_index: Current index of the track
            to_index: Target index
        """
        if 0 <= from_index < len(self.tracks) and 0 <= to_index < len(self.tracks):
            track = self.tracks.pop(from_index)
            self.tracks.insert(to_index, track)

            # Adjust current index
            if from_index == self.current_index:
                self.current_index = to_index
            elif from_index < self.current_index <= to_index:
                self.current_index -= 1
            elif to_index <= self.current_index < from_index:
                self.current_index += 1

    def get_current_track(self) -> Optional[Track]:
        """Get the current track.

        Returns:
            Current track or None if playlist is empty
        """
        if not self.tracks:
            return None

        if self.shuffle_enabled and self.shuffle_indices:
            actual_index = self.shuffle_indices[self.shuffle_position]
        else:
            actual_index = self.current_index

        if 0 <= actual_index < len(self.tracks):
            return self.tracks[actual_index]

        return None

    def next_track(self) -> Optional[Track]:
        """Move to the next track.

        Returns:
            Next track or None
        """
        if not self.tracks:
            return None

        if self.shuffle_enabled:
            return self._next_shuffle()
        else:
            return self._next_sequential()

    def _next_sequential(self) -> Optional[Track]:
        """Get next track in sequential order."""
        if self.repeat_mode == RepeatMode.ONE:
            # Stay on current track
            return self.get_current_track()

        self.current_index += 1

        if self.current_index >= len(self.tracks):
            if self.repeat_mode == RepeatMode.ALL:
                self.current_index = 0
            else:
                self.current_index = len(self.tracks) - 1
                return None

        return self.get_current_track()

    def _next_shuffle(self) -> Optional[Track]:
        """Get next track in shuffle order."""
        if not self.shuffle_indices:
            return None

        if self.repeat_mode == RepeatMode.ONE:
            return self.get_current_track()

        self.shuffle_position += 1

        if self.shuffle_position >= len(self.shuffle_indices):
            if self.repeat_mode == RepeatMode.ALL:
                # Reshuffle and start over
                self._shuffle_tracks()
                self.shuffle_position = 0
            else:
                self.shuffle_position = len(self.shuffle_indices) - 1
                return None

        return self.get_current_track()

    def previous_track(self) -> Optional[Track]:
        """Move to the previous track.

        Returns:
            Previous track or None
        """
        if not self.tracks:
            return None

        if self.shuffle_enabled:
            return self._previous_shuffle()
        else:
            return self._previous_sequential()

    def _previous_sequential(self) -> Optional[Track]:
        """Get previous track in sequential order."""
        self.current_index -= 1

        if self.current_index < 0:
            if self.repeat_mode == RepeatMode.ALL:
                self.current_index = len(self.tracks) - 1
            else:
                self.current_index = 0

        return self.get_current_track()

    def _previous_shuffle(self) -> Optional[Track]:
        """Get previous track in shuffle order."""
        if not self.shuffle_indices:
            return None

        self.shuffle_position -= 1

        if self.shuffle_position < 0:
            if self.repeat_mode == RepeatMode.ALL:
                self.shuffle_position = len(self.shuffle_indices) - 1
            else:
                self.shuffle_position = 0

        return self.get_current_track()

    def set_current_index(self, index: int):
        """Set the current track by index.

        Args:
            index: Track index
        """
        if 0 <= index < len(self.tracks):
            self.current_index = index

            if self.shuffle_enabled:
                # Find this index in shuffle order
                try:
                    self.shuffle_position = self.shuffle_indices.index(index)
                except ValueError:
                    pass

    def toggle_shuffle(self) -> bool:
        """Toggle shuffle mode.

        Returns:
            New shuffle state
        """
        self.shuffle_enabled = not self.shuffle_enabled

        if self.shuffle_enabled:
            self._shuffle_tracks()
        else:
            # Return to the actual current track index
            if self.shuffle_indices and 0 <= self.shuffle_position < len(self.shuffle_indices):
                self.current_index = self.shuffle_indices[self.shuffle_position]

        return self.shuffle_enabled

    def toggle_repeat(self) -> RepeatMode:
        """Toggle repeat mode (OFF -> ALL -> ONE -> OFF).

        Returns:
            New repeat mode
        """
        if self.repeat_mode == RepeatMode.OFF:
            self.repeat_mode = RepeatMode.ALL
        elif self.repeat_mode == RepeatMode.ALL:
            self.repeat_mode = RepeatMode.ONE
        else:
            self.repeat_mode = RepeatMode.OFF

        return self.repeat_mode

    def _shuffle_tracks(self):
        """Create shuffled indices using Fisher-Yates algorithm."""
        self.shuffle_indices = list(range(len(self.tracks)))

        if len(self.shuffle_indices) <= 1:
            return

        # Keep current track at current position
        current_track_index = self.current_index

        # Remove current track from shuffle
        self.shuffle_indices.remove(current_track_index)

        # Shuffle remaining tracks
        random.shuffle(self.shuffle_indices)

        # Insert current track at beginning
        self.shuffle_indices.insert(0, current_track_index)
        self.shuffle_position = 0

    def _update_shuffle_indices(self):
        """Update shuffle indices when playlist changes."""
        if self.shuffle_enabled:
            self._shuffle_tracks()

    async def save_playlist(self, name: str, path: Path):
        """Save playlist to JSON file.

        Args:
            name: Playlist name
            path: Directory path to save playlist
        """
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / f"{name}.json"

        playlist_data = {
            'name': name,
            'tracks': [track.to_dict() for track in self.tracks],
            'shuffle': self.shuffle_enabled,
            'repeat': self.repeat_mode.value,
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat()
        }

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(playlist_data, indent=2, ensure_ascii=False))

    async def load_playlist(self, file_path: Path):
        """Load playlist from JSON file.

        Args:
            file_path: Path to playlist JSON file
        """
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            playlist_data = json.loads(content)

        self.clear()

        tracks = [Track.from_dict(track_data) for track_data in playlist_data.get('tracks', [])]
        self.add_tracks(tracks)

        self.shuffle_enabled = playlist_data.get('shuffle', False)

        repeat_str = playlist_data.get('repeat', 'off')
        try:
            self.repeat_mode = RepeatMode(repeat_str)
        except ValueError:
            self.repeat_mode = RepeatMode.OFF

        if self.shuffle_enabled:
            self._shuffle_tracks()

    def get_track_count(self) -> int:
        """Get number of tracks in playlist.

        Returns:
            Track count
        """
        return len(self.tracks)

    def get_total_duration(self) -> float:
        """Get total duration of all tracks.

        Returns:
            Total duration in seconds
        """
        return sum(track.duration for track in self.tracks)
