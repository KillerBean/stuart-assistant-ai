# Action Plan: Stuart AI Evolution

## 1. Structural Refactoring (Organization)
**Objective:** Organize the codebase into a proper Python package structure to improve maintainability and imports.

- [x] **Package Structure:** Move `assistant.py`, `command_handler.py`, and `tmp_file_handler.py` inside the `stuart_ai/` directory.
- [x] **Entry Point:** Update `main.py` to import from the reorganized package.
- [x] **Dependency Injection:** Refactor classes to accept dependencies (like `llm`, `tools`) via `__init__` rather than instantiating them internally (partially done, but can be improved).

## 2. Configuration & Observability (Robustness)
**Objective:** Remove hardcoded paths/settings and improve error visibility.

- [x] **Pydantic Settings:** Implement a `Settings` class (using `pydantic-settings`) to validate environment variables (`LLM_HOST`, `ASSISTANT_KEYWORD`, API keys) and manage defaults.
- [x] **Structured Logging:** Replace `print()` statements with a proper logging setup (using `structlog` or standard `logging`). This is crucial for debugging async processes.
- [x] **Error Handling:** Create custom exceptions for the Assistant (e.g., `LLMConnectionError`, `AudioDeviceError`) to handle failures gracefully without crashing the loop.

## 3. Core Architecture (Responsiveness)
**Objective:** Make the assistant non-blocking so it can listen/think/speak concurrently where appropriate.

- [x] **AsyncIO Loop:** Rewrite the main `listen_continuously` loop to use `asyncio`.
- [x] **Async Tools:** Make tool execution asynchronous (especially `web_search` and network requests).
- [ ] **State Management:** Introduce a `StateManager` or `Context` class to hold the conversation history and current status (listening, processing, speaking).

## 4. Intelligence Upgrade (The "Brain")
**Objective:** Move from rigid Regex matching to semantic understanding.

- [x] **Semantic Routing:** Currently, you use Regex. We should implement a "Semantic Router" or an Intent Classifier using the LLM.
    - *Fast Path:* Regex (for "stop", "time").
    - *Smart Path:* LLM Router (for "Search about X" or complex requests).
- [x] **Conversation Memory:** Implement a rolling window buffer so Stuart remembers previous questions (e.g., "What is the capital of France?" -> "And its population?").

## 5. Tooling & Capabilities
- [ ] **Local TTS (Optional):** `gTTS` adds latency and requires internet. Suggest integrating a local neural TTS (like `Coqui TTS` or `Piper`) if offline capability is desired.
- [ ] **Media Control:** Improve the app launcher to be OS-agnostic using better libraries.

## 6. Testing
- [ ] **Unit Tests:** Add tests for the new `CommandHandler` and `Settings`.
- [ ] **Mocks:** Mock LLM and Audio inputs for CI/CD testing.
