# Dependências Diretas

Mapeadas a partir dos imports em `main.py` e `stuart_ai/**/*.py`.
O `requirements.txt` atual tem 252 entradas — tudo o resto é transitivo.

## Produção (19)

| Pacote PyPI | Importado como / de | Arquivo |
|---|---|---|
| `faster-whisper` | `faster_whisper` | `main.py` |
| `SpeechRecognition` | `speech_recognition` | `main.py`, `assistant.py` |
| `aiofiles` | `aiofiles` | `assistant.py` |
| `edge-tts` | `edge_tts` | `assistant.py` |
| `playsound` | `playsound` | `assistant.py` |
| `thefuzz` | `thefuzz` | `assistant.py` |
| `wikipedia` | `wikipedia` | `assistant.py`, `system_tools.py` |
| `aiohttp` | `aiohttp` | `system_tools.py` |
| `coloredlogs` | `coloredlogs` | `logger.py` |
| `pydantic-settings` | `pydantic_settings` | `config.py` |
| `ics` | `ics` | `calendar_manager.py` |
| `dateparser` | `dateparser` | `calendar_manager.py` |
| `langchain-ollama` | `langchain_ollama` | `ollama_llm.py`, `document_store.py` |
| `langchain-core` | `langchain_core` | `ollama_llm.py` |
| `langchain-community` | `langchain_community` | `web_search_agent.py` |
| `langchain-text-splitters` | `langchain_text_splitters` | `document_store.py` |
| `requests` | `requests` | `web_search_agent.py` |
| `chromadb` | `chromadb` | `document_store.py` |
| `pypdf` | `pypdf` | `document_store.py` |

> `duckduckgo-search` é transitivo via `langchain-community` — não precisa ser declarado.

## Dev (4)

| Pacote | Uso |
|---|---|
| `pytest` | testes |
| `pytest-asyncio` | testes async |
| `pytest-cov` | cobertura |
| `pytest-mock` | mocks |
