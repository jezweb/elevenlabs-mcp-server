"""Data models for ElevenLabs MCP servers."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """Configuration for an ElevenLabs conversational AI agent."""
    
    name: str = Field(..., description="Agent display name")
    agent_id: Optional[str] = Field(None, description="Unique agent identifier")
    description: Optional[str] = Field(None, description="Agent description")
    
    # Core configuration
    system_prompt: str = Field(..., description="System instructions for the agent")
    first_message: str = Field(..., description="Initial greeting message")
    language: str = Field("en", description="ISO 639-1 language code")
    
    # LLM settings
    llm_model: str = Field("gemini-2.0-flash-001", description="LLM model to use")
    temperature: float = Field(0.5, ge=0.0, le=1.0, description="Response creativity")
    max_tokens: Optional[int] = Field(None, description="Maximum response tokens")
    
    # Voice settings
    voice_id: str = Field("cgSgspJ2msm6clMCkdW9", description="ElevenLabs voice ID")
    tts_model: str = Field("eleven_turbo_v2", description="TTS model")
    stability: float = Field(0.5, ge=0.0, le=1.0)
    similarity_boost: float = Field(0.8, ge=0.0, le=1.0)
    
    # Conversation settings
    turn_timeout: int = Field(7, description="Seconds to wait for response")
    max_duration: int = Field(300, description="Maximum call duration in seconds")
    
    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        """Validate language code."""
        valid_languages = ["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"]
        if v not in valid_languages:
            raise ValueError(f"Language must be one of {valid_languages}")
        return v


class ConversationData(BaseModel):
    """Data from a conversation."""
    
    conversation_id: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Transcript data
    transcript: Optional[str] = None
    turn_count: int = 0
    
    # Metadata
    transfer_occurred: bool = False
    transfer_target: Optional[str] = None
    ended_by: str = "unknown"
    
    # Analytics
    average_response_time_ms: Optional[float] = None
    total_silence_duration: Optional[float] = None
    
    # Data collection
    collected_data: Dict[str, Any] = Field(default_factory=dict)
    evaluation_score: Optional[float] = None


class DocumentData(BaseModel):
    """Knowledge base document data."""
    
    document_id: Optional[str] = None
    name: str
    type: str = Field("text", description="Document type: url, file, text")
    
    # Content
    content: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None
    
    # Processing
    chunk_size: int = Field(512, description="Characters per chunk")
    chunk_overlap: int = Field(50, description="Overlap between chunks")
    chunks_count: Optional[int] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate document type."""
        valid_types = ["url", "file", "text"]
        if v not in valid_types:
            raise ValueError(f"Type must be one of {valid_types}")
        return v


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    suggestion: Optional[str] = Field(None, description="How to resolve the error")
    
    @classmethod
    def from_exception(cls, e: Exception, suggestion: Optional[str] = None):
        """Create from an exception."""
        return cls(
            error=type(e).__name__,
            message=str(e),
            suggestion=suggestion
        )


class TransferConfig(BaseModel):
    """Configuration for agent transfers."""
    
    type: str = Field(..., description="Transfer type: agent, number, end_call")
    target: Optional[str] = Field(None, description="Target agent ID or phone number")
    conditions: str = Field(..., description="Natural language transfer conditions")
    message: Optional[str] = Field(None, description="Transfer announcement message")
    pass_context: bool = Field(True, description="Share conversation history")
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate transfer type."""
        valid_types = ["agent", "number", "end_call"]
        if v not in valid_types:
            raise ValueError(f"Type must be one of {valid_types}")
        return v


class RAGConfig(BaseModel):
    """RAG (Retrieval-Augmented Generation) configuration."""
    
    chunk_size: int = Field(512, ge=100, le=4000)
    chunk_overlap: int = Field(50, ge=0, le=500)
    top_k: int = Field(5, ge=1, le=20)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    
    # Embedding settings
    embedding_model: str = Field("text-embedding-3-small")
    embedding_dimensions: int = Field(1536)
    
    # Search settings
    rerank_enabled: bool = Field(True)
    hybrid_search: bool = Field(False)
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v, info):
        """Ensure overlap is less than chunk size."""
        if info.data.get("chunk_size") and v >= info.data["chunk_size"]:
            raise ValueError("Overlap must be less than chunk size")
        return v