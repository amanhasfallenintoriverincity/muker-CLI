"""Custom progress bar widget for seeking."""

from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text


class ProgressBar(Widget):
    """Interactive progress bar for track seeking."""

    progress: reactive[float] = reactive(0.0)
    duration: reactive[float] = reactive(0.0)

    def __init__(self):
        """Initialize progress bar."""
        super().__init__()

    def render(self) -> Text:
        """Render the progress bar.

        Returns:
            Rich Text with progress bar
        """
        width = self.size.width
        if width == 0:
            return Text("")

        # Calculate filled and empty sections
        filled_width = int(self.progress * width)
        empty_width = width - filled_width

        # Create bar
        bar = "█" * filled_width + "─" * empty_width

        # Format time
        current_time = int(self.progress * self.duration)
        total_time = int(self.duration)

        time_str = f" {current_time // 60:02d}:{current_time % 60:02d} / {total_time // 60:02d}:{total_time % 60:02d}"

        result = Text(bar + time_str)
        return result

    def set_progress(self, position: float, duration: float):
        """Update progress.

        Args:
            position: Current position in seconds
            duration: Total duration in seconds
        """
        self.duration = duration
        if duration > 0:
            self.progress = position / duration
        else:
            self.progress = 0.0
