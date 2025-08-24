"""Shared utilities for ElevenLabs MCP servers."""

from .config import Config
from .client import ElevenLabsClient
from .models import (
    AgentConfig,
    ConversationData,
    DocumentData,
    ErrorResponse
)
from .utils import (
    format_success,
    format_error,
    validate_uuid,
    validate_elevenlabs_id,
    chunk_text,
    retry_with_backoff
)
from .exceptions import (
    ElevenLabsError,
    APIError,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ConfigurationError
)

__all__ = [
    # Configuration
    "Config",
    
    # Client
    "ElevenLabsClient",
    
    # Models
    "AgentConfig",
    "ConversationData",
    "DocumentData",
    "ErrorResponse",
    
    # Utilities
    "format_success",
    "format_error",
    "validate_uuid",
    "validate_elevenlabs_id",
    "chunk_text",
    "retry_with_backoff",
    
    # Exceptions
    "ElevenLabsError",
    "APIError",
    "ValidationError",
    "AuthenticationError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ConfigurationError"
]