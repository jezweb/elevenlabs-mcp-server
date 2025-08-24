# ElevenLabs API Endpoints Research

## Current Known Endpoints (From Existing Code)

### Agent Management
- **GET** `/convai/convai/agents` - List all agents
- **GET** `/convai/convai/agents/{agent_id}` - Get specific agent
- **POST** `/convai/convai/agents` - Create new agent
- **PATCH** `/convai/convai/agents/{agent_id}` - Update agent
- **DELETE** `/convai/convai/agents/{agent_id}` - Delete agent

### Conversation Management
- **GET** `/convai/conversations` - List conversations
- **GET** `/convai/conversations/{conversation_id}` - Get conversation details
- **GET** `/convai/conversations/{conversation_id}/transcript` - Get transcript
- **POST** `/convai/convai/simulations` - Simulate conversation

### Knowledge Base
- **GET** `/convai/knowledge_base` - List knowledge bases
- **POST** `/convai/knowledge_base` - Add document
- **DELETE** `/convai/knowledge_base/{document_id}` - Delete document

## Discovered/Inferred Endpoints for New Tools

### 1. Clone Agent Implementation
**Required Endpoints:**
```
GET /convai/convai/agents/{agent_id}
- Purpose: Fetch complete agent configuration
- Returns: Full agent object with all settings

POST /convai/convai/agents
- Purpose: Create new agent with cloned data
- Payload: Modified agent configuration
```

### 2. Bulk Operations
**Potential Endpoints:**
```
PATCH /convai/convai/agents/bulk
- May not exist, might need to iterate
- Alternative: Loop through individual PATCH requests

GET /convai/convai/agents?ids={id1,id2,id3}
- Query multiple agents at once
- Alternative: Individual GET requests
```

### 3. Agent Metrics/Analytics
**Likely Endpoints:**
```
GET /convai/convai/agents/{agent_id}/analytics
- Purpose: Get usage statistics
- Parameters: date_from, date_to, granularity

GET /convai/convai/agents/{agent_id}/metrics
- Purpose: Get performance metrics
- Returns: call_count, avg_duration, success_rate

GET /convai/conversations/stats?agent_id={agent_id}
- Purpose: Aggregate conversation statistics
- Alternative source for metrics
```

### 4. Business Hours/Scheduling
**Configuration via Platform Settings:**
```
PATCH /convai/convai/agents/{agent_id}
- Payload includes platform_settings.widget.business_hours
- Structure:
  {
    "platform_settings": {
      "widget": {
        "business_hours": {
          "timezone": "America/New_York",
          "schedule": {
            "monday": {"start": "09:00", "end": "17:00"},
            ...
          },
          "offline_message": "We're currently closed..."
        }
      }
    }
  }
```

### 5. Backup/Export
**Composite Operations:**
```
GET /convai/convai/agents/{agent_id}
- Full agent configuration

GET /convai/knowledge_base?agent_id={agent_id}
- Associated knowledge bases

GET /convai/convai/agents/{agent_id}/widgets
- Widget configurations (if separate endpoint)
```

### 6. Voice Management
**From ElevenLabs Voice API:**
```
GET /voices
- List available voices

GET /voices/{voice_id}
- Get voice details

GET /voices/shared
- Get community/shared voices
```

## Payload Structures

### Agent Creation Payload
```json
{
  "name": "Agent Name",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "System prompt text"
      },
      "first_message": "Greeting message",
      "language": "en"
    },
    "tts": {
      "voice_id": "voice_id_here",
      "model_id": "eleven_turbo_v2",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "use_speaker_boost": false
      },
      "pronunciation_dictionary": {}
    },
    "llm": {
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 150
    },
    "stt": {
      "model": "whisper",
      "language": "en"
    }
  },
  "platform_settings": {
    "widget": {
      "variant": "compact",
      "avatar": {
        "type": "default"
      }
    }
  }
}
```

### Conversation Simulation Payload
```json
{
  "agent_id": "agent_xxx",
  "simulation_specification": {
    "num_conversations": 1,
    "conversation_specification": {
      "agent_actions": [{
        "type": "user_input",
        "input": "Test message"
      }]
    }
  }
}
```

### Knowledge Base Addition Payload
```json
{
  "agent_id": "agent_xxx",
  "name": "Document name",
  "type": "text",
  "content": "Document content...",
  "metadata": {
    "source": "manual",
    "category": "faq"
  }
}
```

## Authentication Headers
```python
headers = {
    "xi-api-key": "your_api_key",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

## Rate Limiting Considerations
- Likely rate limits: 100-1000 requests/minute
- Bulk operations should implement batching
- Use exponential backoff for retries
- Cache frequently accessed data (5-minute TTL)

## Error Response Patterns
```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID xxx not found",
    "status": 404
  }
}
```

Common error codes:
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (invalid API key)
- 403: Forbidden (no access to resource)
- 404: Not Found (resource doesn't exist)
- 429: Too Many Requests (rate limited)
- 500: Internal Server Error

## Testing Strategy

### 1. Endpoint Discovery
```python
# Try common patterns
endpoints_to_test = [
    "/convai/convai/agents/{id}/metrics",
    "/convai/convai/agents/{id}/analytics",
    "/convai/convai/agents/{id}/stats",
    "/convai/convai/agents/bulk",
    "/convai/metrics/agents/{id}"
]
```

### 2. Response Validation
```python
# Check response structure
expected_fields = {
    "agent": ["agent_id", "name", "conversation_config"],
    "conversation": ["conversation_id", "agent_id", "started_at"],
    "metrics": ["total_calls", "avg_duration", "success_rate"]
}
```

### 3. Error Handling
```python
# Graceful degradation
if endpoint_not_found:
    use_alternative_method()
    log_for_future_implementation()
```

## Implementation Priority

### High Confidence (Existing Endpoints)
1. Clone agent - Uses GET + POST agents
2. Bulk updates - Uses PATCH in loop
3. Backup/restore - Uses GET agents + knowledge

### Medium Confidence (Likely Exists)
4. Business hours - Via platform_settings
5. Fallback responses - Via conversation_config
6. Voice management - Standard ElevenLabs API

### Low Confidence (May Need Alternative)
7. Direct metrics endpoint - May need to calculate from conversations
8. Bulk operations endpoint - May need to implement client-side
9. Advanced analytics - May need custom aggregation

## Notes for Implementation

1. **Always check API documentation first** - ElevenLabs may have updated docs
2. **Test with small datasets** - Avoid rate limiting during development
3. **Implement caching** - Reduce API calls for frequently accessed data
4. **Use existing client methods** - Leverage shared/client.py patterns
5. **Handle missing endpoints gracefully** - Provide alternative implementations
6. **Log unknown responses** - Help identify new fields/capabilities