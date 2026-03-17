from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class AssistantStatus(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


@dataclass
class AssistantContext:
    status: AssistantStatus = AssistantStatus.IDLE
    last_command: str | None = None
    last_response: str | None = None
    command_count: int = 0
    session_start: datetime = field(default_factory=datetime.now)

    def set_status(self, status: AssistantStatus):
        self.status = status

    def record_command(self, command: str):
        self.last_command = command
        self.command_count += 1

    def record_response(self, response: str):
        self.last_response = response

    def uptime_seconds(self) -> int:
        return int((datetime.now() - self.session_start).total_seconds())
