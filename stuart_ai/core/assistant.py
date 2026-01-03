import os
import uuid
import platform
import subprocess
import whisper
import wikipedia
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
from stuart_ai.utils.tmp_file_handler import TempFileHandler
from stuart_ai.services.command_handler import CommandHandler
from stuart_ai.core.enums import AssistantSignal
from stuart_ai.core.config import settings
from stuart_ai.core.logger import logger

from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.tools import AssistantTools
from stuart_ai.LLM.ollama_llm import OllamaLLM


class Assistant:
    def __init__(self):
        self.keyword = settings.assistant_keyword.lower()
        self.temp_file_path = f"{settings.temp_dir}/temp_audio.wav"
        self.recognizer = sr.Recognizer()
        logger.info("Loading Whisper model...")
        self.model = whisper.load_model("small")
        wikipedia.set_lang("pt")
        logger.info("Model loaded.")
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

        self.llm = OllamaLLM().get_llm_instance()

        self.web_search_agent = WebSearchAgent(llm=self.llm)
        self.assistant_tools = AssistantTools(
            speak_func=self.speak,
            confirmation_func=self.listen_for_confirmation,
            app_aliases=self.app_aliases,
            web_search_agent=self.web_search_agent
        )

        self.command_handler = CommandHandler(
            self.speak,
            self.listen_for_confirmation,
            self.app_aliases,
            self.web_search_agent
        )

    def speak(self, text: str):
        """
        Converts text to speech and plays it.
        """
        temp_audio_file = f"tmp/response_{uuid.uuid4()}.mp3"
        try:
            logger.info(f"Assistant: {text}")
            tts = gTTS(text=text, lang='pt-br')

            dir_name = os.path.dirname(temp_audio_file)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            tts.save(temp_audio_file)

            system = platform.system()
            if system == "Linux":
                try:
                    # Use mpg123 on Linux, as playsound can be problematic
                    subprocess.run(
                        ["mpg123", temp_audio_file], 
                        check=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL
                    )
                except (FileNotFoundError, subprocess.CalledProcessError):
                    # Fallback to playsound if mpg123 is not available or fails
                    logger.warning("mpg123 not found or failed, falling back to playsound...")
                    playsound(temp_audio_file)
            else:
                # Use playsound for other systems (Windows, Darwin)
                playsound(temp_audio_file)

        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
        finally:
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)

    def listen_for_confirmation(self, prompt: str) -> bool:
        """Asks a confirmation question and listens for a 'yes' or 'no' answer."""
        self.speak(prompt)
        try:
            with sr.Microphone() as source:
                logger.info("Listening for confirmation...")
                # Adjust for ambient noise to better capture the short answer
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)

                with TempFileHandler(self.temp_file_path) as temp_file:
                    with open(temp_file, "wb") as f:
                        if hasattr(audio, '__iter__') and not isinstance(audio, sr.AudioData):
                            audio = next(audio)
                            f.write(audio.get_wav_data())
                        elif isinstance(audio, sr.AudioData):
                            f.write(audio.get_wav_data())
                    
                    result = self.model.transcribe(temp_file, language="pt", fp16=False)
                
                response_text = str(result['text']).lower().strip()
                logger.info(f"Confirmation response: '{response_text}'")
                return "sim" in response_text

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            logger.warning("Could not understand confirmation.")
            return False
        except Exception as e:
            logger.error(f"An error occurred during confirmation: {e}")
            return False

    def handle_command(self, text: str):
        command = text.lower().replace(self.keyword, "").strip().lstrip(",").strip()
        if not command:
            self.speak("Sim, em que posso ajudar?")
            return None
        logger.info(f"Keyword detected! Command: '{command}'")
        return self.command_handler.process(command)

    def listen_continuously(self):
        """
        Listens for audio continuously, transcribes it, and checks for the keyword.
        """
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info(f"Listening for keyword '{self.keyword}'...")
            while True:
                try:
                    audio = self.recognizer.listen(source)
                    logger.debug("Audio captured, processing...")
                    
                    
                    with TempFileHandler(self.temp_file_path) as temp_file:
                        with open(temp_file, "wb") as f:
                            if hasattr(audio, '__iter__') and not isinstance(audio, sr.AudioData):
                                audio = next(audio)
                                f.write(audio.get_wav_data())
                            elif isinstance(audio, sr.AudioData):
                                f.write(audio.get_wav_data())
                        
                        # Transcribe using Whisper
                        result = self.model.transcribe(temp_file, language="pt", fp16=False)
                        
                    text = str(result['text']).strip()
                    logger.debug(f"Heard: {text}")

                    if self.keyword in text.lower():
                        result = self.handle_command(text)
                        if result == AssistantSignal.QUIT:
                            break

                except sr.WaitTimeoutError:
                    logger.debug("Listening timed out, listening again...")
                except sr.UnknownValueError:
                    logger.debug("Could not understand audio, listening again...")
                except Exception as e:
                    logger.error(f"An unexpected error occurred: {e}")