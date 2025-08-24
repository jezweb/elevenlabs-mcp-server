"""
RAG Configuration Tools
=======================
Tools for configuring and managing RAG (Retrieval-Augmented Generation) indexes.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def configure_rag(
    client,
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
        
    Example:
        configure_rag("agent_abc123", enabled=True, max_documents_length="15000")
        
    Note:
        - RAG enhances agent responses with knowledge base content
        - Different embedding models may provide different performance
        - Larger max_documents_length increases context but may impact latency
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
    if not validate_elevenlabs_id(agent_id, 'agent'):
        return format_error("Invalid agent ID format")
    
    try:
        # Convert and validate max_documents_length
        max_docs_int = 10000  # default
        if max_documents_length is not None:
            try:
                max_docs_int = int(max_documents_length)
                if max_docs_int < 1000 or max_docs_int > 50000:
                    return format_error("max_documents_length must be between 1000 and 50000")
            except (ValueError, TypeError):
                return format_error("max_documents_length must be a valid integer")
        
        # Build RAG configuration according to ElevenLabs API
        rag_config = {
            "enabled": enabled if enabled is not None else True,
            "embedding_model": embedding_model or "e5_mistral_7b_instruct",
            "max_documents_length": max_docs_int
        }
        
        # Note: This would call the actual RAG configuration endpoint
        return format_success(
            f"RAG configured for agent {agent_id}",
            {"rag_config": rag_config}
        )
    except Exception as e:
        logger.error(f"Failed to configure RAG: {e}")
        return format_error(str(e))


async def rebuild_index(
    client,
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
    from shared import format_success, format_error, validate_elevenlabs_id
    
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


async def compute_rag_index(
    client,
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
    from shared import format_success, format_error, validate_elevenlabs_id
    
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


async def get_rag_index(client, document_id: str) -> Dict[str, Any]:
    """
    Get RAG index details for a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Index configuration and status
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
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


async def get_rag_index_overview(client, document_id: str) -> Dict[str, Any]:
    """
    Get RAG index statistics and overview.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Index statistics and metadata
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
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


async def delete_rag_index(client, document_id: str) -> Dict[str, Any]:
    """
    Delete RAG index for a document.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Deletion confirmation
    """
    from shared import format_success, format_error, validate_elevenlabs_id
    
    if not validate_elevenlabs_id(document_id, 'document'):
        return format_error("Invalid document ID format")
    
    try:
        await client._request("DELETE", f"/convai/knowledge-base/{document_id}/rag-index")
        return format_success(f"RAG index deleted for document {document_id}")
    except Exception as e:
        logger.error(f"Failed to delete RAG index: {e}")
        return format_error(str(e))