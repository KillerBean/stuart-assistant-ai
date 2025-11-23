import pytest
from stuart_ai.LLM.ollama_llm import OllamaLLM
from stuart_ai.agents.web_search_agent import WebSearchAgent, DuckDuckGoSearchTool
from langchain_community.tools import DuckDuckGoSearchRun

@pytest.fixture
def web_search_agent_fixture(mocker):
    """
    Fixture para criar uma instância de WebSearchAgent com dependências mockadas.
    Patches nas classes CrewAI são aplicados para evitar validações Pydantic.
    """
    # Patch nas classes CrewAI onde são importadas/usadas dentro do módulo web_search_agent
    mock_agent_class = mocker.patch('stuart_ai.agents.web_search_agent.Agent')
    mock_task_class = mocker.patch('stuart_ai.agents.web_search_agent.Task')
    mock_crew_class = mocker.patch('stuart_ai.agents.web_search_agent.Crew')

    mock_search_tool = mocker.MagicMock(spec=DuckDuckGoSearchTool)
    mock_llm = mocker.MagicMock(spec=OllamaLLM)
    
    web_agent = WebSearchAgent(search_tool=mock_search_tool, llm=mock_llm)
    
    # Retorna também as classes mockadas para uso nos asserts dos testes
    return web_agent, mock_search_tool, mock_llm, mock_agent_class, mock_task_class, mock_crew_class

def test_init_with_provided_dependencies(web_search_agent_fixture):
    """
    Testa se o __init__ do WebSearchAgent inicializa corretamente as dependências injetadas.
    """
    web_agent, mock_search_tool, mock_llm, _, _, _ = web_search_agent_fixture
    
    assert web_agent.search_tool == mock_search_tool
    assert web_agent.llm == mock_llm

def test_init_with_default_dependencies(mocker):
    """
    Testa se o __init__ do WebSearchAgent inicializa corretamente as dependências padrão.
    """
    # Patch das classes para observar se são instanciadas
    mock_duckduckgo_search_tool_class = mocker.patch('stuart_ai.agents.web_search_agent.DuckDuckGoSearchTool')
    mock_ollama_llm_class = mocker.patch('stuart_ai.agents.web_search_agent.OllamaLLM')

    # Configura o mock para a chamada encadeada: OllamaLLM().get_llm_instance()
    mock_llm_instance = mocker.MagicMock()
    mock_ollama_llm_class.return_value.get_llm_instance.return_value = mock_llm_instance
    
    # Instancia sem passar dependências
    default_web_agent = WebSearchAgent()
    
    # Verifica se as classes foram instanciadas
    mock_duckduckgo_search_tool_class.assert_called_once()
    mock_ollama_llm_class.assert_called_once()
    mock_ollama_llm_class.return_value.get_llm_instance.assert_called_once()

    # Verifica se as instâncias criadas foram atribuídas
    assert default_web_agent.search_tool == mock_duckduckgo_search_tool_class.return_value
    assert default_web_agent.llm == mock_llm_instance

def test_create_web_search_agent(web_search_agent_fixture):
    """
    Testa se create_web_search_agent chama crewai.Agent com os parâmetros corretos.
    """
    web_agent, mock_search_tool, mock_llm, mock_crewai_agent_class, _, _ = web_search_agent_fixture
    
    created_agent = web_agent.create_web_search_agent()
    
    mock_crewai_agent_class.assert_called_once_with(
        role='Pesquisador Web Sênior',
        goal='Encontrar e sintetizar informações relevantes da web sobre um tópico específico.',
        backstory='É um pesquisador experiente, especialista em encontrar e analisar rapidamente informações online para fornecer insights concisos e precisos.',
        verbose=True,
        allow_delegation=False,
        tools=[mock_search_tool],
        llm=mock_llm
    )
    assert created_agent == mock_crewai_agent_class.return_value # Verifica se retornou a instância do mock

def test_create_web_search_task(web_search_agent_fixture, mocker):
    """
    Testa se create_web_search_task chama crewai.Task com os parâmetros corretos.
    """
    web_agent, _, _, _, mock_crewai_task_class, _ = web_search_agent_fixture
    
    mock_agent_instance = mocker.MagicMock() # Mock de uma instância de agente
    query = "test query"
    
    created_task = web_agent.create_web_search_task(mock_agent_instance, query)
    
    mock_crewai_task_class.assert_called_once_with(
        description=f"Pesquise a web por '{query}' e forneça um resumo conciso das informações mais importantes.",
        expected_output='Um resumo conciso e preciso das informações encontradas na web sobre o tópico da pesquisa.',
        agent=mock_agent_instance
    )
    assert created_task == mock_crewai_task_class.return_value # Verifica se retornou a instância do mock

def test_run_search_crew(web_search_agent_fixture, mocker):
    """
    Testa o método run_search_crew para verificar a orquestração correta.
    """
    web_agent, _, _, _, _, mock_crewai_crew_class = web_search_agent_fixture
    
    mock_created_agent = mocker.MagicMock()
    mock_created_task = mocker.MagicMock()
    
    # Mocka os métodos internos que criam agente e tarefa
    mocker.patch.object(web_agent, 'create_web_search_agent', return_value=mock_created_agent)
    mocker.patch.object(web_agent, 'create_web_search_task', return_value=mock_created_task)
    
    mock_crew_instance = mock_crewai_crew_class.return_value
    mock_crew_instance.kickoff.return_value = "Resultado da pesquisa do Crew"
    
    query = "query de teste"
    result = web_agent.run_search_crew(query)
    
    web_agent.create_web_search_agent.assert_called_once()
    web_agent.create_web_search_task.assert_called_once_with(mock_created_agent, query)
    
    mock_crewai_crew_class.assert_called_once_with(
        agents=[mock_created_agent],
        tasks=[mock_created_task],
        verbose=True
    )
    mock_crew_instance.kickoff.assert_called_once()
    assert result == "Resultado da pesquisa do Crew"

def test_duckduckgo_search_tool_run(mocker):
    """
    Testa o método _run da DuckDuckGoSearchTool para verificar a integração com DuckDuckGoSearchRun.
    """
    # Mock da classe DuckDuckGoSearchRun
    mock_duckduckgo_search_run_class = mocker.patch('stuart_ai.agents.web_search_agent.DuckDuckGoSearchRun')
    
    # Configura o retorno do método run da instância mockada
    expected_result = "Resultado da pesquisa DuckDuckGo"
    mock_duckduckgo_search_run_class.return_value.run.return_value = expected_result
    
    # Instancia a DuckDuckGoSearchTool
    tool = DuckDuckGoSearchTool()
    
    # Define a query
    query = "test query for duckduckgo"
    
    # Chama o método _run
    result = tool._run(query)
    
    # Verifica se DuckDuckGoSearchRun foi instanciado
    mock_duckduckgo_search_run_class.assert_called_once()
    
    # Verifica se o método run da instância foi chamado com a query correta
    mock_duckduckgo_search_run_class.return_value.run.assert_called_once_with(query)
    
    # Verifica se o resultado retornado é o esperado
    assert result == expected_result

from stuart_ai.agents.web_search_agent import main as web_search_main

def test_main(mocker):
    """
    Testa a função main (ponto de entrada do script) para verificar a orquestração correta.
    """
    # Mock de argparse para simular argumentos de linha de comando
    test_query = "qual a capital da França"
    mock_args = mocker.MagicMock()
    mock_args.query = test_query
    mock_argparse = mocker.patch('argparse.ArgumentParser')
    mock_argparse.return_value.parse_args.return_value = mock_args

    # Mock das dependências externas
    mock_llm_instance = mocker.MagicMock()
    mock_ollama_llm_class = mocker.patch('stuart_ai.agents.web_search_agent.OllamaLLM')
    mock_ollama_llm_class.return_value.get_llm_instance.return_value = mock_llm_instance

    mock_web_search_agent_class = mocker.patch('stuart_ai.agents.web_search_agent.WebSearchAgent')
    mock_agent_instance = mocker.MagicMock()
    search_result = "Paris"
    mock_agent_instance.run_search_crew.return_value = search_result
    mock_web_search_agent_class.return_value = mock_agent_instance

    # Mock do print para capturar saídas
    mock_print = mocker.patch('builtins.print')

    # Chama a função main
    web_search_main()

    # Asserções
    # Verifica se o parser de argumentos foi configurado corretamente
    mock_argparse.assert_called_once_with(description="Executa uma pesquisa na web usando o WebSearchAgent.")
    mock_argparse.return_value.add_argument.assert_called_once_with("query", type=str, help="O texto a ser pesquisado.")
    mock_argparse.return_value.parse_args.assert_called_once()

    # Verifica se o LLM foi instanciado
    mock_ollama_llm_class.assert_called_once()
    mock_ollama_llm_class.return_value.get_llm_instance.assert_called_once()

    # Verifica se o WebSearchAgent foi instanciado com o LLM correto
    mock_web_search_agent_class.assert_called_once_with(llm=mock_llm_instance)

    # Verifica se a busca foi executada com a query correta
    mock_agent_instance.run_search_crew.assert_called_once_with(test_query)

    # Verifica se os prints foram chamados com as mensagens esperadas
    assert mock_print.call_count == 3
    mock_print.assert_any_call(f"Iniciando pesquisa para: '{test_query}'")
    mock_print.assert_any_call("\n--- Resultado da Pesquisa ---")
    mock_print.assert_any_call(search_result)
