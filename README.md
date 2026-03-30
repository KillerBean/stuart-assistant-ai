# Stuart AI

Assistente de voz pessoal em português (pt-BR), executado inteiramente de forma local. Usa Ollama para inferência de LLM e Faster Whisper para reconhecimento de fala.

## Funcionalidades

- **Ativação por voz** — palavra-chave configurável (padrão: "stuart"), com correspondência exata e fuzzy
- **Reconhecimento de fala offline** — Faster Whisper (modelo configurável: tiny, base, small, medium, large)
- **Síntese de voz** — Edge TTS com voz `pt-BR-AntonioNeural`
- **Roteamento híbrido** — Regex para comandos de sistema + SemanticRouter (LLM) para intenções complexas
- **Memória de conversação** — janela deslizante de contexto (deque-based)
- **Busca na web** — DuckDuckGo com síntese via LLM
- **RAG local** — indexação e consulta de documentos via ChromaDB
- **Calendário local** — agendamento, consulta e remoção de eventos (icalendar)
- **Ferramentas do sistema** — hora, data, clima, Wikipedia, piadas, abertura de apps, desligamento
- **Agents especializados** — ContentAgent e CodingAgent para análise de conteúdo e assistência de programação
- **REST API** — FastAPI para controle e integração do assistente
- **Rastreamento de estado** — AssistantContext para gerência de sessão
- **Segurança** — App whitelist e controles de mídia

## Arquitetura

```
Fala do usuário
    → Whisper (transcrição)
    → Detecção da palavra-chave (exato / fuzzy)
    → SemanticRouter (qwen2.5:0.5b) → {"tool": "...", "args": ...}
    → CommandHandler → Tool correspondente
    → Edge TTS (resposta falada)
```

### Estratégia de dois modelos

| Modelo | Papel | Padrão |
|--------|-------|---------|
| Main LLM | RAG, busca web, chat | `gemma3:latest` |
| Router LLM | Classificação rápida de intenção | `qwen2.5:0.5b` |

### Estrutura de arquivos

```
main.py                              # Ponto de entrada, wiring de dependências
stuart_ai/
├── api/
│   └── app.py                       # FastAPI management API
├── core/
│   ├── assistant.py                 # Orquestrador principal, loop de escuta
│   ├── config.py                    # Configurações via Pydantic Settings
│   ├── memory.py                    # ConversationMemory (deque)
│   ├── state.py                     # AssistantContext para rastreamento de estado
│   ├── enums.py                     # AssistantSignal
│   ├── exceptions.py                # Exceções customizadas
│   └── logger.py                    # Logging estruturado
├── llm/
│   └── ollama_llm.py                # Wrapper ChatOllama
├── services/
│   ├── semantic_router.py           # Classificador de intenção via LLM
│   └── command_handler.py           # Roteamento e execução de ferramentas
├── agents/
│   ├── web_search_agent.py          # DuckDuckGo + síntese LLM
│   ├── content_agent.py             # Análise de conteúdo
│   ├── coding_agent.py              # Assistência de programação
│   ├── rag/
│   │   ├── document_store.py        # Wrapper ChromaDB
│   │   └── rag_agent.py             # Recuperação de documentos locais
│   └── productivity/
│       └── calendar_manager.py      # Gerenciamento de calendário (icalendar)
├── tools/
│   └── system_tools.py              # AssistantTools (hora, clima, apps, etc.)
└── utils/
    ├── audio_utils.py               # Utilitários de áudio
    └── tmp_file_handler.py          # Gerenciamento de arquivos temporários
```

## Ferramentas disponíveis

| Tool | Descrição |
|------|-----------|
| `time` | Hora atual |
| `date` | Data atual |
| `weather` | Previsão do tempo por cidade |
| `joke` | Piada aleatória em pt-BR (JokeAPI) |
| `wikipedia` | Resumo da Wikipedia |
| `web_search` | Busca na web via DuckDuckGo + LLM |
| `search_local_files` | Consulta em documentos indexados (RAG) |
| `index_file` | Indexa um arquivo local no ChromaDB |
| `add_event` | Agenda um evento no calendário |
| `check_calendar` | Consulta eventos do calendário |
| `delete_event` | Remove um evento do calendário |
| `open_app` | Abre um aplicativo do sistema |
| `shutdown_computer` | Desliga o computador (com confirmação) |
| `cancel_shutdown` | Cancela desligamento agendado |
| `quit` | Encerra o assistente |

## Pré-requisitos

- Python 3.12+
- [Ollama](https://ollama.ai) rodando localmente com os modelos baixados:
  ```bash
  ollama pull gemma3
  ollama pull qwen2.5:0.5b
  ollama pull nomic-embed-text
  ```
- `mpg123` para reprodução de áudio no Linux:
  ```bash
  sudo apt install mpg123
  ```
- Microfone funcional

## Instalação

```bash
git clone <repo-url>
cd stuart-ai

# Instalar dependências com uv
uv sync

# Copiar e configurar .env
cp .env.example .env
# Edite .env conforme necessário
```

## Configuração

Crie um arquivo `.env` na raiz do projeto. Todas as variáveis são opcionais (valores padrão abaixo):

```env
ASSISTANT_KEYWORD=stuart
LANGUAGE=pt

# Microfone
MIC_ENERGY_THRESHOLD=4000
MIC_DYNAMIC_ENERGY_THRESHOLD=true
WAKE_WORD_CONFIDENCE=70
PHRASE_TIME_LIMIT=10

# Whisper
WHISPER_MODEL_SIZE=small

# Ollama
LLM_HOST=localhost
LLM_PORT=11434
LLM_MODEL=gemma3:latest
ROUTER_MODEL=qwen2.5:0.5b
LLM_TEMPERATURE=0.7
EMBEDDING_MODEL=nomic-embed-text

# Memória
MEMORY_WINDOW_SIZE=10

# Arquivos
TEMP_DIR=tmp
```

## Uso

```bash
# Modo interativo (voz)
uv run python main.py
```

Após a inicialização, diga **"Stuart"** seguido do comando desejado.

**Exemplos:**
- _"Stuart, que horas são?"_
- _"Stuart, pesquise sobre computação quântica"_
- _"Stuart, como está o tempo em São Paulo?"_
- _"Stuart, agende reunião de equipe amanhã às 14h"_
- _"Stuart, abra o navegador"_
- _"Stuart, leia o arquivo /home/usuario/relatorio.pdf"_

## REST API

A API FastAPI está disponível (porta padrão: 8000):

```bash
# Iniciar com API habilitada
API_ENABLED=true uv run python main.py
```

**Endpoints principais:**
- `GET /health` — Status da API
- `POST /chat` — Enviar mensagem de texto para processamento
- `GET /context` — Obter contexto atual da sessão
- `GET /logs` — Ver logs estruturados (se disponível)

## Desenvolvimento

```bash
# Instalar dependências
uv sync

# Instalar com dev dependencies (testes, lint)
uv sync --group dev

# Executar todos os testes
uv run pytest tests/ -v

# Executar teste específico
uv run pytest tests/test_semantic_router.py -v

# Lint com pylint
uv run pylint stuart_ai/

# Cobertura de testes
uv run pytest tests/ --cov=stuart_ai --cov-report=html

# Atualizar lockfile
bash update-requirements.sh
```

## Padrões de Código

- **Async-first**: Todo I/O usa `asyncio`; chamadas bloqueantes via `asyncio.to_thread()`
- **Injeção de dependência**: Serviços passados via construtor
- **Roteamento semântico**: Classificação de intenção via LLM em vez de regex
- **Sanitização de conteúdo**: Conteúdo externo (web, RAG) sanitizado antes de prompts LLM

## Documentação Adicional

- **[CHANGELOG.md](CHANGELOG.md)** — Histórico completo de versões
- **[CLAUDE.md](CLAUDE.md)** — Instruções para Claude Code
- **[docs/roadmap/NEXT-STEPS.md](docs/roadmap/NEXT-STEPS.md)** — Roadmap de segurança (Tier 1–6)
- **[docs/tasks/TASKS.md](docs/tasks/TASKS.md)** — Checklist de implementações
