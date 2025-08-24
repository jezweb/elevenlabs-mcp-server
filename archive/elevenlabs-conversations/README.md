# ElevenLabs Conversations MCP Server

Manage conversation history and playback for ElevenLabs conversational AI agents.

## Features

- **Conversation Management**: List, retrieve, and delete conversation records
- **Transcript Access**: Extract conversation transcripts for analysis
- **Feedback System**: Submit ratings and feedback for conversations
- **Audio Playback**: Generate download URLs and signed playback links
- **Analytics**: Analyze conversations and generate performance reports
- **Data Export**: Export conversation data in JSON or CSV formats

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Add your ElevenLabs API key:
   ```
   ELEVENLABS_API_KEY=your_api_key_here
   ```

## Usage

### Run the server

```bash
python src/server.py
```

### Test the server

```bash
python src/server.py --test
```

## Available Tools

### Core Conversation Tools

- `list_conversations`: Browse conversation history with filtering
- `get_conversation`: Get detailed conversation data including transcript
- `get_transcript`: Extract conversation transcript text
- `delete_conversation`: Remove conversation records
- `send_feedback`: Submit ratings and feedback

### Playback Tools

- `get_conversation_audio`: Get audio download URL (MP3/WAV)
- `get_signed_url`: Generate secure playback URL with TTL

### Analytics Tools

- `analyze_conversation`: Get conversation insights and metrics
- `performance_report`: Generate agent performance reports
- `export_conversations`: Export data in JSON or CSV format

## Examples

### List Recent Conversations

```python
await list_conversations(limit=10)
```

### Get Conversation Details

```python
await get_conversation("conv_abc123")
```

### Generate Performance Report

```python
await performance_report(
    agent_id="agent_xyz789",
    days=7
)
```

### Export Conversations

```python
await export_conversations(
    agent_id="agent_xyz789",
    format="csv",
    limit=50
)
```

## Environment Variables

- `ELEVENLABS_API_KEY`: Your ElevenLabs API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `API_TIMEOUT`: API request timeout in seconds (default: 30)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
- `MAX_RETRIES`: Maximum retry attempts for API calls (default: 3)

## Error Handling

All tools return consistent error responses with helpful suggestions:

```json
{
  "success": false,
  "error": "Invalid conversation ID format",
  "suggestion": "Use format: conv_XXXX"
}
```

## License

MIT