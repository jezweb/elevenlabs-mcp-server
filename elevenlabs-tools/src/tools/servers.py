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
    server_url: str,
    name: str,
    transport: Literal["SSE", "HTTP"] = "SSE",
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create MCP server integration.
    
    Args:
        server_url: MCP server URL
        name: Server name (required)
        transport: Transport type (SSE or HTTP)
        description: Server description
    
    Returns:
        Integration configuration
    """
    from src.utils import format_error, format_success, validate_url
    
    try:
        if not validate_url(server_url):
            return format_error("Invalid server URL")
        
        if not name:
            return format_error("Server name is required")
        
        # Build config object as per API spec
        config = {
            "url": server_url,
            "name": name,
            "transport": transport
        }
        
        if description:
            config["description"] = description
        
        # Wrap in config object
        data = {
            "config": config
        }
        
        result = await client._request(
            "POST",
            "/convai/mcp-servers",
            json_data=data
        )
        
        return format_success(
            f"Created MCP server '{name}'",
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
            f"/convai/mcp-servers/{server_id}",
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
            f"/convai/mcp-servers/{server_id}/tools",
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