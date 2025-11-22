import os
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun

from stuart_ai.LLM.ollama_llm import OllamaLLM


class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "A tool that can be used to search DuckDuckGo for a given query."
    
    def _run(self, query: str) -> str:
        """Use the tool."""
        return DuckDuckGoSearchRun().run(query)

class WebSearchAgent:
    def __init__(self, llm: LLM, search_tool=None) -> None:
        self.search_tool = search_tool if search_tool else DuckDuckGoSearchTool()
        self.llm = llm

    def create_web_search_agent(self) -> Agent:
        return Agent(
            role='Pesquisador Web Sênior',
            goal='Encontrar e sintetizar informações relevantes da web sobre um tópico específico.',
            backstory='É um pesquisador experiente, especialista em encontrar e analisar rapidamente informações online para fornecer insights concisos e precisos.',
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
            tools=[self.search_tool],
        )

    def create_web_search_task(self, agent, query) -> Task:
        return Task(
            description=f"Pesquise a web por '{query}' e forneça um resumo conciso das informações mais importantes.",
            expected_output='Um resumo conciso e preciso das informações encontradas na web sobre o tópico da pesquisa.',
            agent=agent
        )

    def run_search_crew(self, query) -> str:
        agent = self.create_web_search_agent()
        task = self.create_web_search_task(agent, query)

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True,
        )

        result = str(crew.kickoff())
        return result

if __name__ == '__main__':
    llm = OllamaLLM().get_llm_instance()
    # Instancia e executa o agente de busca
    web_search = WebSearchAgent(llm=llm)
    search_query = "Últimas notícias sobre inteligência artificial"
    print(f"Iniciando pesquisa para: {search_query}")
    result = web_search.run_search_crew(search_query)
    print("\n--- Resultado da Pesquisa ---")
    print(result)
