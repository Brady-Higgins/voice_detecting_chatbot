import whisper
import pyaudio
import wave
import numpy as np
import os
from TTS.api import TTS
import time
import tkinter as tk
import audioop
import collections
import webrtcvad

def record_audio_until_silence(filename: str="output.wav", silence_threshold: int = 12000, chunk_size: int = 1024, sample_rate: int = 44100, channels: int = 1, silence_duration: int = 2, color_box: tk.Label = None, root: tk.Tk= None, audio_index: int = 1):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, f'..\Audio\{filename}')

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    input_device_index= audio_index,
                    frames_per_buffer=chunk_size)

    frames = []
    silent_chunks = 0
    max_silent_chunks = int(silence_duration * sample_rate / chunk_size)
    print("recording!")
    color_box.config(bg="green")
    root.update_idletasks()
    
    while True:
        data = stream.read(chunk_size)
        frames.append(data)
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.linalg.norm(audio_data)
        if volume < silence_threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0
        
        if silent_chunks > max_silent_chunks:
            print("Silence detected. Stopping recording.")
            break
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(audio_path , 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def speech_to_text(audio_filename: str="output.wav") -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, f'..\Audio\{audio_filename}')


    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']
def text_to_speech(audio_filename: str="output.wav",text: str=""):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, f'..\Audio\{audio_filename}')
    tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    tts.tts_to_file(text=text, file_path=audio_path,speaker="p256",speed=.85)

def play_audio(audio_filename: str ="output.wav",rate: int = 21500):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, f'..\Audio\{audio_filename}')
    wf = wave.open(audio_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=rate,
        output=True
    )
    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

def save_audio(audio_data, output_filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, f'..\Audio\{output_filename}')
    with wave.open(audio_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(audio_data)

def vad_collector(stream,silence_threshold):
        
        vad = webrtcvad.Vad(0)
        ring_buffer = collections.deque(maxlen=10)
        voiced_frames = []
        triggered = False
        silence_chunks = 0

        while True:
            chunk = stream.read(480)
            ring_buffer.append(chunk)
            is_speech = vad.is_speech(chunk, 16000)

            # Check if the chunk's amplitude is above the threshold
            amplitude = audioop.max(chunk, 2)  # 2 bytes per sample for paInt16
            #Requires volume about the silence threshold of 1200
            if amplitude < silence_threshold:
                is_speech = False

            if is_speech:  
                voiced_frames.append(chunk)
                triggered = True
                silence_chunks = 0
            elif triggered:
                if silence_chunks > 20:
                    triggered = False
                    pass
                else:
                    silence_chunks +=1
                    voiced_frames.append(chunk)
            elif voiced_frames:
                # Yield collected voiced frames and clear the buffer
                yield b''.join(voiced_frames)
                voiced_frames = []
def wake_collection(wake_word,audio_index,wake_word2="god"):
    audio = pyaudio.PyAudio()
    if audio_index == 1:
        silence_threshold = 10
    else:
        silence_threshold = 1200
    stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            input=True,
                            frames_per_buffer=480,
                            input_device_index=audio_index)
    for audio_frame in vad_collector(stream,silence_threshold=silence_threshold):
        text = ""
        print("Detected speech")
        save_audio(audio_frame,"detected_speech.wav")
        text = speech_to_text("detected_speech.wav")
        print(text)
        if wake_word in text.lower() or wake_word2 in text.lower():
            return True
        


