# ElevenLabs API Endpoints Reference

## Base URL
`https://api.elevenlabs.io`

## Authentication
All requests require the `xi-api-key` header with your API key.

## API Endpoints

### Text to Speech (4 endpoints)
1. `POST /v1/text-to-speech/{voice_id}` - Convert text to speech
2. `POST /v1/text-to-speech/{voice_id}/stream` - Stream text to speech
3. `POST /v1/text-to-speech/{voice_id}/with-timestamps` - TTS with word timestamps
4. `POST /v1/text-to-speech/{voice_id}/stream/with-timestamps` - Stream with timestamps

### Speech to Speech (2 endpoints)
5. `POST /v1/speech-to-speech/{voice_id}` - Transform audio to different voice
6. `POST /v1/speech-to-speech/{voice_id}/stream` - Stream speech transformation

### Voice Management (8 endpoints)
7. `GET /v1/voices` - List all voices
8. `GET /v1/voices/{voice_id}` - Get voice details
9. `POST /v1/voices/add` - Add custom voice (cloning)
10. `PATCH /v1/voices/{voice_id}/edit` - Edit voice
11. `DELETE /v1/voices/{voice_id}` - Delete voice
12. `GET /v1/voices/{voice_id}/settings` - Get voice settings
13. `PATCH /v1/voices/{voice_id}/settings/edit` - Update voice settings
14. `POST /v1/voices/add/{public_user_id}/{voice_id}` - Add from library

### Voice Library (1 endpoint)
15. `GET /v1/shared-voices` - Browse voice library

### Voice Design / Text to Voice (2 endpoints)
16. `POST /v1/text-to-voice/create-previews` - Generate voice previews
17. `POST /v1/text-to-voice/create-voice-from-preview` - Save generated voice

### Models (1 endpoint)
18. `GET /v1/models` - List available models

### Audio Processing (5 endpoints)
19. `POST /v1/audio-isolation` - Isolate speech from background
20. `POST /v1/sound-generation` - Generate sound effects
21. `POST /v1/dubbing` - Video dubbing
22. `POST /v1/audio-native` - Audio native processing
23. `POST /v1/transcribe` - Transcribe audio to text (Speech to Text)

### Conversational AI - Agents (6 endpoints)
24. `GET /v1/convai/agents` - List agents
25. `POST /v1/convai/agents` - Create agent
26. `GET /v1/convai/agents/{agent_id}` - Get agent
27. `PATCH /v1/convai/agents/{agent_id}` - Update agent
28. `DELETE /v1/convai/agents/{agent_id}` - Delete agent
29. `POST /v1/convai/agents/{agent_id}/duplicate` - Duplicate agent

### Conversational AI - Conversations (5 endpoints)
30. `GET /v1/convai/conversations` - List conversations
31. `GET /v1/convai/conversations/{conversation_id}` - Get conversation
32. `DELETE /v1/convai/conversations/{conversation_id}` - Delete conversation
33. `GET /v1/convai/conversations/{conversation_id}/audio` - Get audio
34. `POST /v1/convai/conversations/{conversation_id}/feedback` - Send feedback

### Conversational AI - Knowledge Base (4 endpoints)
35. `GET /v1/convai/knowledge-base` - List documents
36. `POST /v1/convai/knowledge-base` - Add document
37. `GET /v1/convai/knowledge-base/{document_id}` - Get document
38. `DELETE /v1/convai/knowledge-base/{document_id}` - Delete document

### Conversational AI - Phone Numbers (4 endpoints)
39. `GET /v1/convai/phone-numbers` - List phone numbers
40. `POST /v1/convai/phone-numbers` - Import number
41. `PATCH /v1/convai/phone-numbers/{phone_number_id}` - Update number
42. `DELETE /v1/convai/phone-numbers/{phone_number_id}` - Delete number

### Conversational AI - Calling (3 endpoints)
43. `POST /v1/convai/call/sip` - SIP trunk outbound call
44. `POST /v1/convai/call/twilio` - Twilio outbound call
45. `POST /v1/convai/batch-calling` - Batch calling

### Account & Usage (7 endpoints)
46. `GET /v1/user` - Get user info
47. `GET /v1/user/subscription` - Get subscription details
48. `GET /v1/usage/character-stats` - Character usage stats
49. `GET /v1/history` - Generation history
50. `GET /v1/history/{history_item_id}` - Get history item
51. `GET /v1/history/{history_item_id}/audio` - Download audio
52. `DELETE /v1/history/{history_item_id}` - Delete history item

### Projects (5 endpoints)
53. `GET /v1/projects` - List projects
54. `POST /v1/projects` - Create project
55. `GET /v1/projects/{project_id}` - Get project
56. `PATCH /v1/projects/{project_id}` - Update project
57. `DELETE /v1/projects/{project_id}` - Delete project

### Pronunciation Dictionaries (4 endpoints)
58. `GET /v1/pronunciation-dictionaries` - List dictionaries
59. `POST /v1/pronunciation-dictionaries` - Create dictionary
60. `GET /v1/pronunciation-dictionaries/{dictionary_id}` - Get dictionary
61. `DELETE /v1/pronunciation-dictionaries/{dictionary_id}` - Delete dictionary

### Workspace (5 endpoints)
62. `GET /v1/workspace` - Get workspace info
63. `PATCH /v1/workspace` - Update workspace
64. `GET /v1/workspace/members` - List members
65. `POST /v1/workspace/invites` - Send invite
66. `DELETE /v1/workspace/members/{member_id}` - Remove member

## Additional Endpoints (May exist but not fully documented)
- Widget endpoints
- Tools management for agents
- Secrets management
- MCP server endpoints
- LLM usage calculation
- WebSocket endpoints for real-time communication
- Webhook configuration endpoints
- Service account management

## Summary

**Total Documented Endpoints: 66**

### Breakdown by Category:
- Text to Speech: 4
- Speech to Speech: 2
- Voice Management: 8
- Voice Library: 1
- Voice Design: 2
- Models: 1
- Audio Processing: 5
- Conversational AI - Agents: 6
- Conversational AI - Conversations: 5
- Conversational AI - Knowledge Base: 4
- Conversational AI - Phone Numbers: 4
- Conversational AI - Calling: 3
- Account & Usage: 7
- Projects: 5
- Pronunciation Dictionaries: 4
- Workspace: 5

## Authentication Example

```bash
curl -X GET https://api.elevenlabs.io/v1/voices \
  -H "xi-api-key: YOUR_API_KEY"
```

## SDK Support
- Python: `elevenlabs` package
- Node.js: `elevenlabs` package
- JavaScript/TypeScript: Browser and Node support

## Rate Limits
Rate limits vary by subscription tier. Check the `X-RateLimit-*` headers in responses for current limits.

## Response Formats
- JSON for metadata and configuration endpoints
- Audio binary data (MP3, PCM, etc.) for audio generation endpoints
- WebSocket for real-time streaming endpoints

## Error Codes
- 400: Bad Request
- 401: Unauthorized (invalid API key)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 429: Too Many Requests (rate limited)
- 500: Internal Server Error

## Notes
- Voice IDs are required for most audio generation endpoints
- Some endpoints support streaming for real-time applications
- The Conversational AI features are newer and may have additional undocumented endpoints
- Enterprise customers may have access to additional endpoints not listed here