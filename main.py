import tkinter as tk
from tkinter import scrolledtext
from Scripts.chatbot import ChatBot
import time
from TTS.api import TTS
from Scripts.speech import speech_to_text, record_audio_until_silence, play_audio, text_to_speech, wake_collection
import random
import threading

def init():
    global Chatbot
    global SpeakBack
    #Audio output globals
    global Audio_index 
    Audio_index = 1
    # Memory based globals

    # Use vector db
    global LT_Memory
    LT_Memory = True 
    # commit convo to vector db
    global Remember_Conversation
    Remember_Conversation = True

    SpeakBack = False
    Chatbot = ChatBot()
    Chatbot.initialize_model()
    Chatbot.initialize_memory()

def on_submit():
    input_text = input_box.get("1.0", tk.END).strip()
    input_box.delete('1.0',tk.END)
    output_box.insert(tk.END, f"Input: {input_text}\n")
    output_box.see(tk.END)
    time.sleep(3)
    output_text = Chatbot.run(input_text,Remember_Conversation,LT_Memory)
    output_box.insert(tk.END, f"Reponse: {output_text}\n")
    if SpeakBack:
        text_to_speech(text=output_text)
        play_audio(rate=20500)

        

def on_microphone():
    # Placeholder for microphone input functionality
    input_box.delete('1.0',tk.END)
    chosen_confirmation = random.choice(["Confirmation1.wav","Confirmation2.wav","Confirmation3.wav"])
    root.update_idletasks()
    record_audio_until_silence(color_box=color_box, root=root,audio_index=Audio_index)
    
    color_box.config(bg="lightgrey")
    root.update_idletasks()
    time.sleep(1)
    input_text = speech_to_text()
    input_box.insert(tk.END, "User Query: " + input_text + "\n")
    time.sleep(3)
    play_audio(audio_filename=chosen_confirmation, rate=21500)
    output_text = Chatbot.run(input_text,Remember_Conversation,LT_Memory)
    output_box.insert(tk.END, f"Reponse: {output_text}\n")
    if SpeakBack:
        text_to_speech(text=output_text)
        play_audio(rate=21000)
def on_speak_back():
    global SpeakBack
    SpeakBack = not SpeakBack
    if SpeakBack:
        speak_button.config(bg="green")
    else:
        speak_button.config(bg="lightgrey")


def on_listen():
    global SpeakBack
    print("Running on_listen")
    if wake_collection("todd",Audio_index):
        chosen_intro = random.choice(["Intro1.wav","Intro2.wav","Intro3.wav"])
        time.sleep(1)
        play_audio(chosen_intro)
        SpeakBack = True
        on_microphone()
        root.after(5000,on_listen)

def on_headphone():
    global Audio_index
    Audio_index = 2
    stereo_button.config(bg="lightgrey")
    headphone_button.config(bg="green")

def on_stereo():
    global Audio_index
    Audio_index = 1
    stereo_button.config(bg="green")
    headphone_button.config(bg="lightgrey")

def on_memory():
    global LT_Memory
    LT_Memory = not LT_Memory
    if LT_Memory:
        memory_button.config(bg="green")
    else:
        memory_button.config(bg="lightgrey")
def on_remember():
    global Remember_Conversation
    Remember_Conversation = not Remember_Conversation
    if Remember_Conversation:
        remember_button.config(bg="green")
    else:
        remember_button.config(bg="lightgrey")

def on_chat():
    input_text = input_box.get("1.0", tk.END).strip()
    Chatbot.save_memory(input_text)
    input_box.delete('1.0',tk.END)
# Create the main window
root = tk.Tk()
root.title("My Little Chatbot: Void")
root.geometry("550x500")
init()
# Create a text input box
input_box = tk.Text(root, height=5, width=55)
input_box.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)
button_frame2 = tk.Frame(root)
button_frame2.pack(pady=5)
# Create a submit button
submit_button = tk.Button(button_frame, text="Submit", command=on_submit, bg="lightgrey")
submit_button.pack(side=tk.LEFT, padx=4)

mic_frame = tk.Frame(button_frame)
mic_frame.pack(side=tk.LEFT, padx=4)

# Create a microphone button
microphone_button = tk.Button(mic_frame, text="Microphone", command=on_microphone,bg="lightgrey")
microphone_button.pack(side=tk.LEFT, padx=4)

# Create a color-changing box
color_box = tk.Label(mic_frame, text=" ", width=2, height=1, bg="lightgrey")
color_box.pack(side=tk.LEFT, padx=4)

speak_button = tk.Button(button_frame, text="Speak Back", command=on_speak_back, bg="lightgrey")
speak_button.pack(side=tk.LEFT,padx=4)

listen_button = tk.Button(button_frame, text="Listen", command=on_listen, bg="lightgrey")
listen_button.pack(side=tk.LEFT,padx=4)

headphone_button = tk.Button(button_frame, text="Headphones", command=on_headphone, bg="lightgrey")
headphone_button.pack(side=tk.LEFT,padx=4)

stereo_button = tk.Button(button_frame, text="Stereo", command=on_stereo, bg="green")
stereo_button.pack(side=tk.LEFT,padx=4)

# Enables long term commitment to memory
remember_button = tk.Button(button_frame2, text="Remember", command=on_remember, bg="green")
remember_button.pack(side=tk.LEFT,padx=4)
# Utilize memory from previous conversations
memory_button = tk.Button(button_frame2, text="LT Memory", command=on_memory, bg="green")
memory_button.pack(side=tk.LEFT,padx=4)

chat_button = tk.Button(button_frame2, text="Journal", command=on_chat, bg="lightgrey")
chat_button.pack(side=tk.LEFT,padx=4)

# Create an output box
output_box = scrolledtext.ScrolledText(root, height=17, width=64)
output_box.pack(pady=10)


# Start the Tkinter event loop
root.mainloop()
