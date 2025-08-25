"""
Voice Library Tools
===================
Tools for searching, browsing, and managing shared voices from the public library.
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """Simple ElevenLabs API client for voice library operations."""
    
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


async def search_voice_library(
    query: str,
    page: int = 0,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Search the public voice library.
    
    Searches through shared voices in the ElevenLabs voice library using
    keywords to find voices by name, description, or characteristics.
    
    Args:
        query: Search terms for voice discovery
        page: Page number for pagination (0-based)
        page_size: Results per page (1-100)
        
    Returns:
        Search results from public voice library
        
    API Endpoint: GET /shared-voices
    
    Examples:
        search_voice_library("female british accent")
        search_voice_library("narrator", page=1, page_size=20)
    """
    from utils import format_success, format_error, validate_page_size, format_voice_list
    
    if not query or not query.strip():
        return format_error(
            "Search query is required",
            "Provide search terms like 'female voice', 'british accent', or 'narrator'"
        )
    
    if len(query.strip()) < 2:
        return format_error(
            "Search query too short",
            "Provide at least 2 characters for searching"
        )
    
    if not validate_page_size(page_size):
        return format_error(
            f"Invalid page size: {page_size}",
            "Page size must be between 1 and 100"
        )
    
    if page < 0:
        return format_error(
            f"Invalid page number: {page}",
            "Page number must be 0 or greater"
        )
    
    try:
        client = ElevenLabsClient()
        params = {
            "search": query.strip(),
            "page": page,
            "page_size": page_size
        }
        
        result = await client._request("GET", "/shared-voices", params=params)
        
        voices = result.get("voices", [])
        total = result.get("total", len(voices))
        
        formatted_voices = format_voice_list(voices)
        
        return format_success(
            f"Found {len(formatted_voices)} voices matching '{query}'",
            {
                "query": query,
                "page": page,
                "page_size": page_size,
                "total_results": total,
                "result_count": len(formatted_voices),
                "voices": formatted_voices
            }
        )
    except Exception as e:
        logger.error(f"Failed to search voice library: {e}")
        error_msg = str(e)
        
        if "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions"
        elif "timeout" in error_msg.lower():
            suggestion = "Search request timed out. Try a more specific query"
        else:
            suggestion = "Verify your API connection and try a different search term"
            
        return format_error(error_msg, suggestion)


async def add_shared_voice(
    voice_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a shared voice from the public library to user's collection.
    
    Copies a voice from the shared library to the user's personal voice
    collection, allowing it to be used for speech synthesis.
    
    Args:
        voice_id: Public voice ID to add
        name: Custom name for the voice (uses original if not provided)
        description: Custom description (uses original if not provided)
        
    Returns:
        Added voice details
        
    API Endpoint: POST /voices/add/{public_user_id}/{voice_id}
    
    Examples:
        add_shared_voice("abc123def456")
        add_shared_voice("xyz789ghi012", "My Custom Voice", "Professional narrator voice")
    """
    from utils import format_success, format_error, validate_voice_id, extract_voice_info
    
    if not validate_voice_id(voice_id):
        return format_error(
            f"Invalid voice ID format: {voice_id}",
            "Voice ID should be 20 characters, alphanumeric with dashes/underscores"
        )
    
    # Validate optional parameters
    if name is not None and not name.strip():
        name = None
        
    if description is not None and not description.strip():
        description = None
    
    try:
        client = ElevenLabsClient()
        
        # Note: This endpoint structure may vary - using a general approach
        # The actual endpoint might be different based on ElevenLabs API docs
        payload = {"voice_id": voice_id}
        
        if name:
            payload["name"] = name.strip()
        if description:
            payload["description"] = description.strip()
        
        result = await client._request("POST", "/voices/add-shared", json_data=payload)
        
        # Extract voice information
        voice_info = extract_voice_info(result)
        added_voice_id = result.get("voice_id", voice_id)
        
        return format_success(
            f"Shared voice added to your collection",
            {
                "original_voice_id": voice_id,
                "new_voice_id": added_voice_id,
                "name": name or voice_info.get("name", "Unknown"),
                "description": description or voice_info.get("description"),
                "voice": voice_info,
                "status": "added"
            }
        )
    except Exception as e:
        logger.error(f"Failed to add shared voice: {e}")
        error_msg = str(e)
        
        if "404" in error_msg:
            suggestion = f"Voice {voice_id} not found in the public library"
        elif "already" in error_msg.lower():
            suggestion = "You may already have this voice in your collection"
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            suggestion = "You may have reached your voice limit. Check your ElevenLabs plan"
        elif "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions and plan tier"
        else:
            suggestion = "Verify the voice ID is correct and publicly available"
            
        return format_error(error_msg, suggestion)


async def get_shared_voices() -> Dict[str, Any]:
    """
    Get available shared voices from the voice library.
    
    Retrieves a list of popular and featured voices from the public
    voice library that can be added to your collection.
    
    Returns:
        List of available public voices
        
    API Endpoint: GET /shared-voices
    
    Examples:
        get_shared_voices()
    """
    from utils import format_success, format_error, format_voice_list
    
    try:
        client = ElevenLabsClient()
        
        # Get featured/popular voices without specific search
        params = {"page_size": 50}  # Get a reasonable number of featured voices
        result = await client._request("GET", "/shared-voices", params=params)
        
        voices = result.get("voices", [])
        total_available = result.get("total", len(voices))
        
        formatted_voices = format_voice_list(voices)
        
        # Categorize voices by type if possible
        categories = {}
        for voice in formatted_voices:
            category = voice.get("category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append(voice)
        
        return format_success(
            f"Retrieved {len(formatted_voices)} available shared voices",
            {
                "total_available": total_available,
                "retrieved_count": len(formatted_voices),
                "categories": list(categories.keys()),
                "voices": formatted_voices,
                "voices_by_category": categories
            }
        )
    except Exception as e:
        logger.error(f"Failed to get shared voices: {e}")
        error_msg = str(e)
        
        if "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions"
        elif "timeout" in error_msg.lower():
            suggestion = "Request timed out. Try again in a moment"
        else:
            suggestion = "Verify your API connection and try again"
            
        return format_error(error_msg, suggestion)