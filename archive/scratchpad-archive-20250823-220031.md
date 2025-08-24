# ElevenLabs MCP Server Development Scratchpad

## Project Overview
Building two FastMCP servers for ElevenLabs Conversational AI:
1. **elevenlabs-agents**: Agent management, configuration, multi-agent routing
2. **elevenlabs-knowledge**: Knowledge base, RAG, conversation management

## Key Decisions Made
- Monorepo structure for shared code and unified deployment
- Copy-based shared code (not symlinks) for FastMCP Cloud compatibility
- Module-level server objects (critical for cloud deployment)
- Simple, maintainable architecture over complex patterns
- Focus on HIGH priority endpoints first

## Current Status
- [ ] Repository structure created
- [ ] Shared utilities implemented
- [ ] Agents server basic structure
- [ ] Knowledge server basic structure
- [ ] Deployment configuration
- [ ] Documentation complete

## FastMCP Cloud Critical Requirements
1. Server object MUST be at module level (mcp, server, or app)
2. NO function wrappers around server creation
3. PyPI-only dependencies in requirements.txt
4. Embedded shared code (copied, not referenced)
5. Public GitHub repository or accessible to FastMCP

## API Key Notes
- Using ELEVENLABS_API_KEY environment variable
- Client initialization at module level after config validation
- Proper error handling for missing credentials

## Testing Checklist
- [ ] Module import test (server object accessible)
- [ ] Clean venv dependency test
- [ ] Environment variable validation
- [ ] Local server startup
- [ ] Tool registration verification
- [ ] API connection test

## Deployment URLs (Future)
- elevenlabs-agents: https://elevenlabs-agents-jezweb.fastmcp.app/mcp
- elevenlabs-knowledge: https://elevenlabs-knowledge-jezweb.fastmcp.app/mcp

## Git Commit Points
1. Initial structure and tracking files
2. Shared utilities module
3. Agents server implementation
4. Knowledge server implementation
5. Testing and deployment scripts
6. Documentation finalization

## Notes and Observations
- Keep tools focused and single-purpose
- Use async/await consistently for API calls
- Implement proper retry logic for resilience
- Cache responses where appropriate
- Start with minimal resource requirements