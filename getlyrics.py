import os
import lyricsgenius
from dotenv import load_dotenv

#Load environment variables
load_dotenv()

#Genius API Token
GENIUS_TOKEN = os.getenv("GENIUS_API_TOKEN")

#Initialize Genius API
genius = lyricsgenius.Genius(GENIUS_TOKEN)

def get_song_lyrics(song_name):
    try:
        song_details = {}
        song = genius.search_song(song_name)
        if song:
            song_details['artist']=song.artist
            song_details['title']=song.title
            song_details['lyrics']=song.lyrics
        
            return song_details

        else:
            print("No lyrics found for this song.")
    except Exception as e:
        print(f"Error: {e}")


'''
#Example
song_input = input("Enter the song name: ")
a = get_song_lyrics(song_input)
print(a['lyrics'])

'''
