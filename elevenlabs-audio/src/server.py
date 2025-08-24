"""ElevenLabs Audio MCP Server - Audio generation and processing."""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from fastmcp import FastMCP

# Import all tools - using absolute imports for FastMCP compatibility
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from tools import (
    # TTS tools
    text_to_speech,
    text_to_speech_with_timestamps,
    generate_dialogue,
    
    # STT tools
    speech_to_text,
    transcribe_from_base64,
    batch_transcribe,
    
    # Effects tools
    generate_sound_effect,
    batch_generate_effects,
    
    # Voice transformation tools
    speech_to_speech,
    isolate_audio,
    batch_voice_transform
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="elevenlabs-audio",
    instructions="""ElevenLabs Audio MCP Server - Complete audio generation and processing.

This server provides tools for:
- Text-to-Speech (TTS) generation with multiple voices and models
- Speech-to-Text (STT) transcription with diarization
- Sound effects generation from text descriptions
- Voice transformation and audio isolation

Common voice IDs:
- Rachel: 21m00Tcm4TlvDq8ikWAM
- Adam: pNInz6obpgDQGcFmaJgB
- Sam: yoZ06aMxZJJ28mfd3POQ

Models:
- eleven_multilingual_v2: Best quality, 29 languages
- eleven_turbo_v2: Fast, high quality
- eleven_english_sts_v2: Voice transformation"""
)

# Register TTS tools

@mcp.tool()
async def tts_generate(
    text: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True,
    output_format: str = "mp3_44100_128",
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate speech from text using ElevenLabs.
    
    Args:
        text: Text to convert to speech
        voice_id: Voice ID (default: Rachel)
        model_id: Model to use
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity (0.0-1.0)
        style: Style exaggeration (0.0-1.0)
        use_speaker_boost: Enhance voice clarity
        output_format: Audio format
        save_to_file: Optional file path to save audio
    """
    return await text_to_speech(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        stability=stability,
        similarity_boost=similarity_boost,
        style=style,
        use_speaker_boost=use_speaker_boost,
        output_format=output_format,
        save_to_file=save_to_file
    )

@mcp.tool()
async def tts_with_timestamps(
    text: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75
) -> Dict[str, Any]:
    """
    Generate speech with word-level timestamps.
    
    Args:
        text: Text to convert to speech
        voice_id: Voice ID (default: Rachel)
        model_id: Model to use
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity (0.0-1.0)
    """
    return await text_to_speech_with_timestamps(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        stability=stability,
        similarity_boost=similarity_boost
    )

@mcp.tool()
async def tts_dialogue(
    dialogue: list,
    voice_mapping: Dict[str, str],
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate multi-speaker dialogue.
    
    Args:
        dialogue: List of {speaker: str, text: str} dictionaries
        voice_mapping: Map speaker names to voice IDs
        model_id: Model to use
        output_format: Audio format
        save_to_file: Optional file path
    """
    return await generate_dialogue(
        dialogue=dialogue,
        voice_mapping=voice_mapping,
        model_id=model_id,
        output_format=output_format,
        save_to_file=save_to_file
    )

# Register STT tools

@mcp.tool()
async def stt_transcribe(
    audio_file: str,
    language_code: Optional[str] = None,
    diarize: bool = False
) -> Dict[str, Any]:
    """
    Transcribe audio file to text.
    
    Args:
        audio_file: Path to audio file
        language_code: ISO 639-1 language code (auto-detect if not provided)
        diarize: Enable speaker diarization
    """
    return await speech_to_text(
        audio_file=audio_file,
        language_code=language_code,
        diarize=diarize
    )

@mcp.tool()
async def stt_transcribe_base64(
    audio_base64: str,
    language_code: Optional[str] = None,
    diarize: bool = False
) -> Dict[str, Any]:
    """
    Transcribe base64-encoded audio to text.
    
    Args:
        audio_base64: Base64-encoded audio data
        language_code: ISO 639-1 language code
        diarize: Enable speaker diarization
    """
    return await transcribe_from_base64(
        audio_base64=audio_base64,
        language_code=language_code,
        diarize=diarize
    )

@mcp.tool()
async def stt_batch_transcribe(
    audio_files: list,
    language_code: Optional[str] = None,
    diarize: bool = False,
    save_transcripts: bool = False
) -> Dict[str, Any]:
    """
    Batch transcribe multiple audio files.
    
    Args:
        audio_files: List of audio file paths
        language_code: ISO 639-1 language code
        diarize: Enable speaker diarization
        save_transcripts: Save transcripts to text files
    """
    return await batch_transcribe(
        audio_files=audio_files,
        language_code=language_code,
        diarize=diarize,
        save_transcripts=save_transcripts
    )

# Register Effects tools

@mcp.tool()
async def effects_generate(
    text: str,
    duration_seconds: float = 5.0,
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate sound effect from text description.
    
    Args:
        text: Description of the sound effect
        duration_seconds: Duration (0.5-22 seconds)
        save_to_file: Optional file path
    """
    return await generate_sound_effect(
        text=text,
        duration_seconds=duration_seconds,
        save_to_file=save_to_file
    )

@mcp.tool()
async def effects_batch_generate(
    effects: list,
    save_directory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate multiple sound effects.
    
    Args:
        effects: List of {text: str, duration: float, name: str} dictionaries
        save_directory: Optional directory to save files
    """
    return await batch_generate_effects(
        effects=effects,
        save_directory=save_directory
    )

# Register Voice Transformation tools

@mcp.tool()
async def voice_transform(
    audio_file: str,
    voice_id: str,
    model_id: str = "eleven_english_sts_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transform voice in audio to target voice.
    
    Args:
        audio_file: Path to input audio
        voice_id: Target voice ID
        model_id: Model to use
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity (0.0-1.0)
        save_to_file: Optional output path
    """
    return await speech_to_speech(
        audio_file=audio_file,
        voice_id=voice_id,
        model_id=model_id,
        stability=stability,
        similarity_boost=similarity_boost,
        save_to_file=save_to_file
    )

@mcp.tool()
async def audio_isolate(
    audio_file: str,
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Remove background noise from audio.
    
    Args:
        audio_file: Path to input audio
        save_to_file: Optional output path
    """
    return await isolate_audio(
        audio_file=audio_file,
        save_to_file=save_to_file
    )

@mcp.tool()
async def voice_batch_transform(
    audio_files: list,
    voice_id: str,
    model_id: str = "eleven_english_sts_v2",
    save_directory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transform multiple audio files to target voice.
    
    Args:
        audio_files: List of audio file paths
        voice_id: Target voice ID
        model_id: Model to use
        save_directory: Optional directory for output
    """
    return await batch_voice_transform(
        audio_files=audio_files,
        voice_id=voice_id,
        model_id=model_id,
        save_directory=save_directory
    )

# Main entry point
if __name__ == "__main__":
    # Run the server
    asyncio.run(mcp.run())
    logger.info("ElevenLabs Audio MCP Server started")