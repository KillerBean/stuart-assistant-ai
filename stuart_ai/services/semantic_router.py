import json
import asyncio
from typing import Optional, Dict, Any
from stuart_ai.LLM.ollama_llm import OllamaLLM
from stuart_ai.core.logger import logger

class SemanticRouter:
    def __init__(self, llm):
        self.llm = llm

    async def route(self, command: str, history_str: str = "") -> Dict[str, Any]:
        """
        Analyzes the command and returns the intent and arguments in JSON format, considering conversation history.
        """
        prompt = f"""
        Você é o cérebro de um assistente virtual chamado Stuart.
        Sua função é analisar o comando do usuário e decidir qual ferramenta usar.
        
        Histórico da Conversa (use para resolver referências como 'ele', 'disso', 'lá'):
        ---
        {history_str}
        ---
        
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
            "args": "argumento_extraido_ou_resolvido_pelo_historico"
        }}
        
        Exemplos:
        (Histórico vazio) Usuário: "Que horas são?" -> {{"tool": "time", "args": null}}
        (Histórico: User='Tempo em SP?') Usuário: "E no Rio?" -> {{"tool": "weather", "args": "Rio de Janeiro"}}
        (Histórico: User='Quem foi Napoleão?') Usuário: "Onde ele morreu?" -> {{"tool": "wikipedia", "args": "Morte de Napoleão"}}
        
        Comando atual do usuário: "{command}"
        JSON:
        """

        try:
            # We use the synchronous call inside a thread to avoid blocking the loop
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(self.llm.call, messages)
            
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
