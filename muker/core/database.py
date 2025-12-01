"""Database manager for caching metadata and lyrics."""

import sqlite3
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

class DatabaseManager:
    """Manages SQLite database for caching."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection.

        Args:
            db_path: Path to database file
        """
        if db_path is None:
            self.db_path = Path(__file__).parent.parent.parent / 'data' / 'cache.db'
        else:
            self.db_path = db_path
            
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Genius cache table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS genius_cache (
                        query_key TEXT PRIMARY KEY,
                        genius_id INTEGER,
                        primary_color TEXT,
                        secondary_color TEXT,
                        annotations_json TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Spotify lyrics cache table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS spotify_lyrics_cache (
                        spotify_id TEXT PRIMARY KEY,
                        lyrics_json TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] Database initialization failed: {e}")

    def _get_query_key(self, artist: str, title: str) -> str:
        """Generate normalized query key."""
        return f"{artist.lower().strip()}|{title.lower().strip()}"

    def get_genius_data(self, artist: str, title: str) -> Optional[Dict[str, Any]]:
        """Get cached Genius data.

        Returns:
            Dict with annotations and colors, or None if not found
        """
        key = self._get_query_key(artist, title)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT genius_id, primary_color, secondary_color, annotations_json FROM genius_cache WHERE query_key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        'genius_id': row[0],
                        'primary_color': row[1],
                        'secondary_color': row[2],
                        'annotations': json.loads(row[3]) if row[3] else []
                    }
        except Exception as e:
            print(f"[ERROR] Failed to get genius data from cache: {e}")
        return None

    def save_genius_data(self, artist: str, title: str, genius_id: int, 
                        annotations: list, primary_color: str, secondary_color: str):
        """Save Genius data to cache."""
        key = self._get_query_key(artist, title)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO genius_cache 
                    (query_key, genius_id, primary_color, secondary_color, annotations_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (key, genius_id, primary_color, secondary_color, json.dumps(annotations))
                )
                conn.commit()
        except Exception as e:
            print(f"[ERROR] Failed to save genius data to cache: {e}")

    def get_spotify_lyrics(self, spotify_id: str) -> Optional[Dict[str, Any]]:
        """Get cached Spotify lyrics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT lyrics_json FROM spotify_lyrics_cache WHERE spotify_id = ?",
                    (spotify_id,)
                )
                row = cursor.fetchone()
                
                if row and row[0]:
                    return json.loads(row[0])
        except Exception as e:
            print(f"[ERROR] Failed to get lyrics from cache: {e}")
        return None

    def save_spotify_lyrics(self, spotify_id: str, lyrics: dict):
        """Save Spotify lyrics to cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO spotify_lyrics_cache 
                    (spotify_id, lyrics_json)
                    VALUES (?, ?)
                    """,
                    (spotify_id, json.dumps(lyrics))
                )
                conn.commit()
        except Exception as e:
            print(f"[ERROR] Failed to save lyrics to cache: {e}")
