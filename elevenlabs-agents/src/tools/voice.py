"""
Voice configuration tools for ElevenLabs agents.
"""

import logging
from typing import Dict, Any, Optional
from shared import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def configure_voice(
    client,
    agent_id: str,
    voice_id: str,
    stability: Optional[str] = "0.5",
    similarity_boost: Optional[str] = "0.8",
    speed: Optional[str] = "1.0"
) -> Dict[str, Any]:
    """
    Configure agent voice settings.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to configure (format: agent_XXXX or UUID)
        voice_id: ElevenLabs voice ID (e.g., cgSgspJ2msm6clMCkdW9)
        stability: Voice consistency (0.0-1.0, lower=more variable, higher=more stable)
        similarity_boost: Voice matching (0.0-1.0, lower=creative freedom, higher=strict adherence)
        speed: Speech rate (0.7-1.2, 0.7=slower, 1.0=normal, 1.2=faster)
    
    Returns:
        Configuration result with voice settings applied
    
    Examples:
        # Standard configuration
        configure_voice("agent_abc123", "cgSgspJ2msm6clMCkdW9", 0.7, 0.9, 1.0)
        
        # More stable, consistent voice
        configure_voice("agent_abc123", "21m00Tcm4TlvDq8ikWAM", 
                       stability=0.9, similarity_boost=0.95)
        
        # More expressive, variable voice
        configure_voice("agent_abc123", "yoZ06aMxZJJ28mfd3POQ",
                       stability=0.3, similarity_boost=0.5, speed=1.1)
    
    Parameter Guidelines:
        stability:
            - 0.0-0.3: Very expressive, emotional range
            - 0.4-0.6: Balanced expression (default: 0.5)
            - 0.7-1.0: Consistent, stable delivery
        
        similarity_boost:
            - 0.0-0.3: Creative interpretation
            - 0.4-0.7: Natural variation
            - 0.8-1.0: Strict voice matching (default: 0.8)
        
        speed:
            - 0.7-0.9: Slower, more deliberate
            - 1.0: Normal speed (default)
            - 1.1-1.2: Faster, energetic
    
    API Endpoint: PATCH /convai/agents/{agent_id}
    """
    # Validate agent ID
    if not agent_id:
        return format_error(
            "Agent ID is required",
            "Provide agent_id from create_agent() or list_agents()"
        )
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error(
            f"Invalid agent ID format: {agent_id}",
            "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    # Validate voice ID
    if not voice_id:
        return format_error(
            "Voice ID is required",
            "Provide a valid ElevenLabs voice ID"
        )
    
    # Validate and coerce numeric parameters
    if stability is not None:
        try:
            stability = float(stability)
            if not 0.0 <= stability <= 1.0:
                return format_error(
                    f"Stability {stability} out of range",
                    "Stability must be between 0.0 (variable) and 1.0 (stable)"
                )
        except (TypeError, ValueError):
            return format_error(
                "Stability must be a number",
                "Use a value between 0.0 and 1.0"
            )
    
    if similarity_boost is not None:
        try:
            similarity_boost = float(similarity_boost)
            if not 0.0 <= similarity_boost <= 1.0:
                return format_error(
                    f"Similarity boost {similarity_boost} out of range",
                    "Similarity boost must be between 0.0 (creative) and 1.0 (strict)"
                )
        except (TypeError, ValueError):
            return format_error(
                "Similarity boost must be a number",
                "Use a value between 0.0 and 1.0"
            )
    
    if speed is not None:
        try:
            speed = float(speed)
            if not 0.7 <= speed <= 1.2:
                return format_error(
                    f"Speed {speed} out of range",
                    "Speed must be between 0.7 (slower) and 1.2 (faster)"
                )
        except (TypeError, ValueError):
            return format_error(
                "Speed must be a number",
                "Use a value between 0.7 and 1.2"
            )
    
    try:
        config = {
            "conversation_config": {
                "tts": {
                    "voice_id": voice_id,
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "speed": speed
                }
            }
        }
        
        result = await client.update_agent(agent_id, config)
        return format_success(
            "Voice configuration updated",
            {"voice_settings": config["conversation_config"]["tts"]}
        )
    except Exception as e:
        logger.error(f"Failed to configure voice for {agent_id}: {e}")
        error_msg = str(e)
        
        if "voice" in error_msg.lower():
            suggestion = "Check voice_id is valid. Common IDs: cgSgspJ2msm6clMCkdW9, 21m00Tcm4TlvDq8ikWAM"
        elif "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Agent {agent_id} not found. Use list_agents() to see available agents"
        else:
            suggestion = "Verify all parameters are within valid ranges"
            
        return format_error(error_msg, suggestion)


async def set_llm_config(
    client,
    agent_id: str,
    model: Optional[str] = None,
    temperature: Optional[str] = None,
    max_tokens: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure agent LLM settings.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to configure
        model: LLM model name
        temperature: Response creativity (0.0-1.0)
        max_tokens: Maximum response length
    
    Returns:
        Configuration result
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        llm_config = {}
        if model:
            llm_config["model"] = model
        
        # Handle temperature conversion and validation
        if temperature is not None:
            try:
                temperature_float = float(temperature)
                if not 0.0 <= temperature_float <= 2.0:
                    return format_error("temperature must be between 0.0 and 2.0")
                llm_config["temperature"] = temperature_float
            except (ValueError, TypeError):
                return format_error("temperature must be a valid number")
        
        # Handle max_tokens conversion and validation
        if max_tokens is not None:
            try:
                max_tokens_int = int(max_tokens)
                if not 1 <= max_tokens_int <= 8192:
                    return format_error("max_tokens must be between 1 and 8192")
                llm_config["max_tokens"] = max_tokens_int
            except (ValueError, TypeError):
                return format_error("max_tokens must be a valid integer")
        
        if not llm_config:
            return format_error("No LLM settings provided")
        
        config = {"conversation_config": {"llm": llm_config}}
        result = await client.update_agent(agent_id, config)
        return format_success(
            "LLM configuration updated",
            {"llm_settings": llm_config}
        )
    except Exception as e:
        logger.error(f"Failed to configure LLM for {agent_id}: {e}")
        return format_error(str(e))


async def list_voices(client) -> Dict[str, Any]:
    """
    List available ElevenLabs voices.
    
    Args:
        client: ElevenLabs API client
    
    Returns:
        List of available voices with IDs and descriptions
    """
    try:
        voices = await client.list_voices()
        
        # Format voice data for display
        formatted_voices = []
        for voice in voices:
            formatted_voices.append({
                "voice_id": voice.get("voice_id"),
                "name": voice.get("name"),
                "category": voice.get("category", "custom"),
                "description": voice.get("description", ""),
                "labels": voice.get("labels", {})
            })
        
        return format_success(
            f"Found {len(formatted_voices)} voices",
            {"count": len(formatted_voices), "voices": formatted_voices}
        )
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        return format_error(str(e), "Check API key and network connection")


async def get_shared_voices(client) -> Dict[str, Any]:
    """
    Get list of voices shared with your account.
    
    Args:
        client: ElevenLabs API client
    
    Returns:
        List of shared voices
    """
    try:
        voices = await client.list_voices()
        
        # Filter for shared/public voices
        shared_voices = [v for v in voices if v.get("category") in ["premade", "shared", "public"]]
        
        formatted_voices = []
        for voice in shared_voices:
            formatted_voices.append({
                "voice_id": voice.get("voice_id"),
                "name": voice.get("name"),
                "category": voice.get("category"),
                "description": voice.get("description", "")
            })
        
        return format_success(
            f"Found {len(formatted_voices)} shared voices",
            {"count": len(formatted_voices), "voices": formatted_voices}
        )
    except Exception as e:
        logger.error(f"Failed to get shared voices: {e}")
        return format_error(str(e))


async def add_shared_voice(client, voice_id: str, agent_id: str) -> Dict[str, Any]:
    """
    Add a shared voice to an agent.
    
    Args:
        client: ElevenLabs API client
        voice_id: Voice ID to add
        agent_id: Agent to update
    
    Returns:
        Update confirmation
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not voice_id:
        return format_error("Voice ID is required")
    
    try:
        config = {
            "conversation_config": {
                "tts": {
                    "voice_id": voice_id
                }
            }
        }
        
        result = await client.update_agent(agent_id, config)
        return format_success(
            f"Voice {voice_id} added to agent",
            {"agent_id": agent_id, "voice_id": voice_id}
        )
    except Exception as e:
        logger.error(f"Failed to add shared voice: {e}")
        return format_error(str(e))