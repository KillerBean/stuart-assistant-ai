import pytest
import json
from unittest.mock import MagicMock, AsyncMock
from stuart_ai.services.semantic_router import SemanticRouter

@pytest.fixture
def semantic_router_fixture(mocker):
    # Mock OllamaLLM
    mock_llm_class = mocker.patch("stuart_ai.services.semantic_router.OllamaLLM")
    mock_llm_instance = mock_llm_class.return_value.get_llm_instance.return_value
    
    router = SemanticRouter()
    return router, mock_llm_instance

@pytest.mark.asyncio
async def test_route_success(semantic_router_fixture):
    router, mock_llm = semantic_router_fixture
    
    # Mock successful JSON response
    mock_response = '{"tool": "weather", "args": "London"}'
    mock_llm.call.return_value = mock_response
    
    result = await router.route("weather in London")
    
    assert result == {"tool": "weather", "args": "London"}
    mock_llm.call.assert_called_once()

@pytest.mark.asyncio
async def test_route_with_markdown_json(semantic_router_fixture):
    router, mock_llm = semantic_router_fixture
    
    # Mock response wrapped in markdown code blocks
    mock_response = '```json\n{"tool": "time", "args": null}\n```'
    mock_llm.call.return_value = mock_response
    
    result = await router.route("what time is it")
    
    assert result == {"tool": "time", "args": None}

@pytest.mark.asyncio
async def test_route_json_decode_error(semantic_router_fixture):
    router, mock_llm = semantic_router_fixture
    
    # Mock invalid JSON
    mock_response = 'Not a JSON'
    mock_llm.call.return_value = mock_response
    
    result = await router.route("invalid command")
    
    # Should fallback to web_search
    assert result == {"tool": "web_search", "args": "invalid command"}

@pytest.mark.asyncio
async def test_route_llm_exception(semantic_router_fixture):
    router, mock_llm = semantic_router_fixture
    
    # Mock exception during LLM call
    mock_llm.call.side_effect = Exception("LLM Error")
    
    result = await router.route("any command")
    
    # Should fallback to general_chat on generic error
    assert result == {"tool": "general_chat", "args": None}

