import re
import string
import asyncio
from stuart_ai.LLM.ollama_llm import OllamaLLM
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.tools import AssistantTools
from stuart_ai.core.enums import AssistantSignal
from stuart_ai.core.logger import logger
from stuart_ai.services.semantic_router import SemanticRouter
from stuart_ai.core.memory import ConversationMemory

# A simple, custom tool class to avoid crewai's decorator issues
class SimpleTool:
    def __init__(self, name, func):
        self.name = name
        self.func = func
    
    async def run(self, *args, **kwargs):
        return await self.func(*args, **kwargs)

class CommandHandler:
    """
    Handles the processing of user commands using a fast, keyword-based routing system and a Semantic Router.
    """

    def __init__(self, speak_func, confirmation_func, app_aliases, web_search_agent: WebSearchAgent, semantic_router: SemanticRouter, memory: ConversationMemory):
        self.speak = speak_func
        self.confirm = confirmation_func
        self.app_aliases = app_aliases
        self.web_search_agent = web_search_agent 
        self.semantic_router = semantic_router
        self.memory = memory

        assistant_tools = AssistantTools(
            speak_func=self.speak,
            confirmation_func=self.confirm,
            app_aliases=self.app_aliases,
            web_search_agent=self.web_search_agent
        )

        # Tools available
        self.tools = {
            "time": SimpleTool(name='_get_time', func=assistant_tools._get_time),
            "joke": SimpleTool(name='_tell_joke', func=assistant_tools._tell_joke),
            "wikipedia": SimpleTool(name='_search_wikipedia', func=assistant_tools._search_wikipedia),
            "weather": SimpleTool(name='_get_weather', func=assistant_tools._get_weather),
            "web_search": SimpleTool(name='_perform_web_search', func=assistant_tools._perform_web_search),
            "open_app": SimpleTool(name='_open_app', func=assistant_tools._open_app),
            "shutdown_computer": SimpleTool(name='_shutdown_computer', func=assistant_tools._shutdown_computer),
            "cancel_shutdown": SimpleTool(name='_cancel_shutdown', func=assistant_tools._cancel_shutdown),
            "quit": SimpleTool(name='_quit', func=assistant_tools._quit)
        }

        # System/Critical commands - kept in Regex for speed and safety
        self.system_routes = [
            (r"\b(abra|abrir|inicie|iniciar|execute|executar)\b", self._handle_open_app, self.tools["open_app"]),
            (r"\b(desligar|desligue)\b", self.tools["shutdown_computer"]),
            (r"\b(cancele o desligamento|cancelar desligamento)\b", self.tools["cancel_shutdown"]),
            (r"\b(sair|encerrar|tchau)\b", self.tools["quit"]),
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

    async def _handle_open_app(self, command: str, tool_func, matched_keyword: str):
        """Helper to extract argument for the open_app tool and call it."""
        argument = self._extract_argument(command, matched_keyword)
        if argument:
            return await tool_func.run(argument)
        else:
            return "Claro, qual aplicativo você gostaria de abrir?"

    async def _execute_system_actions(self, actions, command: str, match):
        """Run the provided system actions and return (result, errored_flag)."""
        tool_to_log = actions[0] if len(actions) == 1 else actions[1]
        logger.info(f"--- Roteando comando '{command}' para a ação de Sistema: {tool_to_log.name} ---")
        try:
            if len(actions) == 1:  # Tool without arguments
                result = await actions[0].run()
            else:  # Tool with arguments
                handler, tool_func = actions
                matched_keyword = match.group(0)
                result = await handler(command, tool_func, matched_keyword)
            return result, False
        except (AttributeError, TypeError, ValueError) as e:
            logger.error(f"Error processing command with system router: {e}")
            await self.speak("Desculpe, ocorreu um erro ao processar o comando de sistema.")
            return None, True

    async def process(self, command: str):
        """
        Processes the user command using Hybrid Routing (System Regex -> Semantic Router).
        """
        if not command.strip():
            return

        # Add user command to memory
        self.memory.add_user_message(command)

        command_lower = command.lower()

        # 1. Fast Path: System Commands (Regex)
        for keywords_regex, *actions in self.system_routes:
            match = re.search(keywords_regex, command_lower)
            if not match:
                continue

            result, errored = await self._execute_system_actions(actions, command, match)
            if errored:
                return

            if result == AssistantSignal.QUIT:
                return AssistantSignal.QUIT

            if result:
                self.memory.add_assistant_message(str(result))
                await self.speak(str(result))
            return

        # 2. Smart Path: Semantic Router
        logger.info(f"--- Roteando comando '{command}' via Semantic Router ---")
        
        history = self.memory.get_formatted_history()
        router_response = await self.semantic_router.route(command, history_str=history)
        tool_name = router_response.get("tool")
        args = router_response.get("args")

        if tool_name == "general_chat":
             # Simple fallback for now
             response_text = "Entendi. Como posso ajudar com isso?"
             self.memory.add_assistant_message(response_text)
             await self.speak(response_text)
             return

        if tool_name in self.tools:
            tool = self.tools[tool_name]
            try:
                if args:
                    result = await tool.run(args)
                else:
                    result = await tool.run()
                
                if result:
                    self.memory.add_assistant_message(str(result))
                    await self.speak(str(result))
            except Exception as e:
                logger.error(f"Error executing semantic tool {tool_name}: {e}")
                await self.speak("Desculpe, tive um problema ao executar essa ação.")
        else:
            logger.warning(f"--- Ferramenta '{tool_name}' não encontrada ou comando não entendido ---")
            await self.speak("Desculpe, não entendi o que você quis dizer.")
