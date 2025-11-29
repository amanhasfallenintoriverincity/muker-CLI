"""Tests for Track model."""

import pytest
from pathlib import Path
from muker.models.track import Track


def test_track_creation():
    """Test basic track creation."""
    track = Track(
        file_path="/path/to/song.mp3",
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        duration=180.5
    )

    assert track.file_path == "/path/to/song.mp3"
    assert track.title == "Test Song"
    assert track.artist == "Test Artist"
    assert track.album == "Test Album"
    assert track.duration == 180.5


def test_track_defaults():
    """Test track with default values."""
    track = Track(
        file_path="/path/to/song.mp3",
        title="Test Song"
    )

    assert track.artist == "Unknown Artist"
    assert track.album == "Unknown Album"
    assert track.duration == 0.0


def test_track_to_dict():
    """Test track serialization."""
    track = Track(
        file_path="/path/to/song.mp3",
        title="Test Song",
        artist="Test Artist",
        duration=120.0
    )

    data = track.to_dict()

    assert data['path'] == "/path/to/song.mp3"
    assert data['title'] == "Test Song"
    assert data['artist'] == "Test Artist"
    assert data['duration'] == 120.0


def test_track_from_dict():
    """Test track deserialization."""
    data = {
        'path': '/path/to/song.mp3',
        'title': 'Test Song',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'duration': 150.0
    }

    track = Track.from_dict(data)

    assert track.file_path == "/path/to/song.mp3"
    assert track.title == "Test Song"
    assert track.artist == "Test Artist"
    assert track.duration == 150.0


def test_track_format_duration():
    """Test duration formatting."""
    track = Track(
        file_path="/path/to/song.mp3",
        title="Test Song",
        duration=125.0  # 2:05
    )

    formatted = track.format_duration()
    assert formatted == "02:05"


def test_track_filename():
    """Test filename property."""
    track = Track(
        file_path="/path/to/my_song.mp3",
        title="Test Song"
    )

    assert track.filename == "my_song.mp3"


def test_track_extension():
    """Test extension property."""
    track = Track(
        file_path="/path/to/song.MP3",
        title="Test Song"
    )

    assert track.extension == ".mp3"
