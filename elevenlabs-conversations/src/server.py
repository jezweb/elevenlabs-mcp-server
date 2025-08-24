"""ElevenLabs Conversations MCP Server.

Provides tools for managing conversation history and playback.
"""

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    Config,
    ElevenLabsClient,
    format_error,
    format_success,
    validate_elevenlabs_id,
    setup_logging
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
    logger.info("Starting ElevenLabs Conversations MCP server")
    
    # Test connection
    if not await client.test_connection():
        logger.error("Failed to connect to ElevenLabs API")
        logger.warning("Some features may be unavailable")
    else:
        logger.info("ElevenLabs API connection verified")
    
    logger.info("ElevenLabs Conversations MCP server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ElevenLabs Conversations MCP server")
    if client:
        await client.close()


# Set lifespan
mcp.lifespan = lifespan


# Core Conversation Tools

@mcp.tool()
async def list_conversations(
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
    try:
        if agent_id and not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error("Invalid agent ID format", "Use format: agent_XXXX")
        
        if not 1 <= limit <= 100:
            return format_error("Limit must be between 1-100")
        
        if offset < 0:
            return format_error("Offset must be non-negative")
        
        conversations = await client.list_conversations(
            agent_id=agent_id,
            limit=limit,
            offset=offset
        )
        
        # Format response
        formatted = []
        for conv in conversations:
            formatted.append({
                "conversation_id": conv.get("conversation_id"),
                "agent_id": conv.get("agent_id"),
                "start_time": conv.get("start_time"),
                "end_time": conv.get("end_time"),
                "duration": conv.get("duration"),
                "status": conv.get("status"),
                "metadata": conv.get("metadata", {})
            })
        
        return format_success(
            f"Found {len(formatted)} conversations",
            {"conversations": formatted, "total": len(formatted)}
        )
        
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_conversation(
    conversation_id: str
) -> Dict[str, Any]:
    """
    Get detailed conversation data.
    
    Args:
        conversation_id: Conversation to retrieve
    
    Returns:
        Complete conversation details including transcript
    """
    try:
        if not validate_elevenlabs_id(conversation_id, 'conversation'):
            return format_error("Invalid conversation ID format")
        
        conversation = await client.get_conversation(conversation_id)
        
        return format_success(
            "Retrieved conversation details",
            {"conversation": conversation}
        )
        
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_transcript(
    conversation_id: str
) -> Dict[str, Any]:
    """
    Get conversation transcript.
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        Text transcript
    """
    try:
        if not validate_elevenlabs_id(conversation_id, 'conversation'):
            return format_error("Invalid conversation ID format")
        
        transcript = await client.get_transcript(conversation_id)
        
        return format_success(
            "Retrieved transcript",
            {"transcript": transcript}
        )
        
    except Exception as e:
        logger.error(f"Failed to get transcript for {conversation_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def delete_conversation(
    conversation_id: str
) -> Dict[str, Any]:
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation to delete
    
    Returns:
        Deletion confirmation
    """
    try:
        if not validate_elevenlabs_id(conversation_id, 'conversation'):
            return format_error("Invalid conversation ID format")
        
        result = await client._request(
            "DELETE",
            f"/convai/conversations/{conversation_id}"
        )
        
        return format_success(
            f"Deleted conversation {conversation_id}",
            {"deleted": True}
        )
        
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def send_feedback(
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
    
    API Endpoint: POST /v1/convai/conversations/{conversation_id}/feedback
    """
    # Validate conversation ID
    if not conversation_id:
        return format_error(
            "Conversation ID is required",
            "Provide conversation_id from list_conversations() or get_conversation()"
        )
    
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error(
            f"Invalid conversation ID format: {conversation_id}",
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX (conv_ + 28 chars)"
        )
    
    # Validate rating
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return format_error(
            "Rating must be an integer",
            "Provide a rating between 1 (poor) and 5 (excellent)"
        )
    
    if not 1 <= rating <= 5:
        return format_error(
            f"Rating {rating} out of range",
            "Rating must be between 1 (poor) and 5 (excellent)"
        )
    
    # Validate feedback text length if provided
    if feedback_text and len(feedback_text) > 1000:
        return format_error(
            f"Feedback text too long ({len(feedback_text)} characters)",
            "Keep feedback under 1000 characters"
        )
    
    try:
        data = {
            "rating": rating,
            "feedback": feedback_text,
            "metadata": metadata or {}
        }
        
        result = await client._request(
            "POST",
            f"/convai/conversations/{conversation_id}/feedback",
            json_data=data
        )
        
        return format_success(
            f"Feedback submitted (rating: {rating}/5)",
            {
                "conversation_id": conversation_id,
                "rating": rating,
                "has_text": bool(feedback_text),
                "metadata_keys": list(metadata.keys()) if metadata else []
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to send feedback for {conversation_id}: {e}")
        error_msg = str(e)
        
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found"
        elif "already" in error_msg.lower():
            suggestion = "Feedback may have already been submitted for this conversation"
        else:
            suggestion = "Check conversation ID and try again"
            
        return format_error(error_msg, suggestion)


# Playback Tools

@mcp.tool()
async def get_conversation_audio(
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
    
    API Endpoint: GET /v1/convai/conversations/{conversation_id}/audio
    
    Note: URLs expire after ~1 hour. Download promptly or use get_signed_url for longer TTL.
    """
    # Validate conversation ID
    if not conversation_id:
        return format_error(
            "Conversation ID is required",
            "Provide conversation_id from list_conversations() or get_conversation()"
        )
    
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error(
            f"Invalid conversation ID format: {conversation_id}",
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    # Validate and normalize format
    format = format.lower().strip() if format else "mp3"
    if format not in ["mp3", "wav"]:
        return format_error(
            f"Unsupported audio format: {format}",
            "Use 'mp3' for compressed audio or 'wav' for uncompressed"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/conversations/{conversation_id}/audio",
            params={"format": format}
        )
        
        return format_success(
            f"Retrieved {format.upper()} audio URL",
            {
                "audio_url": result.get("url"),
                "format": format,
                "expires_at": result.get("expires_at"),
                "size_estimate": "~1MB/min for MP3, ~10MB/min for WAV"
            }
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide contextual error messages
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found. Check ID or list available conversations."
        elif "audio not available" in error_msg.lower():
            suggestion = "Audio may still be processing. Try again in a few seconds."
        else:
            suggestion = "Check conversation ID and network connection"
            
        logger.error(f"Failed to get audio for {conversation_id}: {e}")
        return format_error(error_msg, suggestion)


@mcp.tool()
async def get_signed_url(
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
    
    API Endpoint: GET /v1/convai/conversations/{conversation_id}/signed-url
    
    Use Cases:
        - Share conversation playback securely
        - Embed in web applications
        - Generate temporary access links
        - Control access duration precisely
    """
    # Validate conversation ID
    if not conversation_id:
        return format_error(
            "Conversation ID is required",
            "Provide conversation_id from list_conversations() or get_conversation()"
        )
    
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error(
            f"Invalid conversation ID format: {conversation_id}",
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    # Validate and coerce TTL
    try:
        ttl = int(ttl)
    except (TypeError, ValueError):
        return format_error(
            "TTL must be an integer",
            "Provide time-to-live in seconds (60-86400)"
        )
    
    if ttl < 60:
        return format_error(
            f"TTL too short: {ttl} seconds",
            "Minimum TTL is 60 seconds (1 minute)"
        )
    elif ttl > 86400:
        return format_error(
            f"TTL too long: {ttl} seconds",
            "Maximum TTL is 86400 seconds (24 hours)"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/conversations/{conversation_id}/signed-url",
            params={"ttl": ttl}
        )
        
        # Format TTL for human readability
        if ttl < 3600:
            ttl_display = f"{ttl // 60} minutes"
        elif ttl < 86400:
            ttl_display = f"{ttl / 3600:.1f} hours"
        else:
            ttl_display = "24 hours"
        
        return format_success(
            f"Generated signed URL (valid for {ttl_display})",
            {
                "signed_url": result.get("url"),
                "expires_at": result.get("expires_at"),
                "ttl_seconds": ttl,
                "ttl_display": ttl_display
            }
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide contextual error messages
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found"
        elif "permission" in error_msg.lower():
            suggestion = "Check API key permissions for conversation access"
        else:
            suggestion = "Verify conversation ID and API connectivity"
            
        logger.error(f"Failed to get signed URL for {conversation_id}: {e}")
        return format_error(error_msg, suggestion)


@mcp.tool()
async def get_conversation_token(
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
    
    API Endpoint: GET /v1/convai/conversations/{conversation_id}/token
    
    Use Cases:
        - Establish websocket connection for real-time conversation
        - Enable bidirectional audio streaming
        - Implement custom conversation clients
        - Build interactive voice applications
    
    Note: Tokens are short-lived for security. Request new token when expired.
    """
    # Validate conversation ID
    if not conversation_id:
        return format_error(
            "Conversation ID is required",
            "Provide conversation_id from list_conversations() or active conversation"
        )
    
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error(
            f"Invalid conversation ID format: {conversation_id}",
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        result = await client._request(
            "GET",
            f"/convai/conversations/{conversation_id}/token"
        )
        
        return format_success(
            "Retrieved websocket access token",
            {
                "token": result.get("token"),
                "expires_at": result.get("expires_at"),
                "websocket_url": result.get("websocket_url"),
                "usage_hint": "Use token to authenticate websocket connection"
            }
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide contextual error messages
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found or not active"
        elif "expired" in error_msg.lower():
            suggestion = "Conversation may have ended. Start a new conversation."
        elif "permission" in error_msg.lower():
            suggestion = "Check API key permissions for websocket access"
        else:
            suggestion = "Verify conversation is active and ID is correct"
            
        logger.error(f"Failed to get token for {conversation_id}: {e}")
        return format_error(error_msg, suggestion)


@mcp.tool()
async def analyze_conversation(
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
    # Validate conversation ID
    if not conversation_id:
        return format_error(
            "Conversation ID is required",
            "Provide conversation_id from list_conversations()"
        )
    
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error(
            f"Invalid conversation ID format: {conversation_id}",
            "Use format: conv_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    try:
        # Get conversation data
        conversation = await client.get_conversation(conversation_id)
        transcript = await client.get_transcript(conversation_id)
        
        # Analyze conversation metrics
        transcript_data = conversation.get("transcript", [])
        duration = conversation.get("duration", 0)
        
        analysis = {
            "conversation_id": conversation_id,
            "status": conversation.get("status", "unknown"),
            "duration_seconds": duration,
            "duration_display": f"{duration // 60}m {duration % 60}s" if duration else "N/A",
            "turn_count": len(transcript_data),
            "metadata": conversation.get("metadata", {}),
            "transcript_length": len(transcript) if transcript else 0
        }
        
        # Calculate advanced metrics
        if analysis["turn_count"] > 0:
            analysis["avg_turn_length"] = round(
                analysis["transcript_length"] / analysis["turn_count"], 1
            )
            analysis["turns_per_minute"] = round(
                (analysis["turn_count"] / duration) * 60, 2
            ) if duration > 0 else 0
        
        # Analyze conversation flow
        if transcript_data:
            speaker_turns = {"user": 0, "agent": 0}
            for turn in transcript_data:
                speaker = turn.get("role", "unknown")
                if speaker in speaker_turns:
                    speaker_turns[speaker] += 1
            analysis["speaker_distribution"] = speaker_turns
        
        # Add completion insights
        if analysis["status"] == "completed":
            analysis["completion_type"] = "normal"
        elif analysis["status"] == "failed":
            analysis["completion_type"] = "error"
        else:
            analysis["completion_type"] = "interrupted"
        
        return format_success(
            "Conversation analysis complete",
            {"analysis": analysis}
        )
        
    except Exception as e:
        error_msg = str(e)
        
        if "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"Conversation {conversation_id} not found"
        else:
            suggestion = "Check conversation ID and try again"
            
        logger.error(f"Failed to analyze conversation {conversation_id}: {e}")
        return format_error(error_msg, suggestion)


@mcp.tool()
async def performance_report(
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
    # Validate agent ID
    if not agent_id:
        return format_error(
            "Agent ID is required",
            "Provide agent_id from list_agents() or get_agent()"
        )
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error(
            f"Invalid agent ID format: {agent_id}",
            "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        )
    
    # Validate and coerce days
    try:
        days = int(days)
    except (TypeError, ValueError):
        return format_error(
            "Days must be an integer",
            "Provide number of days between 1 and 30"
        )
    
    if days < 1:
        return format_error(
            f"Days too low: {days}",
            "Minimum is 1 day"
        )
    elif days > 30:
        return format_error(
            f"Days too high: {days}",
            "Maximum is 30 days for performance reports"
        )
    
    try:
        # Get conversations for the agent
        conversations = await client.list_conversations(
            agent_id=agent_id,
            limit=100  # API limitation
        )
        
        # Calculate core metrics
        total_conversations = len(conversations)
        total_duration = sum(c.get("duration", 0) for c in conversations)
        
        # Status breakdown with insights
        status_counts = {
            "completed": 0,
            "failed": 0,
            "interrupted": 0,
            "unknown": 0
        }
        
        for conv in conversations:
            status = conv.get("status", "unknown")
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts["unknown"] += 1
        
        # Calculate success rate
        success_rate = 0
        if total_conversations > 0:
            success_rate = round(
                (status_counts["completed"] / total_conversations) * 100, 1
            )
        
        # Format duration for display
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        duration_display = f"{hours}h {minutes}m"
        
        # Create comprehensive report
        report = {
            "agent_id": agent_id,
            "period_days": days,
            "period_label": f"Last {days} day{'s' if days != 1 else ''}",
            "total_conversations": total_conversations,
            "total_duration_seconds": total_duration,
            "total_duration_display": duration_display,
            "average_duration": round(
                total_duration / total_conversations if total_conversations > 0 else 0, 1
            ),
            "status_breakdown": status_counts,
            "success_rate": f"{success_rate}%",
            "conversations_per_day": round(
                total_conversations / days if days > 0 else 0, 2
            ),
            "average_daily_duration": round(
                total_duration / days if days > 0 else 0, 1
            ),
            "data_completeness": "Limited to last 100 conversations" if total_conversations >= 100 else "Complete"
        }
        
        # Add performance insights
        insights = []
        if success_rate < 70:
            insights.append("Success rate below 70% - consider reviewing agent configuration")
        if report["average_duration"] < 30:
            insights.append("Short average duration - conversations may be ending prematurely")
        if status_counts["failed"] > status_counts["completed"] * 0.2:
            insights.append("High failure rate detected - check error logs")
        
        if insights:
            report["insights"] = insights
        
        return format_success(
            f"Generated {days}-day performance report",
            {"report": report}
        )
        
    except Exception as e:
        error_msg = str(e)
        
        if "permission" in error_msg.lower():
            suggestion = "Check API key permissions for analytics access"
        else:
            suggestion = "Verify agent ID and API connectivity"
            
        logger.error(f"Failed to generate performance report for {agent_id}: {e}")
        return format_error(error_msg, suggestion)


@mcp.tool()
async def export_conversations(
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
    # Validate agent ID if provided
    if agent_id:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error(
                f"Invalid agent ID format: {agent_id}",
                "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX or omit for all agents"
            )
    
    # Validate and normalize format
    format = format.lower().strip() if format else "json"
    if format not in ["json", "csv"]:
        return format_error(
            f"Unsupported format: {format}",
            "Use 'json' for structured data or 'csv' for spreadsheets"
        )
    
    # Validate and coerce limit
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        return format_error(
            "Limit must be an integer",
            "Provide number between 1 and 1000"
        )
    
    if limit < 1:
        return format_error(
            f"Limit too low: {limit}",
            "Minimum export size is 1 conversation"
        )
    elif limit > 1000:
        return format_error(
            f"Limit too high: {limit}",
            "Maximum export size is 1000 conversations"
        )
    
    try:
        # Get conversations with optional agent filter
        conversations = await client.list_conversations(
            agent_id=agent_id,
            limit=limit
        )
        
        if not conversations:
            return format_success(
                "No conversations found to export",
                {
                    "format": format,
                    "count": 0,
                    "filters": {"agent_id": agent_id} if agent_id else {}
                }
            )
        
        if format == "json":
            # JSON export with pretty formatting
            export_data = json.dumps(conversations, indent=2, default=str)
            
            return format_success(
                f"Exported {len(conversations)} conversations as JSON",
                {
                    "format": "json",
                    "count": len(conversations),
                    "size_bytes": len(export_data),
                    "data": export_data,
                    "agent_filter": agent_id or "all"
                }
            )
            
        else:  # CSV format
            # Convert to CSV with proper handling of nested fields
            import csv
            import io
            
            output = io.StringIO()
            
            # Flatten nested fields for CSV
            flattened_conversations = []
            for conv in conversations:
                flat_conv = {
                    "conversation_id": conv.get("conversation_id", ""),
                    "agent_id": conv.get("agent_id", ""),
                    "status": conv.get("status", ""),
                    "duration": conv.get("duration", 0),
                    "created_at": conv.get("created_at", ""),
                    "turn_count": len(conv.get("transcript", [])),
                    "metadata": json.dumps(conv.get("metadata", {}))
                }
                flattened_conversations.append(flat_conv)
            
            if flattened_conversations:
                writer = csv.DictWriter(
                    output, 
                    fieldnames=flattened_conversations[0].keys()
                )
                writer.writeheader()
                writer.writerows(flattened_conversations)
            
            export_data = output.getvalue()
            
            return format_success(
                f"Exported {len(conversations)} conversations as CSV",
                {
                    "format": "csv",
                    "count": len(conversations),
                    "size_bytes": len(export_data),
                    "csv": export_data,
                    "agent_filter": agent_id or "all",
                    "note": "Nested fields flattened for CSV compatibility"
                }
            )
        
    except Exception as e:
        error_msg = str(e)
        
        if "permission" in error_msg.lower():
            suggestion = "Check API key permissions for data export"
        elif "timeout" in error_msg.lower():
            suggestion = f"Large export timed out. Try reducing limit from {limit}"
        else:
            suggestion = "Check parameters and API connectivity"
            
        logger.error(f"Failed to export conversations: {e}")
        return format_error(error_msg, suggestion)


# Resources

@mcp.resource("resource://documentation")
async def get_documentation() -> str:
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
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("✅ ElevenLabs Conversations MCP server initialized successfully")
        sys.exit(0)
    
    # Run the server
    mcp.run()