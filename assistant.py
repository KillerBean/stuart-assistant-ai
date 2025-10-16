import os
import uuid
import whisper
import wikipedia
from gtts import gTTS
import sounddevice as sd
from playsound import playsound
import speech_recognition as sr
from tmp_file_handler import TempFileHandler
from command_handler import CommandHandler

class Assistant:
    def __init__(self):
        self.keyword = os.getenv("ASSISTANT_KEYWORD", "chronos").lower()
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
        self.command_handler = CommandHandler(self.speak, self.listen_for_confirmation, self.app_aliases)

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

    def listen_for_confirmation(self, prompt: str) -> bool:
        """Asks a confirmation question and listens for a 'yes' or 'no' answer."""
        self.speak(prompt)
        try:
            with sr.Microphone() as source:
                print("Listening for confirmation...")
                # Adjust for ambient noise to better capture the short answer
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)

                with TempFileHandler(self.temp_file_path) as temp_file:
                    with open(temp_file, "wb") as f:
                        f.write(audio.get_wav_data())
                    
                    result = self.model.transcribe(temp_file, language="pt", fp16=False)
                
                response_text = result['text'].lower().strip()
                print(f"Confirmation response: '{response_text}'")
                return "sim" in response_text

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            print("Could not understand confirmation.")
            return False
        except Exception as e:
            print(f"An error occurred during confirmation: {e}")
            return False

    def handle_command(self, text: str):
        command = text.lower().replace(self.keyword, "").strip()
        print(f"Keyword detected! Command: '{command}'")
        self.command_handler.process(command)

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