
import os
from yt_dlp import YoutubeDL

RECORD_FILE = "downloaded.txt"


def download_video(query):
    output_path = "downloads/" + query
    search_opts = {
        'quiet': True,
        'skip_download': True,
    }
    ydl_opts = {
        'format':'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with YoutubeDL() as ydl:
        results = ydl.extract_info(f"ytsearch5:{query}", download=False)
        entries = results['entries']
        if len(entries) < 2:
            raise Exception("Less than 2 results found.")
        second_video_url = entries[0]['webpage_url']

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.download([second_video_url])

def has_been_downloaded(video_id):
    if not os.path.exists(RECORD_FILE):
        return False
    with open(RECORD_FILE, "r") as f:
        return video_id.strip() in {line.strip() for line in f}

def add_to_record(video_id):
    with open(RECORD_FILE, "a") as f:
        f.write(video_id + "\n")

