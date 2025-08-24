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
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from shared import Config, ElevenLabsClient, format_success, format_error, validate_uuid, validate_elevenlabs_id

# Import all tools
from tools import (
    # Agent management
    create_agent,
    list_agents,
    get_agent,
    update_agent,
    delete_agent,
    update_system_prompt,
    duplicate_agent,
    # Voice configuration
    configure_voice,
    set_llm_config,
    list_voices,
    get_shared_voices,
    add_shared_voice,
    # Transfers
    add_transfer_to_agent,
    configure_webhook,
    # Templates
    get_agent_template,
    list_agent_templates,
    get_prompt_template,
    get_voice_preset,
    create_agent_from_template,
    suggest_voice_for_use_case,
    validate_prompt,
    # Testing
    simulate_conversation,
    create_test,
    get_test_results,
    # Widgets
    get_widget_link,
    get_agent_link,
    get_widget,
    create_widget_avatar,
    calculate_llm_usage
)

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
# Register Agent Management Tools
# ============================================================

@mcp.tool()
async def create_agent_tool(
    name: str,
    system_prompt: str,
    first_message: str,
    voice_id: Optional[str] = "cgSgspJ2msm6clMCkdW9",
    llm_model: Optional[str] = "gemini-2.0-flash-001",
    temperature: Optional[str] = "0.5",
    language: Optional[str] = "en"
) -> Dict[str, Any]:
    """Create a new conversational AI agent."""
    return await create_agent(client, name, system_prompt, first_message, voice_id, llm_model, temperature, language)

@mcp.tool()
async def list_agents_tool() -> Dict[str, Any]:
    """List all conversational AI agents."""
    return await list_agents(client)

@mcp.tool()
async def get_agent_tool(agent_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific agent."""
    return await get_agent(client, agent_id)

@mcp.tool()
async def update_agent_tool(
    agent_id: str,
    name: Optional[str] = None,
    system_prompt: Optional[str] = None,
    first_message: Optional[str] = None,
    temperature: Optional[str] = None,
    voice_id: Optional[str] = None
) -> Dict[str, Any]:
    """Update agent configuration."""
    return await update_agent(client, agent_id, name, system_prompt, first_message, temperature, voice_id)

@mcp.tool()
async def delete_agent_tool(agent_id: str) -> Dict[str, Any]:
    """Delete an agent."""
    return await delete_agent(client, agent_id)

@mcp.tool()
async def update_system_prompt_tool(agent_id: str, system_prompt: str) -> Dict[str, Any]:
    """Update an agent's system prompt."""
    return await update_system_prompt(client, agent_id, system_prompt)

@mcp.tool()
async def duplicate_agent_tool(agent_id: str, new_name: str) -> Dict[str, Any]:
    """Create a copy of an existing agent with a new name."""
    return await duplicate_agent(client, agent_id, new_name)

# ============================================================
# Register Voice Configuration Tools
# ============================================================

@mcp.tool()
async def configure_voice_tool(
    agent_id: str,
    voice_id: str,
    stability: Optional[str] = "0.5",
    similarity_boost: Optional[str] = "0.8",
    speed: Optional[str] = "1.0"
) -> Dict[str, Any]:
    """Configure agent voice settings."""
    return await configure_voice(client, agent_id, voice_id, stability, similarity_boost, speed)

@mcp.tool()
async def set_llm_config_tool(
    agent_id: str,
    model: Optional[str] = None,
    temperature: Optional[str] = None,
    max_tokens: Optional[str] = None
) -> Dict[str, Any]:
    """Configure agent LLM settings."""
    return await set_llm_config(client, agent_id, model, temperature, max_tokens)

@mcp.tool()
async def list_voices_tool() -> Dict[str, Any]:
    """List available ElevenLabs voices."""
    return await list_voices(client)

@mcp.tool()
async def get_shared_voices_tool() -> Dict[str, Any]:
    """Get list of voices shared with your account."""
    return await get_shared_voices(client)

@mcp.tool()
async def add_shared_voice_tool(voice_id: str, agent_id: str) -> Dict[str, Any]:
    """Add a shared voice to an agent."""
    return await add_shared_voice(client, voice_id, agent_id)

# ============================================================
# Register Transfer Tools
# ============================================================

@mcp.tool()
async def add_transfer_to_agent_tool(
    from_agent_id: str,
    to_agent_id: str,
    conditions: str,
    message: Optional[str] = "I'll transfer you to a specialist"
) -> Dict[str, Any]:
    """Configure agent-to-agent transfer."""
    return await add_transfer_to_agent(client, from_agent_id, to_agent_id, conditions, message)

@mcp.tool()
async def configure_webhook_tool(
    agent_id: str,
    webhook_url: str,
    events: Optional[list] = None
) -> Dict[str, Any]:
    """Configure webhook for agent events."""
    return await configure_webhook(client, agent_id, webhook_url, events)

# ============================================================
# Register Template Tools
# ============================================================

@mcp.tool()
async def get_agent_template_tool(template_name: str) -> Dict[str, Any]:
    """Get a complete agent template."""
    return await get_agent_template(AGENT_TEMPLATES, template_name)

@mcp.tool()
async def list_agent_templates_tool() -> Dict[str, Any]:
    """List all available agent templates."""
    return await list_agent_templates(AGENT_TEMPLATES)

@mcp.tool()
async def get_prompt_template_tool(use_case: str) -> Dict[str, Any]:
    """Get a prompt template for a specific use case."""
    return await get_prompt_template(PROMPT_TEMPLATES, use_case)

@mcp.tool()
async def get_voice_preset_tool(preset_name: str) -> Dict[str, Any]:
    """Get voice configuration preset."""
    return await get_voice_preset(VOICE_PRESETS, preset_name)

@mcp.tool()
async def create_agent_from_template_tool(
    template_name: str,
    agent_name: str,
    customizations: Optional[dict] = None
) -> Dict[str, Any]:
    """Create agent using a template."""
    return await create_agent_from_template(client, AGENT_TEMPLATES, template_name, agent_name, customizations)

@mcp.tool()
async def suggest_voice_for_use_case_tool(use_case: str) -> Dict[str, Any]:
    """Suggest voices for a specific use case."""
    return await suggest_voice_for_use_case(VOICE_PRESETS, use_case)

@mcp.tool()
async def validate_prompt_tool(
    prompt: str,
    min_length: int = 10,
    max_length: int = 2000
) -> Dict[str, Any]:
    """Validate a system prompt."""
    return await validate_prompt(prompt, min_length, max_length)

# ============================================================
# Register Testing Tools
# ============================================================

@mcp.tool()
async def simulate_conversation_tool(agent_id: str, user_message: str) -> Dict[str, Any]:
    """Simulate a conversation with an agent for testing."""
    return await simulate_conversation(client, agent_id, user_message)

@mcp.tool()
async def create_test_tool(agent_id: str, test_name: str, test_cases: list) -> Dict[str, Any]:
    """Create a test suite for an agent."""
    return await create_test(client, agent_id, test_name, test_cases)

@mcp.tool()
async def get_test_results_tool(test_id: str) -> Dict[str, Any]:
    """Get results from a test run."""
    return await get_test_results(client, test_id)

# ============================================================
# Register Widget Tools
# ============================================================

@mcp.tool()
async def get_widget_link_tool(agent_id: str, settings: Optional[dict] = None) -> Dict[str, Any]:
    """Get embeddable widget link for an agent."""
    return await get_widget_link(client, agent_id, settings)

@mcp.tool()
async def get_agent_link_tool(agent_id: str) -> Dict[str, Any]:
    """Get a shareable link for an agent."""
    return await get_agent_link(client, agent_id)

@mcp.tool()
async def get_widget_tool(agent_id: str) -> Dict[str, Any]:
    """Get widget configuration for an agent."""
    return await get_widget(client, agent_id)

@mcp.tool()
async def create_widget_avatar_tool(agent_id: str, avatar_url: str) -> Dict[str, Any]:
    """Set custom avatar for agent widget."""
    return await create_widget_avatar(client, agent_id, avatar_url)

@mcp.tool()
async def calculate_llm_usage_tool(
    agent_id: str,
    conversation_count: int = 100,
    avg_messages_per_conversation: int = 10
) -> Dict[str, Any]:
    """Calculate estimated LLM usage and costs."""
    return await calculate_llm_usage(client, agent_id, conversation_count, avg_messages_per_conversation)

# ============================================================
# Resources
# ============================================================

@mcp.resource("templates://agent-templates")
async def get_templates_resource() -> str:
    """Get all agent templates as a resource."""
    return json.dumps(AGENT_TEMPLATES, indent=2)

@mcp.resource("templates://prompt-templates")
async def get_prompts_resource() -> str:
    """Get all prompt templates as a resource."""
    return json.dumps(PROMPT_TEMPLATES, indent=2)

@mcp.resource("templates://voice-presets")
async def get_voices_resource() -> str:
    """Get all voice presets as a resource."""
    return json.dumps(VOICE_PRESETS, indent=2)

# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp, host="0.0.0.0", port=8000)