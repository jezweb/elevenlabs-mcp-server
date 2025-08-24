# ElevenLabs Audio Server Architecture

## Overview
The `elevenlabs-audio` MCP server provides comprehensive audio generation and processing capabilities including text-to-speech, speech-to-text, sound effects, music generation, and audio utilities.

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

### 3. Speech-to-Speech

#### Voice Transformation
- **Endpoint**: `POST /v1/speech-to-speech/{voice_id}`
- **Description**: Transform audio from one voice to another
- **Parameters**:
  - `voice_id` (path, required): Target voice ID
  - `audio` (body, required): Source audio file
  - `model_id` (body, optional): Model selection
  - `voice_settings` (body, optional): Same as TTS
  - `output_format` (body, optional): Audio format
  - `remove_background_noise` (body, optional): boolean

#### Streaming Voice Transformation
- **Endpoint**: `POST /v1/speech-to-speech/{voice_id}/stream`
- **Description**: Real-time voice transformation
- **Parameters**: Same as standard speech-to-speech

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

## Tool Implementations

### Core Tools

```python
@mcp.tool()
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

@mcp.tool()
async def speech_to_text(
    audio_file_path: str,
    model_id: str = "scribe_v1",
    language_code: Optional[str] = None,
    diarize: bool = False,
    num_speakers: Optional[int] = None,
    translation_languages: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Transcribe audio to text."""

@mcp.tool()
async def generate_sound_effect(
    description: str,
    duration_seconds: float = 5.0,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Generate sound effects from text description."""

@mcp.tool()
async def generate_music(
    prompt: str,
    duration_seconds: float = 30.0,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Generate music from text prompt."""

@mcp.tool()
async def transform_voice(
    audio_file_path: str,
    target_voice_id: str,
    remove_background_noise: bool = False,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Transform audio from one voice to another."""

@mcp.tool()
async def generate_dialogue(
    dialogue_script: List[Dict[str, str]],
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Generate multi-speaker dialogue."""

@mcp.tool()
async def remove_background_noise(
    audio_file_path: str,
    save_to_file: bool = True,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Remove background noise from audio."""
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

## Configuration

### Environment Variables
- `ELEVENLABS_API_KEY`: Required API key
- `DEFAULT_VOICE_ID`: Default voice for TTS
- `DEFAULT_MODEL_ID`: Default TTS model
- `DEFAULT_OUTPUT_FORMAT`: Default audio format
- `OUTPUT_DIRECTORY`: Default save location

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