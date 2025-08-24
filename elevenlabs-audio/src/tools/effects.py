"""Sound effects generation tools for ElevenLabs audio server."""

import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from shared.client import ElevenLabsClient
from shared.utils import format_success, format_error

logger = logging.getLogger(__name__)


async def generate_sound_effect(
    text: str,
    duration_seconds: float = 5.0,
    save_to_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate sound effect from text description.
    
    Args:
        text: Description of the sound effect
        duration_seconds: Duration in seconds (0.5-22)
        save_to_file: Optional path to save audio file
        
    Returns:
        Generated sound effect audio
    """
    try:
        if not text:
            raise ValueError("Text description is required")
        
        if duration_seconds < 0.5 or duration_seconds > 22:
            raise ValueError("Duration must be between 0.5 and 22 seconds")
        
        client = ElevenLabsClient()
        
        # Generate sound effect
        audio_data = await client.generate_sound_effect(
            text=text,
            duration_seconds=duration_seconds
        )
        
        # Save to file if requested
        file_path = None
        if save_to_file:
            file_path = Path(save_to_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(audio_data)
            logger.info(f"Sound effect saved to {file_path}")
        
        # Return base64 encoded audio
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return format_success({
            "audio": audio_base64,
            "description": text,
            "duration_seconds": duration_seconds,
            "size": len(audio_data),
            "file_path": str(file_path) if file_path else None
        })
        
    except Exception as e:
        logger.error(f"Sound effect generation failed: {e}")
        return format_error(str(e))


async def batch_generate_effects(
    effects: list,
    save_directory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate multiple sound effects in batch.
    
    Args:
        effects: List of {text: str, duration: float, name: str} dictionaries
        save_directory: Optional directory to save audio files
        
    Returns:
        Batch generation results
    """
    try:
        if not effects:
            raise ValueError("No effects to generate")
        
        client = ElevenLabsClient()
        results = []
        save_dir = Path(save_directory) if save_directory else None
        
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        for effect in effects:
            text = effect.get("text")
            duration = effect.get("duration", 5.0)
            name = effect.get("name", text[:20])
            
            if not text:
                results.append({
                    "name": name,
                    "error": "Text description is required"
                })
                continue
            
            try:
                # Generate sound effect
                audio_data = await client.generate_sound_effect(
                    text=text,
                    duration_seconds=duration
                )
                
                # Save to file if directory provided
                file_path = None
                if save_dir:
                    safe_name = "".join(c for c in name if c.isalnum() or c in " -_")
                    file_path = save_dir / f"{safe_name}.mp3"
                    file_path.write_bytes(audio_data)
                
                results.append({
                    "name": name,
                    "text": text,
                    "duration": duration,
                    "size": len(audio_data),
                    "file_path": str(file_path) if file_path else None,
                    "audio": base64.b64encode(audio_data).decode('utf-8')
                })
                
            except Exception as e:
                results.append({
                    "name": name,
                    "error": str(e)
                })
        
        # Calculate statistics
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]
        
        return format_success({
            "results": results,
            "total_effects": len(effects),
            "successful": len(successful),
            "failed": len(failed),
            "total_size": sum(r.get("size", 0) for r in successful)
        })
        
    except Exception as e:
        logger.error(f"Batch effect generation failed: {e}")
        return format_error(str(e))