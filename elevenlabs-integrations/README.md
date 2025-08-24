# ElevenLabs Integrations MCP Server

Manage MCP servers, tools, approvals, and secrets for ElevenLabs conversational AI agents.

## Features

- **Tool Management**: Create and manage custom tools for agents
- **MCP Server Integration**: Connect agents to external MCP servers
- **Approval Policies**: Configure tool usage permissions
- **Secrets Management**: Secure credential storage for agents
- **Dependency Tracking**: Find which agents use specific tools
- **Fine-Grained Control**: Per-tool approval configuration

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Add your ElevenLabs API key:
   ```
   ELEVENLABS_API_KEY=your_api_key_here
   ```

## Usage

### Run the server

```bash
python src/server.py
```

### Test the server

```bash
python src/server.py --test
```

## Available Tools

### Tool Management

- `list_tools`: Browse available tools
- `get_tool`: Get tool configuration details
- `create_tool`: Create custom tool
- `update_tool`: Modify tool configuration
- `delete_tool`: Remove tool
- `get_tool_dependent_agents`: Find agents using a tool

### MCP Server Management

- `create_mcp_server`: Add MCP server integration
- `list_mcp_servers`: List configured servers
- `get_mcp_server`: Get server details
- `list_mcp_server_tools`: List tools from a server

### Approval Management

- `update_approval_policy`: Set approval policy (always_ask, fine_grained, no_approval)
- `create_tool_approval`: Add tool-specific approval rule
- `delete_tool_approval`: Remove approval rule

### Secrets Management

- `get_secrets`: List secrets (values hidden)
- `create_secret`: Add new secret
- `update_secret`: Modify secret value or description
- `delete_secret`: Remove secret

## Examples

### Add MCP Server Integration

```python
await create_mcp_server(
    agent_id="agent_xyz789",
    server_url="https://n8n.example.com/mcp",
    server_type="SSE",
    name="N8N Automation",
    description="Workflow automation server"
)
```

### Configure Tool Approvals

```python
# Set fine-grained approval policy
await update_approval_policy(
    server_id="server_abc123",
    policy="fine_grained"
)

# Require approval for specific tool
await create_tool_approval(
    server_id="server_abc123",
    tool_name="execute_workflow",
    approval_mode="always"
)
```

### Manage Secrets

```python
# Create secret
await create_secret(
    name="OPENAI_API_KEY",
    value="sk-...",
    agent_id="agent_xyz789",
    description="OpenAI API key for external calls"
)

# Update secret value
await update_secret(
    secret_id="secret_abc123",
    value="new-secret-value"
)
```

## Approval Policies

### Always Ask
Every tool usage requires explicit user approval.

### Fine-Grained
Configure approval requirements per tool:
- `always`: Always require approval
- `never`: Never require approval
- `conditional`: Require approval based on conditions

### No Approval
Allow all tool usage without any approval requirements.

## Security Notes

- Secret values are never returned in API responses
- All secrets are encrypted at rest
- Use environment-specific secrets for different deployments
- Regularly rotate sensitive credentials

## Environment Variables

- `ELEVENLABS_API_KEY`: Your ElevenLabs API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `API_TIMEOUT`: API request timeout in seconds (default: 30)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
- `MAX_RETRIES`: Maximum retry attempts for API calls (default: 3)

## Error Handling

All tools return consistent error responses with helpful suggestions:

```json
{
  "success": false,
  "error": "Invalid server URL",
  "suggestion": "URL must start with http:// or https://"
}
```

## License

MIT