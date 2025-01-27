#this module using get you tube URL
from pytube import Search

import yt_dlp
import re

def get_youtube_url(video_title):
    search = Search(video_title)
    if search.results:
        video_url = search.results[0].watch_url
        return video_url
    else:
        return "No video found."

'''
# Example usage
video_title = "perfect"
print(get_youtube_url(video_title))'''


def get_clean_song_name(youtube_url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            title = info_dict.get('title', 'Title not found')

            # Remove common tags like "Official Video," "Lyrics," "HD," etc.
            clean_title = re.sub(r'(\(.*?\)|\[.*?\])', '', title)  # Remove text inside () and []
            clean_title = re.sub(r'(?i)(official|video|lyrics|hd|4k|audio|remix|music|full album|clip)', '', clean_title)
            clean_title = re.sub(r'[-|_]', ' ', clean_title)  # Replace - and _ with spaces
            clean_title = ' '.join(clean_title.split()).strip()  # Remove extra spaces

            return clean_title
    except Exception as e:
        return f"Error: {e}"


'''
# Example usage
youtube_link = input("Enter YouTube link: ")
song_name = get_clean_song_name(youtube_link)
print(f"Song Name: {song_name}")'''


