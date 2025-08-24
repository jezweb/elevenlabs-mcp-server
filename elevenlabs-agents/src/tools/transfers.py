"""
Transfer and webhook configuration tools for ElevenLabs agents.
"""

import logging
from typing import Dict, Any, Optional
from shared import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def add_transfer_to_agent(
    client,
    from_agent_id: str,
    to_agent_id: str,
    conditions: str,
    message: Optional[str] = "I'll transfer you to a specialist"
) -> Dict[str, Any]:
    """
    Configure agent-to-agent transfer.
    
    Args:
        client: ElevenLabs API client
        from_agent_id: Source agent
        to_agent_id: Target agent
        conditions: Natural language transfer conditions
        message: Transfer announcement
    
    Returns:
        Transfer configuration result
    """
    if not validate_elevenlabs_id(from_agent_id, 'agent') or not validate_elevenlabs_id(to_agent_id, 'agent'):
        return format_error("Invalid agent ID format", suggestion="Provide valid agent IDs (e.g., agent_XXXX or UUID)")
    
    try:
        tool_config = {
            "tools": [{
                "type": "transfer_to_agent",
                "config": {
                    "agent_id": to_agent_id,
                    "transfer_conditions": conditions,
                    "transfer_message": message,
                    "pass_context": True
                }
            }]
        }
        
        # Note: This is a simplified example - actual API may differ
        result = await client.update_agent(from_agent_id, tool_config)
        return format_success(
            f"Transfer configured from {from_agent_id} to {to_agent_id}",
            {"transfer_config": tool_config["tools"][0]}
        )
    except Exception as e:
        logger.error(f"Failed to configure transfer: {e}")
        return format_error(str(e))


async def configure_webhook(
    client,
    agent_id: str,
    webhook_url: str,
    events: Optional[list] = None
) -> Dict[str, Any]:
    """
    Configure webhook for agent events.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to configure
        webhook_url: URL to receive webhook events
        events: List of events to subscribe to
    
    Returns:
        Webhook configuration result
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not webhook_url or not webhook_url.startswith(('http://', 'https://')):
        return format_error("Invalid webhook URL", "Provide a valid HTTP/HTTPS URL")
    
    if events is None:
        events = ["conversation.started", "conversation.ended", "message.received", "message.sent"]
    
    try:
        webhook_config = {
            "webhook": {
                "url": webhook_url,
                "events": events
            }
        }
        
        result = await client.update_agent(agent_id, webhook_config)
        return format_success(
            f"Webhook configured for agent {agent_id}",
            {"webhook_config": webhook_config}
        )
    except Exception as e:
        logger.error(f"Failed to configure webhook: {e}")
        return format_error(str(e))