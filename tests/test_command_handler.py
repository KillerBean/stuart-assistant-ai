import pytest
from unittest.mock import patch
from command_handler import CommandHandler
from stuart_ai.tools import AssistantTools
from stuart_ai.agents.web_search_agent import WebSearchAgent

@pytest.fixture
def command_handler_fixture(mocker):
    """
    Fixture para criar uma instância de CommandHandler com dependências mockadas.
    Crucialmente, ele também aplica um patch nas classes Agent e Task do CrewAI
    para evitar erros de validação do Pydantic durante a inicialização do CommandHandler.
    """
    # Patch nas classes onde são importadas/usadas, para que o construtor do CommandHandler use mocks
    mocker.patch('command_handler.Agent')
    mocker.patch('command_handler.Task')

    mock_speak_func = mocker.MagicMock()
    mock_confirm_func = mocker.MagicMock()
    mock_llm = mocker.MagicMock()
    
    mock_assistant_tools = mocker.MagicMock(spec=AssistantTools)
    mock_assistant_tools._get_time = mocker.MagicMock()
    mock_assistant_tools._tell_joke = mocker.MagicMock()
    mock_assistant_tools._search_wikipedia = mocker.MagicMock()
    mock_assistant_tools._get_weather = mocker.MagicMock()
    mock_assistant_tools._open_app = mocker.MagicMock()
    mock_assistant_tools._shutdown_computer = mocker.MagicMock()
    mock_assistant_tools._cancel_shutdown = mocker.MagicMock()
    mock_assistant_tools._perform_web_search = mocker.MagicMock()
    mock_assistant_tools._quit = mocker.MagicMock()

    mock_web_search_agent = mocker.MagicMock(spec=WebSearchAgent)
    app_aliases = {}

    # Agora, quando CommandHandler() é chamado, ele usa as versões mockadas de Agent e Task
    handler = CommandHandler(
        speak_func=mock_speak_func,
        confirmation_func=mock_confirm_func,
        app_aliases=app_aliases,
        llm=mock_llm,
        assistant_tools=mock_assistant_tools,
        web_search_agent=mock_web_search_agent
    )
    
    return handler, mock_speak_func

def test_process_empty_command(command_handler_fixture):
    """
    Testa se o método process ignora comandos vazios ou com apenas espaços.
    """
    handler, mock_speak = command_handler_fixture
    
    handler.process("")
    handler.process("   ")
    
    mock_speak.assert_not_called()

def test_process_success(mocker, command_handler_fixture):
    """
    Testa o caminho de sucesso do método process.
    """
    handler, mock_speak = command_handler_fixture
    expected_result = "O tempo está ensolarado."
    
    mocker.patch.object(handler, '_execute_crew_task', return_value=expected_result)
    
    handler.process("qual é o tempo?")
    
    handler._execute_crew_task.assert_called_once()
    mock_speak.assert_called_once_with(expected_result)

def test_process_crew_empty_result(mocker, command_handler_fixture):
    """

    Testa o que acontece quando o CrewAI retorna um resultado vazio.
    """
    handler, mock_speak = command_handler_fixture
    
    mocker.patch.object(handler, '_execute_crew_task', return_value="")
    
    handler.process("um comando qualquer")
    
    handler._execute_crew_task.assert_called_once()
    mock_speak.assert_called_once_with("Desculpe, não entendi o comando.")

def test_process_exception_handling(mocker, command_handler_fixture):
    """
    Testa o tratamento de exceções durante o processamento do comando.
    """
    handler, mock_speak = command_handler_fixture
    
    mocker.patch.object(handler, '_execute_crew_task', side_effect=Exception("Erro na API"))
    
    handler.process("um comando que vai falhar")
    
    handler._execute_crew_task.assert_called_once()
    mock_speak.assert_called_once_with("Desculpe, ocorreu um erro ao processar o comando com o agente de IA.")

@patch('command_handler.Crew', autospec=True)
def test_execute_crew_task_calls_crew_kickoff(mock_crew, mocker, command_handler_fixture):
    """
    Testa o método _execute_crew_task para garantir que ele instancia e executa um Crew.
    """
    handler, _ = command_handler_fixture
    
    mock_crew_instance = mock_crew.return_value
    mock_crew_instance.kickoff.return_value = "Resultado do kickoff"
    
    # Usamos mocks simples, já que as classes reais são patcheadas na fixture
    mock_agent = mocker.MagicMock()
    mock_task = mocker.MagicMock()

    result = handler._execute_crew_task(mock_agent, mock_task)
    
    mock_crew.assert_called_once_with(
        agents=[mock_agent],
        tasks=[mock_task],
        verbose=True
    )
    
    mock_crew_instance.kickoff.assert_called_once()
    
    assert result == "Resultado do kickoff"
