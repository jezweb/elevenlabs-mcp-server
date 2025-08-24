"""
Secrets Management
==================
Tools for managing secure credentials and secrets.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


async def get_secrets(
    client,
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List secrets.
    
    Args:
        agent_id: Filter by agent
    
    Returns:
        List of secret configurations (values hidden)
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def create_secret(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def update_secret(
    client,
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
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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


async def delete_secret(
    client,
    secret_id: str
) -> Dict[str, Any]:
    """
    Delete secret.
    
    Args:
        secret_id: Secret to delete
    
    Returns:
        Deletion confirmation
    """
    from src.utils import format_error, format_success, validate_elevenlabs_id
    
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