# Tasks - Stuart AI

> Checklist consolidado de implementações pendentes. Atualizado em 2026-03-30.
> Última revisão: marcados itens de segurança concluídos na v0.6.0, adicionados pendentes identificados.

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
- [x] **Path traversal:** `_index_file()` bloqueia caminhos fora de `INDEX_ALLOWED_DIRS`
- [x] **Prompt injection (web search + RAG):** `utils/prompt_sanitizer.py` sanitiza conteúdo externo antes de inserir em prompts
- [x] **Input validation:** `handle_command()` rejeita entradas > 500 chars e com metacaracteres shell
- [x] **Router LLM output validation:** `tool_name` e `args` validados antes do dispatch
- [x] **JSON injection no router:** `json.dumps()` no prompt do `SemanticRouter`
- [x] **Temp files:** diretório `tmp/` com `0o700`, arquivos de áudio com `0o600`
- [ ] **URL injection em `get_weather()`:** `system_tools.py:166` — city sem `urllib.parse.quote()`
- [ ] **API sem autenticação:** `api/app.py` expõe endpoints em `0.0.0.0` sem API key
- [ ] **ICS injection:** `calendar_manager.py` — título de evento sem sanitização
- [ ] **Prompt injection via `ConversationMemory`:** histórico inserido no prompt sem sanitização
- [ ] **Rate limiting e CORS:** FastAPI sem `slowapi` ou CORS policy

---

## 🌐 Infraestrutura / Backend

- [x] **API REST (FastAPI):** `stuart_ai/api/app.py` — endpoints `/status`, `/agents/list`, `/logs`; habilitado via `API_ENABLED=true`
- [x] **CI/CD (GitHub Actions):** `.github/workflows/ci.yml` — lint (pylint ≥7.0) + testes (pytest) a cada push
- [ ] **Graceful Shutdown:** `main.py` sem `loop.add_signal_handler(SIGTERM/SIGINT)` e sem `assistant.shutdown()`
- [ ] **Bandit / pip-audit no CI:** análise estática de segurança ausente do pipeline
- [ ] **Docker:** `Dockerfile` multi-stage, non-root user, não existe ainda

---

## 🧪 Testes

- [x] **Aumentar cobertura:** `tests/test_settings.py` — 12 testes para `Settings` (defaults, overrides, edge cases)
- [ ] **Mocks para CI:** Mocks de LLM e áudio para rodar suite completa sem hardware real
- [ ] **Testes de segurança:** path traversal, prompt injection, API auth, command injection (ver TIER 4 em NEXT-STEPS.md)
- [ ] **Fuzzing com `hypothesis`:** `handle_command()` com inputs aleatórios

---

## 📚 Documentação

- [ ] **README `agents/`:** Documentar arquitetura dos agentes, capacidades e como invocar cada um
- [ ] **SECURITY.md:** Responsible disclosure policy, threat model, limitações conhecidas
- [ ] **Deployment guide:** Setup seguro em produção (CLAUDE.md ou doc dedicado)
