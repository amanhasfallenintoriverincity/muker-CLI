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
- 🎼 **Detailed Track Information**: Display comprehensive metadata including bitrate, sample rate, channels
- 🌐 **Spotify Integration** (Optional): Automatically enrich local metadata with Spotify Web API

## Requirements

- Python 3.10 or higher
- Windows/Linux/macOS

## Installation

### Basic Installation

Install core dependencies:

```bash
pip install -r requirements.txt
```

### Optional: Spotify Integration

To enable metadata enrichment from Spotify Web API:

1. Install optional dependencies (spotipy, python-dotenv):
```bash
pip install spotipy python-dotenv
```

2. Follow the detailed setup guide in [SPOTIFY_SETUP.md](SPOTIFY_SETUP.md)

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
├── core/          # Business logic (player, playlist, visualizer, library)
├── ui/            # Textual UI components and widgets
├── models/        # Data models (Track, etc.)
├── services/      # External API integrations (Spotify)
└── utils/         # Utility functions (file scanner, etc.)
```

## Track Information Display

Muker displays comprehensive track information including:

**Line 1: Main Info**
- Artist and track title

**Line 2: Album Info**
- Track number, album name, release year, genre

**Line 3: Technical Info**
- Audio format (MP3, FLAC, etc.)
- Bitrate (e.g., 320kbps)
- Sample rate (e.g., 44.1kHz)
- Channels (Mono/Stereo)

## Spotify Metadata Enrichment

When enabled, Muker automatically:
- Searches Spotify for tracks with incomplete metadata
- Fills in missing album, year, genre, and track number information
- Uses accurate artist names from Spotify
- Falls back to local metadata if Spotify is unavailable

See [SPOTIFY_SETUP.md](SPOTIFY_SETUP.md) for setup instructions.

## License

MIT License

## Author

AMAN
