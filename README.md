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
*Advanced knowledge management and analytics*

**Core Capabilities:**
- ✅ **Document Management**: Upload PDFs, web pages, text files
- ✅ **RAG Configuration**: Optimize retrieval for better responses
- ✅ **Conversation Analytics**: Performance insights and metrics
- ✅ **Data Export**: Conversation transcripts and usage reports
- ✅ **Real-time Monitoring**: Track agent performance over time

**Key Tools:**
- `add_document_url` - Import web content to knowledge base
- `configure_rag` - Optimize document retrieval settings
- `analyze_conversation` - Extract insights from conversation logs
- `performance_report` - Generate detailed analytics reports
- `export_conversations` - Bulk data export for analysis

**Status**: ✅ Production Ready - Core functionality verified and stable

## 🏗️ Architecture

This project contains two standalone MCP servers:

```
elevenlabs-mcp-server/
├── elevenlabs-agents/      # Agent management server
└── elevenlabs-knowledge/   # Knowledge base server
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