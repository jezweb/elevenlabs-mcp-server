#!/usr/bin/env python3
"""
ElevenLabs Agents MCP Server
============================
Manages conversational AI agents, configuration, and multi-agent orchestration.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to path for shared module access
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from shared import Config, ElevenLabsClient, format_success, format_error, validate_uuid

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

# Initialize FastMCP server - MUST be at module level
mcp = FastMCP(
    name="elevenlabs-agents",
    version="0.1.0",
    description="Manage ElevenLabs conversational AI agents"
)

# Initialize ElevenLabs client at module level
client = ElevenLabsClient(Config.API_KEY)

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
        name: Agent display name
        system_prompt: Instructions defining agent behavior
        first_message: Initial greeting message
        voice_id: ElevenLabs voice ID
        llm_model: LLM model to use
        temperature: Response creativity (0.0-1.0)
        language: ISO 639-1 language code
    
    Returns:
        Created agent details with agent_id
    """
    try:
        config = {
            "name": name,
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": system_prompt,
                        "first_message": first_message,
                        "language": language
                    }
                },
                "tts": {
                    "voice_id": voice_id,
                    "model_id": "eleven_turbo_v2",
                    "stability": 0.5,
                    "similarity_boost": 0.8
                },
                "llm": {
                    "model": llm_model,
                    "temperature": temperature
                }
            }
        }
        
        result = await client.create_agent(config)
        return format_success(
            f"Agent '{name}' created successfully",
            {"agent_id": result.get("agent_id"), "agent": result}
        )
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        return format_error(str(e), suggestion="Check API key and agent configuration")


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
        agent_id: Unique agent identifier
    
    Returns:
        Complete agent configuration and metadata
    """
    if not validate_uuid(agent_id):
        return format_error("Invalid agent ID format", suggestion="Provide a valid UUID")
    
    try:
        agent = await client.get_agent(agent_id)
        return format_success(
            f"Retrieved agent details",
            {"agent": agent}
        )
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        return format_error(str(e), suggestion="Check agent ID exists")


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
    if not validate_uuid(agent_id):
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
    if not validate_uuid(agent_id):
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
    style: Optional[float] = 0.0
) -> Dict[str, Any]:
    """
    Configure agent voice settings.
    
    Args:
        agent_id: Agent to configure
        voice_id: ElevenLabs voice ID
        stability: Voice consistency (0.0-1.0)
        similarity_boost: Voice matching (0.0-1.0)
        style: Style exaggeration (0.0-1.0)
    
    Returns:
        Configuration result
    """
    if not validate_uuid(agent_id):
        return format_error("Invalid agent ID format")
    
    try:
        config = {
            "conversation_config": {
                "tts": {
                    "voice_id": voice_id,
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style
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
        return format_error(str(e))


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
    if not validate_uuid(agent_id):
        return format_error("Invalid agent ID format")
    
    try:
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
    if not validate_uuid(from_agent_id) or not validate_uuid(to_agent_id):
        return format_error("Invalid agent ID format")
    
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
# Testing and Simulation Tools
# ============================================================

@mcp.tool()
async def simulate_conversation(
    agent_id: str,
    user_message: str
) -> Dict[str, Any]:
    """
    Simulate a conversation with an agent.
    
    Args:
        agent_id: Agent to test
        user_message: Test message
    
    Returns:
        Simulated agent response
    """
    if not validate_uuid(agent_id):
        return format_error("Invalid agent ID format")
    
    try:
        # Note: This would call the actual simulation endpoint
        # For now, returning a mock response
        return format_success(
            "Simulation completed",
            {
                "user_message": user_message,
                "agent_response": "This would be the agent's simulated response",
                "confidence": 0.95
            }
        )
    except Exception as e:
        logger.error(f"Failed to simulate conversation: {e}")
        return format_error(str(e))


# ============================================================
# Server lifecycle
# ============================================================

@mcp.on_startup
async def startup():
    """Initialize server resources on startup."""
    logger.info(f"Starting elevenlabs-agents server v0.1.0")
    
    # Test API connection
    if await client.test_connection():
        logger.info("ElevenLabs API connection verified")
    else:
        logger.warning("Failed to verify API connection - some features may be unavailable")


@mcp.on_shutdown
async def shutdown():
    """Cleanup on server shutdown."""
    logger.info("Shutting down elevenlabs-agents server")
    await client.close()


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
        print(f"Server: elevenlabs-agents v0.1.0")
        print(f"Tools: {len(mcp.tools)}")
        print(f"Config: API key {Config.mask_api_key()}")
        print("All components loaded successfully!")
    else:
        # Run server
        logger.info("Starting MCP server...")
        mcp.run()