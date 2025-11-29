"""Visualizer widget for displaying audio visualization."""

from textual.widget import Widget
from textual.strip import Strip
from textual.geometry import Size
from textual import events
from rich.text import Text
from rich.segment import Segment

from muker.core.visualizer import AudioVisualizer, VisualizerStyle
import numpy as np


class VisualizerWidget(Widget):
    """Widget that displays real-time audio visualization."""

    def __init__(self, visualizer: AudioVisualizer):
        """Initialize visualizer widget.

        Args:
            visualizer: AudioVisualizer instance
        """
        super().__init__()
        self.visualizer = visualizer
        self.refresh_rate = 30  # FPS

    def on_mount(self):
        """Called when widget is mounted."""
        # Update at 30 FPS
        self.set_interval(1/30, self.refresh)

    def render(self) -> Text:
        """Render the visualizer.

        Returns:
            Rich Text with visualization
        """
        style = self.visualizer.get_style()

        if style == VisualizerStyle.SPECTRUM:
            return self._render_spectrum()
        elif style == VisualizerStyle.WAVEFORM:
            return self._render_waveform()
        elif style == VisualizerStyle.VU_METER:
            return self._render_vu_meter()
        elif style == VisualizerStyle.BARS:
            return self._render_bars()
        else:
            return self._render_spectrum()

    def _render_spectrum(self) -> Text:
        """Render frequency spectrum visualization."""
        width = self.size.width
        height = self.size.height

        if width == 0 or height == 0:
            return Text("Visualizer", justify="center", style="bold cyan")

        # Get spectrum data
        spectrum = self.visualizer.get_spectrum(min(width, 64))

        # If no audio data, show placeholder
        if np.all(spectrum == 0):
            result = Text()
            result.append("\n" * (height // 2 - 1))
            result.append("♫ Audio Visualizer ♫", style="bold cyan", justify="center")
            result.append("\n")
            result.append(f"Style: {self.visualizer.get_style().value}", style="dim cyan", justify="center")
            result.append("\n")
            result.append("Press 'v' to change style", style="dim", justify="center")
            return result

        lines = []
        bar_chars = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

        # Create bars for each frequency bin
        for row in range(height):
            line_parts = []
            for i, value in enumerate(spectrum):
                # Calculate bar height for this position
                bar_height = int(value * height)

                # Determine which character to use
                if (height - row - 1) < bar_height:
                    char = '█'
                    # Color based on frequency (low=blue, mid=green, high=red)
                    if i < len(spectrum) // 3:
                        color = "cyan"
                    elif i < 2 * len(spectrum) // 3:
                        color = "green"
                    else:
                        color = "red"
                else:
                    char = ' '
                    color = "white"

                line_parts.append((char, color))

            line_text = Text()
            for char, color in line_parts:
                line_text.append(char, style=color)

            lines.append(line_text)

        # Combine lines
        result = Text()
        for i, line in enumerate(lines):
            result.append(line)
            if i < len(lines) - 1:
                result.append("\n")

        # Add style name in corner
        style_name = f" [{self.visualizer.get_style().value}] "
        result.stylize("bold cyan", len(str(result)) - len(style_name), len(str(result)))

        return result

    def _render_waveform(self) -> Text:
        """Render waveform visualization."""
        width = self.size.width
        height = self.size.height

        if width == 0 or height == 0:
            return Text("")

        # Get waveform data
        waveform = self.visualizer.get_waveform(width)

        lines = []
        mid_point = height // 2

        for row in range(height):
            line = ""
            for i, value in enumerate(waveform):
                # Map value (-1 to 1) to row position
                wave_row = mid_point - int(value * mid_point)

                if row == wave_row:
                    line += "█"
                elif row == mid_point:
                    line += "─"
                else:
                    line += " "

            lines.append(line)

        result = Text("\n".join(lines), style="bright_green")
        return result

    def _render_vu_meter(self) -> Text:
        """Render VU meter visualization."""
        width = self.size.width
        height = self.size.height

        if width == 0 or height == 0:
            return Text("")

        left, right = self.visualizer.get_vu_meter()

        lines = []

        # Calculate bar widths
        bar_width = min(width - 10, 50)  # Leave space for labels
        left_bar_len = int(left * bar_width)
        right_bar_len = int(right * bar_width)

        # Add some spacing at top
        for _ in range(height // 3):
            lines.append("")

        # Left channel
        left_bar = "█" * left_bar_len + "─" * (bar_width - left_bar_len)
        lines.append(f"L: {left_bar} {int(left * 100):3d}%")

        lines.append("")

        # Right channel
        right_bar = "█" * right_bar_len + "─" * (bar_width - right_bar_len)
        lines.append(f"R: {right_bar} {int(right * 100):3d}%")

        result = Text("\n".join(lines), style="yellow")
        return result

    def _render_bars(self) -> Text:
        """Render simplified bar visualization."""
        width = self.size.width
        height = self.size.height

        if width == 0 or height == 0:
            return Text("")

        # Get bar data (fewer bins for cleaner look)
        bars = self.visualizer.get_bars(min(width // 2, 32))

        lines = []

        for row in range(height):
            line = ""
            for value in bars:
                bar_height = int(value * height)
                if (height - row - 1) < bar_height:
                    line += "██"
                else:
                    line += "  "

            lines.append(line)

        result = Text("\n".join(lines), style="magenta")
        return result
