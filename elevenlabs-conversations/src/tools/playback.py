"""
Playback tools for ElevenLabs conversations.
"""

import logging
from typing import Dict, Any
from src.utils import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def get_conversation_audio(
    client,
    conversation_id: str,
    format: str = "mp3"
) -> Dict[str, Any]:
    """
    Get conversation audio download URL.
    
    Args:
        client: ElevenLabs API client
        conversation_id: Conversation ID (format: conv_XXXX)
        format: Audio format - "mp3" (default) or "wav"
            - mp3: Smaller file size, good for storage/sharing
            - wav: Uncompressed, higher quality for processing
    
    Returns:
        Audio download URL with expiration time
    
    Examples:
        get_conversation_audio("conv_abc123")  # Default MP3
        get_conversation_audio("conv_xyz789", "wav")  # WAV format
    
    API Endpoint: GET /convai/conversations/{conversation_id}/audio
    
    Note: URLs expire after ~1 hour. Download promptly or use get_signed_url for longer TTL.
    """
    # Validate conversation ID
    if not conversation_id:
        return format_error(
            "Conversation ID is required",
            "Provide conversation_id from list_conversations() or get_conversation()"
        )
    
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error(
            f"Invalid conversation ID format: {conversation_id}",
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    # Validate and normalize format
    format = format.lower().strip() if format else "mp3"
    if format not in ["mp3", "wav"]:
        return format_error(
            f"Unsupported audio format: {format}",
            "Use 'mp3' for compressed audio or 'wav' for uncompressed"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/conversations/{conversation_id}/audio",
            params={"format": format}
        )
        
        return format_success(
            f"Retrieved {format.upper()} audio URL",
            {
                "audio_url": result.get("url"),
                "format": format,
                "expires_at": result.get("expires_at"),
                "size_estimate": "~1MB/min for MP3, ~10MB/min for WAV"
            }
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide contextual error messages
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found. Check ID or list available conversations."
        elif "audio not available" in error_msg.lower():
            suggestion = "Audio may still be processing. Try again in a few seconds."
        else:
            suggestion = "Check conversation ID and network connection"
            
        logger.error(f"Failed to get audio for {conversation_id}: {e}")
        return format_error(error_msg, suggestion)


async def get_signed_url(
    client,
    conversation_id: str,
    ttl: int = 3600
) -> Dict[str, Any]:
    """
    Get signed URL for secure conversation playback.
    
    Args:
        client: ElevenLabs API client
        conversation_id: Conversation ID (format: conv_XXXX)
        ttl: URL time-to-live in seconds (60-86400, default: 3600)
            - 60 = 1 minute (minimum)
            - 3600 = 1 hour (default)
            - 86400 = 24 hours (maximum)
    
    Returns:
        Signed URL with expiration time for secure access
    
    Examples:
        get_signed_url("conv_abc123")  # 1 hour TTL
        get_signed_url("conv_xyz789", 7200)  # 2 hour TTL
        get_signed_url("conv_def456", 86400)  # 24 hour TTL
    
    API Endpoint: GET /convai/conversations/{conversation_id}/signed-url
    
    Use Cases:
        - Share conversation playback securely
        - Embed in web applications
        - Generate temporary access links
        - Control access duration precisely
    """
    # Validate conversation ID
    if not conversation_id:
        return format_error(
            "Conversation ID is required",
            "Provide conversation_id from list_conversations() or get_conversation()"
        )
    
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error(
            f"Invalid conversation ID format: {conversation_id}",
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    # Validate and coerce TTL
    try:
        ttl = int(ttl)
    except (TypeError, ValueError):
        return format_error(
            "TTL must be an integer",
            "Provide time-to-live in seconds (60-86400)"
        )
    
    if ttl < 60:
        return format_error(
            f"TTL too short: {ttl} seconds",
            "Minimum TTL is 60 seconds (1 minute)"
        )
    elif ttl > 86400:
        return format_error(
            f"TTL too long: {ttl} seconds",
            "Maximum TTL is 86400 seconds (24 hours)"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/conversations/{conversation_id}/signed-url",
            params={"ttl": ttl}
        )
        
        # Format TTL for human readability
        if ttl < 3600:
            ttl_display = f"{ttl // 60} minutes"
        elif ttl < 86400:
            ttl_display = f"{ttl / 3600:.1f} hours"
        else:
            ttl_display = "24 hours"
        
        return format_success(
            f"Generated signed URL (valid for {ttl_display})",
            {
                "signed_url": result.get("url"),
                "expires_at": result.get("expires_at"),
                "ttl_seconds": ttl,
                "ttl_display": ttl_display
            }
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide contextual error messages
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found"
        elif "permission" in error_msg.lower():
            suggestion = "Check API key permissions for conversation access"
        else:
            suggestion = "Verify conversation ID and API connectivity"
            
        logger.error(f"Failed to get signed URL for {conversation_id}: {e}")
        return format_error(error_msg, suggestion)


async def get_conversation_token(
    client,
    conversation_id: str
) -> Dict[str, Any]:
    """
    Get access token for real-time conversation websocket connection.
    
    Args:
        client: ElevenLabs API client
        conversation_id: Conversation ID (format: conv_XXXX)
    
    Returns:
        Access token and websocket URL for real-time communication
    
    Examples:
        get_conversation_token("conv_abc123")
    
    API Endpoint: GET /convai/conversations/{conversation_id}/token
    
    Use Cases:
        - Establish websocket connection for real-time conversation
        - Enable bidirectional audio streaming
        - Implement custom conversation clients
        - Build interactive voice applications
    
    Note: Tokens are short-lived for security. Request new token when expired.
    """
    # Validate conversation ID
    if not conversation_id:
        return format_error(
            "Conversation ID is required",
            "Provide conversation_id from list_conversations() or active conversation"
        )
    
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error(
            f"Invalid conversation ID format: {conversation_id}",
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/conversations/{conversation_id}/token"
        )
        
        return format_success(
            "Retrieved websocket access token",
            {
                "token": result.get("token"),
                "expires_at": result.get("expires_at"),
                "websocket_url": result.get("websocket_url"),
                "usage_hint": "Use token to authenticate websocket connection"
            }
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide contextual error messages
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found or not active"
        elif "expired" in error_msg.lower():
            suggestion = "Conversation may have ended. Start a new conversation."
        elif "permission" in error_msg.lower():
            suggestion = "Check API key permissions for websocket access"
        else:
            suggestion = "Verify conversation is active and ID is correct"
            
        logger.error(f"Failed to get token for {conversation_id}: {e}")
        return format_error(error_msg, suggestion)