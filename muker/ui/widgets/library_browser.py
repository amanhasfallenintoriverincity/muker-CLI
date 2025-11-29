"""Library browser widget."""

from pathlib import Path
from textual.widget import Widget
from textual.widgets import DirectoryTree

from muker.core.library import MusicLibrary


class LibraryBrowser(Widget):
    """Widget for browsing and loading music from filesystem."""

    def __init__(self, library: MusicLibrary, initial_path: str = "."):
        """Initialize library browser.

        Args:
            library: Music library instance
            initial_path: Initial directory path
        """
        super().__init__()
        self.library = library
        self.initial_path = Path(initial_path).absolute()

    def on_mount(self):
        """Called when widget is mounted."""
        # Refresh periodically to show library updates
        self.set_interval(0.5, self.refresh)

    def render(self) -> str:
        """Render the library browser."""
        from rich.text import Text

        result = Text()
        result.append("📚 Library", style="bold green")
        result.append("\n")
        result.append("═" * 40, style="green")
        result.append("\n\n")

        if self.library.current_directory:
            result.append("📁 ", style="yellow")
            result.append(str(self.library.current_directory), style="dim")
            result.append("\n\n")

        track_count = self.library.get_track_count()
        if track_count > 0:
            result.append("🎵 Tracks: ", style="bold")
            result.append(f"{track_count}\n", style="cyan")

            # Show some stats
            artists = self.library.get_all_artists()
            albums = self.library.get_all_albums()

            result.append("👤 Artists: ", style="bold")
            result.append(f"{len(artists)}\n", style="cyan")

            result.append("💿 Albums: ", style="bold")
            result.append(f"{len(albums)}\n", style="cyan")
        else:
            result.append("\n" * 3)
            result.append("No music loaded yet", style="dim yellow")
            result.append("\n\n")
            result.append("Press ", style="dim")
            result.append("'o'", style="bold cyan")
            result.append(" to open folder", style="dim")

        return result
