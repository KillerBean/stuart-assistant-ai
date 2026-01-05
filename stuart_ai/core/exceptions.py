class StuartBaseException(Exception):
    """Base exception for Stuart AI."""
    pass

class LLMError(StuartBaseException):
    """Base exception for LLM related errors."""
    pass

class LLMConnectionError(LLMError):
    """Raised when there is a connection error with the LLM provider."""
    pass

class LLMResponseError(LLMError):
    """Raised when the LLM returns an invalid or unexpected response."""
    pass

class AudioError(StuartBaseException):
    """Base exception for audio related errors."""
    pass

class AudioDeviceError(AudioError):
    """Raised when there is an issue accessing or using audio devices."""
    pass

class TranscriptionError(AudioError):
    """Raised when transcription fails."""
    pass

class ToolError(StuartBaseException):
    """Base exception for tool related errors."""
    pass

class CommandExecutionError(ToolError):
    """Raised when a command fails to execute."""
    pass
