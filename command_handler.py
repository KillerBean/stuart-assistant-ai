import platform
import subprocess
from datetime import datetime

import requests
import wikipedia


class CommandHandler:
    """Handles the processing of voice commands."""

    def __init__(self, speak_func, confirmation_func, app_aliases):
        self.speak = speak_func
        self.confirm = confirmation_func
        self.app_aliases = app_aliases
        self.commands = {
            "que horas são": self._get_time,
            "conte uma piada": self._tell_joke,
            "pesquise sobre": self._search_wikipedia,
            "o que é": self._search_wikipedia,
            "previsão do tempo": self._get_weather,
            "abra": self._open_app,
            "inicie": self._open_app,
            "desligar o computador": self._shutdown_computer,
        }

    def process(self, command: str):
        """Finds and executes the appropriate command."""
        #TODO: Melhorar o sistema de correspondência de comandos para ser mais flexível
        try:
            for keyword, function in self.commands.items():
                if command.startswith(keyword):
                    function(command)
                    return
            self.speak("Desculpe, não entendi o comando.")
        except Exception as e:
            print(f"Error processing command '{command}': {e}")
            self.speak("Desculpe, ocorreu um erro ao processar o comando.")

    def _get_time(self, command: str):
        now = datetime.now().strftime("%H:%M")
        self.speak(f"São {now}.")

    def _tell_joke(self, command: str):
        try:
            url = "https://v2.jokeapi.dev/joke/Any?lang=pt&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
            response = requests.get(url)
            response.raise_for_status()
            joke_data = response.json()

            joke = joke_data['joke'] if joke_data.get('type') == 'single' else f"{joke_data['setup']} ... {joke_data['delivery']}"
            self.speak(joke)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching joke from API: {e}")
            self.speak("Desculpe, não consegui buscar uma piada agora.")

    def _search_wikipedia(self, command: str):
        search_term = command.replace("pesquise sobre", "").replace("o que é", "").strip()
        if not search_term:
            self.speak("Claro, o que você gostaria que eu pesquisasse?")
            return
        self.speak(f"Claro, pesquisando sobre {search_term} na Wikipedia.")
        try:
            summary = wikipedia.summary(search_term, sentences=2)
            self.speak(summary)
        except wikipedia.exceptions.PageError:
            self.speak(f"Desculpe, não encontrei nenhum resultado para {search_term}.")
        except wikipedia.exceptions.DisambiguationError:
            self.speak(f"O termo {search_term} é muito vago. Por favor, seja mais específico.")

    def _get_weather(self, command: str):
        city = command.split("para")[-1].strip() if "para" in command else ""
        if not city:
            self.speak("Claro, para qual cidade você gostaria da previsão do tempo?")
            return
        self.speak(f"Verificando a previsão do tempo para {city}.")
        try:
            url = f"https://wttr.in/{city}?format=3"
            response = requests.get(url)
            response.raise_for_status()
            self.speak(response.text)
        except requests.exceptions.RequestException:
            self.speak(f"Desculpe, não consegui obter a previsão do tempo para {city}.")

    def _open_app(self, command: str):
        spoken_name = command.replace("abra", "").replace("inicie", "").strip()
        if not spoken_name:
            self.speak("Claro, qual programa você gostaria de abrir?")
            return
        
        #TODO: Melhorar o mapeamento de nomes falados para nomes de executáveis
        #TODO: filtrar opções para fins de segurança

        system = platform.system()
        executable_name = spoken_name

        if spoken_name in self.app_aliases and system in self.app_aliases[spoken_name]:
            executable_name = self.app_aliases[spoken_name][system]

        self.speak(f"Ok, abrindo {spoken_name}.")
        try:
            if system == "Windows":
                subprocess.Popen(['start', executable_name], shell=True)
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', '-a', executable_name])
            else:  # Linux
                subprocess.Popen([executable_name])
        except FileNotFoundError:
            self.speak(f"Desculpe, não consegui encontrar o programa {spoken_name}.")
        except Exception as e:
            print(f"Error opening application: {e}")
            self.speak(f"Ocorreu um erro ao tentar abrir o {spoken_name}.")

    def _shutdown_computer(self, command: str):
        if self.confirm("Você tem certeza que deseja desligar o computador?"):
            self.speak("Ok, desligando o computador em 30 segundos. Adeus!")
            system = platform.system()
            try:
                if system == "Windows":
                    subprocess.run(["shutdown", "/s", "/t", "30"])
                elif system == "Linux" or system == "Darwin":  # Linux ou macOS
                    subprocess.run(["shutdown", "-h", "+1"]) # Desliga em 1 minuto
                else:
                    self.speak("Desculpe, não sei como desligar o computador neste sistema.")
            except Exception as e:
                print(f"Error trying to shutdown: {e}")
                self.speak("Ocorreu um erro ao tentar executar o comando de desligamento.")
        else:
            self.speak("Ação cancelada.")

    def _cancel_shutdown(self, command: str):
        self.speak("Cancelando o desligamento do computador.")
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(["shutdown", "/a"])
            elif system == "Linux" or system == "Darwin":  # Linux ou macOS
                subprocess.run(["shutdown", "-c"])
            else:
                self.speak("Desculpe, não sei como cancelar o desligamento neste sistema.")
        except Exception as e:
            print(f"Error trying to cancel shutdown: {e}")
            self.speak("Ocorreu um erro ao tentar cancelar o comando de desligamento.")