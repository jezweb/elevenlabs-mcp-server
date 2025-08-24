# ElevenLabs Admin Server Architecture

## Overview
The `elevenlabs-admin` MCP server provides comprehensive workspace administration, member management, pronunciation dictionaries, webhooks, and advanced configuration capabilities.

## Directory Structure (Modular)

```
elevenlabs-admin/
├── src/
│   ├── server.py                    # Main FastMCP server with tool registration
│   ├── utils.py                     # Self-contained utilities (client, config, validation)
│   └── tools/
│       ├── __init__.py
│       ├── workspace_tools.py       # Workspace settings and configuration
│       ├── member_tools.py          # Member and invitation management
│       ├── group_tools.py           # Group and permission management
│       ├── service_account_tools.py # Service accounts and API keys
│       ├── dictionary_tools.py      # Pronunciation dictionaries
│       └── webhook_tools.py         # Webhook configuration
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### 1. Workspace Management

#### Get Workspace Settings
- **Endpoint**: `GET /v1/workspace`
- **Description**: Get current workspace configuration
- **Response**:
  ```json
  {
    "workspace_id": "string",
    "name": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "settings": {
      "default_voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
      },
      "allowed_tts_models": ["eleven_multilingual_v2"],
      "max_character_limit": 1000000,
      "workspace_role_default": "workspace_member",
      "require_2fa": false,
      "api_access_enabled": true,
      "sso_provider": "none|google|microsoft",
      "data_retention_days": 90
    }
  }
  ```

#### Update Workspace Settings
- **Endpoint**: `PATCH /v1/workspace`
- **Description**: Update workspace configuration
- **Parameters**:
  - `name` (body, optional): Workspace name
  - `settings` (body, optional): Configuration object

### 2. Member Management

#### List Members
- **Endpoint**: `GET /v1/workspace/members`
- **Description**: Get all workspace members
- **Parameters**:
  - `page_size` (query, optional): Results per page
  - `start_after_member_id` (query, optional): Pagination cursor
- **Response**:
  ```json
  {
    "members": [
      {
        "member_id": "string",
        "email": "user@example.com",
        "name": "string",
        "workspace_role": "workspace_admin|workspace_member",
        "is_locked": false,
        "is_owner": false,
        "joined_at": "2024-01-01T00:00:00Z",
        "last_active": "2024-01-01T00:00:00Z",
        "character_usage": 10000,
        "groups": ["group_id_1", "group_id_2"]
      }
    ],
    "has_more": true
  }
  ```

#### Invite Member
- **Endpoint**: `POST /v1/workspace/invites`
- **Description**: Invite new member to workspace
- **Parameters**:
  - `email` (body, required): Email to invite
  - `workspace_role` (body, required): Initial role
  - `groups` (body, optional): Group assignments
  - `send_email` (body, optional): Send invite email (default true)

#### Update Member
- **Endpoint**: `POST /v1/workspace/members`
- **Description**: Update member settings
- **Parameters**:
  - `email` (body, required): Member email
  - `workspace_role` (body, optional): New role
  - `is_locked` (body, optional): Lock/unlock account
  - `groups` (body, optional): Update group assignments

#### Remove Member
- **Endpoint**: `DELETE /v1/workspace/members/{member_id}`
- **Description**: Remove member from workspace
- **Parameters**:
  - `member_id` (path, required): Member ID

### 3. Group Management

#### List Groups
- **Endpoint**: `GET /v1/workspace/groups`
- **Description**: Get all workspace groups
- **Response**:
  ```json
  {
    "groups": [
      {
        "group_id": "string",
        "name": "string",
        "description": "string",
        "member_count": 10,
        "permissions": {
          "can_use_instant_voice_cloning": true,
          "can_use_professional_voice_cloning": false,
          "can_manage_pronunciation_dictionaries": true,
          "can_access_api": true,
          "max_character_limit": 100000,
          "allowed_models": ["eleven_multilingual_v2"],
          "allowed_voices": ["voice_id_1", "voice_id_2"]
        },
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
  ```

#### Create Group
- **Endpoint**: `POST /v1/workspace/groups`
- **Description**: Create new group
- **Parameters**:
  - `name` (body, required): Group name
  - `description` (body, optional): Description
  - `permissions` (body, required): Permission set

#### Update Group
- **Endpoint**: `PATCH /v1/workspace/groups/{group_id}`
- **Description**: Update group settings
- **Parameters**:
  - `group_id` (path, required): Group ID
  - `name` (body, optional): New name
  - `description` (body, optional): New description
  - `permissions` (body, optional): Updated permissions

#### Delete Group
- **Endpoint**: `DELETE /v1/workspace/groups/{group_id}`
- **Description**: Delete a group
- **Parameters**:
  - `group_id` (path, required): Group ID

### 4. Service Accounts & API Keys

#### List Service Accounts
- **Endpoint**: `GET /v1/workspace/service-accounts`
- **Description**: Get all service accounts
- **Response**:
  ```json
  {
    "service_accounts": [
      {
        "account_id": "string",
        "name": "string",
        "description": "string",
        "created_at": "2024-01-01T00:00:00Z",
        "last_used": "2024-01-01T00:00:00Z",
        "permissions": {},
        "api_keys": [
          {
            "key_id": "string",
            "name": "string",
            "last_4": "abcd",
            "created_at": "2024-01-01T00:00:00Z",
            "last_used": "2024-01-01T00:00:00Z",
            "expires_at": "2024-12-31T00:00:00Z"
          }
        ]
      }
    ]
  }
  ```

#### Create Service Account
- **Endpoint**: `POST /v1/workspace/service-accounts`
- **Description**: Create new service account
- **Parameters**:
  - `name` (body, required): Account name
  - `description` (body, optional): Description
  - `permissions` (body, required): Permission set

#### Create API Key
- **Endpoint**: `POST /v1/workspace/service-accounts/{account_id}/api-keys`
- **Description**: Generate new API key
- **Parameters**:
  - `account_id` (path, required): Service account ID
  - `name` (body, required): Key name
  - `expires_in_days` (body, optional): Expiration (0 = never)
- **Response**:
  ```json
  {
    "api_key": "xi-abc123...",
    "key_id": "string",
    "expires_at": "2024-12-31T00:00:00Z"
  }
  ```

#### Revoke API Key
- **Endpoint**: `DELETE /v1/workspace/api-keys/{key_id}`
- **Description**: Revoke an API key
- **Parameters**:
  - `key_id` (path, required): API key ID

### 5. Pronunciation Dictionaries

#### List Dictionaries
- **Endpoint**: `GET /v1/pronunciation-dictionaries`
- **Description**: Get all pronunciation dictionaries
- **Response**:
  ```json
  {
    "pronunciation_dictionaries": [
      {
        "pronunciation_dictionary_id": "string",
        "name": "string",
        "description": "string",
        "created_by": "user@example.com",
        "creation_time_unix": 1234567890,
        "version_id": "string",
        "latest_version_id": "string"
      }
    ]
  }
  ```

#### Create Dictionary from File
- **Endpoint**: `POST /v1/pronunciation-dictionaries/add-from-file`
- **Description**: Create dictionary from PLS file
- **Parameters**:
  - `name` (form, required): Dictionary name
  - `file` (form, required): .pls lexicon file
  - `description` (form, optional): Description
  - `workspace_access` (form, optional): Access level

#### Add Rules to Dictionary
- **Endpoint**: `POST /v1/pronunciation-dictionaries/{dictionary_id}/add-rules`
- **Description**: Add pronunciation rules
- **Parameters**:
  - `dictionary_id` (path, required): Dictionary ID
  - `rules` (body, required): Array of rules:
    ```json
    [
      {
        "string_to_replace": "AI",
        "phoneme": "eɪ aɪ",
        "alphabet": "ipa"
      }
    ]
    ```

#### Remove Rules from Dictionary
- **Endpoint**: `POST /v1/pronunciation-dictionaries/{dictionary_id}/remove-rules`
- **Description**: Remove pronunciation rules
- **Parameters**:
  - `dictionary_id` (path, required): Dictionary ID
  - `rule_strings` (body, required): Array of strings to remove

#### Get Dictionary
- **Endpoint**: `GET /v1/pronunciation-dictionaries/{dictionary_id}`
- **Description**: Get dictionary details and rules
- **Parameters**:
  - `dictionary_id` (path, required): Dictionary ID

#### Delete Dictionary
- **Endpoint**: `DELETE /v1/pronunciation-dictionaries/{dictionary_id}`
- **Description**: Delete a dictionary
- **Parameters**:
  - `dictionary_id` (path, required): Dictionary ID

### 6. Webhooks

#### List Webhooks
- **Endpoint**: `GET /v1/workspace/webhooks`
- **Description**: Get all configured webhooks
- **Response**:
  ```json
  {
    "webhooks": [
      {
        "webhook_id": "string",
        "url": "https://example.com/webhook",
        "events": ["voice.created", "generation.completed"],
        "secret": "webhook_secret_...",
        "enabled": true,
        "created_at": "2024-01-01T00:00:00Z",
        "failure_count": 0,
        "last_triggered": "2024-01-01T00:00:00Z"
      }
    ]
  }
  ```

#### Create Webhook
- **Endpoint**: `POST /v1/workspace/webhooks`
- **Description**: Configure new webhook
- **Parameters**:
  - `url` (body, required): Webhook endpoint URL
  - `events` (body, required): Array of event types
  - `secret` (body, optional): Webhook secret for validation
  - `enabled` (body, optional): Enable immediately (default true)

#### Update Webhook
- **Endpoint**: `PATCH /v1/workspace/webhooks/{webhook_id}`
- **Description**: Update webhook configuration
- **Parameters**:
  - `webhook_id` (path, required): Webhook ID
  - `url` (body, optional): New URL
  - `events` (body, optional): Updated events
  - `enabled` (body, optional): Enable/disable

#### Delete Webhook
- **Endpoint**: `DELETE /v1/workspace/webhooks/{webhook_id}`
- **Description**: Remove webhook
- **Parameters**:
  - `webhook_id` (path, required): Webhook ID

#### Test Webhook
- **Endpoint**: `POST /v1/workspace/webhooks/{webhook_id}/test`
- **Description**: Send test event to webhook
- **Parameters**:
  - `webhook_id` (path, required): Webhook ID

### 7. Models Management

#### List Available Models
- **Endpoint**: `GET /v1/models`
- **Description**: Get all available models
- **Response**:
  ```json
  {
    "models": [
      {
        "model_id": "eleven_multilingual_v2",
        "name": "Eleven Multilingual v2",
        "can_be_finetuned": true,
        "can_do_text_to_speech": true,
        "can_do_voice_conversion": true,
        "can_use_style": true,
        "can_use_speaker_boost": true,
        "serves_pro_voices": true,
        "token_cost_factor": 1.0,
        "description": "string",
        "requires_alpha_access": false,
        "max_characters_request_free_user": 333,
        "max_characters_request_subscribed_user": 5000,
        "maximum_text_length_per_request": 5000,
        "languages": [
          {
            "language_id": "en",
            "name": "English"
          }
        ]
      }
    ]
  }
  ```

## Modular Tool Implementation

### Tool Modules

#### 1. workspace_tools.py
```python
"""Workspace settings and configuration tools."""

async def get_workspace_settings(client):
    """Get workspace configuration."""
    
async def update_workspace_settings(client, settings):
    """Update workspace configuration."""
    
async def get_workspace_stats(client):
    """Get workspace usage statistics."""
    
async def export_workspace_config(client):
    """Export workspace configuration."""
    
async def import_workspace_config(client, config):
    """Import workspace configuration."""
```

#### 2. member_tools.py
```python
"""Member and invitation management tools."""

async def list_workspace_members(client, page_size=50):
    """List all workspace members."""
    
async def invite_member(client, email, role="workspace_member", groups=None):
    """Invite new member to workspace."""
    
async def update_member_role(client, email, new_role):
    """Update member's workspace role."""
    
async def remove_member(client, member_id):
    """Remove member from workspace."""
    
async def lock_member_account(client, member_id):
    """Lock a member account."""
    
async def unlock_member_account(client, member_id):
    """Unlock a member account."""
    
async def get_member_activity(client, member_id):
    """Get member activity history."""
```

#### 3. group_tools.py
```python
"""Group and permission management tools."""

async def list_groups(client):
    """List all permission groups."""
    
async def create_group(client, name, permissions, description=None):
    """Create new permission group."""
    
async def update_group_permissions(client, group_id, permissions):
    """Update group permissions."""
    
async def delete_group(client, group_id):
    """Delete a permission group."""
    
async def add_members_to_group(client, group_id, member_ids):
    """Add members to group."""
    
async def remove_members_from_group(client, group_id, member_ids):
    """Remove members from group."""
```

#### 4. service_account_tools.py
```python
"""Service account and API key management tools."""

async def list_service_accounts(client):
    """List all service accounts."""
    
async def create_service_account(client, name, permissions, description=None):
    """Create service account for API access."""
    
async def update_service_account(client, account_id, permissions):
    """Update service account permissions."""
    
async def delete_service_account(client, account_id):
    """Delete service account."""
    
async def generate_api_key(client, service_account_id, name, expires_in_days=None):
    """Generate new API key."""
    
async def revoke_api_key(client, key_id):
    """Revoke API key."""
    
async def list_api_keys(client, service_account_id=None):
    """List API keys."""
    
async def rotate_api_key(client, key_id):
    """Rotate API key."""
```

#### 5. dictionary_tools.py
```python
"""Pronunciation dictionary management tools."""

async def list_dictionaries(client):
    """List all pronunciation dictionaries."""
    
async def create_pronunciation_dictionary(client, name, rules, description=None):
    """Create pronunciation dictionary."""
    
async def create_dictionary_from_file(client, name, file_path, description=None):
    """Create dictionary from PLS file."""
    
async def add_pronunciation_rules(client, dictionary_id, rules):
    """Add rules to pronunciation dictionary."""
    
async def remove_pronunciation_rules(client, dictionary_id, rule_strings):
    """Remove rules from dictionary."""
    
async def get_dictionary(client, dictionary_id):
    """Get dictionary details and rules."""
    
async def delete_dictionary(client, dictionary_id):
    """Delete pronunciation dictionary."""
    
async def export_dictionary(client, dictionary_id, format="pls"):
    """Export dictionary to file."""
```

#### 6. webhook_tools.py
```python
"""Webhook configuration and management tools."""

async def list_webhooks(client):
    """List all configured webhooks."""
    
async def create_webhook(client, url, events, secret=None):
    """Configure webhook for events."""
    
async def update_webhook(client, webhook_id, url=None, events=None, enabled=None):
    """Update webhook configuration."""
    
async def delete_webhook(client, webhook_id):
    """Delete webhook."""
    
async def test_webhook(client, webhook_id):
    """Test webhook configuration."""
    
async def get_webhook_logs(client, webhook_id, limit=100):
    """Get webhook delivery logs."""
    
async def retry_webhook_delivery(client, webhook_id, delivery_id):
    """Retry failed webhook delivery."""
```

### Tool Registration (server.py)

```python
from fastmcp import FastMCP
from utils import Config, ElevenLabsClient

# Import all tool modules
from tools import (
    workspace_tools,
    member_tools,
    group_tools,
    service_account_tools,
    dictionary_tools,
    webhook_tools
)

# Initialize
mcp = FastMCP(name="elevenlabs-admin")
client = ElevenLabsClient(Config.API_KEY)

# Register workspace tools
@mcp.tool()
async def get_workspace_settings():
    return await workspace_tools.get_workspace_settings(client)

@mcp.tool()
async def update_workspace_settings(settings: dict):
    return await workspace_tools.update_workspace_settings(client, settings)

# Register member tools
@mcp.tool()
async def list_workspace_members(page_size: int = 50):
    return await member_tools.list_workspace_members(client, page_size)

@mcp.tool()
async def invite_member(email: str, role: str = "workspace_member", groups: list = None):
    return await member_tools.invite_member(client, email, role, groups)

# Register group tools
@mcp.tool()
async def create_group(name: str, permissions: dict, description: str = None):
    return await group_tools.create_group(client, name, permissions, description)

# ... register remaining tools ...
```

## Resources

```python
@mcp.resource("workspace://settings")
async def get_workspace_resource() -> Resource:
    """Get workspace settings as resource."""

@mcp.resource("members://list")
async def get_members_resource() -> Resource:
    """Get member list as resource."""

@mcp.resource("groups://{group_id}")
async def get_group_resource(group_id: str) -> Resource:
    """Get group details as resource."""

@mcp.resource("dictionary://{dictionary_id}")
async def get_dictionary_resource(dictionary_id: str) -> Resource:
    """Get pronunciation dictionary as resource."""
```

## Configuration

### Environment Variables
- `ELEVENLABS_API_KEY`: Admin API key (requires admin role)
- `WORKSPACE_ID`: Target workspace ID
- `WEBHOOK_SECRET`: Default webhook secret
- `DICTIONARY_DIR`: Directory for dictionary files
- `BACKUP_DIR`: Directory for configuration backups

### Permission Levels
- `workspace_owner`: Full control
- `workspace_admin`: Manage members, settings
- `workspace_member`: Basic access

### Event Types for Webhooks
- `voice.created`: New voice added
- `voice.deleted`: Voice removed
- `generation.completed`: Audio generated
- `generation.failed`: Generation error
- `member.added`: Member joined
- `member.removed`: Member left
- `quota.warning`: Usage warning
- `quota.exceeded`: Quota limit hit

## Error Handling

```python
class InsufficientPermissionsError(Exception):
    """User lacks required permissions."""

class MemberNotFoundError(Exception):
    """Member not found in workspace."""

class GroupNotFoundError(Exception):
    """Group not found."""

class DictionaryError(Exception):
    """Pronunciation dictionary error."""

class WebhookError(Exception):
    """Webhook configuration error."""
```

## Usage Examples

### Invite Member with Groups
```python
result = await invite_member(
    email="newuser@example.com",
    role="workspace_member",
    groups=["content_creators", "voice_users"]
)
# Returns: {"member_id": "mem_123", "invite_sent": true}
```

### Create Service Account with API Key
```python
account = await create_service_account(
    name="Production API",
    permissions={"can_use_api": true, "max_characters": 100000}
)
key = await generate_api_key(
    service_account_id=account["account_id"],
    name="prod-key-1",
    expires_in_days=90
)
# Returns: {"api_key": "xi-...", "expires_at": "2024-04-01"}
```

### Configure Webhook
```python
result = await create_webhook(
    url="https://myapp.com/elevenlabs-webhook",
    events=["generation.completed", "quota.warning"],
    secret="my_webhook_secret"
)
# Returns: {"webhook_id": "wh_123", "status": "active"}
```

## Security Features

### API Key Management
- Scoped permissions
- Expiration dates
- Usage tracking
- Rotation policies

### Access Control
- Role-based permissions
- Group-based access
- IP restrictions
- 2FA enforcement

### Audit Logging
- All admin actions logged
- Member activity tracking
- API usage monitoring
- Security event alerts

## Self-Contained Utils Module

```python
"""
utils.py - All utilities for the admin server
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import asyncio
import aiohttp
import secrets
import hashlib
import json
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# ============================================================
# Configuration
# ============================================================

class Config:
    """Configuration from environment variables."""
    API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    API_BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Admin settings
    WORKSPACE_ID = os.getenv("WORKSPACE_ID", "")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
    
    # Security settings
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")  # For storing secrets
    WEBHOOK_SECRET_LENGTH = int(os.getenv("WEBHOOK_SECRET_LENGTH", "32"))
    API_KEY_PREFIX = os.getenv("API_KEY_PREFIX", "xi-")
    
    # Limits
    MAX_MEMBERS_PER_GROUP = int(os.getenv("MAX_MEMBERS_PER_GROUP", "100"))
    MAX_RULES_PER_DICTIONARY = int(os.getenv("MAX_RULES_PER_DICTIONARY", "1000"))
    MAX_WEBHOOKS = int(os.getenv("MAX_WEBHOOKS", "10"))
    
    # Defaults
    DEFAULT_MEMBER_ROLE = os.getenv("DEFAULT_MEMBER_ROLE", "workspace_member")
    DEFAULT_API_KEY_EXPIRY_DAYS = int(os.getenv("DEFAULT_API_KEY_EXPIRY_DAYS", "90"))
    
    @classmethod
    def validate(cls):
        if not cls.API_KEY:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
        if not cls.ENCRYPTION_KEY:
            cls.ENCRYPTION_KEY = Fernet.generate_key().decode()
            logger.warning("Generated temporary encryption key - set ENCRYPTION_KEY for persistence")

# ============================================================
# API Client
# ============================================================

class ElevenLabsClient:
    """Admin-focused API client."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.API_BASE_URL
        self._session = None
        self._fernet = Fernet(Config.ENCRYPTION_KEY.encode()) if Config.ENCRYPTION_KEY else None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
            )
        return self._session
    
    # Workspace methods
    async def get_workspace(self) -> Dict[str, Any]:
        """Get workspace configuration."""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/workspace") as response:
            response.raise_for_status()
            return await response.json()
    
    async def update_workspace(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update workspace settings."""
        session = await self._get_session()
        async with session.patch(f"{self.base_url}/workspace", json=settings) as response:
            response.raise_for_status()
            return await response.json()
    
    # Member methods
    async def list_members(self, **params) -> Dict[str, Any]:
        """List workspace members."""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/workspace/members", params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def invite_member(self, email: str, role: str, **kwargs) -> Dict[str, Any]:
        """Invite new member."""
        session = await self._get_session()
        payload = {"email": email, "workspace_role": role, **kwargs}
        async with session.post(f"{self.base_url}/workspace/invites", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    # Group methods
    async def create_group(self, name: str, permissions: Dict, **kwargs) -> Dict[str, Any]:
        """Create permission group."""
        session = await self._get_session()
        payload = {"name": name, "permissions": permissions, **kwargs}
        async with session.post(f"{self.base_url}/workspace/groups", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    # Service account methods
    async def create_service_account(self, name: str, permissions: Dict, **kwargs) -> Dict[str, Any]:
        """Create service account."""
        session = await self._get_session()
        payload = {"name": name, "permissions": permissions, **kwargs}
        async with session.post(f"{self.base_url}/workspace/service-accounts", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def generate_api_key(self, account_id: str, name: str, **kwargs) -> Dict[str, Any]:
        """Generate API key for service account."""
        session = await self._get_session()
        payload = {"name": name, **kwargs}
        url = f"{self.base_url}/workspace/service-accounts/{account_id}/api-keys"
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            
            # Encrypt the API key for storage if encryption is available
            if self._fernet and "api_key" in data:
                data["encrypted_key"] = self._fernet.encrypt(data["api_key"].encode()).decode()
            
            return data
    
    # Dictionary methods
    async def create_dictionary(self, name: str, rules: List[Dict], **kwargs) -> Dict[str, Any]:
        """Create pronunciation dictionary."""
        session = await self._get_session()
        payload = {"name": name, "rules": rules, **kwargs}
        async with session.post(f"{self.base_url}/pronunciation-dictionaries", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def create_dictionary_from_file(self, name: str, file_path: str, **kwargs) -> Dict[str, Any]:
        """Create dictionary from PLS file."""
        session = await self._get_session()
        
        with open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('name', name)
            data.add_field('file', f, filename=os.path.basename(file_path))
            for key, value in kwargs.items():
                data.add_field(key, str(value))
            
            async with session.post(
                f"{self.base_url}/pronunciation-dictionaries/add-from-file",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # Webhook methods
    async def create_webhook(self, url: str, events: List[str], secret: str = None) -> Dict[str, Any]:
        """Create webhook."""
        if not secret:
            secret = generate_webhook_secret()
        
        session = await self._get_session()
        payload = {"url": url, "events": events, "secret": secret}
        async with session.post(f"{self.base_url}/workspace/webhooks", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def close(self):
        """Close the client session."""
        if self._session:
            await self._session.close()

# ============================================================
# Security Utilities
# ============================================================

def generate_webhook_secret(length: int = None) -> str:
    """Generate secure webhook secret."""
    length = length or Config.WEBHOOK_SECRET_LENGTH
    return secrets.token_urlsafe(length)

def generate_api_key_name(service: str) -> str:
    """Generate API key name with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{service}_key_{timestamp}"

def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def encrypt_sensitive_data(data: str, key: bytes = None) -> str:
    """Encrypt sensitive data."""
    key = key or Config.ENCRYPTION_KEY.encode()
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted: str, key: bytes = None) -> str:
    """Decrypt sensitive data."""
    key = key or Config.ENCRYPTION_KEY.encode()
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()

# ============================================================
# Permission Management
# ============================================================

class PermissionSet:
    """Standard permission sets for groups and service accounts."""
    
    READONLY = {
        "can_read": True,
        "can_write": False,
        "can_delete": False,
        "can_use_api": True,
        "can_use_instant_voice_cloning": False,
        "can_use_professional_voice_cloning": False,
        "can_manage_pronunciation_dictionaries": False,
        "max_character_limit": 10000
    }
    
    STANDARD = {
        "can_read": True,
        "can_write": True,
        "can_delete": False,
        "can_use_api": True,
        "can_use_instant_voice_cloning": True,
        "can_use_professional_voice_cloning": False,
        "can_manage_pronunciation_dictionaries": True,
        "max_character_limit": 100000
    }
    
    ADMIN = {
        "can_read": True,
        "can_write": True,
        "can_delete": True,
        "can_use_api": True,
        "can_use_instant_voice_cloning": True,
        "can_use_professional_voice_cloning": True,
        "can_manage_pronunciation_dictionaries": True,
        "max_character_limit": 1000000,
        "can_manage_members": True,
        "can_manage_groups": True,
        "can_manage_webhooks": True
    }
    
    @classmethod
    def get_preset(cls, level: str) -> Dict[str, Any]:
        """Get permission preset by level."""
        presets = {
            "readonly": cls.READONLY,
            "standard": cls.STANDARD,
            "admin": cls.ADMIN
        }
        return presets.get(level.lower(), cls.READONLY)

# ============================================================
# Validation
# ============================================================

def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_workspace_role(role: str) -> str:
    """Validate workspace role."""
    valid_roles = ["workspace_admin", "workspace_member", "workspace_viewer"]
    if role not in valid_roles:
        raise ValueError(f"Invalid role: {role}. Must be one of {valid_roles}")
    return role

def validate_webhook_events(events: List[str]) -> List[str]:
    """Validate webhook event types."""
    valid_events = [
        "voice.created", "voice.updated", "voice.deleted",
        "generation.started", "generation.completed", "generation.failed",
        "member.added", "member.removed", "member.updated",
        "api_key.created", "api_key.revoked",
        "workspace.updated"
    ]
    
    invalid = [e for e in events if e not in valid_events]
    if invalid:
        raise ValueError(f"Invalid events: {invalid}")
    
    return events

def validate_pronunciation_rule(rule: Dict[str, str]) -> Dict[str, str]:
    """Validate pronunciation dictionary rule."""
    required = ["string_to_replace", "phoneme", "alphabet"]
    
    for field in required:
        if field not in rule:
            raise ValueError(f"Missing required field: {field}")
    
    if rule["alphabet"] not in ["ipa", "cmu"]:
        raise ValueError(f"Invalid alphabet: {rule['alphabet']}. Must be 'ipa' or 'cmu'")
    
    return rule

# ============================================================
# Response Formatting
# ============================================================

def format_member_response(member: Dict[str, Any]) -> Dict[str, Any]:
    """Format member data for response."""
    return {
        "success": True,
        "member": {
            "id": member.get("member_id"),
            "email": member.get("email"),
            "name": member.get("name"),
            "role": member.get("workspace_role"),
            "status": "active" if not member.get("is_locked") else "locked",
            "joined": member.get("joined_at"),
            "groups": member.get("groups", [])
        }
    }

def format_api_key_response(key_data: Dict[str, Any], mask: bool = True) -> Dict[str, Any]:
    """Format API key response."""
    response = {
        "success": True,
        "api_key": {
            "id": key_data.get("key_id"),
            "name": key_data.get("name"),
            "created": key_data.get("created_at"),
            "expires": key_data.get("expires_at")
        }
    }
    
    if "api_key" in key_data and not mask:
        response["api_key"]["key"] = key_data["api_key"]
    elif "api_key" in key_data:
        # Show only last 4 characters
        key = key_data["api_key"]
        response["api_key"]["key_masked"] = f"xi-...{key[-4:]}"
    
    return response

def format_error(error: Exception) -> Dict[str, Any]:
    """Format error response."""
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "timestamp": datetime.now().isoformat()
    }
```

## Dependencies
- `elevenlabs>=1.0.0`
- `fastmcp>=0.3.0`
- `cryptography>=41.0.0` (for secrets)
- `aiohttp>=3.9.0`