import pytest
from unittest.mock import MagicMock
from stuart_ai.agents.rag.rag_agent import LocalRAGAgent

@pytest.fixture
def rag_agent(mocker):
    mock_llm = MagicMock()
    mock_store = MagicMock()
    return LocalRAGAgent(llm=mock_llm, document_store=mock_store), mock_llm, mock_store

@pytest.mark.asyncio
async def test_run_no_docs(rag_agent):
    agent, mock_llm, mock_store = rag_agent
    
    mock_store.search.return_value = []
    
    result = await agent.run("query")
    
    assert "não encontrei informações relevantes" in result
    mock_llm.call.assert_not_called()

@pytest.mark.asyncio
async def test_run_with_docs(rag_agent):
    agent, mock_llm, mock_store = rag_agent
    
    mock_store.search.return_value = ["Doc 1 content", "Doc 2 content"]
    mock_llm.call.return_value = "Answer based on docs."
    
    result = await agent.run("query")
    
    assert result == "Answer based on docs."
    mock_llm.call.assert_called_once()
    
    # Check prompt content
    args = mock_llm.call.call_args[0][0] # messages list
    prompt = args[0]['content']
    assert "Doc 1 content" in prompt
    assert "Doc 2 content" in prompt
    assert "query" in prompt
