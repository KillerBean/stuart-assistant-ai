from collections import deque
from typing import List, Dict
from stuart_ai.core.config import settings

class ConversationMemory:
    def __init__(self):
        # deque automatically discards old items when maxlen is reached
        self.history = deque(maxlen=settings.memory_window_size)

    def add_user_message(self, message: str):
        self.history.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str):
        self.history.append({"role": "assistant", "content": message})

    def get_history(self) -> List[Dict[str, str]]:
        """Returns the history as a list of dictionaries."""
        return list(self.history)

    def get_formatted_history(self) -> str:
        """Returns history formatted as a string for LLM prompts."""
        formatted = ""
        for msg in self.history:
            role = "Usuário" if msg["role"] == "user" else "Stuart"
            formatted += f"{role}: {msg['content']}\n"
        return formatted

    def clear(self):
        self.history.clear()
