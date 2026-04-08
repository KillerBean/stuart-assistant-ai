from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Assistant Configuration
    assistant_keyword: str = "stuart"
    language: str = "pt"
    
    # Audio/Wake Word Configuration
    mic_energy_threshold: int = 4000  # Adjust based on mic quality/noise
    mic_dynamic_energy_threshold: bool = True # Let it adjust automatically?
    wake_word_confidence: int = 70 # 0-100 match score for fuzzy matching
    phrase_time_limit: int = 10 # Max seconds to record
    whisper_model_size: str = "small" # tiny, base, small, medium, large
    
    # LLM Configuration
    llm_host: str = "localhost"
    llm_port: int = 11434
    llm_model: str = "gemma3:latest"
    router_model: str = "qwen2.5:0.5b"
    llm_temperature: float = 0.7
    embedding_model: str = "nomic-embed-text"
    
    # Memory Configuration
    memory_window_size: int = 10

    # Security: Path traversal protection for file indexing
    # Directories where the assistant is allowed to index files.
    # Paths are resolved at runtime; relative paths are resolved from $HOME.
    index_allowed_dirs: list[str] = ["~/Documents", "~/Downloads"]

    # Allowed file extensions for indexing
    index_allowed_extensions: list[str] = [".txt", ".pdf", ".md", ".docx", ".csv"]

    # Max file size for indexing (bytes) — default 50 MB
    index_max_file_size: int = 50 * 1024 * 1024

    # Security: App Whitelist
    allowed_apps: list[str] = [
        "firefox", "chromium", "chrome", "code", "terminal",
        "nautilus", "files", "spotify", "vlc", "discord", "slack",
        "gedit", "text-editor", "calculator", "gnome-calculator",
    ]

    # Management API
    api_enabled: bool = False
    api_port: int = 8000

    # Web Search
    # Add API keys here if you decide to switch to Serper/Google later
    # serper_api_key: str | None = None

    # Paths
    temp_dir: str = "tmp"

settings = Settings()
