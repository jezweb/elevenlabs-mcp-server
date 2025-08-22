# ElevenLabs Agents MCP Server Reference

## Purpose
A specialized MCP server focused on creating, configuring, and managing ElevenLabs Conversational AI agents with emphasis on system prompts, multi-agent architectures, and transfer logic.

## API Endpoints Coverage

### Agent Management Endpoints (10 endpoints)

| Endpoint | Method | Path | Description | Priority |
|----------|--------|------|-------------|----------|
| Create Agent | POST | `/v1/convai/agents` | Create new agent with full configuration | **High** |
| Get Agent | GET | `/v1/convai/agents/{agent_id}` | Retrieve agent details | **High** |
| List Agents | GET | `/v1/convai/agents` | List all agents in workspace | **High** |
| Update Agent | PATCH | `/v1/convai/agents/{agent_id}` | Modify agent configuration | **High** |
| Delete Agent | DELETE | `/v1/convai/agents/{agent_id}` | Remove agent | **Medium** |
| Duplicate Agent | POST | `/v1/convai/agents/{agent_id}/duplicate` | Clone existing agent | **Medium** |
| Get Agent Link | GET | `/v1/convai/agents/{agent_id}/link` | Get embeddable widget link | **Low** |
| Simulate Conversation | POST | `/v1/convai/agents/{agent_id}/simulate` | Test agent responses | **High** |
| Stream Simulate | POST | `/v1/convai/agents/{agent_id}/simulate/stream` | Real-time simulation | **Medium** |
| Calculate LLM Usage | POST | `/v1/convai/agents/{agent_id}/calculate-usage` | Estimate costs | **Low** |

### Tools Management Endpoints (6 endpoints)

| Endpoint | Method | Path | Description | Priority |
|----------|--------|------|-------------|----------|
| List Tools | GET | `/v1/convai/tools` | Get available tools | **High** |
| Get Tool | GET | `/v1/convai/tools/{tool_id}` | Tool details | **Medium** |
| Create Tool | POST | `/v1/convai/tools` | Add custom tool | **High** |
| Update Tool | PATCH | `/v1/convai/tools/{tool_id}` | Modify tool config | **Medium** |
| Delete Tool | DELETE | `/v1/convai/tools/{tool_id}` | Remove tool | **Low** |
| Get Dependent Agents | GET | `/v1/convai/tools/{tool_id}/agents` | Find tool usage | **Low** |

## Agent Configuration Parameters

### Core Identity Parameters

```python
class AgentIdentity:
    name: str                    # Agent display name (required)
    agent_id: str               # Auto-generated unique ID
    description: str            # Agent purpose/role description
    avatar_url: str            # Optional avatar image
```

### System Prompt Configuration

```python
class SystemPromptConfig:
    system_prompt: str          # Main system instructions (required)
    first_message: str         # Initial greeting (required)
    language: str = "en"       # ISO 639-1 language code
    
    # Prompt Structure (Best Practice)
    # 1. PERSONA - Identity and role
    # 2. GOAL - Primary objectives
    # 3. ENVIRONMENT - Interaction context  
    # 4. TONE - Communication style
    # 5. PERSONALITY - Character traits
    # 6. ADAPTABILITY - Dynamic responses
```

### LLM Configuration

```python
class LLMConfig:
    llm: str = "gemini-2.0-flash-001"  # Model selection
    temperature: float = 0.5            # 0.0-1.0 (creativity)
    max_tokens: int | None = None       # Response length limit
    
    # Model Selection Guidelines:
    # - gemini-2.5-flash-lite: Simple routing (temp: 0.2-0.3)
    # - gemini-2.5-flash: Complex reasoning (temp: 0.4-0.5)
    # - gpt-4o: Advanced capabilities (temp: 0.3-0.6)
    # - claude-3.5-sonnet: Nuanced conversation (temp: 0.4-0.7)
```

### Voice Configuration

```python
class VoiceConfig:
    voice_id: str = "cgSgspJ2msm6clMCkdW9"  # ElevenLabs voice ID
    model_id: str = "eleven_turbo_v2"       # TTS model
    stability: float = 0.5                  # Voice consistency (0-1)
    similarity_boost: float = 0.8           # Voice matching (0-1)
    style: float = 0.0                      # Style exaggeration (0-1)
    use_speaker_boost: bool = True          # Enhanced similarity
    optimize_streaming_latency: int = 3     # 0-4 (lower=faster)
    output_format: str = "pcm_16000"        # Audio format
```

### Audio Processing Configuration

```python
class AudioConfig:
    asr_quality: str = "high"              # Speech recognition quality
    asr_provider: str = "elevenlabs"       # ASR provider
    enable_ssml: bool = False               # SSML tag support
    noise_suppression: bool = True         # Background noise filter
    echo_cancellation: bool = True         # Echo removal
```

### Conversation Flow Configuration

```python
class ConversationConfig:
    turn_timeout: int = 7                  # Seconds to wait for response
    max_duration_seconds: int = 300        # Call time limit
    silence_timeout_seconds: int = 30      # End on silence
    interruption_threshold: float = 0.5    # Sensitivity to interruption
    backchannel_frequency: float = 0.0     # "uh-huh" frequency
    boosted_keywords: List[str] = []       # Enhanced recognition words
```

### Platform Settings

```python
class PlatformSettings:
    record_voice: bool = True              # Store audio recordings
    retention_days: int = 730              # Data retention period
    enable_transcription: bool = True      # Generate transcripts
    enable_analytics: bool = True          # Track metrics
    privacy_mode: bool = False             # Enhanced privacy
```

## Tool Configuration

### Transfer to Agent Tool

```python
class TransferToAgentTool:
    type: str = "transfer_to_agent"
    config: {
        "agent_id": str,                   # Target agent ID
        "transfer_conditions": str,        # Natural language rules
        "transfer_message": str,            # Handoff message
        "enable_first_message": bool,      # Auto-greet on transfer
        "pass_context": bool,              # Share conversation history
    }
```

### Transfer to Number Tool

```python
class TransferToNumberTool:
    type: str = "transfer_to_number"
    config: {
        "phone_number": str,               # E.164 format
        "transfer_conditions": str,        # When to transfer
        "transfer_message": str,            # Announcement
        "emergency_priority": bool,        # Priority routing
    }
```

### End Call Tool

```python
class EndCallTool:
    type: str = "end_call"
    config: {
        "conditions": str,                 # When to end
        "farewell_message": str,           # Closing message
        "collect_feedback": bool,          # Request rating
    }
```

## Multi-Agent Architecture Patterns

### 1. Hub and Spoke Pattern

```python
# Main Router Agent
main_router = {
    "name": "Main Receptionist",
    "system_prompt": """
    You are the main receptionist. Your ONLY job is to:
    1. Greet callers warmly
    2. Understand their need
    3. Route to the appropriate specialist
    
    Available specialists:
    - Sales: Product inquiries, pricing
    - Support: Technical issues, troubleshooting  
    - Booking: Appointments, scheduling
    """,
    "temperature": 0.2,  # Low for consistent routing
    "tools": [
        {
            "type": "transfer_to_agent",
            "agent_id": "sales_agent_id",
            "conditions": "pricing, products, purchase, buy"
        },
        {
            "type": "transfer_to_agent", 
            "agent_id": "support_agent_id",
            "conditions": "problem, issue, broken, help"
        }
    ]
}
```

### 2. Sequential Processing Pattern

```python
# Qualification -> Collection -> Confirmation flow
qualifier_agent = {
    "name": "Qualifier",
    "goal": "Determine eligibility",
    "transfer_on_success": "collector_agent_id"
}

collector_agent = {
    "name": "Data Collector",
    "goal": "Gather required information",
    "transfer_on_complete": "confirmer_agent_id"
}

confirmer_agent = {
    "name": "Confirmation Specialist",
    "goal": "Verify and confirm details",
    "transfer_on_complete": "end_call"
}
```

### 3. Fallback Escalation Pattern

```python
# Progressive escalation for complex queries
level1_agent = {
    "name": "Tier 1 Support",
    "knowledge_base": ["basic_faqs.txt"],
    "escalation_threshold": "unable to resolve",
    "transfer_to": "level2_agent_id"
}

level2_agent = {
    "name": "Tier 2 Specialist",
    "knowledge_base": ["advanced_docs.pdf"],
    "human_escalation": "+61234567890"
}
```

## Implementation Examples

### Complete Agent Creation

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="your_api_key")

def create_sales_agent():
    """Create a well-configured sales agent"""
    
    conversation_config = {
        "agent": {
            "prompt": {
                "prompt": """
                ## PERSONA
                You are Sarah, a friendly sales specialist at TechCorp.
                
                ## GOAL
                PRIMARY: Help customers find the right product
                SECONDARY: Provide pricing information
                TERTIARY: Schedule demos when appropriate
                
                ## ENVIRONMENT
                This is a phone conversation. Background noise may occur.
                
                ## TONE
                Professional yet conversational. Use Australian English.
                Keep responses concise (2-3 sentences max).
                
                ## PERSONALITY
                - Enthusiastic about technology
                - Patient with questions
                - Solution-focused
                
                ## ADAPTABILITY
                - If customer seems confused, slow down
                - If pressed for time, be more direct
                - Match customer's energy level
                """,
                "first_message": "G'day! This is Sarah from TechCorp. How can I help you today?",
                "language": "en"
            }
        },
        "tts": {
            "voice_id": "sarah_voice_id",
            "model_id": "eleven_turbo_v2_5",
            "stability": 0.6,
            "similarity_boost": 0.75,
            "style": 0.2,
            "optimize_streaming_latency": 2
        },
        "llm": {
            "model": "gemini-2.5-flash",
            "temperature": 0.45,
            "max_tokens": 150
        },
        "asr": {
            "quality": "high",
            "provider": "elevenlabs"
        },
        "turn": {
            "mode": "server_vad",
            "turn_timeout": 5000,
            "server_vad": {
                "speech_threshold": 0.5,
                "silence_duration_ms": 700
            }
        }
    }
    
    platform_settings = {
        "record": True,
        "retention": {
            "days": 365,
            "delete_pii": True
        },
        "max_duration": 600
    }
    
    # Add tools
    tools = [
        {
            "type": "transfer_to_agent",
            "config": {
                "agent_id": "technical_specialist_id",
                "conditions": "technical details, specifications, integration",
                "message": "I'll connect you with our technical specialist."
            }
        },
        {
            "type": "end_call",
            "config": {
                "conditions": "goodbye, bye, thanks, that's all",
                "message": "Thanks for calling TechCorp. Have a great day!"
            }
        }
    ]
    
    response = client.conversational_ai.agents.create(
        name="Sarah - Sales Agent",
        conversation_config=conversation_config,
        platform_settings=platform_settings,
        tools=tools
    )
    
    return response.agent_id
```

### Agent Update Example

```python
def update_agent_temperature(agent_id: str, new_temperature: float):
    """Adjust agent's response creativity"""
    
    # Get current config
    agent = client.conversational_ai.agents.get(agent_id)
    
    # Update temperature
    agent.conversation_config.llm.temperature = new_temperature
    
    # Apply update
    client.conversational_ai.agents.update(
        agent_id=agent_id,
        conversation_config=agent.conversation_config
    )
```

### Multi-Agent Transfer Setup

```python
def setup_agent_network():
    """Create interconnected agent system"""
    
    agents = {}
    
    # Create main router
    agents['router'] = create_agent(
        name="Main Router",
        prompt="Route to: Sales, Support, or Emergency",
        temperature=0.2
    )
    
    # Create specialists
    agents['sales'] = create_agent(
        name="Sales Specialist",
        prompt="Handle product inquiries",
        temperature=0.5
    )
    
    agents['support'] = create_agent(
        name="Support Agent", 
        prompt="Resolve technical issues",
        temperature=0.4
    )
    
    # Configure transfers
    add_transfer_tool(
        from_agent=agents['router'],
        to_agent=agents['sales'],
        conditions="buy, purchase, pricing, products"
    )
    
    add_transfer_tool(
        from_agent=agents['router'],
        to_agent=agents['support'],
        conditions="problem, broken, not working, help"
    )
    
    return agents
```

## Testing Strategies

### 1. Conversation Simulation

```python
def test_agent_routing(agent_id: str):
    """Test agent's routing logic"""
    
    test_cases = [
        ("I want to buy a product", "sales"),
        ("My device is broken", "support"),
        ("What are your prices?", "sales"),
        ("I need technical help", "support")
    ]
    
    for user_input, expected_route in test_cases:
        response = client.conversational_ai.agents.simulate(
            agent_id=agent_id,
            text=user_input
        )
        
        # Check if correct transfer was triggered
        assert expected_route in response.agent_response
```

### 2. Load Testing

```python
def stress_test_agent(agent_id: str, concurrent_calls: int = 10):
    """Test agent under load"""
    
    import asyncio
    
    async def simulate_call():
        return await client.conversational_ai.agents.simulate_async(
            agent_id=agent_id,
            text="Hello, I need help"
        )
    
    tasks = [simulate_call() for _ in range(concurrent_calls)]
    results = asyncio.run(asyncio.gather(*tasks))
    
    # Analyze response times and success rates
    return analyze_results(results)
```

## Error Handling Patterns

### Graceful Degradation

```python
def create_agent_with_fallback(config: dict):
    """Create agent with error handling"""
    
    try:
        # Try primary configuration
        return client.conversational_ai.agents.create(**config)
    except VoiceNotFoundError:
        # Fallback to default voice
        config['conversation_config']['tts']['voice_id'] = DEFAULT_VOICE
        return client.conversational_ai.agents.create(**config)
    except ModelNotAvailableError:
        # Fallback to simpler model
        config['conversation_config']['llm']['model'] = 'gemini-flash-lite'
        config['conversation_config']['llm']['temperature'] = 0.3
        return client.conversational_ai.agents.create(**config)
```

### Validation Before Creation

```python
def validate_agent_config(config: dict) -> List[str]:
    """Validate configuration before API call"""
    
    errors = []
    
    # Check required fields
    if not config.get('name'):
        errors.append("Agent name is required")
    
    if not config.get('conversation_config', {}).get('agent', {}).get('prompt'):
        errors.append("System prompt is required")
    
    # Validate temperature range
    temp = config.get('conversation_config', {}).get('llm', {}).get('temperature', 0.5)
    if not 0 <= temp <= 1:
        errors.append(f"Temperature {temp} out of range (0-1)")
    
    # Check voice availability
    voice_id = config.get('conversation_config', {}).get('tts', {}).get('voice_id')
    if voice_id and not check_voice_exists(voice_id):
        errors.append(f"Voice {voice_id} not available")
    
    return errors
```

## Performance Optimization

### Agent Response Time Optimization

```python
optimization_settings = {
    # Reduce latency
    "optimize_streaming_latency": 1,  # Lowest latency
    "model_id": "eleven_flash_v2_5",  # Fastest model
    
    # Simplify processing
    "temperature": 0.3,  # More deterministic
    "max_tokens": 100,   # Shorter responses
    
    # Audio optimization
    "output_format": "pcm_16000",  # Lower bandwidth
    "stability": 0.7,    # Less variation processing
}
```

### Knowledge Base Optimization

```python
def optimize_knowledge_base(agent_id: str):
    """Optimize agent's knowledge retrieval"""
    
    # Index frequently accessed documents
    prioritize_documents(agent_id, frequently_used_docs)
    
    # Set appropriate chunk sizes
    configure_rag_settings(
        agent_id,
        chunk_size=512,
        overlap=50,
        top_k=3
    )
    
    # Cache common queries
    enable_query_caching(agent_id)
```

## Monitoring and Analytics

### Key Metrics to Track

```python
class AgentMetrics:
    # Performance metrics
    response_time_ms: float
    first_token_latency_ms: float
    total_duration_seconds: int
    
    # Quality metrics
    transfer_success_rate: float
    completion_rate: float
    error_rate: float
    
    # User experience
    interruption_count: int
    silence_duration_total: float
    user_satisfaction_score: float
    
    # Cost metrics
    tokens_used: int
    llm_cost_usd: float
    tts_characters: int
```

### Evaluation Criteria Setup

```python
def setup_evaluation_criteria(agent_id: str):
    """Configure agent performance tracking"""
    
    criteria = [
        {
            "name": "Correct Routing",
            "success": "Transfer initiated to correct specialist",
            "failure": "Wrong transfer or no transfer when needed",
            "weight": 0.4
        },
        {
            "name": "Response Quality",
            "success": "Accurate, helpful information provided",
            "failure": "Incorrect or unhelpful response",
            "weight": 0.3
        },
        {
            "name": "Conversation Flow",
            "success": "Natural, smooth interaction",
            "failure": "Awkward pauses or interruptions",
            "weight": 0.3
        }
    ]
    
    client.conversational_ai.agents.update_evaluation(
        agent_id=agent_id,
        criteria=criteria
    )
```

## Security and Compliance

### PII Handling

```python
privacy_config = {
    "retention": {
        "days": 90,  # Minimum retention
        "delete_pii": True,
        "anonymize_transcripts": True
    },
    "recording": {
        "enabled": False,  # No audio storage
        "transcript_only": True
    },
    "data_residency": "au",  # Australia region
}
```

### Access Control

```python
def setup_agent_permissions(agent_id: str):
    """Configure agent access controls"""
    
    permissions = {
        "public_access": False,
        "allowed_domains": ["*.company.com"],
        "require_auth": True,
        "api_key_required": True,
        "rate_limit": {
            "calls_per_minute": 10,
            "calls_per_hour": 100
        }
    }
    
    client.conversational_ai.agents.update_permissions(
        agent_id=agent_id,
        permissions=permissions
    )
```

## Implementation Priorities

### Phase 1: Core Functionality (Week 1)
1. ✅ Create Agent (with all parameters)
2. ✅ List Agents
3. ✅ Get Agent Details
4. ✅ Update Agent Configuration
5. ✅ Delete Agent

### Phase 2: Advanced Features (Week 2)
1. Duplicate Agent
2. Tool Management (Create, List, Update)
3. Transfer Configuration
4. Simulation Testing

### Phase 3: Optimization (Week 3)
1. Performance Monitoring
2. Evaluation Criteria
3. Cost Calculation
4. Batch Operations

## MCP Server Structure

```python
# elevenlabs_agents_mcp/server.py

from mcp import MCPServer
from elevenlabs import ElevenLabs

class ElevenLabsAgentsMCP:
    """Specialized MCP for agent management"""
    
    def __init__(self):
        self.client = ElevenLabs()
        self.server = MCPServer("elevenlabs-agents")
        self.register_tools()
    
    def register_tools(self):
        """Register all agent-related tools"""
        
        # Agent management
        self.server.add_tool("create_agent", self.create_agent)
        self.server.add_tool("list_agents", self.list_agents)
        self.server.add_tool("get_agent", self.get_agent)
        self.server.add_tool("update_agent", self.update_agent)
        self.server.add_tool("delete_agent", self.delete_agent)
        self.server.add_tool("duplicate_agent", self.duplicate_agent)
        
        # Tool management
        self.server.add_tool("add_transfer_tool", self.add_transfer_tool)
        self.server.add_tool("configure_tools", self.configure_tools)
        
        # Testing
        self.server.add_tool("simulate_conversation", self.simulate_conversation)
        self.server.add_tool("test_routing", self.test_routing)
        
        # Analytics
        self.server.add_tool("get_agent_metrics", self.get_agent_metrics)
        self.server.add_tool("setup_evaluation", self.setup_evaluation)
```

## Next Steps

1. **Implement Core MCP Server**
   - Set up project structure
   - Implement priority endpoints
   - Add comprehensive error handling

2. **Create Agent Templates**
   - Receptionist template
   - Sales agent template
   - Support agent template
   - Custom specialist templates

3. **Build Testing Suite**
   - Unit tests for each endpoint
   - Integration tests for transfers
   - Load testing scenarios

4. **Documentation**
   - API reference
   - Quick start guide
   - Best practices cookbook
   - Troubleshooting guide

## Resources

- [ElevenLabs API Docs](https://elevenlabs.io/docs/api-reference/conversational-ai)
- [Prompting Guide](https://elevenlabs.io/docs/conversational-ai/prompting-guide)
- [Voice Design Guide](https://elevenlabs.io/docs/conversational-ai/voice-design)
- [GitHub Examples](https://github.com/elevenlabs/elevenlabs-examples)