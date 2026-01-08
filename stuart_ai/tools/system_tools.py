import os
import platform
import subprocess
import asyncio
from datetime import datetime

import aiohttp
import wikipedia

from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.agents.rag.rag_agent import LocalRAGAgent
from stuart_ai.agents.productivity.calendar_manager import CalendarManager
from stuart_ai.core.enums import AssistantSignal
from stuart_ai.core.logger import logger



class AssistantTools:
    """
    A class to encapsulate all the tools available to the assistant's router agent.
    Each tool should return a string to be spoken by the command handler.
    """

    def __init__(self, speak_func, confirmation_func, app_aliases, web_search_agent: WebSearchAgent, local_rag_agent: LocalRAGAgent):
        self.speak = speak_func
        self.confirm = confirmation_func
        self.app_aliases = app_aliases
        self.web_search_agent = web_search_agent
        self.local_rag_agent = local_rag_agent
        self.calendar_manager = CalendarManager()

    async def _add_calendar_event(self, args: dict | str) -> str:
        """Agendar um compromisso."""
        try:
            if isinstance(args, str):
                # Fallback if LLM returns string
                return "Preciso que você especifique o título e a hora separadamente."
            
            title = args.get("title")
            datetime_str = args.get("datetime")
            
            if not title or not datetime_str:
                return "Preciso do nome do evento e da data/hora."

            await self.speak(f"Agendando {title} para {datetime_str}...")
            return self.calendar_manager.add_event(title, datetime_str)
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            return "Tive um problema ao salvar o evento."

    async def _check_calendar(self, date_str: str | None = None) -> str:
        """Consultar agenda."""
        await self.speak("Consultando sua agenda...")
        return self.calendar_manager.list_events(date_str)

    async def _delete_calendar_event(self, event_title: str) -> str:
        """Excluir um compromisso."""
        await self.speak(f"Excluindo o evento {event_title}...")
        return self.calendar_manager.delete_event(event_title)

    async def _search_local_files(self, query: str) -> str:
        """Pesquisa nos arquivos locais indexados. Use quando o usuário perguntar sobre documentos, arquivos ou 'o que diz o arquivo X'."""
        if not query:
            return "O que você gostaria de pesquisar nos seus arquivos?"
        
        await self.speak("Pesquisando nos seus arquivos...")
        try:
            return await self.local_rag_agent.run(query)
        except Exception as e:
            logger.error(f"Error querying local files: {e}")
            return "Desculpe, tive um erro ao consultar seus arquivos."

    async def _index_file(self, file_path: str) -> str:
        """Adiciona um arquivo ao índice de busca local. Use quando o usuário pedir para 'ler', 'aprender' ou 'indexar' um arquivo."""
        if not file_path:
             return "Qual arquivo você gostaria que eu aprendesse?"
        
        # Simple cleanup of path if user spoke it (though usually this tool argument comes from semantic router resolving path)
        file_path = file_path.strip().strip('"').strip("'")
        
        await self.speak(f"Processando o arquivo {os.path.basename(file_path)}...")
        try:
            # We run the blocking add_document in a thread
            await asyncio.to_thread(self.local_rag_agent.document_store.add_document, file_path)
            return f"Arquivo {os.path.basename(file_path)} aprendido com sucesso!"
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
            return f"Não consegui ler o arquivo. Verifique se o caminho está correto."


    async def _get_time(self) -> str:
        """Retorna a hora e os minutos atuais. Use esta ferramenta sempre que o usuário perguntar as horas."""
        now = datetime.now().strftime("%H:%M")
        return f"São {now}."

    async def _get_date(self) -> str:
        """Retorna a data atual. Use quando o usuário perguntar que dia é hoje."""
        now = datetime.now()
        # Format: Segunda-feira, 05 de Janeiro de 2026 (requires locale)
        # Or simple: 05/01/2026
        return f"Hoje é {now.strftime('%d/%m/%Y')}."

    async def _tell_joke(self) -> str:
        """Conta uma piada aleatória em português. Use quando o usuário pedir para contar uma piada."""
        try:
            url = "https://v2.jokeapi.dev/joke/Any?lang=pt&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    joke_data = await response.json()
                    return joke_data['joke'] if joke_data.get('type') == 'single' else f"{joke_data['setup']} ... {joke_data['delivery']}"
        except Exception as e:
            logger.error(f"Error fetching joke from API: {e}")
            return "Desculpe, não consegui buscar uma piada agora."

    async def _search_wikipedia(self, search_term: str) -> str:
        """Pesquisa um termo na Wikipedia e retorna um resumo. Use para perguntas sobre 'o que é' ou 'pesquise sobre'."""
        if not search_term:
            return "Claro, o que você gostaria que eu pesquisasse?"
        
        try:
            # wikipedia library is blocking, run in thread
            def get_summary():
                wikipedia.set_lang("pt")
                return wikipedia.summary(search_term, sentences=2)
            
            return await asyncio.to_thread(get_summary)
        except wikipedia.exceptions.PageError:
            return f"Desculpe, não encontrei nenhum resultado para {search_term}."
        except wikipedia.exceptions.DisambiguationError:
            return f"O termo {search_term} é muito vago. Por favor, seja mais específico."
        except Exception as e:
            logger.error(f"Error searching Wikipedia for '{search_term}': {e}")
            return "Desculpe, ocorreu um erro ao pesquisar no Wikipedia."

    async def _get_weather(self, city: str) -> str:
        """Obtém a previsão do tempo para uma cidade específica."""
        if not city:
            return "Claro, para qual cidade você gostaria da previsão do tempo?"
        
        try:
            url = f"https://wttr.in/{city}?format=3"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
        except Exception as e:
            logger.error(f"Error getting weather for '{city}': {e}")
            return f"Desculpe, não consegui obter a previsão do tempo para {city}."


    async def _open_app(self, app_name: str) -> str:
        """Abre ou inicia um programa no computador. Use para comandos como 'abra o chrome' ou 'inicie o vscode'."""
        spoken_name = app_name.strip()
        if not spoken_name:
            return "Claro, qual programa você gostaria de abrir?"

        system = platform.system()
        executable_name = spoken_name.lower()

        if spoken_name in self.app_aliases and system in self.app_aliases[spoken_name]:
            executable_name = self.app_aliases[spoken_name][system]

        try:
            if system == "Windows":
                await asyncio.to_thread(subprocess.Popen, ['start', executable_name], shell=True)
            elif system == "Darwin":
                await asyncio.to_thread(subprocess.Popen, ['open', '-a', executable_name])
            else:
                await asyncio.to_thread(subprocess.Popen, [executable_name])
            return f"Abrindo {spoken_name}."
        except FileNotFoundError:
            return f"Desculpe, não consegui encontrar o programa {spoken_name}."
        except Exception as e:
            logger.error(f"Error opening application: {e}")
            return f"Ocorreu um erro ao tentar abrir o {spoken_name}."

    async def _shutdown_computer(self) -> str:
        """Desliga o computador após uma confirmação do usuário."""
        if await self.confirm("Você tem certeza que deseja desligar o computador?"):
            system = platform.system()
            try:
                if system == "Windows":
                    await asyncio.to_thread(subprocess.run, ["shutdown", "/s", "/t", "60"])
                else:  # Linux ou macOS
                    await asyncio.to_thread(subprocess.run, ["shutdown", "-h", "+1"])
                return "Ok, desligando o computador em 1 minuto. Adeus!"
            except Exception as e:
                logger.error(f"Error trying to shutdown: {e}")
                return "Ocorreu um erro ao tentar executar o comando de desligamento."
        else:
            return "Ação de desligamento cancelada."

    async def _cancel_shutdown(self) -> str:
        """Cancela um desligamento do computador agendado."""
        system = platform.system()
        try:
            if system == "Windows":
                await asyncio.to_thread(subprocess.run, ["shutdown", "/a"])
            else:  # Linux ou macOS
                await asyncio.to_thread(subprocess.run, ["shutdown", "-c"])
            return "Desligamento cancelado."
        except Exception as e:
            logger.error(f"Error trying to cancel shutdown: {e}")
            return "Ocorreu um erro ao tentar cancelar o comando de desligamento."

    async def _perform_web_search(self, search_query: str) -> str:
        """Pesquisa na web usando um agente de IA para encontrar informações sobre um tópico. Use para pesquisas complexas ou quando a Wikipedia não for suficiente."""
        if not search_query:
            return "Claro, o que você gostaria que eu pesquisasse na web?"
        
        await self.speak(f"Ok, pesquisando na web sobre {search_query}. Isso pode levar um momento.")
        try:
            # Agent run might be blocking, run in thread
            result = await asyncio.to_thread(self.web_search_agent.run, search_query)
            return f"A pesquisa retornou o seguinte: {str(result)}"
        except Exception as e:
            logger.error(f"Error performing web search for '{search_query}': {e}")
            return "Desculpe, ocorreu um erro ao realizar a pesquisa na web."

    async def _quit(self) -> AssistantSignal:
        """Encerra o assistente. Use quando o usuário disser 'sair', 'encerrar' ou 'tchau'."""
        await self.speak("Encerrando a assistente. Até logo!")
        return AssistantSignal.QUIT

