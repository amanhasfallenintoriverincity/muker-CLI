"""Audio visualizer module with FFT analysis."""

import numpy as np
from enum import Enum
from typing import Tuple
from muker.utils.audio_utils import stereo_to_mono, calculate_rms


class VisualizerStyle(Enum):
    """Visualizer style enumeration."""
    SPECTRUM = "spectrum"      # Frequency spectrum bars
    WAVEFORM = "waveform"      # Time-domain waveform
    VU_METER = "vu_meter"      # VU meter levels
    BARS = "bars"              # Simplified spectrum bars


class AudioVisualizer:
    """Real-time audio analysis and visualization data generator."""

    def __init__(self, sample_rate: int = 44100, fft_size: int = 2048):
        """Initialize audio visualizer.

        Args:
            sample_rate: Audio sample rate in Hz
            fft_size: FFT window size (power of 2)
        """
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.current_style = VisualizerStyle.SPECTRUM

        # Pre-compute Hanning window for FFT
        self.window = np.hanning(fft_size)

        # Data buffers
        self.spectrum_data = np.zeros(32, dtype=np.float32)
        self.waveform_data = np.zeros(100, dtype=np.float32)
        self.vu_left = 0.0
        self.vu_right = 0.0

        # Smoothing factor for VU meter (0-1, higher = smoother)
        self.vu_smoothing = 0.8

    def process_audio(self, pcm_data: np.ndarray):
        """Process audio data and update visualization buffers.

        Args:
            pcm_data: PCM audio data (mono or stereo)
        """
        if pcm_data.size == 0:
            return

        # Convert to mono if stereo
        mono_data = stereo_to_mono(pcm_data)

        # Update spectrum data (FFT)
        self._update_spectrum(mono_data)

        # Update waveform data
        self._update_waveform(mono_data)

        # Update VU meter
        self._update_vu_meter(pcm_data)

    def _update_spectrum(self, pcm_data: np.ndarray):
        """Update frequency spectrum data using FFT.

        Args:
            pcm_data: Mono PCM data
        """
        # Ensure we have enough data
        if len(pcm_data) < self.fft_size:
            # Pad with zeros
            pcm_data = np.pad(pcm_data, (0, self.fft_size - len(pcm_data)))
        else:
            # Take last fft_size samples
            pcm_data = pcm_data[-self.fft_size:]

        # Apply window function to reduce spectral leakage
        windowed = pcm_data * self.window

        # Compute FFT (real FFT for real-valued input)
        fft_result = np.fft.rfft(windowed)
        magnitude = np.abs(fft_result)

        # Normalize magnitude directly (simpler and more visual)
        # Scale by FFT size to get proper magnitude
        magnitude = magnitude / (self.fft_size / 2)

        # Apply logarithmic scaling for better visualization
        # Add small epsilon to avoid log(0)
        epsilon = 1e-6
        log_magnitude = np.log10(magnitude + epsilon)

        # Normalize to 0-1 range with better dynamic range
        # Use percentile-based normalization for adaptive range
        max_val = np.percentile(log_magnitude, 95)  # Use 95th percentile as max (less aggressive)
        min_val = np.percentile(log_magnitude, 5)   # Use 5th percentile as min

        # Avoid division by zero
        if max_val - min_val < epsilon:
            normalized = np.zeros_like(log_magnitude)
        else:
            normalized = (log_magnitude - min_val) / (max_val - min_val)

        # Clip to 0-1
        normalized = np.clip(normalized, 0.0, 1.0)

        # Apply stronger gamma correction to prevent bars from being too tall
        normalized = np.power(normalized, 0.5)  # Stronger gamma correction (0.5 instead of 0.7)

        # Scale down overall height to 60% max to prevent fullness
        normalized = normalized * 0.6

        # Resample to desired number of bins using logarithmic scale
        self.spectrum_data = self._resample_spectrum(normalized, 32)

    def _resample_spectrum(self, spectrum: np.ndarray, bins: int) -> np.ndarray:
        """Resample spectrum to desired number of bins using log scale.

        Args:
            spectrum: Full spectrum data
            bins: Number of output bins

        Returns:
            Resampled spectrum
        """
        spectrum_len = len(spectrum)

        if spectrum_len <= bins:
            # If spectrum is smaller, just pad
            return np.pad(spectrum, (0, bins - spectrum_len))

        # Create logarithmic indices
        # Map bins logarithmically across frequency range
        indices = np.logspace(
            0,
            np.log10(spectrum_len),
            bins,
            dtype=int
        )

        # Clip indices to valid range
        indices = np.clip(indices, 0, spectrum_len - 1)

        # Sample spectrum at these indices
        resampled = spectrum[indices]

        return resampled.astype(np.float32)

    def _update_waveform(self, pcm_data: np.ndarray):
        """Update waveform data.

        Args:
            pcm_data: Mono PCM data
        """
        target_samples = 100

        if len(pcm_data) < target_samples:
            # Pad if too short
            self.waveform_data = np.pad(pcm_data, (0, target_samples - len(pcm_data)))
        else:
            # Downsample by taking evenly spaced samples
            indices = np.linspace(0, len(pcm_data) - 1, target_samples, dtype=int)
            self.waveform_data = pcm_data[indices]

        # Normalize to -1 to 1
        max_val = np.abs(self.waveform_data).max()
        if max_val > 0:
            self.waveform_data = self.waveform_data / max_val

    def _update_vu_meter(self, pcm_data: np.ndarray):
        """Update VU meter levels.

        Args:
            pcm_data: PCM data (mono or stereo)
        """
        if pcm_data.ndim == 2 and pcm_data.shape[1] == 2:
            # Stereo
            left_rms = calculate_rms(pcm_data[:, 0])
            right_rms = calculate_rms(pcm_data[:, 1])
        else:
            # Mono
            left_rms = calculate_rms(pcm_data)
            right_rms = left_rms

        # Apply smoothing (exponential moving average)
        self.vu_left = (self.vu_smoothing * self.vu_left +
                        (1 - self.vu_smoothing) * left_rms)
        self.vu_right = (self.vu_smoothing * self.vu_right +
                         (1 - self.vu_smoothing) * right_rms)

        # Clip to 0-1 range
        self.vu_left = np.clip(self.vu_left, 0.0, 1.0)
        self.vu_right = np.clip(self.vu_right, 0.0, 1.0)

    def get_spectrum(self, bins: int = 32) -> np.ndarray:
        """Get frequency spectrum data.

        Args:
            bins: Number of frequency bins

        Returns:
            Spectrum array (0-1 range)
        """
        if bins == len(self.spectrum_data):
            return self.spectrum_data.copy()

        # Resample if different number of bins requested
        return self._resample_spectrum(self.spectrum_data, bins)

    def get_waveform(self, samples: int = 100) -> np.ndarray:
        """Get waveform data.

        Args:
            samples: Number of waveform samples

        Returns:
            Waveform array (-1 to 1 range)
        """
        if samples == len(self.waveform_data):
            return self.waveform_data.copy()

        # Resample if different number of samples requested
        if samples < len(self.waveform_data):
            indices = np.linspace(0, len(self.waveform_data) - 1, samples, dtype=int)
            return self.waveform_data[indices]
        else:
            return np.pad(self.waveform_data, (0, samples - len(self.waveform_data)))

    def get_vu_meter(self) -> Tuple[float, float]:
        """Get VU meter levels for left and right channels.

        Returns:
            Tuple of (left_level, right_level) in 0-1 range
        """
        return (float(self.vu_left), float(self.vu_right))

    def get_bars(self, count: int = 16) -> np.ndarray:
        """Get simplified bar visualization data.

        Args:
            count: Number of bars

        Returns:
            Bar heights array (0-1 range)
        """
        # Use spectrum data but with fewer bins
        return self.get_spectrum(count)

    def set_style(self, style: VisualizerStyle):
        """Set visualization style.

        Args:
            style: Visualizer style to use
        """
        self.current_style = style

    def get_style(self) -> VisualizerStyle:
        """Get current visualization style.

        Returns:
            Current visualizer style
        """
        return self.current_style

    def cycle_style(self) -> VisualizerStyle:
        """Cycle to next visualization style.

        Returns:
            New visualizer style
        """
        styles = list(VisualizerStyle)
        current_index = styles.index(self.current_style)
        next_index = (current_index + 1) % len(styles)
        self.current_style = styles[next_index]
        return self.current_style

    def get_visualization_data(self) -> np.ndarray:
        """Get visualization data for current style.

        Returns:
            Visualization data array
        """
        if self.current_style == VisualizerStyle.SPECTRUM:
            return self.get_spectrum()
        elif self.current_style == VisualizerStyle.WAVEFORM:
            return self.get_waveform()
        elif self.current_style == VisualizerStyle.VU_METER:
            left, right = self.get_vu_meter()
            return np.array([left, right])
        elif self.current_style == VisualizerStyle.BARS:
            return self.get_bars()
        else:
            return self.get_spectrum()

    def reset(self):
        """Reset all visualization buffers to zero."""
        self.spectrum_data.fill(0)
        self.waveform_data.fill(0)
        self.vu_left = 0.0
        self.vu_right = 0.0
