# Complete ElevenLabs Agent Prompt Guide

A comprehensive, practical guide for creating effective ElevenLabs conversational AI agents using best practices and proven patterns.

## 📋 Quick Start

New to ElevenLabs agents? Start here:
1. **[Quick Start Guide](01-QUICK_START.md)** - Essential checklist and minimal viable prompt
2. **[Six Building Blocks](02-SIX_BUILDING_BLOCKS.md)** - Core framework for all prompts
3. **[Prompt Templates](03-PROMPT_TEMPLATES.md)** - Ready-to-use templates

## 📚 Complete Guide Structure

### Foundation (Start Here)
- **[01-QUICK_START.md](01-QUICK_START.md)** - Essential rules, checklist, and minimal prompt template
- **[02-SIX_BUILDING_BLOCKS.md](02-SIX_BUILDING_BLOCKS.md)** - PERSONA, GOAL, ENVIRONMENT, CONTEXT, TONE, ADAPTABILITY framework
- **[03-PROMPT_TEMPLATES.md](03-PROMPT_TEMPLATES.md)** - 10 ready-to-use agent templates

### Configuration and Setup
- **[04-LLM_CONFIGURATION.md](04-LLM_CONFIGURATION.md)** - Model selection, temperature settings, token optimization
- **[05-VARIABLES_AND_DYNAMICS.md](05-VARIABLES_AND_DYNAMICS.md)** - System variables (critical double underscore rule), SDK integration
- **[06-MULTI_AGENT_ARCHITECTURE.md](06-MULTI_AGENT_ARCHITECTURE.md)** - Multi-agent design patterns and transfer configuration

### Technical Implementation
- **[07-VOICE_AND_AUDIO.md](07-VOICE_AND_AUDIO.md)** - Voice selection, audio configuration, latency optimization
- **[08-TOOLS_AND_INTEGRATIONS.md](08-TOOLS_AND_INTEGRATIONS.md)** - Tool configuration, webhooks, external system integration
- **[09-KNOWLEDGE_BASE_RAG.md](09-KNOWLEDGE_BASE_RAG.md)** - Knowledge base setup, RAG configuration, content optimization
- **[10-TRANSFER_CONFIGURATION.md](10-TRANSFER_CONFIGURATION.md)** - Transfer rules, conditions, loop prevention

### Quality and Optimization
- **[11-DATA_COLLECTION_EVALUATION.md](11-DATA_COLLECTION_EVALUATION.md)** - Data collection, evaluation criteria, analytics
- **[12-TESTING_AND_QUALITY.md](12-TESTING_AND_QUALITY.md)** - Testing frameworks, quality metrics, continuous improvement
- **[13-COMMON_PITFALLS.md](13-COMMON_PITFALLS.md)** - 20 common mistakes and how to avoid them

### Advanced Topics
- **[14-ADVANCED_PATTERNS.md](14-ADVANCED_PATTERNS.md)** - Advanced architectural patterns, ML integration, scaling
- **[15-EXAMPLES_LIBRARY.md](15-EXAMPLES_LIBRARY.md)** - Complete production-ready examples for all agent types

## 🎯 Use Case Guides

### By Agent Type
| Agent Type | Templates | Examples | Configuration |
|------------|-----------|----------|---------------|
| **Router** | [Templates](03-PROMPT_TEMPLATES.md#router-agents) | [Examples](15-EXAMPLES_LIBRARY.md#router-agents) | [Multi-Agent](06-MULTI_AGENT_ARCHITECTURE.md) |
| **Booking** | [Templates](03-PROMPT_TEMPLATES.md#booking-agents) | [Examples](15-EXAMPLES_LIBRARY.md#booking-specialists) | [Data Collection](11-DATA_COLLECTION_EVALUATION.md) |
| **Support** | [Templates](03-PROMPT_TEMPLATES.md#support-agents) | [Examples](15-EXAMPLES_LIBRARY.md#support-specialists) | [Knowledge Base](09-KNOWLEDGE_BASE_RAG.md) |
| **Sales** | [Templates](03-PROMPT_TEMPLATES.md#sales-agents) | [Examples](15-EXAMPLES_LIBRARY.md#sales-specialists) | [Evaluation](11-DATA_COLLECTION_EVALUATION.md) |

### By Industry
| Industry | Relevant Sections | Key Considerations |
|----------|-------------------|-------------------|
| **Healthcare** | [Examples](15-EXAMPLES_LIBRARY.md#healthcare-navigation), [Privacy](11-DATA_COLLECTION_EVALUATION.md#data-privacy-and-compliance) | HIPAA compliance, medical triage |
| **Insurance** | [Examples](15-EXAMPLES_LIBRARY.md#insurance-claims-agent), [Data Collection](11-DATA_COLLECTION_EVALUATION.md) | Claims processing, fraud detection |
| **Retail/E-commerce** | [Sales Examples](15-EXAMPLES_LIBRARY.md#retail-sales-agent), [Customer Service](15-EXAMPLES_LIBRARY.md#customer-service-agent) | Product recommendations, order management |
| **Professional Services** | [B2B Examples](15-EXAMPLES_LIBRARY.md#b2b-sales-qualifier), [Booking](15-EXAMPLES_LIBRARY.md#booking-specialists) | Lead qualification, appointment scheduling |

## ⚠️ Critical Reminders

### Must-Do Checklist
- ✅ **Use double underscores** for system variables: `{{system__time}}` not `{{system_time}}`
- ✅ **Enable RAG** when using knowledge base
- ✅ **Enable First Message** on receiving agents
- ✅ **Include Adaptability section** in all prompts
- ✅ **Test all transfer scenarios** thoroughly

### Common Pitfalls to Avoid
- ❌ Single underscore system variables (see [Common Pitfalls](13-COMMON_PITFALLS.md#1-the-double-underscore-disaster))
- ❌ Vague transfer conditions (see [Transfer Configuration](10-TRANSFER_CONFIGURATION.md))
- ❌ Missing first message on transfers (see [Common Pitfalls](13-COMMON_PITFALLS.md#3-first-message-not-enabled))
- ❌ High temperature for rule-following agents (see [LLM Configuration](04-LLM_CONFIGURATION.md))

## 🔧 Configuration Quick Reference

### Model Selection
```yaml
Router Agents: "gemini-2.5-flash-lite" (temperature: 0.2-0.3)
Booking/Support: "gemini-2.5-flash" (temperature: 0.3-0.5)
Complex Reasoning: "gemini-2.5-pro" (temperature: 0.4-0.6)
```

### Voice Settings
```yaml
Stability: 0.5 (balanced)
Similarity Boost: 0.8 (consistent)
Style: 0.0 (real-time conversations)
Output Format: "pcm_16000" (optimal latency)
```

### Essential Tools
```yaml
Required Tools:
  - end_call
  - transfer_to_agent
  - transfer_to_number
  
Common Additions:
  - data_collection
  - knowledge_base_search
  - external_api_calls
```

## 📈 Implementation Workflow

### 1. Planning Phase
1. Define agent purpose and scope
2. Map user journey and interactions
3. Choose appropriate templates
4. Plan multi-agent architecture if needed

### 2. Development Phase
1. Create prompts using [Six Building Blocks](02-SIX_BUILDING_BLOCKS.md)
2. Configure [LLM settings](04-LLM_CONFIGURATION.md)
3. Set up [transfer rules](10-TRANSFER_CONFIGURATION.md)
4. Configure [data collection](11-DATA_COLLECTION_EVALUATION.md)

### 3. Testing Phase
1. Use [testing frameworks](12-TESTING_AND_QUALITY.md)
2. Test all scenarios from [examples](15-EXAMPLES_LIBRARY.md)
3. Validate against [common pitfalls](13-COMMON_PITFALLS.md)
4. Performance and load testing

### 4. Deployment Phase
1. Monitor using [quality metrics](12-TESTING_AND_QUALITY.md)
2. Set up [evaluation criteria](11-DATA_COLLECTION_EVALUATION.md)
3. Continuous improvement cycle

## 🛠️ Development Tools

### ElevenLabs CLI (Recommended)
```bash
npm install -g @elevenlabs/convai-cli
convai login
convai init your-project
convai sync  # Keep agents in sync
```

### Dashboard Configuration
- Agent creation and prompt editing
- Voice selection and audio settings
- Transfer rule configuration
- Data collection setup

### API Integration
- Webhook endpoints for external systems
- Real-time conversation data
- Custom variable injection
- Advanced analytics integration

## 📊 Monitoring and Analytics

### Key Metrics to Track
- **Effectiveness**: First call resolution, correct routing rate, task completion
- **Efficiency**: Average handling time, transfer rate, escalation rate  
- **Experience**: Customer satisfaction, agent rating, recommendation score
- **Technical**: Uptime, response time, error rate

### Evaluation Setup
```yaml
Multiple Criteria per Agent:
  - Task-specific success metrics
  - Customer experience indicators
  - Technical performance measures
  - Business outcome correlation
```

## 🆘 Troubleshooting

### Common Issues
| Problem | Solution | Reference |
|---------|----------|-----------|
| Variables not working | Check double underscore syntax | [Variables Guide](05-VARIABLES_AND_DYNAMICS.md) |
| Silent transfers | Enable first message on receiving agent | [Common Pitfalls](13-COMMON_PITFALLS.md#3) |
| Poor routing | Refine transfer conditions | [Transfer Config](10-TRANSFER_CONFIGURATION.md) |
| Knowledge base not working | Enable RAG toggle | [Knowledge Base](09-KNOWLEDGE_BASE_RAG.md) |
| High latency | Check voice style and audio format | [Voice Configuration](07-VOICE_AND_AUDIO.md) |

### When You Need Help
1. Check [Common Pitfalls](13-COMMON_PITFALLS.md) first
2. Review relevant configuration guides
3. Test with [provided scripts](15-EXAMPLES_LIBRARY.md#testing-scripts)
4. Use ElevenLabs dashboard testing tools
5. Check conversation logs for specific issues

## 🔄 Updates and Maintenance

### Regular Tasks
- **Weekly**: Review conversation quality and user feedback
- **Monthly**: Update knowledge base content and optimize prompts
- **Quarterly**: Comprehensive performance review and major improvements

### Best Practices
- Version control your prompt configurations
- A/B test prompt variations
- Monitor quality metrics continuously
- Keep knowledge base current
- Regular backup of configurations

## 📝 Contributing

This guide is based on real-world implementation experience and ElevenLabs best practices. Key sources include:
- Official ElevenLabs documentation
- Production deployment learnings
- Community feedback and testing
- Continuous optimization results

---

## 🚀 Getting Started

**New to ElevenLabs?** Start with:
1. [Quick Start Guide](01-QUICK_START.md) (5 minutes)
2. [Six Building Blocks](02-SIX_BUILDING_BLOCKS.md) (15 minutes)  
3. Choose a [template](03-PROMPT_TEMPLATES.md) that matches your use case (10 minutes)

**Ready to build?** Use the [Examples Library](15-EXAMPLES_LIBRARY.md) for complete implementation references.

**Having issues?** Check [Common Pitfalls](13-COMMON_PITFALLS.md) for quick solutions.

---

*Last updated: 2024*  
*For the latest ElevenLabs features and API changes, always refer to the official ElevenLabs documentation.*