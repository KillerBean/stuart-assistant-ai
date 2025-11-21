import platform
import subprocess
from datetime import datetime

import requests
import wikipedia

from langchain.tools import tool
from langchain_community.chat_models import ChatOllama
from crewai import Agent, Task, Crew

from stuart_ai.agents.web_search_agent import WebSearchAgent


class CommandHandler:
    """
    Handles the processing of user commands using an LLM-based intent recognition system.
    """

    def __init__(self, speak_func, confirmation_func, app_aliases):
        self.speak = speak_func
        self.confirm = confirmation_func
        self.app_aliases = app_aliases
        self.web_search_agent = WebSearchAgent()

        # 1. Initialize the LLM for the router agent
        # Ensure Ollama is running with the 'gemma3' model
        try:
            llm = ChatOllama(model="gemma3")
        except Exception as e:
            print("\n---")
            print("ERROR: Could not initialize Ollama.")
            print("Please make sure Ollama is running and the 'gemma3' model is available.")
            print(f"Error details: {e}")
            print("---\n")
            raise

        # 2. Define the tools available to the agent
        # The methods decorated with @tool are used as tools.
        tools = [
            self._get_time,
            self._tell_joke,
            self._search_wikipedia,
            self._get_weather,
            self._open_app,
            self._shutdown_computer,
            self._cancel_shutdown,
            self._perform_web_search,
            self._quit
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
            # self.speak("Não recebi nenhum comando.") # Avoid speaking for empty inputs
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
            # The result from kickoff is the agent's final answer, which might be the output of a tool
            # or a natural language response if no tool was used.
            result = crew.kickoff()
            
            # Since the tools now return the string to be spoken, we let the main loop speak it.
            # This avoids double-speaking and centralizes the output. The exception is for
            # commands that require confirmation or have complex interaction, where speaking
            # might remain inside the tool. Let's adjust tools to return strings.
            print(f"--- Crew finalizado com o resultado: '{result}' ---")
            
            # The tools are designed to call speak() themselves to handle interactivity
            # (like confirmations) and provide immediate feedback. The `result` from kickoff
            # is useful for logging but we won't speak it here to avoid duplication.
            
            # A final check in case the agent failed to find a tool and didn't produce a coherent response.
            if crew.calculate_usage_metrics().successful_requests > 0 and not result:
                 print("WARN: Crew ran but returned an empty result.")

        except Exception as e:
            print(f"Error processing command with CrewAI: {e}")
            self.speak("Desculpe, ocorreu um erro ao processar o comando com o agente de IA.")

    # =================================================================================
    # TOOL DEFINITIONS
    # =================================================================================
    # Each method below is a tool that the agent can use.
    # The docstring of each method is crucial as it tells the LLM what the tool does
    # and what arguments it expects.
    # =================================================================================

    @tool
    def _get_time(self) -> str:
        """Retorna a hora e os minutos atuais. Use esta ferramenta sempre que o usuário perguntar as horas."""
        now = datetime.now().strftime("%H:%M")
        response = f"São {now}."
        self.speak(response)
        return response

    @tool
    def _tell_joke(self) -> str:
        """Conta uma piada aleatória em português. Use quando o usuário pedir para contar uma piada."""
        try:
            url = "https://v2.jokeapi.dev/joke/Any?lang=pt&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
            response = requests.get(url)
            response.raise_for_status()
            joke_data = response.json()
            joke = joke_data['joke'] if joke_data.get('type') == 'single' else f"{joke_data['setup']} ... {joke_data['delivery']}"
            self.speak(joke)
            return joke
        except requests.exceptions.RequestException as e:
            print(f"Error fetching joke from API: {e}")
            error_msg = "Desculpe, não consegui buscar uma piada agora."
            self.speak(error_msg)
            return error_msg

    @tool
    def _search_wikipedia(self, search_term: str) -> str:
        """Pesquisa um termo na Wikipedia e retorna um resumo. Use para perguntas sobre 'o que é' ou 'pesquise sobre'."""
        if not search_term:
            error_msg = "Claro, o que você gostaria que eu pesquisasse?"
            self.speak(error_msg)
            return error_msg
        
        self.speak(f"Claro, pesquisando sobre {search_term} na Wikipedia.")
        try:
            wikipedia.set_lang("pt")
            summary = wikipedia.summary(search_term, sentences=2)
            self.speak(summary)
            return summary
        except wikipedia.exceptions.PageError:
            error_msg = f"Desculpe, não encontrei nenhum resultado para {search_term}."
            self.speak(error_msg)
            return error_msg
        except wikipedia.exceptions.DisambiguationError:
            error_msg = f"O termo {search_term} é muito vago. Por favor, seja mais específico."
            self.speak(error_msg)
            return error_msg

    @tool
    def _get_weather(self, city: str) -> str:
        """Obtém a previsão do tempo para uma cidade específica."""
        if not city:
            error_msg = "Claro, para qual cidade você gostaria da previsão do tempo?"
            self.speak(error_msg)
            return error_msg
        
        self.speak(f"Verificando a previsão do tempo para {city}.")
        try:
            url = f"https://wttr.in/{city}?format=3"
            response = requests.get(url)
            response.raise_for_status()
            weather_info = response.text
            self.speak(weather_info)
            return weather_info
        except requests.exceptions.RequestException:
            error_msg = f"Desculpe, não consegui obter a previsão do tempo para {city}."
            self.speak(error_msg)
            return error_msg

    @tool
    def _open_app(self, app_name: str) -> str:
        """Abre ou inicia um programa no computador. Use para comandos como 'abra o chrome' ou 'inicie o vscode'."""
        spoken_name = app_name.strip()
        if not spoken_name:
            error_msg = "Claro, qual programa você gostaria de abrir?"
            self.speak(error_msg)
            return error_msg

        system = platform.system()
        executable_name = spoken_name.lower()

        if spoken_name in self.app_aliases and system in self.app_aliases[spoken_name]:
            executable_name = self.app_aliases[spoken_name][system]

        self.speak(f"Ok, abrindo {spoken_name}.")
        try:
            if system == "Windows":
                subprocess.Popen(['start', executable_name], shell=True)
            elif system == "Darwin":
                subprocess.Popen(['open', '-a', executable_name])
            else:
                subprocess.Popen([executable_name])
            return f"Programa {spoken_name} iniciado com sucesso."
        except FileNotFoundError:
            error_msg = f"Desculpe, não consegui encontrar o programa {spoken_name}."
            self.speak(error_msg)
            return error_msg
        except Exception as e:
            print(f"Error opening application: {e}")
            error_msg = f"Ocorreu um erro ao tentar abrir o {spoken_name}."
            self.speak(error_msg)
            return error_msg

    @tool
    def _shutdown_computer(self) -> str:
        """Desliga o computador após uma confirmação."""
        if self.confirm("Você tem certeza que deseja desligar o computador?"):
            self.speak("Ok, desligando o computador em 1 minuto. Adeus!")
            system = platform.system()
            try:
                if system == "Windows":
                    subprocess.run(["shutdown", "/s", "/t", "60"])
                else:  # Linux ou macOS
                    subprocess.run(["shutdown", "-h", "+1"])
                return "Comando de desligamento enviado."
            except Exception as e:
                print(f"Error trying to shutdown: {e}")
                error_msg = "Ocorreu um erro ao tentar executar o comando de desligamento."
                self.speak(error_msg)
                return error_msg
        else:
            cancel_msg = "Ação de desligamento cancelada."
            self.speak(cancel_msg)
            return cancel_msg

    @tool
    def _cancel_shutdown(self) -> str:
        """Cancela um desligamento do computador agendado."""
        self.speak("Cancelando o desligamento do computador.")
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(["shutdown", "/a"])
            else:  # Linux ou macOS
                subprocess.run(["shutdown", "-c"])
            return "Comando para cancelar o desligamento foi enviado."
        except Exception as e:
            print(f"Error trying to cancel shutdown: {e}")
            error_msg = "Ocorreu um erro ao tentar cancelar o comando de desligamento."
            self.speak(error_msg)
            return error_msg

    @tool
    def _perform_web_search(self, search_query: str) -> str:
        """Pesquisa na web usando um agente de IA para encontrar informações sobre um tópico. Use para pesquisas complexas ou quando a Wikipedia não for suficiente."""
        if not search_query:
            error_msg = "Claro, o que você gostaria que eu pesquisasse na web?"
            self.speak(error_msg)
            return error_msg
        
        self.speak(f"Ok, pesquisando na web sobre {search_query}. Isso pode levar um momento.")
        try:
            result = self.web_search_agent.run_search_crew(search_query)
            self.speak("A pesquisa retornou o seguinte:")
            self.speak(str(result))
            return str(result)
        except Exception as e:
            print(f"Error performing web search for '{search_query}': {e}")
            error_msg = "Desculpe, ocorreu um erro ao realizar a pesquisa na web."
            self.speak(error_msg)
            return error_msg

    @tool
    def _quit(self) -> str:
        """Encerra o assistente. Use quando o usuário disser 'sair', 'encerrar' ou 'tchau'."""
        self.speak("Encerrando a assistente. Até logo!")
        exit(0)
        return "Saindo..." # This line is unreachable but good practice
