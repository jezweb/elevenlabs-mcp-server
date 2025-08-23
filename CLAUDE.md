# Development Guidelines

## Project Overview

This is a monorepo containing two FastMCP servers for ElevenLabs Conversational AI:
1. **elevenlabs-agents**: Agent management and configuration
2. **elevenlabs-knowledge**: Knowledge base and conversation management

## Critical Requirements for FastMCP Cloud

### ⚠️ MUST FOLLOW

1. **Server Object at Module Level**
   ```python
   # ✅ CORRECT
   from fastmcp import FastMCP
   mcp = FastMCP(name="server-name")  # MUST be at module level
   
   # ❌ WRONG - Will fail in cloud
   def create_server():
       return FastMCP(name="server-name")
   ```

2. **PyPI Dependencies Only**
   ```txt
   # ✅ CORRECT requirements.txt
   fastmcp>=0.3.0
   elevenlabs>=1.0.0
   
   # ❌ WRONG - Will fail
   -e ../shared
   git+https://github.com/...
   ```

3. **Self-Contained Servers**
   - Each server is completely independent
   - All utilities are embedded in each server
   - No cross-server dependencies

## Development Workflow

### Setting Up

1. **Install dependencies**:
   ```bash
   cd elevenlabs-agents
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   cp .env.example .env
   # Add your ELEVENLABS_API_KEY
   ```

### Making Changes

1. **Edit server code**: Make changes directly in the server directory
2. **Test locally**: `python src/server.py`
3. **Verify**: Ensure server runs without errors

### Adding New Tools

1. Create tool in appropriate module:
   ```python
   # elevenlabs-agents/src/tools/new_tool.py
   async def my_new_tool(param: str) -> dict:
       """Tool description."""
       # Implementation
       return {"result": "success"}
   ```

2. Register in server.py:
   ```python
   from tools.new_tool import my_new_tool
   
   @mcp.tool()
   async def wrapped_tool(param: str) -> dict:
       return await my_new_tool(param)
   ```

## Code Style Guidelines

### Python Standards
- Use type hints for all functions
- Comprehensive docstrings (Google style)
- Async/await for all I/O operations
- Handle errors gracefully
- Log important operations

### Simplicity Principles
- Single-purpose tools
- Clear, descriptive names
- Minimal abstraction
- Direct API integration
- Straightforward error messages

### Example Tool Pattern
```python
@mcp.tool()
async def get_agent(agent_id: str) -> dict:
    """
    Retrieve agent details from ElevenLabs.
    
    Args:
        agent_id: The unique identifier of the agent
        
    Returns:
        Agent configuration and metadata
        
    Raises:
        ValueError: If agent_id is invalid
        APIError: If ElevenLabs API fails
    """
    if not agent_id:
        raise ValueError("agent_id is required")
    
    try:
        response = await client.get_agent(agent_id)
        return {
            "success": True,
            "agent": response.data
        }
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

## Testing Guidelines

### Pre-Deployment Checklist
- [ ] Server object at module level
- [ ] All imports work
- [ ] requirements.txt has only PyPI packages
- [ ] Environment variables documented
- [ ] Server runs locally
- [ ] Tools are registered
- [ ] No syntax errors
- [ ] API connection works

### Testing Commands
```bash
# Test import
python -c "from elevenlabs_agents.src.server import mcp; print('✅ Import works')"

# Test server startup
cd elevenlabs-agents
python src/server.py --test

# Run all tests
./scripts/test-all.sh
```

## Git Workflow

### Commit Guidelines
- Make atomic commits
- Use conventional commit format
- Commit at logical checkpoints
- Include relevant files only

### Commit Message Format
```
type(scope): description

feat(agents): add agent duplication tool
fix(knowledge): correct document parsing error
docs(readme): update deployment instructions
refactor(shared): simplify client initialization
```

### When to Commit
1. After completing a feature
2. Before major refactoring
3. After fixing a bug
4. When documentation is updated
5. Before deployment

## Environment Variables

### Required
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key

### Optional
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `API_TIMEOUT`: API request timeout in seconds (default: 30)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
- `MAX_RETRIES`: Maximum API retry attempts (default: 3)

## Troubleshooting

### Common Issues

1. **"No server object found"**
   - Ensure `mcp` is at module level in server.py
   - Check variable name is `mcp`, `server`, or `app`

2. **"Module not found"**
   - Check import paths
   - Verify all required files exist

3. **"API connection failed"**
   - Verify ELEVENLABS_API_KEY is set
   - Check network connectivity
   - Validate API key permissions

4. **"Failed to install dependencies"**
   - Remove any `-e` entries from requirements.txt
   - Ensure all packages are on PyPI

## Performance Optimization

### Best Practices
- Cache API responses (5-minute TTL)
- Use connection pooling
- Implement retry logic with backoff
- Minimize memory usage
- Lazy load resources

### Resource Guidelines
- Start with 1 vCPU / 2GB RAM
- Scale up only if needed
- Monitor response times
- Keep startup under 5 seconds

## Security Notes

### API Key Handling
- Never log API keys
- Validate on startup
- Use environment variables only
- Don't commit .env files

### Data Protection
- No PII storage
- Sanitize error messages
- Validate all inputs
- Use HTTPS only

## Maintenance

### Regular Tasks
- Update dependencies monthly
- Review error logs
- Monitor performance metrics
- Update documentation
- Clean up unused code

### Version Updates
- Test thoroughly before deploying
- Update CHANGELOG.md
- Tag releases in git
- Document breaking changes

## Contact

For questions about this codebase:
- Create an issue in the repository
- Check existing documentation
- Review ElevenLabs API docs
- Consult FastMCP documentation