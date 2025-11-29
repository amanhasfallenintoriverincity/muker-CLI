"""Main Textual application for Muker music player."""

import asyncio
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

from muker.ui.screens.main_screen import MainScreen
from muker.core.player import AudioPlayer
from muker.core.playlist import PlaylistManager
from muker.core.library import MusicLibrary
from muker.core.visualizer import AudioVisualizer
from muker.utils.config import Config


class MukerApp(App):
    """Muker CLI Music Player Application."""

    CSS_PATH = "ui/styles.tcss"
    TITLE = "Muker - CLI Music Player"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
    ]

    def __init__(self):
        """Initialize the Muker application."""
        super().__init__()

        # Core components
        self.config = Config()
        self.player = AudioPlayer()
        self.playlist = PlaylistManager()
        self.library = MusicLibrary()
        self.visualizer = AudioVisualizer()

        # Background task for PCM processing
        self.pcm_task = None

    def compose(self) -> ComposeResult:
        """Create the application layout.

        Returns:
            Composed widgets
        """
        yield Header()
        yield MainScreen(
            player=self.player,
            playlist=self.playlist,
            library=self.library,
            visualizer=self.visualizer
        )
        yield Footer()

    async def on_mount(self):
        """Called when app is mounted."""
        # Set up player callbacks
        self.player.on_track_end = self._on_track_end

        # Load config
        volume = self.config.get('volume', 0.7)
        self.player.set_volume(volume)

        # Start PCM processing task
        self.pcm_task = asyncio.create_task(self._process_pcm_data())

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

    async def _on_track_end(self):
        """Handle track end event."""
        # Get next track from playlist
        next_track = self.playlist.next_track()

        if next_track:
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


if __name__ == "__main__":
    app = MukerApp()
    app.run()
