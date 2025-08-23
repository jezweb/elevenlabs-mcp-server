"""Custom exceptions for ElevenLabs MCP servers."""


class ElevenLabsError(Exception):
    """Base exception for ElevenLabs errors."""
    pass


class APIError(ElevenLabsError):
    """API request failed."""
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(ElevenLabsError):
    """Input validation failed."""
    pass


class AuthenticationError(ElevenLabsError):
    """Authentication failed."""
    pass


class RateLimitError(ElevenLabsError):
    """API rate limit exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message)


class ResourceNotFoundError(ElevenLabsError):
    """Requested resource not found."""
    pass


class ConfigurationError(ElevenLabsError):
    """Configuration is invalid or incomplete."""
    pass