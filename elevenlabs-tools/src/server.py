"""ElevenLabs Tools MCP Server.

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

# Import all tools
from tools import (
    # Tool Management
    list_tools,
    get_tool,
    create_tool,
    update_tool,
    delete_tool,
    get_tool_dependent_agents,
    # MCP Server Management
    create_mcp_server,
    get_mcp_server,
    list_mcp_server_tools,
    # Approval Management
    update_approval_policy,
    create_tool_approval,
    delete_tool_approval,
    # Secrets Management
    get_secrets,
    create_secret,
    update_secret,
    delete_secret
)

# Setup logging
logger = setup_logging(__name__)

# Validate configuration
if not Config.API_KEY:
    logger.error("ELEVENLABS_API_KEY not set")
    sys.exit(1)

# Initialize ElevenLabs client at module level
client = ElevenLabsClient(Config.API_KEY)

# Initialize FastMCP server
mcp = FastMCP(
    name="elevenlabs-tools",
    instructions="Manage ElevenLabs MCP servers, tools, and integrations"
)


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for the MCP server."""
    # Startup
    logger.info("Starting ElevenLabs Tools MCP server")
    
    # Test connection
    if not await client.test_connection():
        logger.error("Failed to connect to ElevenLabs API")
        logger.warning("Some features may be unavailable")
    else:
        logger.info("ElevenLabs API connection verified")
    
    logger.info("ElevenLabs Tools MCP server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ElevenLabs Tools MCP server")
    if client:
        await client.close()


# Set lifespan
mcp.lifespan = lifespan


# ============================================================
# Tool Management
# ============================================================

@mcp.tool()
async def list_tools_tool(
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
    return await list_tools(client, agent_id, tool_type, limit)


@mcp.tool()
async def get_tool_tool(
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
    return await get_tool(client, tool_id)


@mcp.tool()
async def create_tool_tool(
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
    return await create_tool(client, name, description, tool_type, configuration, metadata)


@mcp.tool()
async def update_tool_tool(
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
    return await update_tool(client, tool_id, name, description, configuration, metadata)


@mcp.tool()
async def delete_tool_tool(
    tool_id: str
) -> Dict[str, Any]:
    """
    Delete tool.
    
    Args:
        tool_id: Tool to delete
    
    Returns:
        Deletion confirmation
    """
    return await delete_tool(client, tool_id)


@mcp.tool()
async def get_tool_dependent_agents_tool(
    tool_id: str
) -> Dict[str, Any]:
    """
    Get agents using a tool.
    
    Args:
        tool_id: Tool identifier
    
    Returns:
        List of dependent agents
    """
    return await get_tool_dependent_agents(client, tool_id)


# ============================================================
# MCP Server Management
# ============================================================

@mcp.tool()
async def create_mcp_server_tool(
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
    return await create_mcp_server(client, agent_id, server_url, server_type, name, description)



@mcp.tool()
async def get_mcp_server_tool(
    server_id: str
) -> Dict[str, Any]:
    """
    Get MCP server details.
    
    Args:
        server_id: Server identifier
    
    Returns:
        Server configuration
    """
    return await get_mcp_server(client, server_id)


@mcp.tool()
async def list_mcp_server_tools_tool(
    server_id: str
) -> Dict[str, Any]:
    """
    List tools provided by MCP server.
    
    Args:
        server_id: Server identifier
    
    Returns:
        Available tools from server
    """
    return await list_mcp_server_tools(client, server_id)


# ============================================================
# Approval Management
# ============================================================

@mcp.tool()
async def update_approval_policy_tool(
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
    return await update_approval_policy(client, server_id, policy)


@mcp.tool()
async def create_tool_approval_tool(
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
    return await create_tool_approval(client, server_id, tool_name, approval_mode, conditions)


@mcp.tool()
async def delete_tool_approval_tool(
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
    return await delete_tool_approval(client, server_id, approval_id)


# ============================================================
# Secrets Management
# ============================================================

@mcp.tool()
async def get_secrets_tool(
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List secrets.
    
    Args:
        agent_id: Filter by agent
    
    Returns:
        List of secret configurations (values hidden)
    """
    return await get_secrets(client, agent_id)


@mcp.tool()
async def create_secret_tool(
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
    return await create_secret(client, name, value, agent_id, description)


@mcp.tool()
async def update_secret_tool(
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
    return await update_secret(client, secret_id, value, description)


@mcp.tool()
async def delete_secret_tool(
    secret_id: str
) -> Dict[str, Any]:
    """
    Delete secret.
    
    Args:
        secret_id: Secret to delete
    
    Returns:
        Deletion confirmation
    """
    return await delete_secret(client, secret_id)


# Resources

@mcp.resource("resource://documentation")
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