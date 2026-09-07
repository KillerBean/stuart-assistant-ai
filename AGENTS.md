# AGENTS.md

## Commands

```bash
uv sync                      # install deps
uv sync --group dev          # install + dev deps (tests, lint)
uv run python main.py        # run assistant
uv run pytest tests/ -v      # run all tests
uv run pytest tests/test_semantic_router.py -v  # single test file
uv run pylint stuart_ai/     # lint (fail-under=7.0 in CI)
uv run pytest tests/ --cov=stuart_ai --cov-report=html  # coverage
bash update-requirements.sh  # update lockfile
```

CI order: `uv sync --group dev` → `pylint --fail-under=7.0` → `pytest --tb=short`

## Architecture

Entry point: `main.py` — DI wiring, starts `assistant.listen_continuously()` and optionally FastAPI API.

Data flow: mic → Whisper transcribe → wake word (exact/fuzzy "stuart") → SemanticRouter (qwen2.5:0.5b) → JSON `{"tool", "args"}` → CommandHandler → tool → Edge TTS response.

Two models: `gemma3:latest` (main tasks), `qwen2.5:0.5b` (routing). Both via Ollama at `localhost:11434`.

Key dirs:
- `stuart_ai/core/` — assistant orchestrator, config (Pydantic Settings), memory, state, enums, exceptions, logger
- `stuart_ai/services/` — SemanticRouter, CommandHandler
- `stuart_ai/agents/` — web_search, content, coding, rag/, productivity/calendar_manager
- `stuart_ai/tools/` — system_tools (time, date, weather, joke, wikipedia, open_app, shutdown, etc.)
- `stuart_ai/api/` — FastAPI management app

## Testing

- `pyproject.toml`: `asyncio_mode = "auto"`, so no `@pytest.mark.asyncio` needed
- Default addopts: `-p no:warnings --strict-markers --cov=stuart_ai --cov-report=html`
- Use `mocker.patch` (pytest-mock) to isolate Ollama, TTS, mic calls
- Integration tests with real Ollama are slow — mock for unit tests
- `pythonpath = ["."]` in pytest config — imports resolve from repo root

## Configuration

- `.env` file via pydantic-settings (`stuart_ai/core/config.py`)
- `settings` is a module-level singleton — import directly: `from stuart_ai.core.config import settings`
- All env vars are snake_case versions of the config fields (e.g., `ASSISTANT_KEYWORD`, `WHISPER_MODEL_SIZE`)

## Security Constraints

- Never use `shell=True` in subprocess — always arg lists
- Apps must be in `ALLOWED_APPS` whitelist (config.py)
- External content (web search, RAG docs) must pass through sanitizer before LLM prompts
- Commands >500 chars or with shell metachars (`|;&`$..<script`) are rejected
- File indexing: paths resolved with `Path.resolve()`, checked `is_relative_to(INDEX_ALLOWED_DIRS)`
- Temp files: `tmp/` dir mode 0o700, audio files mode 0o600

## Patterns

- Async-first: all I/O uses asyncio, blocking calls wrapped in `asyncio.to_thread()`
- DI via constructor — no global singletons except `settings` and `logger`
- Semantic routing via LLM JSON output, not regex
- `AssistantSignal.QUIT` from command handler breaks the listen loop

## Prerequisites

- Python 3.14+ (managed via uv — do not use pip directly)
- Ollama running with models: `gemma3:latest`, `qwen2.5:0.5b`, `nomic-embed-text`
- `mpg123` for TTS playback on Linux (`apt install mpg123`)
- Working microphone
