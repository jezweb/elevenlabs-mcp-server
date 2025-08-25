#!/usr/bin/env python3
"""
ElevenLabs Knowledge MCP Server
================================
Manages knowledge base, RAG configuration, and analytics.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from shared import Config, ElevenLabsClient

# Import all tools
from tools import (
    # Document Management
    add_document_url,
    add_document_text,
    list_documents,
    delete_document,
    get_document,
    update_document,
    add_document_file,
    get_document_content,
    get_document_chunk,
    # RAG Configuration
    configure_rag,
    rebuild_index,
    compute_rag_index,
    get_rag_index,
    get_rag_index_overview,
    delete_rag_index,
    # Analytics
    get_dependent_agents,
    get_knowledge_base_size
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
KNOWLEDGE_TEMPLATES = load_resource("knowledge_templates.json")
RAG_PRESETS = load_resource("rag_presets.json") 
ANALYTICS_TEMPLATES = load_resource("analytics_templates.json")

# ============================================================
# Document Management Tools
# ============================================================

@mcp.tool()
async def add_document_url_tool(
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
    return await add_document_url(client, url, name, agent_id)


@mcp.tool()
async def add_document_text_tool(
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
    return await add_document_text(client, text, name, agent_id)


@mcp.tool()
async def list_documents_tool(
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all documents in the knowledge base.
    
    Args:
        agent_id: Filter by agent ID
    
    Returns:
        List of documents with metadata
    """
    return await list_documents(client, agent_id)


@mcp.tool()
async def delete_document_tool(document_id: str) -> Dict[str, Any]:
    """
    Delete a document from the knowledge base.
    
    Args:
        document_id: Document to delete
    
    Returns:
        Deletion confirmation
    """
    return await delete_document(client, document_id)


@mcp.tool()
async def get_document_tool(document_id: str) -> Dict[str, Any]:
    """
    Get document details from knowledge base.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Document metadata and content info
    """
    return await get_document(client, document_id)


@mcp.tool()
async def update_document_tool(
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
    return await update_document(client, document_id, name, metadata)


@mcp.tool()
async def add_document_file_tool(
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
    return await add_document_file(client, file_path, name, agent_id, metadata)


@mcp.tool()
async def get_document_content_tool(document_id: str) -> Dict[str, Any]:
    """
    Get full content of a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Document content
    """
    return await get_document_content(client, document_id)


@mcp.tool()
async def get_document_chunk_tool(
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
    return await get_document_chunk(client, document_id, chunk_id)


# ============================================================
# RAG Configuration Tools
# ============================================================

@mcp.tool()
async def configure_rag_tool(
    agent_id: str,
    enabled: Optional[bool] = True,
    embedding_model: Optional[str] = "e5_mistral_7b_instruct", 
    max_documents_length: Optional[str] = "10000"
) -> Dict[str, Any]:
    """
    Configure RAG settings for an agent.
    
    Args:
        agent_id: Agent to configure (format: agent_XXXX or UUID)
        enabled: Whether to enable RAG for this agent (default: True)
        embedding_model: Model for vector embeddings (default: "e5_mistral_7b_instruct")
        max_documents_length: Maximum length for documents (default: "10000")
    
    Returns:
        Configuration result with RAG settings applied
    """
    return await configure_rag(client, agent_id, enabled, embedding_model, max_documents_length)


@mcp.tool()
async def rebuild_index_tool(
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
    return await rebuild_index(client, agent_id, force)


@mcp.tool()
async def compute_rag_index_tool(
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
    return await compute_rag_index(client, document_id, embedding_model)


@mcp.tool()
async def get_rag_index_tool(document_id: str) -> Dict[str, Any]:
    """
    Get RAG index details for a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Index configuration and status
    """
    return await get_rag_index(client, document_id)


@mcp.tool()
async def get_rag_index_overview_tool(document_id: str) -> Dict[str, Any]:
    """
    Get RAG index statistics and overview.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Index statistics and metadata
    """
    return await get_rag_index_overview(client, document_id)


@mcp.tool()
async def delete_rag_index_tool(document_id: str) -> Dict[str, Any]:
    """
    Delete RAG index for a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Deletion confirmation
    """
    return await delete_rag_index(client, document_id)


# ============================================================
# Analytics Tools
# ============================================================

@mcp.tool()
async def get_dependent_agents_tool(document_id: str) -> Dict[str, Any]:
    """
    Get agents that depend on this document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        List of dependent agents
    """
    return await get_dependent_agents(client, document_id)


@mcp.tool()
async def get_knowledge_base_size_tool(agent_id: str) -> Dict[str, Any]:
    """
    Get knowledge base size and statistics for a specific agent.
    
    Args:
        agent_id: Agent to get knowledge base size for
    
    Returns:
        Storage metrics and document counts
    """
    return await get_knowledge_base_size(client, agent_id)


# ============================================================
# Resources
# ============================================================

@mcp.resource(
    "resource://knowledge-templates",
    name="ElevenLabs Knowledge Base Templates",
    description="Templates and best practices for document management, content organization, and knowledge base setup. Includes examples for adding documents, organizing content by type, and following content best practices.",
    mime_type="application/json",
    tags={"templates", "documents", "knowledge_base", "content"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_knowledge_templates_resource() -> str:
    """Get knowledge base templates as a JSON resource."""
    return json.dumps(KNOWLEDGE_TEMPLATES, indent=2)

@mcp.resource(
    "resource://rag-presets", 
    name="ElevenLabs RAG Configuration Presets",
    description="Pre-configured RAG settings optimized for different use cases including customer support, technical documentation, quick answers, and detailed research. Each preset includes embedding model and document length configurations.",
    mime_type="application/json",
    tags={"templates", "rag", "configuration", "presets"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_rag_presets_resource() -> str:
    """Get RAG configuration presets as a JSON resource."""
    return json.dumps(RAG_PRESETS, indent=2)

@mcp.resource(
    "resource://analytics-templates",
    name="ElevenLabs Knowledge Analytics Templates", 
    description="Templates for performance metrics, reporting formats, and optimization insights. Includes weekly reports, export formats, agent usage analytics, and knowledge base optimization recommendations.",
    mime_type="application/json",
    tags={"templates", "analytics", "metrics", "reporting"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
async def get_analytics_templates_resource() -> str:
    """Get analytics templates as a JSON resource."""
    return json.dumps(ANALYTICS_TEMPLATES, indent=2)

@mcp.resource(
    "resource://documentation",
    name="ElevenLabs Knowledge Server Documentation",
    description="Complete documentation for the knowledge base management server including tool descriptions, usage examples, and API endpoints.",
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
# ElevenLabs Knowledge MCP Server

Manage knowledge base documents, RAG configuration, and analytics.

## Features

### Document Management
- Add documents from URLs or text
- List, get, update, and delete documents
- Upload files to knowledge base
- Retrieve document content and chunks

### RAG Configuration
- Configure RAG settings for agents
- Rebuild search indexes
- Compute and manage RAG indexes
- Get index statistics and overviews

### Analytics
- Get dependent agents for documents
- View knowledge base statistics

## Tool Categories

### Document Tools (9 tools)
- add_document_url: Add from web URLs
- add_document_text: Add text documents
- list_documents: Browse knowledge base
- delete_document: Remove documents
- get_document: Get document details
- update_document: Update metadata
- add_document_file: Upload files
- get_document_content: Get full content
- get_document_chunk: Get specific chunks

### RAG Tools (6 tools)
- configure_rag: Setup RAG for agents
- rebuild_index: Rebuild search index
- compute_rag_index: Create document index
- get_rag_index: Get index details
- get_rag_index_overview: View statistics
- delete_rag_index: Remove indexes

### Analytics Tools (2 tools)
- get_dependent_agents: Find agent dependencies
- get_knowledge_base_size: View storage metrics

## Usage Examples

### Add Document from URL
```python
add_document_url(
    url="https://docs.example.com/guide",
    name="API Guide",
    agent_id="agent_abc123"
)
```

### Configure RAG
```python
configure_rag(
    agent_id="agent_xyz789",
    enabled=True,
    max_documents_length="15000"
)
```

### Get Knowledge Base Stats
```python
get_knowledge_base_size("agent_abc123")
```
"""


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
        import uvicorn
        uvicorn.run(mcp, host="0.0.0.0", port=8000)