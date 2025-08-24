"""Speech-to-Text tools for ElevenLabs audio server."""

import base64
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from shared.client import ElevenLabsClient
from shared.utils import format_success, format_error

logger = logging.getLogger(__name__)


async def speech_to_text(
    audio_file: str,
    language_code: Optional[str] = None,
    diarize: bool = False
) -> Dict[str, Any]:
    """
    Transcribe audio to text using ElevenLabs.
    
    Args:
        audio_file: Path to audio file
        language_code: ISO 639-1 language code (auto-detect if not provided)
        diarize: Enable speaker diarization
        
    Returns:
        Transcription with optional speaker labels
    """
    try:
        audio_path = Path(audio_file)
        if not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_file}")
        
        # Read audio file
        audio_data = audio_path.read_bytes()
        
        client = ElevenLabsClient()
        
        # Transcribe audio
        result = await client.speech_to_text(
            audio_data=audio_data,
            language_code=language_code,
            diarize=diarize
        )
        
        # Extract transcription
        transcription = result.get("text", "")
        speakers = result.get("speakers", [])
        language_detected = result.get("language", language_code)
        
        return format_success({
            "transcription": transcription,
            "language": language_detected,
            "diarization_enabled": diarize,
            "speakers": speakers if diarize else None,
            "word_count": len(transcription.split()),
            "character_count": len(transcription)
        })
        
    except Exception as e:
        logger.error(f"Speech-to-text failed: {e}")
        return format_error(str(e))


async def transcribe_from_base64(
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
        
    Returns:
        Transcription with optional speaker labels
    """
    try:
        # Decode base64 audio
        audio_data = base64.b64decode(audio_base64)
        
        client = ElevenLabsClient()
        
        # Transcribe audio
        result = await client.speech_to_text(
            audio_data=audio_data,
            language_code=language_code,
            diarize=diarize
        )
        
        # Extract transcription
        transcription = result.get("text", "")
        speakers = result.get("speakers", [])
        language_detected = result.get("language", language_code)
        
        return format_success({
            "transcription": transcription,
            "language": language_detected,
            "diarization_enabled": diarize,
            "speakers": speakers if diarize else None,
            "word_count": len(transcription.split()),
            "character_count": len(transcription)
        })
        
    except Exception as e:
        logger.error(f"Transcription from base64 failed: {e}")
        return format_error(str(e))


async def batch_transcribe(
    audio_files: List[str],
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
        
    Returns:
        Batch transcription results
    """
    try:
        if not audio_files:
            raise ValueError("No audio files provided")
        
        client = ElevenLabsClient()
        results = []
        
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
                
                # Transcribe audio
                result = await client.speech_to_text(
                    audio_data=audio_data,
                    language_code=language_code,
                    diarize=diarize
                )
                
                transcription = result.get("text", "")
                
                # Save transcript if requested
                transcript_path = None
                if save_transcripts and transcription:
                    transcript_path = audio_path.with_suffix('.txt')
                    transcript_path.write_text(transcription)
                
                results.append({
                    "file": audio_file,
                    "transcription": transcription,
                    "language": result.get("language", language_code),
                    "transcript_file": str(transcript_path) if transcript_path else None,
                    "word_count": len(transcription.split())
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
            "total_words": sum(r.get("word_count", 0) for r in successful)
        })
        
    except Exception as e:
        logger.error(f"Batch transcription failed: {e}")
        return format_error(str(e))