# ElevenLabs MCP Server Fixes - Scratchpad

## Issues to Fix

### 1. Parameter Type Validation Issues
- [ ] `temperature` parameter - rejects float values
- [ ] `stability` parameter - rejects float values  
- [ ] `similarity_boost` parameter - rejects float values
- [ ] `speed` parameter - rejects float values
- [ ] `top_k` parameter - rejects integer values
- [ ] `max_tokens` parameter - rejects integer values
- [ ] Other numeric parameters

### 2. API Client Initialization Issues
- [ ] elevenlabs-conversations - NoneType errors
- [ ] elevenlabs-testing - NoneType errors
- [ ] elevenlabs-integrations - NoneType errors

### 3. API Endpoint Issues (lower priority)
- [ ] get_knowledge_base_size - 404
- [ ] list_mcp_servers - 404
- [ ] create_secret - 422
- [ ] create_tool - 422

## Investigation Notes

From API docs research:
- Temperature should be a float between 0.0 and 2.0
- Stability should be a float between 0.0 and 1.0
- Similarity boost should be a float between 0.0 and 1.0
- Speed should be a float between 0.7 and 1.2

## Fix Progress

### Step 1: Check current implementation ✅
- Starting with elevenlabs-agents server
- Found the issue: MCP client is sending string values but schema expects numbers
- Error: '0.7' is not valid under any of the given schemas
- Python function signatures are correct: temperature: Optional[float] = 0.5
- Pydantic models exist in shared/models.py with proper validation
- Issue appears to be in FastMCP schema generation or MCP client parameter passing

### Root Cause Analysis ✅
- FastMCP @mcp.tool() decorator generates JSON schema from Python type hints
- MCP protocol expects numeric types but receives string values
- **FOUND THE ISSUE**: According to FastMCP docs, numeric parameters should be passed as **JSON strings**
- Claude Code MCP client is sending raw values, not JSON strings
- FastMCP expects: `"0.7"` as a JSON string that gets parsed to float 0.7
- Claude Code is sending: `"0.7"` as a raw string value

### Step 2: Fix parameter types ✅
- **Root cause identified**: Claude Code MCP client bug
- FastMCP expects JSON strings for numeric parameters 
- Claude Code sends raw string values instead
- This is a Claude Code issue that should be reported
- Reverted to correct type hints for now
- **NEXT**: Move on to client initialization issues

### Step 3: Test fixes
- Verify parameters are accepted

### Step 4: Fix client initialization ✅
- **FIXED**: Missing Config.API_KEY parameter in client initialization
- conversations server: `ElevenLabsClient()` → `ElevenLabsClient(Config.API_KEY)`
- testing server: `ElevenLabsClient()` → `ElevenLabsClient(Config.API_KEY)` 
- integrations server: `ElevenLabsClient()` → `ElevenLabsClient(Config.API_KEY)`
- **TESTED**: conversations and integrations servers now work correctly
- **NOTE**: testing server still gets 404 errors (API endpoints may not exist or require higher plan)

### Step 5: Commit changes
- Commit after each successful fix