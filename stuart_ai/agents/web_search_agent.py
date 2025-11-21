from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun

class WebSearchAgent:
    def __init__(self):
        self.search_tool = DuckDuckGoSearchRun()

    def create_web_search_agent(self):
        return Agent(
            role='Pesquisador Web Sênior',
            goal='Encontrar e sintetizar informações relevantes da web sobre um tópico específico.',
            backstory='É um pesquisador experiente, especialista em encontrar e analisar rapidamente informações online para fornecer insights concisos e precisos.',
            verbose=True,
            allow_delegation=False,
            tools=[self.search_tool]
        )

    def create_web_search_task(self, agent, query):
        return Task(
            description=f"Pesquise a web por '{query}' e forneça um resumo conciso das informações mais importantes.",
            expected_output='Um resumo conciso e preciso das informações encontradas na web sobre o tópico da pesquisa.',
            agent=agent
        )

    def run_search_crew(self, query):
        agent = self.create_web_search_agent()
        task = self.create_web_search_task(agent, query)

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == '__main__':
    # Example usage
    web_search = WebSearchAgent()
    search_query = "Últimas notícias sobre inteligência artificial"
    print(f"Iniciando pesquisa para: {search_query}")
    result = web_search.run_search_crew(search_query)
    print("\n--- Resultado da Pesquisa ---")
    print(result)
