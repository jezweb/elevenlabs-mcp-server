# ElevenLabs Voices MCP Server

Voice resource management server for ElevenLabs Conversational AI platform.

## Overview

This MCP server provides comprehensive voice management capabilities:
- **Voice CRUD**: Create, read, update, and delete voice operations
- **Text-to-Voice**: Generate voices from text descriptions
- **Instant Voice Cloning (IVC)**: Clone voices from audio samples
- **Voice Library**: Search and add voices from the public library
- **Voice Settings**: Configure voice generation parameters

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Add your ELEVENLABS_API_KEY to .env
   ```

3. **Run the server**:
   ```bash
   python src/server.py
   ```

## Available Tools

### Voice Management
- `get_voice_details(voice_id)` - Get detailed voice information
- `list_user_voices(page_size)` - List all user voices
- `delete_user_voice(voice_id)` - Delete a voice

### Voice Design
- `design_voice_from_text(description, text)` - Create voice previews from description
- `create_voice_from_design(generated_voice_id, name, description)` - Make preview permanent

### Voice Cloning
- `clone_voice_instantly(name, audio_files, description)` - Clone voice from audio samples

### Voice Library
- `search_public_voices(query, page, page_size)` - Search public voice library
- `add_public_voice(voice_id, name, description)` - Add shared voice to collection
- `get_public_voices()` - Browse available shared voices

### Voice Settings
- `configure_voice_settings(voice_id, stability, similarity_boost, style, use_speaker_boost)` - Update voice settings
- `get_voice_configuration(voice_id)` - Get current voice settings

## Environment Variables

- `ELEVENLABS_API_KEY` - Your ElevenLabs API key (required)
- `LOG_LEVEL` - Logging level (optional, default: INFO)
- `API_TIMEOUT` - API timeout in seconds (optional, default: 30)

## Voice Settings Guide

- **Stability (0.0-1.0)**:
  - 0.0-0.3: Expressive, variable
  - 0.4-0.7: Balanced (recommended)
  - 0.8-1.0: Consistent, stable

- **Similarity Boost (0.0-1.0)**:
  - 0.0-0.3: Creative interpretation
  - 0.4-0.7: Natural variation
  - 0.8-1.0: Strict voice matching

- **Style (0.0-1.0)**:
  - 0.0: Natural speech
  - 0.5: Moderate style enhancement
  - 1.0: Maximum style exaggeration

## Audio File Support

For voice cloning, supported formats:
- WAV, MP3, FLAC, M4A, OGG, WEBM
- 1-5 minutes total duration recommended
- High quality audio with minimal background noise
- Maximum 25 files per voice

## API Endpoints Used

- Voice Management: `/voices`, `/voices/{voice_id}`
- Voice Design: `/text-to-voice`, `/text-to-voice/create-voice`
- Voice Cloning: `/voices/add`
- Voice Library: `/shared-voices`, `/voices/add-shared`
- Voice Settings: `/voices/{voice_id}/settings`

## Error Handling

All tools return structured responses with:
- Success status and message
- Detailed error information
- Helpful suggestions for resolution
- Input validation with clear feedback