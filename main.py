import os
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
from yt_dlp import YoutubeDL
import pygame

RECORD_FILE = "downloaded.txt"

def record_audio(filename ="output.wav", duration = 5, fs = 16000):
    print("Recording audio...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, audio)
    print("Audio recorded.")
    return audio

def transcribe_audio(filename = "output.wav", model = "medium.en"):
    model = whisper.load_model(model)
    text = model.transcribe(filename)
    return text

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
        second_video_url = entries[1]['webpage_url']

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

def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def __main__():
    audio = record_audio()
    result = transcribe_audio()
    text = result['text'].strip()
    text = text.lower()
    print("Text transcribed:", text)
    if(text.__contains__("jarvis")):
        print("Good Evening, Mr. Jha")

        if(text.__contains__("play")):
            videoParam = text.split("play")[1].strip()
            if(videoParam[-1] == "?" or videoParam[-1] == "!") or videoParam[-1] == ".":
                videoParam = videoParam[:-1]
            print("Playing video", videoParam)
            if has_been_downloaded(videoParam):
                print("Video already downloaded")
            else:
                download_video(videoParam)
                add_to_record(videoParam)

            cwd = os.getcwd()
            path = os.path.join(cwd, "downloads", videoParam + ".mp3")
            play_audio(path)

            



if __name__ == "__main__":
    __main__()