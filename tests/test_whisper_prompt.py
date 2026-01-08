import pytest
from unittest.mock import MagicMock, AsyncMock
import asyncio
import speech_recognition as sr
from stuart_ai.core.assistant import Assistant

@pytest.fixture
def mock_components():
    llm = MagicMock()
    web = MagicMock()
    rag = MagicMock()
    router = MagicMock()
    memory = MagicMock()
    whisper = MagicMock()
    recognizer = MagicMock()
    
    # Mock recognizer methods
    recognizer.adjust_for_ambient_noise = MagicMock()
    # Simulate valid audio data
    audio_data = MagicMock(spec=sr.AudioData)
    audio_data.get_wav_data.return_value = b"fake_wav_data"
    recognizer.listen.return_value = audio_data
    
    # Mock whisper transcribe return
    whisper.transcribe.return_value = {"text": "sim"}
    
    return llm, web, rag, router, memory, whisper, recognizer

@pytest.mark.asyncio
async def test_transcribe_uses_initial_prompt(mock_components, mocker):
    llm, web, rag, router, memory, whisper, recognizer = mock_components
    
    # Mock asyncio.to_thread because Assistant uses it for blocking calls
    # We need to capture the call to whisper.transcribe which happens inside to_thread
    
    # Instead of mocking to_thread globally which is hard, we can inspect the mock_whisper call
    # because the assistant passes the mock instance.
    
    # But wait, asyncio.to_thread(func, *args, **kwargs) calls func(*args, **kwargs).
    # So if we mock whisper.transcribe, it will be called with the args.
    
    # We need to bypass the infinite loop of listen_continuously.
    # Testing listen_for_confirmation is easier as it's finite.
    
    assistant = Assistant(llm, web, rag, router, memory, whisper, recognizer)
    
    # Mock speak to avoid actual TTS
    assistant.speak = AsyncMock()
    
    # Mock sr.Microphone context manager
    mocker.patch("speech_recognition.Microphone.__enter__", return_value=MagicMock())
    mocker.patch("speech_recognition.Microphone.__exit__", return_value=None)
    
    # Mock ignore_stderr
    mocker.patch("stuart_ai.utils.audio_utils.ignore_stderr")

    # Call confirmation logic
    await assistant.listen_for_confirmation("Teste?")
    
    # Check if transcribe was called with initial_prompt
    args, kwargs = whisper.transcribe.call_args
    assert "initial_prompt" in kwargs
    assert kwargs["initial_prompt"] == "Confirmação. Responda apenas Sim ou Não."
    assert kwargs["condition_on_previous_text"] is False
