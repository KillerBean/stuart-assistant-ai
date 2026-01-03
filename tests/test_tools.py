import pytest
from datetime import datetime as dt
import wikipedia
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from stuart_ai.tools import AssistantTools
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.core.enums import AssistantSignal


@pytest.fixture
def assistant_tools_fixture(mocker):
    """
    Fixture to create an instance of AssistantTools with mocked dependencies.
    """
    mock_speak_func = AsyncMock()
    mock_confirm_func = AsyncMock()
    mock_web_search_agent = mocker.MagicMock(spec=WebSearchAgent)
    app_aliases = {
        "browser": {
            "Linux": "firefox",
            "Windows": "chrome",
            "Darwin": "safari"
        }
    }
    
    tools = AssistantTools(
        speak_func=mock_speak_func,
        confirmation_func=mock_confirm_func,
        app_aliases=app_aliases,
        web_search_agent=mock_web_search_agent
    )
    
    return tools, mock_speak_func, mock_confirm_func, mock_web_search_agent

@pytest.mark.asyncio
async def test_get_time(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    fixed_time = dt(2023, 10, 27, 14, 45)
    # Mock datetime where it is used in tools module
    mocker.patch('stuart_ai.tools.datetime').now.return_value = fixed_time
    
    result = await tools._get_time()
    
    assert result == "São 14:45."

@pytest.mark.asyncio
async def test_tell_joke_success(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    # Mock aiohttp ClientSession
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "type": "single",
        "joke": "Qual é o cúmulo da sorte? Ser atropelado por uma ambulância."
    }
    mock_response.raise_for_status = MagicMock()

    # Create a mock for the context manager returned by session.get()
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__.return_value = mock_response
    mock_context_manager.__aexit__.return_value = None

    mock_session = MagicMock()
    mock_session.get.return_value = mock_context_manager
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    
    mocker.patch('aiohttp.ClientSession', return_value=mock_session)
    
    result = await tools._tell_joke()
    assert result == "Qual é o cúmulo da sorte? Ser atropelado por uma ambulância."

@pytest.mark.asyncio
async def test_tell_joke_error(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    mocker.patch('aiohttp.ClientSession', side_effect=Exception("API Error"))
    
    result = await tools._tell_joke()
    assert result == "Desculpe, não consegui buscar uma piada agora."

@pytest.mark.asyncio
async def test_search_wikipedia_success(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    # Since we use asyncio.to_thread, we mock the underlying blocking function
    mocker.patch('stuart_ai.tools.wikipedia.summary', return_value="Python é uma linguagem.")
    mocker.patch('stuart_ai.tools.wikipedia.set_lang')

    result = await tools._search_wikipedia("Python")
    
    assert result == "Python é uma linguagem."

@pytest.mark.asyncio
async def test_search_wikipedia_page_error(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    mocker.patch('stuart_ai.tools.wikipedia.summary', side_effect=wikipedia.exceptions.PageError("page not found"))
    mocker.patch('stuart_ai.tools.wikipedia.set_lang')
    
    result = await tools._search_wikipedia("TermoInexistente")
    assert result == "Desculpe, não encontrei nenhum resultado para TermoInexistente."

@pytest.mark.asyncio
async def test_get_weather_success(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    weather_info = "São Paulo: +25°C"
    mock_response = AsyncMock()
    mock_response.text.return_value = weather_info
    mock_response.raise_for_status = MagicMock()

    # Create a mock for the context manager returned by session.get()
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__.return_value = mock_response
    mock_context_manager.__aexit__.return_value = None

    mock_session = MagicMock()
    mock_session.get.return_value = mock_context_manager
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    
    mocker.patch('aiohttp.ClientSession', return_value=mock_session)

    result = await tools._get_weather("São Paulo")
    
    assert result == weather_info

@pytest.mark.asyncio
async def test_open_app(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    mocker.patch('stuart_ai.tools.platform.system', return_value="Linux")
    mock_popen = mocker.patch('stuart_ai.tools.subprocess.Popen')
    
    result = await tools._open_app("firefox")
    
    assert result == f"Abrindo firefox."
    # asyncio.to_thread calls the function, so mock_popen should be called
    mock_popen.assert_called_once()

@pytest.mark.asyncio
async def test_shutdown_computer_confirmed(assistant_tools_fixture, mocker):
    tools, _, mock_confirm, _ = assistant_tools_fixture
    
    mock_confirm.return_value = True
    mock_run = mocker.patch('stuart_ai.tools.subprocess.run')
    mocker.patch('stuart_ai.tools.platform.system', return_value="Linux")
    
    result = await tools._shutdown_computer()
    
    mock_confirm.assert_called_once()
    mock_run.assert_called_once()
    assert "Adeus!" in result

@pytest.mark.asyncio
async def test_perform_web_search_success(assistant_tools_fixture, mocker):
    tools, mock_speak, _, mock_web_search_agent = assistant_tools_fixture
    
    query = "test query"
    mock_web_search_agent.run_search_crew.return_value = "Search Result"
    
    result = await tools._perform_web_search(query)
    
    mock_speak.assert_called_once()
    assert "Search Result" in result

@pytest.mark.asyncio
async def test_quit(assistant_tools_fixture):
    tools, mock_speak, _, _ = assistant_tools_fixture
    
    result = await tools._quit()
    
    mock_speak.assert_called_once()
    assert result == AssistantSignal.QUIT