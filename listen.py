import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import numpy as np
import queue
import time
import tempfile
import os
import threading
from scipy.io.wavfile import write

model = whisper.load_model("tiny.en")
medium_model = whisper.load_model("medium.en")
wake_word = "okay"

SAMPLERATE = 16000
CHUNK_DURATION = 2.0  # seconds
OVERLAP = 1.9  # seconds
CHANNELS = 1

q = queue.Queue()
stop_event = threading.Event()

def record_chunks():
    """Continuously record audio chunks and send them to the queue."""
    chunk_samples = int(CHUNK_DURATION * SAMPLERATE)
    overlap_samples = int(OVERLAP * SAMPLERATE)
    buffer = np.zeros((chunk_samples,), dtype=np.float32)

    def callback(indata, frames, time_info, status):
        nonlocal buffer
        buffer[:-overlap_samples] = buffer[overlap_samples:]
        buffer[-overlap_samples:] = indata[:, 0] 
        q.put_nowait(buffer.copy())

    with sd.InputStream(
        samplerate=SAMPLERATE,
        channels=CHANNELS,
        callback=callback,
        dtype="float32",
        blocksize=overlap_samples
    ):
        print("🎤 Listening...")
        while not stop_event.is_set():
            time.sleep(0.1)

def transcribe_chunks():
    """Transcribe audio from the queue using Whisper."""
    while True:
        audio = q.get()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            write(tmpfile.name, SAMPLERATE, audio)
            result = model.transcribe(tmpfile.name, fp16=False)
            print(result["text"])
            os.remove(tmpfile.name)
            if(result["text"].lower().__contains__(wake_word.lower())):
                return result["text"]
            
def stop_listening():
    stop_event.set()

def record_audio(filename ="output.wav", duration = 5, fs = 16000):
    print("Recording audio...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, audio)
    print("Audio recorded.")
    return audio

def transcribe_audio(filename = "output.wav"):
    text = medium_model.transcribe(filename, fp16=False)
    return text
