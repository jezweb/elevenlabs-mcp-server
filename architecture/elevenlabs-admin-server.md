# ElevenLabs Admin Server Architecture

## Overview
The `elevenlabs-admin` MCP server provides comprehensive workspace administration, member management, pronunciation dictionaries, webhooks, and advanced configuration capabilities.

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

## Tool Implementations

### Core Tools

```python
@mcp.tool()
async def list_workspace_members(
    page_size: int = 50
) -> Dict[str, Any]:
    """List all workspace members."""

@mcp.tool()
async def invite_member(
    email: str,
    role: str = "workspace_member",
    groups: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Invite new member to workspace."""

@mcp.tool()
async def update_member_role(
    email: str,
    new_role: str
) -> Dict[str, Any]:
    """Update member's workspace role."""

@mcp.tool()
async def remove_member(
    member_id: str
) -> Dict[str, Any]:
    """Remove member from workspace."""

@mcp.tool()
async def create_group(
    name: str,
    permissions: Dict[str, Any],
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create new permission group."""

@mcp.tool()
async def update_group_permissions(
    group_id: str,
    permissions: Dict[str, Any]
) -> Dict[str, Any]:
    """Update group permissions."""

@mcp.tool()
async def create_service_account(
    name: str,
    permissions: Dict[str, Any],
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create service account for API access."""

@mcp.tool()
async def generate_api_key(
    service_account_id: str,
    name: str,
    expires_in_days: Optional[int] = None
) -> Dict[str, Any]:
    """Generate new API key."""

@mcp.tool()
async def revoke_api_key(
    key_id: str
) -> Dict[str, Any]:
    """Revoke API key."""

@mcp.tool()
async def create_pronunciation_dictionary(
    name: str,
    rules: List[Dict[str, str]],
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create pronunciation dictionary."""

@mcp.tool()
async def add_pronunciation_rules(
    dictionary_id: str,
    rules: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Add rules to pronunciation dictionary."""

@mcp.tool()
async def create_webhook(
    url: str,
    events: List[str],
    secret: Optional[str] = None
) -> Dict[str, Any]:
    """Configure webhook for events."""

@mcp.tool()
async def test_webhook(
    webhook_id: str
) -> Dict[str, Any]:
    """Test webhook configuration."""

@mcp.tool()
async def get_workspace_settings() -> Dict[str, Any]:
    """Get workspace configuration."""

@mcp.tool()
async def update_workspace_settings(
    settings: Dict[str, Any]
) -> Dict[str, Any]:
    """Update workspace configuration."""
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

## Dependencies
- `elevenlabs>=1.0.0`
- `fastmcp>=0.3.0`
- `cryptography>=41.0.0` (for secrets)
- `pydantic>=2.0.0` (for validation)