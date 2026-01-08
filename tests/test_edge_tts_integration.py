import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from stuart_ai.core.assistant import Assistant
from stuart_ai.core.config import settings

@pytest.fixture
def mock_components():
    llm = MagicMock()
    web = MagicMock()
    rag = MagicMock()
    router = MagicMock()
    memory = MagicMock()
    whisper = MagicMock()
    recognizer = MagicMock()
    return llm, web, rag, router, memory, whisper, recognizer

@pytest.mark.asyncio
async def test_speak_uses_edge_tts(mock_components, mocker):
    llm, web, rag, router, memory, whisper, recognizer = mock_components
    
    assistant = Assistant(llm, web, rag, router, memory, whisper, recognizer)
    
    # Mock subprocess to avoid playing audio
    mocker.patch("asyncio.create_subprocess_exec", new_callable=AsyncMock)
    mocker.patch("stuart_ai.core.assistant.subprocess.DEVNULL")
    
    # Mock edge_tts
    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()
    
    # We need to patch the class constructor to return our mock instance
    with patch("stuart_ai.core.assistant.edge_tts.Communicate", return_value=mock_communicate) as mock_cls:
        await assistant.speak("Olá mundo")
        
        # Verify constructor call
        mock_cls.assert_called_with("Olá mundo", "pt-BR-AntonioNeural")
        
        # Verify save call
        assert mock_communicate.save.called
        # Check args passed to save (temp file path)
        args, _ = mock_communicate.save.call_args
        assert args[0].endswith(".mp3")
