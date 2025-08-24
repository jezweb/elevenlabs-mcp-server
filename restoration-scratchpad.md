# ElevenLabs MCP Server Restoration Scratchpad

## Current Situation
- Archived 2 servers that actually have valid API implementations
- Lost ~20+ tools that map to real ElevenLabs API endpoints
- Need to restore and reorganize without losing improvements

## API Endpoints Confirmed by User
```
MCP Servers: POST Create, GET List, GET Get server, GET List tools
Tests: GET List, GET Get, POST Create, PUT Update, DEL Delete, POST Get summaries, POST Run tests
Test Invocations: GET Get, POST Resubmit
Conversations: GET List, GET Details, DEL Delete, GET Audio, GET Signed URL, GET Token, POST Feedback
Tools: GET List, GET Get, POST Create, PATCH Update, DEL Delete, GET Dependent agents
```

## Restoration Plan

### Phase 1: Analyze Overlapping Tools
Need to compare implementations between servers to keep best version

#### Conversation Tools Comparison
| Tool | elevenlabs-knowledge | elevenlabs-conversations | Action |
|------|---------------------|-------------------------|---------|
| list_conversations | YES (line unknown) | YES (line 77) | Compare & keep best |
| get_conversation | YES | YES (line 133) | Compare & keep best |
| get_transcript | YES | YES (line 162) | Compare & keep best |
| analyze_conversation | YES | YES (line 584) | Compare & keep best |
| performance_report | YES | YES (line 685) | Compare & keep best |
| export_conversations | YES | YES (line 841) | Compare & keep best |
| delete_conversation | NO | YES (line 191) | Keep in conversations |
| send_feedback | NO | YES (line 223) | Keep in conversations |
| get_conversation_audio | NO | YES (line 330) | Keep in conversations |
| get_signed_url | NO | YES (line 408) | Keep in conversations |
| get_conversation_token | NO | YES (line 512) | Keep in conversations |

### Phase 2: Server Organization

#### 1. elevenlabs-agents (KEEP AS IS)
- Agent CRUD operations ✓
- Voice configuration ✓
- System prompt management ✓
- Transfer configuration ✓
- NEW: Templates and helpers ✓

#### 2. elevenlabs-knowledge (MODIFY)
- Document management ✓
- RAG configuration ✓
- Knowledge base operations ✓
- REMOVE: Conversation tools that belong in conversations server

#### 3. elevenlabs-conversations (RESTORE)
- List conversations (check for improvements)
- Get conversation (check for improvements)
- Get transcript (check for improvements)
- Delete conversation ✓
- Send feedback ✓
- Get conversation audio ✓
- Get signed URL ✓
- Get conversation token ✓
- Analyze conversation (check for improvements)
- Performance report (check for improvements)
- Export conversations (check for improvements)

#### 4. elevenlabs-tools (RESTORE & RENAME from integrations)
- List tools ✓
- Get tool ✓
- Create tool ✓
- Update tool ✓
- Delete tool ✓
- Get tool dependent agents ✓
- Create MCP server ✓
- Get MCP server ✓
- List MCP server tools ✓
- Approval policies ✓
- Secrets management ✓

#### 5. elevenlabs-testing (VERIFY COMPLETENESS)
- Check if covers all Test API endpoints
- Add missing endpoints if any

### Phase 3: Implementation Steps

1. **Compare overlapping tools**
   - Check if knowledge server has improvements over conversations
   - Document any enhancements made

2. **Restore elevenlabs-conversations**
   - Move from archive/ back to root
   - Keep unique tools
   - Update overlapping tools if knowledge has better versions

3. **Restore elevenlabs-integrations as elevenlabs-tools**
   - Move from archive/ back to root
   - Rename directory to elevenlabs-tools
   - Update server name in code
   - Verify all tool management endpoints work

4. **Clean up elevenlabs-knowledge**
   - Remove conversation-specific tools
   - Keep only knowledge/RAG focused tools

5. **Update documentation**
   - README.md with 5 servers
   - ARCHITECTURE.md with new structure
   - Update CHANGELOG.md

## Tool Implementation Comparison

### Need to Check:
1. Do knowledge versions have better error handling?
2. Do knowledge versions have better response formatting?
3. Any parameter improvements?
4. Any bug fixes applied?

## Files to Modify

### Move Operations
```bash
mv archive/elevenlabs-conversations elevenlabs-conversations
mv archive/elevenlabs-integrations elevenlabs-tools
```

### Update Files
- elevenlabs-tools/src/server.py (rename server)
- elevenlabs-knowledge/src/server.py (remove duplicate tools)
- README.md (update server list)
- ARCHITECTURE.md (update architecture)
- CHANGELOG.md (document restoration)

## Context Preservation
- Restored 2 servers with ~20+ valid API tools
- Renamed integrations to tools for clarity
- Removed duplicates from knowledge server
- Kept best implementations of overlapping tools
- Total servers: 5 (agents, knowledge, conversations, tools, testing)