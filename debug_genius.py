import os
from lyricsgenius import Genius

token = os.getenv("GENIUS_ACCESS_TOKEN")
if not token:
    print("GENIUS_ACCESS_TOKEN not set.")
    exit()

genius = Genius(token, verbose=False)
song = genius.search_song("Imagine", "John Lennon")

if song:
    print(f"Type of song: {type(song)}")
    print(f"Dir of song: {dir(song)}")
    try:
        print(f"Song ID: {song.id}")
    except AttributeError:
        print("Song has no 'id' attribute")
        # Try to see if it's in a dictionary under _body or similar if it's that kind of object
        if hasattr(song, '_body'):
             print(f"Body keys: {song._body.keys()}")
else:
    print("Song not found")
