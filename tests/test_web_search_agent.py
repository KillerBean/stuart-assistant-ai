import pytest
from langchain_core.language_models import BaseLanguageModel
from langchain_community.tools import DuckDuckGoSearchRun
from stuart_ai.agents.web_search_agent import WebSearchAgent

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

    mock_llm = mocker.MagicMock(spec=BaseLanguageModel)
    mock_search_tool = mocker.MagicMock(spec=DuckDuckGoSearchRun)
    
    web_agent = WebSearchAgent(llm=mock_llm, search_tool=mock_search_tool)
    
    # Retorna também as classes mockadas para uso nos asserts dos testes
    return web_agent, mock_llm, mock_search_tool, mock_agent_class, mock_task_class, mock_crew_class

def test_init(web_search_agent_fixture, mocker):
    """
    Testa se o __init__ do WebSearchAgent inicializa corretamente o llm e o search_tool.
    """
    web_agent, mock_llm, mock_search_tool, _, _, _ = web_search_agent_fixture
    
    assert web_agent.llm == mock_llm
    assert web_agent.search_tool == mock_search_tool

    # Testa o caso padrão para search_tool
    # Aqui, patchamos DuckDuckGoSearchRun localmente para testar seu comportamento padrão.
    mock_duckduckgo_search_run = mocker.patch('stuart_ai.agents.web_search_agent.DuckDuckGoSearchRun')
    default_web_agent = WebSearchAgent(llm=mock_llm)
    assert default_web_agent.search_tool == mock_duckduckgo_search_run.return_value
    mock_duckduckgo_search_run.assert_called_once()


def test_create_web_search_agent(web_search_agent_fixture):
    """
    Testa se create_web_search_agent chama crewai.Agent com os parâmetros corretos.
    """
    web_agent, mock_llm, mock_search_tool, mock_crewai_agent_class, _, _ = web_search_agent_fixture
    
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
