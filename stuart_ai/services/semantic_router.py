import json
import asyncio
from typing import Optional, Dict, Any
from stuart_ai.llm.ollama_llm import OllamaLLM
from stuart_ai.core.logger import logger
from stuart_ai.core.exceptions import LLMConnectionError, LLMResponseError

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
        - "search_local_files": Perguntas sobre seus documentos ou arquivos locais. Argumento: "query".
        - "index_file": Pedido para ler/aprender um arquivo novo. Argumento: "file_path".
        - "add_event": Agendar compromissos. Argumento (JSON): {{"title": "Nome do evento", "datetime": "Data e hora naturais (ex: amanhã as 14h)"}}.
        - "check_calendar": Consultar agenda. Argumento: "data_para_filtrar" (ou null para ver tudo).
        - "general_chat": Conversa casual, cumprimentos ou perguntas que você mesmo pode responder sem ferramentas.
        
        Responda APENAS um objeto JSON no seguinte formato, sem markdown ou explicações:
        {{
            "tool": "nome_da_ferramenta",
            "args": "argumento_string_ou_objeto_json"
        }}
        
        Exemplos:
        (Histórico vazio) Usuário: "Que horas são?" -> {{"tool": "time", "args": null}}
        (Histórico: User='Tempo em SP?') Usuário: "E no Rio?" -> {{"tool": "weather", "args": "Rio de Janeiro"}}
        (Histórico: User='Quem foi Napoleão?') Usuário: "Onde ele morreu?" -> {{"tool": "wikipedia", "args": "Morte de Napoleão"}}
        Usuário: "Marque dentista amanhã às 10" -> {{"tool": "add_event", "args": {{"title": "Dentista", "datetime": "amanhã às 10:00"}}}}
        Usuário: "O que tenho hoje?" -> {{"tool": "check_calendar", "args": "hoje"}}
        
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
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from router response: {e}")
            raise LLMResponseError(f"Invalid JSON response from LLM: {cleaned_response}")
        except Exception as e:
            logger.error(f"Error in semantic routing: {e}")
            raise LLMConnectionError(f"Failed to communicate with LLM: {e}")
