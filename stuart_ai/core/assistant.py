import os
import uuid
import platform
import subprocess
import asyncio

import wikipedia
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
from stuart_ai.utils.tmp_file_handler import TempFileHandler
from stuart_ai.services.command_handler import CommandHandler
from stuart_ai.core.enums import AssistantSignal
from stuart_ai.core.config import settings
from stuart_ai.core.logger import logger
from stuart_ai.core.exceptions import AudioDeviceError, TranscriptionError

from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.agents.rag.rag_agent import LocalRAGAgent


class Assistant:
    def __init__(
        self,
        llm,
        web_search_agent: WebSearchAgent,
        local_rag_agent: LocalRAGAgent,
        semantic_router,
        memory,
        whisper_model,
        speech_recognizer: sr.Recognizer
    ):
        self.keyword = settings.assistant_keyword.lower()
        self.temp_file_path = f"{settings.temp_dir}/temp_audio.wav"
        
        self.recognizer = speech_recognizer
        self.model = whisper_model
        
        wikipedia.set_lang("pt")
        
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

        self.llm = llm
        self.web_search_agent = web_search_agent
        self.local_rag_agent = local_rag_agent

        self.command_handler = CommandHandler(
            self.speak,
            self.listen_for_confirmation,
            self.app_aliases,
            self.web_search_agent,
            self.local_rag_agent,
            semantic_router,
            memory
        )

    async def speak(self, text: str):
        """
        Converts text to speech and plays it.
        """
        temp_audio_file = f"{settings.temp_dir}/response_{uuid.uuid4()}.mp3"
        try:
            logger.info("Assistant: %s", text)
            tts = await asyncio.to_thread(gTTS, text=text, lang='pt-br')

            dir_name = os.path.dirname(temp_audio_file)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            await asyncio.to_thread(tts.save, temp_audio_file)

            system = platform.system()
            if system == "Linux":
                try:
                    # Use mpg123 on Linux, as playsound can be problematic
                    await asyncio.create_subprocess_exec(
                        "mpg123", temp_audio_file,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    # We wait a bit or use wait() if we want it to be fully synchronous playback
                    # For now, let's wait for it to finish to mimic original behavior
                    process = await asyncio.create_subprocess_exec(
                        "mpg123", temp_audio_file,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    await process.wait()
                except (FileNotFoundError, Exception):
                    # Fallback to playsound if mpg123 is not available or fails
                    logger.warning("mpg123 not found or failed, falling back to playsound...")
                    await asyncio.to_thread(playsound, temp_audio_file)
            else:
                # Use playsound for other systems (Windows, Darwin)
                await asyncio.to_thread(playsound, temp_audio_file)

        except Exception as e:
            logger.error("Error in text-to-speech: %s", e)
        finally:
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)

    async def listen_for_confirmation(self, prompt: str) -> bool:
        """Asks a confirmation question and listens for a 'yes' or 'no' answer."""
        await self.speak(prompt)
        try:
            def listen_act():
                try:
                    with sr.Microphone() as source:
                        logger.info("Listening for confirmation...")
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                        return self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                except OSError as e:
                    raise AudioDeviceError(f"Could not access microphone: {e}")

            audio = await asyncio.to_thread(listen_act)

            with TempFileHandler(self.temp_file_path) as temp_file:
                with open(temp_file, "wb") as f:
                    if hasattr(audio, '__iter__') and not isinstance(audio, sr.AudioData):
                        audio = next(audio)
                        f.write(audio.get_wav_data())
                    elif isinstance(audio, sr.AudioData):
                        f.write(audio.get_wav_data())
                
                try:
                    result = await asyncio.to_thread(self.model.transcribe, temp_file, language="pt", fp16=False)
                except Exception as e:
                    raise TranscriptionError(f"Transcription failed: {e}")
            
            response_text = str(result['text']).lower().strip()
            logger.info("Confirmation response: '%s'", response_text)
            return "sim" in response_text

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            logger.warning("Could not understand confirmation.")
            return False
        except AudioDeviceError as e:
            logger.error("Audio device error during confirmation: %s", e)
            await self.speak("Desculpe, não consegui acessar o microfone.")
            return False
        except TranscriptionError as e:
            logger.error("Transcription error during confirmation: %s", e)
            await self.speak("Desculpe, tive um problema ao processar sua voz.")
            return False
        except Exception as e:
            logger.error("An error occurred during confirmation: %s", e)
            return False

    async def handle_command(self, text: str):
        command = text.lower().replace(self.keyword, "").strip().lstrip(",").strip()
        if not command:
            await self.speak("Sim, em que posso ajudar?")
            return None
        logger.info("Keyword detected! Command: '%s'", command)
        return await self.command_handler.process(command)

    async def listen_continuously(self):
        """
        Listens for audio continuously, transcribes it, and checks for the keyword.
        """
        logger.info("Adjusting for ambient noise...")
        # Initial adjustment
        def adjust():
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            except OSError as e:
                raise AudioDeviceError(f"Could not access microphone: {e}")
        
        try:
            await asyncio.to_thread(adjust)
        except AudioDeviceError as e:
            logger.critical("Initial microphone access failed: %s", e)
            await self.speak("Erro crítico: Não consegui encontrar um microfone funcional.")
            return

        logger.info("Listening for keyword '%s'...", self.keyword)
        
        while True:
            try:
                def listen_loop():
                    try:
                        with sr.Microphone() as source:
                            return self.recognizer.listen(source)
                    except OSError as e:
                        raise AudioDeviceError(f"Could not access microphone: {e}")

                audio = await asyncio.to_thread(listen_loop)
                logger.debug("Audio captured, processing...")
                
                with TempFileHandler(self.temp_file_path) as temp_file:
                    with open(temp_file, "wb") as f:
                        if hasattr(audio, '__iter__') and not isinstance(audio, sr.AudioData):
                            audio = next(audio)
                            f.write(audio.get_wav_data())
                        elif isinstance(audio, sr.AudioData):
                            f.write(audio.get_wav_data())
                    
                    # Transcribe using Whisper
                    try:
                        result = await asyncio.to_thread(self.model.transcribe, temp_file, language="pt", fp16=False)
                    except Exception as e:
                        raise TranscriptionError(f"Transcription failed: {e}")
                    
                text = str(result['text']).strip()
                logger.debug("Heard: %s", text)

                if self.keyword in text.lower():
                    result = await self.handle_command(text)
                    if result == AssistantSignal.QUIT:
                        break

            except sr.WaitTimeoutError:
                logger.debug("Listening timed out, listening again...")
            except sr.UnknownValueError:
                logger.debug("Could not understand audio, listening again...")
            except AudioDeviceError as e:
                logger.error("Audio device error: %s", e)
                await self.speak("Tive um problema com o microfone. Tentando reconectar...")
                await asyncio.sleep(5)
            except TranscriptionError as e:
                logger.error("Transcription error: %s", e)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error("An unexpected error occurred: %s", e)
                await asyncio.sleep(1) # Prevent tight error loop