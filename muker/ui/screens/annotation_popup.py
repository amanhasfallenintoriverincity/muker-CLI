"""Annotation popup screen."""

from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Container, Vertical, VerticalScroll
from textual.app import ComposeResult

class AnnotationPopup(ModalScreen):
    """Popup screen for displaying annotations."""

    CSS = """
    AnnotationPopup {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #popup-container {
        width: 60%;
        height: 60%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #annotation-title {
        text-align: center;
        text-style: bold;
        border-bottom: solid $primary;
        margin-bottom: 1;
        padding-bottom: 1;
    }

    #annotation-scroll {
        height: 1fr;
    }
    
    #annotation-text {
        width: 100%;
    }

    #close-btn {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(self, title: str, content: str):
        """Initialize popup.

        Args:
            title: Title (lyric fragment)
            content: Annotation text
        """
        super().__init__()
        self.annotation_title = title
        self.annotation_content = content

    def compose(self) -> ComposeResult:
        with Container(id="popup-container"):
            yield Static(self.annotation_title, id="annotation-title")
            with VerticalScroll(id="annotation-scroll"):
                yield Static(self.annotation_content, id="annotation-text")
            yield Button("Close", variant="primary", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def update_content(self, new_content: str) -> None:
        """Update the annotation content dynamically."""
        self.annotation_content = new_content
        try:
            self.query_one("#annotation-text", Static).update(new_content)
        except Exception:
            pass
