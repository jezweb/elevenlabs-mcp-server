# ElevenLabs Master Agent Development Guide
*The Complete Reference for Building Professional Conversational AI Agents*

## Table of Contents
1. [Platform Overview](#platform-overview)
2. [The Six Building Blocks Framework](#the-six-building-blocks-framework)
3. [LLM Selection Strategy](#llm-selection-strategy)
4. [Multi-Agent Architecture](#multi-agent-architecture)
5. [Voice Configuration](#voice-configuration)
6. [System Variables & Dynamic Content](#system-variables--dynamic-content)
7. [Transfer Configuration](#transfer-configuration)
8. [Tools & Capabilities](#tools--capabilities)
9. [Knowledge Base & RAG](#knowledge-base--rag)
10. [Audio Configuration](#audio-configuration)
11. [Data Collection & Analytics](#data-collection--analytics)
12. [Evaluation Criteria](#evaluation-criteria)
13. [Implementation Patterns](#implementation-patterns)
14. [Best Practices](#best-practices)
15. [Common Pitfalls](#common-pitfalls)

---

## Platform Overview

ElevenLabs provides a comprehensive platform for creating lifelike conversational AI agents with:
- **Ultra-realistic voice synthesis** with custom voice cloning
- **Multiple LLM integrations** (Gemini, GPT, Claude)
- **Multi-agent orchestration** with seamless transfers
- **Tool integration** for external actions
- **Knowledge base** with RAG for domain expertise
- **Real-time analytics** and conversation tracking

### Key Differentiators
- Sub-second latency for natural conversation flow
- Multilingual support with automatic language detection
- Pronunciation dictionaries for industry-specific terms
- Client-side and server-side tool execution
- Enterprise-grade privacy and retention controls

---

## The Six Building Blocks Framework

Every successful agent prompt MUST include these six components in order:

### 1. PERSONA
Establishes the agent's identity and credibility.

```markdown
## PERSONA
You are [Name], a [specific role] at [company/organization]. 
You have [X years] of experience in [field/specialty].
You are known for [key characteristic or expertise].
```

**Key Elements:**
- **Name**: Give your agent a memorable name
- **Role**: Be specific (e.g., "Senior Technical Support Specialist" not just "support")
- **Background**: Establish expertise and credibility
- **Company Context**: Align with brand identity

**Example:**
```markdown
## PERSONA
You are Marcus, a Master Plumber with 20 years of experience in residential and commercial plumbing systems. You hold certifications in backflow prevention and gas fitting. You're known for your ability to explain complex plumbing issues in simple terms.
```

### 2. GOAL
Defines clear objectives with fallback priorities.

```markdown
## GOAL
PRIMARY: [Main objective - what success looks like]
SECONDARY: [Fallback if primary isn't achievable]
TERTIARY: [Final fallback or escalation]
```

**Goal Types by Agent Role:**
- **Router**: Identify need → Route correctly → Minimize time
- **Information**: Answer questions → Provide guidance → Suggest next steps
- **Booking**: Collect data → Confirm details → Schedule appointment
- **Technical**: Diagnose issue → Provide solution → Recommend service
- **Sales**: Qualify lead → Present value → Close or schedule follow-up

### 3. ENVIRONMENT
Provides context about the interaction channel.

```markdown
## ENVIRONMENT
This is a [phone call/web chat/video call].
The user is likely [context about their situation].
The interaction is happening [time/location context].
Business hours are [schedule] in [timezone].
```

**Channel-Specific Considerations:**
- **Phone**: May be in noisy environment, can't see visual aids
- **Web Chat**: Can share links, may multitask
- **Video**: Can show problems visually, more personal connection

### 4. CONTEXT (System Variables)
⚠️ **CRITICAL: Always use double underscore for system variables**

```markdown
## CONTEXT
- Current time: {{system__time}} ({{system__timezone}})
- UTC time: {{system__time_utc}}
- Caller ID: {{system__caller_id}}
- Conversation ID: {{system__conversation_id}}
- Agent ID: {{system__agent_id}}
```

**Available System Variables:**
- `{{system__time}}` - Local time in caller's timezone
- `{{system__timezone}}` - Caller's timezone
- `{{system__time_utc}}` - Current UTC time
- `{{system__caller_id}}` - Phone number if available
- `{{system__conversation_id}}` - Unique conversation identifier
- `{{system__agent_id}}` - Current agent's ID

### 5. TONE
Defines communication style and linguistic patterns.

```markdown
## TONE
- [Language variety] (e.g., Professional Australian English)
- [Sentence structure] (e.g., Short, clear sentences)
- [Speech patterns] (e.g., Natural fillers like "let me see...")
- [Formality level] (e.g., Address by first name)
- [Energy level] (e.g., Warm and engaging)
```

**Tone Variations by Role:**
- **Receptionist**: Warm, welcoming, efficient
- **Technical Expert**: Clear, precise, educational
- **Sales**: Enthusiastic, consultative, value-focused
- **Support**: Empathetic, patient, solution-oriented
- **Emergency**: Calm, decisive, reassuring

### 6. ADAPTABILITY
Dynamic behavior adjustments based on context.

```markdown
## ADAPTABILITY
- If user sounds frustrated: Acknowledge with "I understand this is frustrating..."
- If user is in a hurry: Skip pleasantries, be direct
- If technical level unclear: Start simple, adjust based on response
- If emergency detected: Immediately prioritize safety
- If price questioned: Emphasize value before defending cost
```

---

## LLM Selection Strategy

### Model Selection Matrix

| Use Case | Recommended Model | Temperature | Rationale |
|----------|------------------|-------------|-----------|
| Simple Routing | Gemini 2.5 Flash Lite | 0.2-0.3 | Fast, consistent, cost-effective |
| Information Delivery | Gemini 2.5 Flash | 0.3-0.4 | Balanced accuracy and naturalness |
| Complex Technical | Gemini 2.5 Pro | 0.2-0.3 | Maximum accuracy, detailed reasoning |
| Data Collection | Gemini 2.5 Flash | 0.4-0.5 | Natural conversation, systematic |
| Sales/Persuasion | Gemini 2.5 Flash | 0.5-0.6 | Creative, engaging, adaptive |
| Creative/Entertainment | Gemini 2.5 Flash | 0.6-0.7 | Maximum personality, variety |

### Temperature Guidelines

**0.2-0.3: Consistency Critical**
- Routing decisions
- Compliance statements
- Technical accuracy
- Emergency handling

**0.4-0.5: Balanced Natural**
- General conversation
- Information delivery
- Data collection
- Customer service

**0.6-0.7: Creative Engagement**
- Sales conversations
- Entertainment
- Storytelling
- Personality-driven

### Token Limits by Role

- **Router**: 100-150 (force conciseness)
- **Information**: 200-300 (detailed explanations)
- **Technical**: 300-400 (comprehensive answers)
- **Booking**: 150-200 (systematic collection)
- **Sales**: 250-350 (persuasive content)

---

## Multi-Agent Architecture

### The Hub-and-Spoke Pattern

```
                Main Router Agent
                (Gemini Flash Lite, 0.2)
                       |
    ┌─────────┬────────┼────────┬─────────┐
    ↓         ↓        ↓        ↓         ↓
Services   Booking  Technical  Sales   Emergency
(Flash)    (Flash)   (Pro)    (Flash)  (Human)
```

### Transfer Decision Tree

```markdown
Main Router Logic:
├── Keywords: "emergency", "flood", "gas leak" → Emergency Human
├── Keywords: "book", "schedule", "appointment" → Booking Agent
├── Keywords: "price", "cost", "services" → Services Info
├── Keywords: "why", "explain", "technical" → Technical Expert
├── Keywords: "AI", "automation", "digital" → Sales Agent
└── Default: "Not sure" → Support Human
```

### Transfer Configuration Rules

1. **Enable "First Message" on all receiving agents**
2. **Set clear transfer conditions in natural language**
3. **Include transfer message for smooth handoff**
4. **Test every transfer path**
5. **Monitor transfer success rates**

### Multi-Agent Design Principles

1. **Single Responsibility**: Each agent has ONE primary function
2. **Clear Boundaries**: No overlap in capabilities
3. **Graceful Handoffs**: Smooth transfer messages
4. **Fallback Paths**: Always have human escalation
5. **Context Preservation**: Pass relevant data in transfers

---

## Voice Configuration

### Voice Selection Criteria

**Professional/Business:**
- Paul (Australian male) - Authoritative presenter
- Matilda (Australian female) - Professional, clear
- Will (British male) - Corporate, sophisticated

**Friendly/Service:**
- Emily (Australian female) - Warm, approachable
- Sam (American male) - Friendly, knowledgeable
- Lisa (British female) - Helpful, patient

**Technical/Expert:**
- Marcus (Deep male) - Authoritative expert
- Victoria (Mature female) - Experienced professional

### Voice Settings

```json
{
  "voice_id": "XrExE9yKIg1WjnnlVkGX",
  "stability": 0.5,        // 0=variable, 1=consistent
  "similarity_boost": 0.8,  // Voice matching strength
  "style": 0.4,            // Style exaggeration
  "use_speaker_boost": true // Enhanced clarity
}
```

**Stability Settings:**
- 0.3-0.4: More expressive, emotional range
- 0.5-0.6: Balanced naturalness
- 0.7-0.8: Consistent, professional

### Pronunciation Dictionaries

For technical terms, acronyms, or names:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0" xmlns="http://www.w3.org/2005/01/pronunciation-lexicon" 
         alphabet="ipa" xml:lang="en-US">
  <lexeme>
    <grapheme>AS/NZS</grapheme>
    <phoneme>eɪ ɛs slæʃ ɛn zɛd ɛs</phoneme>
  </lexeme>
  <lexeme>
    <grapheme>kPa</grapheme>
    <phoneme>kɪləpæskəl</phoneme>
  </lexeme>
</lexicon>
```

---

## System Variables & Dynamic Content

### ⚠️ CRITICAL: Double Underscore Rule

**CORRECT:** `{{system__time}}`  
**WRONG:** `{{system_time}}` ❌

### System Variables Reference

| Variable | Description | Example Output |
|----------|-------------|----------------|
| `{{system__time}}` | Local time | "2:30 PM" |
| `{{system__timezone}}` | Timezone | "Australia/Sydney" |
| `{{system__time_utc}}` | UTC time | "2024-01-15T04:30:00Z" |
| `{{system__caller_id}}` | Phone number | "+61411234567" |
| `{{system__conversation_id}}` | Unique ID | "conv_abc123xyz" |
| `{{system__agent_id}}` | Agent ID | "agent_7701k2pr..." |

### Custom Variables (SDK Only)

When using SDK implementation:

```javascript
window.ElevenLabsConvai.embed({
  agentId: 'agent_id',
  variables: {
    business_hours_start: '08:00',
    business_hours_end: '18:00',
    emergency_number: '0400123456',
    company_name: 'ACME Corp'
  }
});
```

In prompt: `{{business_hours_start}}` to `{{business_hours_end}}`

### Variable Best Practices

1. **Always test variable rendering**
2. **Provide fallbacks for missing variables**
3. **Don't use variables in First Message**
4. **Use system variables for time-based routing**
5. **Document all custom variables**

---

## Transfer Configuration

### Transfer Types

#### 1. Transfer to AI Agent
```json
{
  "tool_type": "transfer_to_ai_agent",
  "agent_id": "agent_8801k2px9ch5ee2bs65xwwhdzcjq",
  "condition": "User wants to book, schedule, or needs appointment",
  "transfer_message": "I'll connect you with our booking specialist...",
  "enable_first_message": true
}
```

#### 2. Transfer to Human/Phone
```json
{
  "tool_type": "transfer_to_number",
  "phone_number": "0411234567",
  "condition": "Emergency or urgent situation requiring immediate human help",
  "transfer_message": "This requires immediate attention. Connecting you now..."
}
```

### Transfer Condition Writing

**Effective Conditions:**
```
"User mentions booking, appointment, schedule, wants to book a time, asks about availability, says they need someone to come out, or indicates readiness to schedule service"
```

**Key Principles:**
- Use multiple trigger variations
- Include common phrasings
- Be specific but comprehensive
- Test edge cases

### Transfer Testing Script

```markdown
Test Each Transfer Path:
1. Direct keyword: "I want to book"
2. Indirect intent: "When can someone come?"
3. Question form: "Do you have availability?"
4. Statement form: "I need this fixed"
5. Complex: "It's not urgent but I'd like someone this week"
```

---

## Tools & Capabilities

### System Tools

**end_call**
- Allows agent to end conversation naturally
- Triggers on goodbye keywords
- Always enable for better UX

**transfer_to_ai_agent**
- Seamless handoff between agents
- Preserves conversation context
- Requires target agent ID

**transfer_to_number**
- Human escalation path
- Emergency handling
- Direct phone transfer

**language_detection**
- Automatic language switching
- Multi-language support
- Requires additional languages configured

### Webhook Tools (Server-Side)

Connect to external services via webhooks:

```json
{
  "tool_type": "webhook",
  "name": "check_availability",
  "description": "Check available appointment slots",
  "url": "https://n8n.yourcompany.com/webhook/availability",
  "parameters": [
    {
      "name": "date",
      "type": "string",
      "description": "Requested date",
      "required": true
    },
    {
      "name": "service_type",
      "type": "string",
      "description": "Type of service needed",
      "required": true
    }
  ]
}
```

### Client Tools (Local Execution)

For actions on user's device:

```python
# Python SDK example
from elevenlabs import ConversationAgent

def handle_screen_share(params):
    # Access user's camera/screen
    return {"status": "screen_shared"}

agent.register_tool("share_screen", handle_screen_share)
```

### Tool Integration Patterns

**Database Lookup:**
```
User → Agent → Webhook → n8n → Database → Response → Agent → User
```

**CRM Integration:**
```
Agent → Webhook → Zapier/n8n → Salesforce/HubSpot → Confirmation
```

**Calendar Booking:**
```
Agent → Check Availability → Show Slots → Confirm → Create Booking
```

---

## Knowledge Base & RAG

### Knowledge Base Setup

**Supported Formats:**
- PDF documents
- DOCX files
- TXT files (including converted markdown)
- HTML files
- EPUB books

**File Preparation:**
1. Convert markdown to .txt
2. Structure content clearly
3. Use headers for sections
4. Include relevant keywords
5. Keep files under 10MB

### RAG Configuration

**Enable RAG for:**
- Technical documentation search
- Product information retrieval
- Policy and procedure lookup
- FAQ responses

**RAG Settings:**
```json
{
  "use_rag": true,
  "search_threshold": 0.7,
  "max_results": 3,
  "include_source": true
}
```

### Knowledge Base Best Practices

1. **Organize by Topic**: Separate files for different domains
2. **Update Regularly**: Keep information current
3. **Test Search**: Verify RAG returns relevant results
4. **Include Examples**: Add real scenarios and solutions
5. **Avoid Duplication**: Prevent conflicting information

---

## Audio Configuration

### Optimal Settings

**User Input Audio Format:**
```
PCM 16000 Hz (Recommended)
- Full speech frequency range (80-8000 Hz)
- Lower latency than 48kHz
- 4x less bandwidth
- Industry telephony standard
```

**Output Format:**
```
Format: MP3
Sample Rate: 24000 Hz
Bitrate: 96 kbps
```

### Advanced Audio Settings

```json
{
  "turn_timeout": 60,              // Seconds before agent responds
  "silence_end_call_timeout": -1,  // No auto-termination
  "max_duration": 600,              // 10-minute max call
  "optimize_streaming_latency": 3,  // 0-4 scale
  "vad_sensitivity": 0.5           // Voice activity detection
}
```

### Client Events

**Essential Events:**
- ✅ audio
- ✅ interruption
- ✅ user_transcript
- ✅ agent_response
- ✅ agent_response_correction
- ✅ **agent_tool_response** (track tool usage)

**Debug Events:**
- vad_score (voice detection issues)
- latency_measurement (performance)

---

## Data Collection & Analytics

### Data Collection Schema

```json
{
  "data_collection": [
    {
      "type": "string",
      "identifier": "customer_name",
      "prompt": "Extract the customer's full name. Return 'not_provided' if not given."
    },
    {
      "type": "boolean",
      "identifier": "issue_resolved",
      "prompt": "Was the customer's issue fully resolved? Return true or false."
    },
    {
      "type": "integer",
      "identifier": "satisfaction_score",
      "prompt": "On a scale of 1-10, how satisfied was the customer? Return -1 if not determinable."
    },
    {
      "type": "number",
      "identifier": "call_duration_minutes",
      "prompt": "Calculate the call duration in minutes with decimals."
    }
  ]
}
```

### Data Types

- **String**: Text, categories, descriptions
- **Boolean**: Yes/no, true/false
- **Integer**: Whole numbers, counts
- **Number**: Decimals, percentages

### Analytics Integration

**Webhook for Analytics:**
```json
{
  "webhook_url": "https://analytics.company.com/conversations",
  "events": ["conversation_end"],
  "include_transcript": true,
  "include_data_collection": true
}
```

---

## Evaluation Criteria

### Multiple Criteria Per Agent

Each agent should have 3-5 evaluation criteria:

```json
{
  "evaluation_criteria": [
    {
      "name": "Correct Routing",
      "prompt": "Did the agent route to the correct specialist? Success: correct transfer. Failure: wrong transfer or handled incorrectly. Unknown: call ended early."
    },
    {
      "name": "Response Time",
      "prompt": "Did the agent respond within acceptable time? Success: under 30 seconds. Failure: over 30 seconds. Unknown: technical issues."
    },
    {
      "name": "Data Completeness",
      "prompt": "Were all required fields collected? Success: all fields. Failure: missing required data. Unknown: call interrupted."
    }
  ]
}
```

### Evaluation Categories

**Performance Metrics:**
- Speed of response
- Transfer accuracy
- Task completion rate

**Quality Metrics:**
- Information accuracy
- Customer satisfaction
- Professional tone

**Compliance Metrics:**
- Following procedures
- Safety protocols
- Data privacy

---

## Implementation Patterns

### Pattern 1: Simple Q&A Bot
```
Single Agent
├── Knowledge Base (FAQs)
├── RAG Enabled
├── Fallback to Human
└── Low Temperature (0.3)
```

### Pattern 2: Appointment Scheduler
```
Router Agent → Booking Agent
              ├── Availability Check (Webhook)
              ├── Data Collection
              ├── Confirmation Email
              └── Calendar Integration
```

### Pattern 3: Technical Support System
```
Router Agent
├── Level 1 Support (Flash)
├── Level 2 Technical (Pro)
├── Emergency Escalation (Human)
└── Ticket Creation (Webhook)
```

### Pattern 4: Sales Funnel
```
Qualifier Agent → Product Specialist → Closing Agent
                                    ├── CRM Update
                                    ├── Meeting Scheduler
                                    └── Follow-up Email
```

---

## Best Practices

### Prompt Engineering

1. **Start with the Six Building Blocks**
2. **Be specific about expectations**
3. **Include examples of good responses**
4. **Define failure scenarios clearly**
5. **Test with edge cases**

### Testing Protocol

1. **Test every transfer path**
2. **Verify data collection accuracy**
3. **Check emergency handling**
4. **Validate time-based routing**
5. **Test with various accents/speeds**

### Performance Optimization

1. **Use appropriate LLM for task complexity**
2. **Minimize token usage in routers**
3. **Cache frequently accessed data**
4. **Optimize audio settings for network**
5. **Monitor latency metrics**

### Security & Privacy

1. **Never log sensitive data**
2. **Use secure webhooks (HTTPS only)**
3. **Implement retention policies**
4. **Encrypt stored conversations**
5. **Audit tool access regularly**

---

## Common Pitfalls

### Top 10 Mistakes to Avoid

1. ❌ **Using single underscore in system variables**
   - Wrong: `{{system_time}}`
   - Right: `{{system__time}}`

2. ❌ **Not enabling "First Message" on transfer targets**
   - Always check this box for receiving agents

3. ❌ **Setting temperature too high for routers**
   - Keep at 0.2-0.3 for consistent routing

4. ❌ **Using markdown files in knowledge base**
   - Convert to .txt first

5. ❌ **Forgetting to test transfer paths**
   - Test every possible transfer scenario

6. ❌ **Making prompts too complex**
   - Break into multiple specialized agents

7. ❌ **Not providing fallback options**
   - Always have human escalation path

8. ❌ **Ignoring audio optimization**
   - Use PCM 16000 Hz for best results

9. ❌ **Hardcoding time-sensitive information**
   - Use system variables for dynamic content

10. ❌ **Not monitoring conversation quality**
    - Regular transcript reviews essential

### Debugging Checklist

When things go wrong:

- [ ] Check system variable syntax (double underscore?)
- [ ] Verify agent IDs in transfers
- [ ] Confirm "First Message" enabled
- [ ] Test with simple prompts first
- [ ] Check webhook URL accessibility
- [ ] Verify knowledge base file formats
- [ ] Review LLM temperature settings
- [ ] Confirm audio settings match network
- [ ] Check evaluation criteria logic
- [ ] Monitor tool execution logs

---

## Quick Start Templates

### Minimal Router Agent
```markdown
## PERSONA
You are the receptionist at [Company].

## GOAL
PRIMARY: Route callers to the right department quickly.

## ENVIRONMENT
This is a phone call.

## CONTEXT
Time: {{system__time}}

## TONE
Professional and efficient.

## ADAPTABILITY
If emergency: Transfer immediately.
```

### Basic Information Agent
```markdown
## PERSONA
You are [Name], a customer service specialist.

## GOAL
PRIMARY: Answer questions about our services.
SECONDARY: Collect contact info for follow-up.

## ENVIRONMENT
This is a phone conversation.

## CONTEXT
Current time: {{system__time}}

## TONE
Friendly and helpful.

## ADAPTABILITY
If question too complex: Offer to transfer to specialist.
```

---

## Resources & References

### Official Documentation
- ElevenLabs API: https://docs.elevenlabs.io
- Voice Library: https://elevenlabs.io/voice-library
- SDK Documentation: Platform-specific guides

### Integration Platforms
- n8n: Workflow automation
- Make/Zapier: No-code integrations
- Custom webhooks: Direct API integration

### Community Resources
- GitHub examples
- Discord community
- Video tutorials

---

*Last Updated: 2025-08-15*
*Version: 2.0*
*Maintainer: jeremy@jezweb.net*