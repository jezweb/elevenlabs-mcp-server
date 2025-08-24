#!/usr/bin/env python3
"""
ElevenLabs Agents MCP Server
============================
Manages conversational AI agents, configuration, and multi-agent orchestration.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from shared import Config, ElevenLabsClient, format_success, format_error, validate_uuid, validate_elevenlabs_id

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration on import
try:
    Config.validate()
    logger.info(f"Configuration validated. API key: {Config.mask_api_key()}")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(1)

# Initialize ElevenLabs client at module level
client = ElevenLabsClient(Config.API_KEY)

# Define lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app):
    """Handle server lifecycle events."""
    # Startup
    logger.info(f"Starting elevenlabs-agents server")
    
    # Test API connection
    if await client.test_connection():
        logger.info("ElevenLabs API connection verified")
    else:
        logger.warning("Failed to verify API connection - some features may be unavailable")
    
    yield  # Server runs here
    
    # Shutdown
    logger.info("Shutting down elevenlabs-agents server")
    await client.close()

# Initialize FastMCP server - MUST be at module level
mcp = FastMCP(
    name="elevenlabs-agents",
    instructions="Manage ElevenLabs conversational AI agents",
    lifespan=lifespan
)

# ============================================================
# Resource Loading Helpers
# ============================================================

def load_resource(filename: str) -> Dict[str, Any]:
    """Load a JSON resource file."""
    resource_path = Path(__file__).parent / "resources" / filename
    if resource_path.exists():
        with open(resource_path, 'r') as f:
            return json.load(f)
    return {}

# Load templates at module level for efficiency
PROMPT_TEMPLATES = load_resource("prompt_templates.json")
VOICE_PRESETS = load_resource("voice_presets.json")
AGENT_TEMPLATES = load_resource("agent_templates.json")

# ============================================================
# Agent Management Tools
# ============================================================

@mcp.tool()
async def create_agent(
    name: str,
    system_prompt: str,
    first_message: str,
    voice_id: Optional[str] = "cgSgspJ2msm6clMCkdW9",
    llm_model: Optional[str] = "gemini-2.0-flash-001",
    temperature: Optional[str] = "0.5",
    language: Optional[str] = "en"
) -> Dict[str, Any]:
    """
    Create a new conversational AI agent.
    
    Args:
        name: Agent display name (e.g., "Customer Support Bot")
        system_prompt: Instructions defining agent behavior and personality
        first_message: Initial greeting message (e.g., "Hello! How can I help you today?")
        voice_id: ElevenLabs voice ID (default: cgSgspJ2msm6clMCkdW9)
        llm_model: LLM model to use (default: gemini-2.0-flash-001)
        temperature: Response creativity (0.0-1.0, lower=consistent, higher=creative)
        language: ISO 639-1 language code (e.g., "en", "es", "fr")
    
    Returns:
        Created agent details with agent_id for further operations
    
    Examples:
        create_agent("Support Bot", "You are a helpful customer support agent", 
                    "Hi! I'm here to help with your questions.")
        
        create_agent("Sales Assistant", 
                    "You are a knowledgeable sales assistant for our products",
                    "Welcome! What product information can I help you with today?",
                    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                    temperature=0.7)
    
    Common Voice IDs:
        - cgSgspJ2msm6clMCkdW9: Default professional voice
        - 21m00Tcm4TlvDq8ikWAM: Rachel (calm, female)
        - yoZ06aMxZJJ28mfd3POQ: Sam (young, male)
    
    Valid LLM Models:
        - gemini-2.0-flash-001 (default, fast)
        - gpt-4o-mini (OpenAI, balanced)
        - claude-3-haiku (Anthropic, efficient)
    
    API Endpoint: POST /convai/agents
    """
    # Input validation
    if not name or not name.strip():
        return format_error(
            "Agent name cannot be empty",
            "Provide a descriptive name like 'Customer Support' or 'Sales Assistant'"
        )
    
    if not system_prompt or len(system_prompt) < 10:
        return format_error(
            "System prompt too short",
            "Provide clear instructions at least 10 characters long"
        )
    
    if not first_message or len(first_message) < 5:
        return format_error(
            "First message too short", 
            "Provide a greeting at least 5 characters long"
        )
    
    # Convert and validate temperature
    temperature_float = 0.5  # default
    if temperature is not None:
        try:
            temperature_float = float(temperature)
        except (ValueError, TypeError):
            return format_error(
                "Temperature must be a number",
                "Use a value between 0.0 (deterministic) and 1.0 (creative)"
            )
        
        if not 0.0 <= temperature_float <= 1.0:
            return format_error(
                f"Temperature {temperature_float} out of range",
                "Temperature must be between 0.0 and 1.0"
            )
    
    # Validate language code
    valid_languages = ["en", "es", "fr", "de", "it", "pt", "pl", "hi", "ja", "ko", "zh"]
    if language and language not in valid_languages:
        return format_error(
            f"Language '{language}' not supported",
            f"Use one of: {', '.join(valid_languages)}"
        )
    
    try:
        # Build the conversation_config for the API
        conversation_config = {
            "agent": {
                "prompt": {
                    "prompt": system_prompt,
                    "first_message": first_message
                }
            },
            "tts": {
                "voice_id": voice_id
            },
            "llm": {
                "model": llm_model,
                "temperature": temperature_float
            },
            "language": language
        }
        
        # Create the agent using the API
        agent_data = {
            "conversation_config": conversation_config,
            "name": name
        }
        
        result = await client.create_agent(agent_data)
        
        return format_success(
            f"Agent '{name}' created successfully",
            {
                "agent_id": result.get("agent_id"),
                "name": name,
                "config": conversation_config
            }
        )
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        error_msg = str(e)
        
        # Provide specific suggestions based on error
        if "voice_id" in error_msg.lower():
            suggestion = "Check voice_id is valid. Use list_voices() to see available voices"
        elif "model" in error_msg.lower():
            suggestion = "Check LLM model name. Common models: gemini-2.0-flash-001, gpt-4o-mini"
        elif "unauthorized" in error_msg.lower() or "401" in error_msg:
            suggestion = "Check your ELEVENLABS_API_KEY is valid"
        else:
            suggestion = "Check API key and ensure all parameters are valid"
            
        return format_error(error_msg, suggestion)


@mcp.tool()
async def list_agents() -> Dict[str, Any]:
    """
    List all conversational AI agents.
    
    Returns:
        List of agents with their configurations
    """
    try:
        agents = await client.list_agents()
        return format_success(
            f"Found {len(agents)} agents",
            {"count": len(agents), "agents": agents}
        )
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        return format_error(str(e), suggestion="Check API key and permissions")


@mcp.tool()
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific agent.
    
    Args:
        agent_id: Unique agent identifier (format: agent_XXXX or UUID)
    
    Returns:
        Complete agent configuration and metadata
    
    Examples:
        get_agent("agent_abc123def456ghi789jkl012mno345")
        get_agent("550e8400-e29b-41d4-a716-446655440000")
    
    ID Format:
        - agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX (agent_ + 28 characters)
        - Standard UUID format also accepted
    
    API Endpoint: GET /convai/agents/{agent_id}
    """
    if not agent_id:
        return format_error(
            "Agent ID is required",
            "Provide agent_id from create_agent() or list_agents()"
        )
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error(
            f"Invalid agent ID format: {agent_id}",
            "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX (agent_ + 28 chars) or valid UUID"
        )
    
    try:
        agent = await client.get_agent(agent_id)
        return format_success(
            f"Retrieved agent details",
            {"agent": agent}
        )
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        error_msg = str(e)
        
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Agent {agent_id} not found. Use list_agents() to see available agents"
        elif "unauthorized" in error_msg.lower() or "401" in error_msg:
            suggestion = "Check your ELEVENLABS_API_KEY is valid"
        else:
            suggestion = "Verify agent ID format and that the agent exists"
            
        return format_error(error_msg, suggestion)


@mcp.tool()
async def update_agent(
    agent_id: str,
    name: Optional[str] = None,
    system_prompt: Optional[str] = None,
    first_message: Optional[str] = None,
    temperature: Optional[str] = None,
    voice_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update agent configuration.
    
    Args:
        agent_id: Agent to update
        name: New agent name
        system_prompt: New system instructions
        first_message: New greeting
        temperature: New temperature (0.0-1.0)
        voice_id: New voice ID
    
    Returns:
        Updated agent details
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Build update config with only provided fields
        update_config = {}
        
        if name:
            update_config["name"] = name
        
        conversation_config = {}
        if system_prompt or first_message:
            conversation_config["agent"] = {"prompt": {}}
            if system_prompt:
                conversation_config["agent"]["prompt"]["prompt"] = system_prompt
            if first_message:
                conversation_config["agent"]["prompt"]["first_message"] = first_message
        
        if temperature is not None:
            try:
                temperature_float = float(temperature)
                if not 0.0 <= temperature_float <= 1.0:
                    return format_error(
                        f"Temperature {temperature_float} out of range",
                        "Temperature must be between 0.0 and 1.0"
                    )
                conversation_config["llm"] = {"temperature": temperature_float}
            except (ValueError, TypeError):
                return format_error(
                    "Temperature must be a number",
                    "Use a value between 0.0 (deterministic) and 1.0 (creative)"
                )
        
        if voice_id:
            conversation_config["tts"] = {"voice_id": voice_id}
        
        if conversation_config:
            update_config["conversation_config"] = conversation_config
        
        if not update_config:
            return format_error("No update fields provided")
        
        result = await client.update_agent(agent_id, update_config)
        return format_success(
            "Agent updated successfully",
            {"agent": result}
        )
    except Exception as e:
        logger.error(f"Failed to update agent {agent_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def delete_agent(agent_id: str) -> Dict[str, Any]:
    """
    Delete an agent.
    
    Args:
        agent_id: Agent to delete
    
    Returns:
        Deletion confirmation
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        await client.delete_agent(agent_id)
        return format_success(f"Agent {agent_id} deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete agent {agent_id}: {e}")
        return format_error(str(e))


# ============================================================
# Agent Configuration Tools
# ============================================================

@mcp.tool()
async def update_system_prompt(
    agent_id: str,
    system_prompt: str
) -> Dict[str, Any]:
    """
    Update an agent's system prompt.
    
    Args:
        agent_id: Agent to update
        system_prompt: New system instructions
    
    Returns:
        Update confirmation
    """
    return await update_agent(agent_id, system_prompt=system_prompt)


@mcp.tool()
async def configure_voice(
    agent_id: str,
    voice_id: str,
    stability: Optional[str] = "0.5",
    similarity_boost: Optional[str] = "0.8",
    speed: Optional[str] = "1.0"
) -> Dict[str, Any]:
    """
    Configure agent voice settings.
    
    Args:
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


@mcp.tool()
async def set_llm_config(
    agent_id: str,
    model: Optional[str] = None,
    temperature: Optional[str] = None,
    max_tokens: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure agent LLM settings.
    
    Args:
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


# ============================================================
# Transfer Configuration Tools
# ============================================================

@mcp.tool()
async def add_transfer_to_agent(
    from_agent_id: str,
    to_agent_id: str,
    conditions: str,
    message: Optional[str] = "I'll transfer you to a specialist"
) -> Dict[str, Any]:
    """
    Configure agent-to-agent transfer.
    
    Args:
        from_agent_id: Source agent
        to_agent_id: Target agent
        conditions: Natural language transfer conditions
        message: Transfer announcement
    
    Returns:
        Transfer configuration result
    """
    if not validate_elevenlabs_id(from_agent_id, 'agent') or not validate_elevenlabs_id(to_agent_id, 'agent'):
        return format_error("Invalid agent ID format", suggestion="Provide valid agent IDs (e.g., agent_XXXX or UUID)")
    
    try:
        tool_config = {
            "tools": [{
                "type": "transfer_to_agent",
                "config": {
                    "agent_id": to_agent_id,
                    "transfer_conditions": conditions,
                    "transfer_message": message,
                    "pass_context": True
                }
            }]
        }
        
        # Note: This is a simplified example - actual API may differ
        result = await client.update_agent(from_agent_id, tool_config)
        return format_success(
            f"Transfer configured from {from_agent_id} to {to_agent_id}",
            {"transfer_config": tool_config["tools"][0]}
        )
    except Exception as e:
        logger.error(f"Failed to configure transfer: {e}")
        return format_error(str(e))


# ============================================================
# Additional Agent Management Tools
# ============================================================

@mcp.tool()
async def duplicate_agent(
    agent_id: str,
    new_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Duplicate an existing agent.
    
    Args:
        agent_id: Agent to duplicate
        new_name: Name for the duplicated agent
    
    Returns:
        New agent details with agent_id
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Duplicate the agent
        result = await client._request(
            "POST", 
            f"/convai/agents/{agent_id}/duplicate",
            json_data={"name": new_name} if new_name else {}
        )
        
        return format_success(
            f"Agent duplicated successfully",
            {"agent": result}
        )
    except Exception as e:
        logger.error(f"Failed to duplicate agent {agent_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_agent_link(agent_id: str) -> Dict[str, Any]:
    """
    Get a shareable link for an agent.
    
    Args:
        agent_id: Agent to get link for
    
    Returns:
        Shareable link URL
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        result = await client._request("GET", f"/convai/agents/{agent_id}/link")
        
        # Check if link is available
        link = result.get("link")
        if not link:
            return format_success(
                "Agent link not available",
                {
                    "link": None,
                    "agent_id": agent_id,
                    "message": "Agent does not have a shareable link configured. Enable sharing in agent settings to generate a link."
                }
            )
        
        return format_success(
            "Agent link retrieved",
            {"link": link, "agent_id": agent_id}
        )
    except Exception as e:
        logger.error(f"Failed to get agent link: {e}")
        return format_error(str(e))


@mcp.tool()
async def calculate_llm_usage(
    agent_id: str,
    estimated_conversations: Optional[int] = 100,
    average_duration_minutes: Optional[float] = 5.0
) -> Dict[str, Any]:
    """
    Calculate expected LLM usage and costs for an agent.
    
    Args:
        agent_id: Agent to calculate usage for
        estimated_conversations: Number of expected conversations
        average_duration_minutes: Average conversation duration
    
    Returns:
        Usage statistics and cost estimates
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        result = await client._request(
            "POST",
            f"/convai/agents/{agent_id}/calculate-llm-usage",
            json_data={
                "estimated_conversations": estimated_conversations,
                "average_duration_minutes": average_duration_minutes
            }
        )
        
        return format_success(
            "LLM usage calculated",
            {"usage": result}
        )
    except Exception as e:
        logger.error(f"Failed to calculate LLM usage: {e}")
        return format_error(str(e))


# ============================================================
# Widget Management Tools
# ============================================================

@mcp.tool()
async def get_widget(widget_id: str) -> Dict[str, Any]:
    """
    Get widget configuration for an agent.
    
    Args:
        widget_id: Widget identifier
    
    Returns:
        Widget configuration and embed code
    """
    if not validate_uuid(widget_id):
        return format_error("Invalid widget ID format")
    
    try:
        result = await client._request("GET", f"/convai/widgets/{widget_id}")
        return format_success(
            "Widget configuration retrieved",
            {"widget": result}
        )
    except Exception as e:
        logger.error(f"Failed to get widget: {e}")
        return format_error(str(e))


@mcp.tool()
async def create_widget_avatar(
    widget_id: str,
    avatar_image_url: Optional[str] = None,
    avatar_style: Optional[str] = "default"
) -> Dict[str, Any]:
    """
    Create or update widget avatar.
    
    Args:
        widget_id: Widget identifier
        avatar_image_url: URL of avatar image
        avatar_style: Avatar style (default, animated, custom)
    
    Returns:
        Avatar configuration
    """
    if not validate_uuid(widget_id):
        return format_error("Invalid widget ID format")
    
    try:
        result = await client._request(
            "POST",
            f"/convai/widgets/{widget_id}/avatar",
            json_data={
                "avatar_image_url": avatar_image_url,
                "style": avatar_style
            }
        )
        
        return format_success(
            "Widget avatar created",
            {"avatar": result}
        )
    except Exception as e:
        logger.error(f"Failed to create widget avatar: {e}")
        return format_error(str(e))


# ============================================================
# Voice Library Tools
# ============================================================

@mcp.tool()
async def get_shared_voices() -> Dict[str, Any]:
    """
    Get available shared voices from the voice library.
    
    Returns:
        List of available voices with details
    """
    try:
        result = await client._request("GET", "/voices/shared", use_cache=True)
        voices = result.get("voices", [])
        
        return format_success(
            f"Found {len(voices)} shared voices",
            {"count": len(voices), "voices": voices}
        )
    except Exception as e:
        logger.error(f"Failed to get shared voices: {e}")
        return format_error(str(e))


@mcp.tool()
async def add_shared_voice(
    voice_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a shared voice to your workspace.
    
    Args:
        voice_id: Voice identifier to add
        name: Custom name for the voice
        description: Voice description
    
    Returns:
        Added voice details
    """
    try:
        result = await client._request(
            "POST",
            "/voices/add",
            json_data={
                "voice_id": voice_id,
                "name": name,
                "description": description
            }
        )
        
        return format_success(
            f"Voice '{name or voice_id}' added to workspace",
            {"voice": result}
        )
    except Exception as e:
        logger.error(f"Failed to add shared voice: {e}")
        return format_error(str(e))


# ============================================================
# Template and Helper Tools
# ============================================================

@mcp.tool()
async def simulate_conversation(
    agent_id: str,
    user_message: str
) -> Dict[str, Any]:
    """
    Simulate a conversation with an agent for testing.
    
    Args:
        agent_id: Agent to test
        user_message: Test message to send
    
    Returns:
        Simulated agent response
    
    Examples:
        simulate_conversation("agent_abc123", "Hello, I need help")
        simulate_conversation("agent_xyz789", "What are your business hours?")
    
    Note: This creates a test conversation to validate agent behavior.
    
    API Endpoint: POST /convai/convai/simulations
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not user_message or len(user_message.strip()) < 2:
        return format_error("Message too short", "Provide a meaningful test message")
    
    try:
        result = await client._request(
            "POST",
            "/convai/convai/simulations",
            json_data={
                "agent_id": agent_id,
                "simulation_specification": {
                    "num_conversations": 1,
                    "conversation_specification": {
                        "customer": {
                            "prompt": {
                                "prompt": f"You are a user testing the agent. Send this message: {user_message}"
                            }
                        },
                        "max_messages": 2
                    }
                }
            }
        )
        
        return format_success(
            "Simulation created",
            {"simulation": result, "test_message": user_message}
        )
    except Exception as e:
        logger.error(f"Failed to simulate conversation: {e}")
        return format_error(str(e))


@mcp.tool()
async def list_voices() -> Dict[str, Any]:
    """
    List available voices with descriptions and characteristics.
    
    Returns:
        List of voices with details and suggested use cases
    
    Note: Returns both preset voices and any custom voices in your workspace.
    """
    try:
        # Get voices from API
        api_voices = await client._request("GET", "/voices", use_cache=True)
        voices_list = api_voices.get("voices", [])
        
        # Enhance with preset information
        enhanced_voices = []
        for voice in voices_list:
            voice_id = voice.get("voice_id")
            
            # Check if we have preset info
            preset_match = None
            for preset_name, preset_data in VOICE_PRESETS.items():
                if preset_data.get("voice_id") == voice_id:
                    preset_match = preset_name
                    voice["preset_name"] = preset_name
                    voice["preset_description"] = preset_data.get("description")
                    voice["use_cases"] = preset_data.get("use_cases")
                    voice["personality"] = preset_data.get("personality")
                    break
            
            enhanced_voices.append(voice)
        
        return format_success(
            f"Found {len(enhanced_voices)} voices",
            {
                "count": len(enhanced_voices),
                "voices": enhanced_voices,
                "presets_available": list(VOICE_PRESETS.keys())
            }
        )
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_prompt_template(template_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a prompt template for common use cases.
    
    Args:
        template_name: Template to retrieve (e.g., "customer_support", "appointment_booking")
                      Leave empty to list all available templates
    
    Returns:
        Template details or list of available templates
    
    Available Templates:
        - customer_support: Professional support agent
        - appointment_booking: Scheduling assistant
        - sales_qualification: Lead qualifier using BANT
        - technical_support: IT troubleshooting
        - survey_collector: Feedback gathering
        - product_information: Product Q&A
        - receptionist: Call routing
        - order_status: Order tracking
        - faq_assistant: FAQ responses
        - lead_capture: Website visitor conversion
    """
    if not PROMPT_TEMPLATES:
        return format_error("No templates available", "Template file may be missing")
    
    if template_name:
        template = PROMPT_TEMPLATES.get(template_name)
        if not template:
            return format_error(
                f"Template '{template_name}' not found",
                f"Available: {', '.join(PROMPT_TEMPLATES.keys())}"
            )
        return format_success(
            f"Retrieved template: {template_name}",
            {"template": template}
        )
    
    # Return all templates
    return format_success(
        f"Available prompt templates: {len(PROMPT_TEMPLATES)}",
        {
            "templates": list(PROMPT_TEMPLATES.keys()),
            "details": PROMPT_TEMPLATES
        }
    )


@mcp.tool()
async def get_voice_preset(preset_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get voice configuration presets for different personalities.
    
    Args:
        preset_name: Preset to retrieve (e.g., "professional", "friendly", "energetic")
                    Leave empty to list all presets
    
    Returns:
        Voice preset configuration or list of available presets
    
    Available Presets:
        - professional: Clear, confident business tone
        - friendly: Warm, approachable manner
        - energetic: Dynamic, enthusiastic delivery
        - calm: Soothing, patient voice
        - youthful: Modern, relatable tone
        - authoritative: Commanding, expert presence
        - neutral: Balanced, versatile
        - expressive: Emotional, varied delivery
        - efficient: Quick, concise communication
        - empathetic: Understanding, supportive
    """
    if not VOICE_PRESETS:
        return format_error("No presets available", "Preset file may be missing")
    
    if preset_name:
        preset = VOICE_PRESETS.get(preset_name)
        if not preset:
            return format_error(
                f"Preset '{preset_name}' not found",
                f"Available: {', '.join(VOICE_PRESETS.keys())}"
            )
        return format_success(
            f"Retrieved voice preset: {preset_name}",
            {"preset": preset}
        )
    
    # Return all presets
    return format_success(
        f"Available voice presets: {len(VOICE_PRESETS)}",
        {
            "presets": list(VOICE_PRESETS.keys()),
            "details": VOICE_PRESETS
        }
    )


@mcp.tool()
async def create_agent_from_template(
    template_name: str,
    custom_name: Optional[str] = None,
    modifications: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an agent from a pre-configured template.
    
    Args:
        template_name: Template to use (e.g., "customer_support_pro", "appointment_scheduler")
        custom_name: Override the default agent name
        modifications: Optional modifications to template settings
    
    Returns:
        Created agent details
    
    Available Templates:
        - customer_support_pro: Full support agent with escalation
        - appointment_scheduler: Smart booking assistant
        - sales_qualifier: B2B lead qualification (BANT)
        - tech_support_tier1: L1 technical support
        - virtual_receptionist: Call routing assistant
        - survey_bot: Feedback collector
        - lead_capture_web: Website visitor converter
        - order_tracker: E-commerce order status
        - hr_screening: Initial candidate screening
        - product_advisor: Product recommendations
    
    Examples:
        create_agent_from_template("customer_support_pro")
        create_agent_from_template("appointment_scheduler", "My Booking Bot")
        create_agent_from_template("sales_qualifier", modifications={"temperature": 0.9})
    """
    if not AGENT_TEMPLATES:
        return format_error("No templates available", "Template file may be missing")
    
    template = AGENT_TEMPLATES.get(template_name)
    if not template:
        return format_error(
            f"Template '{template_name}' not found",
            f"Available: {', '.join(AGENT_TEMPLATES.keys())}"
        )
    
    try:
        # Extract configuration
        config = template.get("config", {})
        
        # Apply modifications if provided
        if modifications:
            for key, value in modifications.items():
                if key in config:
                    config[key] = value
                elif key in config.get("voice_settings", {}):
                    config["voice_settings"][key] = value
        
        # Create the agent
        name = custom_name or template.get("name", "Agent from Template")
        
        # Get voice settings
        voice_settings = config.get("voice_settings", {})
        
        # Create agent with base configuration
        result = await create_agent(
            name=name,
            system_prompt=config.get("system_prompt"),
            first_message=config.get("first_message"),
            voice_id=config.get("voice_id"),
            llm_model=config.get("llm_model"),
            temperature=str(config.get("temperature", 0.7)),
            language=config.get("language", "en")
        )
        
        # If agent created successfully and we have voice settings, configure voice
        if result.get("success") and voice_settings:
            agent_id = result.get("data", {}).get("agent_id")
            if agent_id:
                await configure_voice(
                    agent_id=agent_id,
                    voice_id=config.get("voice_id"),
                    stability=str(voice_settings.get("stability", 0.5)),
                    similarity_boost=str(voice_settings.get("similarity_boost", 0.8)),
                    speed=str(voice_settings.get("speed", 1.0))
                )
        
        return format_success(
            f"Agent created from template: {template_name}",
            {
                "agent": result.get("data"),
                "template_used": template_name,
                "description": template.get("description")
            }
        )
    except Exception as e:
        logger.error(f"Failed to create agent from template: {e}")
        return format_error(str(e))


@mcp.tool()
async def suggest_voice_for_use_case(use_case: str) -> Dict[str, Any]:
    """
    Suggest the best voice configuration for a specific use case.
    
    Args:
        use_case: Description of the use case or business context
    
    Returns:
        Recommended voice configurations with rationale
    
    Examples:
        suggest_voice_for_use_case("customer support for tech company")
        suggest_voice_for_use_case("friendly appointment booking")
        suggest_voice_for_use_case("serious legal consultation")
    """
    use_case_lower = use_case.lower()
    suggestions = []
    
    # Check each preset for matching use cases
    for preset_name, preset_data in VOICE_PRESETS.items():
        score = 0
        matches = []
        
        # Check use cases
        for uc in preset_data.get("use_cases", []):
            if uc.lower() in use_case_lower or use_case_lower in uc.lower():
                score += 2
                matches.append(f"use case: {uc}")
        
        # Check personality traits
        personality = preset_data.get("personality", "")
        for trait in personality.split(", "):
            if trait.lower() in use_case_lower:
                score += 1
                matches.append(f"trait: {trait}")
        
        # Check description
        if any(word in use_case_lower for word in preset_name.lower().split("_")):
            score += 1
            matches.append(f"name match: {preset_name}")
        
        if score > 0:
            suggestions.append({
                "preset": preset_name,
                "score": score,
                "voice_id": preset_data.get("voice_id"),
                "description": preset_data.get("description"),
                "matches": matches,
                "config": {
                    "stability": preset_data.get("stability"),
                    "similarity_boost": preset_data.get("similarity_boost"),
                    "speed": preset_data.get("speed")
                }
            })
    
    # Sort by score
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    
    if not suggestions:
        # Provide default suggestion
        return format_success(
            "No specific match found, suggesting default professional voice",
            {
                "recommendation": VOICE_PRESETS.get("professional"),
                "reason": "Professional voice works well for most business contexts"
            }
        )
    
    return format_success(
        f"Found {len(suggestions)} voice suggestions for: {use_case}",
        {
            "best_match": suggestions[0] if suggestions else None,
            "alternatives": suggestions[1:3] if len(suggestions) > 1 else [],
            "all_suggestions": suggestions
        }
    )


@mcp.tool()
async def validate_prompt(system_prompt: str) -> Dict[str, Any]:
    """
    Validate and improve an agent's system prompt.
    
    Args:
        system_prompt: The prompt to validate and analyze
    
    Returns:
        Analysis with suggestions for improvement
    
    Checks for:
        - Clarity and structure
        - Specific instructions
        - Personality definition
        - Escalation handling
        - Length appropriateness
    """
    issues = []
    suggestions = []
    score = 100
    
    # Check length
    prompt_length = len(system_prompt)
    if prompt_length < 50:
        issues.append("Prompt is too short (< 50 chars)")
        suggestions.append("Add more specific instructions about the agent's role and behavior")
        score -= 20
    elif prompt_length > 2000:
        issues.append("Prompt may be too long (> 2000 chars)")
        suggestions.append("Consider breaking into clear sections or removing redundancy")
        score -= 10
    
    # Check for key components
    prompt_lower = system_prompt.lower()
    
    # Role definition
    if not any(word in prompt_lower for word in ["you are", "your role", "act as", "you're"]):
        issues.append("Missing clear role definition")
        suggestions.append("Start with 'You are a...' to clearly define the agent's role")
        score -= 15
    
    # Behavioral instructions
    if not any(word in prompt_lower for word in ["help", "assist", "support", "provide", "answer"]):
        issues.append("Missing action verbs")
        suggestions.append("Include specific actions the agent should take")
        score -= 10
    
    # Tone/personality
    if not any(word in prompt_lower for word in ["friendly", "professional", "helpful", "polite", "tone", "manner"]):
        issues.append("No personality or tone specified")
        suggestions.append("Define the communication style (e.g., 'maintain a friendly, professional tone')")
        score -= 10
    
    # Escalation or limitations
    if not any(word in prompt_lower for word in ["don't know", "unsure", "escalate", "cannot", "unable"]):
        suggestions.append("Consider adding guidance for handling unknown questions or escalation")
        score -= 5
    
    # Structure check
    if "\n" in system_prompt and system_prompt.count("\n") > 1:
        # Has structure
        score += 5
    else:
        suggestions.append("Consider using numbered lists or paragraphs for better organization")
    
    # Specific examples
    if any(word in prompt_lower for word in ["example", "such as", "like", "including"]):
        score += 5
    else:
        suggestions.append("Add specific examples of expected behavior or responses")
    
    # Calculate final score
    score = max(0, min(100, score))
    
    # Determine quality level
    if score >= 80:
        quality = "Excellent"
    elif score >= 60:
        quality = "Good"
    elif score >= 40:
        quality = "Fair"
    else:
        quality = "Needs Improvement"
    
    return format_success(
        f"Prompt validation complete - Quality: {quality}",
        {
            "score": score,
            "quality": quality,
            "character_count": prompt_length,
            "issues": issues if issues else ["No major issues found"],
            "suggestions": suggestions if suggestions else ["Prompt is well-structured"],
            "has_role": "you are" in prompt_lower,
            "has_instructions": any(word in prompt_lower for word in ["help", "assist"]),
            "has_personality": any(word in prompt_lower for word in ["friendly", "professional"]),
            "has_structure": "\n" in system_prompt
        }
    )


# ============================================================
# Main entry point
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ElevenLabs Agents MCP Server")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode - verify all components
        print(f"Server: elevenlabs-agents v0.3.0")
        print(f"Tools: {len(mcp.tools)} registered")
        print(f"Config: API key {Config.mask_api_key()}")
        print(f"Templates: {len(PROMPT_TEMPLATES)} prompts, {len(VOICE_PRESETS)} voices, {len(AGENT_TEMPLATES)} agents")
        print("All components loaded successfully!")
    else:
        # Run server
        logger.info("Starting MCP server...")
        mcp.run()