# ElevenLabs System Prompt Quick Start Guide

## 🚀 Agent Creation Checklist

### Essential Steps
- [ ] Define agent identity (PERSONA)
- [ ] Set clear objectives (GOAL)
- [ ] Configure voice and language
- [ ] Add system variables to prompt
- [ ] Test all transfer paths
- [ ] Enable required tools
- [ ] Upload knowledge base (if needed)
- [ ] Set appropriate LLM and temperature

## 📝 Minimal Viable System Prompt

```markdown
## PERSONA
You are [Name], a [role] at [company].

## GOAL
PRIMARY: [Main objective]
SECONDARY: [Fallback goal]

## ENVIRONMENT
This is a [phone call/web chat].

## CONTEXT
- Current time: {{system__time}} ({{system__timezone}})
- Caller ID: {{system__caller_id}}

## TONE
[Language style and patterns]

## ADAPTABILITY
If [condition]: [response adjustment]
```

## ⚡ Critical Rules

### 1. System Variables MUST Use Double Underscore
- ✅ CORRECT: `{{system__time}}`
- ❌ WRONG: `{{system_time}}`

### 2. Enable "First Message" for Transfer Targets
Every agent that receives transfers must have this enabled.

### 3. Temperature by Agent Type
- **Router/Receptionist**: 0.2-0.3
- **Information/Support**: 0.4-0.5
- **Sales/Creative**: 0.5-0.7

### 4. Voice Settings Quick Reference
- **Stability**: 0.5 (balanced)
- **Similarity Boost**: 0.8 (consistency)
- **Audio Format**: PCM 16000 Hz (optimal)

## 🔗 Quick Links to Detailed Sections

| Topic | File | Use When |
|-------|------|----------|
| Full Framework | [02-SIX_BUILDING_BLOCKS.md](02-SIX_BUILDING_BLOCKS.md) | Understanding core concepts |
| Templates | [03-PROMPT_TEMPLATES.md](03-PROMPT_TEMPLATES.md) | Need a starting point |
| LLM Settings | [04-LLM_CONFIGURATION.md](04-LLM_CONFIGURATION.md) | Choosing model/temperature |
| Variables | [05-VARIABLES_AND_DYNAMICS.md](05-VARIABLES_AND_DYNAMICS.md) | Using dynamic content |
| Multi-Agent | [06-MULTI_AGENT_ARCHITECTURE.md](06-MULTI_AGENT_ARCHITECTURE.md) | Building agent systems |
| Voice/Audio | [07-VOICE_AND_AUDIO.md](07-VOICE_AND_AUDIO.md) | Voice configuration |
| Tools | [08-TOOLS_AND_INTEGRATIONS.md](08-TOOLS_AND_INTEGRATIONS.md) | Adding capabilities |
| Knowledge Base | [09-KNOWLEDGE_BASE_RAG.md](09-KNOWLEDGE_BASE_RAG.md) | Document search |
| Transfers | [10-TRANSFER_CONFIGURATION.md](10-TRANSFER_CONFIGURATION.md) | Agent routing |
| Analytics | [11-DATA_COLLECTION_EVALUATION.md](11-DATA_COLLECTION_EVALUATION.md) | Tracking performance |
| Testing | [12-TESTING_AND_QUALITY.md](12-TESTING_AND_QUALITY.md) | Quality assurance |
| Debugging | [13-COMMON_PITFALLS.md](13-COMMON_PITFALLS.md) | Troubleshooting |
| Advanced | [14-ADVANCED_PATTERNS.md](14-ADVANCED_PATTERNS.md) | Complex scenarios |
| Examples | [15-EXAMPLES_LIBRARY.md](15-EXAMPLES_LIBRARY.md) | Complete implementations |

## 🎯 Agent Type Quick Selector

### Need a Router/Receptionist?
- Model: Gemini 2.5 Flash Lite
- Temperature: 0.2-0.3
- Max Tokens: 100-150
- See: [Router Template](03-PROMPT_TEMPLATES.md#router-receptionist)

### Need Information/FAQ Agent?
- Model: Gemini 2.5 Flash
- Temperature: 0.3-0.4
- Max Tokens: 200-300
- Enable: Knowledge Base with RAG
- See: [Information Template](03-PROMPT_TEMPLATES.md#information-faq)

### Need Booking/Sales Agent?
- Model: Gemini 2.5 Flash
- Temperature: 0.4-0.5
- Max Tokens: 250-350
- Enable: Data Collection
- See: [Booking Template](03-PROMPT_TEMPLATES.md#booking-appointment)

### Need Technical Expert?
- Model: Gemini 2.5 Pro
- Temperature: 0.2-0.3
- Max Tokens: 300-400
- Enable: Knowledge Base
- See: [Technical Template](03-PROMPT_TEMPLATES.md#technical-support)

## 🛠️ Essential Tools to Enable

### Always Enable
- ✅ **end_call** - Natural conversation ending
- ✅ **transfer_to_ai_agent** - Agent handoffs (if multi-agent)
- ✅ **transfer_to_number** - Human escalation

### Enable When Needed
- **language_detection** - For multilingual support
- **skip_turn** - Let user continue speaking
- **Webhooks** - External integrations

## 📊 Testing Checklist

Before going live:
1. Test each transfer scenario
2. Verify emergency handling
3. Check voice clarity and speed
4. Test with different accents
5. Validate knowledge base responses
6. Review conversation transcripts
7. Monitor latency metrics

## 🚨 Most Common Mistakes

1. **Using single underscore** in system variables
2. **Not enabling "First Message"** on transfer targets
3. **Temperature too high** for routers (keep at 0.2-0.3)
4. **Using markdown files** in knowledge base (convert to .txt)
5. **Forgetting to test** transfer paths
6. **Making prompts too complex** (use multiple agents instead)
7. **Not providing fallbacks** for failed scenarios

## 💡 Pro Tips

- **Start simple**: Get basic flow working before adding complexity
- **Test incrementally**: Add one feature at a time
- **Monitor transcripts**: Regular reviews reveal improvement areas
- **Use multiple agents**: Better than one complex agent
- **Document everything**: Keep notes on what works
- **Version your prompts**: Track changes over time

## 🔄 Iteration Workflow

1. **Create** minimal viable prompt
2. **Test** with 5-10 conversations
3. **Review** transcripts for issues
4. **Refine** based on patterns
5. **Add** features incrementally
6. **Deploy** with monitoring
7. **Iterate** based on data

## 📞 Emergency Configuration

If your agent handles emergencies:
```markdown
## ADAPTABILITY
If user mentions: emergency, urgent, fire, flood, injury, accident:
- Immediately say: "I understand this is an emergency."
- Transfer to: emergency_number
- Transfer message: "Connecting you to emergency services now."
```

## 🌍 Multilingual Setup

```markdown
## CONTEXT
- Default language: English
- Additional languages: Spanish, French, Mandarin
- Enable tool: language_detection

## ADAPTABILITY
If language detected != English:
- Switch to detected language
- Maintain same tone and personality
```

---

*Next: Deep dive into the [Six Building Blocks Framework →](02-SIX_BUILDING_BLOCKS.md)*