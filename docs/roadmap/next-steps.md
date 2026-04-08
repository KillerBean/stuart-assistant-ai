# Plano de Ação: Implementação de Agentes de IA

Este documento detalha o plano de ação para construir e integrar capacidades de agentes de IA no assistente Stuart, com base nas metas definidas no arquivo `TODO-List.md`.

## Estratégia Geral

A implementação será dividida em fases, permitindo uma abordagem incremental que prioriza a entrega de valor contínua. Começaremos com um agente simples para validar a arquitetura e, progressivamente, adicionaremos complexidade, novos agentes e capacidades de gerenciamento.

**Escolha de Ferramentas:**
Para orquestração de agentes, **CrewAI** é uma excelente escolha por ser poderosa e declarativa, alinhando-se bem com os objetivos de criar fluxos de trabalho com múltiplos agentes. **LangChain** será usado como uma biblioteca de suporte fundamental para integrações, manipulação de dados e componentes de LLM. **LlamaIndex** será considerado para tarefas intensivas de RAG (Análise de Documentos).

## Fase 1: Fundação e Prova de Conceito (PoC)

**Objetivo:** Implementar um único agente para realizar buscas na web, estabelecendo a arquitetura base para futuros agentes.

1. **Estrutura do Projeto:**
    * Criar um novo diretório `stuart_ai/agents` para abrigar toda a lógica relacionada aos agentes.
    * Dentro de `agents`, criar um `web_search_agent.py` para definir o primeiro agente.

2. **Configuração do Ambiente:**
    * Adicionar as bibliotecas necessárias ao `requirements.txt`:

        ```text
        crewai
        crewai[tools]
        duckduckgo-search
        langchain_community
        ```

3. **Desenvolvimento do Agente:**
    * **Ferramenta (Tool):** Utilizar a ferramenta `DuckDuckGoSearchRun` da biblioteca `langchain_community` para acesso à web.
    * **Agente:** Em `web_search_agent.py`, definir um `Agent` do CrewAI com o `role` de "Pesquisador Web Sênior" e um `goal` claro para encontrar e sintetizar informações da web.
    * **Tarefa (Task):** Criar uma `Task` que instrui o agente a pesquisar um tópico fornecido pelo usuário e retornar uma resposta concisa.

4. **Integração com o Comando Principal:**
    * Modificar `command_handler.py` para reconhecer um novo comando, como `/search <query>`.
    * Este comando irá instanciar e executar o "crew" (composto pelo agente de busca e sua tarefa), e exibir o resultado para o usuário.

## Fase 2: Expansão com Agentes Especializados e Ferramentas Customizadas

**Objetivo:** Desenvolver agentes para tarefas mais específicas e criar ferramentas personalizadas para integrações profundas.

1. **Agente de Análise de Documentos:**
    * **Tarefa:** "Analisar documentos longos".
    * **Ferramentas:** Utilizar **LangChain** ou **LlamaIndex** para carregar, dividir (chunking) e vetorizar documentos.
    * **Desenvolvimento:**
        * Criar uma ferramenta customizada que recebe o caminho de um arquivo (`.txt`, `.md`, `.pdf`).
        * A ferramenta irá processar o documento e preparar um RAG (Retrieval-Augmented Generation) para que o agente possa responder a perguntas sobre o conteúdo.
        * **Consideração sobre Repositório:** Para agentes complexos como este, que podem ter dependências pesadas (ex: bibliotecas de ML, banco de dados vetorial), **deve-se considerar a criação de um microserviço em um repositório separado**. O assistente principal faria uma chamada de API para este serviço. Isso mantém o cliente principal leve.

2. **Agente Gerenciador de Calendário:**
    * **Tarefa:** "Gerenciar calendários e compromissos".
    * **Desenvolvimento:**
        * Criar uma ferramenta customizada que se integra com uma API de calendário (Google Calendar, Microsoft Graph).
        * Implementar o fluxo de autenticação segura (OAuth2).
        * Desenvolver funções na ferramenta para `listar_eventos`, `criar_evento` e `deletar_evento`.
        * O agente usará essas funções para interagir com o calendário do usuário com base em linguagem natural.

## Fase 3: Orquestração de Múltiplos Agentes (Crew)

**Objetivo:** Criar fluxos de trabalho onde múltiplos agentes colaboram para realizar tarefas complexas.

1. **Caso de Uso: Análise de Tópicos Atuais:**
    * **Agente 1: Pesquisador:** Responsável por coletar dados em tempo real da web e redes sociais sobre um determinado tópico.
    * **Agente 2: Analista:** Responsável por receber os dados brutos do pesquisador, analisar, identificar tendências, prós e contras, e sintetizar as informações.
    * **Agente 3: Redator:** Responsável por pegar a análise e formatá-la em um relatório coeso e bem escrito para o usuário.
2. **Implementação com CrewAI:**
    * Definir os três agentes, cada um com sua especialidade e ferramentas.
    * Definir as tarefas para cada agente, garantindo que o output de um seja o input do próximo.
    * Criar um `Crew` que define o processo sequencial e orquestra a execução.
    * Integrar a chamada deste `Crew` a um novo comando no `command_handler.py`.

## Fase 4: Gerenciamento, Monitoramento e UI

**Objetivo:** Construir a infraestrutura para gerenciar, monitorar e interagir com os agentes de forma robusta.

1. **Logging e Auditoria:**
    * Implementar logging estruturado para todas as operações dos agentes: `agente executado`, `ferramenta usada`, `input`, `output`.

2. **API de Gerenciamento (Potencial Microserviço):**
    * Desenvolver uma API interna simples (usando FastAPI ou Flask) que exponha endpoints para:
        * `GET /agents`: Listar todos os agentes disponíveis.
        * `GET /agents/{agent_id}/history`: Ver o histórico de execuções de um agente.
        * `POST /agents/run`: Disparar uma tarefa para um agente.

3. **Interface de Gerenciamento (Visão de Futuro):**
    * Uma vez que a API de gerenciamento esteja no lugar, uma interface de usuário (Web UI com Streamlit, por exemplo) pode ser desenvolvida para fornecer um painel de controle visual para monitorar a atividade dos agentes.

## Fase 5: Segurança, Documentação e Validação

**Objetivo:** Garantir que o sistema de agentes seja seguro, bem documentado e eficaz.

1. **Segurança:**
    * Implementar sanitização rigorosa de todos os inputs do usuário para prevenir ataques de injeção de prompt.
    * Gerenciar chaves de API e segredos de forma segura (usando variáveis de ambiente ou um cofre de segredos).
    * Para ferramentas que acessam dados sensíveis (ex: calendário), implementar um mecanismo de permissão explícita do usuário antes da execução.

2. **Documentação:**
    * Criar um `README.md` no diretório `stuart_ai/agents` explicando a arquitetura geral.
    * Documentar cada agente, suas capacidades, as ferramentas que utiliza e como invocá-lo.

3. **Testes e Validação:**
    * Criar testes unitários para as ferramentas customizadas.
    * Desenvolver testes de integração para os "crews", validando que o fluxo de trabalho de ponta a ponta produz o resultado esperado para inputs conhecidos.
4. **Feedback do Usuário:**
    * Implementar um sistema de coleta de feedback para avaliar a eficácia dos agentes e identificar áreas de melhoria contínua.

## Conclusão

Este plano de ação fornece um roteiro claro para a implementação de agentes de IA no assistente Stuart. A abordagem faseada permite a construção incremental, garantindo que cada etapa seja validada antes de avançar para a próxima. Com o uso de ferramentas poderosas como CrewAI e LangChain, o assistente estará bem posicionado para oferecer capacidades avançadas de automação e inteligência artificial aos seus usuários.
