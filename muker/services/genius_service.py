"""Genius API service for fetching annotations."""

import os
import asyncio
from typing import Optional, List, Dict, Any
from muker.models.track import Track

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from lyricsgenius import Genius
    GENIUS_AVAILABLE = True
except ImportError:
    GENIUS_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class GeniusService:
    """Service for interacting with Genius API and translating annotations."""

    def __init__(self):
        """Initialize Genius service."""
        self.token = os.getenv("GENIUS_ACCESS_TOKEN")
        self.genius = None
        self._initialize_client()
        
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        self._initialize_gemini_client()

    def _initialize_client(self):
        """Initialize Genius client if token is available."""
        if GENIUS_AVAILABLE and self.token:
            try:
                self.genius = Genius(self.token, verbose=False, remove_section_headers=True)
                print("[INFO] Genius API client initialized successfully")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Genius client: {e}")
                self.genius = None
        else:
            if not GENIUS_AVAILABLE:
                print("[INFO] lyricsgenius package not installed. Install with: pip install lyricsgenius")
            elif not self.token:
                print("[INFO] Genius access token not found. Set GENIUS_ACCESS_TOKEN to enable annotations.")

    def _initialize_gemini_client(self):
        """Initialize Gemini client if API key is available."""
        if GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                print("[INFO] Gemini API client initialized successfully")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Gemini client: {e}")
                self.gemini_client = None
        elif not GEMINI_AVAILABLE:
             print("[INFO] google-genai package not installed. Install with: pip install google-genai")
        elif not self.gemini_api_key:
             print("[INFO] Gemini API key not found. Set GEMINI_API_KEY to enable translation.")

    def is_available(self) -> bool:
        """Check if Genius API is available."""
        return self.genius is not None

    def search_song(self, title: str, artist: str) -> Optional[Any]:
        """Search for a song on Genius.

        Args:
            title: Song title
            artist: Artist name

        Returns:
            Song object if found, None otherwise
        """
        if not self.is_available():
            return None
        try:
            return self.genius.search_song(title, artist)
        except Exception as e:
            print(f"[ERROR] Genius search failed: {e}")
            return None

    def get_annotations(self, song_id: int) -> List[Dict[str, Any]]:
        """Get annotations for a song.

        Args:
            song_id: Genius song ID

        Returns:
            List of annotation dictionaries containing fragment and body text
        """
        if not self.is_available():
            return []
        
        try:
            # lyricsgenius song_annotations returns list of (fragment, [annotations])
            # We'll convert this to a friendlier list of dicts
            raw_annotations = self.genius.song_annotations(song_id)
            processed_annotations = []
            
            for fragment, annotation_list in raw_annotations:
                # Flatten annotation list (usually contains lists of strings)
                text_content = []
                for ann in annotation_list:
                    if isinstance(ann, list):
                        text_content.extend(ann)
                    elif isinstance(ann, str):
                        text_content.append(ann)
                
                processed_annotations.append({
                    "fragment": fragment,
                    "text": "\n\n".join(text_content)
                })
                
            return processed_annotations
        except Exception as e:
            print(f"[ERROR] Failed to fetch annotations: {e}")
            return []

    async def _translate_text(self, text: str) -> str:
        """Translate text to Korean using Gemini."""
        if not self.gemini_client:
            return text
        
        try:
            response = await self.gemini_client.aio.models.generate_content(
                model='gemini-flash-lite-latest',
                contents=f"Translate the following music annotation to Korean naturally. Keep the tone informative and easy to understand. Output ONLY the translated text:\n\n{text}"
            )
            return response.text.strip()
        except Exception as e:
            print(f"[ERROR] Translation failed: {e}")
            return text

    async def enrich_track_with_annotations(self, track: Track):
        """Find song on Genius and fetch annotations in background.
        
        Args:
            track: Track to enrich
        """
        if not self.is_available() or track.annotations:
            return

        def _fetch_sync():
            # Clean title/artist for better search results
            clean_title = track.title.split('(')[0].split('-')[0].strip()
            clean_artist = track.artist.split(',')[0].strip()
            
            print(f"[DEBUG] Searching Genius for: {clean_title} by {clean_artist}")
            song = self.search_song(clean_title, clean_artist)
            
            if song:
                # Debug song object
                # print(f"[DEBUG] Song object type: {type(song)}")
                # Try to get ID safely
                song_id = None
                if hasattr(song, 'id'):
                    song_id = song.id
                elif hasattr(song, '_body') and 'id' in song._body:
                    song_id = song._body['id']
                
                if song_id:
                    track.genius_song_id = song_id
                    print(f"[INFO] Found Genius song ID: {song_id}")
                    return self.get_annotations(song_id)
                else:
                    print(f"[ERROR] Could not determine song ID from Genius result.")
            else:
                print(f"[INFO] No Genius match for {track.title}")
            return None

        # 1. Fetch annotations (Sync)
        annotations = await asyncio.to_thread(_fetch_sync)
        
        if annotations:
            # 2. Translate if available (Async)
            if self.gemini_client:
                 print(f"[INFO] Translating {len(annotations)} annotations...")
                 # Process concurrently
                 tasks = [self._translate_text(ann['text']) for ann in annotations]
                 translated_texts = await asyncio.gather(*tasks)
                 
                 for i, trans_text in enumerate(translated_texts):
                     annotations[i]['text'] = trans_text
            
            track.annotations = annotations
            print(f"[INFO] Fetched {len(annotations)} annotations for {track.title}")