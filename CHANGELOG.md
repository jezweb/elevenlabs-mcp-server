# Changelog

All notable changes to the ElevenLabs MCP Servers project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Fixed `simulate_conversation` API payload structure using `simulation_specification` format
- Corrected all testing endpoint URLs by removing double `/v1/v1/` prefixes
- Fixed parameter type validation for decimal numbers (temperature, stability, similarity_boost)
- Updated `create_test` payload structure with correct API parameters
- Fixed `configure_rag` payload structure with official API parameters
- Improved `get_agent_link` error handling and validation
- Removed `list_mcp_servers` function due to non-existent endpoint
- Fixed `get_knowledge_base_size` to require agent_id parameter

### Changed
- Updated all API endpoint URLs to use correct base paths
- Changed numeric parameters to accept string inputs with float conversion
- Enhanced error messages for better debugging

### Production Validation
- ✅ All core features verified working in FastMCP Cloud deployment
- ✅ End-to-end testing completed successfully
- ✅ API connection and authentication validated
- ✅ Parameter handling for MCP string inputs confirmed

## [0.1.0] - 2025-01-24

### Added
- Initial project structure with monorepo architecture
- Three specialized MCP servers:
  - `elevenlabs-agents`: Agent management and configuration
  - `elevenlabs-knowledge`: Knowledge base and conversation management
  - `elevenlabs-testing`: Agent testing and simulation
- Comprehensive documentation (README, ARCHITECTURE, DEPLOYMENT, CLAUDE.md)
- Environment-based configuration
- FastMCP Cloud deployment compatibility
- Pre-deployment validation scripts

### Agents Server Features
- Agent CRUD operations (create, read, update, delete)
- System prompt management and updates
- LLM configuration (model, temperature, max_tokens)
- Voice and TTS settings (stability, similarity_boost, style)
- Multi-agent transfer configuration
- Agent-to-agent routing setup
- Conversation simulation and testing
- Configuration validation and error handling

### Knowledge Server Features
- Document management (URL upload, text documents)
- RAG configuration (chunk_size, chunk_overlap, top_k, similarity_threshold)
- Knowledge base index rebuilding
- Conversation retrieval and transcript access
- Performance analytics and reporting
- Data export (JSON, CSV formats)
- Real-time conversation monitoring

### Testing Server Features
- Agent conversation simulation
- Test case creation and management
- Performance validation tools
- Integration testing capabilities

### Infrastructure
- FastMCP Cloud deployment configuration
- Module-level server objects for cloud compatibility
- PyPI-only dependency management (fastmcp>=2.11.3)
- Async/await architecture throughout
- Comprehensive error handling and logging

### Security
- API key management via environment variables
- Input validation on all endpoints
- Error message sanitization
- No PII storage in local systems
- Secure credential handling

---

## Version Guidelines

- **Major version (1.0.0)**: Breaking API changes
- **Minor version (0.1.0)**: New features, backwards compatible
- **Patch version (0.0.1)**: Bug fixes, backwards compatible

## Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore
Scope: agents, knowledge, shared, deployment