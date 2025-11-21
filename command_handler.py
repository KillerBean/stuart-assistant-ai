from langchain_community.chat_models import ChatOllama
from crewai import Agent, Task, Crew

from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.tools import AssistantTools


class CommandHandler:
    """
    Handles the processing of user commands using an LLM-based intent recognition system.
    """

    def __init__(self, speak_func, confirmation_func, app_aliases, 
                 llm, assistant_tools: AssistantTools, web_search_agent: WebSearchAgent):
        self.speak = speak_func
        self.confirm = confirmation_func
        self.app_aliases = app_aliases
        
        self.llm = llm
        self.assistant_tools = assistant_tools
        self.web_search_agent = web_search_agent 

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

        self.router_agent = Agent(
            role="Router de Comandos Inteligente",
            goal="Analisar o comando do usuário, entender a intenção e selecionar a ferramenta apropriada para executá-lo. Extraia todos os argumentos necessários para a ferramenta a partir do comando do usuário. Se nenhum comando corresponder, informe ao usuário que você não entendeu.",
            backstory="Você é um assistente de IA eficiente, especialista em entender a linguagem natural e encaminhar solicitações para a função apropriada. Você é preciso e direto.",
            llm=self.llm,
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

        try:
            print(f"--- Executando Crew para o comando: '{command}' ---")
            result = self._execute_crew_task(self.router_agent, task)
            print(f"--- Crew finalizado com o resultado: '{result}' ---")
            
            if result:
                self.speak(str(result))
            else:
                print("WARN: Crew returned an empty result.")
                self.speak("Desculpe, não entendi o comando.")

        except Exception as e:
            print(f"Error processing command with CrewAI: {e}")
            self.speak("Desculpe, ocorreu um erro ao processar o comando com o agente de IA.")

    def _execute_crew_task(self, agent: Agent, task: Task) -> str:
        """
        Encapsulates the creation and execution of a CrewAI Crew.
        This method can be mocked in unit tests to avoid actual LLM calls.
        """
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        result = str(crew.kickoff())

        return result