"""
Voice Settings Tools
====================
Tools for configuring and managing voice generation settings.
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """Simple ElevenLabs API client for voice settings operations."""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.base_url}{endpoint}"
        headers = {"xi-api-key": self.api_key}
        
        if json_data:
            headers["Content-Type"] = "application/json"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, json=json_data, params=params, headers=headers
            ) as response:
                if response.status not in [200, 201, 204]:
                    error_text = await response.text()
                    raise Exception(f"API request failed ({response.status}): {error_text}")
                
                if response.status == 204:
                    return {"success": True}
                
                return await response.json()


async def voice_settings(
    voice_id: str,
    stability: Optional[float] = None,
    similarity_boost: Optional[float] = None,
    style: Optional[float] = None,
    use_speaker_boost: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Configure voice generation settings.
    
    Updates the default settings for a voice that will be used for
    speech synthesis. These settings affect the voice's consistency,
    similarity to original, and style characteristics.
    
    Args:
        voice_id: Voice to configure
        stability: Voice stability/consistency (0.0-1.0)
            - Lower values: More variable, expressive
            - Higher values: More consistent, stable
        similarity_boost: Similarity to original voice (0.0-1.0)
            - Lower values: More creative freedom
            - Higher values: Closer to original voice
        style: Style exaggeration (0.0-1.0)
            - Lower values: More natural
            - Higher values: More exaggerated style
        use_speaker_boost: Enable speaker boost for similarity
        
    Returns:
        Updated voice settings
        
    API Endpoint: POST /voices/{voice_id}/settings
    
    Examples:
        voice_settings("abc123", stability=0.7, similarity_boost=0.8)
        voice_settings("def456", stability=0.3, style=0.6, use_speaker_boost=True)
    """
    from utils import (
        format_success, format_error, validate_voice_id,
        validate_stability, validate_similarity_boost, validate_style
    )
    
    if not validate_voice_id(voice_id):
        return format_error(
            f"Invalid voice ID format: {voice_id}",
            "Voice ID should be 20 characters, alphanumeric with dashes/underscores"
        )
    
    # Validate parameter ranges
    if stability is not None and not validate_stability(stability):
        return format_error(
            f"Invalid stability value: {stability}",
            "Stability must be between 0.0 and 1.0"
        )
    
    if similarity_boost is not None and not validate_similarity_boost(similarity_boost):
        return format_error(
            f"Invalid similarity_boost value: {similarity_boost}",
            "Similarity boost must be between 0.0 and 1.0"
        )
    
    if style is not None and not validate_style(style):
        return format_error(
            f"Invalid style value: {style}",
            "Style must be between 0.0 and 1.0"
        )
    
    # Build settings payload
    settings = {}
    if stability is not None:
        settings["stability"] = stability
    if similarity_boost is not None:
        settings["similarity_boost"] = similarity_boost
    if style is not None:
        settings["style"] = style
    if use_speaker_boost is not None:
        settings["use_speaker_boost"] = use_speaker_boost
    
    if not settings:
        return format_error(
            "No settings provided",
            "Provide at least one setting to update: stability, similarity_boost, style, or use_speaker_boost"
        )
    
    try:
        client = ElevenLabsClient()
        result = await client._request("POST", f"/voices/{voice_id}/settings", json_data=settings)
        
        # Get the updated settings
        updated_settings = result.get("settings", settings)
        
        return format_success(
            f"Voice settings updated for {voice_id}",
            {
                "voice_id": voice_id,
                "updated_settings": updated_settings,
                "settings_applied": settings
            }
        )
    except Exception as e:
        logger.error(f"Failed to update voice settings: {e}")
        error_msg = str(e)
        
        if "404" in error_msg:
            suggestion = f"Voice {voice_id} not found. Check the voice ID or list available voices"
        elif "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions"
        elif "validation" in error_msg.lower() or "invalid" in error_msg.lower():
            suggestion = "Check that all parameter values are within valid ranges (0.0-1.0)"
        else:
            suggestion = "Verify your API connection and voice ID"
            
        return format_error(error_msg, suggestion)


async def get_voice_settings(voice_id: str) -> Dict[str, Any]:
    """
    Get current voice settings and configuration.
    
    Retrieves the current generation settings for a voice, including
    stability, similarity boost, style, and speaker boost settings.
    
    Args:
        voice_id: Voice ID to get settings for
        
    Returns:
        Current voice configuration
        
    API Endpoint: GET /voices/{voice_id}/settings
    
    Examples:
        get_voice_settings("abc123def456ghi789")
    """
    from utils import format_success, format_error, validate_voice_id
    
    if not validate_voice_id(voice_id):
        return format_error(
            f"Invalid voice ID format: {voice_id}",
            "Voice ID should be 20 characters, alphanumeric with dashes/underscores"
        )
    
    try:
        client = ElevenLabsClient()
        result = await client._request("GET", f"/voices/{voice_id}/settings")
        
        settings = result.get("settings", {})
        
        # Provide default values if not present
        default_settings = {
            "stability": settings.get("stability", 0.75),
            "similarity_boost": settings.get("similarity_boost", 0.75),
            "style": settings.get("style", 0.0),
            "use_speaker_boost": settings.get("use_speaker_boost", True)
        }
        
        # Add helpful descriptions
        settings_with_descriptions = {
            "stability": {
                "value": default_settings["stability"],
                "description": "Voice consistency (0.0=variable/expressive, 1.0=stable/consistent)"
            },
            "similarity_boost": {
                "value": default_settings["similarity_boost"],
                "description": "Similarity to original (0.0=creative freedom, 1.0=strict adherence)"
            },
            "style": {
                "value": default_settings["style"],
                "description": "Style exaggeration (0.0=natural, 1.0=exaggerated)"
            },
            "use_speaker_boost": {
                "value": default_settings["use_speaker_boost"],
                "description": "Enhanced similarity to original speaker"
            }
        }
        
        return format_success(
            f"Voice settings retrieved for {voice_id}",
            {
                "voice_id": voice_id,
                "settings": default_settings,
                "settings_with_descriptions": settings_with_descriptions,
                "usage_tips": {
                    "conversational": {"stability": 0.7, "similarity_boost": 0.8, "style": 0.1},
                    "professional": {"stability": 0.9, "similarity_boost": 0.9, "style": 0.0},
                    "expressive": {"stability": 0.3, "similarity_boost": 0.5, "style": 0.7}
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to get voice settings: {e}")
        error_msg = str(e)
        
        if "404" in error_msg:
            suggestion = f"Voice {voice_id} not found. Check the voice ID or list available voices"
        elif "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions"
        else:
            suggestion = "Verify your API connection and voice ID"
            
        return format_error(error_msg, suggestion)