"""ElevenLabs Integrations MCP Server.

Provides tools for managing MCP servers, tools, approvals, and secrets.
"""

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal

from fastmcp import FastMCP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    Config,
    ElevenLabsClient,
    format_error,
    format_success,
    validate_elevenlabs_id,
    validate_url,
    validate_mcp_server,
    setup_logging
)

# Setup logging
logger = setup_logging(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="elevenlabs-integrations",
    description="Manage ElevenLabs MCP servers, tools, and integrations"
)

# Global client instance
client: Optional[ElevenLabsClient] = None


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for the MCP server."""
    global client
    
    # Startup
    logger.info("Starting ElevenLabs Integrations MCP server")
    
    # Initialize client
    if not Config.API_KEY:
        logger.error("ELEVENLABS_API_KEY not set")
        sys.exit(1)
    
    client = ElevenLabsClient()
    
    # Test connection
    if not await client.test_connection():
        logger.error("Failed to connect to ElevenLabs API")
        sys.exit(1)
    
    logger.info("ElevenLabs Integrations MCP server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ElevenLabs Integrations MCP server")
    if client:
        await client.close()


# Set lifespan
mcp.lifespan = lifespan


# Tool Management

@mcp.tool()
async def list_tools(
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
    
    API Endpoint: GET /v1/convai/tools
    """
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


@mcp.tool()
async def get_tool(
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
    
    API Endpoint: GET /v1/convai/tools/{tool_id}
    
    Tool Details Include:
        - Name and description
        - Input/output schemas
        - Authentication requirements
        - Rate limits and quotas
        - Usage statistics
    """
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


@mcp.tool()
async def create_tool(
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
    
    API Endpoint: POST /v1/convai/tools
    """
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


@mcp.tool()
async def update_tool(
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


@mcp.tool()
async def delete_tool(
    tool_id: str
) -> Dict[str, Any]:
    """
    Delete tool.
    
    Args:
        tool_id: Tool to delete
    
    Returns:
        Deletion confirmation
    """
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


@mcp.tool()
async def get_tool_dependent_agents(
    tool_id: str
) -> Dict[str, Any]:
    """
    Get agents using a tool.
    
    Args:
        tool_id: Tool identifier
    
    Returns:
        List of dependent agents
    """
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


# MCP Server Management

@mcp.tool()
async def create_mcp_server(
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


@mcp.tool()
async def list_mcp_servers(
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List MCP servers.
    
    Args:
        agent_id: Filter by agent
    
    Returns:
        List of MCP server configurations
    """
    try:
        if agent_id and not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error("Invalid agent ID format", "Use format: agent_XXXX")
        
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        
        result = await client._request(
            "GET",
            "/convai/mcp/servers",
            params=params,
            use_cache=True
        )
        
        servers = result.get("servers", [])
        
        return format_success(
            f"Found {len(servers)} MCP servers",
            {"servers": servers, "count": len(servers)}
        )
        
    except Exception as e:
        logger.error(f"Failed to list MCP servers: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_mcp_server(
    server_id: str
) -> Dict[str, Any]:
    """
    Get MCP server details.
    
    Args:
        server_id: Server identifier
    
    Returns:
        Server configuration
    """
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


@mcp.tool()
async def list_mcp_server_tools(
    server_id: str
) -> Dict[str, Any]:
    """
    List tools provided by MCP server.
    
    Args:
        server_id: Server identifier
    
    Returns:
        Available tools from server
    """
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


# Approval Management

@mcp.tool()
async def update_approval_policy(
    server_id: str,
    policy: Literal["always_ask", "fine_grained", "no_approval"]
) -> Dict[str, Any]:
    """
    Set tool approval policy.
    
    Args:
        server_id: MCP server ID
        policy: Approval policy
    
    Returns:
        Updated policy configuration
    """
    try:
        if not validate_elevenlabs_id(server_id, 'server'):
            return format_error("Invalid server ID format", "Use format: server_XXXX")
        
        result = await client._request(
            "PATCH",
            f"/convai/mcp/servers/{server_id}/approval-policy",
            json_data={"policy": policy}
        )
        
        return format_success(
            f"Updated approval policy to '{policy}'",
            {"policy": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to update approval policy for {server_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def create_tool_approval(
    server_id: str,
    tool_name: str,
    approval_mode: Literal["always", "never", "conditional"],
    conditions: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Add tool approval rule.
    
    Args:
        server_id: MCP server ID
        tool_name: Tool to configure
        approval_mode: Approval requirement
        conditions: Conditional approval rules
    
    Returns:
        Approval configuration
    """
    try:
        if not validate_elevenlabs_id(server_id, 'server'):
            return format_error("Invalid server ID format", "Use format: server_XXXX")
        
        data = {
            "tool_name": tool_name,
            "approval_mode": approval_mode,
            "conditions": conditions or {}
        }
        
        result = await client._request(
            "POST",
            f"/convai/mcp/servers/{server_id}/tool-approvals",
            json_data=data
        )
        
        return format_success(
            f"Created approval rule for '{tool_name}'",
            {"approval": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to create tool approval: {e}")
        return format_error(str(e))


@mcp.tool()
async def delete_tool_approval(
    server_id: str,
    approval_id: str
) -> Dict[str, Any]:
    """
    Remove tool approval rule.
    
    Args:
        server_id: MCP server ID
        approval_id: Approval rule ID
    
    Returns:
        Deletion confirmation
    """
    try:
        if not validate_elevenlabs_id(server_id, 'server'):
            return format_error("Invalid server ID format", "Use format: server_XXXX")
        
        await client._request(
            "DELETE",
            f"/convai/mcp/servers/{server_id}/tool-approvals/{approval_id}"
        )
        
        return format_success(
            f"Deleted approval rule {approval_id}",
            {"deleted": True}
        )
        
    except Exception as e:
        logger.error(f"Failed to delete tool approval: {e}")
        return format_error(str(e))


# Secrets Management

@mcp.tool()
async def get_secrets(
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List secrets.
    
    Args:
        agent_id: Filter by agent
    
    Returns:
        List of secret configurations (values hidden)
    """
    try:
        if agent_id and not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error("Invalid agent ID format", "Use format: agent_XXXX")
        
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        
        result = await client._request(
            "GET",
            "/convai/secrets",
            params=params,
            use_cache=True
        )
        
        secrets = result.get("secrets", [])
        
        return format_success(
            f"Found {len(secrets)} secrets",
            {"secrets": secrets, "count": len(secrets)}
        )
        
    except Exception as e:
        logger.error(f"Failed to list secrets: {e}")
        return format_error(str(e))


@mcp.tool()
async def create_secret(
    name: str,
    value: str,
    agent_id: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add secret.
    
    Args:
        name: Secret name
        value: Secret value
        agent_id: Associated agent
        description: Secret description
    
    Returns:
        Secret configuration (value hidden)
    """
    try:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error("Invalid agent ID format", "Use format: agent_XXXX")
        
        data = {
            "name": name,
            "value": value,
            "agent_id": agent_id,
            "description": description
        }
        
        result = await client._request(
            "POST",
            "/convai/secrets",
            json_data=data
        )
        
        # Remove value from response for security
        if "value" in result:
            result["value"] = "***"
        
        return format_success(
            f"Created secret '{name}'",
            {"secret": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to create secret: {e}")
        return format_error(str(e))


@mcp.tool()
async def update_secret(
    secret_id: str,
    value: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update secret.
    
    Args:
        secret_id: Secret to update
        value: New secret value
        description: New description
    
    Returns:
        Updated configuration (value hidden)
    """
    try:
        if not validate_elevenlabs_id(secret_id, 'secret'):
            return format_error("Invalid secret ID format", "Use format: secret_XXXX")
        
        data = {}
        if value:
            data["value"] = value
        if description:
            data["description"] = description
        
        result = await client._request(
            "PATCH",
            f"/convai/secrets/{secret_id}",
            json_data=data
        )
        
        # Remove value from response for security
        if "value" in result:
            result["value"] = "***"
        
        return format_success(
            f"Updated secret {secret_id}",
            {"secret": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to update secret {secret_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def delete_secret(
    secret_id: str
) -> Dict[str, Any]:
    """
    Delete secret.
    
    Args:
        secret_id: Secret to delete
    
    Returns:
        Deletion confirmation
    """
    try:
        if not validate_elevenlabs_id(secret_id, 'secret'):
            return format_error("Invalid secret ID format", "Use format: secret_XXXX")
        
        await client._request(
            "DELETE",
            f"/convai/secrets/{secret_id}"
        )
        
        return format_success(
            f"Deleted secret {secret_id}",
            {"deleted": True}
        )
        
    except Exception as e:
        logger.error(f"Failed to delete secret {secret_id}: {e}")
        return format_error(str(e))


# Resources

@mcp.resource("documentation")
async def get_documentation() -> str:
    """Get server documentation."""
    return """
# ElevenLabs Integrations MCP Server

Manage MCP servers, tools, approvals, and secrets for ElevenLabs agents.

## Features

### Tool Management
- Create and manage custom tools
- Track tool usage across agents
- Configure tool parameters

### MCP Server Integration
- Add MCP servers to agents
- Configure SSE/HTTP transport
- List available tools from servers

### Approval Policies
- Set approval requirements
- Configure fine-grained permissions
- Conditional approval rules

### Secrets Management
- Secure credential storage
- Agent-specific secrets
- Environment variable injection

## Tool Categories

### Tool Management
- list_tools: Browse available tools
- get_tool: Get tool details
- create_tool: Create custom tool
- update_tool: Modify tool configuration
- delete_tool: Remove tool
- get_tool_dependent_agents: Find tool usage

### MCP Servers
- create_mcp_server: Add MCP integration
- list_mcp_servers: List configured servers
- get_mcp_server: Get server details
- list_mcp_server_tools: Available server tools

### Approvals
- update_approval_policy: Set policy type
- create_tool_approval: Add approval rule
- delete_tool_approval: Remove approval

### Secrets
- get_secrets: List secrets (values hidden)
- create_secret: Add new secret
- update_secret: Modify secret
- delete_secret: Remove secret

## Usage Examples

### Add MCP Server
```python
create_mcp_server(
    agent_id="agent_xyz789",
    server_url="https://n8n.example.com/mcp",
    server_type="SSE",
    name="N8N Automation"
)
```

### Configure Approval Policy
```python
update_approval_policy(
    server_id="server_abc123",
    policy="fine_grained"
)

create_tool_approval(
    server_id="server_abc123",
    tool_name="execute_workflow",
    approval_mode="always"
)
```

### Add Secret
```python
create_secret(
    name="API_KEY",
    value="sk-...",
    agent_id="agent_xyz789",
    description="External API key"
)
```

## Approval Policies

### Always Ask
Require approval for every tool use

### Fine-Grained
Configure per-tool approval rules

### No Approval
Allow all tool usage without approval
"""


# Entry point
if __name__ == "__main__":
    import sys
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("✅ ElevenLabs Integrations MCP server initialized successfully")
        sys.exit(0)
    
    # Run the server
    mcp.run()