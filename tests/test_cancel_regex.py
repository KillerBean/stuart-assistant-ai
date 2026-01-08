import pytest
from unittest.mock import MagicMock, AsyncMock
from stuart_ai.services.command_handler import CommandHandler

@pytest.fixture
def mock_dependencies():
    speak = AsyncMock()
    confirm = AsyncMock()
    app_aliases = {}
    web_search = MagicMock()
    rag = MagicMock()
    router = MagicMock()
    memory = MagicMock()
    
    # Configure router to return something else to ensure Regex takes precedence
    router.route = AsyncMock(return_value={"tool": "general_chat", "args": None})
    
    return speak, confirm, app_aliases, web_search, rag, router, memory

@pytest.mark.asyncio
async def test_cancel_regex_precedence(mock_dependencies):
    speak, confirm, app_aliases, web_search, rag, router, memory = mock_dependencies
    
    handler = CommandHandler(speak, confirm, app_aliases, web_search, rag, router, memory)
    
    # Simulate a user saying "cancelar" which should match the regex
    await handler.process("cancelar")
    
    # Verify the assistant spoke the cancellation message
    speak.assert_called_with("Tudo bem, comando cancelado.")
    
    # Verify router was NOT called (Regex precedence)
    router.route.assert_not_called()
