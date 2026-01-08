from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Assistant Configuration
    assistant_keyword: str = "stuart"
    language: str = "pt"
    
    # LLM Configuration
    llm_host: str = "localhost"
    llm_port: int = 11434
    llm_model: str = "gemma3:latest"
    router_model: str = "qwen2.5:0.5b"
    llm_temperature: float = 0.7
    embedding_model: str = "nomic-embed-text"
    
    # Memory Configuration
    memory_window_size: int = 10

    # Web Search
    # Add API keys here if you decide to switch to Serper/Google later
    # serper_api_key: str | None = None

    # Paths
    temp_dir: str = "tmp"

settings = Settings()
