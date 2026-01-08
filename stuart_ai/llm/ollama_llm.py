from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
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
        
        base_url = f"http://{self.host}:{self.port}"
        
        self._llm = ChatOllama(
            base_url=base_url,
            model=self.model,
            temperature=self.temperature
        )
    
    def get_llm_instance(self):
        """Returns self to maintain compatibility with existing injection, 
        or returns the underlying langchain llm if needed.
        For now, we return self because usage is `llm.call()`.
        """
        return self

    def call(self, messages: list[dict]) -> str:
        """
        Adapts the simple message format [{'role': 'user', 'content': '...'}] 
        to LangChain messages and invokes the LLM.
        """
        lc_messages = []
        for msg in messages:
            if msg['role'] == 'user':
                lc_messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'system':
                lc_messages.append(SystemMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                lc_messages.append(AIMessage(content=msg['content']))
        
        response = self._llm.invoke(lc_messages)
        return response.content # type: ignore