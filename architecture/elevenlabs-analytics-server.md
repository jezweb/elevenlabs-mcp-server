# ElevenLabs Analytics Server Architecture

## Overview
The `elevenlabs-analytics` MCP server provides comprehensive usage analytics, billing information, generation history tracking, and monitoring capabilities for ElevenLabs API usage.

## API Endpoints

### 1. User & Subscription

#### Get User Info
- **Endpoint**: `GET /v1/user`
- **Description**: Get current user information
- **Response**:
  ```json
  {
    "xi_api_key": "string",
    "email": "string",
    "can_use_instant_voice_cloning": true,
    "can_use_professional_voice_cloning": true,
    "can_use_delayed_payment_methods": true,
    "is_new_user": false,
    "max_history_items": 1000,
    "voice_limit": 10,
    "professional_voice_limit": 5,
    "can_extend_voice_limit": true,
    "allowed_to_extend_character_limit": true,
    "can_use_instant_voice_cloning": true,
    "can_use_professional_voice_cloning": true,
    "can_extend_voice_limit": true,
    "can_add_project": true,
    "can_delete_project": true,
    "can_monitor_project_usage": true,
    "uses_gravatar": true,
    "gravatar_url": "string"
  }
  ```

#### Get Subscription Info
- **Endpoint**: `GET /v1/user/subscription`
- **Description**: Get subscription details and quotas
- **Response**:
  ```json
  {
    "tier": "free|starter|creator|pro|scale|business",
    "character_count": 10000,
    "character_limit": 10000,
    "can_extend_character_limit": true,
    "allowed_to_extend_character_limit": true,
    "next_character_count_reset_unix": 1234567890,
    "voice_limit": 10,
    "max_voice_add_edits": 5,
    "voice_add_edit_counter": 2,
    "professional_voice_limit": 5,
    "can_extend_voice_limit": true,
    "can_use_instant_voice_cloning": true,
    "can_use_professional_voice_cloning": true,
    "available_models": [
      {
        "model_id": "eleven_multilingual_v2",
        "display_name": "Eleven Multilingual v2"
      }
    ],
    "currency": "USD",
    "status": "active|trialing|past_due|paused|deleted",
    "billing_period": "monthly|annual",
    "character_refresh_period": "monthly|weekly|daily",
    "next_invoice": {
      "amount_due_cents": 1999,
      "next_payment_attempt_unix": 1234567890
    },
    "has_open_invoices": false
  }
  ```

### 2. Usage Statistics

#### Get Character Usage Stats
- **Endpoint**: `GET /v1/usage/character-stats`
- **Description**: Get detailed character usage metrics
- **Parameters**:
  - `start_unix` (query, required): Start timestamp
  - `end_unix` (query, required): End timestamp
  - `include_workspace_metrics` (query, optional): Include workspace stats
  - `breakdown_type` (query, optional): How to segment data
    - Options: "voice", "user", "apikey", "model", "language"
  - `aggregation_interval` (query, optional): Time aggregation
    - Options: "minute", "hour", "day", "week", "month"
- **Response**:
  ```json
  {
    "time": [1234567890, 1234567891],
    "usage": {
      "voice_id_1": [1000, 1500],
      "voice_id_2": [500, 750]
    },
    "total": [1500, 2250],
    "metadata": {
      "aggregation_interval": "day",
      "breakdown_type": "voice"
    }
  }
  ```

#### Get TTS Usage Stats
- **Endpoint**: `GET /v1/usage/tts-stats`
- **Description**: Get text-to-speech specific usage
- **Parameters**: Same as character-stats
- **Response**: Similar structure with TTS-specific metrics

#### Get STS Usage Stats
- **Endpoint**: `GET /v1/usage/sts-stats`
- **Description**: Get speech-to-speech usage
- **Parameters**: Same as character-stats

#### Get VC Usage Stats
- **Endpoint**: `GET /v1/usage/vc-stats`
- **Description**: Get voice cloning usage statistics
- **Parameters**: Same as character-stats

### 3. History Management

#### Get History
- **Endpoint**: `GET /v1/history`
- **Description**: Get list of generated audio items
- **Parameters**:
  - `page_size` (query, optional): 1-1000 (default 100)
  - `start_after_history_item_id` (query, optional): Pagination cursor
  - `voice_id` (query, optional): Filter by voice
  - `search` (query, optional): Search term
  - `source` (query, optional): "TTS" or "STS"
  - `start_date_unix` (query, optional): Filter start date
  - `end_date_unix` (query, optional): Filter end date
- **Response**:
  ```json
  {
    "history": [
      {
        "history_item_id": "string",
        "request_id": "string",
        "voice_id": "string",
        "model_id": "string",
        "voice_name": "string",
        "voice_category": "premade|cloned|generated",
        "text": "string",
        "date_unix": 1234567890,
        "character_count_from_text": 100,
        "character_count_change": 100,
        "content_type": "text|ssml",
        "source": "TTS|STS",
        "settings": {
          "stability": 0.5,
          "similarity_boost": 0.75,
          "style": 0.0,
          "use_speaker_boost": true
        },
        "feedback": {
          "thumbs_up": true,
          "feedback": "string",
          "emotions": true,
          "inaccurate_clone": false,
          "glitches": false,
          "audio_quality": true,
          "other": false
        },
        "share_link_id": "string",
        "state": "created|deleted|processing"
      }
    ],
    "has_more": true,
    "last_history_item_id": "string"
  }
  ```

#### Get History Item
- **Endpoint**: `GET /v1/history/{history_item_id}`
- **Description**: Get single history item details
- **Parameters**:
  - `history_item_id` (path, required): History item ID

#### Get History Item Audio
- **Endpoint**: `GET /v1/history/{history_item_id}/audio`
- **Description**: Download audio for history item
- **Parameters**:
  - `history_item_id` (path, required): History item ID
- **Response**: Audio file stream

#### Delete History Item
- **Endpoint**: `DELETE /v1/history/{history_item_id}`
- **Description**: Delete a history item
- **Parameters**:
  - `history_item_id` (path, required): History item ID

#### Download History Items
- **Endpoint**: `POST /v1/history/download`
- **Description**: Download multiple history items as ZIP
- **Parameters**:
  - `history_item_ids` (body, required): Array of IDs
  - `output_format` (body, optional): Audio format
- **Response**: ZIP file stream

### 4. Billing & Invoices

#### Get Invoices
- **Endpoint**: `GET /v1/invoices`
- **Description**: Get billing invoices
- **Parameters**:
  - `page_size` (query, optional): Results per page
  - `start_after_invoice_id` (query, optional): Pagination cursor
- **Response**:
  ```json
  {
    "invoices": [
      {
        "invoice_id": "string",
        "amount_due_cents": 1999,
        "currency": "USD",
        "status": "paid|open|void",
        "created_unix": 1234567890,
        "due_unix": 1234567890,
        "paid_unix": 1234567890,
        "period_start": 1234567890,
        "period_end": 1234567890,
        "pdf_url": "string",
        "items": [
          {
            "description": "Pro subscription",
            "amount_cents": 1999,
            "quantity": 1
          }
        ]
      }
    ],
    "has_more": true
  }
  ```

#### Get Invoice
- **Endpoint**: `GET /v1/invoices/{invoice_id}`
- **Description**: Get specific invoice details
- **Parameters**:
  - `invoice_id` (path, required): Invoice ID

### 5. Workspace Analytics

#### Get Workspace Usage
- **Endpoint**: `GET /v1/admin/usage`
- **Description**: Get workspace-wide usage statistics
- **Parameters**:
  - `start_unix` (query, required): Start timestamp
  - `end_unix` (query, required): End timestamp
  - `breakdown_by_user` (query, optional): Per-user breakdown
- **Response**:
  ```json
  {
    "workspace_total": 100000,
    "by_user": {
      "user_id_1": 50000,
      "user_id_2": 50000
    },
    "by_api_key": {
      "key_1": 30000,
      "key_2": 70000
    }
  }
  ```

#### Get Workspace Activity
- **Endpoint**: `GET /v1/admin/activity`
- **Description**: Get workspace activity log
- **Parameters**:
  - `page_size` (query, optional): Results per page
  - `start_after_activity_id` (query, optional): Pagination cursor
- **Response**: Activity log entries

## Tool Implementations

### Core Tools

```python
@mcp.tool()
async def get_subscription_info() -> Dict[str, Any]:
    """Get current subscription details and quotas."""

@mcp.tool()
async def get_character_usage(
    start_date: str,
    end_date: str,
    breakdown_by: Optional[str] = None,
    aggregation: str = "day"
) -> Dict[str, Any]:
    """Get character usage statistics."""

@mcp.tool()
async def get_usage_summary(
    days: int = 30
) -> Dict[str, Any]:
    """Get usage summary for the last N days."""

@mcp.tool()
async def get_generation_history(
    page_size: int = 100,
    voice_id: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get audio generation history."""

@mcp.tool()
async def get_history_item(
    history_item_id: str,
    include_audio: bool = False
) -> Dict[str, Any]:
    """Get specific history item details."""

@mcp.tool()
async def download_history_audio(
    history_item_id: str,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """Download audio for history item."""

@mcp.tool()
async def delete_history_item(
    history_item_id: str
) -> Dict[str, Any]:
    """Delete a history item."""

@mcp.tool()
async def get_invoices(
    page_size: int = 20
) -> Dict[str, Any]:
    """Get billing invoices."""

@mcp.tool()
async def get_invoice_details(
    invoice_id: str
) -> Dict[str, Any]:
    """Get specific invoice details."""

@mcp.tool()
async def analyze_voice_usage(
    voice_id: str,
    days: int = 30
) -> Dict[str, Any]:
    """Analyze usage for specific voice."""

@mcp.tool()
async def get_cost_breakdown(
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """Get cost breakdown by feature."""

@mcp.tool()
async def export_usage_report(
    start_date: str,
    end_date: str,
    format: str = "csv"
) -> Dict[str, Any]:
    """Export usage report."""

@mcp.tool()
async def get_quota_status() -> Dict[str, Any]:
    """Get current quota usage and limits."""

@mcp.tool()
async def predict_usage(
    days_ahead: int = 7
) -> Dict[str, Any]:
    """Predict future usage based on trends."""
```

## Resources

```python
@mcp.resource("usage://current")
async def get_current_usage() -> Resource:
    """Get current usage as resource."""

@mcp.resource("history://recent")
async def get_recent_history() -> Resource:
    """Get recent generation history."""

@mcp.resource("invoice://{invoice_id}")
async def get_invoice_resource(invoice_id: str) -> Resource:
    """Get invoice as resource."""

@mcp.resource("report://monthly/{year}/{month}")
async def get_monthly_report(year: int, month: int) -> Resource:
    """Get monthly usage report."""
```

## Configuration

### Environment Variables
- `ELEVENLABS_API_KEY`: Required API key
- `DEFAULT_PAGE_SIZE`: Default pagination size
- `HISTORY_RETENTION_DAYS`: Days to keep history
- `REPORT_OUTPUT_DIR`: Directory for reports
- `TIMEZONE`: Timezone for reports (default UTC)

### Aggregation Options
- `minute`: Minute-level granularity
- `hour`: Hourly aggregation
- `day`: Daily aggregation (default)
- `week`: Weekly aggregation
- `month`: Monthly aggregation

### Breakdown Types
- `voice`: Usage by voice
- `user`: Usage by user
- `apikey`: Usage by API key
- `model`: Usage by model
- `language`: Usage by language
- `feature`: Usage by feature (TTS/STS/VC)

## Error Handling

```python
class QuotaExceededError(Exception):
    """Usage quota exceeded."""

class HistoryNotFoundError(Exception):
    """History item not found."""

class InvoiceNotFoundError(Exception):
    """Invoice not found."""

class InsufficientDataError(Exception):
    """Not enough data for analysis."""
```

## Usage Examples

### Get Usage Summary
```python
result = await get_usage_summary(days=7)
# Returns: {
#   "total_characters": 50000,
#   "daily_average": 7142,
#   "remaining_quota": 450000,
#   "reset_date": "2024-02-01"
# }
```

### Analyze Voice Usage
```python
result = await analyze_voice_usage(
    voice_id="21m00Tcm4TlvDq8ikWAM",
    days=30
)
# Returns: {
#   "total_usage": 25000,
#   "percentage_of_total": 50,
#   "trend": "increasing",
#   "daily_breakdown": [...]
# }
```

### Export Usage Report
```python
result = await export_usage_report(
    start_date="2024-01-01",
    end_date="2024-01-31",
    format="csv"
)
# Returns: {"file_path": "/reports/january_2024.csv"}
```

## Analytics Features

### Real-time Monitoring
- Current quota usage
- Active generation tracking
- Rate limit monitoring
- Error rate tracking

### Historical Analysis
- Usage trends
- Cost analysis
- Voice popularity
- Model performance

### Predictive Analytics
- Usage forecasting
- Budget predictions
- Quota exhaustion warnings

### Reporting
- CSV/JSON exports
- Scheduled reports
- Custom dashboards
- Alert notifications

## Dependencies
- `elevenlabs>=1.0.0`
- `fastmcp>=0.3.0`
- `pandas>=2.0.0` (for analytics)
- `matplotlib>=3.7.0` (for visualizations)