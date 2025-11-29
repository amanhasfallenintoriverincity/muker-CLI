"""Main screen for Muker music player."""

from pathlib import Path
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static
from textual.binding import Binding

from muker.core.player import AudioPlayer
from muker.core.playlist import PlaylistManager
from muker.core.library import MusicLibrary
from muker.core.visualizer import AudioVisualizer

from muker.ui.widgets.visualizer_widget import VisualizerWidget
from muker.ui.widgets.playlist_view import PlaylistView
from muker.ui.widgets.player_controls import PlayerControls
from muker.ui.widgets.library_browser import LibraryBrowser


class MainScreen(Screen):
    """Main screen with player interface."""

    BINDINGS = [
        Binding("space", "toggle_play", "Play/Pause"),
        Binding("n", "next_track", "Next"),
        Binding("p", "previous_track", "Previous"),
        Binding("up,+", "volume_up", "Volume Up"),
        Binding("down,-", "volume_down", "Volume Down"),
        Binding("s", "toggle_shuffle", "Shuffle"),
        Binding("r", "toggle_repeat", "Repeat"),
        Binding("v", "cycle_visualizer", "Visualizer"),
        Binding("o", "open_folder", "Open Folder"),
    ]

    def __init__(
        self,
        player: AudioPlayer,
        playlist: PlaylistManager,
        library: MusicLibrary,
        visualizer: AudioVisualizer
    ):
        """Initialize main screen.

        Args:
            player: Audio player instance
            playlist: Playlist manager instance
            library: Music library instance
            visualizer: Audio visualizer instance
        """
        super().__init__()
        self.player = player
        self.playlist = playlist
        self.library = library
        self.visualizer = visualizer

    def compose(self):
        """Create the screen layout."""
        with Container(id="main-container"):
            # Visualizer area (top 30%)
            with Container(id="visualizer-container"):
                yield VisualizerWidget(self.visualizer)

            # Content area (middle 50%)
            with Horizontal(id="content-container"):
                # Library browser (left 40%)
                with Vertical(id="library-panel"):
                    yield LibraryBrowser(self.library)

                # Playlist view (right 60%)
                with Vertical(id="playlist-panel"):
                    yield PlaylistView(self.playlist)

            # Player controls (bottom 20%)
            with Container(id="controls-container"):
                yield PlayerControls(self.player, self.playlist)

    async def action_toggle_play(self):
        """Toggle play/pause."""
        if self.player.is_playing:
            if self.player.is_paused:
                await self.player.play()
            else:
                await self.player.pause()
        else:
            # Start playing current track
            track = self.playlist.get_current_track()
            if track:
                await self.player.load_track(track)
                await self.player.play()

    async def action_next_track(self):
        """Play next track."""
        next_track = self.playlist.next_track()
        if next_track:
            await self.player.load_track(next_track)
            await self.player.play()

    async def action_previous_track(self):
        """Play previous track."""
        prev_track = self.playlist.previous_track()
        if prev_track:
            await self.player.load_track(prev_track)
            await self.player.play()

    def action_volume_up(self):
        """Increase volume."""
        current_volume = self.player.get_volume()
        new_volume = min(1.0, current_volume + 0.05)
        self.player.set_volume(new_volume)

    def action_volume_down(self):
        """Decrease volume."""
        current_volume = self.player.get_volume()
        new_volume = max(0.0, current_volume - 0.05)
        self.player.set_volume(new_volume)

    def action_toggle_shuffle(self):
        """Toggle shuffle mode."""
        self.playlist.toggle_shuffle()

    def action_toggle_repeat(self):
        """Toggle repeat mode."""
        self.playlist.toggle_repeat()

    def action_cycle_visualizer(self):
        """Cycle through visualizer styles."""
        self.visualizer.cycle_style()

    async def action_open_folder(self):
        """Open folder dialog and scan for music files."""
        # For now, use a simple default directory
        # In a full implementation, this would show a directory picker dialog

        # Try to use user's Music folder
        music_dir = Path.home() / "Music"
        if not music_dir.exists():
            music_dir = Path.home()

        try:
            self.notify(f"Scanning {music_dir}...", timeout=2)
            print(f"[DEBUG] Scanning directory: {music_dir}")

            # Scan directory for music files
            tracks = await self.library.scan_directory(music_dir, recursive=True)
            print(f"[DEBUG] Found {len(tracks)} tracks")

            # Add tracks to playlist
            self.playlist.clear()
            self.playlist.add_tracks(tracks)
            print(f"[DEBUG] Added {len(tracks)} tracks to playlist")

            self.notify(f"Loaded {len(tracks)} tracks", severity="information", timeout=3)

            # Force refresh of playlist view
            try:
                playlist_view = self.query_one(PlaylistView)
                if playlist_view:
                    print("[DEBUG] Forcing playlist view update")
                    playlist_view.update_playlist()
            except Exception as ex:
                print(f"[DEBUG] Could not update playlist view: {ex}")

            # Start playing first track if available
            if tracks:
                first_track = self.playlist.get_current_track()
                print(f"[DEBUG] First track: {first_track.title if first_track else 'None'}")
                if first_track:
                    print(f"[DEBUG] Loading first track: {first_track.file_path}")
                    await self.player.load_track(first_track)
                    await self.player.play()
            else:
                print("[DEBUG] No tracks to play")
        except Exception as e:
            # Handle error (would show error dialog in full implementation)
            import traceback
            self.notify(f"Error loading music: {str(e)}", severity="error", timeout=5)
            traceback.print_exc()

    async def on_playlist_view_track_selected(self, message: PlaylistView.TrackSelected) -> None:
        """Handle track selection from playlist view.

        Args:
            message: TrackSelected message containing the selected track
        """
        try:
            # Load and play the selected track
            await self.player.load_track(message.track)
            await self.player.play()

            self.notify(
                f"Now playing: {message.track.artist} - {message.track.title}",
                severity="information",
                timeout=2
            )
        except Exception as e:
            self.notify(f"Error playing track: {str(e)}", severity="error", timeout=3)
