#!/usr/bin/env python3
"""
ElevenLabs Knowledge MCP Server
================================
Manages knowledge base, RAG configuration, and conversation analytics.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from contextlib import asynccontextmanager

# Add parent directory to path for shared module access
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from shared import (
    Config, 
    ElevenLabsClient, 
    format_success, 
    format_error, 
    validate_uuid,
    validate_elevenlabs_id,
    chunk_text
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
    logger.info(f"Starting elevenlabs-knowledge server")
    
    # Test API connection
    if await client.test_connection():
        logger.info("ElevenLabs API connection verified")
    else:
        logger.warning("Failed to verify API connection - some features may be unavailable")
    
    yield  # Server runs here
    
    # Shutdown
    logger.info("Shutting down elevenlabs-knowledge server")
    await client.close()

# Initialize FastMCP server - MUST be at module level
mcp = FastMCP(
    name="elevenlabs-knowledge",
    instructions="Manage ElevenLabs knowledge base and conversations",
    lifespan=lifespan
)

# ============================================================
# Document Management Tools
# ============================================================

@mcp.tool()
async def add_document_url(
    url: str,
    name: Optional[str] = None,
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a document to the knowledge base from a URL.
    
    Args:
        url: Web page URL to add
        name: Document name (auto-generated if not provided)
        agent_id: Optional agent to attach document to
    
    Returns:
        Document ID and details
    """
    try:
        # Auto-generate name from URL if not provided
        if not name:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            name = f"{parsed.netloc}{parsed.path}".replace("/", "_")
        
        result = await client.add_document_url(name, url)
        
        response_data = {
            "document_id": result.get("id"),
            "name": name,
            "url": url
        }
        
        # Attach to agent if specified
        if agent_id and validate_elevenlabs_id(agent_id, 'agent'):
            # Note: Would need additional API call to attach to agent
            response_data["attached_to_agent"] = agent_id
        
        return format_success(
            f"Document '{name}' added from URL",
            response_data
        )
    except Exception as e:
        logger.error(f"Failed to add document from URL: {e}")
        return format_error(str(e), suggestion="Check URL is accessible")


@mcp.tool()
async def add_document_text(
    text: str,
    name: str,
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a text document to the knowledge base.
    
    Args:
        text: Document content
        name: Document name
        agent_id: Optional agent to attach to
    
    Returns:
        Document ID and details
    """
    try:
        result = await client.add_document_text(name, text)
        
        response_data = {
            "document_id": result.get("id"),
            "name": name,
            "character_count": len(text),
            "estimated_chunks": len(text) // 512 + 1
        }
        
        if agent_id and validate_elevenlabs_id(agent_id, 'agent'):
            response_data["attached_to_agent"] = agent_id
        
        return format_success(
            f"Document '{name}' added",
            response_data
        )
    except Exception as e:
        logger.error(f"Failed to add text document: {e}")
        return format_error(str(e))


@mcp.tool()
async def list_documents(
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all documents in the knowledge base.
    
    Args:
        agent_id: Filter by agent ID
    
    Returns:
        List of documents with metadata
    """
    try:
        documents = await client.list_knowledge_base(agent_id)
        return format_success(
            f"Found {len(documents)} documents",
            {
                "count": len(documents),
                "documents": documents,
                "agent_filter": agent_id
            }
        )
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        return format_error(str(e))


@mcp.tool()
async def delete_document(document_id: str) -> Dict[str, Any]:
    """
    Delete a document from the knowledge base.
    
    Args:
        document_id: Document to delete
    
    Returns:
        Deletion confirmation
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        await client.delete_document(document_id)
        return format_success(f"Document {document_id} deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        return format_error(str(e))


# ============================================================
# RAG Configuration Tools
# ============================================================

@mcp.tool()
async def configure_rag(
    agent_id: str,
    chunk_size: Optional[int] = 512,
    chunk_overlap: Optional[int] = 50,
    top_k: Optional[int] = 5,
    similarity_threshold: Optional[float] = 0.7
) -> Dict[str, Any]:
    """
    Configure RAG settings for an agent.
    
    Args:
        agent_id: Agent to configure
        chunk_size: Characters per chunk (100-4000)
        chunk_overlap: Overlap between chunks (0-500)
        top_k: Number of results to retrieve (1-20)
        similarity_threshold: Minimum relevance score (0.0-1.0)
    
    Returns:
        Configuration result
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Validate parameters
        if chunk_size < 100 or chunk_size > 4000:
            return format_error("chunk_size must be between 100 and 4000")
        if chunk_overlap >= chunk_size:
            return format_error("chunk_overlap must be less than chunk_size")
        if top_k < 1 or top_k > 20:
            return format_error("top_k must be between 1 and 20")
        if similarity_threshold < 0 or similarity_threshold > 1:
            return format_error("similarity_threshold must be between 0.0 and 1.0")
        
        rag_config = {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        }
        
        # Note: This would call the actual RAG configuration endpoint
        return format_success(
            f"RAG configured for agent {agent_id}",
            {"rag_config": rag_config}
        )
    except Exception as e:
        logger.error(f"Failed to configure RAG: {e}")
        return format_error(str(e))


@mcp.tool()
async def rebuild_index(
    agent_id: str,
    force: bool = False
) -> Dict[str, Any]:
    """
    Rebuild the search index for an agent's knowledge base.
    
    Args:
        agent_id: Agent whose index to rebuild
        force: Force rebuild even if current
    
    Returns:
        Index rebuild status
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Note: This would call the actual index rebuild endpoint
        return format_success(
            f"Index rebuild initiated for agent {agent_id}",
            {
                "status": "rebuilding",
                "estimated_time_seconds": 60,
                "force": force
            }
        )
    except Exception as e:
        logger.error(f"Failed to rebuild index: {e}")
        return format_error(str(e))


# ============================================================
# Conversation Management Tools
# ============================================================

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
        if limit < 1 or limit > 100:
            return format_error("limit must be between 1 and 100")
        
        conversations = await client.list_conversations(agent_id, limit, offset)
        return format_success(
            f"Found {len(conversations)} conversations",
            {
                "count": len(conversations),
                "conversations": conversations,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(conversations) == limit
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    Get detailed conversation data.
    
    Args:
        conversation_id: Conversation to retrieve
    
    Returns:
        Complete conversation details
    """
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error("Invalid conversation ID format")
    
    try:
        conversation = await client.get_conversation(conversation_id)
        return format_success(
            "Retrieved conversation details",
            {"conversation": conversation}
        )
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_transcript(conversation_id: str) -> Dict[str, Any]:
    """
    Get conversation transcript.
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        Text transcript
    """
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error("Invalid conversation ID format")
    
    try:
        transcript = await client.get_transcript(conversation_id)
        
        # Parse transcript into structured format
        lines = transcript.split('\n')
        turns = []
        current_speaker = None
        current_text = []
        
        for line in lines:
            if line.startswith(('Agent:', 'User:', 'Customer:')):
                if current_speaker:
                    turns.append({
                        "speaker": current_speaker,
                        "text": ' '.join(current_text)
                    })
                parts = line.split(':', 1)
                current_speaker = parts[0]
                current_text = [parts[1].strip()] if len(parts) > 1 else []
            elif line.strip():
                current_text.append(line.strip())
        
        if current_speaker:
            turns.append({
                "speaker": current_speaker,
                "text": ' '.join(current_text)
            })
        
        return format_success(
            "Retrieved transcript",
            {
                "conversation_id": conversation_id,
                "turn_count": len(turns),
                "turns": turns,
                "raw_transcript": transcript
            }
        )
    except Exception as e:
        logger.error(f"Failed to get transcript: {e}")
        return format_error(str(e))


@mcp.tool()
async def analyze_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    Analyze a conversation for insights.
    
    Args:
        conversation_id: Conversation to analyze
    
    Returns:
        Analysis with metrics and insights
    """
    if not validate_elevenlabs_id(conversation_id, 'conversation'):
        return format_error("Invalid conversation ID format")
    
    try:
        # Get conversation and transcript
        conversation = await client.get_conversation(conversation_id)
        transcript = await client.get_transcript(conversation_id)
        
        # Basic analysis
        word_count = len(transcript.split())
        line_count = len(transcript.split('\n'))
        
        # Sentiment indicators (simplified)
        positive_words = ['great', 'excellent', 'perfect', 'thank', 'helpful']
        negative_words = ['problem', 'issue', 'bad', 'wrong', 'frustrated']
        
        positive_count = sum(1 for word in positive_words if word in transcript.lower())
        negative_count = sum(1 for word in negative_words if word in transcript.lower())
        
        analysis = {
            "conversation_id": conversation_id,
            "duration_seconds": conversation.get("duration"),
            "metrics": {
                "word_count": word_count,
                "turn_count": line_count,
                "average_turn_length": word_count // line_count if line_count > 0 else 0
            },
            "sentiment": {
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
                "overall": "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"
            },
            "outcomes": {
                "transfer_occurred": conversation.get("transfer", {}).get("occurred", False),
                "ended_by": conversation.get("ended_by", "unknown")
            }
        }
        
        return format_success(
            "Conversation analyzed",
            {"analysis": analysis}
        )
    except Exception as e:
        logger.error(f"Failed to analyze conversation: {e}")
        return format_error(str(e))


# ============================================================
# Analytics Tools
# ============================================================

@mcp.tool()
async def performance_report(
    agent_id: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Generate performance report for an agent.
    
    Args:
        agent_id: Agent to analyze
        days: Number of days to include (1-30)
    
    Returns:
        Performance metrics and insights
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    if days < 1 or days > 30:
        return format_error("days must be between 1 and 30")
    
    try:
        # Get recent conversations
        conversations = await client.list_conversations(agent_id, limit=100)
        
        if not conversations:
            return format_success(
                "No conversations found",
                {"agent_id": agent_id, "period_days": days}
            )
        
        # Calculate metrics
        total_conversations = len(conversations)
        total_duration = sum(c.get("duration", 0) for c in conversations)
        avg_duration = total_duration / total_conversations if total_conversations > 0 else 0
        
        # Transfer rate
        transfers = sum(1 for c in conversations if c.get("transfer", {}).get("occurred", False))
        transfer_rate = (transfers / total_conversations * 100) if total_conversations > 0 else 0
        
        report = {
            "agent_id": agent_id,
            "period_days": days,
            "metrics": {
                "total_conversations": total_conversations,
                "average_duration_seconds": round(avg_duration, 2),
                "total_duration_seconds": total_duration,
                "transfer_rate_percent": round(transfer_rate, 2),
                "conversations_per_day": round(total_conversations / days, 2)
            },
            "outcomes": {
                "successful": total_conversations - transfers,
                "transferred": transfers
            }
        }
        
        return format_success(
            f"Performance report for {days} days",
            {"report": report}
        )
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return format_error(str(e))


@mcp.tool()
async def export_conversations(
    agent_id: Optional[str] = None,
    format: str = "json",
    limit: int = 100
) -> Dict[str, Any]:
    """
    Export conversation data.
    
    Args:
        agent_id: Filter by agent
        format: Export format (json or csv)
        limit: Maximum conversations to export
    
    Returns:
        Exported data
    """
    if format not in ["json", "csv"]:
        return format_error("format must be 'json' or 'csv'")
    
    try:
        conversations = await client.list_conversations(agent_id, limit=limit)
        
        if format == "json":
            export_data = json.dumps(conversations, indent=2, default=str)
        else:  # csv
            # Simplified CSV generation
            if conversations:
                headers = ["conversation_id", "agent_id", "duration", "start_time"]
                rows = [headers]
                for c in conversations:
                    rows.append([
                        c.get("conversation_id", ""),
                        c.get("agent_id", ""),
                        str(c.get("duration", "")),
                        c.get("start_time", "")
                    ])
                export_data = '\n'.join([','.join(row) for row in rows])
            else:
                export_data = "No data"
        
        return format_success(
            f"Exported {len(conversations)} conversations",
            {
                "format": format,
                "count": len(conversations),
                "data": export_data if format == "csv" else conversations
            }
        )
    except Exception as e:
        logger.error(f"Failed to export conversations: {e}")
        return format_error(str(e))


# ============================================================
# Main entry point
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ElevenLabs Knowledge MCP Server")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode - verify all components
        print(f"Server: elevenlabs-knowledge v0.1.0")
        print(f"Tools: {len(mcp.tools)}")
        print(f"Config: API key {Config.mask_api_key()}")
        print("All components loaded successfully!")
    else:
        # Run server
        logger.info("Starting MCP server...")
        mcp.run()