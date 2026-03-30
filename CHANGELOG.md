# CHANGELOG

Todas as mudanças notáveis neste projeto estão documentadas neste arquivo.
Formato: [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)

## [Unreleased]

### Changed
- Reorganização de documentação em `docs/roadmap/` e `docs/tasks/`
- NEXT-STEPS movido para `docs/roadmap/next-steps.md` com status atualizado

## [0.6.0] - 2026-03-21 | Security Release

### Security
- **Path traversal bloqueado em `_index_file()`** — Caminhos resolvidos com `pathlib.Path.resolve()` validados contra whitelist de diretórios permitidos (`INDEX_ALLOWED_DIRS`). Extensões e tamanho de arquivo validados antes de qualquer I/O.
- **Prompt injection mitigado em WebSearchAgent e RAGAgent** — Módulo centralizado `utils/prompt_sanitizer.py` sanitiza conteúdo externo (resultados web, documentos ChromaDB) antes de inserção em prompts LLM. Remove padrões de injeção comuns (`[INST]`, `<|im_start|>`, `System:`, etc.).
- **JSON injection no SemanticRouter eliminado** — Comando do usuário escapado com `json.dumps()` antes de interpolação no prompt do router.
- **Validação de input em `handle_command()`** — Comandos rejeitados se > 500 chars ou contêm metacaracteres shell (`|`, `;`, `&`, `` ` ``, `$`, `..`).
- **Schema validation do output router LLM** — `tool_name` desconhecido redireciona para `web_search`; `args` com tipo inválido descartados com warning.
- **Permissões de temp files corrigidas** — Diretório `tmp/` com `mode=0o700`, arquivos de áudio com `mode=0o600` (owner-only).

### Added
- `stuart_ai/utils/prompt_sanitizer.py` — Sanitizador compartilhado para conteúdo externo
- Documentação completa em `docs/` (roadmap, tasks, planning)
- `docs/roadmap/NEXT-STEPS.md` — Roadmap de segurança (Tier 1–6)

### Fixed
- URL encoding em `_get_weather()` com `urllib.parse.quote()`
- Remoção de `shell=True` em chamadas subprocess

### Notes
- Auditoria completa de segurança realizada
- Projeto preparado para análise de código externo

## [0.5.0] - 2026-03-21 | Testing & Documentation

### Added
- Testes unitários para `Settings` e `AssistantContext` com cobertura completa
- Seções de Testing, Structured Logging e Graceful Shutdown em `CLAUDE.md`
- Documentação automática via git hooks
- `docs/` directory para organização de planning docs

### Changed
- Estrutura de documentação centralizada em `docs/`
- Tarefas organizadas em `docs/tasks/TASKS.md`

## [0.4.2] - 2026-03-18 | CI/CD & Agents

### Added
- **GitHub Actions CI/CD** — Pipeline automático (testes, lint, build)
- **ContentAgent** — Resumo de artigos via `trafilatura` e YouTube via `youtube-transcript-api`
- **CodingAgent** — Explicação de stack traces, geração de scripts, análise de código
- **FastAPI Management REST API** — Endpoints `/health`, `/chat`, `/context`
- **AssistantContext** — Rastreamento de estado de sessão (idle/listening/processing/speaking)
- **App Whitelist & Media Controls** — Validação de aplicativos, controle via `playerctl` e `pactl`

### Fixed
- Migração `ics` → `icalendar` para compatibilidade Python 3.14
- Correção de imports e tipagem

### Changed
- Estrutura de projeto com API separada
- Dependências atualizadas para Python 3.14+

## [0.4.0] - 2026-03-10 | Dependency Management

### Added
- **FastAPI REST API** — Interface HTTP para controle do assistente (porta 8000)
- **uv Package Manager** — Migração completa de pip para `uv` (mais rápido, determinístico)

### Changed
- Python versão mínima: 3.14+
- Lockfile atualizado via `uv sync`
- Estrutura de dev dependencies organizada

## [0.3.5] - 2026-03-01 | Session State

### Added
- **AssistantContext** — Rastreamento robusto de estado (`stuart_ai/core/state.py`)
- **App Whitelist** — Segurança para `_open_app()` com lista de aplicativos permitidos

### Fixed
- Correcções de lint (pylint)
- Melhorias de performance em audição e processamento

## [0.3.0] - 2026-02-15 | Semantic Routing & Memory

Major refactoring com arquitetura completamente refeita:

### Added
- **Semantic Router LLM-based** — Classificação inteligente de intenção com modelo leve (`qwen2.5:0.5b`)
- **Conversation Memory** — Memória em janela deslizante (deque-based) para contexto persistente
- **Async I/O First** — Refatoração total para asyncio; chamadas bloqueantes via `asyncio.to_thread()`
- **Dependency Injection** — Padrão DI consistente em todas as classes
- **Custom Exception System** — Exceções customizadas em `stuart_ai/core/exceptions.py`
- **RAG Agent** — Indexação e consulta de documentos locais via ChromaDB
- **Test Suite** — Testes com pytest e pytest-asyncio
- **Logging Estruturado** — Sistema centralizado com coloredlogs
- **Pydantic Settings** — Configuração centralizada via `.env`

### Fixed
- Métodos de cancelamento funcionando corretamente
- Bugs na listagem de eventos do calendário
- Tipagem de argumentos no CommandHandler
- Chamadas síncronas ao LLM tornadas assíncronas

### Changed
- Roteamento: regex → LLM-based semantic routing
- TTS melhorado com suporte a múltiplos modelos
- Arquitetura: procedural → DI + async patterns
- Performance otimizada em audição e processamento

### Notes
- PR #5: Async refactoring e memória de conversação
- Alicerce para agentes especializados

## [0.2.0] - 2026-01-30 | Web & Calendar

### Added
- **Web Search Agent** — Busca via DuckDuckGo com síntese LLM
- **Calendar Management** — Agendamento, consulta e remoção de eventos (`icalendar`)
- **System Tools** — Hora, data, clima (wttr.in), Wikipedia, piadas (JokeAPI), abertura de apps, desligamento com confirmação
- **Tool System** — Arquitetura genérica e extensível
- **Logging Centralizado** — Sistema estruturado
- **Pydantic Settings** — Configuração via `.env`

### Fixed
- Erros de tipagem e imports
- Chamadas síncronas ao LLM

### Changed
- Separação de lógica em arquivos estruturados
- Injeção de dependência em CommandHandler

### Notes
- PR #4: Refatoração de testes e estrutura
- PR #3: Web Search Agent (removeu CrewAI posteriormente)

## [0.1.0] - 2025-12-15 | Initial Release

### Added
- **Core Features**
  - ✅ Ativação por voz com palavra-chave ("stuart")
  - ✅ Reconhecimento de fala offline (Faster Whisper)
  - ✅ Síntese de voz (Edge TTS, pt-BR-AntonioNeural)
  - ✅ Resposta em voz natural

- **System Tools**
  - Hora e data
  - Previsão do tempo
  - Piadas
  - Wikipedia search
  - Abertura de aplicativos
  - Desligamento do computador

- **Infrastructure**
  - Configuração via `.env`
  - Logging estruturado
  - Tool system extensível
  - Tratamento genérico de exceções
  - Suporte a múltiplos modelos Ollama

### Notes
- Suporte completo a português (pt-BR)
- Arquitetura preparada para extensões futuras
- PRs #1 & #2: Setup inicial + comandos de produtividade

---

## Timeline de Desenvolvimento

| Período | Versão | Foco |
|---------|--------|------|
| 2025-12 | v0.1.0 | Setup inicial, core features |
| 2026-01 | v0.2.0 | Web search, calendário |
| 2026-02 | v0.3.0 | Semantic router, async, RAG |
| 2026-03-01 | v0.3.5 | State management |
| 2026-03-10 | v0.4.0 | FastAPI, uv migration |
| 2026-03-18 | v0.4.2 | CI/CD, agents (content/coding) |
| 2026-03-21 | v0.5.0 | Tests, documentação |
| 2026-03-21 | v0.6.0 | Security hardening |

## Dependências Principais

- **Python 3.14+**
- **Ollama** — Inferência local LLM
- **Faster Whisper** — Reconhecimento de fala
- **ChromaDB** — Indexação de documentos (RAG)
- **FastAPI** — REST API
- **Edge TTS** — Síntese de voz
- **DuckDuckGo API** — Busca na web
- **icalendar** — Gerenciamento de calendário
- **uv** — Package manager
