
import os
from crewai import LLM
from stuart_ai.core.config import settings


class OllamaLLM:
    def __init__(self, host: str | None = None,
                  port: int | None = None,
                  model: str | None = None,
                  temperature: float | None = None):
        
        self.host = host if host else settings.llm_host
        self.port = port if port else settings.llm_port
        self.model = model if model else settings.llm_model
        self.temperature = temperature if temperature else settings.llm_temperature
    
    def get_llm_instance(self):
        return LLM(
            host=self.host,
            port=self.port,
            model=self.model,
            temperature=self.temperature
        )