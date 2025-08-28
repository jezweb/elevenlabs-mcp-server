# Audio Preview Handling Notes

## Current Implementation
- Voice design returns only metadata (generated_voice_id, description, audio_size)
- Base64 audio data is omitted to prevent token overflow
- Users select voice based on description and create it using the ID

## Limitations for Cloud MCP Servers
1. **No direct file serving**: Cloud MCP servers can't provide public HTTP URLs
2. **No preview URLs from API**: ElevenLabs doesn't provide playable preview URLs
3. **Resources are programmatic**: MCP resources are accessed by AI, not clickable for users

## Why Current Approach is Optimal
- Avoids token limits (audio previews can be 1.6MB+)
- Works reliably in cloud environment
- Simple implementation without complex file handling
- Users can still create voices using the generated IDs

## Alternative Considered
Could implement MCP resources to store audio in memory, but:
- Still wouldn't provide clickable links
- Adds complexity without user benefit
- Resources would be AI-accessible only

## Conclusion
The current implementation (returning only IDs and metadata) is the most practical solution for cloud-deployed MCP servers.