class StuartBaseException(Exception):
    """Base exception for Stuart AI."""


class LLMError(StuartBaseException):
    """Base exception for LLM related errors."""


class LLMConnectionError(LLMError):
    """Raised when there is a connection error with the LLM provider."""


class LLMResponseError(LLMError):
    """Raised when the LLM returns an invalid or unexpected response."""


class AudioError(StuartBaseException):
    """Base exception for audio related errors."""


class AudioDeviceError(AudioError):
    """Raised when there is an issue accessing or using audio devices."""


class TranscriptionError(AudioError):
    """Raised when transcription fails."""


class ToolError(StuartBaseException):
    """Base exception for tool related errors."""


class CommandExecutionError(ToolError):
    """Raised when a command fails to execute."""
