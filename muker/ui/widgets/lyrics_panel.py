"Lyrics panel widget for displaying synchronized lyrics."

from textual.widget import Widget
from textual.widgets import Label
from textual.containers import VerticalScroll
from textual import work
from typing import Optional, List, Dict, Any, Callable
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

    def __init__(self, text: str, timestamp: float, annotations: Optional[List[Dict[str, Any]]] = None, on_click_callback: Optional[Callable] = None):
        super().__init__(text)
        self.text_content = text
        self.timestamp = timestamp
        self.annotations = annotations or []
        self.on_click_callback = on_click_callback
        if self.annotations:
            self.add_class("has-annotation")

    def on_click(self) -> None:
        """Handle click event."""
        if self.annotations and self.on_click_callback:
            # Display only the first annotation found
            self.on_click_callback(self.text_content, self.annotations[0])

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
                
                # Initialize with empty annotations list and callback
                line_widget = LyricLine(
                    text, 
                    time, 
                    annotations=[],
                    on_click_callback=self.on_annotation_click
                )
                self.lines.append(line_widget)
                await scroll.mount(line_widget)
            
            print(f"[DEBUG] Lyrics loaded. Synced: {self.is_synced}, Lines: {len(self.lines)}")
                
        except Exception as e:
            print(f"[ERROR] Failed to load lyrics: {e}")

    @work(exclusive=True)
    async def _fetch_annotations(self, track):
        """Fetch annotations and update lines."""
        if not self.genius_service.is_available():
            return

        await self.genius_service.enrich_track_with_annotations(track)
        
        if track.annotations:
            # Map annotations to lines safely on main thread
            self._apply_annotations(track.annotations)

        # Update theme colors if available
        if track.primary_color and track.secondary_color:
            if hasattr(self.app, 'update_theme_colors'):
                self.app.update_theme_colors(track.primary_color, track.secondary_color)

    def _apply_annotations(self, annotations: List[Dict[str, Any]]):
        """Apply annotations to lyric lines (Main Thread)."""
        import re
        import unicodedata
        from difflib import SequenceMatcher

        def clean_text(text: str) -> str:
            # 1. Normalize Unicode
            text = unicodedata.normalize('NFKC', text)
            # 2. Remove non-alphanumeric characters (punctuation), keep whitespace
            text = re.sub(r'[^\w\s]', '', text)
            # 3. Collapse all whitespace to single space
            text = re.sub(r'\s+', ' ', text)
            return text.strip().lower()

        for line_widget in self.lines:
            # Normalize line text
            line_clean = clean_text(line_widget.text_content)
            if not line_clean:
                continue
            
            matched = False
            
            for ann in annotations:
                raw_fragment = ann['fragment']
                sub_fragments = raw_fragment.split('\n')
                
                # IMPORTANT: Also check the FULL fragment as a single block.
                if len(sub_fragments) > 1:
                    sub_fragments.append(raw_fragment)
                
                for sub in sub_fragments:
                    sub_clean = clean_text(sub)
                    
                    if not sub_clean or len(sub_clean) < 2:
                        continue
                    
                    # 1. Bidirectional Substring Match
                    if sub_clean in line_clean or line_clean in sub_clean:
                        matched = True
                    
                    # 2. Fuzzy Similarity Match
                    elif SequenceMatcher(None, line_clean, sub_clean).ratio() > 0.55:
                        matched = True
                            
                    # 3. Word Subset Match
                    else:
                        line_tokens = line_clean.split()
                        sub_tokens = set(sub_clean.split())
                        
                        if len(line_tokens) >= 2:
                            match_count = sum(1 for t in line_tokens if t in sub_tokens)
                            subset_ratio = match_count / len(line_tokens)
                            
                            if subset_ratio >= 0.55:
                                matched = True

                    if matched:
                        # Store the full annotation dictionary
                        line_widget.annotations.append(ann)
                        break 
                
                if matched:
                    break
            
            if matched:
                line_widget.add_class("has-annotation")

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
        
        # Update classes
        for i, line in enumerate(self.lines):
            if i == active_idx:
                if not line.has_class("active"):
                    line.add_class("active")
                    line.refresh() # Force refresh
                    # Scroll to keep in view
                    try:
                        line.scroll_visible(animate=True, top=False, duration=0.5)
                    except Exception as e:
                        print(f"[ERROR] Scroll failed: {e}")
            else:
                if line.has_class("active"):
                    line.remove_class("active")
                    line.refresh() # Force refresh

    def on_annotation_click(self, title: str, annotation: Dict[str, Any]):
        """Handle annotation click."""
        # Show loading state initially or existing translation
        initial_text = annotation.get('translation', 'Loading translation...')
        if not annotation.get('translation'):
             # Fallback to raw text if we want to show something while loading? 
             # Or just "Loading..."
             pass
             
        popup = AnnotationPopup(title, initial_text)
        self.app.push_screen(popup)
        
        if not annotation.get('translation'):
            self._translate_and_show(popup, annotation)

    @work(exclusive=False)
    async def _translate_and_show(self, popup: AnnotationPopup, annotation: Dict[str, Any]):
        """Fetch translation and update popup."""
        current_track = self.playlist.get_current_track()
        if not current_track:
            return
            
        translated_text = await self.genius_service.translate_single_annotation(current_track, annotation)
        
        # Update popup UI directly since we are in the async event loop
        popup.update_content(translated_text)
