"""Playlist view widget."""

from textual.widget import Widget
from textual.widgets import ListView, ListItem, Label
from textual.reactive import reactive
from textual.message import Message

from muker.core.playlist import PlaylistManager
from muker.models.track import Track


class PlaylistView(Widget):
    """Widget for displaying and managing the current playlist."""

    current_index: reactive[int] = reactive(0)
    track_count: reactive[int] = reactive(0)

    class TrackSelected(Message):
        """Message sent when a track is selected."""

        def __init__(self, track_index: int, track: Track):
            super().__init__()
            self.track_index = track_index
            self.track = track

    def __init__(self, playlist: PlaylistManager):
        """Initialize playlist view.

        Args:
            playlist: Playlist manager instance
        """
        super().__init__()
        self.playlist = playlist

    def compose(self):
        """Create the playlist view layout."""
        yield Label("Playlist", id="playlist-title")
        yield ListView(id="playlist-list")

    def on_mount(self):
        """Called when widget is mounted."""
        self.track_count = len(self.playlist.tracks)
        self.update_playlist()
        # Refresh periodically to check for updates
        self.set_interval(0.1, self.check_updates)

    def check_updates(self):
        """Check if playlist has been updated."""
        current_count = len(self.playlist.tracks)
        current_idx = self.playlist.current_index

        if current_count != self.track_count or current_idx != self.current_index:
            self.track_count = current_count
            self.current_index = current_idx
            self.update_playlist()

    def update_playlist(self):
        """Update the playlist display."""
        list_view = self.query_one("#playlist-list", ListView)
        list_view.clear()

        if not self.playlist.tracks:
            list_view.append(ListItem(Label("No tracks loaded")))
            return

        for i, track in enumerate(self.playlist.tracks):
            # Mark current track
            is_current = (i == self.playlist.current_index)
            marker = "▶ " if is_current else "  "

            # Format track info
            track_text = f"{marker}{i+1}. {track.artist} - {track.title}"
            if track.duration > 0:
                track_text += f" ({track.format_duration()})"

            label = Label(track_text)
            if is_current:
                label.styles.color = "cyan"
                label.styles.text_style = "bold"

            list_view.append(ListItem(label))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle track selection from the list."""
        if not self.playlist.tracks:
            return

        # Get the selected index
        selected_index = event.list_view.index

        # Check if it's a valid track (not the "No tracks loaded" message)
        if selected_index is not None and 0 <= selected_index < len(self.playlist.tracks):
            track = self.playlist.tracks[selected_index]
            # Update playlist current index
            self.playlist.set_current_index(selected_index)
            # Post message to parent screen
            self.post_message(self.TrackSelected(selected_index, track))
