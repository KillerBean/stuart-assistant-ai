import os
import speech_recognition as sr
import sounddevice as sd
import whisper
from tmp_file_handler import TempFileHandler
from gtts import gTTS
from playsound import playsound
import uuid
from datetime import datetime
import random

class Assistant:
    def __init__(self):
        self.keyword = os.getenv("ASSISTANT_KEYWORD", "chronos").lower()
        self.temp_file_path = "tmp/temp_audio.wav"
        self.recognizer = sr.Recognizer()
        print("Loading Whisper model...")
        self.model = whisper.load_model("small")
        print("Model loaded.")

    def _print_device_info(self):
        print("Available audio input devices:")
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"{idx}: {device['name']}")

    def select_input_device(self):
        self._print_device_info()
        try:
            device_index = int(input("Select the input device index: "))
            sd.default.device = device_index
            print(f"Selected device: {sd.query_devices(device_index)['name']}")
        except (ValueError, IndexError) as e:
            print(f"Invalid device index. {e}")
            exit(1)

    def set_input_device_by_name(self, name):
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if name.lower() in device['name'].lower() and device['max_input_channels'] > 0:
                sd.default.device = idx
                print(f"Selected device: {device['name']}")
                return
        print(f"No input device found with name containing '{name}'")
        exit(1)

    def speak(self, text: str):
        """
        Converts text to speech and plays it.
        """
        try:
            print(f"Assistant: {text}")
            tts = gTTS(text=text, lang='pt-br')

            # Use a unique filename to avoid conflicts
            temp_audio_file = f"tmp/response_{uuid.uuid4()}.mp3"
            
            # Ensure tmp directory exists
            dir_name = os.path.dirname(temp_audio_file)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            tts.save(temp_audio_file)
            playsound(temp_audio_file)
            os.remove(temp_audio_file)
        except Exception as e:
            print(f"Error in text-to-speech: {e}")

    def handle_command(self, text: str):
        command = text.lower().replace(self.keyword, "").strip()
        print(f"Keyword detected! Command: '{command}'")
        if "horas são" in command:
            now = datetime.now().strftime("%H:%M")
            self.speak(f"São {now}.")
        elif "conte uma piada" in command:
            jokes = [
                "O que o pato disse para a pata? Vem quá!",
                "Por que o pinheiro não se perde na floresta? Porque ele tem uma pinha!",
                "Qual é o cúmulo da rapidez? Sair de uma briga antes do primeiro soco.",
                "O que um cromossomo disse para o outro? Cromossomos felizes!",
                "Você conhece a piada do pônei? Pô nei eu."
            ]
            joke = random.choice(jokes)
            self.speak(joke)
        else:
            self.speak("Desculpe, não entendi o comando.")

    def listen_continuously(self):
        """
        Listens for audio continuously, transcribes it, and checks for the keyword.
        """
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"Listening for keyword '{self.keyword}'...")
            while True:
                try:
                    audio = self.recognizer.listen(source)
                    print("Audio captured, processing...")
                    
                    with TempFileHandler(self.temp_file_path) as temp_file:
                        with open(temp_file, "wb") as f:
                            f.write(audio.get_wav_data())
                        
                        # Transcribe using Whisper
                        result = self.model.transcribe(temp_file, language="pt", fp16=False)
                        
                    text = result['text'].strip()
                    print(f"Heard: {text}")

                    if self.keyword in text.lower():
                        self.handle_command(text)

                except sr.WaitTimeoutError:
                    print("Listening timed out, listening again...")
                except sr.UnknownValueError:
                    print("Could not understand audio, listening again...")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")