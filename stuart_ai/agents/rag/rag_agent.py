from stuart_ai.agents.rag.document_store import DocumentStore
from stuart_ai.core.logger import logger
from langchain_core.messages import HumanMessage, SystemMessage

class LocalRAGAgent:
    def __init__(self, llm, document_store: DocumentStore):
        self.llm = llm
        self.document_store = document_store

    async def run(self, query: str) -> str:
        """Answers a query using local documents."""
        logger.info("RAG Agent querying: %s", query)
        
        # Retrieve context
        retrieved_docs = self.document_store.search(query)
        
        if not retrieved_docs:
            return "Desculpe, não encontrei informações relevantes nos seus documentos indexados."

        context_str = "\n\n".join(retrieved_docs)
        
        prompt = f"""
        Você é um assistente útil que responde perguntas com base APENAS no contexto fornecido abaixo.
        Se a informação não estiver no contexto, diga que não sabe. Não invente.
        
        Contexto:
        ---
        {context_str}
        ---
        
        Pergunta do Usuário: {query}
        
        Responda de forma concisa e direta, em português.
        """

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # Ensure we are using the raw 'call' method of the injected LLM wrapper (OllamaLLM)
        # Check if llm is the wrapper or the crewai LLM object.
        # In main.py: llm = OllamaLLM().get_llm_instance() -> returns a crewai LLM object.
        # crewai LLM object has a 'call' method? checking docs/code...
        # Actually crewai LLM might be a wrapper around LiteLLM.
        # Let's rely on how SemanticRouter calls it: `self.llm.call(messages)`
        
        response = self.llm.call(messages)
        return response
