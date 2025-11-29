"""Tests for PlaylistManager."""

import pytest
from muker.core.playlist import PlaylistManager
from muker.models.track import Track
from muker.models.playlist_model import RepeatMode


@pytest.fixture
def sample_tracks():
    """Create sample tracks for testing."""
    return [
        Track(file_path="/path/track1.mp3", title="Track 1", artist="Artist A", duration=120),
        Track(file_path="/path/track2.mp3", title="Track 2", artist="Artist B", duration=180),
        Track(file_path="/path/track3.mp3", title="Track 3", artist="Artist C", duration=200),
    ]


def test_playlist_creation():
    """Test creating an empty playlist."""
    playlist = PlaylistManager()
    assert len(playlist.tracks) == 0
    assert playlist.current_index == 0
    assert not playlist.shuffle_enabled
    assert playlist.repeat_mode == RepeatMode.OFF


def test_add_track(sample_tracks):
    """Test adding tracks to playlist."""
    playlist = PlaylistManager()

    playlist.add_track(sample_tracks[0])
    assert len(playlist.tracks) == 1

    playlist.add_tracks(sample_tracks[1:])
    assert len(playlist.tracks) == 3


def test_get_current_track(sample_tracks):
    """Test getting current track."""
    playlist = PlaylistManager()
    playlist.add_tracks(sample_tracks)

    current = playlist.get_current_track()
    assert current == sample_tracks[0]

    playlist.current_index = 1
    current = playlist.get_current_track()
    assert current == sample_tracks[1]


def test_next_track_sequential(sample_tracks):
    """Test sequential next track."""
    playlist = PlaylistManager()
    playlist.add_tracks(sample_tracks)

    next_track = playlist.next_track()
    assert next_track == sample_tracks[1]
    assert playlist.current_index == 1

    next_track = playlist.next_track()
    assert next_track == sample_tracks[2]


def test_next_track_with_repeat_all(sample_tracks):
    """Test next track with repeat all."""
    playlist = PlaylistManager()
    playlist.add_tracks(sample_tracks)
    playlist.repeat_mode = RepeatMode.ALL
    playlist.current_index = 2  # Last track

    next_track = playlist.next_track()
    assert next_track == sample_tracks[0]  # Should wrap to first
    assert playlist.current_index == 0


def test_next_track_with_repeat_one(sample_tracks):
    """Test next track with repeat one."""
    playlist = PlaylistManager()
    playlist.add_tracks(sample_tracks)
    playlist.repeat_mode = RepeatMode.ONE

    current = playlist.get_current_track()
    next_track = playlist.next_track()
    assert next_track == current  # Should stay on same track


def test_previous_track(sample_tracks):
    """Test previous track."""
    playlist = PlaylistManager()
    playlist.add_tracks(sample_tracks)
    playlist.current_index = 2

    prev_track = playlist.previous_track()
    assert prev_track == sample_tracks[1]
    assert playlist.current_index == 1


def test_shuffle_mode(sample_tracks):
    """Test shuffle mode."""
    playlist = PlaylistManager()
    playlist.add_tracks(sample_tracks)

    assert not playlist.shuffle_enabled

    playlist.toggle_shuffle()
    assert playlist.shuffle_enabled
    assert len(playlist.shuffle_indices) == 3

    playlist.toggle_shuffle()
    assert not playlist.shuffle_enabled


def test_repeat_mode_toggle():
    """Test repeat mode toggling."""
    playlist = PlaylistManager()

    assert playlist.repeat_mode == RepeatMode.OFF

    playlist.toggle_repeat()
    assert playlist.repeat_mode == RepeatMode.ALL

    playlist.toggle_repeat()
    assert playlist.repeat_mode == RepeatMode.ONE

    playlist.toggle_repeat()
    assert playlist.repeat_mode == RepeatMode.OFF


def test_remove_track(sample_tracks):
    """Test removing tracks."""
    playlist = PlaylistManager()
    playlist.add_tracks(sample_tracks)

    playlist.remove_track(1)
    assert len(playlist.tracks) == 2
    assert playlist.tracks[0].title == "Track 1"
    assert playlist.tracks[1].title == "Track 3"


def test_clear_playlist(sample_tracks):
    """Test clearing playlist."""
    playlist = PlaylistManager()
    playlist.add_tracks(sample_tracks)

    playlist.clear()
    assert len(playlist.tracks) == 0
    assert playlist.current_index == 0


def test_get_track_count(sample_tracks):
    """Test track count."""
    playlist = PlaylistManager()
    assert playlist.get_track_count() == 0

    playlist.add_tracks(sample_tracks)
    assert playlist.get_track_count() == 3
