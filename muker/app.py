"""Main Textual application for Muker music player."""

import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

# Removed MainScreen import - not used
from muker.core.player import AudioPlayer
from muker.core.playlist import PlaylistManager
from muker.core.library import MusicLibrary
from muker.core.visualizer import AudioVisualizer
from muker.utils.config import Config

print("[DEBUG] app.py imports completed successfully")


class MukerApp(App):
    """Muker CLI Music Player Application."""

    # Get CSS path relative to this file
    _css_path = Path(__file__).parent / "ui" / "styles.tcss"
    print(f"[DEBUG] CSS path: {_css_path}")
    print(f"[DEBUG] CSS file exists: {_css_path.exists()}")

    # Enable CSS for better styling
    CSS_PATH = str(_css_path) if _css_path.exists() else None
    TITLE = "Muker - CLI Music Player"

    BINDINGS = [
        Binding("space", "toggle_play", "Play/Pause", priority=True),
        Binding("n", "next_track", "Next", priority=True),
        Binding("p", "previous_track", "Previous", priority=True),
        Binding("up,+", "volume_up", "Volume Up", priority=True),
        Binding("down,-", "volume_down", "Volume Down", priority=True),
        Binding("s", "toggle_shuffle", "Shuffle", priority=True),
        Binding("r", "toggle_repeat", "Repeat", priority=True),
        Binding("v", "cycle_visualizer", "Visualizer", priority=True),
        Binding("l", "toggle_lyrics", "Lyrics", priority=True),
        Binding("o", "open_folder", "Open Folder", priority=True),
        Binding("q", "quit", "Quit", priority=True),
    ]

    def __init__(self):
        """Initialize the Muker application."""
        print("[DEBUG] Initializing MukerApp...")
        super().__init__()

        # Core components
        print("[DEBUG] Creating Config...")
        self.config = Config()
        print("[DEBUG] Creating AudioPlayer...")
        self.player = AudioPlayer()
        print("[DEBUG] Creating PlaylistManager...")
        self.playlist = PlaylistManager()
        print("[DEBUG] Creating MusicLibrary...")
        self.library = MusicLibrary()
        print("[DEBUG] Creating AudioVisualizer...")
        self.visualizer = AudioVisualizer()

        # Background task for PCM processing
        self.pcm_task = None
        print("[DEBUG] MukerApp initialization complete")

    def compose(self) -> ComposeResult:
        """Create the application layout.

        Returns:
            Composed widgets
        """
        print("[DEBUG] compose() called")
        from textual.containers import Container, Vertical, Horizontal
        from textual.widgets import Static

        print("[DEBUG] Importing widgets...")
        try:
            from muker.ui.widgets.visualizer_widget import VisualizerWidget
            print("[DEBUG] VisualizerWidget imported")
        except Exception as e:
            print(f"[ERROR] Failed to import VisualizerWidget: {e}")
            VisualizerWidget = None

        try:
            from muker.ui.widgets.playlist_view import PlaylistView
            print("[DEBUG] PlaylistView imported")
        except Exception as e:
            print(f"[ERROR] Failed to import PlaylistView: {e}")
            PlaylistView = None

        try:
            from muker.ui.widgets.player_controls import PlayerControls
            print("[DEBUG] PlayerControls imported")
        except Exception as e:
            print(f"[ERROR] Failed to import PlayerControls: {e}")
            PlayerControls = None

        try:
            from muker.ui.widgets.library_browser import LibraryBrowser
            print("[DEBUG] LibraryBrowser imported")
        except Exception as e:
            print(f"[ERROR] Failed to import LibraryBrowser: {e}")
            LibraryBrowser = None

        try:
            from muker.ui.widgets.lyrics_panel import LyricsPanel
            print("[DEBUG] LyricsPanel imported")
        except Exception as e:
            print(f"[ERROR] Failed to import LyricsPanel: {e}")
            LyricsPanel = None

        print("[DEBUG] Creating layout...")
        yield Header()

        with Container(id="main-container"):
            with Container(id="visualizer-container"):
                if VisualizerWidget:
                    print("[DEBUG] Creating VisualizerWidget...")
                    try:
                        yield VisualizerWidget(self.visualizer)
                        print("[DEBUG] VisualizerWidget created")
                    except Exception as e:
                        print(f"[ERROR] Failed to create VisualizerWidget: {e}")
                        yield Static(f"Error: {e}")
                else:
                    yield Static("VisualizerWidget import failed")

            with Horizontal(id="content-container"):
                with Vertical(id="library-panel", classes="hidden"):
                    if LibraryBrowser:
                        print("[DEBUG] Creating LibraryBrowser...")
                        try:
                            yield LibraryBrowser(self.library)
                            print("[DEBUG] LibraryBrowser created")
                        except Exception as e:
                            print(f"[ERROR] Failed to create LibraryBrowser: {e}")
                            yield Static(f"Error: {e}")
                    else:
                        yield Static("LibraryBrowser import failed")

                with Vertical(id="playlist-panel"):
                    if PlaylistView:
                        print("[DEBUG] Creating PlaylistView...")
                        try:
                            yield PlaylistView(self.playlist)
                            print("[DEBUG] PlaylistView created")
                        except Exception as e:
                            print(f"[ERROR] Failed to create PlaylistView: {e}")
                            yield Static(f"Error: {e}")
                    else:
                        yield Static("PlaylistView import failed")

                with Vertical(id="lyrics-panel"):
                    if LyricsPanel:
                        print("[DEBUG] Creating LyricsPanel...")
                        try:
                            yield LyricsPanel(self.player, self.playlist)
                            print("[DEBUG] LyricsPanel created")
                        except Exception as e:
                            print(f"[ERROR] Failed to create LyricsPanel: {e}")
                            yield Static(f"Error: {e}")
                    else:
                        yield Static("LyricsPanel import failed")

            with Container(id="controls-container"):
                if PlayerControls:
                    print("[DEBUG] Creating PlayerControls...")
                    try:
                        yield PlayerControls(self.player, self.playlist)
                        print("[DEBUG] PlayerControls created")
                    except Exception as e:
                        print(f"[ERROR] Failed to create PlayerControls: {e}")
                        yield Static(f"Error: {e}")
                else:
                    yield Static("PlayerControls import failed")

        yield Footer()
        print("[DEBUG] compose() complete")

    async def on_mount(self):
        """Called when app is mounted."""
        print("[DEBUG] App mounted")
        # Set up player callbacks
        self.player.on_track_end = self._on_track_end

        # Load config
        volume = self.config.get('volume', 0.7)
        self.player.set_volume(volume)

        # Start PCM processing task
        self.pcm_task = asyncio.create_task(self._process_pcm_data())

    async def on_key(self, event) -> None:
        """Handle key press events."""
        print(f"[DEBUG] Key pressed: {event.key}")
        # Let the default handler process it

    async def _process_pcm_data(self):
        """Background task to process PCM data for visualizer."""
        while True:
            try:
                if self.player.is_playing:
                    # Get PCM data from player
                    pcm_data = await asyncio.to_thread(self.player.get_pcm_data)

                    # Process with visualizer
                    self.visualizer.process_audio(pcm_data)

                # Update at ~30 FPS
                await asyncio.sleep(1/30)

            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue
                pass

    async def _fetch_lyrics_for_track(self, track):
        """Fetch lyrics for a track if available.

        Args:
            track: Track to fetch lyrics for
        """
        # Check if Spotify service is available
        if not hasattr(self.library, 'spotify_enabled') or not self.library.spotify_enabled:
            return

        # Skip if track already has lyrics
        if track.lyrics:
            return

        # Skip if no Spotify track ID
        if not track.spotify_track_id:
            return

        try:
            # Import SpotifyService
            from muker.services.spotify_service import SpotifyService
            from muker.utils.file_scanner import FileScanner

            # Get Spotify service instance
            spotify_service = FileScanner._spotify_service
            if not spotify_service:
                return

            # Fetch lyrics in background
            await asyncio.to_thread(
                spotify_service.enrich_track_with_lyrics,
                track,
                format="lrc"
            )
        except Exception as e:
            print(f"[WARNING] Failed to fetch lyrics: {e}")

    async def _on_track_end(self):
        """Handle track end event."""
        # Get next track from playlist
        next_track = self.playlist.next_track()

        if next_track:
            # Fetch lyrics for next track
            await self._fetch_lyrics_for_track(next_track)

            # Load and play next track
            await self.player.load_track(next_track)
            await self.player.play()

    async def on_unmount(self):
        """Called when app is unmounted."""
        # Cancel PCM task
        if self.pcm_task:
            self.pcm_task.cancel()
            try:
                await self.pcm_task
            except asyncio.CancelledError:
                pass

        # Clean up player
        await self.player.cleanup()

        # Save config
        self.config.set('volume', self.player.get_volume())
        self.config.save()

    def action_quit(self):
        """Quit the application."""
        self.exit()

    async def action_toggle_play(self):
        """Toggle play/pause."""
        print("[DEBUG] action_toggle_play called")
        print(f"[DEBUG] Player state - is_playing: {self.player.is_playing}, is_paused: {self.player.is_paused}")
        print(f"[DEBUG] Playlist has {len(self.playlist.tracks)} tracks")

        if self.player.is_playing:
            if self.player.is_paused:
                print("[DEBUG] Resuming from pause")
                await self.player.play()
            else:
                print("[DEBUG] Pausing playback")
                await self.player.pause()
        else:
            # Start playing current track
            track = self.playlist.get_current_track()
            print(f"[DEBUG] Current track: {track.title if track else 'None'}")
            if track:
                print(f"[DEBUG] Loading and playing track: {track.file_path}")
                # Fetch lyrics for track
                await self._fetch_lyrics_for_track(track)
                await self.player.load_track(track)
                await self.player.play()
            else:
                print("[DEBUG] No track available to play")
                self.notify("No tracks loaded. Press 'o' to open a folder.", severity="warning", timeout=3)

    async def action_next_track(self):
        """Play next track."""
        next_track = self.playlist.next_track()
        if next_track:
            await self._fetch_lyrics_for_track(next_track)
            await self.player.load_track(next_track)
            await self.player.play()

    async def action_previous_track(self):
        """Play previous track."""
        prev_track = self.playlist.previous_track()
        if prev_track:
            await self._fetch_lyrics_for_track(prev_track)
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

    def action_toggle_lyrics(self):
        """Toggle lyrics panel visibility."""
        lyrics_panel = self.query_one("#lyrics-panel")
        library_panel = self.query_one("#library-panel")
        lyrics_panel.toggle_class("hidden")
        library_panel.toggle_class("hidden")

    async def action_open_folder(self):
        """Open folder dialog and scan for music files."""
        from pathlib import Path
        from muker.ui.widgets.playlist_view import PlaylistView

        # Try to use user's Music folder
        music_dir = Path.home() / "Music"
        if not music_dir.exists():
            music_dir = Path.home()

        print(f"[DEBUG] Music folder exists: {music_dir.exists()}")
        print(f"[DEBUG] Music folder path: {music_dir}")

        # List files in the directory for debugging
        if music_dir.exists():
            try:
                files = list(music_dir.glob("*.mp3"))
                print(f"[DEBUG] Found {len(files)} MP3 files in {music_dir}")
                if files:
                    for f in files[:5]:  # Show first 5
                        print(f"[DEBUG]   - {f.name}")
            except Exception as e:
                print(f"[DEBUG] Error listing files: {e}")

        try:
            self.notify(f"Scanning {music_dir}...", timeout=2)
            print(f"[DEBUG] Starting scan of directory: {music_dir}")

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
                    await self._fetch_lyrics_for_track(first_track)
                    await self.player.load_track(first_track)
                    await self.player.play()
            else:
                print("[DEBUG] No tracks to play")
        except Exception as e:
            # Handle error (would show error dialog in full implementation)
            import traceback
            self.notify(f"Error loading music: {str(e)}", severity="error", timeout=5)
            traceback.print_exc()

    async def on_playlist_view_track_selected(self, message) -> None:
        """Handle track selection from playlist view.

        Args:
            message: TrackSelected message containing the selected track
        """
        print("[DEBUG] on_playlist_view_track_selected called")
        print(f"[DEBUG] Selected track: {message.track.title} - {message.track.artist}")
        try:
            # Fetch lyrics for the selected track
            await self._fetch_lyrics_for_track(message.track)
            # Load and play the selected track
            await self.player.load_track(message.track)
            await self.player.play()

            self.notify(
                f"Now playing: {message.track.artist} - {message.track.title}",
                severity="information",
                timeout=2
            )
        except Exception as e:
            print(f"[ERROR] Error playing selected track: {e}")
            import traceback
            traceback.print_exc()
            self.notify(f"Error playing track: {str(e)}", severity="error", timeout=3)


if __name__ == "__main__":
    app = MukerApp()
    app.run()
