"""
Conversation management tools for ElevenLabs.
"""

import logging
from typing import Dict, Any, Optional
from src.utils import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def list_conversations(
    client,
    agent_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List conversations.
    
    Args:
        client: ElevenLabs API client
        agent_id: Filter by agent
        limit: Maximum results (1-100)
        offset: Pagination offset
    
    Returns:
        List of conversations with metadata
    """
    try:
        if agent_id and not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error("Invalid agent ID format", "Use format: agent_XXXX")
        
        if not 1 <= limit <= 100:
            return format_error("Limit must be between 1-100")
        
        if offset < 0:
            return format_error("Offset must be non-negative")
        
        conversations = await client.list_conversations(
            agent_id=agent_id,
            limit=limit,
            offset=offset
        )
        
        # Format response
        formatted = []
        for conv in conversations:
            formatted.append({
                "conversation_id": conv.get("conversation_id"),
                "agent_id": conv.get("agent_id"),
                "start_time": conv.get("start_time"),
                "end_time": conv.get("end_time"),
                "duration": conv.get("duration"),
                "status": conv.get("status"),
                "metadata": conv.get("metadata", {})
            })
        
        return format_success(
            f"Found {len(formatted)} conversations",
            {"conversations": formatted, "total": len(formatted)}
        )
        
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        return format_error(str(e))


async def get_conversation(
    client,
    conversation_id: str
) -> Dict[str, Any]:
    """
    Get detailed conversation data.
    
    Args:
        client: ElevenLabs API client
        conversation_id: Conversation to retrieve
    
    Returns:
        Complete conversation details including transcript
    """
    try:
        if not validate_elevenlabs_id(conversation_id, 'conversation'):
            return format_error("Invalid conversation ID format")
        
        conversation = await client.get_conversation(conversation_id)
        
        return format_success(
            "Retrieved conversation details",
            {"conversation": conversation}
        )
        
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        return format_error(str(e))


async def get_transcript(
    client,
    conversation_id: str
) -> Dict[str, Any]:
    """
    Get conversation transcript.
    
    Args:
        client: ElevenLabs API client
        conversation_id: Conversation ID
    
    Returns:
        Text transcript
    """
    try:
        if not validate_elevenlabs_id(conversation_id, 'conversation'):
            return format_error("Invalid conversation ID format")
        
        transcript = await client.get_transcript(conversation_id)
        
        return format_success(
            "Retrieved transcript",
            {"transcript": transcript}
        )
        
    except Exception as e:
        logger.error(f"Failed to get transcript for {conversation_id}: {e}")
        return format_error(str(e))


async def delete_conversation(
    client,
    conversation_id: str
) -> Dict[str, Any]:
    """
    Delete a conversation.
    
    Args:
        client: ElevenLabs API client
        conversation_id: Conversation to delete
    
    Returns:
        Deletion confirmation
    """
    try:
        if not validate_elevenlabs_id(conversation_id, 'conversation'):
            return format_error("Invalid conversation ID format")
        
        result = await client._request(
            "DELETE",
            f"/convai/conversations/{conversation_id}"
        )
        
        return format_success(
            f"Deleted conversation {conversation_id}",
            {"deleted": True}
        )
        
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        return format_error(str(e))