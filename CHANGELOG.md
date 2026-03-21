# CHANGELOG

Todas as mudanças notáveis neste projeto estão documentadas neste arquivo.
Formato: [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)

## [Unreleased]

## [0.5.0] - 2026-03-21

### Added
- Testes unitários para Settings e AssistantContext com cobertura completa
- Seções de Testing, Structured Logging e Graceful Shutdown na documentação (CLAUDE.md)
- Tarefas estruturadas para logging e shutdown gracioso (TASKS.md)
- Checklist de tarefas para rastreamento de progresso

### Fixed
- Atualização de testes para comportamento correto de whitelist
- Alvo de mocks corrigidos em testes de whitelist
- Comportamento de whitelist validado nos testes

### Changed
- Documentação automática atualizada via git hook

## [0.4.2] - 2026-03-18

### Added
- **GitHub Actions CI/CD** — Pipeline automático para testes, build e validação
- **ContentAgent & CodingAgent** — Agentes especializados para análise de conteúdo e assistência de programação
- **FastAPI Management REST API** — Endpoints para controle remoto do assistente (`/health`, `/chat`, `/context`)
- **AssistantContext** — Sistema de rastreamento de estado de sessão
- **App Whitelist & Media Controls** — Segurança aprimorada para execução de aplicativos

### Fixed
- Migração de `ics` para `icalendar` para compatibilidade com Python 3.14
- Dependências resolvidas para Python 3.14

### Changed
- Melhor estrutura de projeto com API separada

## [0.4.0] - 2026-03-10

### Added
- **FastAPI REST API** — Interface HTTP para controle do assistente
- **ContentAgent** — Análise inteligente de conteúdo
- **CodingAgent** — Assistência especializada em programação
- **Gerenciamento com uv** — Migração completa de pip para `uv` (Python package manager)

### Changed
- Python versão mínima elevada para 3.14
- Migração de `icalendar` para melhor compatibilidade

## [0.3.5] - 2026-03-01

### Added
- **AssistantContext** — Rastreamento robusto de estado de sessão
- **App Whitelist** — Controle de segurança para aplicativos
- **Signal Handlers** — Suporte para SIGTERM/SIGINT

### Fixed
- Correcções de lint (pylint)
- Melhorias de performance na audição

### Changed
- Refinamentos na estrutura de projeto

## [0.3.0] - 2026-02-15

### Added
- **Semantic Router LLM-based** — Classificação inteligente de intenção com modelo leve (qwen2.5:0.5b)
- **Conversation Memory** — Memória em janela deslizante (deque) para contexto persistente
- **Async I/O Completo** — Refatoração total para asyncio com `asyncio.to_thread()`
- **Dependency Injection** — Padrão DI em todas as classes
- **Custom Exception System** — Sistema robusto de exceções customizadas
- **RAG Agent** — Indexação e consulta de documentos locais via ChromaDB
- **Test Suite Inicial** — Testes com pytest e pytest-asyncio
- **Logging Estruturado** — Sistema de logging centralizado
- **Configuração Centralizada** — Pydantic Settings com `.env`

### Fixed
- Métodos cancelados funcionando corretamente
- Bugs na listagem de eventos do calendário
- Tipagem de argumentos no CommandHandler
- Chamadas síncronas ao LLM tornadas assíncronas

### Changed
- Roteamento migrado de regex para LLM-based semantic routing
- TTS melhorado com suporte a múltiplos modelos
- Arquitetura refatorada para padrão de injeção de dependência
- Performance otimizada na audição e processamento

## [0.2.0] - 2026-01-30

### Added
- **Web Search Agent** — Busca na web via DuckDuckGo com síntese LLM
- **Calendar Management** — Agendamento, consulta e remoção de eventos (icalendar)
- **System Tools** — Hora, data, clima, Wikipedia, piadas, abertura de apps
- **Shutdown Command** — Desligamento do computador com confirmação
- **Tool System** — Arquitetura genérica e extensível de ferramentas
- **Logging Centralizado** — Sistema de log estruturado
- **Configuração via .env** — Suporte a Pydantic Settings

### Fixed
- Erros de tipagem e imports
- Chamadas síncronas ao LLM

### Changed
- Separação em arquivos estruturados
- Injeção de dependência em CommandHandler

## [0.1.0] - 2025-12-15

### Added
- **Core Features**
  - Ativação por voz com palavra-chave configurável ("stuart")
  - Reconhecimento de fala offline com Faster Whisper
  - Síntese de voz com Edge TTS (pt-BR-AntonioNeural)
  - Resposta em voz natural
  - Roteamento de comandos via regex

- **System Tools**
  - Hora e data
  - Previsão do tempo (API externa)
  - Piadas (JokeAPI)
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
- Primeiro release com funcionalidades básicas
- Suporte completo a português (pt-BR)
- Arquitetura preparada para extensões futuras

---

## Histórico de Mudanças Importantes

### Major Refactorings
- **#6 (2026-02)**: Melhorias gerais e otimizações
- **#5 (2026-02)**: Async refactoring e memória de conversação
- **#4 (2026-01)**: Refatoração de testes e estrutura
- **#3 (2026-01)**: Web Search Agent (removeu CrewAI depois)
- **#2 (2025-12)**: Comandos e ferramentas de produtividade
- **#1 (2025-12)**: Setup inicial

### Tecnologias & Dependências
- **Python 3.12+** (com upgrade para 3.14+)
- **Ollama** — Inferência local de LLMs
- **Faster Whisper** — Reconhecimento de fala
- **ChromaDB** — Indexação de documentos
- **FastAPI** — REST API
- **Edge TTS** — Síntese de voz
- **DuckDuckGo API** — Busca na web
- **icalendar** — Gerenciamento de calendário
