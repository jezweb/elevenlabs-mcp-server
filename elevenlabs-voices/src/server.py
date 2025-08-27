"""
ElevenLabs Voices MCP Server
============================
Voice resource management server for ElevenLabs Conversational AI platform.

This server handles voice-related operations including:
- Voice CRUD operations (create, read, update, delete)
- Text-to-voice design and generation
- Instant Voice Cloning (IVC)
- Voice library management and sharing
- Voice configuration and settings

The server is designed to work with the ElevenLabs Conversational AI API
and follows FastMCP patterns for cloud deployment.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="elevenlabs-voices",
    instructions="""ElevenLabs Voices MCP Server - Voice resource management.

This server provides tools for:
- Voice CRUD operations (create, read, update, delete)
- Text-to-Voice design and generation
- Instant Voice Cloning (IVC) from audio samples
- Voice library search and management
- Voice settings and configuration

Voice Settings Guide:
- Stability (0.0-1.0): 0.3=expressive, 0.7=balanced, 0.9=consistent
- Similarity Boost (0.0-1.0): 0.5=creative, 0.8=natural, 1.0=strict
- Style (0.0-1.0): 0.0=natural, 0.5=enhanced, 1.0=exaggerated"""
)

# Import all tools - using absolute imports for FastMCP compatibility
from tools import (
    # Voice management tools
    get_voice,
    list_voices,
    delete_voice,
    # Voice design tools  
    text_to_voice,
    create_voice_from_preview,
    # IVC tools
    instant_voice_clone,
    # Voice library tools
    search_voice_library,
    add_shared_voice,
    get_shared_voices,
    # Voice settings tools
    get_voice_settings
)

# Voice Management Tools
@mcp.tool()
async def get_voice_details(voice_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific voice.
    
    Args:
        voice_id: ElevenLabs voice ID to retrieve
        
    Returns:
        Voice details including settings, samples, and metadata
    """
    return await get_voice(voice_id)

@mcp.tool()
async def list_user_voices(page_size: int = 30) -> Dict[str, Any]:
    """
    List all voices in the user's voice library.
    
    Args:
        page_size: Number of voices per page (1-100)
        
    Returns:
        List of user's voices with metadata
    """
    return await list_voices(page_size)

@mcp.tool()
async def delete_user_voice(voice_id: str) -> Dict[str, Any]:
    """
    Delete a voice from the user's library.
    
    Args:
        voice_id: Voice ID to delete
        
    Returns:
        Deletion confirmation
    """
    return await delete_voice(voice_id)

# Voice Design Tools
@mcp.tool()
async def design_voice_from_text(
    description: str,
    text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create voice previews from a text description.
    
    Args:
        description: Description of the desired voice characteristics
        text: Custom text for preview (auto-generated if not provided)
        
    Returns:
        Generated voice previews with IDs for creation
    """
    return await text_to_voice(description, text)

@mcp.tool()
async def create_voice_from_design(
    generated_voice_id: str,
    name: str,
    description: str
) -> Dict[str, Any]:
    """
    Create a permanent voice from a generated preview.
    
    Args:
        generated_voice_id: ID from text_to_voice generation
        name: Name for the new voice
        description: Description of the voice
        
    Returns:
        Created voice details
    """
    return await create_voice_from_preview(generated_voice_id, name, description)

# IVC (Instant Voice Cloning) Tools
@mcp.tool()
async def clone_voice_instantly(
    name: str,
    audio_files: List[str],
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clone a voice using audio samples (Instant Voice Cloning).
    
    Args:
        name: Name for the cloned voice
        audio_files: List of audio file paths for cloning
        description: Optional description for the voice
        
    Returns:
        Cloned voice details
    """
    return await instant_voice_clone(name, audio_files, description)

# Voice Library Tools
@mcp.tool()
async def search_public_voices(
    query: str,
    page: int = 0,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Search the public voice library.
    
    Args:
        query: Search terms for voice discovery
        page: Page number for pagination
        page_size: Results per page
        
    Returns:
        Search results from public voice library
    """
    return await search_voice_library(query, page, page_size)

@mcp.tool()
async def add_public_voice(
    voice_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a shared voice from the public library to user's collection.
    
    Args:
        voice_id: Public voice ID to add
        name: Custom name for the voice
        description: Custom description
        
    Returns:
        Added voice details
    """
    return await add_shared_voice(voice_id, name, description)

@mcp.tool()
async def get_public_voices() -> Dict[str, Any]:
    """
    Get available shared voices from the voice library.
    
    Returns:
        List of available public voices
    """
    return await get_shared_voices()

# Voice Settings Tools  
@mcp.tool()
async def get_voice_configuration(voice_id: str) -> Dict[str, Any]:
    """
    Get current voice settings and configuration.
    
    Args:
        voice_id: Voice ID to get settings for
        
    Returns:
        Current voice configuration
    """
    return await get_voice_settings(voice_id)

if __name__ == "__main__":
    import uvicorn
    
    # Check for required environment variables
    if not os.getenv("ELEVENLABS_API_KEY"):
        logger.error("ELEVENLABS_API_KEY environment variable is required")
        sys.exit(1)
        
    logger.info("Starting ElevenLabs Voices MCP Server")
    logger.info("Server handles voice management, cloning, library, and configuration")
    
    uvicorn.run(mcp.server, host="127.0.0.1", port=3001)