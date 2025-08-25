"""
Voice-specific utilities for ElevenLabs Voices MCP Server.

This module contains self-contained utilities for voice validation,
response formatting, and error handling. No external dependencies
from other servers.
"""

import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def format_success(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format a successful response.
    
    Args:
        message: Success message
        data: Optional data payload
        
    Returns:
        Formatted success response
    """
    response = {
        "success": True,
        "message": message
    }
    if data:
        response["data"] = data
    return response


def format_error(error: str, suggestion: Optional[str] = None) -> Dict[str, Any]:
    """
    Format an error response.
    
    Args:
        error: Error message
        suggestion: Optional suggestion for resolution
        
    Returns:
        Formatted error response
    """
    response = {
        "success": False,
        "error": error
    }
    if suggestion:
        response["suggestion"] = suggestion
    return response


def validate_voice_id(voice_id: str) -> bool:
    """
    Validate ElevenLabs voice ID format.
    
    Args:
        voice_id: Voice ID to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not voice_id:
        return False
        
    # ElevenLabs voice IDs are typically 20 characters, alphanumeric + some special chars
    if len(voice_id) != 20:
        return False
        
    # Allow alphanumeric characters and common special characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', voice_id):
        return False
        
    return True


def validate_generated_voice_id(generated_voice_id: str) -> bool:
    """
    Validate generated voice ID format (from text-to-voice).
    
    Args:
        generated_voice_id: Generated voice ID to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not generated_voice_id:
        return False
        
    # Generated voice IDs are typically longer and may have different format
    if len(generated_voice_id) < 10:
        return False
        
    # Allow alphanumeric and common special characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', generated_voice_id):
        return False
        
    return True


def validate_voice_name(name: str) -> bool:
    """
    Validate voice name.
    
    Args:
        name: Voice name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name or not name.strip():
        return False
        
    # Reasonable length limits
    if len(name.strip()) < 1 or len(name.strip()) > 100:
        return False
        
    return True


def validate_voice_description(description: str) -> bool:
    """
    Validate voice description.
    
    Args:
        description: Description to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not description or not description.strip():
        return False
        
    # Reasonable length limits
    if len(description.strip()) < 5 or len(description.strip()) > 1000:
        return False
        
    return True


def validate_stability(stability: float) -> bool:
    """
    Validate stability parameter.
    
    Args:
        stability: Stability value to validate
        
    Returns:
        True if valid range (0.0-1.0), False otherwise
    """
    return 0.0 <= stability <= 1.0


def validate_similarity_boost(similarity_boost: float) -> bool:
    """
    Validate similarity_boost parameter.
    
    Args:
        similarity_boost: Similarity boost value to validate
        
    Returns:
        True if valid range (0.0-1.0), False otherwise
    """
    return 0.0 <= similarity_boost <= 1.0


def validate_style(style: float) -> bool:
    """
    Validate style parameter.
    
    Args:
        style: Style value to validate
        
    Returns:
        True if valid range (0.0-1.0), False otherwise
    """
    return 0.0 <= style <= 1.0


def validate_page_size(page_size: int) -> bool:
    """
    Validate page size parameter.
    
    Args:
        page_size: Page size to validate
        
    Returns:
        True if valid range (1-100), False otherwise
    """
    return 1 <= page_size <= 100


def validate_audio_files(audio_files: List[str]) -> Dict[str, Any]:
    """
    Validate audio file paths for voice cloning.
    
    Args:
        audio_files: List of audio file paths
        
    Returns:
        Validation result with success status and details
    """
    if not audio_files:
        return {
            "valid": False,
            "error": "At least one audio file is required for voice cloning"
        }
        
    if len(audio_files) > 25:
        return {
            "valid": False,
            "error": "Maximum 25 audio files allowed for voice cloning"
        }
        
    # Check file extensions (common audio formats)
    valid_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.webm'}
    invalid_files = []
    
    for file_path in audio_files:
        if not file_path:
            invalid_files.append("Empty file path")
            continue
            
        # Check extension
        if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
            invalid_files.append(f"Invalid format: {file_path}")
            
    if invalid_files:
        return {
            "valid": False,
            "error": f"Invalid audio files: {', '.join(invalid_files)}",
            "suggestion": f"Use supported formats: {', '.join(valid_extensions)}"
        }
        
    return {"valid": True}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "voice_file"
        
    # Replace spaces and special characters
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Limit length
    if len(sanitized) > 100:
        name_part, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name_part[:95] + ('.' + ext if ext else '')
        
    return sanitized


def extract_voice_info(voice_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and format voice information from API response.
    
    Args:
        voice_data: Raw voice data from API
        
    Returns:
        Formatted voice information
    """
    if not voice_data:
        return {}
        
    info = {
        "voice_id": voice_data.get("voice_id"),
        "name": voice_data.get("name"),
        "category": voice_data.get("category", "Unknown"),
        "description": voice_data.get("description"),
        "preview_url": voice_data.get("preview_url"),
        "available_for_tiers": voice_data.get("available_for_tiers", []),
        "settings": voice_data.get("settings", {}),
        "samples": voice_data.get("samples", [])
    }
    
    # Remove None values
    return {k: v for k, v in info.items() if v is not None}


def format_voice_list(voices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format a list of voices for consistent output.
    
    Args:
        voices: List of voice data from API
        
    Returns:
        Formatted voice list
    """
    return [extract_voice_info(voice) for voice in voices if voice]


def get_voice_summary(voice_data: Dict[str, Any]) -> str:
    """
    Generate a summary string for a voice.
    
    Args:
        voice_data: Voice data
        
    Returns:
        Human-readable voice summary
    """
    if not voice_data:
        return "Unknown voice"
        
    name = voice_data.get("name", "Unnamed")
    category = voice_data.get("category", "Unknown")
    description = voice_data.get("description", "")
    
    summary = f"{name} ({category})"
    if description and len(description) < 50:
        summary += f" - {description}"
        
    return summary