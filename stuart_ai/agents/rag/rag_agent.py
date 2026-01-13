from stuart_ai.agents.rag.document_store import DocumentStore
from stuart_ai.core.logger import logger

class LocalRAGAgent:
    def __init__(self, llm, document_store: DocumentStore):
        self.llm = llm
        self.document_store = document_store

    async def run(self, query: str) -> str:
        """Answers a query using local documents."""
        logger.info("RAG Agent querying: %s", query)
        
        # Retrieve context
        import asyncio
        retrieved_docs = await asyncio.to_thread(self.document_store.search, query)
        
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
        
        response = await asyncio.to_thread(self.llm.call, messages)
        return response
