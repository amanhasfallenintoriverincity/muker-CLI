# Muker CLI - Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip or Poetry package manager

## Installation Steps

### Method 1: Using pip

1. **Clone or download the repository**
   ```bash
   cd muker-CLI
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**

   Windows:
   ```bash
   .venv\Scripts\activate
   ```

   Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python -m muker
   ```

### Method 2: Using Poetry

1. **Install Poetry** (if not already installed)
   ```bash
   pip install poetry
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Run the application**
   ```bash
   poetry run muker
   ```

## Troubleshooting

### Windows Audio Issues

If you encounter audio device errors on Windows:
- Make sure no other application is using exclusive audio access
- Try restarting the application
- Check Windows audio settings

### Missing Audio Files

The player supports the following formats:
- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- OGG (.ogg)

Make sure your audio files are in one of these formats.

### Performance Issues

If the visualizer is slow or laggy:
- The visualizer runs at 30 FPS by default
- Close other resource-intensive applications
- Try reducing terminal window size

## Quick Start

1. Run the application: `python -m muker`
2. Press `o` to open a folder (default: your Music folder)
3. Use `Space` to play/pause
4. Use `n` and `p` for next/previous track
5. Use `+` and `-` to adjust volume
6. Press `v` to cycle through visualizer styles
7. Press `q` to quit

## Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `n` | Next track |
| `p` | Previous track |
| `+` / `↑` | Volume up |
| `-` / `↓` | Volume down |
| `s` | Toggle shuffle |
| `r` | Cycle repeat mode |
| `v` | Change visualizer style |
| `o` | Open folder |
| `q` | Quit |

Enjoy your music! 🎵
