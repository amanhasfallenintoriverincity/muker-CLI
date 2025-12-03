"""Genius API service for fetching annotations."""

import os
import asyncio
from typing import Optional, List, Dict, Any
from muker.models.track import Track
from muker.core.database import DatabaseManager

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
        
        self.db = DatabaseManager()

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
            # Use referents endpoint directly to control pagination limit (default is often 10)
            # Fetch up to 50 annotations (Genius usually caps popular songs around here per request)
            response = self.genius.referents(song_id=song_id, per_page=50)
            
            processed_annotations = []
            
            # 'response' is usually a dict with 'referents' list if successful
            # handle both direct list return or dict wrapper depending on library version
            referents_list = response.get('referents', []) if isinstance(response, dict) else response

            for referent in referents_list:
                fragment = referent.get('fragment', '')
                annotations = referent.get('annotations', [])
                
                if not fragment or not annotations:
                    continue
                
                # Usually there is one primary annotation per referent
                first_ann = annotations[0]
                body = first_ann.get('body', {})
                
                # 'plain' contains the raw text representation
                text_content = body.get('plain', '')
                
                if text_content:
                    processed_annotations.append({
                        "fragment": fragment,
                        "text": text_content
                    })
                
            return processed_annotations
        except Exception as e:
            print(f"[ERROR] Failed to fetch annotations: {e}")
            return []

    async def _translate_text(self, text: str, artist: str = "", title: str = "", fragment: str = "") -> str:
        """Translate text to Korean using Gemini with context."""
        if not self.gemini_client:
            return text
        
        prompt = (
            f"Song: {title} - {artist}\n"
            f"Lyrics: {fragment}\n"
            f"Annotation: {text}\n\n"
            f"Please translate this annotation into Korean. The annotation explains the meaning of the lyrics.\n"
            f"- Translate naturally and fluently.\n"
            f"- Consider the context of the song and lyrics.\n"
            f"- Only output the Korean translation."
        )

        try:
            response = await self.gemini_client.aio.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
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
        if track.annotations:
            return

        # Clean title/artist
        clean_title = track.title.split('(')[0].split('-')[0].strip()
        clean_artist = track.artist.split(',')[0].strip()

        # 1. Check Cache
        cached_data = await asyncio.to_thread(self.db.get_genius_data, clean_artist, clean_title)
        if cached_data:
            print(f"[INFO] Loaded annotations for '{track.title}' from cache")
            track.genius_song_id = cached_data['genius_id']
            track.annotations = cached_data['annotations']
            track.primary_color = cached_data['primary_color']
            track.secondary_color = cached_data['secondary_color']
            return

        if not self.is_available():
            return

        def _fetch_sync():
            print(f"[DEBUG] Searching Genius for: {clean_title} by {clean_artist}")
            song = self.search_song(clean_title, clean_artist)
            
            result = {
                'song_id': None,
                'annotations': None,
                'primary_color': None,
                'secondary_color': None
            }

            if song:
                # Try to get ID safely
                song_id = None
                if hasattr(song, 'id'):
                    song_id = song.id
                elif hasattr(song, '_body') and 'id' in song._body:
                    song_id = song._body['id']
                
                if song_id:
                    result['song_id'] = song_id
                    print(f"[INFO] Found Genius song ID: {song_id}")
                    
                    # Get annotations
                    result['annotations'] = self.get_annotations(song_id)

                    # Get colors
                    if hasattr(song, 'song_art_primary_color'):
                        result['primary_color'] = song.song_art_primary_color
                    elif hasattr(song, '_body'):
                        result['primary_color'] = song._body.get('song_art_primary_color')

                    if hasattr(song, 'song_art_secondary_color'):
                        result['secondary_color'] = song.song_art_secondary_color
                    elif hasattr(song, '_body'):
                        result['secondary_color'] = song._body.get('song_art_secondary_color')
                else:
                    print(f"[ERROR] Could not determine song ID from Genius result.")
            else:
                print(f"[INFO] No Genius match for {track.title}")
            return result

        # 2. Fetch data (Sync)
        data = await asyncio.to_thread(_fetch_sync)
        
        if data and data['song_id']:
            annotations = data['annotations']
            
            track.annotations = annotations
            print(f"[INFO] Fetched {len(annotations)} annotations for {track.title}")

            # Update colors
            if data['primary_color']:
                track.primary_color = data['primary_color']
            if data['secondary_color']:
                track.secondary_color = data['secondary_color']
            
            track.genius_song_id = data['song_id']

            # 4. Save to Cache
            await asyncio.to_thread(
                self.db.save_genius_data,
                clean_artist, 
                clean_title, 
                data['song_id'], 
                annotations or [], 
                data['primary_color'], 
                data['secondary_color']
            )

    async def translate_single_annotation(self, track: Track, annotation: Dict[str, Any]) -> str:
        """Translate a single annotation and update cache.
        
        Args:
            track: The track object containing the annotation
            annotation: The specific annotation dictionary to translate
            
        Returns:
            The translated text
        """
        # Return existing translation if available
        if 'translation' in annotation:
            return annotation['translation']

        original_text = annotation.get('text', '')
        fragment = annotation.get('fragment', '')
        if not original_text:
            return ""
            
        translated_text = await self._translate_text(original_text, track.artist, track.title, fragment)
        
        # Update in-memory object
        annotation['translation'] = translated_text
        
        # Update cache
        clean_title = track.title.split('(')[0].split('-')[0].strip()
        clean_artist = track.artist.split(',')[0].strip()
        
        await asyncio.to_thread(
            self.db.save_genius_data,
            clean_artist,
            clean_title,
            track.genius_song_id,
            track.annotations, # This list now contains the updated annotation dict
            track.primary_color,
            track.secondary_color
        )
        
        return translated_text
