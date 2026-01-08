import pytest
from unittest.mock import MagicMock
from stuart_ai.llm.ollama_llm import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

@pytest.fixture
def mock_chat_ollama(mocker):
    return mocker.patch('stuart_ai.llm.ollama_llm.ChatOllama')

def test_init_defaults(mock_chat_ollama, mocker):
    mocker.patch('stuart_ai.llm.ollama_llm.settings.llm_host', 'localhost')
    mocker.patch('stuart_ai.llm.ollama_llm.settings.llm_port', 11434)
    mocker.patch('stuart_ai.llm.ollama_llm.settings.llm_model', 'mistral')
    
    llm = OllamaLLM()
    
    mock_chat_ollama.assert_called_with(
        base_url="http://localhost:11434",
        model="mistral",
        temperature=0.7 # assuming default in config or None handling?
        # In code: temperature=self.temperature if self.temperature else settings.llm_temperature
    )

def test_init_overrides(mock_chat_ollama):
    llm = OllamaLLM(host="remote", port=8080, model="llama3", temperature=0.1)
    
    mock_chat_ollama.assert_called_with(
        base_url="http://remote:8080",
        model="llama3",
        temperature=0.1
    )

def test_get_llm_instance(mock_chat_ollama):
    llm = OllamaLLM()
    assert llm.get_llm_instance() == llm

def test_call_conversion(mock_chat_ollama):
    llm = OllamaLLM()
    mock_instance = mock_chat_ollama.return_value
    mock_instance.invoke.return_value.content = "Response"
    
    messages = [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "User prompt"},
        {"role": "assistant", "content": "Assistant prev"},
        {"role": "user", "content": "User prompt 2"}
    ]
    
    result = llm.call(messages)
    
    assert result == "Response"
    
    # Check conversion
    called_messages = mock_instance.invoke.call_args[0][0]
    assert len(called_messages) == 4
    assert isinstance(called_messages[0], SystemMessage)
    assert isinstance(called_messages[1], HumanMessage)
    assert isinstance(called_messages[2], AIMessage)
    assert isinstance(called_messages[3], HumanMessage)
    assert called_messages[0].content == "System prompt"
