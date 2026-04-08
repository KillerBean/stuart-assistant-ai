# Backlog de Tarefas - Stuart AI

Este arquivo contém as tarefas pendentes organizadas para importação ou cadastro manual em um quadro Kanban (Trello, Jira, GitHub Projects, Notion).

## 🚀 Novas Features (Agentes)

### 1. Agente de Produtividade: Integração de E-mail
- **Descrição:** Expandir o agente de produtividade para ler e-mails não lidos e enviar mensagens simples.
- **Detalhes:** Integração com APIs do Gmail ou Outlook. Requer autenticação segura (OAuth2).
- **Labels:** Feature, Productivity, Email

### 2. Agente de Coding/Dev
- **Descrição:** Criar um agente especializado em tarefas de desenvolvimento.
- **Detalhes:** Capacidade de explicar stack traces, gerar scripts simples (Python/Bash) e analisar snippets de código.
- **Labels:** Feature, DevTools, LLM

### 3. Agente de Conteúdo (Resumos)
- **Descrição:** Implementar capacidade de resumir vídeos do YouTube e artigos longos.
- **Detalhes:** Usar ferramentas de extração de transcript (YouTube API) e scrapers de texto para alimentar o LLM.
- **Labels:** Feature, Content, Web

---

## 🛠️ Melhorias (Core & Ferramentas)

### 4. Controle de Mídia Local
- **Descrição:** Adicionar ferramentas de sistema para controlar reprodução de mídia.
- **Detalhes:** Comandos: Play, Pause, Próximo, Anterior, Aumentar/Diminuir Volume. Deve ser compatível com Linux/Windows/Mac.
- **Labels:** Enhancement, System Tools

### 5. TTS Local de Alta Qualidade
- **Descrição:** Substituir ou adicionar alternativa ao gTTS/Online TTS por uma solução local neural.
- **Detalhes:** Avaliar Coqui TTS ou Piper para reduzir latência e dependência de internet.
- **Labels:** Enhancement, Audio, Offline

### 6. Gerenciamento de Estado e Contexto
- **Descrição:** Implementar uma classe robusta de `Context` para a conversa.
- **Detalhes:** Manter histórico da sessão, estado atual (ouvindo, falando, processando) e permitir referências a perguntas anteriores.
- **Labels:** Refactoring, Core, Architecture

---

## 🔒 Segurança & Dívida Técnica

### 7. Segurança: Whitelist de Aplicativos
- **Descrição:** Restringir o comando "abrir [app]" a uma lista aprovada.
- **Detalhes:** Criar arquivo de configuração com apps permitidos para evitar execução de malwares ou scripts perigosos via comando de voz.
- **Labels:** Security, System Tools

### 8. Tratamento de Erros Amigável
- **Descrição:** Melhorar as mensagens de erro faladas pelo assistente.
- **Detalhes:** Substituir mensagens técnicas ("ConnectionRefusedError") por frases naturais ("Não consegui conectar ao servidor, verifique sua internet").
- **Labels:** UX, Error Handling

### 9. API de Gerenciamento (Backend)
- **Descrição:** Criar endpoints REST para monitorar o status do assistente.
- **Detalhes:** Usar FastAPI para expor rotas: `/status`, `/agents/list`, `/logs`. Passo inicial para uma UI.
- **Labels:** Backend, Infrastructure

---

## 🧪 Testes & Infraestrutura

### 10. Mocks para Testes de Integração
- **Descrição:** Criar mocks robustos para as chamadas de LLM e Áudio.
- **Detalhes:** Permitir rodar a suíte de testes completa sem chaves de API reais ou hardware de áudio (CI/CD friendly).
- **Labels:** Testing, CI/CD

### 11. Pipeline de CI/CD
- **Descrição:** Configurar automação de testes no repositório.
- **Detalhes:** Workflow (GitHub Actions) para rodar linting (ruff/pylint) e testes (pytest) a cada push.
- **Labels:** DevOps, Infrastructure

### 12. Aumentar Cobertura de Testes
- **Descrição:** Escrever testes unitários para `CommandHandler` e `Settings`.
- **Detalhes:** Focar em casos de borda e validação de configurações inválidas.
- **Labels:** Testing, Quality
