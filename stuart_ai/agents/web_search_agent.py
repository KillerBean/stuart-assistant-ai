from langchain_community.tools import DuckDuckGoSearchRun
from stuart_ai.core.logger import logger

class WebSearchAgent:
    def __init__(self, llm):
        self.llm = llm
        self.search_tool = DuckDuckGoSearchRun()

    def run(self, query: str) -> str:
        """
        Executes a web search and summarizes the results using the LLM.
        """
        logger.info("WebSearchAgent executing query: '%s'", query)
        
        try:
            # 1. Execute Search
            search_results = self.search_tool.run(query)
            
            # 2. Synthesize with LLM
            prompt = f"""
            Você é um pesquisador especialista. Resuma as informações abaixo para responder à pergunta do usuário de forma concisa e direta.
            
            Pergunta: {query}
            
            Resultados da Busca:
            ---
            {search_results}
            ---
            
            Resumo (em português):
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.call(messages)
            
            return response

        except Exception as e:
            logger.error("Web search failed: %s", e)
            return f"Desculpe, encontrei um erro ao pesquisar na web: {e}"