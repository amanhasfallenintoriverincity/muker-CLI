"""Audio player core module using miniaudio."""

import asyncio
import threading
from typing import Optional, Callable
from pathlib import Path
import numpy as np
import miniaudio

from muker.models.track import Track


class AudioPlayer:
    """Audio playback engine using miniaudio."""

    def __init__(self, buffer_size: int = 4096):
        """Initialize audio player.

        Args:
            buffer_size: Size of PCM data buffer
        """
        self.buffer_size = buffer_size
        self.device: Optional[miniaudio.PlaybackDevice] = None
        self.current_stream: Optional[miniaudio.DecodedSoundFile] = None
        self.current_track: Optional[Track] = None

        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7

        # Thread-safe PCM buffer for visualizer
        self.pcm_buffer = np.zeros(buffer_size, dtype=np.float32)
        self.pcm_lock = threading.Lock()

        # Playback state
        self.current_position = 0.0
        self.duration = 0.0

        # Callbacks
        self.on_track_end: Optional[Callable] = None
        self.on_error: Optional[Callable[[str], None]] = None

        # Initialize playback device
        self._init_device()

    def _init_device(self):
        """Initialize miniaudio playback device."""
        try:
            self.device = miniaudio.PlaybackDevice()
        except Exception as e:
            if self.on_error:
                self.on_error(f"Failed to initialize audio device: {e}")

    async def load_track(self, track: Track):
        """Load a track for playback.

        Args:
            track: Track object to load
        """
        # Stop current playback
        if self.is_playing:
            await self.stop()

        try:
            print(f"[DEBUG] Loading track: {track.file_path}")
            # Decode the audio file
            self.current_stream = miniaudio.decode_file(track.file_path)
            self.current_track = track
            self.duration = track.duration

            if self.duration == 0 and self.current_stream:
                # Calculate duration from samples if not in metadata
                self.duration = len(self.current_stream.samples) / self.current_stream.sample_rate

            self.current_position = 0.0
            self.is_paused = False
            print(f"[DEBUG] Track loaded successfully. Duration: {self.duration:.2f}s")

        except Exception as e:
            error_msg = f"Failed to load track {track.file_path}: {e}"
            print(f"[ERROR] {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
            raise

    async def play(self):
        """Start or resume playback."""
        if not self.current_stream or not self.device:
            print("[DEBUG] Cannot play: No stream or device")
            return

        if self.is_paused:
            # Resume playback
            print("[DEBUG] Resuming playback")
            self.is_paused = False
            self.is_playing = True
            return

        print(f"[DEBUG] Starting playback of {self.current_track.title if self.current_track else 'Unknown'}")
        self.is_playing = True
        self.is_paused = False

        # Start playback in a separate thread
        def play_thread():
            try:
                print("[DEBUG] Playback thread started")
                # Apply volume to samples
                samples = self.current_stream.samples.copy()
                samples = (samples * self.volume).astype(np.float32)

                # Convert to the format miniaudio expects
                sound = miniaudio.DecodedSoundFile(
                    name=self.current_stream.name,
                    nchannels=self.current_stream.nchannels,
                    sample_rate=self.current_stream.sample_rate,
                    sample_format=miniaudio.SampleFormat.FLOAT32,
                    samples=samples
                )

                # Create a generator for samples with PCM capture
                def sample_generator():
                    frame_size = self.buffer_size
                    num_samples = len(sound.samples)
                    position = 0

                    while position < num_samples and self.is_playing and not self.is_paused:
                        end_pos = min(position + frame_size, num_samples)
                        chunk = sound.samples[position:end_pos]

                        # Update PCM buffer for visualizer
                        with self.pcm_lock:
                            # Convert stereo to mono for visualizer
                            if chunk.ndim == 2:
                                mono_chunk = np.mean(chunk, axis=1)
                            else:
                                mono_chunk = chunk

                            # Store in PCM buffer
                            chunk_len = min(len(mono_chunk), self.buffer_size)
                            self.pcm_buffer[:chunk_len] = mono_chunk[:chunk_len]
                            if chunk_len < self.buffer_size:
                                self.pcm_buffer[chunk_len:] = 0

                        # Update position
                        self.current_position = position / sound.sample_rate

                        yield chunk

                        position = end_pos

                    # Track ended
                    if position >= num_samples:
                        self.is_playing = False
                        if self.on_track_end:
                            asyncio.run_coroutine_threadsafe(
                                self._call_track_end(),
                                asyncio.get_event_loop()
                            )

                # Stream the audio
                self.device.start(sample_generator())

            except Exception as e:
                self.is_playing = False
                if self.on_error:
                    self.on_error(f"Playback error: {e}")

        # Run in a separate thread
        playback_thread = threading.Thread(target=play_thread, daemon=True)
        playback_thread.start()

    async def _call_track_end(self):
        """Wrapper to call track end callback."""
        if self.on_track_end:
            await self.on_track_end()

    async def pause(self):
        """Pause playback."""
        self.is_paused = True

    async def stop(self):
        """Stop playback."""
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0.0

        if self.device:
            self.device.close()
            self._init_device()

    async def seek(self, position: float):
        """Seek to a specific position in the track.

        Args:
            position: Position in seconds
        """
        if not self.current_stream:
            return

        # For now, seeking requires reloading the track
        # This is a limitation we'll improve later
        position = max(0, min(position, self.duration))
        self.current_position = position

        # TODO: Implement proper seeking by sample position

    def set_volume(self, volume: float):
        """Set playback volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))

    def get_volume(self) -> float:
        """Get current volume level.

        Returns:
            Current volume (0.0 to 1.0)
        """
        return self.volume

    def get_pcm_data(self) -> np.ndarray:
        """Get current PCM data for visualizer.

        Returns:
            PCM data array
        """
        with self.pcm_lock:
            return self.pcm_buffer.copy()

    def get_position(self) -> float:
        """Get current playback position in seconds.

        Returns:
            Current position in seconds
        """
        return self.current_position

    def get_duration(self) -> float:
        """Get total duration of current track.

        Returns:
            Duration in seconds
        """
        return self.duration

    def get_progress(self) -> float:
        """Get playback progress as a percentage.

        Returns:
            Progress from 0.0 to 1.0
        """
        if self.duration > 0:
            return self.current_position / self.duration
        return 0.0

    async def cleanup(self):
        """Clean up resources."""
        await self.stop()
        if self.device:
            self.device.close()
