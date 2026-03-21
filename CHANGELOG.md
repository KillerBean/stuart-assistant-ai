# CHANGELOG

## [Unreleased]

### Added
- **Agents Framework** — ContentAgent e CodingAgent para análise de conteúdo e assistência de programação
- **REST API** — FastAPI management API com endpoints para controle do assistente
- **AssistantContext** — Rastreamento de estado de sessão e contexto de assistente
- **App Whitelist** — Controle de segurança para aplicativos que podem ser abertos
- **Media Controls** — Suporte a controles de mídia do sistema
- **GitHub Actions CI/CD** — Pipeline de integração contínua e deployment automático
- **Structured Logging** — Logging estruturado em JSON para melhor observabilidade
- **Graceful Shutdown** — Handlers de sinal para desligamento limpo (SIGTERM, SIGINT)

### Changed
- **Calendar Migration** — Migrado de `ics` para `icalendar` para compatibilidade com Python 3.14
- **Test Coverage** — Testes unitários para Settings, ferramentas do sistema e roteamento semântico
- **Documentation** — Adicionadas seções de Testing, Logging e Graceful Shutdown ao CLAUDE.md

### Fixed
- Correção de targets de mock nos testes de whitelist
- Atualização de testes para comportamento de whitelist corrigido

## [0.1.0] - 2026-03-20

### Added
- **Core Features**
  - Ativação por voz com palavra-chave configurável (padrão: "stuart")
  - Reconhecimento de fala offline com Faster Whisper
  - Síntese de voz com Edge TTS (pt-BR-AntonioNeural)
  - Roteamento híbrido (Regex + SemanticRouter LLM)
  - Memória de conversação com janela deslizante

- **Agents**
  - WebSearchAgent — Busca na web via DuckDuckGo com síntese LLM
  - RAG Agent — Indexação e consulta de documentos locais via ChromaDB
  - Calendar Manager — Agendamento, consulta e remoção de eventos

- **Tools**
  - System: hora, data, clima, Wikipedia, piadas
  - Productivity: calendário, abertura de apps
  - Admin: desligamento, shutdown scheduling

- **Infrastructure**
  - Configuração via `.env` com Pydantic Settings
  - Logging centralizado
  - Dependency Injection pattern
  - Async-first architecture com `asyncio`

### Notes
- Dois modelos LLM: `gemma3:latest` (main), `qwen2.5:0.5b` (routing)
- ChromaDB para persistência de documentos
- Suporte completo a português (pt-BR)
