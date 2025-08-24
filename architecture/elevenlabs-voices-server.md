# ElevenLabs Voices Server Architecture

## Overview
The `elevenlabs-voices` MCP server provides comprehensive voice management capabilities including voice creation, cloning, editing, library management, and sharing functionality.

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

### 4. Voice Generation

#### Generate Random Voice
- **Endpoint**: `POST /v1/voice-generation/generate-voice`
- **Description**: Generate a random voice
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

#### Voice Design
- **Endpoint**: `POST /v1/text-to-voice`
- **Description**: Design a voice from text description
- **Parameters**:
  - `voice_description` (body, required): Text description of desired voice
  - `text` (body, optional): Sample text for generation
- **Response**: Three voice variations with IDs and audio previews

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

## Tool Implementations

### Core Tools

```python
@mcp.tool()
async def list_voices(
    show_legacy: bool = False,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """List all available voices."""

@mcp.tool()
async def get_voice(
    voice_id: str,
    include_settings: bool = True
) -> Dict[str, Any]:
    """Get detailed information about a voice."""

@mcp.tool()
async def create_voice(
    name: str,
    audio_files: List[str],
    description: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    remove_background_noise: bool = False
) -> Dict[str, Any]:
    """Create a new voice from audio samples."""

@mcp.tool()
async def clone_voice_instant(
    name: str,
    audio_file_path: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create instant voice clone from audio."""

@mcp.tool()
async def clone_voice_professional(
    name: str,
    audio_files: List[str],
    language: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create professional voice clone."""

@mcp.tool()
async def edit_voice(
    voice_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Edit voice metadata."""

@mcp.tool()
async def delete_voice(
    voice_id: str
) -> Dict[str, Any]:
    """Delete a voice."""

@mcp.tool()
async def update_voice_settings(
    voice_id: str,
    stability: float,
    similarity_boost: float,
    style: Optional[float] = None,
    use_speaker_boost: Optional[bool] = None
) -> Dict[str, Any]:
    """Update voice settings."""

@mcp.tool()
async def generate_random_voice(
    gender: str,
    age: str,
    accent: str,
    accent_strength: float = 1.0
) -> Dict[str, Any]:
    """Generate a random voice."""

@mcp.tool()
async def design_voice(
    voice_description: str,
    sample_text: Optional[str] = None
) -> Dict[str, Any]:
    """Design a voice from text description."""

@mcp.tool()
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

@mcp.tool()
async def add_voice_from_library(
    public_user_id: str,
    voice_id: str,
    name: str
) -> Dict[str, Any]:
    """Add a shared voice to your collection."""

@mcp.tool()
async def share_voice(
    voice_id: str,
    description: str,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """Share voice to community library."""

@mcp.tool()
async def unshare_voice(
    voice_id: str
) -> Dict[str, Any]:
    """Remove voice from public library."""
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

## Configuration

### Environment Variables
- `ELEVENLABS_API_KEY`: Required API key
- `DEFAULT_STABILITY`: Default voice stability (0.5)
- `DEFAULT_SIMILARITY_BOOST`: Default similarity (0.75)
- `DEFAULT_STYLE`: Default style exaggeration (0.0)
- `VOICE_SAMPLES_DIR`: Directory for voice samples

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