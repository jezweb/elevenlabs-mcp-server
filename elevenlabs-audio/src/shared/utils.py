"""Utility functions for ElevenLabs MCP servers."""

import asyncio
import functools
import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar
from uuid import UUID

logger = logging.getLogger(__name__)

T = TypeVar("T")


def format_success(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Format a successful response."""
    response = {
        "success": True,
        "message": message
    }
    if data:
        response["data"] = data
    return response


def format_error(error: str, details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None) -> Dict[str, Any]:
    """Format an error response."""
    response = {
        "success": False,
        "error": error
    }
    if details:
        response["details"] = details
    if suggestion:
        response["suggestion"] = suggestion
    return response


def validate_uuid(value: str) -> bool:
    """Validate if a string is a valid UUID."""
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def validate_elevenlabs_id(value: str, id_type: Optional[str] = None) -> bool:
    """
    Validate ElevenLabs-specific ID formats.
    
    Args:
        value: The ID string to validate
        id_type: Optional type hint ('agent', 'conversation', 'document', etc.)
    
    Returns:
        True if the ID matches ElevenLabs format patterns
    
    Examples:
        - Agent ID: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX (agent_ + 30 chars)
        - Conversation ID: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX (conv_ + 29 chars)  
        - Document ID: alphanumeric string (variable length)
        - Command ID: command_XXXXXXXXXXXXXXXXXXXXXXXXXX
    """
    if not value or not isinstance(value, str):
        return False
    
    # Check for standard UUID first (some IDs might be UUIDs)
    if validate_uuid(value):
        return True
    
    # ElevenLabs specific patterns
    patterns = {
        'agent': r'^agent_[a-zA-Z0-9]{28}$',
        'conversation': r'^conv_[a-zA-Z0-9]{28}$', 
        'command': r'^command_[a-zA-Z0-9]{26}$',
        'document': r'^[a-zA-Z0-9]{16,32}$',  # Variable length alphanumeric
        'phone': r'^phone_[a-zA-Z0-9]{24}$',
        'webhook': r'^webhook_[a-zA-Z0-9]{24}$'
    }
    
    import re
    
    # If specific type provided, check that pattern
    if id_type and id_type in patterns:
        return bool(re.match(patterns[id_type], value))
    
    # Otherwise check all patterns
    for pattern in patterns.values():
        if re.match(pattern, value):
            return True
    
    # Also accept simple alphanumeric strings of reasonable length
    # (for document IDs and other resources)
    if re.match(r'^[a-zA-Z0-9]{8,40}$', value):
        return True
    
    return False


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Calculate end position
        end = min(start + chunk_size, text_length)
        
        # Try to break at a sentence or word boundary
        if end < text_length:
            # Look for sentence end
            for sep in [". ", "! ", "? ", "\n\n", "\n", " "]:
                last_sep = text.rfind(sep, start, end)
                if last_sep != -1:
                    end = last_sep + len(sep)
                    break
        
        # Extract chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < text_length else text_length
    
    return chunks


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
) -> Callable:
    """Decorator for retrying async functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        sleep_time = min(delay, max_delay)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {sleep_time:.1f}s..."
                        )
                        await asyncio.sleep(sleep_time)
                        delay *= exponential_base
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1
        filename = f"{name[:max_name_length]}.{ext}" if ext else name[:255]
    return filename


def parse_bool(value: Any) -> bool:
    """Parse various representations of boolean values."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on', 'enabled')
    return bool(value)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_error_message(exception: Exception) -> str:
    """Extract a clean error message from an exception."""
    error_str = str(exception)
    
    # Remove common prefixes
    prefixes_to_remove = [
        "Error: ",
        "Exception: ",
        "Failed: ",
        "Invalid: "
    ]
    
    for prefix in prefixes_to_remove:
        if error_str.startswith(prefix):
            error_str = error_str[len(prefix):]
            break
    
    # Capitalize first letter
    if error_str and error_str[0].islower():
        error_str = error_str[0].upper() + error_str[1:]
    
    return error_str


def calculate_duration(start_time: float, end_time: Optional[float] = None) -> float:
    """Calculate duration in seconds."""
    if end_time is None:
        end_time = time.time()
    return round(end_time - start_time, 2)


def merge_dicts(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from a dictionary."""
    return {k: v for k, v in data.items() if v is not None}


async def run_with_timeout(coro, timeout_seconds: int):
    """Run a coroutine with a timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")