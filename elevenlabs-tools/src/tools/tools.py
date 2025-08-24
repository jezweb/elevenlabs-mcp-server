"""
Tool Management
===============
Tools for creating and managing custom tools and integrations.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def list_tools(
    client,
    agent_id: Optional[str] = None,
    tool_type: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    List all available tools and integrations.
    
    Args:
        agent_id: Filter by specific agent (optional)
        tool_type: Filter by type ("api", "webhook", "database", "custom")
        limit: Maximum results (1-100, default: 50)
    
    Returns:
        List of tools with configurations and metadata
    
    Examples:
        list_tools()  # All tools
        list_tools(agent_id="agent_abc123")  # Agent-specific tools
        list_tools(tool_type="webhook", limit=100)  # All webhooks
    
    API Endpoint: GET /convai/tools
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    # Validate agent ID if provided
    if agent_id:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error(
                f"Invalid agent ID format: {agent_id}",
                "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            )
    
    # Validate limit
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        return format_error(
            "Limit must be an integer",
            "Provide a number between 1 and 100"
        )
    
    if limit < 1:
        return format_error(
            f"Limit too low: {limit}",
            "Minimum is 1 tool"
        )
    elif limit > 100:
        return format_error(
            f"Limit too high: {limit}",
            "Maximum is 100 tools per request"
        )
    
    try:
        params = {"limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if tool_type:
            params["type"] = tool_type
        
        result = await client._request(
            "GET",
            "/convai/tools",
            params=params,
            use_cache=True
        )
        
        tools = result.get("tools", [])
        
        return format_success(
            f"Found {len(tools)} tools",
            {"tools": tools, "count": len(tools)}
        )
        
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        return format_error(str(e))


async def get_tool(
    client,
    tool_id: str
) -> Dict[str, Any]:
    """
    Get detailed tool configuration and metadata.
    
    Args:
        tool_id: Tool identifier (format: tool_XXXX)
    
    Returns:
        Complete tool configuration with parameters and schemas
    
    Examples:
        get_tool("tool_abc123")
    
    API Endpoint: GET /convai/tools/{tool_id}
    
    Tool Details Include:
        - Name and description
        - Input/output schemas
        - Authentication requirements
        - Rate limits and quotas
        - Usage statistics
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    # Validate tool ID
    if not tool_id:
        return format_error(
            "Tool ID is required",
            "Provide tool_id from list_tools()"
        )
    
    if not validate_elevenlabs_id(tool_id, 'tool'):
        return format_error(
            f"Invalid tool ID format: {tool_id}",
            "Use format: tool_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/tools/{tool_id}",
            use_cache=True
        )
        
        return format_success(
            "Retrieved tool details",
            {"tool": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to get tool {tool_id}: {e}")
        return format_error(str(e))


async def create_tool(
    client,
    name: str,
    description: str,
    tool_type: str,
    configuration: Dict[str, Any],
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create custom tool or integration.
    
    Args:
        name: Tool name (descriptive, unique)
        description: What the tool does
        tool_type: Type of tool
            - "api": External API integration
            - "webhook": Webhook handler
            - "database": Database connection
            - "custom": Custom function
        configuration: Tool-specific configuration
            - API tools: endpoint, method, headers, auth
            - Webhook: url, events, secret
            - Database: connection string, queries
        metadata: Additional metadata (tags, owner, etc.)
    
    Returns:
        Created tool with ID and configuration
    
    Examples:
        create_tool(
            "Weather API",
            "Get current weather data",
            "api",
            {"endpoint": "https://api.weather.com", "method": "GET"}
        )
    
    API Endpoint: POST /convai/tools
    """
    from src.utils import format_error, format_success
    
    # Validate inputs
    if not name or not name.strip():
        return format_error(
            "Tool name cannot be empty",
            "Provide a descriptive name like 'Weather API' or 'Database Query'"
        )
    
    if not description or not description.strip():
        return format_error(
            "Tool description cannot be empty",
            "Describe what the tool does"
        )
    
    if tool_type not in ["api", "webhook", "database", "custom"]:
        return format_error(
            f"Invalid tool type: {tool_type}",
            "Use 'api', 'webhook', 'database', or 'custom'"
        )
    
    if not configuration:
        return format_error(
            "Configuration is required",
            "Provide tool-specific configuration parameters"
        )
    
    try:
        data = {
            "name": name,
            "description": description,
            "type": tool_type,
            "configuration": configuration,
            "metadata": metadata or {}
        }
        
        result = await client._request(
            "POST",
            "/convai/tools",
            json_data=data
        )
        
        return format_success(
            f"Created tool '{name}'",
            {"tool": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to create tool: {e}")
        return format_error(str(e))


async def update_tool(
    client,
    tool_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    configuration: Optional[Dict] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Update tool configuration.
    
    Args:
        tool_id: Tool to update
        name: New name
        description: New description
        configuration: New configuration
        metadata: New metadata
    
    Returns:
        Updated tool details
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    try:
        if not validate_elevenlabs_id(tool_id, 'tool'):
            return format_error("Invalid tool ID format", "Use format: tool_XXXX")
        
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if configuration is not None:
            data["configuration"] = configuration
        if metadata is not None:
            data["metadata"] = metadata
        
        result = await client._request(
            "PATCH",
            f"/convai/tools/{tool_id}",
            json_data=data
        )
        
        return format_success(
            f"Updated tool {tool_id}",
            {"tool": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to update tool {tool_id}: {e}")
        return format_error(str(e))


async def delete_tool(
    client,
    tool_id: str
) -> Dict[str, Any]:
    """
    Delete tool.
    
    Args:
        tool_id: Tool to delete
    
    Returns:
        Deletion confirmation
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    try:
        if not validate_elevenlabs_id(tool_id, 'tool'):
            return format_error("Invalid tool ID format", "Use format: tool_XXXX")
        
        await client._request(
            "DELETE",
            f"/convai/tools/{tool_id}"
        )
        
        return format_success(
            f"Deleted tool {tool_id}",
            {"deleted": True}
        )
        
    except Exception as e:
        logger.error(f"Failed to delete tool {tool_id}: {e}")
        return format_error(str(e))


async def get_tool_dependent_agents(
    client,
    tool_id: str
) -> Dict[str, Any]:
    """
    Get agents using a tool.
    
    Args:
        tool_id: Tool identifier
    
    Returns:
        List of dependent agents
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    try:
        if not validate_elevenlabs_id(tool_id, 'tool'):
            return format_error("Invalid tool ID format", "Use format: tool_XXXX")
        
        result = await client._request(
            "GET",
            f"/convai/tools/{tool_id}/dependent-agents",
            use_cache=True
        )
        
        agents = result.get("agents", [])
        
        return format_success(
            f"Found {len(agents)} agents using this tool",
            {"agents": agents, "count": len(agents)}
        )
        
    except Exception as e:
        logger.error(f"Failed to get dependent agents for {tool_id}: {e}")
        return format_error(str(e))