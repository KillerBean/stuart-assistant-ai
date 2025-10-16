import os
import uuid
import platform
import whisper
import requests
import wikipedia
import subprocess
from gtts import gTTS
import sounddevice as sd
from datetime import datetime
from playsound import playsound
import speech_recognition as sr
from tmp_file_handler import TempFileHandler

class Assistant:
    def __init__(self):
        self.keyword = os.getenv("ASSISTANT_KEYWORD", "cronos").lower()
        self.temp_file_path = "tmp/temp_audio.wav"
        self.recognizer = sr.Recognizer()
        print("Loading Whisper model...")
        self.model = whisper.load_model("small")
        wikipedia.set_lang("pt")
        print("Model loaded.")
        self.app_aliases = {
            "navegador": {
                "Linux": "firefox",
                "Windows": "firefox",
                "Darwin": "Firefox"
            },
            "editor de código": {
                "Linux": "code",
                "Windows": "code",
                "Darwin": "Visual Studio Code"
            },
            # Adicione mais apelidos aqui
        }

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
        elif "previsão do tempo" in command:
            city = ""
            if "para" in command:
                city = command.split("para")[-1].strip()
            
            if not city:
                self.speak("Claro, para qual cidade você gostaria da previsão do tempo?")
                return

            self.speak(f"Verificando a previsão do tempo para {city}.")
            try:
                url = f"https://wttr.in/{city}?format=3"
                response = requests.get(url)
                response.raise_for_status()
                self.speak(response.text)
            except requests.exceptions.RequestException:
                self.speak(f"Desculpe, não consegui obter a previsão do tempo para {city}.")
        elif "abra" in command or "inicie" in command:
            spoken_name = command.replace("abra", "").replace("inicie", "").strip()
            if not spoken_name:
                self.speak("Claro, qual programa você gostaria de abrir?")
                return

            system = platform.system()
            executable_name = spoken_name

            # Check if the spoken name is an alias
            if spoken_name in self.app_aliases:
                if system in self.app_aliases[spoken_name]:
                    executable_name = self.app_aliases[spoken_name][system]
                else:
                    self.speak(f"Não sei como abrir o '{spoken_name}' neste sistema operacional.")
                    return

            self.speak(f"Ok, abrindo {spoken_name}.")
            try:
                if system == "Windows":
                    # No Windows, 'start' é um comando de shell
                    subprocess.Popen(['start', executable_name], shell=True)
                elif system == "Darwin":  # macOS
                    subprocess.Popen(['open', '-a', executable_name])
                elif system == "Linux":
                    subprocess.Popen([executable_name])
                else:
                    self.speak(f"Desculpe, não sei como abrir programas no sistema {system}.")
            except FileNotFoundError:
                self.speak(f"Desculpe, não consegui encontrar o programa {spoken_name}.")
            except Exception as e:
                print(f"Error opening application: {e}")
                self.speak(f"Ocorreu um erro ao tentar abrir o {spoken_name}.")
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