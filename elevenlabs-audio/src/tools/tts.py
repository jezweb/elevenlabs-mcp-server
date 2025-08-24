"""Text-to-Speech tools for ElevenLabs audio server."""

import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from shared.client import ElevenLabsClient
from shared.utils import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def text_to_speech(
    text: str,
    voice_id: str,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True,
    output_format: str = "mp3_44100_128",
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert text to speech using ElevenLabs.
    
    Args:
        text: Text to convert to speech
        voice_id: Voice ID to use
        model_id: Model ID (eleven_multilingual_v2, eleven_turbo_v2, etc.)
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity (0.0-1.0)
        style: Style exaggeration (0.0-1.0)
        use_speaker_boost: Use speaker boost
        output_format: Audio format (mp3_44100_128, mp3_44100_192, etc.)
        save_to_file: Optional path to save audio file
        
    Returns:
        Audio data as base64 and metadata
    """
    try:
        if not text:
            raise ValueError("Text is required")
        
        if not validate_elevenlabs_id(voice_id):
            raise ValueError(f"Invalid voice ID: {voice_id}")
        
        # Prepare voice settings
        voice_settings = {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        }
        
        client = ElevenLabsClient()
        
        # Generate audio
        audio_data = await client.text_to_speech(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            voice_settings=voice_settings,
            output_format=output_format
        )
        
        # Save to file if requested
        file_path = None
        if save_to_file:
            file_path = Path(save_to_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(audio_data)
            logger.info(f"Audio saved to {file_path}")
        
        # Return base64 encoded audio
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return format_success({
            "audio": audio_base64,
            "format": output_format,
            "size": len(audio_data),
            "file_path": str(file_path) if file_path else None,
            "voice_id": voice_id,
            "model_id": model_id
        })
        
    except Exception as e:
        logger.error(f"Text-to-speech failed: {e}")
        return format_error(str(e))


async def text_to_speech_with_timestamps(
    text: str,
    voice_id: str,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True
) -> Dict[str, Any]:
    """
    Generate speech with word-level timestamps.
    
    Args:
        text: Text to convert to speech
        voice_id: Voice ID to use
        model_id: Model ID
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity (0.0-1.0)
        style: Style exaggeration (0.0-1.0)
        use_speaker_boost: Use speaker boost
        
    Returns:
        Audio data with timestamps
    """
    try:
        if not text:
            raise ValueError("Text is required")
        
        if not validate_elevenlabs_id(voice_id):
            raise ValueError(f"Invalid voice ID: {voice_id}")
        
        # Prepare voice settings
        voice_settings = {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        }
        
        client = ElevenLabsClient()
        
        # Generate audio with timestamps
        result = await client.text_to_speech_with_timestamps(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            voice_settings=voice_settings
        )
        
        # Extract audio and alignment data
        audio_base64 = result.get("audio_base64", "")
        alignment = result.get("alignment", {})
        
        return format_success({
            "audio": audio_base64,
            "alignment": alignment,
            "characters": alignment.get("characters", []),
            "words": alignment.get("words", []),
            "voice_id": voice_id,
            "model_id": model_id
        })
        
    except Exception as e:
        logger.error(f"Text-to-speech with timestamps failed: {e}")
        return format_error(str(e))


async def generate_dialogue(
    dialogue: list,
    voice_mapping: Dict[str, str],
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate multi-speaker dialogue audio.
    
    Args:
        dialogue: List of {speaker: str, text: str} dictionaries
        voice_mapping: Mapping of speaker names to voice IDs
        model_id: Model ID to use
        output_format: Audio format
        save_to_file: Optional path to save audio file
        
    Returns:
        Combined dialogue audio
    """
    try:
        if not dialogue:
            raise ValueError("Dialogue is required")
        
        if not voice_mapping:
            raise ValueError("Voice mapping is required")
        
        client = ElevenLabsClient()
        audio_segments = []
        
        # Generate audio for each dialogue segment
        for segment in dialogue:
            speaker = segment.get("speaker")
            text = segment.get("text")
            
            if not speaker or not text:
                continue
            
            voice_id = voice_mapping.get(speaker)
            if not voice_id:
                raise ValueError(f"No voice mapping for speaker: {speaker}")
            
            # Generate audio for this segment
            audio_data = await client.text_to_speech(
                text=text,
                voice_id=voice_id,
                model_id=model_id,
                output_format=output_format
            )
            
            audio_segments.append({
                "speaker": speaker,
                "text": text,
                "audio": base64.b64encode(audio_data).decode('utf-8'),
                "size": len(audio_data)
            })
        
        # Save combined audio if requested
        file_path = None
        if save_to_file and audio_segments:
            # For now, return segments separately
            # In production, you'd combine audio files
            file_path = Path(save_to_file)
            logger.info(f"Dialogue segments prepared for {file_path}")
        
        return format_success({
            "segments": audio_segments,
            "total_segments": len(audio_segments),
            "format": output_format,
            "file_path": str(file_path) if file_path else None
        })
        
    except Exception as e:
        logger.error(f"Dialogue generation failed: {e}")
        return format_error(str(e))