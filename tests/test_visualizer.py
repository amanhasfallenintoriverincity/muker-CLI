"""Tests for AudioVisualizer."""

import pytest
import numpy as np
from muker.core.visualizer import AudioVisualizer, VisualizerStyle


@pytest.fixture
def visualizer():
    """Create a visualizer instance."""
    return AudioVisualizer(sample_rate=44100, fft_size=2048)


def test_visualizer_creation(visualizer):
    """Test visualizer initialization."""
    assert visualizer.sample_rate == 44100
    assert visualizer.fft_size == 2048
    assert visualizer.current_style == VisualizerStyle.SPECTRUM


def test_process_audio_empty(visualizer):
    """Test processing empty audio data."""
    empty_data = np.array([])
    visualizer.process_audio(empty_data)
    # Should not crash


def test_process_audio_mono(visualizer):
    """Test processing mono audio data."""
    # Generate a simple sine wave
    duration = 0.1  # seconds
    samples = int(visualizer.sample_rate * duration)
    frequency = 440  # A4 note
    t = np.linspace(0, duration, samples)
    audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)

    visualizer.process_audio(audio_data)

    # Check that data was processed
    spectrum = visualizer.get_spectrum()
    assert len(spectrum) == 32
    assert np.all(spectrum >= 0)
    assert np.all(spectrum <= 1)


def test_get_spectrum(visualizer):
    """Test getting spectrum data."""
    # Process some audio first
    audio_data = np.random.randn(4096).astype(np.float32) * 0.5
    visualizer.process_audio(audio_data)

    spectrum = visualizer.get_spectrum(bins=32)
    assert len(spectrum) == 32
    assert spectrum.dtype == np.float32


def test_get_waveform(visualizer):
    """Test getting waveform data."""
    audio_data = np.random.randn(4096).astype(np.float32) * 0.5
    visualizer.process_audio(audio_data)

    waveform = visualizer.get_waveform(samples=100)
    assert len(waveform) == 100
    assert np.all(waveform >= -1.0)
    assert np.all(waveform <= 1.0)


def test_get_vu_meter(visualizer):
    """Test getting VU meter levels."""
    audio_data = np.random.randn(4096).astype(np.float32) * 0.5
    visualizer.process_audio(audio_data)

    left, right = visualizer.get_vu_meter()
    assert 0 <= left <= 1.0
    assert 0 <= right <= 1.0


def test_cycle_style(visualizer):
    """Test cycling through visualizer styles."""
    assert visualizer.get_style() == VisualizerStyle.SPECTRUM

    visualizer.cycle_style()
    assert visualizer.get_style() == VisualizerStyle.WAVEFORM

    visualizer.cycle_style()
    assert visualizer.get_style() == VisualizerStyle.VU_METER

    visualizer.cycle_style()
    assert visualizer.get_style() == VisualizerStyle.BARS

    visualizer.cycle_style()
    assert visualizer.get_style() == VisualizerStyle.SPECTRUM  # Should wrap


def test_set_style(visualizer):
    """Test setting specific style."""
    visualizer.set_style(VisualizerStyle.WAVEFORM)
    assert visualizer.get_style() == VisualizerStyle.WAVEFORM


def test_reset(visualizer):
    """Test resetting visualizer."""
    # Process some audio
    audio_data = np.random.randn(4096).astype(np.float32) * 0.5
    visualizer.process_audio(audio_data)

    # Reset
    visualizer.reset()

    # Check that buffers are zeroed
    assert np.all(visualizer.spectrum_data == 0)
    assert np.all(visualizer.waveform_data == 0)
    assert visualizer.vu_left == 0.0
    assert visualizer.vu_right == 0.0
