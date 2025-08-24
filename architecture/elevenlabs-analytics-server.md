# ElevenLabs Analytics Server Architecture

## Overview
The `elevenlabs-analytics` MCP server provides comprehensive usage analytics, billing information, generation history tracking, and monitoring capabilities for ElevenLabs API usage.

## Directory Structure (Modular)

```
elevenlabs-analytics/
├── src/
│   ├── server.py           # Main FastMCP server with tool registration
│   ├── utils.py            # Self-contained utilities (client, config, validation)
│   └── tools/
│       ├── __init__.py
│       ├── subscription_tools.py    # User & subscription management
│       ├── usage_tools.py          # Usage statistics and tracking
│       ├── history_tools.py        # Generation history management
│       ├── billing_tools.py        # Invoices and payment tracking
│       ├── analytics_tools.py      # Advanced analytics and reporting
│       └── export_tools.py         # Data export and reporting
├── requirements.txt
├── .env.example
└── README.md
```

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

## Modular Tool Implementation

### Tool Modules

#### 1. subscription_tools.py
```python
"""User and subscription management tools."""

async def get_user_info(client):
    """Get current user information."""
    
async def get_subscription_info(client):
    """Get subscription details and quotas."""
    
async def get_quota_status(client):
    """Get current quota usage and limits."""
    
async def check_subscription_limits(client):
    """Check if approaching any limits."""
```

#### 2. usage_tools.py
```python
"""Usage statistics and tracking tools."""

async def get_character_usage(client, start_date, end_date, breakdown_by=None, aggregation="day"):
    """Get character usage statistics."""
    
async def get_tts_usage(client, start_date, end_date, breakdown_by=None):
    """Get text-to-speech usage stats."""
    
async def get_sts_usage(client, start_date, end_date, breakdown_by=None):
    """Get speech-to-speech usage stats."""
    
async def get_vc_usage(client, start_date, end_date, breakdown_by=None):
    """Get voice cloning usage stats."""
    
async def get_usage_summary(client, days=30):
    """Get usage summary for the last N days."""
```

#### 3. history_tools.py
```python
"""Generation history management tools."""

async def get_generation_history(client, page_size=100, voice_id=None, search=None, start_date=None, end_date=None):
    """Get audio generation history."""
    
async def get_history_item(client, history_item_id):
    """Get specific history item details."""
    
async def download_history_audio(client, history_item_id, output_directory=None):
    """Download audio for history item."""
    
async def delete_history_item(client, history_item_id):
    """Delete a history item."""
    
async def batch_download_history(client, history_item_ids, output_format=None):
    """Download multiple history items as ZIP."""
```

#### 4. billing_tools.py
```python
"""Billing and invoice management tools."""

async def get_invoices(client, page_size=20):
    """Get billing invoices."""
    
async def get_invoice_details(client, invoice_id):
    """Get specific invoice details."""
    
async def get_payment_methods(client):
    """Get configured payment methods."""
    
async def get_billing_summary(client, months=6):
    """Get billing summary for recent months."""
```

#### 5. analytics_tools.py
```python
"""Advanced analytics and insights tools."""

async def analyze_voice_usage(client, voice_id, days=30):
    """Analyze usage for specific voice."""
    
async def get_cost_breakdown(client, start_date, end_date):
    """Get cost breakdown by feature."""
    
async def predict_usage(client, days_ahead=7):
    """Predict future usage based on trends."""
    
async def get_workspace_usage(client, start_unix, end_unix, breakdown_by_user=False):
    """Get workspace-wide usage statistics."""
    
async def get_workspace_activity(client, page_size=50):
    """Get workspace activity log."""
    
async def analyze_trends(client, metric="characters", period="month"):
    """Analyze usage trends over time."""
```

#### 6. export_tools.py
```python
"""Data export and reporting tools."""

async def export_usage_report(client, start_date, end_date, format="csv"):
    """Export usage report."""
    
async def generate_monthly_report(client, year, month):
    """Generate comprehensive monthly report."""
    
async def export_history_data(client, filters=None, format="json"):
    """Export generation history data."""
    
async def create_dashboard_data(client):
    """Create data for dashboard visualization."""
```

### Tool Registration (server.py)

```python
from fastmcp import FastMCP
from utils import Config, ElevenLabsClient

# Import all tool modules
from tools import (
    subscription_tools,
    usage_tools,
    history_tools,
    billing_tools,
    analytics_tools,
    export_tools
)

# Initialize
mcp = FastMCP(name="elevenlabs-analytics")
client = ElevenLabsClient(Config.API_KEY)

# Register subscription tools
@mcp.tool()
async def get_subscription_info():
    return await subscription_tools.get_subscription_info(client)

@mcp.tool()
async def get_quota_status():
    return await subscription_tools.get_quota_status(client)

# Register usage tools
@mcp.tool()
async def get_character_usage(start_date: str, end_date: str, breakdown_by: str = None, aggregation: str = "day"):
    return await usage_tools.get_character_usage(client, start_date, end_date, breakdown_by, aggregation)

@mcp.tool()
async def get_usage_summary(days: int = 30):
    return await usage_tools.get_usage_summary(client, days)

# Register history tools
@mcp.tool()
async def get_generation_history(page_size: int = 100, voice_id: str = None, search: str = None):
    return await history_tools.get_generation_history(client, page_size, voice_id, search)

# ... register remaining tools ...
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

## Self-Contained Utils Module

```python
"""
utils.py - All utilities for the analytics server
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
from functools import lru_cache
import pandas as pd
import json

logger = logging.getLogger(__name__)

# ============================================================
# Configuration
# ============================================================

class Config:
    """Configuration from environment variables."""
    API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    API_BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Analytics settings
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "100"))
    HISTORY_RETENTION_DAYS = int(os.getenv("HISTORY_RETENTION_DAYS", "90"))
    REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "./reports")
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    
    # Cache settings
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    
    # Export settings
    MAX_EXPORT_ROWS = int(os.getenv("MAX_EXPORT_ROWS", "10000"))
    EXPORT_BATCH_SIZE = int(os.getenv("EXPORT_BATCH_SIZE", "500"))
    
    @classmethod
    def validate(cls):
        if not cls.API_KEY:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")

# ============================================================
# API Client
# ============================================================

class ElevenLabsClient:
    """Analytics-focused API client."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.API_BASE_URL
        self._session = None
        self._usage_cache = {}
        self._cache_timestamps = {}
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
            )
        return self._session
    
    async def get_subscription(self) -> Dict[str, Any]:
        """Get subscription information."""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/user/subscription") as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_usage_stats(
        self,
        start_unix: int,
        end_unix: int,
        stat_type: str = "character-stats",
        **params
    ) -> Dict[str, Any]:
        """Get usage statistics."""
        cache_key = f"{stat_type}_{start_unix}_{end_unix}_{json.dumps(params, sort_keys=True)}"
        
        # Check cache
        if cache_key in self._usage_cache:
            if datetime.now().timestamp() - self._cache_timestamps[cache_key] < Config.CACHE_TTL:
                return self._usage_cache[cache_key]
        
        session = await self._get_session()
        url = f"{self.base_url}/usage/{stat_type}"
        params = {
            "start_unix": start_unix,
            "end_unix": end_unix,
            **params
        }
        
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            
            # Cache result
            self._usage_cache[cache_key] = data
            self._cache_timestamps[cache_key] = datetime.now().timestamp()
            
            return data
    
    async def get_history(self, **params) -> Dict[str, Any]:
        """Get generation history."""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/history", params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def download_history_audio(self, history_item_id: str) -> bytes:
        """Download audio for history item."""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/history/{history_item_id}/audio") as response:
            response.raise_for_status()
            return await response.read()
    
    async def get_invoices(self, **params) -> Dict[str, Any]:
        """Get billing invoices."""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/invoices", params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def close(self):
        """Close the client session."""
        if self._session:
            await self._session.close()

# ============================================================
# Analytics Utilities
# ============================================================

def calculate_usage_trends(data: List[Dict], window: int = 7) -> Dict[str, Any]:
    """Calculate usage trends from raw data."""
    if not data:
        return {"trend": "insufficient_data"}
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('date')
    
    # Calculate rolling average
    rolling_avg = df['usage'].rolling(window=window).mean()
    
    # Calculate trend
    if len(rolling_avg) >= 2:
        recent = rolling_avg.iloc[-1]
        previous = rolling_avg.iloc[-window] if len(rolling_avg) > window else rolling_avg.iloc[0]
        change_pct = ((recent - previous) / previous * 100) if previous > 0 else 0
        
        if change_pct > 10:
            trend = "increasing"
        elif change_pct < -10:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "trend": trend,
        "change_percentage": change_pct if 'change_pct' in locals() else 0,
        "current_average": rolling_avg.iloc[-1] if len(rolling_avg) > 0 else 0,
        "window_days": window
    }

def predict_usage(
    historical_data: List[Dict],
    days_ahead: int = 7
) -> Dict[str, Any]:
    """Predict future usage based on historical data."""
    if len(historical_data) < 14:  # Need at least 2 weeks
        return {"error": "Insufficient data for prediction"}
    
    df = pd.DataFrame(historical_data)
    df['date'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('date')
    
    # Simple linear regression for prediction
    from scipy import stats
    x = range(len(df))
    y = df['usage'].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Predict future values
    predictions = []
    for i in range(days_ahead):
        future_index = len(df) + i
        predicted_value = slope * future_index + intercept
        predictions.append({
            "date": (df.index[-1] + timedelta(days=i+1)).strftime("%Y-%m-%d"),
            "predicted_usage": max(0, predicted_value)  # Ensure non-negative
        })
    
    return {
        "predictions": predictions,
        "confidence": r_value ** 2,  # R-squared
        "trend_slope": slope
    }

def aggregate_usage_data(
    data: Dict[str, List],
    aggregation: str = "day"
) -> Dict[str, Any]:
    """Aggregate usage data by specified interval."""
    aggregated = {}
    
    for key, values in data.items():
        df = pd.DataFrame(values)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Set aggregation rule
        if aggregation == "hour":
            rule = "H"
        elif aggregation == "day":
            rule = "D"
        elif aggregation == "week":
            rule = "W"
        elif aggregation == "month":
            rule = "M"
        else:
            rule = "D"
        
        # Perform aggregation
        df = df.set_index('timestamp').resample(rule).sum()
        aggregated[key] = df.to_dict('records')
    
    return aggregated

# ============================================================
# Export Utilities
# ============================================================

async def export_to_csv(data: List[Dict], filename: str) -> str:
    """Export data to CSV file."""
    output_path = os.path.join(Config.REPORT_OUTPUT_DIR, filename)
    os.makedirs(Config.REPORT_OUTPUT_DIR, exist_ok=True)
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    
    return output_path

async def export_to_json(data: Any, filename: str) -> str:
    """Export data to JSON file."""
    output_path = os.path.join(Config.REPORT_OUTPUT_DIR, filename)
    os.makedirs(Config.REPORT_OUTPUT_DIR, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return output_path

# ============================================================
# Validation
# ============================================================

def validate_date_range(start_date: str, end_date: str) -> tuple:
    """Validate and parse date range."""
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        if start > end:
            raise ValueError("Start date must be before end date")
        
        # Check maximum range (1 year)
        if (end - start).days > 365:
            raise ValueError("Date range cannot exceed 365 days")
        
        return int(start.timestamp()), int(end.timestamp())
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")

def validate_aggregation(aggregation: str) -> str:
    """Validate aggregation parameter."""
    valid = ["minute", "hour", "day", "week", "month"]
    if aggregation not in valid:
        raise ValueError(f"Invalid aggregation: {aggregation}. Must be one of {valid}")
    return aggregation

def validate_breakdown(breakdown: str) -> str:
    """Validate breakdown parameter."""
    valid = ["voice", "user", "apikey", "model", "language", "feature"]
    if breakdown and breakdown not in valid:
        raise ValueError(f"Invalid breakdown: {breakdown}. Must be one of {valid}")
    return breakdown

# ============================================================
# Response Formatting
# ============================================================

def format_usage_response(data: Dict[str, Any], include_summary: bool = True) -> Dict[str, Any]:
    """Format usage data response."""
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    if include_summary and "usage" in data:
        total = sum(sum(values) for values in data["usage"].values())
        response["summary"] = {
            "total_usage": total,
            "period_start": data.get("period_start"),
            "period_end": data.get("period_end"),
            "breakdown_type": data.get("metadata", {}).get("breakdown_type")
        }
    
    return response

def format_error(error: Exception) -> Dict[str, Any]:
    """Format error response."""
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "timestamp": datetime.now().isoformat()
    }
```

## Dependencies
- `elevenlabs>=1.0.0`
- `fastmcp>=0.3.0`
- `pandas>=2.0.0` (for analytics)
- `scipy>=1.11.0` (for predictions)
- `aiohttp>=3.9.0`