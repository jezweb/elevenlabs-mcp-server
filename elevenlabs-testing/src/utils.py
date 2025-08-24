"""Utility functions for ElevenLabs Testing MCP server."""

import asyncio
import functools
import logging
import os
import re
from typing import Any, Dict, List, Optional, TypeVar, Callable
from datetime import datetime

import httpx
from httpx import AsyncClient


# Configuration
class Config:
    """Configuration for ElevenLabs Testing server."""
    API_KEY = os.getenv("ELEVENLABS_API_KEY")
    API_BASE_URL = os.getenv("ELEVENLABS_API_BASE_URL", "https://api.elevenlabs.io/v1")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))


# Logging setup
def setup_logging(name: str) -> logging.Logger:
    """Setup logging configuration."""
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    return logger


logger = setup_logging(__name__)


# Type variable for decorators
T = TypeVar('T')


# Retry decorator
def retry_with_backoff(max_retries: int = 3):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e
            
            # If all retries failed, raise the last exception
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


# API Client
class ElevenLabsClient:
    """Async client for ElevenLabs API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ElevenLabs client."""
        self.api_key = api_key or Config.API_KEY
        self.base_url = Config.API_BASE_URL
        self._client: Optional[AsyncClient] = None
        self._cache: Dict[str, Any] = {}
        
    async def _get_client(self) -> AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=httpx.Timeout(Config.API_TIMEOUT),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._client
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        use_cache: bool = False
    ) -> Dict[str, Any]:
        """Make an API request with retry logic."""
        import json
        
        # Check cache if enabled
        cache_key = f"{method}:{endpoint}:{json.dumps(params or {})}"
        if use_cache and method == "GET" and cache_key in self._cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]
        
        client = await self._get_client()
        
        @retry_with_backoff(max_retries=Config.MAX_RETRIES)
        async def _do_request():
            response = await client.request(
                method=method,
                url=endpoint,
                json=json_data,
                params=params,
                files=files
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        
        try:
            result = await _do_request()
            
            # Cache successful GET requests
            if use_cache and method == "GET":
                self._cache[cache_key] = result
                # Simple cache expiry - clear after TTL
                asyncio.create_task(self._expire_cache(cache_key))
            
            return result
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def _expire_cache(self, key: str):
        """Expire cache entry after TTL."""
        await asyncio.sleep(Config.CACHE_TTL)
        self._cache.pop(key, None)
    
    # Utility Methods
    
    async def test_connection(self) -> bool:
        """Test API connection."""
        try:
            await self._request("GET", "/user/subscription", use_cache=False)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Formatting helpers
def format_success(message: str, data: Any = None) -> Dict[str, Any]:
    """Format a success response."""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response


def format_error(error: str, suggestion: str = None) -> Dict[str, Any]:
    """Format an error response."""
    response = {
        "success": False,
        "error": error
    }
    if suggestion:
        response["suggestion"] = suggestion
    return response


# Validation helpers
def validate_elevenlabs_id(id_value: str, id_type: str) -> bool:
    """Validate ElevenLabs ID format."""
    patterns = {
        'agent': r'^agent_[a-zA-Z0-9]+$',
        'conversation': r'^conv_[a-zA-Z0-9]+$',
        'document': r'^doc_[a-zA-Z0-9]+$',
        'test': r'^test_[a-zA-Z0-9]+$',
        'tool': r'^tool_[a-zA-Z0-9]+$',
        'server': r'^server_[a-zA-Z0-9]+$',
        'secret': r'^secret_[a-zA-Z0-9]+$',
        'widget': r'^widget_[a-zA-Z0-9]+$',
        'invocation': r'^inv_[a-zA-Z0-9]+$'
    }
    
    pattern = patterns.get(id_type)
    if not pattern:
        return False
    
    return bool(re.match(pattern, id_value))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(url_pattern, url))


def validate_mcp_server(config: Dict) -> bool:
    """Validate MCP server configuration."""
    required_fields = ['url', 'type']
    for field in required_fields:
        if field not in config:
            return False
    
    if config['type'] not in ['SSE', 'HTTP']:
        return False
    
    return validate_url(config['url'])


def validate_test_scenario(scenario: Dict) -> bool:
    """Validate test scenario structure."""
    required_fields = ['user', 'expected_response']
    for field in required_fields:
        if field not in scenario:
            return False
    return True


def validate_test_expectations(expectations: Dict) -> bool:
    """Validate test expectations."""
    valid_keys = ['response_time', 'sentiment', 'accuracy', 'contains', 'not_contains']
    for key in expectations:
        if key not in valid_keys:
            return False
    return True


# Caching helpers
_cache_store: Dict[str, Any] = {}


async def cache_get(key: str) -> Any:
    """Get value from cache."""
    return _cache_store.get(key)


async def cache_set(key: str, value: Any, ttl: int = None) -> None:
    """Set value in cache with optional TTL."""
    _cache_store[key] = value
    
    if ttl:
        async def expire():
            await asyncio.sleep(ttl)
            _cache_store.pop(key, None)
        asyncio.create_task(expire())


# Time helpers
def format_timestamp(timestamp: Optional[str]) -> str:
    """Format timestamp for display."""
    if not timestamp:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return timestamp


def calculate_duration(start: str, end: str) -> int:
    """Calculate duration in seconds between two timestamps."""
    try:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        return int((end_dt - start_dt).total_seconds())
    except:
        return 0


# Test helpers
def generate_test_report(results: List[Dict]) -> Dict[str, Any]:
    """Generate test report from results."""
    total = len(results)
    passed = sum(1 for r in results if r.get('status') == 'passed')
    failed = sum(1 for r in results if r.get('status') == 'failed')
    skipped = sum(1 for r in results if r.get('status') == 'skipped')
    
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'success_rate': (passed / total * 100) if total > 0 else 0,
        'summary': f"{passed}/{total} tests passed"
    }


def format_test_result(result: Dict) -> str:
    """Format test result for display."""
    status = result.get('status', 'unknown')
    name = result.get('name', 'Unnamed test')
    duration = result.get('duration', 0)
    
    status_emoji = {
        'passed': '✅',
        'failed': '❌',
        'skipped': '⏭️',
        'running': '🔄'
    }.get(status, '❓')
    
    return f"{status_emoji} {name} ({duration}ms)"