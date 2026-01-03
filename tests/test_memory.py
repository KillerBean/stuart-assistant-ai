import pytest
from stuart_ai.core.memory import ConversationMemory
from stuart_ai.core.config import settings

def test_add_user_message():
    memory = ConversationMemory()
    memory.add_user_message("Hello")
    assert len(memory.history) == 1
    assert memory.history[0] == {"role": "user", "content": "Hello"}

def test_add_assistant_message():
    memory = ConversationMemory()
    memory.add_assistant_message("Hi there")
    assert len(memory.history) == 1
    assert memory.history[0] == {"role": "assistant", "content": "Hi there"}

def test_memory_limit(mocker):
    # Patch settings to have a small window size
    mocker.patch.object(settings, 'memory_window_size', 2)
    
    memory = ConversationMemory()
    memory.add_user_message("1")
    memory.add_assistant_message("2")
    memory.add_user_message("3")
    
    assert len(memory.history) == 2
    # Should contain "2" and "3"
    assert memory.history[0]["content"] == "2"
    assert memory.history[1]["content"] == "3"

def test_get_formatted_history():
    memory = ConversationMemory()
    memory.add_user_message("Hello")
    memory.add_assistant_message("Hi")
    
    history_str = memory.get_formatted_history()
    
    assert "Usuário: Hello" in history_str
    assert "Stuart: Hi" in history_str

def test_clear_memory():
    memory = ConversationMemory()
    memory.add_user_message("Hello")
    memory.clear()
    assert len(memory.history) == 0

def test_get_history_returns_list():
    memory = ConversationMemory()
    memory.add_user_message("Test")
    hist_list = memory.get_history()
    assert isinstance(hist_list, list)
    assert len(hist_list) == 1
