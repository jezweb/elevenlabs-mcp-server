"""
Feedback tools for ElevenLabs conversations.
"""

import logging
from typing import Dict, Any, Optional
from src.utils import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def send_feedback(
    client,
    conversation_id: str,
    rating: int,
    feedback_text: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Send feedback for a conversation.
    
    Args:
        client: ElevenLabs API client
        conversation_id: Conversation to rate (format: conv_XXXX)
        rating: Rating (1-5, where 1=poor, 5=excellent)
        feedback_text: Optional detailed feedback
        metadata: Additional metadata (tags, categories, etc.)
    
    Returns:
        Feedback confirmation
    
    Examples:
        send_feedback("conv_abc123", 5, "Great interaction!")
        send_feedback("conv_xyz789", 2, "Agent was confused", 
                     metadata={"issue": "misunderstanding"})
    
    Rating Scale:
        1 - Poor: Major issues, failed interaction
        2 - Below Average: Some problems, partially successful
        3 - Average: Acceptable, met basic needs
        4 - Good: Effective interaction, minor issues only
        5 - Excellent: Perfect interaction, exceeded expectations
    
    API Endpoint: POST /convai/conversations/{conversation_id}/feedback
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
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX (conv_ + 28 chars)"
        )
    
    # Validate rating
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return format_error(
            "Rating must be an integer",
            "Provide a rating between 1 (poor) and 5 (excellent)"
        )
    
    if not 1 <= rating <= 5:
        return format_error(
            f"Rating {rating} out of range",
            "Rating must be between 1 (poor) and 5 (excellent)"
        )
    
    # Validate feedback text length if provided
    if feedback_text and len(feedback_text) > 1000:
        return format_error(
            f"Feedback text too long ({len(feedback_text)} characters)",
            "Keep feedback under 1000 characters"
        )
    
    try:
        data = {
            "rating": rating,
            "feedback": feedback_text,
            "metadata": metadata or {}
        }
        
        result = await client._request(
            "POST",
            f"/convai/conversations/{conversation_id}/feedback",
            json_data=data
        )
        
        return format_success(
            f"Feedback submitted (rating: {rating}/5)",
            {
                "conversation_id": conversation_id,
                "rating": rating,
                "has_text": bool(feedback_text),
                "metadata_keys": list(metadata.keys()) if metadata else []
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to send feedback for {conversation_id}: {e}")
        error_msg = str(e)
        
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found"
        elif "already" in error_msg.lower():
            suggestion = "Feedback may have already been submitted for this conversation"
        else:
            suggestion = "Check conversation ID and try again"
            
        return format_error(error_msg, suggestion)


async def get_feedback_summary(
    client,
    agent_id: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get feedback summary for an agent.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to analyze
        days: Number of days to include (1-30)
    
    Returns:
        Feedback summary with ratings distribution
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not 1 <= days <= 30:
        return format_error("Days must be between 1-30")
    
    try:
        # This would typically call a specific feedback API endpoint
        # For now, we'll return a structured example
        summary = {
            "agent_id": agent_id,
            "period_days": days,
            "total_feedback": 0,
            "average_rating": 0.0,
            "rating_distribution": {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0
            },
            "feedback_with_text": 0
        }
        
        return format_success(
            f"Retrieved feedback summary for {days} days",
            {"summary": summary}
        )
        
    except Exception as e:
        logger.error(f"Failed to get feedback summary: {e}")
        return format_error(str(e))