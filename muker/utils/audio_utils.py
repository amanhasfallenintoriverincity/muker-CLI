"""Audio utility functions."""

import numpy as np
from typing import Tuple


def normalize_pcm_data(pcm_data: np.ndarray) -> np.ndarray:
    """Normalize PCM data to range [-1.0, 1.0].

    Args:
        pcm_data: Raw PCM data

    Returns:
        Normalized PCM data
    """
    if pcm_data.size == 0:
        return pcm_data

    max_val = np.abs(pcm_data).max()
    if max_val > 0:
        return pcm_data / max_val
    return pcm_data


def stereo_to_mono(pcm_data: np.ndarray) -> np.ndarray:
    """Convert stereo PCM data to mono by averaging channels.

    Args:
        pcm_data: Stereo PCM data with shape (samples, 2)

    Returns:
        Mono PCM data with shape (samples,)
    """
    if pcm_data.ndim == 1:
        return pcm_data

    if pcm_data.ndim == 2 and pcm_data.shape[1] == 2:
        return np.mean(pcm_data, axis=1)

    return pcm_data


def calculate_rms(pcm_data: np.ndarray) -> float:
    """Calculate RMS (Root Mean Square) of PCM data.

    Args:
        pcm_data: PCM data array

    Returns:
        RMS value
    """
    if pcm_data.size == 0:
        return 0.0

    return float(np.sqrt(np.mean(np.square(pcm_data))))


def db_to_linear(db: float) -> float:
    """Convert decibels to linear scale.

    Args:
        db: Decibel value

    Returns:
        Linear scale value
    """
    return 10.0 ** (db / 20.0)


def linear_to_db(linear: float) -> float:
    """Convert linear scale to decibels.

    Args:
        linear: Linear scale value

    Returns:
        Decibel value
    """
    if linear <= 0:
        return -float('inf')
    return 20.0 * np.log10(linear)


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
