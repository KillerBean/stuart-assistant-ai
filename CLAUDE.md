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

## Requirements

- Python 3.12+
- Ollama running locally with models pulled
- mpg123 for TTS audio playback
- Working microphone
