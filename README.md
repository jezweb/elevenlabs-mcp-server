# ElevenLabs MCP Servers

Two specialized MCP (Model Context Protocol) servers for managing ElevenLabs Conversational AI agents and knowledge bases.

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

Manages conversational AI agents, their configuration, and multi-agent orchestration.

**Key Features:**
- Create and manage AI agents with custom prompts
- Configure LLM settings (model, temperature, tokens)
- Set up voice and TTS parameters
- Design multi-agent transfer flows
- Test agent responses with simulation

**Example Tools:**
- `create_agent` - Create a new conversational agent
- `update_system_prompt` - Modify agent's behavior
- `add_transfer_to_agent` - Configure agent handoffs
- `simulate_conversation` - Test agent responses

[Full documentation →](./elevenlabs-agents/README.md)

### 2. ElevenLabs Knowledge Server

Handles knowledge base operations, RAG configuration, and conversation analytics.

**Key Features:**
- Upload documents (PDF, DOCX, TXT, HTML)
- Configure RAG settings for optimal retrieval
- Analyze conversation transcripts
- Export conversation data
- Generate performance reports

**Example Tools:**
- `add_document_url` - Add web content to knowledge base
- `configure_rag` - Optimize retrieval settings
- `analyze_conversation` - Extract insights from calls
- `performance_report` - Generate analytics

[Full documentation →](./elevenlabs-knowledge/README.md)

## 🏗️ Architecture

This project uses a monorepo structure with shared utilities:

```
elevenlabs-mcp-server/
├── shared/                 # Shared utilities (development)
├── elevenlabs-agents/      # Agent management server
└── elevenlabs-knowledge/   # Knowledge base server
```

Each server is independently deployable to FastMCP Cloud.

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

## 🧪 Testing

Run tests for both servers:

```bash
# Test all servers
./scripts/test-all.sh

# Test individual server
cd elevenlabs-agents
pytest tests/
```

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