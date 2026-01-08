import pytest
import json
from unittest.mock import MagicMock, AsyncMock
from stuart_ai.services.semantic_router import SemanticRouter

@pytest.fixture
def semantic_router_fixture(mocker):
    # Mock LLM
    mock_llm = mocker.MagicMock()
    
    router = SemanticRouter(llm=mock_llm)
    return router, mock_llm

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
    
    from stuart_ai.core.exceptions import LLMResponseError
    with pytest.raises(LLMResponseError):
        await router.route("invalid command")

@pytest.mark.asyncio
async def test_route_llm_exception(semantic_router_fixture):
    router, mock_llm = semantic_router_fixture
    
    # Mock exception during LLM call
    mock_llm.call.side_effect = Exception("LLM Error")
    
    from stuart_ai.core.exceptions import LLMConnectionError
    with pytest.raises(LLMConnectionError):
        await router.route("any command")

