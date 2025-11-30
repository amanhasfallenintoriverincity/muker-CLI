"""Audio player core module using pygame.mixer."""

import asyncio
import threading
from typing import Optional, Callable
from pathlib import Path
import numpy as np
import miniaudio
import pygame.mixer
import time

from muker.models.track import Track


class AudioPlayer:
    """Audio playback engine using pygame.mixer."""

    def __init__(self, buffer_size: int = 4096):
        """Initialize audio player.

        Args:
            buffer_size: Size of PCM data buffer
        """
        self.buffer_size = buffer_size
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

        # Playback thread control
        self.playback_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Callbacks
        self.on_track_end: Optional[Callable] = None
        self.on_error: Optional[Callable[[str], None]] = None

        # Initialize pygame.mixer
        print("[DEBUG] Initializing pygame.mixer...")
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.mixer.music.set_volume(self.volume)
        print(f"[DEBUG] pygame.mixer initialized - volume: {self.volume * 100:.0f}%")

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
            self.current_stream = miniaudio.decode_file(str(track.file_path))
            self.current_track = track
            self.duration = track.duration

            if self.duration == 0 and self.current_stream:
                # Calculate duration from samples if not in metadata
                self.duration = len(self.current_stream.samples) / self.current_stream.sample_rate

            self.current_position = 0.0
            self.is_paused = False
            print(f"[DEBUG] Track loaded successfully. Duration: {self.duration:.2f}s")
            print(f"[DEBUG] Stream info - channels: {self.current_stream.nchannels}, sample_rate: {self.current_stream.sample_rate}")

        except Exception as e:
            error_msg = f"Failed to load track {track.file_path}: {e}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            if self.on_error:
                self.on_error(error_msg)
            raise

    async def play(self):
        """Start or resume playback."""
        if not self.current_track:
            print("[DEBUG] Cannot play: No track loaded")
            return

        if self.is_paused:
            # Resume playback with pygame
            print("[DEBUG] Resuming playback")
            pygame.mixer.music.unpause()
            self.is_paused = False
            return

        if self.is_playing:
            print("[DEBUG] Already playing")
            return

        print(f"[DEBUG] Starting playback of {self.current_track.title}")

        # Stop any existing playback thread
        self.stop_event.set()
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)

        self.stop_event.clear()
        self.is_playing = True
        self.is_paused = False

        # Start playback in a separate thread
        def play_thread():
            try:
                print("[DEBUG] Playback thread started")

                # Load and play with pygame.mixer (simple and stable!)
                print(f"[DEBUG] Loading file with pygame.mixer: {self.current_track.file_path}")
                pygame.mixer.music.load(str(self.current_track.file_path))
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                print(f"[DEBUG] pygame.mixer playback started - volume: {self.volume * 100:.0f}%")

                # Get samples for visualizer (using miniaudio)
                if self.current_stream:
                    samples = np.array(self.current_stream.samples, dtype=np.float32)
                    if self.current_stream.nchannels == 2:
                        samples = samples.reshape(-1, 2)
                    print(f"[DEBUG] Visualizer samples ready - shape: {samples.shape}")
                else:
                    samples = None

                # Monitor playback and update visualizer
                start_time = time.time()

                while self.is_playing and not self.stop_event.is_set():
                    # Check if pygame is still playing
                    if not pygame.mixer.music.get_busy() and not self.is_paused:
                        print("[DEBUG] Track finished (pygame reports not busy)")
                        self.is_playing = False

                        # Call track end callback
                        if self.on_track_end:
                            try:
                                loop = asyncio.get_event_loop()
                                asyncio.run_coroutine_threadsafe(self._call_track_end(), loop)
                            except:
                                pass
                        break

                    # Update position
                    if not self.is_paused:
                        # Get position from pygame (in milliseconds)
                        pos_ms = pygame.mixer.music.get_pos()
                        if pos_ms >= 0:
                            self.current_position = pos_ms / 1000.0
                        else:
                            # Fallback to time-based
                            elapsed = time.time() - start_time
                            self.current_position = min(elapsed, self.duration)

                        # Update visualizer buffer
                        if samples is not None:
                            sample_pos = int(self.current_position * self.current_stream.sample_rate)
                            if sample_pos < len(samples):
                                end_pos = min(sample_pos + self.buffer_size, len(samples))
                                chunk = samples[sample_pos:end_pos]

                                with self.pcm_lock:
                                    if chunk.ndim == 2:
                                        mono = np.mean(chunk, axis=1)
                                    else:
                                        mono = chunk

                                    chunk_len = min(len(mono), self.buffer_size)
                                    self.pcm_buffer[:chunk_len] = mono[:chunk_len]
                                    if chunk_len < self.buffer_size:
                                        self.pcm_buffer[chunk_len:] = 0

                    time.sleep(0.03)  # Update ~30 FPS

                print("[DEBUG] Playback completed!")

            except Exception as e:
                print(f"[ERROR] Playback error: {e}")
                import traceback
                traceback.print_exc()
                self.is_playing = False
                if self.on_error:
                    self.on_error(f"Playback error: {e}")

        # Run in a separate thread
        self.playback_thread = threading.Thread(target=play_thread, daemon=True)
        self.playback_thread.start()
        print("[DEBUG] Playback thread launched")

    async def _call_track_end(self):
        """Wrapper to call track end callback."""
        if self.on_track_end:
            await self.on_track_end()

    async def pause(self):
        """Pause playback."""
        if self.is_playing and not self.is_paused:
            print("[DEBUG] Pausing playback")
            pygame.mixer.music.pause()
            self.is_paused = True

    async def stop(self):
        """Stop playback."""
        print("[DEBUG] Stopping playback")
        pygame.mixer.music.stop()
        self.stop_event.set()
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0.0

        # Wait for playback thread to finish
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)

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
        # Apply volume immediately with pygame
        pygame.mixer.music.set_volume(self.volume)
        print(f"[DEBUG] Volume changed to {self.volume * 100:.0f}%")

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
        print("[DEBUG] Cleaning up player resources")
        await self.stop()
