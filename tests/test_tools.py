import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime as dt
import requests
import wikipedia

from stuart_ai.tools import AssistantTools
from stuart_ai.agents.web_search_agent import WebSearchAgent

@pytest.fixture
def assistant_tools_fixture(mocker):
    """
    Fixture to create an instance of AssistantTools with mocked dependencies.
    """
    mock_speak_func = mocker.MagicMock()
    mock_confirm_func = mocker.MagicMock()
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
    
    # Retorna as ferramentas e seus mocks para uso nos testes
    return tools, mock_speak_func, mock_confirm_func, mock_web_search_agent

# Test for _get_time
def test_get_time(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    # Mock datetime.now() para retornar um valor fixo
    fixed_time = dt(2023, 10, 27, 14, 45)
    mock_datetime = mocker.patch('stuart_ai.tools.datetime')
    mock_datetime.now.return_value = fixed_time
    
    result = tools._get_time.func(tools)
    
    assert result == "São 14:45."
    mock_datetime.now.assert_called_once()

# Test for _tell_joke
def test_tell_joke_success(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    # Mock requests.get para simular uma piada de uma linha
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {
        "type": "single",
        "joke": "Qual é o cúmulo da sorte? Ser atropelado por uma ambulância."
    }
    mock_response.raise_for_status.return_value = None # Não levanta exceção
    mock_get = mocker.patch('stuart_ai.tools.requests.get', return_value=mock_response)
    
    result = tools._tell_joke.func(tools)
    assert result == "Qual é o cúmulo da sorte? Ser atropelado por uma ambulância."
    mock_get.assert_called_once()

def test_tell_joke_api_error(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    # Mock requests.get para simular um erro de API
    mocker.patch('stuart_ai.tools.requests.get', side_effect=requests.exceptions.RequestException("API down"))
    
    result = tools._tell_joke.func(tools)
    assert result == "Desculpe, não consegui buscar uma piada agora."

# Test for _search_wikipedia
def test_search_wikipedia_success(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    # Mock wikipedia.summary para retornar um texto fixo
    mock_summary = mocker.patch('stuart_ai.tools.wikipedia.summary', return_value="Python é uma linguagem de programação.")
    mock_set_lang = mocker.patch('stuart_ai.tools.wikipedia.set_lang') # Também mockamos set_lang
    
    result = tools._search_wikipedia.func(tools, "Python")
    
    mock_set_lang.assert_called_once_with("pt")
    mock_summary.assert_called_once_with("Python", sentences=2)
    assert result == "Python é uma linguagem de programação."

def test_search_wikipedia_page_error(assistant_tools_fixture, mocker):
    tools, _, _, _ = assistant_tools_fixture
    
    # Mock wikipedia.summary para levantar PageError
    mocker.patch('stuart_ai.tools.wikipedia.summary', side_effect=wikipedia.exceptions.PageError("page not found"))
    mocker.patch('stuart_ai.tools.wikipedia.set_lang')
    
    result = tools._search_wikipedia.func(tools, "TermoInexistente")
    assert result == "Desculpe, não encontrei nenhum resultado para TermoInexistente."

def test_search_wikipedia_no_term(assistant_tools_fixture):
    tools, _, _, _ = assistant_tools_fixture
    result = tools._search_wikipedia.func(tools, "")
    assert result == "Claro, o que você gostaria que eu pesquisasse?"

# Test for _open_app
@pytest.mark.parametrize("system, app_name, expected_call, expected_kwargs", [
    ("Linux", "firefox", ["firefox"], {}),
    ("Linux", "browser", ["firefox"], {}),
    ("Windows", "chrome", ['start', 'chrome'], {'shell': True}),
    ("Darwin", "safari", ['open', '-a', 'safari'], {})
])
def test_open_app(assistant_tools_fixture, mocker, system, app_name, expected_call, expected_kwargs):
    tools, _, _, _ = assistant_tools_fixture
    
    # Mock das funções do sistema
    mocker.patch('stuart_ai.tools.platform.system', return_value=system)
    mock_popen = mocker.patch('stuart_ai.tools.subprocess.Popen')
    
    result = tools._open_app.func(tools, app_name)
    
    assert result == f"Abrindo {app_name}."
    
    mock_popen.assert_called_once_with(expected_call, **expected_kwargs)

# Test for _shutdown_computer
def test_shutdown_computer_confirmed(assistant_tools_fixture, mocker):
    tools, _, mock_confirm, _ = assistant_tools_fixture
    
    mock_confirm.return_value = True # Simula a confirmação do usuário
    mock_run = mocker.patch('stuart_ai.tools.subprocess.run')
    mocker.patch('stuart_ai.tools.platform.system', return_value="Linux")
    
    result = tools._shutdown_computer.func(tools)
    
    mock_confirm.assert_called_once()
    mock_run.assert_called_once_with(["shutdown", "-h", "+1"])
    assert result == "Ok, desligando o computador em 1 minuto. Adeus!"

def test_shutdown_computer_cancelled(assistant_tools_fixture, mocker):
    tools, _, mock_confirm, _ = assistant_tools_fixture
    
    mock_confirm.return_value = False # Simula o cancelamento do usuário
    mock_run = mocker.patch('stuart_ai.tools.subprocess.run')
    
    result = tools._shutdown_computer.func(tools)
    
    mock_confirm.assert_called_once()
    mock_run.assert_not_called()
    assert result == "Ação de desligamento cancelada."

# Test for _perform_web_search
def test_perform_web_search_success(assistant_tools_fixture):
    tools, mock_speak, _, mock_web_search_agent = assistant_tools_fixture
    
    query = "melhores práticas em Python"
    search_result = "Mantenha seu código limpo e bem documentado."
    mock_web_search_agent.run_search_crew.return_value = search_result
    
    result = tools._perform_web_search.func(tools, query)
    
    mock_speak.assert_called_once_with(f"Ok, pesquisando na web sobre {query}. Isso pode levar um momento.")
    mock_web_search_agent.run_search_crew.assert_called_once_with(query)
    assert result == f"A pesquisa retornou o seguinte: {search_result}"

# Test for _quit
def test_quit(assistant_tools_fixture, mocker):
    tools, mock_speak, _, _ = assistant_tools_fixture
    
    # Mockamos a função exit para que ela não encerre o processo de teste
    mock_exit = mocker.patch('stuart_ai.tools.exit')
    
    tools._quit.func(tools)
    
    mock_speak.assert_called_once_with("Encerrando a assistente. Até logo!")
    mock_exit.assert_called_once_with(0)
