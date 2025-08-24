"""
Document Management Tools
========================
Tools for managing knowledge base documents.
"""

import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


async def add_document_url(
    client,
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
    
    API Endpoint: POST /convai/knowledge-base
    """
    from shared import format_error, format_success, validate_elevenlabs_id
    
    # Validate URL
    if not url:
        return format_error(
            "URL is required",
            "Provide a valid URL starting with http:// or https://"
        )
    
    # Check URL format
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


async def add_document_text(
    client,
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
    
    API Endpoint: POST /convai/knowledge-base
    """
    from shared import format_error, format_success, validate_elevenlabs_id
    
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
        from shared import format_error
        return format_error(str(e))


async def list_documents(
    client,
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all documents in the knowledge base.
    
    Args:
        agent_id: Filter by agent ID
    
    Returns:
        List of documents with metadata
    """
    from shared import format_success, format_error
    
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


async def delete_document(client, document_id: str) -> Dict[str, Any]:
    """
    Delete a document from the knowledge base.
    
    Args:
        document_id: Document to delete
    
    Returns:
        Deletion confirmation
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        await client.delete_document(document_id)
        return format_success(f"Document {document_id} deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        return format_error(str(e))


async def get_document(client, document_id: str) -> Dict[str, Any]:
    """
    Get document details from knowledge base.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Document metadata and content info
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
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


async def update_document(
    client,
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
    from shared import format_success, format_error, validate_elevenlabs_id
    
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


async def add_document_file(
    client,
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
    from shared import format_success, format_error
    
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


async def get_document_content(client, document_id: str) -> Dict[str, Any]:
    """
    Get full content of a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Document content
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
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


async def get_document_chunk(
    client,
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
    from shared import format_success, format_error, validate_elevenlabs_id
    
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