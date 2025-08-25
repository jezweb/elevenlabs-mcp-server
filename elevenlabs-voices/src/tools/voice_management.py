"""
Voice Management Tools
======================
Tools for basic CRUD operations on voices.
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """Simple ElevenLabs API client for voice operations."""
    
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


async def get_voice(voice_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific voice.
    
    Args:
        voice_id: ElevenLabs voice ID to retrieve
        
    Returns:
        Voice details including settings, samples, and metadata
        
    API Endpoint: GET /voices/{voice_id}
    """
    from utils import format_success, format_error, validate_voice_id, extract_voice_info
    
    if not validate_voice_id(voice_id):
        return format_error(
            f"Invalid voice ID format: {voice_id}",
            "Voice ID should be 20 characters, alphanumeric with dashes/underscores"
        )
    
    try:
        client = ElevenLabsClient()
        result = await client._request("GET", f"/voices/{voice_id}")
        
        voice_info = extract_voice_info(result)
        
        return format_success(
            f"Voice '{voice_info.get('name', voice_id)}' retrieved",
            {"voice": voice_info}
        )
    except Exception as e:
        logger.error(f"Failed to get voice {voice_id}: {e}")
        error_msg = str(e)
        
        if "404" in error_msg:
            suggestion = f"Voice {voice_id} not found. Check the voice ID or list available voices"
        elif "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions"
        else:
            suggestion = "Verify your API connection and try again"
            
        return format_error(error_msg, suggestion)


async def list_voices(page_size: int = 30) -> Dict[str, Any]:
    """
    List all voices in the user's voice library.
    
    Args:
        page_size: Number of voices per page (1-100)
        
    Returns:
        List of user's voices with metadata
        
    API Endpoint: GET /voices
    """
    from utils import format_success, format_error, validate_page_size, format_voice_list
    
    if not validate_page_size(page_size):
        return format_error(
            f"Invalid page size: {page_size}",
            "Page size must be between 1 and 100"
        )
    
    try:
        client = ElevenLabsClient()
        params = {"page_size": page_size}
        result = await client._request("GET", "/voices", params=params)
        
        voices = result.get("voices", [])
        formatted_voices = format_voice_list(voices)
        
        return format_success(
            f"Retrieved {len(formatted_voices)} voices",
            {
                "count": len(formatted_voices),
                "voices": formatted_voices,
                "page_size": page_size
            }
        )
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        error_msg = str(e)
        
        if "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions"
        else:
            suggestion = "Verify your API connection and try again"
            
        return format_error(error_msg, suggestion)


async def delete_voice(voice_id: str) -> Dict[str, Any]:
    """
    Delete a voice from the user's library.
    
    Args:
        voice_id: Voice ID to delete
        
    Returns:
        Deletion confirmation
        
    API Endpoint: DELETE /voices/{voice_id}
    """
    from utils import format_success, format_error, validate_voice_id
    
    if not validate_voice_id(voice_id):
        return format_error(
            f"Invalid voice ID format: {voice_id}",
            "Voice ID should be 20 characters, alphanumeric with dashes/underscores"
        )
    
    try:
        client = ElevenLabsClient()
        await client._request("DELETE", f"/voices/{voice_id}")
        
        return format_success(f"Voice {voice_id} deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete voice {voice_id}: {e}")
        error_msg = str(e)
        
        if "404" in error_msg:
            suggestion = f"Voice {voice_id} not found. It may have already been deleted"
        elif "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions"
        elif "cannot delete" in error_msg.lower():
            suggestion = "This voice cannot be deleted (may be a default or premium voice)"
        else:
            suggestion = "Verify your API connection and try again"
            
        return format_error(error_msg, suggestion)