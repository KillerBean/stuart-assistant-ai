import pytest
from pydantic import ValidationError
from stuart_ai.core.config import Settings


def test_default_values():
    """Verifies Settings loads without errors and types are correct."""
    s = Settings()
    assert isinstance(s.assistant_keyword, str)
    assert len(s.assistant_keyword) > 0
    assert isinstance(s.language, str)
    assert isinstance(s.llm_model, str)
    assert isinstance(s.router_model, str)
    assert isinstance(s.whisper_model_size, str)
    assert isinstance(s.memory_window_size, int)
    assert isinstance(s.wake_word_confidence, int)
    assert isinstance(s.phrase_time_limit, int)
    assert isinstance(s.temp_dir, str)


def test_allowed_apps_default_is_list():
    """Verifies allowed_apps is a list with sensible defaults."""
    s = Settings()
    assert isinstance(s.allowed_apps, list)
    assert len(s.allowed_apps) > 0
    assert "firefox" in s.allowed_apps


def test_allowed_apps_blocks_unlisted(monkeypatch):
    """Verifies that allowed_apps can be overridden via env."""
    monkeypatch.setenv("ALLOWED_APPS", '["firefox", "code"]')
    s = Settings()
    assert "firefox" in s.allowed_apps
    assert "code" in s.allowed_apps


def test_keyword_override(monkeypatch):
    """Verifies assistant_keyword can be overridden."""
    monkeypatch.setenv("ASSISTANT_KEYWORD", "jarvis")
    s = Settings()
    assert s.assistant_keyword == "jarvis"


def test_llm_model_override(monkeypatch):
    """Verifies LLM model can be changed via env."""
    monkeypatch.setenv("LLM_MODEL", "llama3:latest")
    s = Settings()
    assert s.llm_model == "llama3:latest"


def test_memory_window_size_override(monkeypatch):
    """Verifies memory_window_size can be overridden."""
    monkeypatch.setenv("MEMORY_WINDOW_SIZE", "20")
    s = Settings()
    assert s.memory_window_size == 20


def test_wake_word_confidence_bounds():
    """Verifies wake_word_confidence is a valid int."""
    s = Settings()
    assert 0 <= s.wake_word_confidence <= 100


def test_llm_temperature_range():
    """Verifies llm_temperature is within valid range."""
    s = Settings()
    assert 0.0 <= s.llm_temperature <= 2.0


def test_api_enabled_default():
    """Verifies API is disabled by default."""
    s = Settings()
    assert s.api_enabled is False


def test_api_port_default():
    """Verifies default API port."""
    s = Settings()
    assert s.api_port == 8000


def test_api_port_override(monkeypatch):
    """Verifies API port can be changed."""
    monkeypatch.setenv("API_PORT", "9000")
    s = Settings()
    assert s.api_port == 9000
