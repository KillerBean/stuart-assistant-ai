import pytest
from unittest.mock import MagicMock, patch
from command_handler import CommandHandler, SimpleTool
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.enums import AssistantSignal

@pytest.fixture
def command_handler_fixture(mocker):
    """
    Fixture for creating a CommandHandler instance with mocked dependencies,
    aligned with the new keyword-based router implementation.
    """
    mock_speak_func = mocker.MagicMock()
    mock_confirm_func = mocker.MagicMock()
    mock_web_search_agent = mocker.MagicMock(spec=WebSearchAgent)
    app_aliases = {"browser": "firefox"}

    handler = CommandHandler(
        speak_func=mock_speak_func,
        confirmation_func=mock_confirm_func,
        app_aliases=app_aliases,
        web_search_agent=mock_web_search_agent
    )

    # Replace the actual tools with mocks to isolate the handler's logic
    # The regex patterns are now correct (raw strings with single backslashes)
    handler.router_config = [
        (r"\b(horas?|tempo)\b", SimpleTool(name='_get_time', func=MagicMock(return_value="São 10:00"))),
        (r"\b(piada|conte-me uma piada)\b", SimpleTool(name='_tell_joke', func=MagicMock(return_value="Uma piada engraçada."))),
        (r"\b(wikipedia|pesquise sobre|o que é)\b", handler._handle_search, SimpleTool(name='_search_wikipedia', func=MagicMock(return_value="Resultado da Wikipedia."))),
        (r"\b(abra|abrir)\b", handler._handle_open_app, SimpleTool(name='_open_app', func=MagicMock(return_value="Aplicativo aberto."))),
        (r"\b(sair|encerrar)\b", SimpleTool(name='_quit', func=MagicMock(return_value=AssistantSignal.QUIT))),
    ]
    
    return handler, mock_speak_func, mock_confirm_func

def test_process_empty_command(command_handler_fixture):
    """Tests that the process method ignores empty or whitespace-only commands."""
    handler, mock_speak, _ = command_handler_fixture
    
    handler.process("")
    handler.process("   ")
    
    mock_speak.assert_not_called()

def test_routing_to_tool_no_args(command_handler_fixture):
    """Tests routing to a tool that requires no arguments."""
    handler, mock_speak, _ = command_handler_fixture
    
    handler.process("que horas são?")
    
    mock_speak.assert_called_once_with("São 10:00")

def test_routing_to_tool_with_args(command_handler_fixture):
    """Tests routing to a tool that requires an argument."""
    handler, mock_speak, _ = command_handler_fixture
    
    handler.process("pesquise sobre Python")
    
    search_tool_func = handler.router_config[2][2].func
    search_tool_func.assert_called_once_with("Python")
    mock_speak.assert_called_once_with("Resultado da Wikipedia.")

def test_routing_open_app_with_arg(command_handler_fixture):
    """Tests the specific handler for opening apps."""
    handler, mock_speak, _ = command_handler_fixture
    
    handler.process("abra o firefox")

    open_app_tool_func = handler.router_config[3][2].func
    open_app_tool_func.assert_called_once_with("firefox")
    mock_speak.assert_called_once_with("Aplicativo aberto.")

def test_routing_open_app_without_arg(command_handler_fixture):
    """Tests the specific handler for opening apps when no app is specified."""
    handler, mock_speak, _ = command_handler_fixture
    
    handler.process("abrir")

    open_app_tool_func = handler.router_config[3][2].func
    open_app_tool_func.assert_not_called()
    mock_speak.assert_called_once_with("Claro, qual aplicativo você gostaria de abrir?")

def test_command_not_found(command_handler_fixture):
    """Tests that an unknown command results in the 'não entendi' message."""
    handler, mock_speak, _ = command_handler_fixture
    
    handler.process("faça um sanduíche para mim")
    
    mock_speak.assert_called_once_with("Desculpe, não entendi o comando.")

def test_quit_signal_is_returned(command_handler_fixture):
    """Tests that a command like 'sair' returns the QUIT signal."""
    handler, mock_speak, _ = command_handler_fixture
    
    result = handler.process("sair")
    
    assert result == AssistantSignal.QUIT
    mock_speak.assert_not_called()

def test_tool_exception_handling(command_handler_fixture):
    """Tests that if a tool raises an exception, the error is handled gracefully."""
    handler, mock_speak, _ = command_handler_fixture

    # Correctly configure the joke tool to raise an exception
    joke_tool = handler.router_config[1][1] # Index 1 is the SimpleTool object
    joke_tool.func.side_effect = Exception("API de piadas fora do ar")

    handler.process("conte-me uma piada")
    
    mock_speak.assert_called_once_with("Desculpe, ocorreu um erro ao processar o comando.")

def test_extract_argument_removes_articles(command_handler_fixture):
    """Tests that _extract_argument correctly removes articles from the beginning."""
    handler, _, _ = command_handler_fixture
    command = "pesquise sobre o universo"
    keyword = "pesquise sobre"
    argument = handler._extract_argument(command, keyword)
    assert argument == "universo"

def test_handle_search_extracts_argument(command_handler_fixture):
    """Tests that _handle_search correctly extracts the argument for the tool."""
    handler, mock_speak, _ = command_handler_fixture
    
    handler.process("o que é fotossíntese?")

    search_tool_func = handler.router_config[2][2].func
    search_tool_func.assert_called_once_with("fotossíntese?")
    mock_speak.assert_called_once_with("Resultado da Wikipedia.")

def test_extract_argument_exception(command_handler_fixture, mocker):
    """Tests exception handling within _extract_argument."""
    handler, _, _ = command_handler_fixture
    mocker.patch('command_handler.string.punctuation', side_effect=Exception("Unexpected error"))
    
    command = "any command"
    keyword = "any"
    
    argument = handler._extract_argument(command, keyword)
    assert argument == ""