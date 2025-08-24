"""Voice transformation tools for ElevenLabs audio server."""

import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from shared.client import ElevenLabsClient
from shared.utils import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def speech_to_speech(
    audio_file: str,
    voice_id: str,
    model_id: str = "eleven_english_sts_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True,
    output_format: str = "mp3_44100_128",
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transform voice in audio to target voice.
    
    Args:
        audio_file: Path to input audio file
        voice_id: Target voice ID
        model_id: Model ID (eleven_english_sts_v2, eleven_multilingual_sts_v2)
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity (0.0-1.0)
        style: Style exaggeration (0.0-1.0)
        use_speaker_boost: Use speaker boost
        output_format: Audio format
        save_to_file: Optional path to save transformed audio
        
    Returns:
        Transformed audio data
    """
    try:
        audio_path = Path(audio_file)
        if not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_file}")
        
        if not validate_elevenlabs_id(voice_id):
            raise ValueError(f"Invalid voice ID: {voice_id}")
        
        # Read audio file
        audio_data = audio_path.read_bytes()
        
        # Prepare voice settings
        voice_settings = {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        }
        
        client = ElevenLabsClient()
        
        # Transform voice
        transformed_audio = await client.speech_to_speech(
            audio_data=audio_data,
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
            file_path.write_bytes(transformed_audio)
            logger.info(f"Transformed audio saved to {file_path}")
        
        # Return base64 encoded audio
        audio_base64 = base64.b64encode(transformed_audio).decode('utf-8')
        
        return format_success({
            "audio": audio_base64,
            "format": output_format,
            "size": len(transformed_audio),
            "file_path": str(file_path) if file_path else None,
            "voice_id": voice_id,
            "model_id": model_id
        })
        
    except Exception as e:
        logger.error(f"Speech-to-speech transformation failed: {e}")
        return format_error(str(e))


async def isolate_audio(
    audio_file: str,
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Remove background noise from audio.
    
    Args:
        audio_file: Path to input audio file
        save_to_file: Optional path to save cleaned audio
        
    Returns:
        Cleaned audio data
    """
    try:
        audio_path = Path(audio_file)
        if not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_file}")
        
        # Read audio file
        audio_data = audio_path.read_bytes()
        
        client = ElevenLabsClient()
        
        # Isolate audio
        cleaned_audio = await client.isolate_audio(audio_data=audio_data)
        
        # Save to file if requested
        file_path = None
        if save_to_file:
            file_path = Path(save_to_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(cleaned_audio)
            logger.info(f"Cleaned audio saved to {file_path}")
        
        # Return base64 encoded audio
        audio_base64 = base64.b64encode(cleaned_audio).decode('utf-8')
        
        return format_success({
            "audio": audio_base64,
            "size": len(cleaned_audio),
            "file_path": str(file_path) if file_path else None,
            "original_size": len(audio_data),
            "reduction_ratio": f"{(1 - len(cleaned_audio)/len(audio_data))*100:.1f}%"
        })
        
    except Exception as e:
        logger.error(f"Audio isolation failed: {e}")
        return format_error(str(e))


async def batch_voice_transform(
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
        model_id: Model ID
        save_directory: Optional directory to save transformed files
        
    Returns:
        Batch transformation results
    """
    try:
        if not audio_files:
            raise ValueError("No audio files provided")
        
        if not validate_elevenlabs_id(voice_id):
            raise ValueError(f"Invalid voice ID: {voice_id}")
        
        client = ElevenLabsClient()
        results = []
        save_dir = Path(save_directory) if save_directory else None
        
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        for audio_file in audio_files:
            audio_path = Path(audio_file)
            
            if not audio_path.exists():
                results.append({
                    "file": audio_file,
                    "error": "File not found"
                })
                continue
            
            try:
                # Read audio file
                audio_data = audio_path.read_bytes()
                
                # Transform voice
                transformed_audio = await client.speech_to_speech(
                    audio_data=audio_data,
                    voice_id=voice_id,
                    model_id=model_id
                )
                
                # Save to file if directory provided
                file_path = None
                if save_dir:
                    file_path = save_dir / f"transformed_{audio_path.name}"
                    file_path.write_bytes(transformed_audio)
                
                results.append({
                    "file": audio_file,
                    "size": len(transformed_audio),
                    "file_path": str(file_path) if file_path else None,
                    "audio": base64.b64encode(transformed_audio).decode('utf-8')
                })
                
            except Exception as e:
                results.append({
                    "file": audio_file,
                    "error": str(e)
                })
        
        # Calculate statistics
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]
        
        return format_success({
            "results": results,
            "total_files": len(audio_files),
            "successful": len(successful),
            "failed": len(failed),
            "voice_id": voice_id,
            "model_id": model_id
        })
        
    except Exception as e:
        logger.error(f"Batch voice transformation failed: {e}")
        return format_error(str(e))