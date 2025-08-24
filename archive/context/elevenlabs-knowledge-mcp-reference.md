# ElevenLabs Knowledge Base MCP Server Reference

## Purpose
A specialized MCP server focused on knowledge base management, RAG (Retrieval-Augmented Generation) configuration, conversation context, and data collection for ElevenLabs Conversational AI agents.

## API Endpoints Coverage

### Knowledge Base Management Endpoints (12 endpoints)

| Endpoint | Method | Path | Description | Priority |
|----------|--------|------|-------------|----------|
| List Documents | GET | `/v1/convai/knowledge-base` | List all KB documents | **High** |
| Create from URL | POST | `/v1/convai/knowledge-base/url` | Add document from URL | **High** |
| Create from Text | POST | `/v1/convai/knowledge-base/text` | Add text document | **High** |
| Create from File | POST | `/v1/convai/knowledge-base/file` | Upload document file | **High** |
| Get Document | GET | `/v1/convai/knowledge-base/{document_id}` | Retrieve document details | **Medium** |
| Update Document | PATCH | `/v1/convai/knowledge-base/{document_id}` | Modify document | **Medium** |
| Delete Document | DELETE | `/v1/convai/knowledge-base/{document_id}` | Remove document | **Medium** |
| Get Document Content | GET | `/v1/convai/knowledge-base/{document_id}/content` | Full text retrieval | **Low** |
| Get Document Chunks | GET | `/v1/convai/knowledge-base/{document_id}/chunks` | Get processed chunks | **Low** |
| Compute RAG Index | POST | `/v1/convai/knowledge-base/compute-index` | Build search index | **High** |
| Get RAG Index | GET | `/v1/convai/knowledge-base/index` | Retrieve index status | **Medium** |
| Get KB Size | GET | `/v1/convai/knowledge-base/size` | Storage metrics | **Low** |

### Conversation Management Endpoints (7 endpoints)

| Endpoint | Method | Path | Description | Priority |
|----------|--------|------|-------------|----------|
| List Conversations | GET | `/v1/convai/conversations` | Get all conversations | **High** |
| Get Conversation | GET | `/v1/convai/conversations/{conversation_id}` | Full conversation details | **High** |
| Get Transcript | GET | `/v1/convai/conversations/{conversation_id}/transcript` | Text transcript | **High** |
| Get Audio | GET | `/v1/convai/conversations/{conversation_id}/audio` | Audio recording | **Medium** |
| Delete Conversation | DELETE | `/v1/convai/conversations/{conversation_id}` | Remove conversation | **Low** |
| Send Feedback | POST | `/v1/convai/conversations/{conversation_id}/feedback` | Rate conversation | **Medium** |
| Get Signed URL | GET | `/v1/convai/conversations/{conversation_id}/signed-url` | Secure download link | **Low** |

### Data Collection Endpoints (5 endpoints)

| Endpoint | Method | Path | Description | Priority |
|----------|--------|------|-------------|----------|
| Create Collection Schema | POST | `/v1/convai/data-collection/schema` | Define data points | **High** |
| List Collected Data | GET | `/v1/convai/data-collection` | Retrieve collected data | **High** |
| Export Data | POST | `/v1/convai/data-collection/export` | Bulk data export | **Medium** |
| Create Evaluation Criteria | POST | `/v1/convai/evaluation/criteria` | Setup metrics | **High** |
| Get Evaluation Results | GET | `/v1/convai/evaluation/results` | Performance data | **Medium** |

## Knowledge Base Configuration

### Document Types and Formats

```python
class SupportedFormats:
    """File formats accepted by knowledge base"""
    
    DOCUMENTS = [
        '.pdf',    # PDF documents (most common)
        '.docx',   # Word documents
        '.txt',    # Plain text files
        '.html',   # Web pages
        '.epub',   # E-books
        '.md',     # Markdown (convert to .txt first)
    ]
    
    MAX_FILE_SIZE_MB = 50
    MAX_DOCUMENTS_PER_AGENT = 100
    MAX_TOTAL_STORAGE_GB = 10
```

### Document Processing Configuration

```python
class DocumentProcessingConfig:
    """RAG and chunking configuration"""
    
    # Chunking parameters
    chunk_size: int = 512              # Characters per chunk
    chunk_overlap: int = 50            # Overlap between chunks
    separators: List[str] = ["\n\n", "\n", ". ", " "]
    
    # Embedding configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    
    # Search configuration
    similarity_threshold: float = 0.7   # Minimum relevance score
    top_k: int = 5                     # Number of results
    rerank_enabled: bool = True        # Secondary ranking
    
    # Processing options
    extract_metadata: bool = True      # Title, author, date
    ocr_enabled: bool = True          # For scanned PDFs
    language_detection: bool = True    # Auto-detect language
```

## Document Management Implementation

### Create Document from URL

```python
from elevenlabs import ElevenLabs
from typing import Optional, Dict, Any
import validators

client = ElevenLabs(api_key="your_api_key")

def add_url_to_knowledge_base(
    agent_id: str,
    url: str,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Add web page to agent's knowledge base"""
    
    # Validate URL
    if not validators.url(url):
        raise ValueError(f"Invalid URL: {url}")
    
    # Auto-generate name from URL if not provided
    if not name:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        name = f"{parsed.netloc} - {parsed.path}".replace("/", "_")
    
    # Create document from URL
    doc_response = client.conversational_ai.knowledge_base.documents.create_from_url(
        name=name,
        url=url,
        metadata=metadata or {},
        process_options={
            "extract_images": True,
            "follow_links": False,
            "max_depth": 1
        }
    )
    
    # Attach to agent
    agent = client.conversational_ai.agents.get(agent_id)
    agent.conversation_config.agent.prompt.knowledge_base.append({
        "type": "url",
        "name": name,
        "id": doc_response.id
    })
    
    # Update agent configuration
    client.conversational_ai.agents.update(
        agent_id=agent_id,
        conversation_config=agent.conversation_config
    )
    
    return doc_response.id
```

### Create Document from File

```python
import mimetypes
from pathlib import Path

def add_file_to_knowledge_base(
    agent_id: str,
    file_path: str,
    name: Optional[str] = None,
    auto_chunk: bool = True
) -> str:
    """Upload document file to knowledge base"""
    
    path = Path(file_path)
    
    # Validate file
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file size
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > 50:
        raise ValueError(f"File too large: {file_size_mb:.2f}MB (max 50MB)")
    
    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(str(path))
    
    # Convert markdown to text if needed
    if path.suffix == '.md':
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create temporary text file
        temp_path = path.with_suffix('.txt')
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        path = temp_path
    
    # Upload file
    with open(path, 'rb') as file:
        doc_response = client.conversational_ai.knowledge_base.documents.create_from_file(
            name=name or path.stem,
            file=file,
            mime_type=mime_type,
            processing_config={
                "auto_chunk": auto_chunk,
                "chunk_size": 512,
                "overlap": 50
            }
        )
    
    # Attach to agent
    attach_document_to_agent(agent_id, doc_response.id, "file", name or path.stem)
    
    return doc_response.id
```

### Batch Document Upload

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

def batch_upload_documents(
    agent_id: str,
    file_paths: List[str],
    max_workers: int = 5
) -> Dict[str, str]:
    """Upload multiple documents concurrently"""
    
    results = {}
    errors = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all upload tasks
        future_to_path = {
            executor.submit(
                add_file_to_knowledge_base,
                agent_id,
                path
            ): path
            for path in file_paths
        }
        
        # Collect results
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                doc_id = future.result()
                results[path] = doc_id
                print(f"✓ Uploaded: {path}")
            except Exception as e:
                errors[path] = str(e)
                print(f"✗ Failed: {path} - {e}")
    
    # Rebuild RAG index after batch upload
    if results:
        rebuild_rag_index(agent_id)
    
    return {"success": results, "errors": errors}
```

## RAG Configuration and Optimization

### Configure RAG Settings

```python
def configure_rag_for_agent(
    agent_id: str,
    use_case: str = "general"
) -> None:
    """Optimize RAG settings for specific use cases"""
    
    configs = {
        "general": {
            "chunk_size": 512,
            "overlap": 50,
            "top_k": 5,
            "similarity_threshold": 0.7
        },
        "technical": {
            "chunk_size": 1024,  # Larger for code/docs
            "overlap": 100,
            "top_k": 10,
            "similarity_threshold": 0.8
        },
        "conversational": {
            "chunk_size": 256,  # Smaller for dialogue
            "overlap": 25,
            "top_k": 3,
            "similarity_threshold": 0.6
        },
        "legal": {
            "chunk_size": 2048,  # Large for context
            "overlap": 200,
            "top_k": 15,
            "similarity_threshold": 0.9
        }
    }
    
    config = configs.get(use_case, configs["general"])
    
    # Update agent's RAG configuration
    client.conversational_ai.agents.update_rag_config(
        agent_id=agent_id,
        rag_config=config
    )
```

### Rebuild and Optimize Index

```python
def rebuild_rag_index(
    agent_id: str,
    force: bool = False
) -> Dict[str, Any]:
    """Rebuild search index for better performance"""
    
    # Get current index status
    status = client.conversational_ai.knowledge_base.get_index_status(agent_id)
    
    # Check if rebuild needed
    if not force and status.get("is_current", False):
        return {"status": "current", "message": "Index is up to date"}
    
    # Trigger index rebuild
    response = client.conversational_ai.knowledge_base.compute_index(
        agent_id=agent_id,
        options={
            "algorithm": "hnsw",  # Hierarchical Navigable Small World
            "metric": "cosine",
            "ef_construction": 200,
            "m": 16
        }
    )
    
    return {
        "status": "rebuilding",
        "estimated_time": response.get("estimated_seconds", 60),
        "document_count": response.get("document_count", 0)
    }
```

## Conversation Context Management

### Retrieve Conversation with Full Context

```python
def get_conversation_analysis(conversation_id: str) -> Dict[str, Any]:
    """Get comprehensive conversation analysis"""
    
    # Get conversation details
    conversation = client.conversational_ai.conversations.get(conversation_id)
    
    # Extract key metrics
    analysis = {
        "conversation_id": conversation_id,
        "duration_seconds": conversation.duration,
        "agent_id": conversation.agent_id,
        "start_time": conversation.start_time,
        "end_time": conversation.end_time,
        
        # Transcript analysis
        "transcript": parse_transcript(conversation.transcript),
        "turn_count": len(conversation.turns),
        "interruptions": count_interruptions(conversation),
        
        # Knowledge base usage
        "kb_queries": extract_kb_queries(conversation),
        "kb_documents_used": conversation.metadata.get("documents_referenced", []),
        
        # Performance metrics
        "average_response_time_ms": calculate_avg_response_time(conversation),
        "silence_duration_total": sum_silence_duration(conversation),
        
        # Outcomes
        "transfer_occurred": conversation.metadata.get("transfer", {}).get("occurred", False),
        "transfer_target": conversation.metadata.get("transfer", {}).get("target"),
        "ended_by": conversation.metadata.get("ended_by", "unknown"),
        
        # Data collected
        "data_points": conversation.data_collection or {},
        "evaluation_results": conversation.evaluation or {}
    }
    
    return analysis
```

### Parse and Structure Transcript

```python
def parse_transcript(transcript: str) -> List[Dict[str, Any]]:
    """Parse transcript into structured format"""
    
    lines = transcript.split('\n')
    structured_transcript = []
    current_speaker = None
    current_text = []
    
    for line in lines:
        # Detect speaker change
        if line.startswith(('Agent:', 'User:', 'Customer:')):
            # Save previous turn
            if current_speaker and current_text:
                structured_transcript.append({
                    "speaker": current_speaker,
                    "text": ' '.join(current_text),
                    "timestamp": extract_timestamp(line)
                })
            
            # Start new turn
            parts = line.split(':', 1)
            current_speaker = parts[0]
            current_text = [parts[1].strip()] if len(parts) > 1 else []
        else:
            # Continue current turn
            if line.strip():
                current_text.append(line.strip())
    
    # Add final turn
    if current_speaker and current_text:
        structured_transcript.append({
            "speaker": current_speaker,
            "text": ' '.join(current_text)
        })
    
    return structured_transcript
```

### Export Conversation Data

```python
def export_conversations(
    agent_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "csv"
) -> str:
    """Export conversation data for analysis"""
    
    import csv
    import json
    from datetime import datetime
    
    # Fetch conversations
    filters = {}
    if agent_id:
        filters["agent_id"] = agent_id
    if start_date:
        filters["start_time_after"] = start_date
    if end_date:
        filters["start_time_before"] = end_date
    
    conversations = client.conversational_ai.conversations.list(**filters)
    
    # Prepare export data
    export_data = []
    for conv in conversations:
        export_data.append({
            "conversation_id": conv.conversation_id,
            "agent_id": conv.agent_id,
            "start_time": conv.start_time,
            "duration_seconds": conv.duration,
            "transcript_preview": conv.transcript[:500],
            "transfer_occurred": conv.metadata.get("transfer", {}).get("occurred", False),
            "evaluation_score": conv.evaluation.get("overall_score"),
            "data_collected": json.dumps(conv.data_collection)
        })
    
    # Export based on format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "csv":
        filename = f"conversations_export_{timestamp}.csv"
        with open(filename, 'w', newline='') as f:
            if export_data:
                writer = csv.DictWriter(f, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
    
    elif format == "json":
        filename = f"conversations_export_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    return filename
```

## Data Collection Configuration

### Define Data Collection Schema

```python
def setup_data_collection(agent_id: str, use_case: str = "general") -> None:
    """Configure data points to collect during conversations"""
    
    schemas = {
        "sales": [
            {
                "name": "product_interest",
                "type": "string",
                "description": "Product customer is interested in"
            },
            {
                "name": "budget_range",
                "type": "string",
                "description": "Customer's budget range"
            },
            {
                "name": "purchase_timeline",
                "type": "string",
                "description": "When customer plans to purchase"
            },
            {
                "name": "lead_quality",
                "type": "integer",
                "description": "Lead score 1-10"
            }
        ],
        "support": [
            {
                "name": "issue_category",
                "type": "string",
                "description": "Type of issue"
            },
            {
                "name": "severity",
                "type": "string",
                "description": "Issue severity: low/medium/high/critical"
            },
            {
                "name": "resolved",
                "type": "boolean",
                "description": "Was issue resolved"
            },
            {
                "name": "escalated",
                "type": "boolean",
                "description": "Was escalation needed"
            }
        ],
        "booking": [
            {
                "name": "service_type",
                "type": "string",
                "description": "Service being booked"
            },
            {
                "name": "preferred_date",
                "type": "string",
                "description": "Customer's preferred date"
            },
            {
                "name": "preferred_time",
                "type": "string",
                "description": "Customer's preferred time"
            },
            {
                "name": "booking_confirmed",
                "type": "boolean",
                "description": "Was booking confirmed"
            }
        ]
    }
    
    schema = schemas.get(use_case, [])
    
    # Update agent with data collection schema
    client.conversational_ai.agents.update_data_collection(
        agent_id=agent_id,
        schema=schema
    )
```

### Configure Evaluation Criteria

```python
def setup_evaluation_criteria(
    agent_id: str,
    criteria_type: str = "standard"
) -> None:
    """Setup performance evaluation metrics"""
    
    criteria_sets = {
        "standard": [
            {
                "name": "Task Completion",
                "success_conditions": [
                    "Primary goal achieved",
                    "Customer need addressed",
                    "Appropriate action taken"
                ],
                "failure_conditions": [
                    "Failed to address need",
                    "Incorrect action",
                    "Conversation abandoned"
                ],
                "weight": 0.4
            },
            {
                "name": "Conversation Quality",
                "success_conditions": [
                    "Natural flow maintained",
                    "Professional tone used",
                    "Clear communication"
                ],
                "failure_conditions": [
                    "Awkward interactions",
                    "Unprofessional language",
                    "Confusion or misunderstanding"
                ],
                "weight": 0.3
            },
            {
                "name": "Efficiency",
                "success_conditions": [
                    "Quick resolution",
                    "Minimal repetition",
                    "Direct approach"
                ],
                "failure_conditions": [
                    "Excessive duration",
                    "Multiple repetitions",
                    "Unclear direction"
                ],
                "weight": 0.3
            }
        ],
        "technical": [
            {
                "name": "Technical Accuracy",
                "success_conditions": [
                    "Correct information provided",
                    "Accurate troubleshooting",
                    "Valid solutions offered"
                ],
                "failure_conditions": [
                    "Incorrect information",
                    "Wrong diagnosis",
                    "Invalid solutions"
                ],
                "weight": 0.5
            },
            {
                "name": "Knowledge Base Usage",
                "success_conditions": [
                    "Relevant documents referenced",
                    "Accurate retrieval",
                    "Appropriate context"
                ],
                "failure_conditions": [
                    "Failed to use KB when needed",
                    "Wrong documents referenced",
                    "Misinterpreted content"
                ],
                "weight": 0.3
            }
        ]
    }
    
    criteria = criteria_sets.get(criteria_type, criteria_sets["standard"])
    
    # Apply evaluation criteria
    client.conversational_ai.agents.update_evaluation(
        agent_id=agent_id,
        criteria=criteria
    )
```

## Analytics and Reporting

### Generate Performance Report

```python
def generate_agent_performance_report(
    agent_id: str,
    period_days: int = 7
) -> Dict[str, Any]:
    """Generate comprehensive performance report"""
    
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    # Fetch conversations
    conversations = client.conversational_ai.conversations.list(
        agent_id=agent_id,
        start_time_after=start_date.isoformat(),
        start_time_before=end_date.isoformat()
    )
    
    # Calculate metrics
    total_conversations = len(conversations)
    
    if total_conversations == 0:
        return {"message": "No conversations in period"}
    
    # Performance metrics
    metrics = {
        "period": f"{period_days} days",
        "total_conversations": total_conversations,
        
        "duration": {
            "average_seconds": sum(c.duration for c in conversations) / total_conversations,
            "min_seconds": min(c.duration for c in conversations),
            "max_seconds": max(c.duration for c in conversations)
        },
        
        "outcomes": {
            "successful": sum(1 for c in conversations if c.evaluation.get("success", False)),
            "transferred": sum(1 for c in conversations if c.metadata.get("transfer", {}).get("occurred")),
            "escalated": sum(1 for c in conversations if c.metadata.get("escalated", False))
        },
        
        "knowledge_base": {
            "queries_made": sum(len(c.metadata.get("kb_queries", [])) for c in conversations),
            "documents_used": set(
                doc 
                for c in conversations 
                for doc in c.metadata.get("documents_referenced", [])
            )
        },
        
        "evaluation_scores": calculate_evaluation_scores(conversations),
        "data_collection_summary": summarize_data_collection(conversations)
    }
    
    return metrics
```

### Track Knowledge Base Usage

```python
def analyze_kb_usage(agent_id: str) -> Dict[str, Any]:
    """Analyze knowledge base effectiveness"""
    
    # Get all documents
    documents = client.conversational_ai.knowledge_base.list(agent_id=agent_id)
    
    # Get recent conversations
    conversations = client.conversational_ai.conversations.list(
        agent_id=agent_id,
        limit=100
    )
    
    # Analyze usage
    doc_usage = {}
    for doc in documents:
        doc_usage[doc.id] = {
            "name": doc.name,
            "times_referenced": 0,
            "conversations": []
        }
    
    for conv in conversations:
        for doc_id in conv.metadata.get("documents_referenced", []):
            if doc_id in doc_usage:
                doc_usage[doc_id]["times_referenced"] += 1
                doc_usage[doc_id]["conversations"].append(conv.conversation_id)
    
    # Identify unused documents
    unused_docs = [
        doc_id for doc_id, usage in doc_usage.items()
        if usage["times_referenced"] == 0
    ]
    
    # Most used documents
    most_used = sorted(
        doc_usage.items(),
        key=lambda x: x[1]["times_referenced"],
        reverse=True
    )[:10]
    
    return {
        "total_documents": len(documents),
        "unused_documents": unused_docs,
        "most_used_documents": most_used,
        "average_references_per_conversation": sum(
            d["times_referenced"] for d in doc_usage.values()
        ) / len(conversations) if conversations else 0
    }
```

## Error Handling and Validation

### Document Validation

```python
def validate_document_before_upload(file_path: str) -> List[str]:
    """Validate document before adding to knowledge base"""
    
    from pathlib import Path
    import PyPDF2
    import docx
    
    errors = []
    warnings = []
    
    path = Path(file_path)
    
    # Check file exists
    if not path.exists():
        errors.append(f"File not found: {file_path}")
        return errors
    
    # Check file size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        errors.append(f"File too large: {size_mb:.2f}MB (max 50MB)")
    elif size_mb > 25:
        warnings.append(f"Large file: {size_mb:.2f}MB may take time to process")
    
    # Check format
    if path.suffix not in ['.pdf', '.docx', '.txt', '.html', '.epub']:
        if path.suffix == '.md':
            warnings.append("Markdown file will be converted to text")
        else:
            errors.append(f"Unsupported format: {path.suffix}")
    
    # Check content based on type
    try:
        if path.suffix == '.pdf':
            with open(path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                if pdf.is_encrypted:
                    errors.append("PDF is encrypted")
                if len(pdf.pages) > 500:
                    warnings.append(f"Large PDF: {len(pdf.pages)} pages")
                    
        elif path.suffix == '.docx':
            doc = docx.Document(path)
            if len(doc.paragraphs) < 1:
                errors.append("Document appears to be empty")
                
    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")
    
    return errors + warnings
```

### Conversation Error Recovery

```python
def handle_conversation_errors(conversation_id: str) -> Dict[str, Any]:
    """Analyze and recover from conversation errors"""
    
    try:
        conversation = client.conversational_ai.conversations.get(conversation_id)
    except Exception as e:
        return {"error": f"Failed to retrieve conversation: {str(e)}"}
    
    issues = []
    recommendations = []
    
    # Check for common issues
    if conversation.metadata.get("errors", []):
        for error in conversation.metadata["errors"]:
            if "knowledge_base" in error:
                issues.append("Knowledge base query failed")
                recommendations.append("Check document indexing")
            
            if "timeout" in error:
                issues.append("Response timeout occurred")
                recommendations.append("Reduce max_tokens or simplify prompt")
            
            if "transfer_failed" in error:
                issues.append("Agent transfer failed")
                recommendations.append("Verify target agent ID and availability")
    
    # Check performance issues
    if conversation.duration > 900:  # 15 minutes
        issues.append("Excessive conversation duration")
        recommendations.append("Add time limits or escalation rules")
    
    avg_response_time = calculate_avg_response_time(conversation)
    if avg_response_time > 5000:  # 5 seconds
        issues.append("Slow response times")
        recommendations.append("Optimize prompt or reduce knowledge base size")
    
    return {
        "conversation_id": conversation_id,
        "issues_found": issues,
        "recommendations": recommendations,
        "severity": "high" if len(issues) > 2 else "medium" if issues else "low"
    }
```

## Testing Strategies

### Knowledge Base Testing

```python
def test_knowledge_base_retrieval(
    agent_id: str,
    test_queries: List[str]
) -> Dict[str, Any]:
    """Test knowledge base query accuracy"""
    
    results = []
    
    for query in test_queries:
        # Simulate KB query
        response = client.conversational_ai.knowledge_base.query(
            agent_id=agent_id,
            query=query,
            top_k=5
        )
        
        results.append({
            "query": query,
            "documents_found": len(response.results),
            "top_result": response.results[0].document_name if response.results else None,
            "relevance_score": response.results[0].score if response.results else 0,
            "passed": response.results[0].score > 0.7 if response.results else False
        })
    
    # Calculate success rate
    success_rate = sum(1 for r in results if r["passed"]) / len(results)
    
    return {
        "total_queries": len(test_queries),
        "success_rate": success_rate,
        "results": results,
        "recommendation": "Good" if success_rate > 0.8 else "Needs improvement"
    }
```

### Data Collection Verification

```python
def verify_data_collection(agent_id: str, sample_size: int = 10) -> Dict[str, Any]:
    """Verify data collection is working correctly"""
    
    # Get recent conversations
    conversations = client.conversational_ai.conversations.list(
        agent_id=agent_id,
        limit=sample_size
    )
    
    # Check data collection
    collection_stats = {
        "total_checked": len(conversations),
        "with_data": 0,
        "complete_data": 0,
        "missing_fields": {},
        "data_quality": []
    }
    
    # Get expected schema
    agent = client.conversational_ai.agents.get(agent_id)
    expected_fields = [
        field["name"] 
        for field in agent.data_collection_schema
    ]
    
    for conv in conversations:
        data = conv.data_collection or {}
        
        if data:
            collection_stats["with_data"] += 1
            
            # Check completeness
            missing = [f for f in expected_fields if f not in data]
            if not missing:
                collection_stats["complete_data"] += 1
            else:
                for field in missing:
                    collection_stats["missing_fields"][field] = \
                        collection_stats["missing_fields"].get(field, 0) + 1
            
            # Assess data quality
            quality_score = assess_data_quality(data)
            collection_stats["data_quality"].append(quality_score)
    
    return collection_stats
```

## MCP Server Implementation

### Server Structure

```python
# elevenlabs_knowledge_mcp/server.py

from mcp import MCPServer
from elevenlabs import ElevenLabs
from typing import Optional, List, Dict, Any

class ElevenLabsKnowledgeMCP:
    """Specialized MCP for knowledge base and conversation management"""
    
    def __init__(self):
        self.client = ElevenLabs()
        self.server = MCPServer("elevenlabs-knowledge")
        self.register_tools()
    
    def register_tools(self):
        """Register all knowledge-related tools"""
        
        # Knowledge Base Management
        self.server.add_tool("add_document_url", self.add_document_url)
        self.server.add_tool("add_document_file", self.add_document_file)
        self.server.add_tool("add_document_text", self.add_document_text)
        self.server.add_tool("list_documents", self.list_documents)
        self.server.add_tool("delete_document", self.delete_document)
        self.server.add_tool("update_document", self.update_document)
        self.server.add_tool("batch_upload", self.batch_upload)
        
        # RAG Configuration
        self.server.add_tool("configure_rag", self.configure_rag)
        self.server.add_tool("rebuild_index", self.rebuild_index)
        self.server.add_tool("test_retrieval", self.test_retrieval)
        
        # Conversation Management
        self.server.add_tool("list_conversations", self.list_conversations)
        self.server.add_tool("get_conversation", self.get_conversation)
        self.server.add_tool("analyze_conversation", self.analyze_conversation)
        self.server.add_tool("export_conversations", self.export_conversations)
        
        # Data Collection
        self.server.add_tool("setup_data_collection", self.setup_data_collection)
        self.server.add_tool("setup_evaluation", self.setup_evaluation)
        self.server.add_tool("get_collected_data", self.get_collected_data)
        
        # Analytics
        self.server.add_tool("performance_report", self.performance_report)
        self.server.add_tool("kb_usage_analysis", self.kb_usage_analysis)
        self.server.add_tool("error_analysis", self.error_analysis)
    
    async def add_document_url(
        self,
        agent_id: str,
        url: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add document from URL to knowledge base"""
        # Implementation here
        pass
    
    async def configure_rag(
        self,
        agent_id: str,
        chunk_size: int = 512,
        overlap: int = 50,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Configure RAG settings for agent"""
        # Implementation here
        pass
```

### CLI Integration

```python
# elevenlabs_knowledge_mcp/cli.py

import click
from pathlib import Path

@click.group()
def cli():
    """ElevenLabs Knowledge Base Management CLI"""
    pass

@cli.command()
@click.option('--agent-id', required=True, help='Agent ID')
@click.option('--path', required=True, help='Path to documents')
@click.option('--recursive', is_flag=True, help='Include subdirectories')
def upload_folder(agent_id: str, path: str, recursive: bool):
    """Upload all documents in a folder"""
    
    folder = Path(path)
    pattern = '**/*' if recursive else '*'
    
    files = [
        f for f in folder.glob(pattern)
        if f.suffix in ['.pdf', '.docx', '.txt', '.html', '.epub']
    ]
    
    click.echo(f"Found {len(files)} documents")
    
    with click.progressbar(files) as bar:
        for file in bar:
            try:
                add_file_to_knowledge_base(agent_id, str(file))
            except Exception as e:
                click.echo(f"Failed: {file.name} - {e}", err=True)

@cli.command()
@click.option('--agent-id', required=True, help='Agent ID')
def analyze_usage(agent_id: str):
    """Analyze knowledge base usage"""
    
    analysis = analyze_kb_usage(agent_id)
    
    click.echo("Knowledge Base Usage Analysis")
    click.echo(f"Total Documents: {analysis['total_documents']}")
    click.echo(f"Unused Documents: {len(analysis['unused_documents'])}")
    
    click.echo("\nMost Used Documents:")
    for doc_id, usage in analysis['most_used_documents']:
        click.echo(f"  - {usage['name']}: {usage['times_referenced']} references")
```

## Implementation Priorities

### Phase 1: Core Knowledge Base (Week 1)
1. ✅ Add documents (URL, file, text)
2. ✅ List and manage documents
3. ✅ Basic RAG configuration
4. ✅ Attach to agents

### Phase 2: Conversation Management (Week 2)
1. List and retrieve conversations
2. Parse transcripts
3. Export functionality
4. Basic analytics

### Phase 3: Advanced Features (Week 3)
1. Data collection schemas
2. Evaluation criteria
3. Performance reporting
4. Usage analytics

### Phase 4: Optimization (Week 4)
1. Batch operations
2. Index optimization
3. Error recovery
4. Testing suite

## Next Steps

1. **Set Up Project Structure**
   ```bash
   elevenlabs-knowledge-mcp/
   ├── src/
   │   ├── server.py
   │   ├── knowledge_base.py
   │   ├── conversations.py
   │   ├── analytics.py
   │   └── utils.py
   ├── tests/
   ├── examples/
   └── README.md
   ```

2. **Implement Priority Endpoints**
   - Start with document upload
   - Add RAG configuration
   - Implement conversation retrieval

3. **Create Templates**
   - Document processing configs
   - Data collection schemas
   - Evaluation criteria sets

4. **Build Testing Framework**
   - Unit tests for each module
   - Integration tests
   - Performance benchmarks

## Resources

- [ElevenLabs KB API Docs](https://elevenlabs.io/docs/api-reference/knowledge-base)
- [RAG Best Practices](https://elevenlabs.io/docs/conversational-ai/rag-guide)
- [Conversation Analytics](https://elevenlabs.io/docs/conversational-ai/analytics)
- [Data Collection Guide](https://elevenlabs.io/docs/conversational-ai/data-collection)