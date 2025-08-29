"""
Approval Management
===================
Tools for managing tool approval policies and rules.
"""

import logging
from typing import Any, Dict, Optional, Literal

logger = logging.getLogger(__name__)


async def update_approval_policy(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    try:
        if not validate_elevenlabs_id(server_id, 'server'):
            return format_error("Invalid server ID format", "Use format: server_XXXX")
        
        result = await client._request(
            "PATCH",
            f"/convai/mcp-servers/{server_id}/approval-policy",
            json_data={"policy": policy}
        )
        
        return format_success(
            f"Updated approval policy to '{policy}'",
            {"policy": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to update approval policy for {server_id}: {e}")
        return format_error(str(e))


async def create_tool_approval(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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
            f"/convai/mcp-servers/{server_id}/tool-approvals",
            json_data=data
        )
        
        return format_success(
            f"Created approval rule for '{tool_name}'",
            {"approval": result}
        )
        
    except Exception as e:
        logger.error(f"Failed to create tool approval: {e}")
        return format_error(str(e))


async def delete_tool_approval(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
    try:
        if not validate_elevenlabs_id(server_id, 'server'):
            return format_error("Invalid server ID format", "Use format: server_XXXX")
        
        await client._request(
            "DELETE",
            f"/convai/mcp-servers/{server_id}/tool-approvals/{approval_id}"
        )
        
        return format_success(
            f"Deleted approval rule {approval_id}",
            {"deleted": True}
        )
        
    except Exception as e:
        logger.error(f"Failed to delete tool approval: {e}")
        return format_error(str(e))