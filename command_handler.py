from langchain_community.chat_models import ChatOllama
from crewai import Agent, Task, Crew

from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.tools import AssistantTools


class CommandHandler:
    """
    Handles the processing of user commands using an LLM-based intent recognition system.
    """

    def __init__(self, speak_func, confirmation_func, app_aliases):
        self.web_search_agent = WebSearchAgent()
        
        # Instantiate the tools class, passing all necessary dependencies
        self.assistant_tools = AssistantTools(
            speak_func=speak_func,
            confirmation_func=confirmation_func,
            app_aliases=app_aliases,
            web_search_agent=self.web_search_agent
        )

        # 1. Initialize the LLM for the router agent
        try:
            llm = ChatOllama(model="gemma3")
        except Exception as e:
            print("\n---")
            print("ERROR: Could not initialize Ollama.")
            print("Please make sure Ollama is running and the 'gemma3' model is available.")
            print(f"Error details: {e}")
            print("---\n")
            raise

        # 2. Get the list of tools from the AssistantTools instance
        tools = [
            self.assistant_tools._get_time,
            self.assistant_tools._tell_joke,
            self.assistant_tools._search_wikipedia,
            self.assistant_tools._get_weather,
            self.assistant_tools._open_app,
            self.assistant_tools._shutdown_computer,
            self.assistant_tools._cancel_shutdown,
            self.assistant_tools._perform_web_search,
            self.assistant_tools._quit
        ]

        # 3. Create the Router Agent
        self.router_agent = Agent(
            role="Router de Comandos Inteligente",
            goal="Analisar o comando do usuário, entender a intenção e selecionar a ferramenta apropriada para executá-lo. Extraia todos os argumentos necessários para a ferramenta a partir do comando do usuário. Se nenhum comando corresponder, informe ao usuário que você não entendeu.",
            backstory="Você é um assistente de IA eficiente, especialista em entender a linguagem natural e encaminhar solicitações para a função apropriada. Você é preciso e direto.",
            llm=llm,
            tools=tools,
            allow_delegation=False,
            verbose=True
        )

    def process(self, command: str):
        """Processes the user command by routing it to the correct tool using an LLM agent."""
        if not command.strip():
            return

        task = Task(
            description=f"Analise e execute o seguinte comando do usuário: '{command}'. Responda em português.",
            expected_output="A resposta em texto da ferramenta que foi executada, ou uma mensagem informando que o comando não foi entendido.",
            agent=self.router_agent
        )

        crew = Crew(
            agents=[self.router_agent],
            tasks=[task],
            verbose=True
        )

        try:
            print(f"--- Executando Crew para o comando: '{command}' ---")
            result = crew.kickoff()
            print(f"--- Crew finalizado com o resultado: '{result}' ---")
            
            # A final check in case the agent failed to find a tool and didn't produce a coherent response.
            if crew.calculate_usage_metrics().successful_requests > 0 and not result:
                 print("WARN: Crew ran but returned an empty result.")

        except Exception as e:
            print(f"Error processing command with CrewAI: {e}")
            self.assistant_tools.speak("Desculpe, ocorreu um erro ao processar o comando com o agente de IA.")