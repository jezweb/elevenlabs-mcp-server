"""
Instant Voice Cloning (IVC) Tools
==================================
Tools for cloning voices using audio samples.
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """Simple ElevenLabs API client for IVC operations."""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
    
    async def _request_multipart(
        self,
        method: str,
        endpoint: str,
        files: Dict[str, Any],
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a multipart form data API request."""
        url = f"{self.base_url}{endpoint}"
        headers = {"xi-api-key": self.api_key}
        
        form_data = aiohttp.FormData()
        
        # Add files
        for field_name, file_info in files.items():
            if isinstance(file_info, tuple):
                filename, file_content, content_type = file_info
                form_data.add_field(field_name, file_content, filename=filename, content_type=content_type)
            else:
                form_data.add_field(field_name, file_info)
        
        # Add data fields
        if data:
            for key, value in data.items():
                form_data.add_field(key, str(value))
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, data=form_data, headers=headers
            ) as response:
                if response.status not in [200, 201, 204]:
                    error_text = await response.text()
                    raise Exception(f"API request failed ({response.status}): {error_text}")
                
                if response.status == 204:
                    return {"success": True}
                
                return await response.json()


async def instant_voice_clone(
    name: str,
    audio_files: List[str],
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clone a voice using audio samples (Instant Voice Cloning).
    
    Creates a new voice by analyzing provided audio samples. Best results
    with 1-5 minutes of clear speech across multiple files.
    
    Args:
        name: Name for the cloned voice
        audio_files: List of audio file paths for cloning (1-25 files)
        description: Optional description for the voice
        
    Returns:
        Cloned voice details
        
    API Endpoint: POST /voices/add
    
    Examples:
        instant_voice_clone("John's Voice", ["/path/to/sample1.wav", "/path/to/sample2.mp3"])
        instant_voice_clone("CEO Voice", ["recording.wav"], "Professional executive voice")
        
    Requirements:
        - Audio files: WAV, MP3, FLAC, M4A, OGG, WEBM
        - Total duration: 1-5 minutes recommended
        - Clear speech, minimal background noise
        - Maximum 25 files per voice
    """
    from utils import (
        format_success, format_error, validate_voice_name,
        validate_audio_files, sanitize_filename, extract_voice_info
    )
    
    # Validate inputs
    if not validate_voice_name(name):
        return format_error(
            "Invalid voice name",
            "Provide a name between 1-100 characters"
        )
    
    # Validate audio files
    audio_validation = validate_audio_files(audio_files)
    if not audio_validation["valid"]:
        return format_error(
            audio_validation["error"],
            audio_validation.get("suggestion", "Use supported audio formats")
        )
    
    if description and not description.strip():
        description = None
    
    try:
        client = ElevenLabsClient()
        
        # Prepare files for upload
        files = {}
        data = {"name": name}
        
        if description:
            data["description"] = description
        
        # Read and prepare audio files
        for i, file_path in enumerate(audio_files):
            try:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Generate field name and sanitize filename
                field_name = f"files"
                filename = sanitize_filename(os.path.basename(file_path))
                
                # Determine content type
                if file_path.lower().endswith('.wav'):
                    content_type = "audio/wav"
                elif file_path.lower().endswith('.mp3'):
                    content_type = "audio/mpeg"
                elif file_path.lower().endswith('.flac'):
                    content_type = "audio/flac"
                elif file_path.lower().endswith('.m4a'):
                    content_type = "audio/mp4"
                elif file_path.lower().endswith('.ogg'):
                    content_type = "audio/ogg"
                elif file_path.lower().endswith('.webm'):
                    content_type = "audio/webm"
                else:
                    content_type = "audio/mpeg"  # Default
                
                files[f"{field_name}"] = (filename, file_content, content_type)
                
            except FileNotFoundError:
                return format_error(
                    f"Audio file not found: {file_path}",
                    "Verify all file paths exist and are accessible"
                )
            except Exception as file_error:
                return format_error(
                    f"Error reading file {file_path}: {str(file_error)}",
                    "Ensure the file is not corrupted and is a valid audio format"
                )
        
        # Make the API request
        result = await client._request_multipart("POST", "/voices/add", files, data)
        
        # Extract voice information
        voice_info = extract_voice_info(result)
        voice_id = result.get("voice_id")
        
        return format_success(
            f"Voice '{name}' cloned successfully using {len(audio_files)} audio samples",
            {
                "voice_id": voice_id,
                "name": name,
                "description": description,
                "sample_count": len(audio_files),
                "voice": voice_info,
                "cloning_method": "instant",
                "status": "ready"
            }
        )
    except Exception as e:
        logger.error(f"Failed to clone voice: {e}")
        error_msg = str(e)
        
        if "file" in error_msg.lower() and ("format" in error_msg.lower() or "type" in error_msg.lower()):
            suggestion = "Use supported audio formats: WAV, MP3, FLAC, M4A, OGG, WEBM"
        elif "duration" in error_msg.lower():
            suggestion = "Provide 1-5 minutes of clear speech across all audio samples"
        elif "quality" in error_msg.lower():
            suggestion = "Use high-quality audio with minimal background noise"
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            suggestion = "You may have reached your voice cloning limit. Check your ElevenLabs plan"
        elif "401" in error_msg or "403" in error_msg:
            suggestion = "Check your ElevenLabs API key permissions and plan tier"
        elif "name" in error_msg.lower() and "taken" in error_msg.lower():
            suggestion = "This voice name is already taken. Try a different name"
        elif "size" in error_msg.lower():
            suggestion = "Audio files may be too large. Try compressing or shortening them"
        else:
            suggestion = "Verify your audio files are valid and try again"
            
        return format_error(error_msg, suggestion)