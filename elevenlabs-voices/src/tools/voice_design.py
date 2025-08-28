"""
Voice Design Tools
==================
Tools for creating voices from text descriptions (Text-to-Voice).
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """Simple ElevenLabs API client for voice design operations."""
    
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


async def text_to_voice(
    description: str,
    text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create voice previews from a text description.
    
    Creates three preview variations of a voice based on the description.
    Use create_voice_from_preview() to make a generated voice permanent.
    
    Args:
        description: Description of the desired voice characteristics
        text: Custom text for preview (auto-generated if not provided)
        
    Returns:
        Generated voice previews with IDs for creation
        
    API Endpoint: POST /text-to-voice/create-previews
    
    Examples:
        text_to_voice("A calm, professional female voice")
        text_to_voice("Young energetic male voice", "Hello there!")
    """
    from utils import format_success, format_error, validate_voice_description
    
    if not validate_voice_description(description):
        return format_error(
            "Invalid voice description",
            "Provide a description between 5-1000 characters describing the voice characteristics"
        )
    
    try:
        client = ElevenLabsClient()
        payload = {"voice_description": description}
        
        # Add custom text if provided, otherwise auto-generate
        if text and text.strip():
            payload["text"] = text.strip()
        else:
            # Auto-generate text if none provided
            payload["auto_generate_text"] = True
        
        # Try new endpoint first, fall back to legacy if needed
        result = None
        endpoint_used = None
        
        try:
            # Try the new endpoint first
            result = await client._request("POST", "/text-to-voice/design", json_data=payload)
            endpoint_used = "new"
        except Exception as e:
            error_msg = str(e)
            # If new endpoint fails with 422 or 404, try legacy endpoint
            if "422" in error_msg or "404" in error_msg or "voice_name" in error_msg:
                try:
                    result = await client._request("POST", "/text-to-voice/create-previews", json_data=payload)
                    endpoint_used = "legacy"
                except Exception as legacy_e:
                    # If both fail, raise the original error
                    raise e
            else:
                raise e
        
        # Extract generated voice information
        # The API returns "previews" array
        previews_data = result.get("previews", [])
        
        if not previews_data:
            return format_error(
                "No voice previews generated",
                "Try a different description or check your API tier permissions"
            )
        
        # Format the response with preview information
        # Note: Omitting audio_base_64 to avoid token limits in MCP
        previews = []
        for i, voice in enumerate(previews_data):
            preview = {
                "preview_number": i + 1,
                "generated_voice_id": voice.get("generated_voice_id"),
                # Omit audio_base_64 to prevent token overflow in MCP
                # Could save to file: f"voice_preview_{voice.get('generated_voice_id')}.mp3"
                "has_audio": bool(voice.get("audio_base_64")),
                "audio_size_bytes": len(voice.get("audio_base_64", "")) if voice.get("audio_base_64") else 0,
                "description": description
            }
            previews.append(preview)
        
        return format_success(
            f"Generated {len(previews)} voice previews from description",
            {
                "description": description,
                "preview_count": len(previews),
                "previews": previews,
                "endpoint_used": endpoint_used,
                "next_step": "Use create_voice_from_preview() with a generated_voice_id to make permanent"
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate voice from text: {e}")
        error_msg = str(e)
        
        if "quota" in error_msg.lower() or "limit" in error_msg.lower():
            suggestion = "You may have reached your voice generation limit. Check your ElevenLabs plan"
        elif "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions and plan tier"
        elif "description" in error_msg.lower():
            suggestion = "Try a more specific voice description (age, gender, accent, tone)"
        else:
            suggestion = "Verify your API connection and try a different description"
            
        return format_error(error_msg, suggestion)


async def create_voice_from_preview(
    generated_voice_id: str,
    name: str,
    description: str
) -> Dict[str, Any]:
    """
    Create a permanent voice from a generated preview.
    
    Takes a generated_voice_id from text_to_voice() and creates a permanent
    voice that can be used for speech synthesis.
    
    Args:
        generated_voice_id: ID from text_to_voice generation
        name: Name for the new voice
        description: Description of the voice
        
    Returns:
        Created voice details
        
    API Endpoint: POST /text-to-voice/create-voice-from-preview
    
    Examples:
        create_voice_from_preview("abc123def456", "Sarah Professional", "Calm business voice")
    """
    from utils import (
        format_success, format_error, validate_generated_voice_id,
        validate_voice_name, validate_voice_description, extract_voice_info
    )
    
    # Validate inputs
    if not validate_generated_voice_id(generated_voice_id):
        return format_error(
            f"Invalid generated voice ID: {generated_voice_id}",
            "Use the generated_voice_id from text_to_voice() output"
        )
    
    if not validate_voice_name(name):
        return format_error(
            "Invalid voice name",
            "Provide a name between 1-100 characters"
        )
        
    if not validate_voice_description(description):
        return format_error(
            "Invalid voice description", 
            "Provide a description between 5-1000 characters"
        )
    
    try:
        client = ElevenLabsClient()
        payload = {
            "generated_voice_id": generated_voice_id,
            "voice_name": name,
            "voice_description": description
        }
        
        result = await client._request("POST", "/text-to-voice", json_data=payload)
        
        # Extract and format voice information
        voice_info = extract_voice_info(result)
        voice_id = result.get("voice_id")
        
        return format_success(
            f"Voice '{name}' created successfully",
            {
                "voice_id": voice_id,
                "name": name,
                "description": description,
                "voice": voice_info,
                "status": "created"
            }
        )
    except Exception as e:
        logger.error(f"Failed to create voice from preview: {e}")
        error_msg = str(e)
        
        if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
            suggestion = "The generated_voice_id may have expired. Generate new previews with text_to_voice()"
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            suggestion = "You may have reached your voice creation limit. Check your ElevenLabs plan"
        elif "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions and plan tier"
        elif "name" in error_msg.lower() and "taken" in error_msg.lower():
            suggestion = "This voice name is already taken. Try a different name"
        else:
            suggestion = "Verify the generated_voice_id is correct and try again"
            
        return format_error(error_msg, suggestion)