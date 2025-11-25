from enum import Enum, auto

class AssistantSignal(Enum):
    """
    Defines signals for controlling the assistant's main loop.
    """
    QUIT = auto()
    # In the future, other signals like RESTART or SLEEP could be added here.
