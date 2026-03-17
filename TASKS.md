# Tasks - Stuart AI

> Checklist consolidado de implementações pendentes. Atualizado em 2026-03-17.
> Última revisão: incluídas novas tarefas do CLAUDE.md (Structured Logging JSON + Graceful Shutdown).

---

## 🏗️ Core / Arquitetura

- [x] **State Management:** `AssistantContext` + `AssistantStatus` em `stuart_ai/core/state.py` — tracking de status (idle/listening/processing/speaking), comando atual, contagem e uptime
- [x] **Tratamento de erros amigável:** Mensagens de erro em português natural em `_open_app`, agentes de conteúdo e coding
- [ ] **Structured Logging (JSON):** `stuart_ai/core/logger.py` usa `coloredlogs` — migrar para formato JSON estruturado conforme CLAUDE.md: `{"time":..., "level":..., "module":..., "msg":...}`. Nunca logar texto completo reconhecido (PII).
- [ ] **Graceful Shutdown:** `main.py` não captura `SIGTERM`/`SIGINT` via `loop.add_signal_handler` nem chama `assistant.shutdown()`. Implementar conforme padrão do CLAUDE.md e criar método `shutdown()` no `Assistant` para fechar conexões Ollama, ChromaDB e TTS.

---

## 🤖 Agentes

- [ ] **Agente de E-mail:** Ler e-mails não lidos e enviar mensagens via Gmail/Outlook (OAuth2)
- [x] **Agente de Coding/Dev:** `stuart_ai/agents/coding_agent.py` — explica stack traces, gera scripts Python/Bash, analisa snippets de código
- [x] **Agente de Conteúdo:** `stuart_ai/agents/content_agent.py` — resume artigos via `trafilatura` e vídeos YouTube via `youtube-transcript-api`

---

## 🔊 Áudio / TTS

- [ ] **TTS Local:** Avaliar e integrar Coqui TTS ou Piper como alternativa offline ao Edge TTS
- [x] **Controle de Mídia:** Play/Pause, Próximo, Anterior, Volume ±10% via `playerctl` e `pactl` (Linux)

---

## 🔒 Segurança

- [x] **Whitelist de aplicativos:** `allowed_apps` em `config.py` — `_open_app` bloqueia apps não listados e loga a tentativa
- [ ] **Sanitização de inputs:** Prevenir prompt injection nos agentes

---

## 🌐 Infraestrutura / Backend

- [x] **API REST (FastAPI):** `stuart_ai/api/app.py` — endpoints `/status`, `/agents/list`, `/logs`; habilitado via `API_ENABLED=true`
- [x] **CI/CD (GitHub Actions):** `.github/workflows/ci.yml` — lint (pylint ≥7.0) + testes (pytest) a cada push

---

## 🧪 Testes

- [x] **Aumentar cobertura:** `tests/test_settings.py` — 12 testes para `Settings` (defaults, overrides, edge cases)
- [ ] **Mocks para CI:** Mocks de LLM e áudio para rodar suite completa sem hardware real

---

## 📚 Documentação

- [ ] **README `agents/`:** Documentar arquitetura dos agentes, capacidades e como invocar cada um
