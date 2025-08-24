"""
ElevenLabs Tools - Tool Modules
================================
Modular tools for managing ElevenLabs MCP integrations.
"""

# Tool Management
from .tools import (
    list_tools,
    get_tool,
    create_tool,
    update_tool,
    delete_tool,
    get_tool_dependent_agents
)

# MCP Server Management
from .servers import (
    create_mcp_server,
    get_mcp_server,
    list_mcp_server_tools
)

# Approval Management
from .approvals import (
    update_approval_policy,
    create_tool_approval,
    delete_tool_approval
)

# Secrets Management
from .secrets import (
    get_secrets,
    create_secret,
    update_secret,
    delete_secret
)

__all__ = [
    # Tool Management
    "list_tools",
    "get_tool",
    "create_tool",
    "update_tool",
    "delete_tool",
    "get_tool_dependent_agents",
    # MCP Server Management
    "create_mcp_server",
    "get_mcp_server",
    "list_mcp_server_tools",
    # Approval Management
    "update_approval_policy",
    "create_tool_approval",
    "delete_tool_approval",
    # Secrets Management
    "get_secrets",
    "create_secret",
    "update_secret",
    "delete_secret"
]