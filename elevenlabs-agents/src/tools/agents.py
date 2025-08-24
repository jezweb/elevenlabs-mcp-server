"""
Agent management tools for ElevenLabs conversational AI.
"""

import logging
from typing import Dict, Any, Optional
from shared import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def create_agent(
    client,
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
        client: ElevenLabs API client
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


async def list_agents(client) -> Dict[str, Any]:
    """
    List all conversational AI agents.
    
    Args:
        client: ElevenLabs API client
    
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


async def get_agent(client, agent_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific agent.
    
    Args:
        client: ElevenLabs API client
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


async def update_agent(
    client,
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
        client: ElevenLabs API client
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


async def delete_agent(client, agent_id: str) -> Dict[str, Any]:
    """
    Delete an agent.
    
    Args:
        client: ElevenLabs API client
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


async def update_system_prompt(
    client,
    agent_id: str,
    system_prompt: str
) -> Dict[str, Any]:
    """
    Update an agent's system prompt.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to update
        system_prompt: New system instructions
    
    Returns:
        Update confirmation
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not system_prompt or len(system_prompt) < 10:
        return format_error("System prompt too short (min 10 characters)")
    
    try:
        update_config = {
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": system_prompt
                    }
                }
            }
        }
        
        result = await client.update_agent(agent_id, update_config)
        return format_success(
            "System prompt updated successfully",
            {"agent": result}
        )
    except Exception as e:
        logger.error(f"Failed to update system prompt: {e}")
        return format_error(str(e))


async def duplicate_agent(client, agent_id: str, new_name: str) -> Dict[str, Any]:
    """
    Create a copy of an existing agent with a new name.
    
    Args:
        client: ElevenLabs API client
        agent_id: Agent to duplicate
        new_name: Name for the new agent
    
    Returns:
        New agent details
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if not new_name or not new_name.strip():
        return format_error("New agent name is required")
    
    try:
        # Get the original agent's configuration
        original = await client.get_agent(agent_id)
        
        # Extract configuration
        config = original.get("conversation_config", {})
        
        # Create new agent with same config but new name
        agent_data = {
            "conversation_config": config,
            "name": new_name
        }
        
        result = await client.create_agent(agent_data)
        
        return format_success(
            f"Agent duplicated as '{new_name}'",
            {
                "original_id": agent_id,
                "new_id": result.get("agent_id"),
                "name": new_name
            }
        )
    except Exception as e:
        logger.error(f"Failed to duplicate agent: {e}")
        return format_error(str(e))