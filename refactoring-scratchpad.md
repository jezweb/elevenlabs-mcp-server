# MCP Server Refactoring Scratchpad

## Objective
Refactor all 5 ElevenLabs MCP servers from monolithic server.py files (800-1400+ lines) to FastMCP structured template pattern with separate tool files.

## Current State
- elevenlabs-agents: 1,425 lines
- elevenlabs-conversations: 1,085 lines  
- elevenlabs-tools: 945 lines
- elevenlabs-testing: 897 lines
- elevenlabs-knowledge: 839 lines

## Target Structure (per server)
```
server-name/
├── src/
│   ├── server.py (100-125 lines - just registration)
│   └── tools/
│       ├── __init__.py
│       ├── group1.py
│       ├── group2.py
│       └── group3.py
```

## Refactoring Order & Groupings

### 1. elevenlabs-agents (First - Template Example)
**Tool Groups:**
- `agents.py`: create_agent, list_agents, get_agent, update_agent, delete_agent, update_system_prompt
- `voice.py`: configure_voice, set_llm_config  
- `transfers.py`: add_transfer_to_agent, configure_webhook
- `templates.py`: get_agent_template, list_agent_templates
- `testing.py`: simulate_conversation, create_test, get_test_results
- `widgets.py`: get_widget_link, get_agent_link

### 2. elevenlabs-conversations
**Tool Groups:**
- `conversations.py`: list_conversations, get_conversation, get_transcript, delete_conversation
- `feedback.py`: add_feedback, get_feedback_summary
- `playback.py`: get_audio_url, get_video_url
- `analytics.py`: analyze_conversation, get_conversation_metrics, performance_report

### 3. elevenlabs-knowledge
**Tool Groups:**
- `documents.py`: add_document_url, add_document_text, list_documents, delete_document
- `rag.py`: configure_rag, rebuild_index
- `search.py`: search_knowledge_base
- `analytics.py`: get_knowledge_stats, list_conversations, get_conversation, get_transcript, analyze_conversation, performance_report, export_conversations

### 4. elevenlabs-testing
**Tool Groups:**
- `tests.py`: create_test, list_tests, get_test, delete_test
- `execution.py`: run_test, run_test_suite
- `results.py`: get_test_results, get_test_summary
- `simulation.py`: simulate_conversation, simulate_transfer

### 5. elevenlabs-tools  
**Tool Groups:**
- `servers.py`: list_mcp_servers, get_server_info, test_server_connection
- `tools.py`: list_server_tools, get_tool_info, search_tools
- `resources.py`: list_server_resources, get_resource_content
- `diagnostics.py`: health_check, validate_config, diagnostic_report

## Implementation Steps

### Phase 1: Create Template with elevenlabs-agents
1. Create tools/ directory structure
2. Move tools to appropriate files
3. Update server.py to import and register
4. Test locally
5. Document pattern

### Phase 2: Apply to Remaining Servers
1. elevenlabs-conversations
2. elevenlabs-knowledge  
3. elevenlabs-testing
4. elevenlabs-tools

### Phase 3: Validation
1. Test each server locally
2. Verify all tools still work
3. Update documentation
4. Commit changes

## Key Considerations
- Maintain module-level mcp object for FastMCP Cloud
- Keep tool signatures identical
- Preserve all docstrings
- No changes to functionality
- Each tool file should be self-contained

## Progress Tracking
- [x] elevenlabs-agents refactored (1,425 → 358 lines)
- [ ] elevenlabs-conversations refactored
- [ ] elevenlabs-knowledge refactored
- [ ] elevenlabs-testing refactored
- [ ] elevenlabs-tools refactored
- [ ] All servers tested
- [ ] Documentation updated
- [ ] Changes committed

## Refactoring Results

### elevenlabs-agents ✅
- **Before**: 1,425 lines in single server.py
- **After**: 358 lines in server.py + 7 tool files
- **Structure**:
  - server.py: 358 lines (registration & lifecycle)
  - agents.py: 413 lines (7 tools)
  - voice.py: 320 lines (5 tools)
  - transfers.py: 100 lines (2 tools)
  - templates.py: 284 lines (8 tools)
  - testing.py: 148 lines (3 tools)
  - widgets.py: 233 lines (5 tools)
  - __init__.py: 89 lines (exports)
- **Total tools**: 30 tools properly organized
- **Test status**: ✅ Imports working, server starts

## Notes
- Start with elevenlabs-agents as template
- Each server takes ~15-20 minutes to refactor
- Test after each server to catch issues early