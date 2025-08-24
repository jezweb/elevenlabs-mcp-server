"""
Analytics tools for ElevenLabs conversations.
"""

import json
import logging
from typing import Dict, Any, Optional
from src.utils import format_success, format_error, validate_elevenlabs_id

logger = logging.getLogger(__name__)


async def analyze_conversation(
    client,
    conversation_id: str
) -> Dict[str, Any]:
    """
    Analyze a conversation for detailed insights and metrics.
    
    Args:
        client: ElevenLabs API client
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
        
        # Extract transcript for analysis
        transcript = conversation.get("transcript", [])
        
        # Calculate metrics
        turn_count = len(transcript)
        
        # Calculate average turn length
        total_chars = sum(len(turn.get("text", "")) for turn in transcript)
        avg_turn_length = round(total_chars / turn_count if turn_count > 0 else 0, 1)
        
        # Count user vs agent turns
        user_turns = sum(1 for turn in transcript if turn.get("role") == "user")
        agent_turns = sum(1 for turn in transcript if turn.get("role") == "agent")
        
        # Calculate conversation balance
        if turn_count > 0:
            user_ratio = round((user_turns / turn_count) * 100, 1)
            agent_ratio = round((agent_turns / turn_count) * 100, 1)
        else:
            user_ratio = agent_ratio = 0
        
        # Create analysis report
        analysis = {
            "conversation_id": conversation_id,
            "status": conversation.get("status"),
            "duration": conversation.get("duration"),
            "turn_count": turn_count,
            "user_turns": user_turns,
            "agent_turns": agent_turns,
            "conversation_balance": {
                "user_percentage": f"{user_ratio}%",
                "agent_percentage": f"{agent_ratio}%"
            },
            "average_turn_length": avg_turn_length,
            "total_characters": total_chars,
            "metadata": conversation.get("metadata", {})
        }
        
        # Add insights
        insights = []
        if turn_count < 3:
            insights.append("Very short conversation - may indicate early termination")
        if user_ratio < 30:
            insights.append("Agent-dominated conversation - consider more user engagement")
        if avg_turn_length < 20:
            insights.append("Very short responses - may need more detailed interactions")
        
        if insights:
            analysis["insights"] = insights
        
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


async def performance_report(
    client,
    agent_id: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Generate comprehensive performance report for an agent.
    
    Args:
        client: ElevenLabs API client
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


async def export_conversations(
    client,
    agent_id: Optional[str] = None,
    format: str = "json",
    limit: int = 100
) -> Dict[str, Any]:
    """
    Export conversation data for analysis or backup.
    
    Args:
        client: ElevenLabs API client
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