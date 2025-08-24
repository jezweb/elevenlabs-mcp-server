# ElevenLabs MCP Servers

Production-ready MCP (Model Context Protocol) servers for comprehensive ElevenLabs Conversational AI management. Deploy to FastMCP Cloud for instant access to advanced agent creation, knowledge base management, and conversation analytics.

[![FastMCP Ready](https://img.shields.io/badge/FastMCP-Ready-green)](https://fastmcp.com)
[![ElevenLabs Compatible](https://img.shields.io/badge/ElevenLabs-API%20v1-blue)](https://elevenlabs.io)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

🎯 **Perfect for**: AI developers, conversational AI teams, customer support automation

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jezweb/elevenlabs-mcp-server.git
cd elevenlabs-mcp-server
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your ELEVENLABS_API_KEY
```

3. Install dependencies:
```bash
# For agents server
cd elevenlabs-agents
pip install -r requirements.txt

# For knowledge server
cd elevenlabs-knowledge
pip install -r requirements.txt
```

### Local Development

Run servers locally for testing:

```bash
# Run agents server
cd elevenlabs-agents
python src/server.py

# Run knowledge server (in another terminal)
cd elevenlabs-knowledge
python src/server.py
```

## 📦 Servers

### 1. ElevenLabs Agents Server
*Complete agent lifecycle management*

**Core Capabilities:**
- ✅ **Agent Creation**: Custom prompts, voice settings, LLM configuration
- ✅ **Voice Customization**: Stability, similarity boost, speed controls  
- ✅ **Multi-Agent Orchestration**: Transfer flows and handoff logic
- ✅ **Testing & Simulation**: Conversation testing and validation
- ✅ **Real-time Management**: Update agents without downtime

**Key Tools:**
- `create_agent` - Create conversational agents with custom parameters
- `configure_voice` - Fine-tune voice characteristics and TTS settings
- `simulate_conversation` - Test agent responses in real-time
- `add_transfer_to_agent` - Build complex multi-agent workflows
- `get_agent_link` - Generate shareable agent interfaces

**Status**: ✅ Production Ready - All major features fully tested and working

### 2. ElevenLabs Knowledge Server  
*Advanced knowledge management and RAG configuration*

**Core Capabilities:**
- ✅ **Document Management**: Upload PDFs, web pages, text files
- ✅ **RAG Configuration**: Optimize retrieval for better responses
- ✅ **Knowledge Base Statistics**: Monitor document usage and size
- ✅ **Index Management**: Rebuild search indexes for performance
- ✅ **Multi-Agent Support**: Share knowledge across agents

**Key Tools:**
- `add_document_url` - Import web content to knowledge base
- `add_document_text` - Add text documents directly
- `configure_rag` - Optimize document retrieval settings
- `rebuild_index` - Refresh search indexes
- `get_knowledge_base_size` - Monitor storage usage

**Status**: ✅ Production Ready - Core functionality verified and stable

### 3. ElevenLabs Conversations Server
*Conversation management and analytics*

**Core Capabilities:**
- ✅ **Conversation Access**: List, retrieve, and delete conversations
- ✅ **Transcript Management**: Export and analyze conversation text
- ✅ **Audio Retrieval**: Access conversation recordings
- ✅ **Performance Analytics**: Deep conversation insights
- ✅ **Feedback Collection**: User satisfaction tracking

**Key Tools:**
- `list_conversations` - Browse conversation history
- `get_conversation_audio` - Download conversation recordings
- `analyze_conversation` - Extract insights from conversation logs
- `performance_report` - Generate detailed analytics reports
- `export_conversations` - Bulk data export for analysis

**Status**: ✅ Production Ready - Full conversation API coverage

### 4. ElevenLabs Tools Server
*MCP server and tool management*

**Core Capabilities:**
- ✅ **Tool Management**: Create, update, and delete tools
- ✅ **MCP Server Control**: Deploy and manage MCP servers
- ✅ **Approval Policies**: Configure tool approval workflows
- ✅ **Secrets Management**: Secure credential storage
- ✅ **Dependency Tracking**: Monitor tool usage by agents

**Key Tools:**
- `list_tools` - Browse available tools and integrations
- `create_mcp_server` - Deploy new MCP servers
- `configure_approval_policy` - Set up tool approval rules
- `manage_secrets` - Handle secure credentials
- `get_tool_dependent_agents` - Track tool usage

**Status**: ✅ Production Ready - Complete tools API implementation

### 5. ElevenLabs Testing Server
*Agent testing and simulation framework*

**Core Capabilities:**
- ✅ **Test Management**: Create and run test suites
- ✅ **Test Invocations**: Execute and monitor test runs
- ✅ **Batch Testing**: Run multiple tests simultaneously
- ✅ **Result Analysis**: Detailed test performance metrics
- ✅ **Continuous Testing**: Automated test scheduling

**Key Tools:**
- `create_test` - Design test scenarios
- `run_test` - Execute single test cases
- `batch_test` - Run multiple tests in parallel
- `get_test_results` - Retrieve detailed test outcomes
- `get_test_summaries` - Generate test reports

**Status**: ✅ Production Ready - Complete testing API coverage

## 🏗️ Architecture

This project contains five standalone MCP servers:

```
elevenlabs-mcp-server/
├── elevenlabs-agents/        # Agent management server
├── elevenlabs-knowledge/     # Knowledge base server
├── elevenlabs-conversations/ # Conversation analytics server
├── elevenlabs-tools/         # MCP tools and integrations server
└── elevenlabs-testing/       # Testing and simulation server
```

Each server is completely independent and deployable to FastMCP Cloud.

[Architecture details →](./ARCHITECTURE.md)

## 🚢 Deployment

### FastMCP Cloud

Both servers are designed for deployment to FastMCP Cloud:

1. Push to GitHub
2. Configure in FastMCP Cloud dashboard:
   - Repository: `your-username/elevenlabs-mcp-server`
   - Entrypoint: `elevenlabs-agents/src/server.py` or `elevenlabs-knowledge/src/server.py`
   - Environment variables: `ELEVENLABS_API_KEY`

[Deployment guide →](./DEPLOYMENT.md)

## 🔧 Configuration

### Environment Variables

```env
# Required
ELEVENLABS_API_KEY=your-api-key-here

# Optional
LOG_LEVEL=INFO
API_TIMEOUT=30
CACHE_TTL=300
MAX_RETRIES=3
```

### Client Configuration

Configure your MCP client (e.g., Claude Desktop) to connect:

```json
{
  "mcpServers": {
    "elevenlabs-agents": {
      "url": "https://elevenlabs-agents-username.fastmcp.app/mcp"
    },
    "elevenlabs-knowledge": {
      "url": "https://elevenlabs-knowledge-username.fastmcp.app/mcp"
    }
  }
}
```

## 📚 Documentation

- [Architecture](./ARCHITECTURE.md) - System design and components
- [Deployment](./DEPLOYMENT.md) - FastMCP Cloud deployment guide
- [Development](./CLAUDE.md) - Development guidelines
- [Changelog](./CHANGELOG.md) - Version history

## 🧪 Testing & Validation

### End-to-End Testing Status

**✅ Core Features Verified:**
- Agent creation with custom temperature settings
- Voice configuration with decimal parameters (stability, similarity_boost, speed)
- Conversation simulation and testing
- Knowledge base document management
- Real-time conversation analytics

### Test Commands

```bash
# Test all servers
./scripts/test-all.sh

# Test individual server
cd elevenlabs-agents
python src/server.py --test

# Validate API connections
cd elevenlabs-knowledge  
python -c "from src.server import mcp; print('✅ Server ready')"
```

### Production Readiness Checklist

- ✅ All critical API endpoints working
- ✅ Parameter validation handles MCP string inputs
- ✅ Error handling and retry logic implemented  
- ✅ FastMCP Cloud deployment compatibility
- ✅ Comprehensive logging and monitoring
- ✅ Environment variable configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](./LICENSE) file

## 🔗 Resources

- [ElevenLabs API Documentation](https://elevenlabs.io/docs/api-reference)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io)

## 💬 Support

For issues and questions:
- GitHub Issues: [elevenlabs-mcp-server/issues](https://github.com/jezweb/elevenlabs-mcp-server/issues)
- ElevenLabs Discord: [discord.gg/elevenlabs](https://discord.gg/elevenlabs)

---

Built with ❤️ using [FastMCP](https://github.com/jlowin/fastmcp)