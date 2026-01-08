import pytest
from unittest.mock import MagicMock, AsyncMock
from stuart_ai.tools.system_tools import AssistantTools
from stuart_ai.core.enums import AssistantSignal

@pytest.fixture
def tools():
    speak = AsyncMock()
    confirm = AsyncMock()
    app_aliases = {}
    web = MagicMock()
    rag = MagicMock()
    
    return AssistantTools(speak, confirm, app_aliases, web, rag)

@pytest.mark.asyncio
async def test_get_date_ignores_args(tools):
    # Should not raise TypeError
    result = tools._get_date("hoje", useless_arg=1)
    assert "Hoje é" in result

@pytest.mark.asyncio
async def test_get_time_ignores_args(tools):
    result = tools._get_time("agora")
    assert "São" in result

@pytest.mark.asyncio
async def test_quit_ignores_args(tools):
    result = await tools._quit("tchau")
    assert result == AssistantSignal.QUIT

@pytest.mark.asyncio
async def test_shutdown_ignores_args(tools):
    # Mock confirm to return False to avoid actual shutdown logic
    tools.confirm.return_value = False
    result = await tools._shutdown_computer("agora")
    assert "cancelada" in result
