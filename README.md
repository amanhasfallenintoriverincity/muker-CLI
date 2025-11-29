# Muker CLI - Terminal Music Player

A feature-rich command-line interface music player with real-time audio visualizer.

## Features

- 🎵 **Multi-format Support**: Play MP3, WAV, FLAC, OGG files
- 🎨 **Real-time Visualizer**: Multiple visualization styles (spectrum, waveform, VU meter)
- 📝 **Playlist Management**: Create, save, and load playlists
- 🎛️ **Full Playback Control**: Play, pause, seek, volume control
- 🔀 **Shuffle & Repeat**: Multiple playback modes
- 🖥️ **Rich TUI**: Modern terminal user interface powered by Textual
- ⚡ **High Performance**: Optimized for smooth 30-60 FPS visualizer updates

## Requirements

- Python 3.10 or higher
- Windows/Linux/macOS

## Installation

### Using pip

```bash
pip install -r requirements.txt
```

### Using Poetry

```bash
poetry install
```

## Usage

```bash
python -m muker
```

Or if installed via Poetry:

```bash
poetry run muker
```

## Keyboard Shortcuts

- `Space` - Play/Pause
- `n` - Next track
- `p` - Previous track
- `+` / `-` - Volume up/down
- `s` - Toggle shuffle
- `r` - Toggle repeat mode
- `v` - Cycle through visualizer styles
- `q` - Quit

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black muker/
```

### Type Checking

```bash
mypy muker/
```

## Architecture

```
muker/
├── core/          # Business logic (player, playlist, visualizer)
├── ui/            # Textual UI components
├── models/        # Data models
└── utils/         # Utility functions
```

## License

MIT License

## Author

AMAN
