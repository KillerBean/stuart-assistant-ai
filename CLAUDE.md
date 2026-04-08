# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stuart AI is a voice-activated AI assistant for Portuguese (pt-BR) built with Python 3.14+. It runs entirely locally using Ollama for LLM inference and Whisper for speech recognition.

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
├── tools/
│   └── system_tools.py              # AssistantTools (time, calendar, apps, etc.)
└── utils/
    ├── prompt_sanitizer.py          # Shared sanitizer for external content in LLM prompts
    └── tmp_file_handler.py          # Secure temp file lifecycle (mode 0o600)
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
| INDEX_ALLOWED_DIRS | `~/Documents,~/Downloads` | Diretórios permitidos para indexação de arquivos |
| INDEX_ALLOWED_EXTENSIONS | `.txt,.pdf,.md,.docx,.csv` | Extensões permitidas para indexação |
| INDEX_MAX_FILE_SIZE | `52428800` (50 MB) | Tamanho máximo de arquivo para indexação |
| API_ENABLED | `false` | Habilita a REST API de gerenciamento |
| API_PORT | `8000` | Porta da REST API |

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

## Security

### Input Validation
- `handle_command()` rejeita comandos com mais de 500 chars ou com metacaracteres shell (`|`, `;`, `&`, `` ` ``, `$`, `..`, `<script`).
- O schema JSON retornado pelo router LLM é validado antes do dispatch: `tool_name` deve estar no dict de tools conhecido; `args` deve ser str, dict ou None.

### Path Traversal Protection
- `_index_file()` resolve caminhos com `pathlib.Path.resolve()` e verifica `is_relative_to()` contra `INDEX_ALLOWED_DIRS`.
- Arquivos fora dos diretórios permitidos são bloqueados e a tentativa é logada como warning.
- Extensão e tamanho são validados antes de qualquer I/O.

### Prompt Injection Mitigation
- Todo conteúdo externo (resultados de busca web, documentos do ChromaDB) passa por `sanitize_external_content()` de `utils/prompt_sanitizer.py` antes de ser inserido em prompts LLM.
- O comando do usuário é escapado com `json.dumps()` no `SemanticRouter` para prevenir JSON injection.
- Nunca inserir conteúdo de terceiros diretamente em f-strings de prompt sem passar pelo sanitizador.

### Subprocess Security
- Nunca usar `shell=True` em chamadas `subprocess`. Sempre usar lista de argumentos.
- Apps só podem ser abertos se estiverem na whitelist `ALLOWED_APPS` de `config.py`.

### Temp Files
- Diretório `tmp/` criado com `mode=0o700` (apenas owner).
- Arquivos de áudio criados com `mode=0o600` via `os.open()` — não world-readable.

## Requirements

- Python 3.14+ (gerenciado via `uv` — não use pip diretamente)
- Ollama running locally com modelos pulled: `gemma3:latest`, `qwen2.5:0.5b`
- mpg123 para playback de TTS (`apt install mpg123`)
- Working microphone
