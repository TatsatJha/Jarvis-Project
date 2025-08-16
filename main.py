import os
from listen import record_audio, transcribe_audio
from download import download_video, has_been_downloaded, add_to_record
from speaker import play
import threading
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import socket

HOST = "127.0.0.1"
PORT = 65432


device = "cpu"
model = ChatterboxTTS.from_pretrained(device=device)
audio_prompt_path = "sound/jarvis.wav"


def say(text):
    wav = model.generate(
        text,
        audio_prompt_path=audio_prompt_path
    )
    ta.save("output.wav", wav, model.sr)
    return "output.wav"


def play_audio(filename):
    threading.Thread(target=play, args=(filename,), daemon=True).start()


def handle_play(text):
    videoParam = text.split("play")[1].strip()
    if (videoParam[-1] == "?" or videoParam[-1] == "!") or videoParam[-1] == ".":
        videoParam = videoParam[:-1]
    print("Playing video", videoParam)
    if has_been_downloaded(videoParam):
        print("Video already downloaded")
    else:
        download_video(videoParam)
        add_to_record(videoParam)

    cwd = os.getcwd()
    path = os.path.join(cwd, "downloads", videoParam + ".mp3")
    file = say("Playing " + videoParam)
    play_audio(file)
    play_audio(path)


def handle_bootup():
    play("downloads/bootup.mp3")
    play("downloads/good-evening.wav")


def run_voice_command():
    # tts = TTS("sound/jarvis.wav")
    print("We have a command")
    record_audio(duration=5)
    result = transcribe_audio()
    text = result['text'].strip()
    text = text.lower()
    print("Text transcribed:", text)
    if (text.__contains__("play")):
        handle_play(text)
    elif (text.__contains__("wake up")):
        handle_bootup()
    elif (text.__contains__("introduce")):
        play_audio("downloads/introduce.wav")
    else:
        print("some banter")


def __main__():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Serer is lisetning on {HOST}:{PORT}".format(
            HOST=HOST, PORT=PORT))

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode("utf-8").strip()
                if data == "wake":
                    print("Hot key detected, starting voice command")
                    # run voice command
                    run_voice_command()


if __name__ == "__main__":
    __main__()
