# ElevenLabs Audio Server Architecture

## Overview
The `elevenlabs-audio` MCP server focuses on audio content generation and processing, including text-to-speech, speech-to-text, dialogue creation, music generation, sound effects, and audio processing utilities. This server uses voices (managed by the voices server) to generate audio content.

## Modular Structure

Following the FastMCP structured template pattern for better organization and maintainability:

```
elevenlabs-audio/
├── src/
│   ├── server.py                 # Main entry point, registers all tools
│   ├── utils.py                  # Self-contained utilities
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tts_tools.py         # Text-to-speech operations
│   │   ├── stt_tools.py         # Speech-to-text operations  
│   │   ├── dialogue_tools.py    # Multi-voice dialogue creation
│   │   ├── music_tools.py       # Music generation and composition
│   │   ├── effects_tools.py     # Sound effects generation
│   │   ├── voice_changer_tools.py # Voice transformation (speech-to-speech)
│   │   ├── audio_processing_tools.py # Audio isolation and processing
│   │   └── dubbing_tools.py     # Dubbing and audio native projects
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── audio_files.py       # Generated audio file resources
│   │   └── transcripts.py       # Transcription result resources
│   └── handlers/
│       ├── __init__.py
│       └── streaming.py         # WebSocket streaming handlers
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### 1. Text-to-Speech (TTS)

#### Standard TTS
- **Endpoint**: `POST /v1/text-to-speech/{voice_id}`
- **Description**: Converts text into speech using a specified voice
- **Parameters**:
  - `voice_id` (path, required): Voice identifier
  - `text` (body, required): Text to convert (max 5000 chars)
  - `model_id` (body, optional): TTS model selection
  - `output_format` (body, optional): Audio format (mp3_44100_128, pcm_16000, etc.)
  - `voice_settings` (body, optional):
    - `stability`: 0.0-1.0
    - `similarity_boost`: 0.0-1.0
    - `style`: 0.0-1.0
    - `use_speaker_boost`: boolean
  - `seed` (body, optional): For reproducible results
  - `previous_text` (body, optional): Context for better pronunciation
  - `next_text` (body, optional): Context for better pronunciation
  - `language_code` (body, optional): ISO 639-1 code
  - `pronunciation_dictionary_locators` (body, optional): Array of dictionary IDs

#### Streaming TTS
- **Endpoint**: `POST /v1/text-to-speech/{voice_id}/stream`
- **Description**: Real-time streaming text-to-speech
- **Parameters**: Same as standard TTS
- **Additional**:
  - `optimize_streaming_latency` (body, optional): 0-4, lower = faster
  - `chunk_length_schedule` (body, optional): Array of chunk sizes

#### TTS with Timestamps
- **Endpoint**: `POST /v1/text-to-speech/{voice_id}/with-timestamps`
- **Description**: Returns audio with character-level timing information
- **Response**: Audio stream + alignment JSON with character positions

### 2. Speech-to-Text (STT)

#### Transcription
- **Endpoint**: `POST /v1/speech-to-text`
- **Description**: Transcribe audio/video files with optional speaker diarization
- **Parameters**:
  - `model_id` (body, required): "scribe_v1" or "scribe_v1_experimental"
  - `file` (body, optional): Audio/video file (multipart/form-data)
  - `url` (body, optional): URL to audio/video file
  - `language_code` (body, optional): Expected language (ISO 639-3)
  - `num_speakers` (body, optional): Max number of speakers (1-32)
  - `diarize` (body, optional): Enable speaker identification
  - `webhook` (body, optional): Callback URL for async processing
  - `translation_config` (body, optional):
    - `target_languages`: Array of target language codes
- **Response**:
  ```json
  {
    "text": "transcribed text",
    "chunks": [
      {
        "text": "word",
        "start_time": 0.0,
        "end_time": 0.5,
        "speaker": 1
      }
    ],
    "language_probability": {
      "en": 0.95
    }
  }
  ```

### 3. Voice Changer

#### Voice Transformation
- **Endpoint**: `POST /v1/voice-generation/voice-changer`
- **Description**: Transform audio from one voice to another
- **Parameters**:
  - `voice_id` (body, required): Target voice ID
  - `audio` (body, required): Source audio file
  - `model_id` (body, optional): Model selection
  - `voice_settings` (body, optional): Same as TTS
  - `output_format` (body, optional): Audio format
  - `remove_background_noise` (body, optional): boolean

#### Streaming Voice Transformation
- **Endpoint**: `POST /v1/voice-generation/voice-changer/stream`
- **Description**: Real-time voice transformation
- **Parameters**: Same as standard voice changer

### 4. Sound Effects Generation

#### Generate Sound Effects
- **Endpoint**: `POST /v1/sound-generation`
- **Description**: Generate sound effects from text descriptions
- **Parameters**:
  - `text` (body, required): Description of desired sound
  - `duration_seconds` (body, optional): Length of sound (0.5-22.0)
  - `prompt_influence` (body, optional): 0.0-1.0, text adherence

### 5. Music Generation

#### Generate Music
- **Endpoint**: `POST /v1/music`
- **Description**: Generate music from text prompts or composition plans
- **Parameters**:
  - `prompt` (body, optional): Text description (max 2000 chars)
  - `composition_plan` (body, optional): Structured music plan
  - `music_length_milliseconds` (body, optional): 10-300000 ms
  - `model_id` (body, optional): Music generation model
  - `output_format` (body, optional): Audio format

### 6. Multi-Voice Dialogue

#### Generate Dialogue
- **Endpoint**: `POST /v1/text-to-dialogue`
- **Description**: Generate multi-speaker dialogue
- **Parameters**:
  - `dialogue` (body, required): Array of:
    ```json
    {
      "text": "Speaker text",
      "voice_id": "voice_identifier",
      "voice_settings": {...}
    }
    ```
  - `model_id` (body, optional): TTS model
  - `output_format` (body, optional): Audio format

#### Streaming Dialogue
- **Endpoint**: `POST /v1/text-to-dialogue/stream`
- **Description**: Real-time multi-voice dialogue generation

### 7. Audio Utilities

#### Audio Isolation
- **Endpoint**: `POST /v1/audio-isolation`
- **Description**: Remove background noise from audio
- **Parameters**:
  - `audio` (body, required): Audio file with background noise
- **Response**: Cleaned audio stream

#### Audio Isolation (Streaming)
- **Endpoint**: `POST /v1/audio-isolation/stream`
- **Description**: Real-time background noise removal

### 8. Dubbing & Audio Native

#### Create Audio Native Project
- **Endpoint**: `POST /v1/audio-native`
- **Description**: Create a new audio native enabled project
- **Parameters**:
  - `name` (body, required): Project name
  - `file` (body, required): Audio/video file
  - `target_languages` (body, optional): Languages for dubbing

#### Get Audio Native Project Settings
- **Endpoint**: `GET /v1/audio-native/{project_id}`
- **Description**: Get project configuration and status
- **Parameters**:
  - `project_id` (path, required): Project identifier

#### Update Audio Native Project
- **Endpoint**: `POST /v1/audio-native/{project_id}`
- **Description**: Update project settings or add files
- **Parameters**:
  - `project_id` (path, required): Project identifier
  - `settings` (body, optional): Updated configuration

## Modular Tool Implementations

### Tool Module Organization

Tools are organized into focused modules for better maintainability:

#### 1. TTS Tools Module (`tts_tools.py`)
```python
# Text-to-speech operations
async def text_to_speech(
    text: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True,
    language_code: Optional[str] = None,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Generate speech from text."""

async def streaming_tts(
    text: str,
    voice_id: str,
    optimize_streaming_latency: int = 2,
    chunk_length_schedule: Optional[List[int]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Stream text-to-speech in real-time."""

async def tts_with_timestamps(
    text: str,
    voice_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Generate speech with character-level timing."""
```

#### 2. STT Tools Module (`stt_tools.py`)
```python
# Speech-to-text operations
async def speech_to_text(
    audio_file_path: str,
    model_id: str = "scribe_v1",
    language_code: Optional[str] = None,
    diarize: bool = False,
    num_speakers: Optional[int] = None,
    translation_languages: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Transcribe audio to text."""

async def transcribe_from_url(
    audio_url: str,
    **kwargs
) -> Dict[str, Any]:
    """Transcribe audio from URL."""

async def batch_transcribe(
    audio_files: List[str],
    **kwargs
) -> Dict[str, Any]:
    """Batch transcribe multiple files."""
```

#### 3. Dialogue Tools Module (`dialogue_tools.py`)
```python
# Multi-voice dialogue creation
async def generate_dialogue(
    dialogue_script: List[Dict[str, str]],
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Generate multi-speaker dialogue."""

async def streaming_dialogue(
    dialogue_script: List[Dict[str, str]],
    **kwargs
) -> Dict[str, Any]:
    """Stream multi-voice dialogue generation."""
```

#### 4. Music Tools Module (`music_tools.py`)
```python
# Music generation and composition
async def generate_music(
    prompt: str,
    duration_seconds: float = 30.0,
    composition_plan: Optional[Dict] = None,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Generate music from text prompt."""

async def stream_music(
    prompt: str,
    **kwargs
) -> Dict[str, Any]:
    """Stream music generation."""

async def create_composition_plan(
    description: str,
    style: Optional[str] = None,
    instruments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create detailed composition plan."""
```

#### 5. Effects Tools Module (`effects_tools.py`)
```python
# Sound effects generation
async def generate_sound_effect(
    description: str,
    duration_seconds: float = 5.0,
    prompt_influence: float = 0.5,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Generate sound effects from text description."""
```

#### 6. Voice Changer Tools Module (`voice_changer_tools.py`)
```python
# Voice transformation (speech-to-speech)
async def transform_voice(
    audio_file_path: str,
    target_voice_id: str,
    remove_background_noise: bool = False,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Transform audio from one voice to another."""

async def streaming_voice_transform(
    audio_stream: Any,
    target_voice_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Real-time voice transformation."""
```

#### 7. Audio Processing Tools Module (`audio_processing_tools.py`)
```python
# Audio processing utilities
async def remove_background_noise(
    audio_file_path: str,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Remove background noise from audio."""

async def streaming_noise_removal(
    audio_stream: Any,
    **kwargs
) -> Dict[str, Any]:
    """Real-time background noise removal."""
```

#### 8. Dubbing Tools Module (`dubbing_tools.py`)
```python
# Dubbing and audio native projects
async def create_audio_native_project(
    name: str,
    file_path: str,
    target_languages: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create audio native enabled project."""

async def get_project_settings(
    project_id: str
) -> Dict[str, Any]:
    """Get project configuration and status."""

async def update_project(
    project_id: str,
    settings: Optional[Dict] = None,
    add_file: Optional[str] = None
) -> Dict[str, Any]:
    """Update project settings or add files."""
```

### Tool Registration in server.py

```python
# src/server.py
from fastmcp import FastMCP
from utils import Config

# Initialize server
mcp = FastMCP(
    name="elevenlabs-audio",
    version="1.0.0"
)

# Import tool modules
from tools import (
    # TTS tools
    text_to_speech,
    streaming_tts,
    tts_with_timestamps,
    
    # STT tools
    speech_to_text,
    transcribe_from_url,
    batch_transcribe,
    
    # Dialogue tools
    generate_dialogue,
    streaming_dialogue,
    
    # Music tools
    generate_music,
    stream_music,
    create_composition_plan,
    
    # Effects tools
    generate_sound_effect,
    
    # Voice changer tools
    transform_voice,
    streaming_voice_transform,
    
    # Audio processing tools
    remove_background_noise,
    streaming_noise_removal,
    
    # Dubbing tools
    create_audio_native_project,
    get_project_settings,
    update_project
)

# Register all tools
for tool in [
    text_to_speech, streaming_tts, tts_with_timestamps,
    speech_to_text, transcribe_from_url, batch_transcribe,
    generate_dialogue, streaming_dialogue,
    generate_music, stream_music, create_composition_plan,
    generate_sound_effect,
    transform_voice, streaming_voice_transform,
    remove_background_noise, streaming_noise_removal,
    create_audio_native_project, get_project_settings, update_project
]:
    mcp.tool(tool)
```

## Resources

The server exposes audio files as resources:

```python
@mcp.resource("audio://{file_id}")
async def get_audio_file(file_id: str) -> Resource:
    """Retrieve generated audio file."""

@mcp.resource("transcript://{transcript_id}")
async def get_transcript(transcript_id: str) -> Resource:
    """Retrieve transcription results."""
```

## Self-Contained Utils Module

The `utils.py` file contains all shared utilities following the FastMCP structured pattern:

```python
# src/utils.py
"""Self-contained utilities for ElevenLabs Audio MCP Server"""

import logging
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from functools import lru_cache

# Configuration
class Config:
    API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    BASE_URL = "https://api.elevenlabs.io/v1"
    DEFAULT_VOICE_ID = os.getenv("DEFAULT_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    DEFAULT_MODEL_ID = os.getenv("DEFAULT_MODEL_ID", "eleven_multilingual_v2")
    DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "mp3_44100_128")
    OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "./output")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# ElevenLabs API Client
class ElevenLabsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.BASE_URL
        self.session = None
        
    async def get_session(self):
        if not self.session:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=Config.API_TIMEOUT)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"xi-api-key": self.api_key}
            )
        return self.session
    
    async def post(self, endpoint: str, data: Dict, **kwargs):
        # Implementation with retry logic
        pass
    
    async def get(self, endpoint: str, params: Dict = None, **kwargs):
        # Implementation with retry logic
        pass

# Response formatting
def format_success(data: Any, message: str = "Success") -> Dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

def format_error(error: Any, code: str = "ERROR") -> Dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": str(error)
        },
        "timestamp": datetime.now().isoformat()
    }

# Validation utilities
def validate_voice_id(voice_id: str) -> bool:
    """Validate ElevenLabs voice ID format."""
    return bool(voice_id and len(voice_id) > 0)

def validate_audio_format(format: str) -> bool:
    """Validate audio output format."""
    valid_formats = [
        "mp3_22050_32", "mp3_44100_32", "mp3_44100_64",
        "mp3_44100_96", "mp3_44100_128", "mp3_44100_192",
        "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100",
        "ulaw_8000", "alaw_8000"
    ]
    return format in valid_formats

def validate_model_id(model_id: str) -> bool:
    """Validate TTS model ID."""
    valid_models = [
        "eleven_multilingual_v2", "eleven_turbo_v2_5",
        "eleven_flash_v2_5", "eleven_monolingual_v1"
    ]
    return model_id in valid_models

# Parameter conversion
def convert_mcp_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MCP string parameters to appropriate types."""
    converted = {}
    for key, value in params.items():
        if isinstance(value, str):
            # Try to convert numeric strings
            if '.' in value:
                try:
                    converted[key] = float(value)
                    continue
                except ValueError:
                    pass
            try:
                converted[key] = int(value)
                continue
            except ValueError:
                pass
            # Handle boolean strings
            if value.lower() in ('true', 'false'):
                converted[key] = value.lower() == 'true'
                continue
        converted[key] = value
    return converted

# Caching utilities
cache_store = {}

async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache if not expired."""
    if key in cache_store:
        item = cache_store[key]
        if datetime.now().timestamp() < item['expires']:
            return item['value']
        del cache_store[key]
    return None

async def cache_set(key: str, value: Any, ttl: int = None) -> None:
    """Set value in cache with TTL."""
    ttl = ttl or Config.CACHE_TTL
    cache_store[key] = {
        'value': value,
        'expires': datetime.now().timestamp() + ttl
    }

# File handling utilities
async def save_audio_file(audio_data: bytes, filename: str, output_dir: str = None) -> str:
    """Save audio data to file."""
    output_dir = output_dir or Config.OUTPUT_DIRECTORY
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(audio_data)
    return filepath

# Logger setup
logger = logging.getLogger(__name__)
```

## Configuration

### Environment Variables
- `ELEVENLABS_API_KEY`: Required API key
- `DEFAULT_VOICE_ID`: Default voice for TTS
- `DEFAULT_MODEL_ID`: Default TTS model
- `DEFAULT_OUTPUT_FORMAT`: Default audio format
- `OUTPUT_DIRECTORY`: Default save location
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
- `API_TIMEOUT`: API request timeout in seconds (default: 30)
- `MAX_RETRIES`: Maximum API retry attempts (default: 3)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Audio Format Options
- `mp3_22050_32`: MP3 22.05kHz 32kbps
- `mp3_44100_32`: MP3 44.1kHz 32kbps
- `mp3_44100_64`: MP3 44.1kHz 64kbps
- `mp3_44100_96`: MP3 44.1kHz 96kbps
- `mp3_44100_128`: MP3 44.1kHz 128kbps (default)
- `mp3_44100_192`: MP3 44.1kHz 192kbps (Pro+)
- `pcm_16000`: PCM 16kHz
- `pcm_22050`: PCM 22.05kHz
- `pcm_24000`: PCM 24kHz
- `pcm_44100`: PCM 44.1kHz (Pro+)
- `ulaw_8000`: μ-law 8kHz (telephony)

### Model Options
- `eleven_multilingual_v2`: 29 languages, high quality
- `eleven_turbo_v2_5`: 32 languages, fast
- `eleven_flash_v2_5`: 32 languages, ultra-low latency
- `eleven_monolingual_v1`: English only, legacy

## Error Handling

```python
class AudioGenerationError(Exception):
    """Audio generation failed."""

class TranscriptionError(Exception):
    """Speech-to-text failed."""

class QuotaExceededError(Exception):
    """API quota exceeded."""
```

## Usage Examples

### Generate Speech
```python
result = await text_to_speech(
    text="Hello, this is a test.",
    voice_id="21m00Tcm4TlvDq8ikWAM",
    language_code="en",
    stability=0.7,
    output_directory="/path/to/audio"
)
# Returns: {"file_path": "/path/to/audio/speech_123.mp3", "duration": 2.5}
```

### Transcribe Audio
```python
result = await speech_to_text(
    audio_file_path="/path/to/audio.mp3",
    diarize=True,
    num_speakers=2
)
# Returns: {"text": "...", "speakers": [...], "timestamps": [...]}
```

### Generate Sound Effect
```python
result = await generate_sound_effect(
    description="Thunder rumbling in the distance",
    duration_seconds=3.0
)
# Returns: {"file_path": "/path/to/sound_effect.mp3"}
```

## Dependencies
- `elevenlabs>=1.0.0`
- `fastmcp>=0.3.0`
- `aiofiles>=23.0.0`
- `pydub>=0.25.0` (for audio processing)