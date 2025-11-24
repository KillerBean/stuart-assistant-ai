import re
from stuart_ai.LLM.ollama_llm import OllamaLLM
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.tools import AssistantTools

# A simple, custom tool class to avoid crewai's decorator issues
class SimpleTool:
    def __init__(self, name, func):
        self.name = name
        self.func = func
    
    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class CommandHandler:
    """
    Handles the processing of user commands using a fast, keyword-based routing system.
    """

    def __init__(self, speak_func, confirmation_func, app_aliases, web_search_agent: WebSearchAgent):
        self.speak = speak_func
        self.confirm = confirmation_func
        self.app_aliases = app_aliases
        self.llm = OllamaLLM().get_llm_instance()
        self.web_search_agent = web_search_agent 

        assistant_tools = AssistantTools(
            speak_func=self.speak,
            confirmation_func=self.confirm,
            app_aliases=self.app_aliases,
            web_search_agent=self.web_search_agent
        )

        # Manually create tools using our SimpleTool class
        get_time = SimpleTool(name='_get_time', func=assistant_tools._get_time)
        tell_joke = SimpleTool(name='_tell_joke', func=assistant_tools._tell_joke)
        search_wikipedia = SimpleTool(name='_search_wikipedia', func=assistant_tools._search_wikipedia)
        get_weather = SimpleTool(name='_get_weather', func=assistant_tools._get_weather)
        open_app = SimpleTool(name='_open_app', func=assistant_tools._open_app)
        shutdown_computer = SimpleTool(name='_shutdown_computer', func=assistant_tools._shutdown_computer)
        cancel_shutdown = SimpleTool(name='_cancel_shutdown', func=assistant_tools._cancel_shutdown)
        perform_web_search = SimpleTool(name='_perform_web_search', func=assistant_tools._perform_web_search)
        quit_tool = SimpleTool(name='_quit', func=assistant_tools._quit)

        # Keyword-based router configuration
        self.router_config = [
            (r"\b(horas?|tempo)\b", get_time),
            (r"\b(piada|conte-me uma piada)\b", tell_joke),
            (r"\b(wikipedia|pesquise sobre|o que é)\b", self._handle_search, search_wikipedia),
            (r"\b(clima|previsão do tempo)\b", self._handle_search, get_weather),
            (r"\b(abra|inicie|execute)\b", self._handle_search, open_app),
            (r"\b(desligar|desligue)\b", shutdown_computer),
            (r"\b(cancele o desligamento|cancelar desligamento)\b", cancel_shutdown),
            (r"\b(pesquise na web|procure na web|busque na web)\b", self._handle_search, perform_web_search),
            (r"\b(sair|encerrar|tchau)\b", quit_tool),
        ]

    def _extract_argument(self, command: str, keywords: list[str]) -> str:
        """Extracts the argument from the command based on the position of keywords."""
        try:
            # Simple regex to remove keywords and get the rest of the string
            for keyword in keywords:
                command = re.sub(r'\b' + re.escape(keyword) + r'\b', '', command, flags=re.IGNORECASE).strip()
            return command
        except Exception as e:
            print(f"Error extracting argument: {e}")
            return ""

    def _handle_search(self, command: str, tool_func, keywords: list[str]):
        """Helper to extract argument and call a tool that needs it."""
        argument = self._extract_argument(command, keywords)
        if argument:
            return tool_func.run(argument)
        else:
            # Ask for clarification if the argument is missing
            return "Claro, sobre o que você gostaria?"

    def process(self, command: str):
        """Processes the user command by routing it to the correct tool using keywords."""
        if not command.strip():
            return

        command_lower = command.lower()
        
        for keywords_regex, *actions in self.router_config:
            match = re.search(keywords_regex, command_lower)
            if match:
                tool_to_log = actions[0] if len(actions) == 1 else actions[1]
                print(f"--- Roteando comando '{command}' para a ação: {tool_to_log.name} ---")
                
                try:
                    if len(actions) == 1: # Tool without arguments
                        result = actions[0].run()
                    else: # Tool with arguments
                        handler, tool_func = actions
                        keywords = [kw for kw in keywords_regex.replace(r'\b', '').split('|') if kw]
                        result = handler(command, tool_func, keywords)
                    
                    if result:
                        self.speak(str(result))
                    return

                except Exception as e:
                    print(f"Error processing command with new router: {e}")
                    self.speak("Desculpe, ocorreu um erro ao processar o comando.")
                    return
        
        # If no route is found
        print(f"--- Comando '{command}' não entendido ---")
        self.speak("Desculpe, não entendi o comando.")
