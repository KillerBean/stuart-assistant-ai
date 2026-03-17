# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stuart AI is a voice-activated AI assistant for Portuguese (pt-BR) built with Python 3.12+. It runs entirely locally using Ollama for LLM inference and Whisper for speech recognition.

## Commands

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --group dev

# Run the assistant
uv run python main.py

# Run tests with coverage
uv run pytest tests/

# Run a single test file
uv run pytest tests/test_semantic_router.py

# Run tests with verbose output
uv run pytest tests/ -v

# Lint
uv run pylint stuart_ai/

# Update lockfile
bash update-requirements.sh
```

## Architecture

**Data Flow:**
1. User speaks → Whisper transcribes to Portuguese text
2. Wake word detection ("stuart") via exact/fuzzy matching
3. SemanticRouter (lightweight LLM) analyzes intent → returns JSON `{"tool": "...", "args": ...}`
4. CommandHandler executes the corresponding tool
5. Response spoken via Edge TTS

**Two-Model Strategy:**
- Main LLM (`gemma3:latest`): Complex tasks (RAG, chat, search synthesis)
- Router LLM (`qwen2.5:0.5b`): Fast intent classification

**Key Components:**

```
main.py                              # Entry point, DI wiring
stuart_ai/
├── core/
│   ├── assistant.py                 # Main orchestrator, async listen loop
│   ├── config.py                    # Pydantic settings (Settings class)
│   └── memory.py                    # ConversationMemory (deque-based)
├── llm/
│   └── ollama_llm.py                # ChatOllama wrapper
├── services/
│   ├── semantic_router.py           # LLM-based intent classifier
│   └── command_handler.py           # Routes intents to tools
├── agents/
│   ├── web_search_agent.py          # DuckDuckGo + LLM synthesis
│   └── rag/
│       ├── document_store.py        # ChromaDB wrapper
│       └── rag_agent.py             # Local document retrieval
└── tools/
    └── system_tools.py              # AssistantTools (time, calendar, apps, etc.)
```

**Patterns:**
- Async-first: All I/O uses `asyncio`, blocking calls wrapped in `asyncio.to_thread()`
- Dependency injection: All services passed via constructor
- Semantic routing: LLM-based intent detection instead of regex

## Configuration

Configuration via `.env` file (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| ASSISTANT_KEYWORD | stuart | Wake word |
| MODEL | gemma3:latest | Main LLM model |
| ROUTER_MODEL | qwen2.5:0.5b | Fast routing LLM |
| OLLAMA_API_BASE | http://localhost:11434 | Ollama endpoint |

All settings in `stuart_ai/core/config.py` can be overridden via environment variables.

## Testing

| Nível | O que testa | Mocks | Ferramentas |
|-------|-------------|-------|-------------|
| **Unit — lógica pura** | Parsers, formatters, utilitários | ❌ | pytest |
| **Unit — serviços** | SemanticRouter, CommandHandler, agents | ✅ mock de Ollama, TTS | pytest-mock |
| **Integration** | Fluxo completo com Ollama real (lento) | ❌ | pytest-asyncio |

```bash
uv run pytest tests/ -v --cov=stuart_ai --cov-report=html
```

Mocks: use `pytest-mock` (`mocker.patch`) para isolar chamadas ao Ollama e ao microfone.
Testes async: decorar com `@pytest.mark.asyncio`.

## Structured Logging

Use o `logging` padrão do Python com formatação estruturada:
```python
import logging
logging.basicConfig(
    format='{"time":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","msg":"%(message)s"}',
    level=logging.INFO
)
```
Logar: intent detectada, tool chamada, tempo de resposta do LLM, erros de speech recognition.
Nunca logar o texto completo reconhecido (pode conter PII).

## Graceful Shutdown

O `asyncio` event loop em `main.py` deve capturar `SIGTERM` e `SIGINT`:
```python
import signal, asyncio

async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    # ... inicia assistant ...
    await stop
    await assistant.shutdown()  # fecha conexões Ollama, ChromaDB, TTS
```

## Requirements

- Python 3.12+ (gerenciado via `uv` — não use pip diretamente)
- Ollama running locally com modelos pulled: `gemma3:latest`, `qwen2.5:0.5b`
- mpg123 para playback de TTS (`apt install mpg123`)
- Working microphone
