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
import requests
import wikipedia

class Assistant:
    def __init__(self):
        self.keyword = os.getenv("ASSISTANT_KEYWORD", "cronos").lower()
        self.temp_file_path = "tmp/temp_audio.wav"
        self.recognizer = sr.Recognizer()
        print("Loading Whisper model...")
        self.model = whisper.load_model("small")
        wikipedia.set_lang("pt")
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
                return device['name']
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
            try:
                # API URL for jokes in Portuguese, avoiding sensitive topics
                url = "https://v2.jokeapi.dev/joke/Any?lang=pt&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for bad status codes
                joke_data = response.json()

                if joke_data.get('type') == 'single':
                    joke = joke_data['joke']
                else:
                    joke = f"{joke_data['setup']} ... {joke_data['delivery']}"
                
                self.speak(joke)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching joke from API: {e}")
                self.speak("Desculpe, não consegui buscar uma piada agora. Tente novamente mais tarde.")
        elif "pesquise sobre" in command or "o que é" in command:
            search_term = command.replace("pesquise sobre", "").replace("o que é", "").strip()
            self.speak(f"Claro, pesquisando sobre {search_term} na Wikipedia.")
            try:
                summary = wikipedia.summary(search_term, sentences=2)
                self.speak(summary)
            except wikipedia.exceptions.PageError:
                self.speak(f"Desculpe, não encontrei nenhum resultado para {search_term}.")
            except wikipedia.exceptions.DisambiguationError:
                self.speak(f"O termo {search_term} é muito vago. Por favor, seja mais específico.")
            except Exception as e:
                print(f"Error fetching from Wikipedia: {e}")
                self.speak("Desculpe, ocorreu um erro ao tentar pesquisar na Wikipedia.")
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