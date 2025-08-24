"""
ElevenLabs Knowledge Tools
==========================
Knowledge base management and RAG configuration tools.
"""

# Document Management
from .documents import (
    add_document_url,
    add_document_text,
    list_documents,
    delete_document,
    get_document,
    update_document,
    add_document_file,
    get_document_content,
    get_document_chunk
)

# RAG Configuration
from .rag import (
    configure_rag,
    rebuild_index,
    compute_rag_index,
    get_rag_index,
    get_rag_index_overview,
    delete_rag_index
)

# Analytics
from .analytics import (
    get_dependent_agents,
    get_knowledge_base_size
)

__all__ = [
    # Documents
    'add_document_url',
    'add_document_text',
    'list_documents',
    'delete_document',
    'get_document',
    'update_document',
    'add_document_file',
    'get_document_content',
    'get_document_chunk',
    # RAG
    'configure_rag',
    'rebuild_index',
    'compute_rag_index',
    'get_rag_index',
    'get_rag_index_overview',
    'delete_rag_index',
    # Analytics
    'get_dependent_agents',
    'get_knowledge_base_size'
]