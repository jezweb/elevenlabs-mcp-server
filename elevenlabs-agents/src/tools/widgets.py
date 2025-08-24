"""
Widget and integration tools for ElevenLabs agents.
"""

import logging
from typing import Dict, Any, Optional
from shared import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def get_widget_link(client, agent_id: str, settings: Optional[dict] = None) -> Dict[str, Any]:
    """
    Get embeddable widget link for an agent.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to create widget for
        settings: Optional widget settings
    
    Returns:
        Widget embed code and link
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Generate widget URL
        base_url = "https://elevenlabs.io/convai/widget"
        widget_url = f"{base_url}/{agent_id}"
        
        # Add settings as query parameters if provided
        if settings:
            params = []
            for key, value in settings.items():
                params.append(f"{key}={value}")
            if params:
                widget_url += "?" + "&".join(params)
        
        # Generate embed code
        embed_code = f'''<iframe
  src="{widget_url}"
  width="400"
  height="600"
  frameborder="0"
  allow="microphone">
</iframe>'''
        
        return format_success(
            "Widget link generated",
            {
                "agent_id": agent_id,
                "widget_url": widget_url,
                "embed_code": embed_code,
                "settings": settings or {}
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate widget link: {e}")
        return format_error(str(e))


async def get_agent_link(client, agent_id: str) -> Dict[str, Any]:
    """
    Get a shareable link for an agent.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to get link for
    
    Returns:
        Shareable link URL
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Generate shareable link
        share_url = f"https://elevenlabs.io/convai/share/{agent_id}"
        
        return format_success(
            "Agent link generated",
            {
                "agent_id": agent_id,
                "share_url": share_url,
                "embed_url": f"https://elevenlabs.io/convai/widget/{agent_id}"
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate agent link: {e}")
        return format_error(str(e))


async def create_widget_avatar(client, agent_id: str, avatar_url: str) -> Dict[str, Any]:
    """
    Set custom avatar for agent widget.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to update
        avatar_url: URL of the avatar image
    
    Returns:
        Update confirmation
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not avatar_url or not avatar_url.startswith(('http://', 'https://')):
        return format_error("Invalid avatar URL", "Provide a valid HTTP/HTTPS image URL")
    
    try:
        # Update agent with avatar
        config = {
            "widget_config": {
                "avatar_url": avatar_url
            }
        }
        
        result = await client.update_agent(agent_id, config)
        return format_success(
            "Widget avatar updated",
            {
                "agent_id": agent_id,
                "avatar_url": avatar_url
            }
        )
    except Exception as e:
        logger.error(f"Failed to set widget avatar: {e}")
        return format_error(str(e))


async def get_widget(client, agent_id: str) -> Dict[str, Any]:
    """
    Get widget configuration for an agent.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to get widget for
    
    Returns:
        Widget configuration and embed options
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Get agent details to extract widget config
        agent = await client.get_agent(agent_id)
        
        widget_config = agent.get("widget_config", {})
        
        # Generate all widget options
        widget_info = {
            "agent_id": agent_id,
            "widget_url": f"https://elevenlabs.io/convai/widget/{agent_id}",
            "embed_code": f'<iframe src="https://elevenlabs.io/convai/widget/{agent_id}" width="400" height="600"></iframe>',
            "configuration": widget_config,
            "customization_options": {
                "width": "400-800px recommended",
                "height": "600-800px recommended",
                "theme": "light or dark",
                "position": "bottom-right, bottom-left, or custom"
            }
        }
        
        return format_success(
            "Widget configuration retrieved",
            widget_info
        )
    except Exception as e:
        logger.error(f"Failed to get widget config: {e}")
        return format_error(str(e))


async def calculate_llm_usage(
    client,
    agent_id: str,
    conversation_count: int = 100,
    avg_messages_per_conversation: int = 10
) -> Dict[str, Any]:
    """
    Calculate estimated LLM usage and costs.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to calculate for
        conversation_count: Number of conversations
        avg_messages_per_conversation: Average messages per conversation
    
    Returns:
        Usage estimates and cost projections
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Get agent configuration
        agent = await client.get_agent(agent_id)
        llm_model = agent.get("conversation_config", {}).get("llm", {}).get("model", "unknown")
        
        # Estimate tokens (simplified calculation)
        avg_tokens_per_message = 50  # Rough estimate
        total_messages = conversation_count * avg_messages_per_conversation
        total_tokens = total_messages * avg_tokens_per_message
        
        # Estimate costs (example rates - actual rates may vary)
        cost_per_1k_tokens = {
            "gemini-2.0-flash-001": 0.001,
            "gpt-4o-mini": 0.002,
            "claude-3-haiku": 0.0015
        }
        
        rate = cost_per_1k_tokens.get(llm_model, 0.002)
        estimated_cost = (total_tokens / 1000) * rate
        
        return format_success(
            "Usage calculation complete",
            {
                "agent_id": agent_id,
                "llm_model": llm_model,
                "estimates": {
                    "conversation_count": conversation_count,
                    "avg_messages_per_conversation": avg_messages_per_conversation,
                    "total_messages": total_messages,
                    "estimated_tokens": total_tokens,
                    "estimated_cost_usd": round(estimated_cost, 2)
                },
                "note": "These are rough estimates. Actual usage may vary."
            }
        )
    except Exception as e:
        logger.error(f"Failed to calculate usage: {e}")
        return format_error(str(e))