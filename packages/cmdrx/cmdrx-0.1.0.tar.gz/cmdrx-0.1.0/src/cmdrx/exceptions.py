"""
CmdRx Exception Classes

Custom exception classes for CmdRx error handling.
"""


class CmdRxError(Exception):
    """Base exception class for CmdRx errors."""
    pass


class ConfigurationError(CmdRxError):
    """Raised when there are configuration-related errors."""
    pass


class LLMError(CmdRxError):
    """Raised when there are LLM service-related errors."""
    pass


class InputError(CmdRxError):
    """Raised when there are input processing errors."""
    pass


class OutputError(CmdRxError):
    """Raised when there are output generation errors."""
    pass


class SecurityError(CmdRxError):
    """Raised when there are security-related errors."""
    pass