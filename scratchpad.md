# ElevenLabs MCP Servers - Templates & Resources Planning

## Core Philosophy
- Keep it simple and practical
- Focus on real use cases that people actually need
- Make templates that work out-of-the-box
- Avoid over-engineering

## Implementation Status

### ✅ Architecture Updates (Completed)
- Refined separation between audio and voices servers
- elevenlabs-audio: Content generation (TTS, STT, effects, voice transform)
- elevenlabs-voices: Resource management (voice CRUD, cloning, library)

### ✅ elevenlabs-audio Server (Completed - 2024-12-XX)
Successfully implemented with:
- **TTS Tools**: text_to_speech, timestamps, dialogue generation
- **STT Tools**: transcription, batch processing, diarization
- **Effects**: Sound effect generation from text
- **Voice Transform**: Speech-to-speech, audio isolation

Key implementation decisions:
- Used absolute imports with sys.path modification for FastMCP compatibility
- Separated client methods for binary vs JSON responses (_request_binary method)
- Modular tool organization in separate files
- Self-contained shared utilities (no cross-server dependencies)
- Fixed relative imports for cloud deployment

Technical notes:
- FastMCP requires server object (mcp) at module level
- All dependencies must be from PyPI (no local packages)
- Import path fix: sys.path.insert(0, str(Path(__file__).parent))

### ✅ elevenlabs-voices Server (Completed - 2025-01-25)
Successfully implemented with comprehensive voice management:
- **Voice Management**: CRUD operations (get, list, delete)
- **Voice Design**: Text-to-voice generation with previews and permanent creation
- **Instant Voice Cloning (IVC)**: Clone voices from audio samples (WAV, MP3, FLAC, M4A, OGG, WEBM)
- **Voice Library**: Search public library, add shared voices to collection
- **Voice Settings**: Configure stability, similarity_boost, style, use_speaker_boost

Key implementation decisions:
- Modular tool organization with 5 focused modules
- Self-contained utilities with voice-specific validation
- Comprehensive error handling with helpful suggestions
- Support for 25 audio files per voice cloning
- Parameter validation with clear range guidance
- FastMCP compatible with sys.path modification pattern

---

## 1. elevenlabs-agents Server

### Current Resources (Already Good!)
- ✅ prompt_templates.json - 10 solid use cases
- ✅ voice_presets.json - 10 voice personalities  
- ✅ agent_templates.json - 10 complete agents

### Proposed Additions

#### A. Quick Start Templates (agent_quickstart.json)
Simple, focused agents that do one thing well:
```json
{
  "greeting_bot": {
    "description": "Just says hello and goodbye",
    "system_prompt": "Greet people warmly, ask how you can help, say goodbye politely",
    "first_message": "Hello! How can I help you today?"
  },
  "yes_no_qualifier": {
    "description": "Simple lead qualifier with yes/no questions",
    "system_prompt": "Ask 3 yes/no questions to qualify leads. Be brief.",
    "questions": ["Do you have a budget?", "Are you the decision maker?", "Do you need this within 30 days?"]
  }
}
```

#### B. Industry Verticals (industry_templates.json)
Keep it to top 5 most requested:
1. **Healthcare** - Appointment reminders, prescription refills
2. **Real Estate** - Property info, showing scheduler
3. **Restaurant** - Reservations, menu questions
4. **Education** - Student help desk, enrollment
5. **E-commerce** - Order status, returns

#### C. Voice Selection Helper (voice_matcher.json)
Simple mapping:
```json
{
  "need_professional": ["cgSgspJ2msm6clMCkdW9"],
  "need_friendly": ["21m00Tcm4TlvDq8ikWAM"],
  "need_energetic": ["yoZ06aMxZJJ28mfd3POQ"]
}
```

## 2. elevenlabs-knowledge Server

### Proposed Resources

#### A. Document Templates (document_templates.json)
How to structure docs for best results:
```json
{
  "faq_format": "Q: [Question]\nA: [Answer]\n---",
  "product_info": "Product: [Name]\nFeatures: [List]\nPrice: [Amount]\n---",
  "policy_format": "Policy: [Title]\nDetails: [Description]\nExceptions: [List]\n---"
}
```

#### B. Chunking Strategies (chunking_guide.json)
Simple rules:
- FAQs: One Q&A per chunk
- Products: One product per chunk  
- Policies: One section per chunk
- Articles: Paragraph-based (300-500 chars)

## 3. elevenlabs-conversations Server

### Proposed Resources

#### A. Analysis Templates (analysis_templates.json)
What to look for in conversations:
```json
{
  "satisfaction_indicators": ["thank you", "perfect", "great", "helpful"],
  "frustration_indicators": ["confused", "frustrated", "don't understand", "not working"],
  "escalation_triggers": ["speak to human", "manager", "supervisor", "real person"]
}
```

#### B. Export Formats (export_formats.json)
- CSV for spreadsheets
- JSON for developers
- Markdown for reports

## 4. elevenlabs-testing Server

### Proposed Resources

#### A. Test Scenarios (test_scenarios.json)
Common things to test:
```json
{
  "basic_flow": [
    {"user": "Hello", "expect": "greeting"},
    {"user": "I need help", "expect": "offer_assistance"},
    {"user": "Goodbye", "expect": "farewell"}
  ],
  "error_handling": [
    {"user": "", "expect": "prompt_for_input"},
    {"user": "askdjfhaskjdfh", "expect": "clarification"},
    {"user": "[silence]", "expect": "are_you_there"}
  ]
}
```

#### B. Performance Benchmarks (benchmarks.json)
- Response time: < 2 seconds
- Conversation completion: > 80%
- Error rate: < 5%

## 5. elevenlabs-integrations Server

### Proposed Resources

#### A. Webhook Patterns (webhook_patterns.json)
Common integrations:
```json
{
  "slack_notification": {
    "event": "conversation_completed",
    "url": "https://hooks.slack.com/...",
    "payload": {"text": "Conversation with {{customer}} completed"}
  },
  "crm_update": {
    "event": "lead_captured",
    "url": "https://crm.example.com/webhook",
    "payload": {"lead": "{{data}}"}
  }
}
```

#### B. Tool Configs (tool_configs.json)
Pre-configured tool setups:
- Weather lookup
- Calendar checking
- Database queries
- Email sending

## Next Steps for Each Server

### Phase 1 - Immediate Value (Do First)
1. **agents**: Add 5 industry templates
2. **knowledge**: Add FAQ and product templates
3. **testing**: Add basic test scenarios
4. **conversations**: Add export templates
5. **integrations**: Add webhook patterns

### Phase 2 - Enhanced Features (Do Next)
1. **agents**: Voice matcher tool
2. **knowledge**: Chunking strategies
3. **testing**: Performance benchmarks
4. **conversations**: Analysis templates
5. **integrations**: Tool configurations

### Phase 3 - Advanced (Later)
- Cross-server workflow templates
- Multi-agent orchestration patterns
- Advanced analytics dashboards

## Key Principles

1. **Start Small**: Each template should work immediately
2. **Real Use Cases**: Based on actual customer needs
3. **No Dependencies**: Templates work standalone
4. **Clear Documentation**: Each template has example usage
5. **Iterative**: Start with basics, enhance based on feedback

## Known Voice IDs (From Existing Code)

Popular voices we're already using:
- `cgSgspJ2msm6clMCkdW9` - Default professional voice
- `21m00Tcm4TlvDq8ikWAM` - Rachel (calm, female)  
- `yoZ06aMxZJJ28mfd3POQ` - Sam (young, male)
- `EXAVITQu4vr4xnSDxMaL` - Calm/soothing voice
- `MF3mGyEYCl7XYWbV9V6O` - Neutral voice
- `pNInz6obpgDQGcFmaJgB` - Adam (professional, male)

## Common Patterns We're Seeing

From existing templates:
1. **Temperature Settings**: 0.4-0.5 for factual, 0.6-0.7 for conversational, 0.8+ for creative
2. **Speed Settings**: 0.95 for slow/clear, 1.0 for normal, 1.05-1.1 for energetic
3. **Stability**: 0.8-0.9 for consistent, 0.3-0.5 for expressive
4. **First Messages**: Always short, friendly, and action-oriented

## Practical Implementation Plan

### What to Build First (MVP)

1. **elevenlabs-agents**: Add 3 new files
   - `mini_agents.json` - 10 one-liner agents for quick setup
   - `industry_basics.json` - 5 industry templates (healthcare, real estate, restaurant, education, ecommerce)
   - `conversation_flows.json` - 5 common conversation patterns

2. **elevenlabs-knowledge**: Add 2 new files
   - `document_formats.json` - How to structure FAQs, products, policies
   - `chunking_guide.json` - Best practices for different content types

3. **elevenlabs-testing**: Add 1 new file
   - `test_library.json` - 10 ready-to-use test scenarios

4. **elevenlabs-conversations**: Keep simple, use existing tools
   - Just document how to use export and analysis features

5. **elevenlabs-integrations**: Add 1 new file
   - `webhook_templates.json` - 5 common webhook patterns

### Resource File Structure (Simplified)

Each server keeps existing structure, just add to resources/:
```
src/resources/
├── existing_files.json     # Don't touch these
└── new_templates.json      # Add our new templates here
```

## Template Validation

Each template should have:
- `name`: Clear, descriptive name
- `description`: What it does
- `use_case`: When to use it
- `config`: The actual configuration
- `example`: Sample usage
- `tags`: For searching

## Simplification Rules

1. If it needs more than 3 steps, it's too complex
2. If it needs external data, provide mock data
3. If it needs customization, provide sensible defaults
4. If it could fail, provide fallback behavior
5. If it's unclear, add an example

## Testing Each Template

Before including a template:
1. Does it work with default settings?
2. Is the purpose immediately clear?
3. Can a non-technical user understand it?
4. Does it solve a real problem?
5. Is it better than starting from scratch?

## Specific Template Ideas

### For elevenlabs-agents

#### Mini Templates (one_liner_agents.json)
```json
{
  "answering_machine": {
    "system_prompt": "You're an answering machine. Take a message with name and number.",
    "first_message": "You've reached our office. Please leave your name and number."
  },
  "availability_checker": {
    "system_prompt": "Check if the caller is free on Tuesday or Thursday at 2pm.",
    "first_message": "Hi! I'm calling to schedule your appointment. Are you free Tuesday or Thursday at 2pm?"
  }
}
```

#### Conversation Flows (conversation_flows.json)
```json
{
  "three_question_qualifier": {
    "flow": [
      "Ask about their biggest challenge",
      "Ask about their timeline", 
      "Ask about their budget range"
    ]
  },
  "appointment_flow": {
    "flow": [
      "Greet and ask what service they need",
      "Suggest 2-3 time slots",
      "Confirm and get contact info"
    ]
  }
}
```

### For elevenlabs-knowledge

#### Content Structures (content_structures.json)
```json
{
  "simple_faq": {
    "format": "Question: {q}\nAnswer: {a}\n\n",
    "example": "Question: What are your hours?\nAnswer: We're open 9-5 Monday through Friday.\n\n"
  },
  "product_sheet": {
    "format": "PRODUCT: {name}\nPRICE: {price}\nFEATURES: {features}\n\n",
    "example": "PRODUCT: Basic Plan\nPRICE: $10/month\nFEATURES: 100 calls, email support\n\n"
  }
}
```

### For elevenlabs-testing

#### Quick Tests (quick_tests.json)
```json
{
  "smoke_test": [
    {"say": "Hello", "expect_contains": ["hi", "hello", "greet"]},
    {"say": "Goodbye", "expect_contains": ["bye", "farewell", "later"]}
  ],
  "confusion_test": [
    {"say": "ajsdkfjaksd", "expect_contains": ["understand", "clarify", "repeat"]},
    {"say": "", "expect_contains": ["there", "hello", "speak"]}
  ]
}
```

### For elevenlabs-conversations

#### Analysis Queries (analysis_queries.json)
```json
{
  "find_frustrated": {
    "keywords": ["frustrated", "annoyed", "doesn't work", "broken"],
    "action": "Flag for review"
  },
  "find_successful": {
    "keywords": ["thank you", "perfect", "solved", "great"],
    "action": "Mark as successful"
  }
}
```

### For elevenlabs-integrations

#### Simple Webhooks (simple_webhooks.json)
```json
{
  "email_on_complete": {
    "trigger": "conversation_ended",
    "action": "Send email with transcript"
  },
  "log_to_spreadsheet": {
    "trigger": "lead_captured",
    "action": "Add row to Google Sheet"
  }
}
```

## Summary - What We're Actually Building

### Immediate Additions (7 new files total)

1. **elevenlabs-agents/src/resources/**
   - `mini_agents.json` - Ultra-simple, one-line agents
   - `industry_basics.json` - Top 5 industries
   - `conversation_flows.json` - Common patterns

2. **elevenlabs-knowledge/src/resources/**
   - `document_formats.json` - Structure templates
   - `chunking_guide.json` - Best practices

3. **elevenlabs-testing/src/resources/**
   - `test_library.json` - Ready-to-use tests

4. **elevenlabs-integrations/src/resources/**
   - `webhook_templates.json` - Common integrations

### Why This Approach Works

- **Minimal Changes**: Just adding resource files, no code changes
- **Immediate Value**: Users can copy-paste and go
- **Real Use Cases**: Based on existing patterns that work
- **No Complexity**: Simple JSON files with examples
- **Backwards Compatible**: Doesn't break anything existing

### Next Actions

1. Create the 7 JSON files with templates
2. Test each template with actual API calls
3. Add one README per server explaining the new resources
4. Ship it!

### What We're NOT Doing (Keeping it Simple)

- ❌ No complex workflow engines
- ❌ No external dependencies  
- ❌ No new API endpoints
- ❌ No database schemas
- ❌ No authentication changes
- ❌ No breaking changes

Just simple, useful templates that work.