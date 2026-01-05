import pytest
from unittest.mock import MagicMock
from stuart_ai.agents.web_search_agent import WebSearchAgent

@pytest.fixture
def web_search_agent_fixture(mocker):
    mock_llm = mocker.MagicMock()
    mock_llm.call.return_value = "Resumo da pesquisa."
    
    agent = WebSearchAgent(llm=mock_llm)
    
    # Mock the internal search tool
    agent.search_tool = mocker.MagicMock()
    agent.search_tool.run.return_value = "Conteúdo cru da busca."
    
    return agent, mock_llm

def test_web_search_run_success(web_search_agent_fixture):
    agent, mock_llm = web_search_agent_fixture
    
    result = agent.run("python tutorial")
    
    # Verify search was called
    agent.search_tool.run.assert_called_once_with("python tutorial")
    
    # Verify LLM was called
    mock_llm.call.assert_called_once()
    args = mock_llm.call.call_args[0][0] # Get messages list
    assert "python tutorial" in args[0]['content']
    assert "Conteúdo cru da busca" in args[0]['content']
    
    assert result == "Resumo da pesquisa."

def test_web_search_run_exception(web_search_agent_fixture):
    agent, mock_llm = web_search_agent_fixture
    
    # Simulate search error
    agent.search_tool.run.side_effect = Exception("Network Error")
    
    result = agent.run("fail query")
    
    assert "encontrei um erro" in result
    assert "Network Error" in result
    mock_llm.call.assert_not_called()