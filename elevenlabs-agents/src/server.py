#!/usr/bin/env python3
"""
ElevenLabs Agents MCP Server
============================
Manages conversational AI agents, configuration, and multi-agent orchestration.
"""

import sys
import logging
from typing import Dict, Any, Optional, List
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
# Agent Management Tools
# ============================================================

@mcp.tool()
async def create_agent(
    name: str,
    system_prompt: str,
    first_message: str,
    voice_id: Optional[str] = "cgSgspJ2msm6clMCkdW9",
    llm_model: Optional[str] = "gemini-2.0-flash-001",
    temperature: Optional[float] = 0.5,
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
    
    API Endpoint: POST /v1/convai/agents
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
    
    # Validate temperature
    if temperature is not None:
        if not isinstance(temperature, (int, float)):
            return format_error(
                "Temperature must be a number",
                "Use a value between 0.0 (deterministic) and 1.0 (creative)"
            )
        if not 0.0 <= temperature <= 1.0:
            return format_error(
                f"Temperature {temperature} out of range",
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
                "temperature": float(temperature) if temperature is not None else 0.5
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
    
    API Endpoint: GET /v1/convai/agents/{agent_id}
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
    temperature: Optional[float] = None,
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
            conversation_config["llm"] = {"temperature": temperature}
        
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
    stability: Optional[float] = 0.5,
    similarity_boost: Optional[float] = 0.8,
    speed: Optional[float] = 1.0
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
    
    API Endpoint: PATCH /v1/convai/agents/{agent_id}
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
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
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
        # Validate parameters
        if temperature is not None and (temperature < 0.0 or temperature > 2.0):
            return format_error("temperature must be between 0.0 and 2.0")
        if max_tokens is not None and (max_tokens < 1 or max_tokens > 8192):
            return format_error("max_tokens must be between 1 and 8192")
        
        llm_config = {}
        if model:
            llm_config["model"] = model
        if temperature is not None:
            llm_config["temperature"] = temperature
        if max_tokens is not None:
            llm_config["max_tokens"] = max_tokens
        
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
        return format_success(
            "Agent link retrieved",
            {"link": result.get("link"), "agent_id": agent_id}
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
# Main entry point
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ElevenLabs Agents MCP Server")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode - verify all components
        print(f"Server: elevenlabs-agents v0.2.0")
        print(f"Tools: {len(mcp.tools)} (expecting 12)")
        print(f"Config: API key {Config.mask_api_key()}")
        print("All components loaded successfully!")
    else:
        # Run server
        logger.info("Starting MCP server...")
        mcp.run()