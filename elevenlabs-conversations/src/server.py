"""ElevenLabs Conversations MCP Server.

Provides tools for managing conversation history and playback.
"""

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    Config,
    ElevenLabsClient,
    setup_logging
)

# Import all tools
from src.tools import (
    # Conversations
    list_conversations,
    get_conversation,
    get_transcript,
    delete_conversation,
    # Feedback
    send_feedback,
    get_feedback_summary,
    # Playback
    get_conversation_audio,
    get_signed_url,
    get_conversation_token,
    # Analytics
    analyze_conversation,
    performance_report,
    export_conversations
)

# Setup logging
logger = setup_logging(__name__)

# Validate configuration
if not Config.API_KEY:
    logger.error("ELEVENLABS_API_KEY not set")
    sys.exit(1)

# Initialize ElevenLabs client at module level
client = ElevenLabsClient(Config.API_KEY)

# Initialize FastMCP server
mcp = FastMCP(
    name="elevenlabs-conversations",
    instructions="Manage ElevenLabs conversation history and playback"
)


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for the MCP server."""
    # Startup
    logger.info("Starting ElevenLabs Conversations MCP Server")
    
    # Test API connection
    try:
        await client._request("GET", "/user")
        logger.info("✓ ElevenLabs API connection successful")
    except Exception as e:
        logger.error(f"✗ Failed to connect to ElevenLabs API: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ElevenLabs Conversations MCP Server")


# Register the lifespan with FastMCP
mcp.lifespan_manager = lifespan

# ============================================================
# Resource Loading Helpers
# ============================================================

def load_resource(filename: str) -> Dict[str, Any]:
    """Load a JSON resource file with proper error handling."""
    resource_path = Path(__file__).parent / "resources" / filename
    try:
        if not resource_path.exists():
            logger.error(f"Resource file not found: {resource_path}")
            return {}
        
        with open(resource_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded {filename}: {len(data)} items")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in {filename}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading resource {filename}: {e}")
        return {}

# Load templates at module level for efficiency
CONVERSATION_TEMPLATES = load_resource("conversation_templates.json")
EXPORT_TEMPLATES = load_resource("export_templates.json")
FEEDBACK_TEMPLATES = load_resource("feedback_templates.json")


# Conversation Management Tools

@mcp.tool()
async def list_conversations_tool(
    agent_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List conversations.
    
    Args:
        agent_id: Filter by agent
        limit: Maximum results (1-100)
        offset: Pagination offset
    
    Returns:
        List of conversations with metadata
    """
    return await list_conversations(client, agent_id, limit, offset)


@mcp.tool()
async def get_conversation_tool(
    conversation_id: str
) -> Dict[str, Any]:
    """
    Get detailed conversation data.
    
    Args:
        conversation_id: Conversation to retrieve
    
    Returns:
        Complete conversation details including transcript
    """
    return await get_conversation(client, conversation_id)


@mcp.tool()
async def get_transcript_tool(
    conversation_id: str
) -> Dict[str, Any]:
    """
    Get conversation transcript.
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        Text transcript
    """
    return await get_transcript(client, conversation_id)


@mcp.tool()
async def delete_conversation_tool(
    conversation_id: str
) -> Dict[str, Any]:
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation to delete
    
    Returns:
        Deletion confirmation
    """
    return await delete_conversation(client, conversation_id)


# Feedback Tools

@mcp.tool()
async def send_feedback_tool(
    conversation_id: str,
    rating: int,
    feedback_text: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Send feedback for a conversation.
    
    Args:
        conversation_id: Conversation to rate (format: conv_XXXX)
        rating: Rating (1-5, where 1=poor, 5=excellent)
        feedback_text: Optional detailed feedback
        metadata: Additional metadata (tags, categories, etc.)
    
    Returns:
        Feedback confirmation
    
    Examples:
        send_feedback("conv_abc123", 5, "Great interaction!")
        send_feedback("conv_xyz789", 2, "Agent was confused", 
                     metadata={"issue": "misunderstanding"})
    
    Rating Scale:
        1 - Poor: Major issues, failed interaction
        2 - Below Average: Some problems, partially successful
        3 - Average: Acceptable, met basic needs
        4 - Good: Effective interaction, minor issues only
        5 - Excellent: Perfect interaction, exceeded expectations
    """
    return await send_feedback(client, conversation_id, rating, feedback_text, metadata)


@mcp.tool()
async def get_feedback_summary_tool(
    agent_id: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get feedback summary for an agent.
    
    Args:
        agent_id: Agent to analyze
        days: Number of days to include (1-30)
    
    Returns:
        Feedback summary with ratings distribution
    """
    return await get_feedback_summary(client, agent_id, days)


# Playback Tools

@mcp.tool()
async def get_conversation_audio_tool(
    conversation_id: str,
    format: str = "mp3"
) -> Dict[str, Any]:
    """
    Get conversation audio download URL.
    
    Args:
        conversation_id: Conversation ID (format: conv_XXXX)
        format: Audio format - "mp3" (default) or "wav"
            - mp3: Smaller file size, good for storage/sharing
            - wav: Uncompressed, higher quality for processing
    
    Returns:
        Audio download URL with expiration time
    
    Examples:
        get_conversation_audio("conv_abc123")  # Default MP3
        get_conversation_audio("conv_xyz789", "wav")  # WAV format
    
    Note: URLs expire after ~1 hour. Download promptly or use get_signed_url for longer TTL.
    """
    return await get_conversation_audio(client, conversation_id, format)


@mcp.tool()
async def get_signed_url_tool(
    conversation_id: str,
    ttl: int = 3600
) -> Dict[str, Any]:
    """
    Get signed URL for secure conversation playback.
    
    Args:
        conversation_id: Conversation ID (format: conv_XXXX)
        ttl: URL time-to-live in seconds (60-86400, default: 3600)
            - 60 = 1 minute (minimum)
            - 3600 = 1 hour (default)
            - 86400 = 24 hours (maximum)
    
    Returns:
        Signed URL with expiration time for secure access
    
    Examples:
        get_signed_url("conv_abc123")  # 1 hour TTL
        get_signed_url("conv_xyz789", 7200)  # 2 hour TTL
        get_signed_url("conv_def456", 86400)  # 24 hour TTL
    
    Use Cases:
        - Share conversation playback securely
        - Embed in web applications
        - Generate temporary access links
        - Control access duration precisely
    """
    return await get_signed_url(client, conversation_id, ttl)


@mcp.tool()
async def get_conversation_token_tool(
    conversation_id: str
) -> Dict[str, Any]:
    """
    Get access token for real-time conversation websocket connection.
    
    Args:
        conversation_id: Conversation ID (format: conv_XXXX)
    
    Returns:
        Access token and websocket URL for real-time communication
    
    Examples:
        get_conversation_token("conv_abc123")
    
    Use Cases:
        - Establish websocket connection for real-time conversation
        - Enable bidirectional audio streaming
        - Implement custom conversation clients
        - Build interactive voice applications
    
    Note: Tokens are short-lived for security. Request new token when expired.
    """
    return await get_conversation_token(client, conversation_id)


# Analytics Tools

@mcp.tool()
async def analyze_conversation_tool(
    conversation_id: str
) -> Dict[str, Any]:
    """
    Analyze a conversation for detailed insights and metrics.
    
    Args:
        conversation_id: Conversation to analyze (format: conv_XXXX)
    
    Returns:
        Comprehensive analysis with metrics and insights
    
    Examples:
        analyze_conversation("conv_abc123")
    
    Metrics Included:
        - Duration and timing
        - Turn count and average length
        - Conversation flow patterns
        - Status and completion rate
        - Transcript statistics
    
    Note: This performs client-side analysis. For AI-powered insights, 
          use specialized analytics endpoints if available.
    """
    return await analyze_conversation(client, conversation_id)


@mcp.tool()
async def performance_report_tool(
    agent_id: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Generate comprehensive performance report for an agent.
    
    Args:
        agent_id: Agent to analyze (format: agent_XXXX)
        days: Number of days to include (1-30, default: 7)
            - 1: Daily report
            - 7: Weekly report (default)
            - 30: Monthly report
    
    Returns:
        Detailed performance metrics and insights
    
    Examples:
        performance_report("agent_abc123")  # Last 7 days
        performance_report("agent_xyz789", 30)  # Last month
        performance_report("agent_def456", 1)  # Today only
    
    Metrics Included:
        - Total conversations and duration
        - Average conversation metrics
        - Success/failure rates
        - Daily conversation patterns
        - Status breakdowns
        - Performance trends
    
    Note: Limited to last 100 conversations. For full analytics, 
          use dedicated reporting endpoints if available.
    """
    return await performance_report(client, agent_id, days)


@mcp.tool()
async def export_conversations_tool(
    agent_id: Optional[str] = None,
    format: str = "json",
    limit: int = 100
) -> Dict[str, Any]:
    """
    Export conversation data for analysis or backup.
    
    Args:
        agent_id: Filter by specific agent (optional)
        format: Export format - "json" (default) or "csv"
            - json: Full structured data with nested fields
            - csv: Flattened tabular format for spreadsheets
        limit: Maximum conversations to export (1-1000, default: 100)
    
    Returns:
        Exported conversation data in requested format
    
    Examples:
        export_conversations()  # All agents, JSON, 100 conversations
        export_conversations("agent_abc123", "csv", 500)  # Specific agent CSV
        export_conversations(format="json", limit=1000)  # Max export
    
    Use Cases:
        - Backup conversation history
        - Import to analytics tools
        - Compliance and auditing
        - Training data extraction
        - Performance analysis in spreadsheets
    
    Note: Large exports may take time. CSV format flattens nested data.
    """
    return await export_conversations(client, agent_id, format, limit)


# Resources

@mcp.resource(
    "resource://conversation-templates",
    name="ElevenLabs Conversation Analysis Templates",
    description="Templates for conversation feedback collection, quality analysis, and pattern recognition. Includes structured approaches to gathering user feedback, analyzing conversation flows, and measuring conversation quality across multiple dimensions.",
    mime_type="application/json",
    tags={"templates", "conversations", "feedback", "analysis"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_conversation_templates_resource() -> str:
    """Get conversation templates as a JSON resource."""
    return json.dumps(CONVERSATION_TEMPLATES, indent=2)

@mcp.resource(
    "resource://export-templates", 
    name="ElevenLabs Conversation Export Templates",
    description="Export format templates for conversation data including CSV structures, JSON schemas, filtered exports, and batch processing configurations. Includes compliance-ready export formats for audit trails and regulatory requirements.",
    mime_type="application/json",
    tags={"templates", "export", "data", "compliance"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_export_templates_resource() -> str:
    """Get export templates as a JSON resource."""
    return json.dumps(EXPORT_TEMPLATES, indent=2)

@mcp.resource(
    "resource://feedback-templates",
    name="ElevenLabs Feedback Collection Templates", 
    description="Comprehensive feedback collection and analysis templates including rating systems, feedback categories, collection prompts, and automated processing workflows. Supports various feedback methodologies from simple thumbs up/down to detailed NPS-style surveys.",
    mime_type="application/json",
    tags={"templates", "feedback", "ratings", "surveys"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_feedback_templates_resource() -> str:
    """Get feedback templates as a JSON resource."""
    return json.dumps(FEEDBACK_TEMPLATES, indent=2)

@mcp.resource(
    "resource://documentation",
    name="ElevenLabs Conversations Server Documentation",
    description="Complete documentation for the conversation management server including tool descriptions, usage examples, and API endpoints for conversation history, playback, and analytics.",
    mime_type="text/markdown",
    tags={"documentation", "help", "reference"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_documentation_resource() -> str:
    """Get server documentation."""
    return """
# ElevenLabs Conversations MCP Server

Manage conversation history and playback for ElevenLabs agents.

## Features

### Core Conversation Management
- List conversations with filtering
- Get detailed conversation data
- Delete conversations
- Send feedback and ratings

### Playback Features
- Get conversation audio downloads
- Generate signed playback URLs
- Multiple audio formats (MP3, WAV)

### Analytics
- Analyze individual conversations
- Generate agent performance reports
- Export conversation data (JSON/CSV)

## Tool Categories

### Core Tools
- list_conversations: Browse conversation history
- get_conversation: Get full conversation details
- get_transcript: Extract conversation transcript
- delete_conversation: Remove conversation records
- send_feedback: Rate and provide feedback

### Playback Tools
- get_conversation_audio: Download audio files
- get_signed_url: Generate secure playback URLs

### Analytics Tools
- analyze_conversation: Get conversation insights
- performance_report: Agent performance metrics
- export_conversations: Bulk data export

## Usage Examples

### List Recent Conversations
```python
list_conversations(limit=10)
```

### Get Conversation Details
```python
get_conversation("conv_abc123")
```

### Export Agent Conversations
```python
export_conversations(
    agent_id="agent_xyz789",
    format="csv",
    limit=50
)
```

### Generate Performance Report
```python
performance_report(
    agent_id="agent_xyz789",
    days=7
)
```
"""


# Entry point
if __name__ == "__main__":
    import sys
    
    # Check for test mode
    if "--test" in sys.argv:
        print("✓ Server module loaded successfully")
        print(f"✓ Found {len([m for m in dir(mcp) if m.endswith('_tool')])} tools")
        sys.exit(0)
    
    # Run the server
    asyncio.run(mcp.run())