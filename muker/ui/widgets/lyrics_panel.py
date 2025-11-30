"""Lyrics panel widget for displaying synchronized lyrics."""

from textual.widget import Widget
from textual.widgets import Label
from textual.containers import VerticalScroll
from textual import work
from typing import Optional, List, Dict, Any
from muker.core.player import AudioPlayer
from muker.core.playlist import PlaylistManager
from muker.services.genius_service import GeniusService
from muker.ui.screens.annotation_popup import AnnotationPopup

class LyricLine(Label):
    """A single line of lyrics."""
    
    DEFAULT_CSS = """
    LyricLine {
        width: 100%;
        padding: 0 1;
        color: $text-muted;
    }
    LyricLine.active {
        color: #ffffff;
        text-style: bold;
        background: $success;
    }
    LyricLine.has-annotation {
        text-style: underline;
        color: $accent;
    }
    LyricLine.has-annotation:hover {
        background: $surface-lighten-1;
    }
    """

    def __init__(self, text: str, timestamp: float, annotation: Optional[str] = None):
        super().__init__(text)
        self.text_content = text
        self.timestamp = timestamp
        self.annotation = annotation
        if annotation:
            self.add_class("has-annotation")

    def on_click(self) -> None:
        """Handle click event."""
        if self.annotation:
            self.app.push_screen(AnnotationPopup(self.text_content, self.annotation))

class LyricsPanel(Widget):
    """Widget for displaying synchronized lyrics."""

    DEFAULT_CSS = """
    LyricsPanel {
        height: 100%;
        border: solid $primary;
        background: $surface;
    }
    #lyrics-scroll {
        height: 100%;
    }
    .info-msg {
        text_align: center;
        padding: 2;
        color: $text-muted;
    }
    """

    def __init__(self, player: AudioPlayer, playlist: PlaylistManager):
        """Initialize lyrics panel."""
        super().__init__()
        self.player = player
        self.playlist = playlist
        self.genius_service = GeniusService()
        self.current_track_path: Optional[str] = None
        self.lines: List[LyricLine] = []
        self.is_synced = False

    def compose(self):
        yield VerticalScroll(id="lyrics-scroll")

    def on_mount(self):
        """Called when widget is mounted."""
        self.set_interval(0.1, self.update_lyrics_display)

    async def update_lyrics_display(self):
        """Update lyrics display based on current track and position."""
        current_track = self.playlist.get_current_track()
        
        if not current_track:
            if self.current_track_path is not None:
                self._clear_lyrics("No track playing")
            return

        # Check if track changed
        if current_track.file_path != self.current_track_path:
            self.current_track_path = current_track.file_path
            await self._load_lyrics(current_track)
            # Trigger annotation fetch in background
            self._fetch_annotations(current_track)
        
        # Check if lyrics arrived late (track is same, but lyrics appear and we have no lines)
        elif current_track.lyrics and not self.lines:
             await self._load_lyrics(current_track)
             self._fetch_annotations(current_track)

        # Update active line
        if self.is_synced and self.lines:
            self._update_active_line()

    def _clear_lyrics(self, message: str):
        """Clear lyrics display."""
        try:
            scroll = self.query_one("#lyrics-scroll", VerticalScroll)
            scroll.remove_children()
            scroll.mount(Label(message, classes="info-msg"))
            self.lines = []
            self.current_track_path = None
        except Exception:
            pass

    async def _load_lyrics(self, track):
        """Load lyrics for the track."""
        try:
            scroll = self.query_one("#lyrics-scroll", VerticalScroll)
            await scroll.remove_children()
            self.lines = []

            if not track.lyrics or 'lines' not in track.lyrics:
                 scroll.mount(Label("No lyrics available", classes="info-msg"))
                 self.is_synced = False
                 return

            self.is_synced = track.lyrics.get('syncType') == "LINE_SYNCED"
            print(f"[DEBUG] Lyrics loaded. Synced: {self.is_synced}, Lines: {len(self.lines)}")
            
            # Helper to parse time
            def parse_time(tag):
                try:
                    parts = tag.split(':')
                    if len(parts) == 2:
                        return int(parts[0]) * 60 + float(parts[1])
                    return 0.0
                except:
                    return 0.0

            for line_data in track.lyrics['lines']:
                text = line_data.get('words', '')
                if not text.strip():
                    continue
                    
                time = parse_time(line_data.get('timeTag', '00:00'))
                
                line_widget = LyricLine(text, time)
                self.lines.append(line_widget)
                await scroll.mount(line_widget)
                
        except Exception as e:
            print(f"[ERROR] Failed to load lyrics: {e}")

    @work(exclusive=True)
    async def _fetch_annotations(self, track):
        """Fetch annotations and update lines."""
        if not self.genius_service.is_available():
            return

        await self.genius_service.enrich_track_with_annotations(track)
        
        if track.annotations:
            # Map annotations to lines
            # Simple matching: if fragment is in line text
            # Doing this on the main thread via call_from_thread or similar is safest for UI updates
            # But @work runs in a worker, so we need to be careful updating UI.
            # Textual widgets are not thread safe, but @work allows calling app methods.
            # Actually, better to schedule the update on the main loop.
            
            self._apply_annotations(track.annotations)

    def _apply_annotations(self, annotations: List[Dict[str, Any]]):
        """Apply annotations to lyric lines (Main Thread)."""
        for line_widget in self.lines:
            line_text = line_widget.text_content.lower()
            for ann in annotations:
                fragment = ann['fragment'].lower()
                # Basic matching logic
                if fragment in line_text and len(fragment) > 3:
                    line_widget.annotation = ann['text']
                    line_widget.add_class("has-annotation")
                    # Break to avoid overwriting with multiple annotations (simple v1)
                    break

    def _update_active_line(self):
        """Highlight the current line."""
        position = self.player.get_position()
        active_idx = -1
        
        # Find active line (the one with largest timestamp <= position)
        for i, line in enumerate(self.lines):
            if line.timestamp <= position:
                active_idx = i
            else:
                break
        
        # Debug position vs first few lines
        # print(f"[DEBUG] Pos: {position:.2f}, ActiveIdx: {active_idx}")
        
        # Update classes
        for i, line in enumerate(self.lines):
            if i == active_idx:
                if not line.has_class("active"):
                    line.add_class("active")
                    line.refresh() # Force refresh
                    print(f"[DEBUG] Set active line {i}: {line.classes}")
                    # Scroll to keep in view
                    try:
                        line.scroll_visible(animate=True, top=False, duration=0.5)
                    except Exception as e:
                        print(f"[ERROR] Scroll failed: {e}")
            else:
                if line.has_class("active"):
                    line.remove_class("active")
                    line.refresh() # Force refresh