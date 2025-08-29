"""
Analytics Tools
===============
Tools for knowledge base analytics and agent dependencies.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def get_dependent_agents(client, document_id: str) -> Dict[str, Any]:
    """
    Get agents that depend on this document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        List of dependent agents
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        result = await client._request(
            "GET",
            f"/convai/knowledge-base/{document_id}/dependent-agents"
        )
        agents = result.get("agents", [])
        
        return format_success(
            f"Found {len(agents)} dependent agents",
            {"agents": agents, "count": len(agents)}
        )
    except Exception as e:
        logger.error(f"Failed to get dependent agents: {e}")
        return format_error(str(e))


async def get_knowledge_base_size(client, agent_id: str) -> Dict[str, Any]:
    """
    Get knowledge base size and statistics for a specific agent.
    
    Args:
        agent_id: Agent to get knowledge base size for
    
    Returns:
        Storage metrics and document counts
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error(
            f"Invalid agent ID format: {agent_id}",
            "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        result = await client._request("GET", f"/convai/agents/{agent_id}/knowledge-base/size")
        return format_success(
            "Knowledge base statistics retrieved",
            {"statistics": result}
        )
    except Exception as e:
        logger.error(f"Failed to get knowledge base size: {e}")
        return format_error(str(e))