# ElevenLabs Voices Server Architecture

## Overview
The `elevenlabs-voices` MCP server manages voices as resources, providing capabilities for voice creation (both from text and audio), cloning (IVC and PVC), library management, configuration, and sharing. This server handles all voice-related operations independent of audio generation.

## Modular Structure

Following the FastMCP structured template pattern for better organization and maintainability:

```
elevenlabs-voices/
├── src/
│   ├── server.py                # Main entry point, registers all tools
│   ├── utils.py                 # Self-contained utilities
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── voice_management.py # CRUD operations for voices
│   │   ├── voice_design.py     # Text-to-voice creation and design
│   │   ├── ivc_tools.py        # Instant Voice Cloning operations
│   │   ├── pvc_tools.py        # Professional Voice Cloning operations
│   │   ├── voice_library.py    # Search, browse, and sharing
│   │   └── voice_settings.py   # Voice configuration and tuning
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── voice_profiles.py   # Voice metadata resources
│   │   └── voice_samples.py    # Audio sample resources
│   └── handlers/
│       ├── __init__.py
│       └── upload_handlers.py  # File upload handling
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### 1. Voice Management

#### List Voices
- **Endpoint**: `GET /v1/voices`
- **Description**: Returns a list of available voices
- **Parameters**:
  - `show_legacy` (query, optional): Include legacy voices
- **Response**:
  ```json
  {
    "voices": [
      {
        "voice_id": "string",
        "name": "string",
        "samples": [],
        "category": "premade|cloned|generated",
        "fine_tuning": {
          "is_allowed_to_fine_tune": true,
          "state": "not_started|is_fine_tuning|fine_tuned"
        },
        "labels": {
          "accent": "string",
          "description": "string",
          "age": "string",
          "gender": "string",
          "use_case": "string"
        },
        "description": "string",
        "preview_url": "string",
        "available_for_tiers": [],
        "settings": {
          "stability": 0.5,
          "similarity_boost": 0.75,
          "style": 0.0,
          "use_speaker_boost": true
        },
        "sharing": {
          "status": "enabled|disabled",
          "history_item_sample_id": "string",
          "original_voice_id": "string",
          "public_owner_id": "string",
          "liked_by_count": 0,
          "cloned_by_count": 0,
          "name": "string",
          "description": "string",
          "labels": {},
          "review_status": "not_requested|pending|approved|rejected",
          "review_message": "string",
          "enabled_in_library": true,
          "instagram_username": "string",
          "twitter_username": "string",
          "youtube_username": "string",
          "tiktok_username": "string"
        },
        "high_quality_base_model_ids": []
      }
    ]
  }
  ```

#### Get Voice Details
- **Endpoint**: `GET /v1/voices/{voice_id}`
- **Description**: Returns metadata about a specific voice
- **Parameters**:
  - `voice_id` (path, required): Voice ID
  - `with_settings` (query, optional): Include settings
  - `with_subscription` (query, optional): Include subscription info

#### Add Voice
- **Endpoint**: `POST /v1/voices/add`
- **Description**: Add a new voice from audio samples
- **Parameters**:
  - `name` (form, required): Voice name
  - `files` (form, required): Audio samples (multipart/form-data)
  - `description` (form, optional): Voice description
  - `labels` (form, optional): JSON string of labels
  - `remove_background_noise` (form, optional): Clean audio samples
- **Requirements**:
  - Minimum 1 minute of audio
  - Maximum 15 minutes per sample
  - Supported formats: MP3, WAV, FLAC, M4A

#### Edit Voice
- **Endpoint**: `POST /v1/voices/{voice_id}/edit`
- **Description**: Edit voice metadata
- **Parameters**:
  - `voice_id` (path, required): Voice ID
  - `name` (form, optional): New name
  - `description` (form, optional): New description
  - `files` (form, optional): Additional samples
  - `labels` (form, optional): Updated labels
  - `remove_background_noise` (form, optional): Clean new samples

#### Delete Voice
- **Endpoint**: `DELETE /v1/voices/{voice_id}`
- **Description**: Delete a voice
- **Parameters**:
  - `voice_id` (path, required): Voice ID to delete

### 2. Voice Settings

#### Get Default Voice Settings
- **Endpoint**: `GET /v1/voices/settings/default`
- **Description**: Get default voice settings
- **Response**:
  ```json
  {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": true
  }
  ```

#### Get Voice Settings
- **Endpoint**: `GET /v1/voices/{voice_id}/settings`
- **Description**: Get settings for a specific voice
- **Parameters**:
  - `voice_id` (path, required): Voice ID

#### Update Voice Settings
- **Endpoint**: `POST /v1/voices/{voice_id}/settings/edit`
- **Description**: Update voice settings
- **Parameters**:
  - `voice_id` (path, required): Voice ID
  - `stability` (body, required): 0.0-1.0
  - `similarity_boost` (body, required): 0.0-1.0
  - `style` (body, optional): 0.0-1.0
  - `use_speaker_boost` (body, optional): boolean

### 3. Voice Cloning

#### Professional Voice Clone (PVC)
- **Endpoint**: `POST /v1/voices/add/pvc`
- **Description**: Create professional voice clone
- **Parameters**:
  - `name` (form, required): Voice name (max 100 chars)
  - `language` (form, required): Voice language
  - `description` (form, optional): Description (max 500 chars)
  - `files` (form, required): High-quality audio samples
  - `labels` (form, optional): Voice labels
- **Requirements**:
  - Minimum 30 minutes of audio
  - High-quality recordings
  - Consent verification required

#### Instant Voice Clone (IVC)
- **Endpoint**: `POST /v1/voices/add`
- **Description**: Create instant voice clone
- **Parameters**: Same as Add Voice
- **Requirements**:
  - Minimum 1 minute of audio
  - Faster processing than PVC

#### Professional Voice Clone (PVC) - Create
- **Endpoint**: `POST /v1/voices/add/professional`
- **Description**: Create professional voice clone with high fidelity
- **Parameters**:
  - `name` (body, required): Voice name
  - `description` (body, optional): Voice description
  - `files` (body, required): Audio files for training
  - `labels` (body, optional): Voice metadata

#### PVC - Train Voice
- **Endpoint**: `POST /v1/voices/{voice_id}/professional/train`
- **Description**: Start PVC training process
- **Parameters**:
  - `voice_id` (path, required): Voice ID to train

#### PVC - Add Samples
- **Endpoint**: `POST /v1/voices/{voice_id}/professional/samples`
- **Description**: Add training samples to PVC voice
- **Parameters**:
  - `voice_id` (path, required): Voice ID
  - `files` (body, required): Additional audio samples

#### PVC - Speaker Separation
- **Endpoint**: `POST /v1/voices/{voice_id}/professional/speaker-separation`
- **Description**: Separate speakers in multi-speaker audio
- **Parameters**:
  - `voice_id` (path, required): Voice ID
  - `audio_file` (body, required): Multi-speaker audio

#### PVC - Manual Verification
- **Endpoint**: `POST /v1/voices/{voice_id}/professional/verification`
- **Description**: Request manual verification for PVC
- **Parameters**:
  - `voice_id` (path, required): Voice ID
  - `captcha_response` (body, required): Verification captcha

### 4. Voice Design & Generation

#### Text to Voice - Design a Voice
- **Endpoint**: `POST /v1/text-to-voice`
- **Description**: Design a voice from text description
- **Parameters**:
  - `voice_description` (body, required): Text description of desired voice characteristics
  - `text` (body, optional): Sample text for generation
- **Response**: Three voice variations with IDs and audio previews

#### Text to Voice - Create Voice
- **Endpoint**: `POST /v1/text-to-voice/create-voice-from-preview`
- **Description**: Create a permanent voice from preview
- **Parameters**:
  - `generated_voice_id` (body, required): ID from design preview
  - `voice_name` (body, required): Name for the new voice
  - `voice_description` (body, optional): Description text
- **Response**: Created voice with permanent voice_id

#### Text to Voice - Stream Preview
- **Endpoint**: `POST /v1/text-to-voice/stream-voice-preview`
- **Description**: Stream voice preview in real-time
- **Parameters**:
  - `voice_description` (body, required): Voice characteristics
  - `text` (body, required): Text to stream
- **Response**: Audio stream of generated voice

#### Generate Random Voice
- **Endpoint**: `POST /v1/voice-generation/generate-voice`
- **Description**: Generate a random voice with parameters
- **Parameters**:
  - `gender` (body, required): "male" or "female"
  - `age` (body, required): "young", "middle_aged", or "old"
  - `accent` (body, required): Accent description
  - `accent_strength` (body, required): 0.3-2.0
  - `text` (body, required): Sample text for preview
- **Response**:
  ```json
  {
    "voice_id": "generated_voice_id",
    "audio": "base64_audio_preview"
  }
  ```

### 5. Voice Library

#### Get Shared Voices
- **Endpoint**: `GET /v1/shared-voices`
- **Description**: Browse community voice library
- **Parameters**:
  - `page_size` (query, optional): Results per page (default 30)
  - `category` (query, optional): Filter by category
  - `gender` (query, optional): Filter by gender
  - `age` (query, optional): Filter by age
  - `accent` (query, optional): Filter by accent
  - `language` (query, optional): Filter by language
  - `search` (query, optional): Search term
  - `use_cases` (query, optional): Filter by use case
  - `descriptives` (query, optional): Filter by descriptive tags
  - `featured` (query, optional): Show featured only
  - `reader_app_enabled` (query, optional): Reader app compatible
  - `owner_id` (query, optional): Filter by creator
  - `sort` (query, optional): Sort order
  - `page` (query, optional): Page number

#### Add Shared Voice
- **Endpoint**: `POST /v1/voices/add/{public_user_id}/{voice_id}`
- **Description**: Add a shared voice to your library
- **Parameters**:
  - `public_user_id` (path, required): Public owner ID
  - `voice_id` (path, required): Voice ID to add
  - `new_name` (body, required): Name in your library

### 6. Voice Samples

#### Get Voice Samples
- **Endpoint**: `GET /v1/voices/{voice_id}/samples`
- **Description**: Get audio samples for a voice
- **Parameters**:
  - `voice_id` (path, required): Voice ID

#### Delete Voice Sample
- **Endpoint**: `DELETE /v1/voices/{voice_id}/samples/{sample_id}`
- **Description**: Delete a voice sample
- **Parameters**:
  - `voice_id` (path, required): Voice ID
  - `sample_id` (path, required): Sample ID

### 7. Voice Sharing

#### Share Voice
- **Endpoint**: `POST /v1/voices/{voice_id}/sharing/enable`
- **Description**: Share voice to community library
- **Parameters**:
  - `voice_id` (path, required): Voice ID
  - `description` (body, required): Public description
  - `category` (body, optional): Voice category
  - `instagram_username` (body, optional): Social link
  - `twitter_username` (body, optional): Social link
  - `youtube_username` (body, optional): Social link
  - `tiktok_username` (body, optional): Social link

#### Disable Voice Sharing
- **Endpoint**: `POST /v1/voices/{voice_id}/sharing/disable`
- **Description**: Remove voice from public library
- **Parameters**:
  - `voice_id` (path, required): Voice ID

## Modular Tool Implementations

### Tool Module Organization

Tools are organized into focused modules for better maintainability:

#### 1. Voice Management Module (`voice_management.py`)
```python
# CRUD operations for voices
async def list_voices(
    show_legacy: bool = False,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """List all available voices."""

async def get_voice(
    voice_id: str,
    include_settings: bool = True
) -> Dict[str, Any]:
    """Get detailed information about a voice."""

async def create_voice(
    name: str,
    audio_files: List[str],
    description: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    remove_background_noise: bool = False
) -> Dict[str, Any]:
    """Create a new voice from audio samples."""

async def edit_voice(
    voice_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Edit voice metadata."""

async def delete_voice(
    voice_id: str
) -> Dict[str, Any]:
    """Delete a voice."""

async def get_voice_samples(
    voice_id: str
) -> Dict[str, Any]:
    """Get audio samples for a voice."""

async def delete_voice_sample(
    voice_id: str,
    sample_id: str
) -> Dict[str, Any]:
    """Delete a voice sample."""
```

#### 2. Voice Design Module (`voice_design.py`)
```python
# Text-to-voice creation and design
async def design_voice(
    voice_description: str,
    text: Optional[str] = None
) -> Dict[str, Any]:
    """Design voice from text description."""

async def create_voice_from_preview(
    generated_voice_id: str,
    voice_name: str,
    voice_description: Optional[str] = None
) -> Dict[str, Any]:
    """Create permanent voice from preview."""

async def stream_voice_preview(
    voice_description: str,
    text: str
) -> Dict[str, Any]:
    """Stream voice preview in real-time."""

async def generate_random_voice(
    gender: str,
    age: str,
    accent: str,
    accent_strength: float = 1.0,
    text: str = "This is a test."
) -> Dict[str, Any]:
    """Generate a random voice with parameters."""
```

#### 3. IVC Tools Module (`ivc_tools.py`)
```python
# Instant Voice Cloning operations
async def instant_voice_clone(
    name: str,
    files: List[str],
    description: Optional[str] = None,
    labels: Optional[Dict] = None,
    remove_background_noise: bool = False
) -> Dict[str, Any]:
    """Create instant voice clone."""

async def add_ivc_samples(
    voice_id: str,
    files: List[str],
    remove_background_noise: bool = False
) -> Dict[str, Any]:
    """Add samples to IVC voice."""

async def list_similar_voices(
    voice_id: str,
    limit: int = 10
) -> Dict[str, Any]:
    """Find voices similar to given voice."""
```

#### 4. PVC Tools Module (`pvc_tools.py`)
```python
# Professional Voice Cloning operations
async def create_pvc_voice(
    name: str,
    files: List[str],
    description: Optional[str] = None,
    labels: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create professional voice clone."""

async def train_pvc_voice(
    voice_id: str
) -> Dict[str, Any]:
    """Start PVC training process."""

async def add_pvc_samples(
    voice_id: str,
    files: List[str]
) -> Dict[str, Any]:
    """Add training samples to PVC voice."""

async def update_pvc_sample(
    voice_id: str,
    sample_id: str,
    metadata: Dict
) -> Dict[str, Any]:
    """Update PVC sample metadata."""

async def delete_pvc_sample(
    voice_id: str,
    sample_id: str
) -> Dict[str, Any]:
    """Delete PVC sample."""

async def speaker_separation(
    voice_id: str,
    audio_file: str
) -> Dict[str, Any]:
    """Separate speakers in audio."""

async def request_pvc_verification(
    voice_id: str,
    captcha_response: str
) -> Dict[str, Any]:
    """Request manual PVC verification."""
```

#### 4. Voice Library Module (`voice_library.py`)
```python
# Library browsing and sharing
async def search_voice_library(
    search: Optional[str] = None,
    category: Optional[str] = None,
    gender: Optional[str] = None,
    age: Optional[str] = None,
    accent: Optional[str] = None,
    language: Optional[str] = None,
    page_size: int = 30
) -> Dict[str, Any]:
    """Search the voice library."""

async def add_voice_from_library(
    public_user_id: str,
    voice_id: str,
    name: str
) -> Dict[str, Any]:
    """Add a shared voice to your collection."""

async def share_voice(
    voice_id: str,
    description: str,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """Share voice to community library."""

async def unshare_voice(
    voice_id: str
) -> Dict[str, Any]:
    """Remove voice from public library."""

async def get_featured_voices() -> Dict[str, Any]:
    """Get featured community voices."""

async def get_trending_voices() -> Dict[str, Any]:
    """Get trending voices in library."""
```

#### 5. Voice Settings Module (`voice_settings.py`)
```python
# Voice configuration and tuning
async def get_default_voice_settings() -> Dict[str, Any]:
    """Get default voice settings."""

async def get_voice_settings(
    voice_id: str
) -> Dict[str, Any]:
    """Get settings for a specific voice."""

async def update_voice_settings(
    voice_id: str,
    stability: float,
    similarity_boost: float,
    style: Optional[float] = None,
    use_speaker_boost: Optional[bool] = None
) -> Dict[str, Any]:
    """Update voice settings."""

async def reset_voice_settings(
    voice_id: str
) -> Dict[str, Any]:
    """Reset voice settings to defaults."""

async def fine_tune_voice(
    voice_id: str,
    training_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Fine-tune voice with additional data."""
```

### Tool Registration in server.py

```python
# src/server.py
from fastmcp import FastMCP
from utils import Config

# Initialize server
mcp = FastMCP(
    name="elevenlabs-voices",
    version="1.0.0"
)

# Import tool modules
from tools import (
    # Voice management
    list_voices,
    get_voice,
    create_voice,
    edit_voice,
    delete_voice,
    get_voice_samples,
    delete_voice_sample,
    
    # Voice cloning
    clone_voice_instant,
    clone_voice_professional,
    add_voice_samples,
    check_clone_status,
    
    # Voice generation
    generate_random_voice,
    design_voice,
    save_generated_voice,
    preview_generated_voice,
    
    # Voice library
    search_voice_library,
    add_voice_from_library,
    share_voice,
    unshare_voice,
    get_featured_voices,
    get_trending_voices,
    
    # Voice settings
    get_default_voice_settings,
    get_voice_settings,
    update_voice_settings,
    reset_voice_settings,
    fine_tune_voice
)

# Register all tools
for tool in [
    list_voices, get_voice, create_voice, edit_voice, delete_voice,
    get_voice_samples, delete_voice_sample,
    clone_voice_instant, clone_voice_professional, add_voice_samples,
    check_clone_status,
    generate_random_voice, design_voice, save_generated_voice, 
    preview_generated_voice,
    search_voice_library, add_voice_from_library, share_voice,
    unshare_voice, get_featured_voices, get_trending_voices,
    get_default_voice_settings, get_voice_settings, update_voice_settings,
    reset_voice_settings, fine_tune_voice
]:
    mcp.tool(tool)
```

## Resources

```python
@mcp.resource("voice://{voice_id}")
async def get_voice_resource(voice_id: str) -> Resource:
    """Get voice as a resource."""

@mcp.resource("voice-sample://{voice_id}/{sample_id}")
async def get_voice_sample(voice_id: str, sample_id: str) -> Resource:
    """Get voice sample audio."""

@mcp.resource("voice-library://search/{query}")
async def search_library_resource(query: str) -> Resource:
    """Search voice library as resource."""
```

## Self-Contained Utils Module

The `utils.py` file contains all shared utilities following the FastMCP structured pattern:

```python
# src/utils.py
"""Self-contained utilities for ElevenLabs Voices MCP Server"""

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
    DEFAULT_STABILITY = float(os.getenv("DEFAULT_STABILITY", "0.5"))
    DEFAULT_SIMILARITY_BOOST = float(os.getenv("DEFAULT_SIMILARITY_BOOST", "0.75"))
    DEFAULT_STYLE = float(os.getenv("DEFAULT_STYLE", "0.0"))
    VOICE_SAMPLES_DIR = os.getenv("VOICE_SAMPLES_DIR", "./voice_samples")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50MB

# ElevenLabs API Client (shared implementation)
class ElevenLabsClient:
    # Same as audio server implementation
    pass

# Response formatting (shared)
def format_success(data: Any, message: str = "Success") -> Dict[str, Any]:
    # Same implementation
    pass

def format_error(error: Any, code: str = "ERROR") -> Dict[str, Any]:
    # Same implementation
    pass

# Voice-specific validation utilities
def validate_voice_labels(labels: Dict[str, str]) -> bool:
    """Validate voice label structure."""
    valid_keys = ["accent", "age", "gender", "use_case", "description"]
    return all(key in valid_keys for key in labels.keys())

def validate_voice_category(category: str) -> bool:
    """Validate voice category."""
    valid_categories = ["premade", "cloned", "generated", "professional"]
    return category in valid_categories

def validate_age_group(age: str) -> bool:
    """Validate age group."""
    valid_ages = ["young", "middle_aged", "old"]
    return age in valid_ages

def validate_gender(gender: str) -> bool:
    """Validate gender."""
    valid_genders = ["male", "female", "neutral"]
    return gender in valid_genders

# File handling for voice samples
async def save_voice_sample(
    audio_data: bytes,
    voice_id: str,
    sample_id: str
) -> str:
    """Save voice sample to disk."""
    samples_dir = os.path.join(Config.VOICE_SAMPLES_DIR, voice_id)
    os.makedirs(samples_dir, exist_ok=True)
    filepath = os.path.join(samples_dir, f"{sample_id}.mp3")
    with open(filepath, 'wb') as f:
        f.write(audio_data)
    return filepath

async def validate_audio_file(filepath: str) -> Dict[str, Any]:
    """Validate audio file for voice cloning."""
    import wave
    import contextlib
    
    try:
        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size > Config.MAX_UPLOAD_SIZE:
            return {"valid": False, "error": "File too large"}
        
        # Check format (basic validation)
        # More complex validation would use pydub or similar
        
        return {"valid": True, "duration": 0, "format": "mp3"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

# Voice settings utilities
def merge_voice_settings(
    base: Dict[str, Any],
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge voice settings with defaults."""
    settings = {
        "stability": Config.DEFAULT_STABILITY,
        "similarity_boost": Config.DEFAULT_SIMILARITY_BOOST,
        "style": Config.DEFAULT_STYLE,
        "use_speaker_boost": True
    }
    settings.update(base)
    settings.update(updates)
    return settings

# Caching for voice library
voice_cache = {}

async def cache_voice_search(
    query_hash: str,
    results: List[Dict]
) -> None:
    """Cache voice search results."""
    voice_cache[query_hash] = {
        "results": results,
        "expires": datetime.now().timestamp() + Config.CACHE_TTL
    }

async def get_cached_voice_search(query_hash: str) -> Optional[List[Dict]]:
    """Get cached voice search results."""
    if query_hash in voice_cache:
        entry = voice_cache[query_hash]
        if datetime.now().timestamp() < entry["expires"]:
            return entry["results"]
        del voice_cache[query_hash]
    return None
```

## Configuration

### Environment Variables
- `ELEVENLABS_API_KEY`: Required API key
- `DEFAULT_STABILITY`: Default voice stability (0.5)
- `DEFAULT_SIMILARITY_BOOST`: Default similarity (0.75)
- `DEFAULT_STYLE`: Default style exaggeration (0.0)
- `VOICE_SAMPLES_DIR`: Directory for voice samples
- `MAX_UPLOAD_SIZE`: Maximum file upload size (default: 50MB)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Voice Categories
- `generated`: AI-generated voices
- `cloned`: Cloned from samples
- `premade`: Pre-made library voices
- `professional`: Professional clones

### Voice Labels
- `accent`: Voice accent
- `age`: young, middle_aged, old
- `gender`: male, female, neutral
- `use_case`: narration, gaming, meditation, etc.
- `description`: Descriptive text

## Error Handling

```python
class VoiceNotFoundError(Exception):
    """Voice ID not found."""

class VoiceCreationError(Exception):
    """Failed to create voice."""

class InsufficientAudioError(Exception):
    """Not enough audio for cloning."""

class VoiceQuotaExceededError(Exception):
    """Voice creation quota exceeded."""
```

## Usage Examples

### Create Instant Voice Clone
```python
result = await clone_voice_instant(
    name="My Voice",
    audio_file_path="/path/to/recording.mp3",
    description="Personal voice clone"
)
# Returns: {"voice_id": "abc123", "status": "created"}
```

### Search Voice Library
```python
results = await search_voice_library(
    gender="female",
    age="young",
    accent="british",
    category="professional"
)
# Returns: {"voices": [...], "total": 42}
```

### Generate Random Voice
```python
result = await generate_random_voice(
    gender="male",
    age="middle_aged",
    accent="american",
    accent_strength=1.2
)
# Returns: {"voice_id": "gen_xyz", "preview_audio": "..."}
```

## Dependencies
- `elevenlabs>=1.0.0`
- `fastmcp>=0.3.0`
- `aiofiles>=23.0.0`