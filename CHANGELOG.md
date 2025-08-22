# Changelog

All notable changes to the ElevenLabs MCP Servers project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with monorepo architecture
- Two specialized MCP servers:
  - `elevenlabs-agents`: Agent management and configuration
  - `elevenlabs-knowledge`: Knowledge base and conversation management
- Shared utilities module for common functionality
- Comprehensive documentation (README, ARCHITECTURE, DEPLOYMENT)
- Environment-based configuration
- Copy-based shared code distribution for FastMCP Cloud compatibility
- Pre-deployment validation scripts
- Git tracking and project management files

### Infrastructure
- FastMCP Cloud deployment configuration
- Module-level server objects for cloud compatibility
- PyPI-only dependency management
- Async/await architecture throughout

### Security
- API key management via environment variables
- Input validation on all endpoints
- Error message sanitization
- No PII storage

## [0.1.0] - 2025-01-22 (Planned)

### Agents Server Features
- Agent CRUD operations
- System prompt management
- LLM configuration (model, temperature, tokens)
- Voice and TTS settings
- Multi-agent transfer configuration
- Agent-to-agent routing
- Phone transfer setup
- Conversation simulation
- Configuration validation

### Knowledge Server Features
- Document upload (URL, file, text)
- Multi-format support (PDF, DOCX, TXT, HTML, EPUB)
- RAG configuration (chunking, indexing)
- Index rebuilding and optimization
- Conversation retrieval and analysis
- Transcript parsing
- Data export (CSV, JSON)
- Performance analytics
- Knowledge base usage tracking

### Developer Experience
- Local development setup
- Testing framework
- Deployment scripts
- Comprehensive documentation
- Error handling patterns
- Logging configuration

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