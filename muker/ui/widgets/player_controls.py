"""Player controls widget."""

from textual.widget import Widget
from rich.text import Text
from rich.panel import Panel

from muker.core.player import AudioPlayer
from muker.core.playlist import PlaylistManager
from muker.utils.audio_utils import format_time


class PlayerControls(Widget):
    """Widget for displaying player controls and current track info."""

    def __init__(self, player: AudioPlayer, playlist: PlaylistManager):
        """Initialize player controls.

        Args:
            player: Audio player instance
            playlist: Playlist manager instance
        """
        super().__init__()
        self.player = player
        self.playlist = playlist

    def on_mount(self):
        """Called when widget is mounted."""
        # Update display frequently
        self.set_interval(0.1, self.refresh)

    def render(self) -> Text:
        """Render the player controls.

        Returns:
            Rich Text with player information
        """
        result = Text()

        # Current track info (top line)
        current_track = self.playlist.get_current_track()
        if current_track:
            # Main track info
            track_info = f"♫ {current_track.artist} - {current_track.title}"
            result.append(track_info, style="bold cyan")

            result.append("\n")

            # Secondary info line (album, year, genre)
            secondary_parts = []

            if current_track.album and current_track.album != "Unknown Album":
                album_str = current_track.album
                if current_track.track_number:
                    album_str = f"#{current_track.track_number} {album_str}"
                secondary_parts.append(album_str)

            if current_track.year:
                secondary_parts.append(f"({current_track.year})")

            if current_track.genre:
                secondary_parts.append(f"[{current_track.genre}]")

            if secondary_parts:
                result.append("  " + " · ".join(secondary_parts), style="dim cyan")
                result.append("\n")

            # Technical info line (format, bitrate, sample rate)
            tech_parts = []

            # File format
            tech_parts.append(current_track.extension.upper().replace('.', ''))

            # Bitrate
            if current_track.bitrate:
                tech_parts.append(f"{current_track.bitrate}kbps")

            # Sample rate
            if current_track.sample_rate:
                if current_track.sample_rate >= 1000:
                    tech_parts.append(f"{current_track.sample_rate / 1000:.1f}kHz")
                else:
                    tech_parts.append(f"{current_track.sample_rate}Hz")

            # Channels
            if current_track.channels:
                tech_parts.append(current_track.format_channels())

            if tech_parts:
                result.append("  " + " │ ".join(tech_parts), style="dim white")
        else:
            result.append("No track loaded", style="dim")

        result.append("\n\n")

        # Time info
        position = self.player.get_position()
        duration = self.player.get_duration()
        time_start = format_time(position)
        time_end = format_time(duration)

        # Large progress bar with percentage
        progress = self.player.get_progress()
        # Use full width minus some padding
        bar_width = max(60, self.size.width - 30) if self.size.width > 30 else 40
        filled = int(progress * bar_width)
        empty = bar_width - filled

        # Create colorful progress bar
        result.append(time_start + " ", style="cyan")
        result.append("━" * filled, style="bold green")
        result.append("━" * empty, style="dim white")
        result.append(" " + time_end, style="cyan")
        result.append(f" ({int(progress * 100)}%)", style="yellow")

        result.append("\n\n")

        # Playback controls line
        if self.player.is_playing and not self.player.is_paused:
            play_symbol = "⏸ "
            play_style = "bold yellow"
        else:
            play_symbol = "▶ "
            play_style = "bold green"

        result.append("  ⏮ ", style="bold white")
        result.append(play_symbol, style=play_style)
        result.append("⏭  ", style="bold white")

        # Volume bar
        volume = self.player.get_volume()
        volume_width = 20
        vol_filled = int(volume * volume_width)
        vol_empty = volume_width - vol_filled

        result.append("  │  🔊 ", style="white")
        result.append("█" * vol_filled, style="bold magenta")
        result.append("─" * vol_empty, style="dim white")
        result.append(f" {int(volume * 100)}%", style="magenta")

        # Playback mode info
        mode_parts = []
        if self.playlist.shuffle_enabled:
            mode_parts.append("🔀")
        if self.playlist.repeat_mode.value == "all":
            mode_parts.append("🔁")
        elif self.playlist.repeat_mode.value == "one":
            mode_parts.append("🔂")

        if mode_parts:
            result.append("  │  " + " ".join(mode_parts), style="bold blue")

        # Lyrics toggle info
        result.append("  │  📜 Lyrics (l)", style="bold purple")

        return result
