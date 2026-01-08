import pytest
from unittest.mock import MagicMock, AsyncMock
from stuart_ai.tools.system_tools import AssistantTools

@pytest.fixture
def tools():
    speak = AsyncMock()
    confirm = AsyncMock()
    app_aliases = {}
    web = MagicMock()
    rag = MagicMock()
    
    tools = AssistantTools(speak, confirm, app_aliases, web, rag)
    # Mock manager to avoid file I/O
    tools.calendar_manager = MagicMock()
    tools.calendar_manager.list_events.return_value = "Events listed"
    return tools

@pytest.mark.asyncio
async def test_check_calendar_with_string(tools):
    result = await tools._check_calendar("2026-01-08")
    tools.calendar_manager.list_events.assert_called_with("2026-01-08")
    assert result == "Events listed"

@pytest.mark.asyncio
async def test_check_calendar_with_dict(tools):
    # Simulate LLM returning a dict wrapper
    result = await tools._check_calendar({"date": "amanhã"})
    tools.calendar_manager.list_events.assert_called_with("amanhã")
    assert result == "Events listed"

@pytest.mark.asyncio
async def test_check_calendar_with_complex_dict(tools):
    # Simulate LLM returning a dict with different key
    result = await tools._check_calendar({"datetime": "hoje"})
    tools.calendar_manager.list_events.assert_called_with("hoje")
    assert result == "Events listed"

@pytest.mark.asyncio
async def test_check_calendar_with_none(tools):
    result = await tools._check_calendar(None)
    tools.calendar_manager.list_events.assert_called_with(None)
    assert result == "Events listed"
