"""
MCP Server Management
=====================
Tools for managing MCP server integrations.
"""

import logging
from typing import Any, Dict, Optional, Literal

logger = logging.getLogger(__name__)


async def create_mcp_server(
    client,
    agent_id: str,
    server_url: str,
    server_type: Literal["SSE", "HTTP"] = "SSE",
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add MCP server integration.
    
    Args:
        agent_id: Agent to add server to
        server_url: MCP server URL
        server_type: Transport type (SSE or HTTP)
        name: Server name
        description: Server description
    
    Returns:
        Integration configuration
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id, validate_url
    
    try:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error("Invalid agent ID format", "Use format: agent_XXXX")
        
        if not validate_url(server_url):
            return format_error("Invalid server URL")
        
        data = {
            "agent_id": agent_id,
            "url": server_url,
            "type": server_type,
            "name": name,
            "description": description
        }
        
        result = await client._request(
            "POST",
            "/convai/mcp/servers",
            json_data=data
        )
        
        return format_success(
            f"Added MCP server to agent {agent_id}",
            {"server": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}")
        return format_error(str(e))


async def get_mcp_server(
    client,
    server_id: str
) -> Dict[str, Any]:
    """
    Get MCP server details.
    
    Args:
        server_id: Server identifier
    
    Returns:
        Server configuration
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    try:
        if not validate_elevenlabs_id(server_id, 'server'):
            return format_error("Invalid server ID format", "Use format: server_XXXX")
        
        result = await client._request(
            "GET",
            f"/convai/mcp/servers/{server_id}",
            use_cache=True
        )
        
        return format_success(
            "Retrieved MCP server details",
            {"server": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to get MCP server {server_id}: {e}")
        return format_error(str(e))


async def list_mcp_server_tools(
    client,
    server_id: str
) -> Dict[str, Any]:
    """
    List tools provided by MCP server.
    
    Args:
        server_id: Server identifier
    
    Returns:
        Available tools from server
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    try:
        if not validate_elevenlabs_id(server_id, 'server'):
            return format_error("Invalid server ID format", "Use format: server_XXXX")
        
        result = await client._request(
            "GET",
            f"/convai/mcp/servers/{server_id}/tools",
            use_cache=True
        )
        
        tools = result.get("tools", [])
        
        return format_success(
            f"Found {len(tools)} tools from MCP server",
            {"tools": tools, "count": len(tools)}
        )
        
    except Exception as e:
        logger.error(f"Failed to list tools for {server_id}: {e}")
        return format_error(str(e))