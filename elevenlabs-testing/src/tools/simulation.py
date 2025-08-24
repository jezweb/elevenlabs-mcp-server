"""
Simulation Tools
================
Tools for simulating conversations with agents.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


async def simulate_conversation(
    client,
    agent_id: str,
    user_message: str,
    context: Optional[Dict] = None,
    max_turns: int = 10
) -> Dict[str, Any]:
    """
    Simulate a realistic conversation with an agent for testing.
    
    Args:
        agent_id: Agent to test (format: agent_XXXX)
        user_message: Initial user input to start conversation
        context: Conversation context/variables (optional)
            - user_name, location, preferences, etc.
        max_turns: Maximum conversation turns (1-50, default: 10)
    
    Returns:
        Complete simulated conversation with analysis
    
    Examples:
        simulate_conversation("agent_abc123", "Hello, I need help")
        simulate_conversation(
            "agent_xyz789",
            "I want to order pizza",
            context={"location": "NYC", "time": "evening"},
            max_turns=20
        )
    
    API Endpoint: POST /convai/agents/{agent_id}/simulate-conversation
    
    Use Cases:
        - Test agent responses without real conversations
        - Validate conversation flows
        - Debug agent behavior
        - Generate sample interactions
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    # Validate agent ID
    if not agent_id:
        return format_error(
            "Agent ID is required",
            "Provide agent_id to simulate conversation with"
        )
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error(
            f"Invalid agent ID format: {agent_id}",
            "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    # Validate user message
    if not user_message or not user_message.strip():
        return format_error(
            "User message cannot be empty",
            "Provide an initial message to start the conversation"
        )
    
    # Validate and coerce max_turns
    try:
        max_turns = int(max_turns)
    except (TypeError, ValueError):
        return format_error(
            "Max turns must be an integer",
            "Provide a number between 1 and 50"
        )
    
    if max_turns < 1:
        return format_error(
            f"Max turns too low: {max_turns}",
            "Minimum is 1 turn"
        )
    elif max_turns > 50:
        return format_error(
            f"Max turns too high: {max_turns}",
            "Maximum is 50 turns to prevent excessive simulation"
        )
    
    try:
        data = {
            "simulation_specification": {
                "simulated_user_config": {
                    "first_message": user_message,
                    "language": "en"
                }
            }
        }
        
        # Add context if provided
        if context:
            data["simulation_specification"]["context"] = context
            
        # Add max_turns if specified
        if max_turns != 10:  # Only include if different from default
            data["simulation_specification"]["max_turns"] = max_turns
        
        result = await client._request(
            "POST",
            f"/convai/agents/{agent_id}/simulate-conversation",
            json_data=data
        )
        
        return format_success(
            "Simulated conversation completed",
            {
                "conversation": result.get("conversation"),
                "turns": result.get("turns"),
                "duration": result.get("duration")
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to simulate conversation for {agent_id}: {e}")
        return format_error(str(e))


async def stream_simulate_conversation(
    client,
    agent_id: str,
    user_message: str,
    stream_callback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Stream conversation simulation in real-time.
    
    Args:
        agent_id: Agent to test
        user_message: Initial message
        stream_callback: Webhook for streaming
    
    Returns:
        Stream session details
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    try:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error("Invalid agent ID format", "Use format: agent_XXXX")
        
        data = {
            "message": user_message,
            "stream_callback": stream_callback
        }
        
        result = await client._request(
            "POST",
            f"/convai/agents/{agent_id}/stream-simulate-conversation",
            json_data=data
        )
        
        return format_success(
            "Started streaming simulation",
            {
                "session_id": result.get("session_id"),
                "stream_url": result.get("stream_url"),
                "status": "streaming"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to stream simulation for {agent_id}: {e}")
        return format_error(str(e))