import re
import string
from stuart_ai.LLM.ollama_llm import OllamaLLM
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.tools import AssistantTools
from stuart_ai.core.enums import AssistantSignal
from stuart_ai.core.logger import logger

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
            (r"\b(abra|abrir|inicie|iniciar|execute|executar)\b", self._handle_open_app, open_app),
            (r"\b(desligar|desligue)\b", shutdown_computer),
            (r"\b(cancele o desligamento|cancelar desligamento)\b", cancel_shutdown),
            (r"\b(pesquise na web|procure na web|busque na web)\b", self._handle_search, perform_web_search),
            (r"\b(sair|encerrar|tchau)\b", quit_tool),
        ]

    def _extract_argument(self, command: str, keyword: str) -> str:
        """Extracts the argument from the command by finding the keyword and taking the rest of the string."""
        try:
            # Find the position of the keyword (case-insensitive)
            keyword_pos = command.lower().find(keyword.lower())
            if keyword_pos == -1:
                return ""
            
            # Get the substring after the keyword
            argument = command[keyword_pos + len(keyword):].strip()
            
            # Remove common articles from the beginning of the argument
            articles = ['o', 'a', 'os', 'as']
            arg_list = argument.split()
            if arg_list and arg_list[0].lower() in articles:
                argument = ' '.join(arg_list[1:])
            
            # Remove trailing punctuation
            argument = argument.rstrip(string.punctuation)
                
            return argument
        except (AttributeError, TypeError, ValueError) as e:
            logger.error(f"Error extracting argument: {e}")
            return ""

    def _handle_open_app(self, command: str, tool_func, matched_keyword: str):
        """Helper to extract argument for the open_app tool and call it."""
        argument = self._extract_argument(command, matched_keyword)
        if argument:
            return tool_func.run(argument)
        else:
            # Ask for clarification if the argument is missing
            return "Claro, qual aplicativo você gostaria de abrir?"

    def _handle_search(self, command: str, tool_func, matched_keyword: str):
        """Helper to extract argument and call a search-like tool."""
        keyword_pos = command.lower().find(matched_keyword.lower())
        argument = ""
        if keyword_pos != -1:
            argument = command[keyword_pos + len(matched_keyword):].strip()

        if argument:
            return tool_func.run(argument)
        else:
            # Ask for clarification if the argument is missing
            return "Claro, sobre o que você gostaria?"

    def _execute_actions(self, actions, command: str, match):
        """Run the provided actions and return (result, errored_flag)."""
        tool_to_log = actions[0] if len(actions) == 1 else actions[1]
        logger.info(f"--- Roteando comando '{command}' para a ação: {tool_to_log.name} ---")
        try:
            if len(actions) == 1:  # Tool without arguments
                result = actions[0].run()
            else:  # Tool with arguments
                handler, tool_func = actions
                matched_keyword = match.group(0)
                result = handler(command, tool_func, matched_keyword)
            return result, False
        except (AttributeError, TypeError, ValueError) as e:
            logger.error(f"Error processing command with new router: {e}")
            self.speak("Desculpe, ocorreu um erro ao processar o comando.")
            return None, True

    def process(self, command: str):
        """
        Processes the user command, routes it to the correct tool, and handles graceful shutdown.
        Returns 'QUIT_ASSISTANT' to signal the main loop to exit.
        """
        if not command.strip():
            return

        command_lower = command.lower()

        for keywords_regex, *actions in self.router_config:
            match = re.search(keywords_regex, command_lower)
            if not match:
                continue

            result, errored = self._execute_actions(actions, command, match)
            if errored:
                return

            if result == AssistantSignal.QUIT:
                return AssistantSignal.QUIT

            if result:
                self.speak(str(result))
            return

        # If no route is found
        logger.warning(f"--- Comando '{command}' não entendido ---")
        self.speak("Desculpe, não entendi o comando.")
