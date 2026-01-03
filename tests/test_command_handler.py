import pytest
from unittest.mock import MagicMock, AsyncMock
from stuart_ai.services.command_handler import CommandHandler, SimpleTool
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.core.enums import AssistantSignal

@pytest.fixture
def command_handler_fixture(mocker):
    """
    Fixture for creating a CommandHandler instance with mocked dependencies.
    """
    mock_speak_func = AsyncMock()
    mock_confirm_func = AsyncMock()
    mock_web_search_agent = mocker.MagicMock(spec=WebSearchAgent)
    app_aliases = {"browser": "firefox"}

    # Mock OllamaLLM to prevent actual instantiation
    mocker.patch("stuart_ai.services.command_handler.OllamaLLM")

    # Mock SemanticRouter to prevent actual LLM calls
    mock_router = mocker.patch("stuart_ai.services.command_handler.SemanticRouter")
    mock_router_instance = mock_router.return_value
    mock_router_instance.route = AsyncMock()

    handler = CommandHandler(
        speak_func=mock_speak_func,
        confirmation_func=mock_confirm_func,
        app_aliases=app_aliases,
        web_search_agent=mock_web_search_agent
    )

    # We need to mock the tools inside the handler to isolate logic
    # The handler creates real SimpleTool instances which call real AssistantTools methods.
    # We want to mock what those SimpleTool instances do.
    
    # Let's mock the `run` method of the tools in the handler.tools dictionary
    for name, tool in handler.tools.items():
        tool.run = AsyncMock(return_value=f"Result from {name}")

    # Specifically set return values for some tools to match test expectations
    handler.tools["time"].run.return_value = "São 10:00"
    handler.tools["joke"].run.return_value = "Uma piada engraçada."
    handler.tools["wikipedia"].run.return_value = "Resultado da Wikipedia."
    handler.tools["open_app"].run.return_value = "Aplicativo aberto."
    handler.tools["quit"].run.return_value = AssistantSignal.QUIT

    return handler, mock_speak_func, mock_router_instance

@pytest.mark.asyncio
async def test_process_empty_command(command_handler_fixture):
    """Tests that the process method ignores empty or whitespace-only commands."""
    handler, mock_speak, _ = command_handler_fixture
    
    await handler.process("")
    await handler.process("   ")
    
    mock_speak.assert_not_called()

@pytest.mark.asyncio
async def test_system_route_open_app(command_handler_fixture):
    """Tests that system commands (regex) like 'open app' are routed correctly."""
    handler, mock_speak, _ = command_handler_fixture
    
    await handler.process("abra o firefox")

    # Verify open_app tool was called with 'firefox'
    handler.tools["open_app"].run.assert_called_once_with("firefox")
    mock_speak.assert_called_once_with("Aplicativo aberto.")

@pytest.mark.asyncio
async def test_system_route_quit(command_handler_fixture):
    """Tests that 'sair' returns the QUIT signal."""
    handler, mock_speak, _ = command_handler_fixture
    
    result = await handler.process("sair")
    
    assert result == AssistantSignal.QUIT
    # Quit tool usually speaks before returning, but here we mocked the tool run.
    # The handler speaks whatever the tool returns if it's not QUIT signal (or if it is? let's check code)
    # Code says: if result == AssistantSignal.QUIT: return AssistantSignal.QUIT
    mock_speak.assert_not_called() 

@pytest.mark.asyncio
async def test_semantic_route_time(command_handler_fixture):
    """Tests routing to a semantic tool (time)."""
    handler, mock_speak, mock_router = command_handler_fixture
    
    # Mock Router response
    mock_router.route.return_value = {"tool": "time", "args": None}

    await handler.process("que horas são?")
    
    mock_router.route.assert_called_once()
    handler.tools["time"].run.assert_called_once()
    mock_speak.assert_called_once_with("São 10:00")

@pytest.mark.asyncio
async def test_semantic_route_with_args(command_handler_fixture):
    """Tests routing to a semantic tool with arguments (wikipedia)."""
    handler, mock_speak, mock_router = command_handler_fixture
    
    mock_router.route.return_value = {"tool": "wikipedia", "args": "Python"}

    await handler.process("pesquise sobre Python")
    
    handler.tools["wikipedia"].run.assert_called_once_with("Python")
    mock_speak.assert_called_once_with("Resultado da Wikipedia.")

@pytest.mark.asyncio
async def test_semantic_route_not_found(command_handler_fixture):
    """Tests when semantic router returns a tool that doesn't exist."""
    handler, mock_speak, mock_router = command_handler_fixture
    
    mock_router.route.return_value = {"tool": "unknown_tool", "args": None}

    await handler.process("faça algo impossível")
    
    mock_speak.assert_called_once_with("Desculpe, não entendi o que você quis dizer.")

@pytest.mark.asyncio
async def test_semantic_route_general_chat(command_handler_fixture):
    """Tests general chat fallback."""
    handler, mock_speak, mock_router = command_handler_fixture
    
    mock_router.route.return_value = {"tool": "general_chat", "args": None}

    await handler.process("Olá")
    
    mock_speak.assert_called_once_with("Entendi. Como posso ajudar com isso?")

@pytest.mark.asyncio
async def test_extract_argument_removes_articles(command_handler_fixture):
    """Tests that _extract_argument correctly removes articles from the beginning."""
    handler, _, _ = command_handler_fixture
    command = "pesquise sobre o universo"
    keyword = "pesquise sobre"
    argument = handler._extract_argument(command, keyword)
    assert argument == "universo"
