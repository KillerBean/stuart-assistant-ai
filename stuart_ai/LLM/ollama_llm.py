
import os
from crewai import LLM


class OllamaLLM:
    def __init__(self, host: str | None = None,
                  port: int | None = None,
                  model: str | None = None,
                  temperature: float | None = None):
        
        self.host = host if host else os.getenv("LLM_HOST", "localhost")
        self.port = port if port else int(os.getenv("LLM_PORT", "11434"))
        self.model = model if model else os.getenv("MODEL", "ollama/gemma3:latest")
        self.temperature = temperature if temperature else 0.7
    
    def get_llm_instance(self):
        return LLM(
            host=self.host,
            port=self.port,
            model=self.model,
            temperature=self.temperature
        )