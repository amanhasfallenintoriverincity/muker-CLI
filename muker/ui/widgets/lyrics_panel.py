"""Lyrics panel widget for displaying synchronized lyrics."""

from textual.widget import Widget
from textual.containers import VerticalScroll
from textual.widgets import Static
from rich.text import Text
from typing import Optional, List, Dict, Any

from muker.core.player import AudioPlayer
from muker.core.playlist import PlaylistManager


class LyricsPanel(Widget):
    """Widget for displaying synchronized lyrics."""

    def __init__(self, player: AudioPlayer, playlist: PlaylistManager):
        """Initialize lyrics panel.

        Args:
            player: Audio player instance
            playlist: Playlist manager instance
        """
        super().__init__()
        self.player = player
        self.playlist = playlist
        self.current_lyrics: Optional[Dict[str, Any]] = None
        self.current_line_index: int = -1

    def on_mount(self):
        """Called when widget is mounted."""
        # Update display at 10 FPS for smooth scrolling
        self.set_interval(0.1, self.update_lyrics_display)

    def update_lyrics_display(self):
        """Update lyrics display based on current playback position."""
        current_track = self.playlist.get_current_track()

        # Check if track changed
        if current_track and current_track.lyrics:
            if self.current_lyrics != current_track.lyrics:
                self.current_lyrics = current_track.lyrics
                self.current_line_index = -1
        else:
            if self.current_lyrics is not None:
                self.current_lyrics = None
                self.current_line_index = -1

        self.refresh()

    def _parse_time_tag(self, time_tag: str) -> float:
        """Parse LRC time tag to seconds.

        Args:
            time_tag: Time tag in format MM:SS.mm

        Returns:
            Time in seconds
        """
        try:
            parts = time_tag.split(':')
            if len(parts) != 2:
                return 0.0

            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        except (ValueError, IndexError):
            return 0.0

    def _get_current_line_index(self, position: float, lines: List[Dict[str, str]]) -> int:
        """Get the index of the current lyric line based on playback position.

        Args:
            position: Current playback position in seconds
            lines: List of lyric lines with time tags

        Returns:
            Index of current line, or -1 if none
        """
        if not lines:
            return -1

        current_index = -1
        for i, line in enumerate(lines):
            line_time = self._parse_time_tag(line.get('timeTag', '00:00.00'))
            if line_time <= position:
                current_index = i
            else:
                break

        return current_index

    def render(self) -> Text:
        """Render the lyrics panel.

        Returns:
            Rich Text with lyrics
        """
        result = Text()

        if not self.current_lyrics:
            # No lyrics available
            current_track = self.playlist.get_current_track()
            if current_track:
                result.append("♪ No lyrics available\n", style="dim italic")
                result.append(f"\n{current_track.artist} - {current_track.title}", style="dim")
            else:
                result.append("♪ No track playing", style="dim italic")
            return result

        # Get lyrics data
        sync_type = self.current_lyrics.get('syncType', 'UNSYNCED')
        lines = self.current_lyrics.get('lines', [])

        if not lines:
            result.append("♪ No lyrics found", style="dim italic")
            return result

        # Get current playback position
        position = self.player.get_position()

        # Find current line for synced lyrics
        if sync_type == "LINE_SYNCED":
            self.current_line_index = self._get_current_line_index(position, lines)
            print(f"[DEBUG-LYRICS-PANEL] Position: {position:.2f}s, Current Line Index: {self.current_line_index}")

        # Display lyrics with highlighting
        total_lines = len(lines)

        # Calculate visible range (show 3 lines before and after current)
        visible_before = 3
        visible_after = 5

        if sync_type == "LINE_SYNCED" and self.current_line_index >= 0:
            start_idx = max(0, self.current_line_index - visible_before)
            end_idx = min(total_lines, self.current_line_index + visible_after + 1)
        else:
            # For unsynced, show first 10 lines
            start_idx = 0
            end_idx = min(total_lines, 10)

        # Add some spacing at top
        if sync_type == "LINE_SYNCED" and self.current_line_index >= 0:
            result.append("\n" * 2)

        # Render visible lines
        for i in range(start_idx, end_idx):
            line = lines[i]
            words = line.get('words', '').strip()

            if not words:
                result.append("\n")
                continue

            # Highlight current line
            if sync_type == "LINE_SYNCED" and i == self.current_line_index:
                result.append("  ▶ ", style="bold cyan")
                result.append(words, style="bold white")
                result.append("\n")
            # Dim past lines
            elif sync_type == "LINE_SYNCED" and i < self.current_line_index:
                result.append("    ", style="dim")
                result.append(words, style="dim white")
                result.append("\n")
            # Normal future lines
            else:
                result.append("    ")
                result.append(words, style="white")
                result.append("\n")

        # Add spacing at bottom
        if sync_type == "LINE_SYNCED":
            result.append("\n" * 3)

        return result
