from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.language_models import BaseLanguageModel

class WebSearchAgent:
    def __init__(self, llm: BaseLanguageModel, search_tool=None):
        self.llm = llm
        self.search_tool = search_tool if search_tool else DuckDuckGoSearchRun()

    def create_web_search_agent(self):
        return Agent(
            role='Pesquisador Web Sênior',
            goal='Encontrar e sintetizar informações relevantes da web sobre um tópico específico.',
            backstory='É um pesquisador experiente, especialista em encontrar e analisar rapidamente informações online para fornecer insights concisos e precisos.',
            verbose=True,
            allow_delegation=False,
            tools=[self.search_tool],
            llm=self.llm  # Pass the LLM here
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
    # Example usage - NOTE: A real LLM instance would be needed here for actual execution
    # For demonstration, we'll use a placeholder.
    from langchain_community.chat_models import ChatOllama # Example LLM

    # This part would typically be handled by your main application's setup
    example_llm = ChatOllama(model="gemma3") # Or any other LLM

    web_search = WebSearchAgent(llm=example_llm)
    search_query = "Últimas notícias sobre inteligência artificial"
    print(f"Iniciando pesquisa para: {search_query}")
    # result = web_search.run_search_crew(search_query) # Uncomment to run with a real LLM
    # print("\n--- Resultado da Pesquisa ---")
    # print(result)
