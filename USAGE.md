# Muker CLI - Usage Guide

## Getting Started

### First Launch

When you first launch Muker:

```bash
python -m muker
```

You'll see the main interface with three panels:
1. **Visualizer** (top) - Real-time audio visualization
2. **Library & Playlist** (middle) - File browser and track list
3. **Player Controls** (bottom) - Playback controls and track info

### Loading Music

Press `o` to open a folder. By default, it will scan your Music folder for supported audio files (MP3, WAV, FLAC, OGG).

The application will:
- Recursively scan the directory
- Extract metadata (artist, album, track info)
- Add all found tracks to the playlist
- Start playing the first track automatically

## Features

### Playback Control

- **Play/Pause**: Press `Space`
- **Next Track**: Press `n`
- **Previous Track**: Press `p`
- **Volume Control**: Press `+` or `-` (or arrow keys `↑`/`↓`)

### Playlist Modes

**Shuffle Mode** (Press `s`):
- ON: Plays tracks in random order
- OFF: Plays tracks in sequential order

**Repeat Mode** (Press `r` to cycle):
- OFF: Stops after last track
- ALL: Repeats entire playlist
- ONE: Repeats current track

### Visualizer Styles

Press `v` to cycle through different visualizer styles:

1. **Spectrum** - Frequency spectrum bars (default)
   - Low frequencies on the left (blue)
   - Mid frequencies in the center (green)
   - High frequencies on the right (red)

2. **Waveform** - Time-domain waveform
   - Shows the actual audio signal
   - Good for seeing rhythm and dynamics

3. **VU Meter** - Volume unit meters
   - Shows left and right channel levels
   - Classic analog-style meters

4. **Bars** - Simplified spectrum bars
   - Cleaner, less detailed view
   - Better for smaller terminals

## Tips & Tricks

### Performance

- The visualizer updates at 30 FPS for smooth animation
- If you experience lag, try reducing your terminal window size
- The app uses minimal CPU when music is paused

### Playlist Management

- Tracks are automatically sorted by artist, album, and track number
- The current track is marked with ▶ in the playlist
- Playlist shows track number, artist, title, and duration

### Saving Your Session

The application automatically saves:
- Last used volume level
- Visualizer style preference

These settings are restored when you restart the app.

## Interface Layout

```
┌────────────────────────────────────┐
│  Muker - CLI Music Player          │  ← Header
├────────────────────────────────────┤
│  VISUALIZER                        │  ← 30% height
│  ████ ██ ███ █ ████ ██            │     Real-time audio viz
├──────────────┬─────────────────────┤
│ Library      │ Playlist            │  ← 50% height
│ (40% width)  │ (60% width)         │     Library & tracks
│              │ ▶ 1. Track.mp3      │
├──────────────┴─────────────────────┤
│ Player Controls                    │  ← 20% height
│ ⏮ ▶ ⏭  │██████─────│ 🔊████       │     Controls & info
│ Artist - Title                     │
│ 02:15 / 04:30                      │
├────────────────────────────────────┤
│  [Shortcuts: Space=Play q=Quit]    │  ← Footer
└────────────────────────────────────┘
```

## Advanced Usage

### Custom Music Folder

By default, the app scans your `~/Music` folder. To use a different folder:
1. Press `o` to trigger folder scan
2. Currently uses default Music folder
3. (In future versions, will support custom folder selection)

### Playlist Files

The app can save and load playlists as JSON files (feature for future enhancement).

## Troubleshooting

### No Sound

- Check system volume
- Verify audio files are in supported format
- Ensure no other app has exclusive audio access

### Visualizer Not Moving

- Make sure audio is actually playing
- Check if PCM data is being captured
- Try changing visualizer style with `v`

### Can't Find Music Files

- Verify files are in supported formats (.mp3, .wav, .flac, .ogg)
- Check that the folder contains audio files
- Try with a different folder

## System Requirements

- Python 3.10+
- Terminal with Unicode support
- Audio output device
- Supported OS: Windows, Linux, macOS

## Getting Help

- Press `q` to quit the application
- Check [README.md](README.md) for general information
- See [INSTALL.md](INSTALL.md) for installation help

Happy listening! 🎶
