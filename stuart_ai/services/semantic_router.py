import json
from typing import Optional, Dict, Any
from stuart_ai.LLM.ollama_llm import OllamaLLM
from stuart_ai.core.logger import logger

class SemanticRouter:
    def __init__(self):
        self.llm = OllamaLLM().get_llm_instance()

    async def route(self, command: str) -> Dict[str, Any]:
        """
        Analyzes the command and returns the intent and arguments in JSON format.
        """
        prompt = f"""
        Você é o cérebro de um assistente virtual chamado Stuart.
        Sua função é analisar o comando do usuário e decidir qual ferramenta usar.
        
        Ferramentas disponíveis:
        - "time": Perguntas sobre horas.
        - "date": Perguntas sobre a data de hoje.
        - "weather": Perguntas sobre clima/tempo. Argumento: "city".
        - "joke": Pedidos de piada.
        - "wikipedia": Perguntas de definição ("O que é", "Quem foi"). Argumento: "query".
        - "web_search": Perguntas sobre atualidades, notícias ou buscas complexas. Argumento: "query".
        - "general_chat": Conversa casual, cumprimentos ou perguntas que você mesmo pode responder sem ferramentas.
        
        Responda APENAS um objeto JSON no seguinte formato, sem markdown ou explicações:
        {{
            "tool": "nome_da_ferramenta",
            "args": "argumento_extraido_ou_null"
        }}
        
        Exemplos:
        Usuário: "Que horas são?" -> {{"tool": "time", "args": null}}
        Usuário: "Está chovendo em São Paulo?" -> {{"tool": "weather", "args": "São Paulo"}}
        Usuário: "Pesquise sobre a teoria das cordas" -> {{"tool": "wikipedia", "args": "Teoria das Cordas"}}
        Usuário: "Preço do Bitcoin hoje" -> {{"tool": "web_search", "args": "Preço do Bitcoin hoje"}}
        Usuário: "Olá Stuart, tudo bem?" -> {{"tool": "general_chat", "args": null}}
        
        Comando do usuário: "{command}"
        JSON:
        """

        try:
            # We use the synchronous call inside a thread if needed, but CrewAI LLM call might be blocking.
            # CrewAI LLM 'call' method returns a string.
            response = self.llm.call([{"role": "user", "content": prompt}])
            
            # Clean up response (remove markdown code blocks if present)
            cleaned_response = response.strip().replace("```json", "").replace("```", "").strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from router response: {response}")
            # Fallback to general chat or search if parsing fails
            return {"tool": "web_search", "args": command}
        except Exception as e:
            logger.error(f"Error in semantic routing: {e}")
            return {"tool": "general_chat", "args": None}
