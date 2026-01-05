import pytest
from datetime import datetime as dt
import wikipedia
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from stuart_ai.tools.system_tools import AssistantTools
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.agents.rag.rag_agent import LocalRAGAgent
from stuart_ai.core.enums import AssistantSignal


@pytest.fixture
def assistant_tools_fixture(mocker):
    """
    Fixture to create an instance of AssistantTools with mocked dependencies.
    """
    mock_speak_func = AsyncMock()
    mock_confirm_func = AsyncMock()
    mock_web_search_agent = mocker.MagicMock(spec=WebSearchAgent)
    mock_local_rag_agent = mocker.MagicMock(spec=LocalRAGAgent)
    mock_local_rag_agent.document_store = mocker.MagicMock()
    
    # Mock CalendarManager
    mock_calendar_cls = mocker.patch('stuart_ai.tools.system_tools.CalendarManager')
    mock_calendar_instance = mock_calendar_cls.return_value

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
        web_search_agent=mock_web_search_agent,
        local_rag_agent=mock_local_rag_agent
    )
    
    return tools, mock_speak_func, mock_confirm_func, mock_web_search_agent, mock_local_rag_agent, mock_calendar_instance

@pytest.mark.asyncio
async def test_get_time(assistant_tools_fixture, mocker):
    tools, _, _, _, _, _ = assistant_tools_fixture
    
    fixed_time = dt(2023, 10, 27, 14, 45)
    # Mock datetime where it is used in tools module
    mocker.patch('stuart_ai.tools.system_tools.datetime').now.return_value = fixed_time
    
    result = await tools._get_time()
    
    assert result == "São 14:45."

@pytest.mark.asyncio
async def test_tell_joke_success(assistant_tools_fixture, mocker):
    tools, _, _, _, _, _ = assistant_tools_fixture
    
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
    tools, _, _, _, _, _ = assistant_tools_fixture
    
    mocker.patch('aiohttp.ClientSession', side_effect=Exception("API Error"))
    
    result = await tools._tell_joke()
    assert result == "Desculpe, não consegui buscar uma piada agora."

@pytest.mark.asyncio
async def test_search_wikipedia_success(assistant_tools_fixture, mocker):
    tools, _, _, _, _, _ = assistant_tools_fixture
    
    # Since we use asyncio.to_thread, we mock the underlying blocking function
    mocker.patch('stuart_ai.tools.system_tools.wikipedia.summary', return_value="Python é uma linguagem.")
    mocker.patch('stuart_ai.tools.system_tools.wikipedia.set_lang')

    result = await tools._search_wikipedia("Python")
    
    assert result == "Python é uma linguagem."

@pytest.mark.asyncio
async def test_search_wikipedia_page_error(assistant_tools_fixture, mocker):
    tools, _, _, _, _, _ = assistant_tools_fixture
    
    mocker.patch('stuart_ai.tools.system_tools.wikipedia.summary', side_effect=wikipedia.exceptions.PageError("page not found"))
    mocker.patch('stuart_ai.tools.system_tools.wikipedia.set_lang')
    
    result = await tools._search_wikipedia("TermoInexistente")
    assert result == "Desculpe, não encontrei nenhum resultado para TermoInexistente."

@pytest.mark.asyncio
async def test_get_weather_success(assistant_tools_fixture, mocker):
    tools, _, _, _, _, _ = assistant_tools_fixture
    
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
    tools, _, _, _, _, _ = assistant_tools_fixture
    
    mocker.patch('stuart_ai.tools.system_tools.platform.system', return_value="Linux")
    mock_popen = mocker.patch('stuart_ai.tools.system_tools.subprocess.Popen')
    
    result = await tools._open_app("firefox")
    
    assert result == f"Abrindo firefox."
    # asyncio.to_thread calls the function, so mock_popen should be called
    mock_popen.assert_called_once()

@pytest.mark.asyncio
async def test_shutdown_computer_confirmed(assistant_tools_fixture, mocker):
    tools, _, mock_confirm, _, _, _ = assistant_tools_fixture
    
    mock_confirm.return_value = True
    mock_run = mocker.patch('stuart_ai.tools.system_tools.subprocess.run')
    mocker.patch('stuart_ai.tools.system_tools.platform.system', return_value="Linux")
    
    result = await tools._shutdown_computer()
    
    mock_confirm.assert_called_once()
    mock_run.assert_called_once()
    assert "Adeus!" in result

@pytest.mark.asyncio
async def test_perform_web_search_success(assistant_tools_fixture, mocker):
    tools, mock_speak, _, mock_web_search_agent, _, _ = assistant_tools_fixture
    
    query = "test query"
    mock_web_search_agent.run.return_value = "Search Result"
    
    result = await tools._perform_web_search(query)
    
    mock_speak.assert_called_once()
    assert "Search Result" in result

@pytest.mark.asyncio
async def test_quit(assistant_tools_fixture):
    tools, mock_speak, _, _, _, _ = assistant_tools_fixture
    
    result = await tools._quit()
    
    mock_speak.assert_called_once()
    assert result == AssistantSignal.QUIT

@pytest.mark.asyncio
async def test_search_local_files(assistant_tools_fixture):
    tools, mock_speak, _, _, mock_rag_agent, _ = assistant_tools_fixture
    
    mock_rag_agent.run.return_value = "Conteúdo do arquivo."
    result = await tools._search_local_files("resumo projeto")
    
    mock_speak.assert_called_once_with("Pesquisando nos seus arquivos...")
    mock_rag_agent.run.assert_called_once_with("resumo projeto")
    assert result == "Conteúdo do arquivo."

@pytest.mark.asyncio
async def test_index_file(assistant_tools_fixture, mocker):
    tools, mock_speak, _, _, mock_rag_agent, _ = assistant_tools_fixture
    
    # Mock os.path.basename
    mocker.patch('stuart_ai.tools.system_tools.os.path.basename', return_value="doc.txt")
    
    result = await tools._index_file("/path/to/doc.txt")
    
    mock_speak.assert_called_once_with("Processando o arquivo doc.txt...")
    # Since we use asyncio.to_thread, we check if the method was called
    # However, mocking asyncio.to_thread or the method directly is tricky if we don't mock to_thread.
    # But checking if add_document was called on the mock object should work if to_thread executes it.
    # Wait, asyncio.to_thread runs the function in a thread. The mock object is thread-safe mostly.
    
    # Let's check if the method was called.
    mock_rag_agent.document_store.add_document.assert_called_once_with("/path/to/doc.txt")
    assert "aprendido com sucesso" in result

@pytest.mark.asyncio
async def test_add_calendar_event_success(assistant_tools_fixture):
    tools, mock_speak, _, _, _, mock_calendar = assistant_tools_fixture
    
    args = {"title": "Reunião", "datetime": "amanhã às 14h"}
    mock_calendar.add_event.return_value = "Evento agendado."
    
    result = await tools._add_calendar_event(args)
    
    mock_speak.assert_called_once()
    mock_calendar.add_event.assert_called_once_with("Reunião", "amanhã às 14h")
    assert result == "Evento agendado."

@pytest.mark.asyncio
async def test_add_calendar_event_missing_args(assistant_tools_fixture):
    tools, _, _, _, _, _ = assistant_tools_fixture
    
    args = {"title": "Reunião"} # Missing datetime
    result = await tools._add_calendar_event(args)
    
    assert "Preciso do nome do evento e da data/hora" in result

@pytest.mark.asyncio
async def test_check_calendar(assistant_tools_fixture):
    tools, mock_speak, _, _, _, mock_calendar = assistant_tools_fixture
    
    mock_calendar.list_events.return_value = "Lista de eventos."
    
    result = await tools._check_calendar("hoje")
    
    mock_speak.assert_called_once()
    mock_calendar.list_events.assert_called_once_with("hoje")
    assert result == "Lista de eventos."