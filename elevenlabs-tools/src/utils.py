"""Utility functions for ElevenLabs Integrations MCP server."""

import asyncio
import functools
import logging
import os
import re
from typing import Any, Dict, Optional, TypeVar, Callable
from datetime import datetime

import httpx
from httpx import AsyncClient


# Configuration
class Config:
    """Configuration for ElevenLabs Integrations server."""
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


def validate_tool_config(config: Dict) -> bool:
    """Validate tool configuration."""
    required_fields = ['name', 'type']
    for field in required_fields:
        if field not in config:
            return False
    return True


def validate_approval_rule(rule: Dict) -> bool:
    """Validate approval rule configuration."""
    if 'approval_mode' not in rule:
        return False
    
    if rule['approval_mode'] not in ['always', 'never', 'conditional']:
        return False
    
    if rule['approval_mode'] == 'conditional' and 'conditions' not in rule:
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


# Security helpers
def sanitize_secret_response(data: Dict) -> Dict:
    """Remove sensitive values from secret responses."""
    if 'value' in data:
        data['value'] = '***'
    if 'secrets' in data:
        for secret in data['secrets']:
            if 'value' in secret:
                secret['value'] = '***'
    return data


def validate_secret_name(name: str) -> bool:
    """Validate secret name format."""
    # Allow alphanumeric, underscore, and hyphen
    pattern = r'^[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, name))


# Integration helpers
def format_mcp_server_info(server: Dict) -> Dict:
    """Format MCP server information for display."""
    return {
        'id': server.get('id'),
        'name': server.get('name'),
        'url': server.get('url'),
        'type': server.get('type'),
        'status': server.get('status', 'unknown'),
        'tools_count': len(server.get('tools', [])),
        'approval_policy': server.get('approval_policy', 'unknown'),
        'created_at': format_timestamp(server.get('created_at'))
    }


def format_tool_info(tool: Dict) -> Dict:
    """Format tool information for display."""
    return {
        'id': tool.get('id'),
        'name': tool.get('name'),
        'description': tool.get('description'),
        'type': tool.get('type'),
        'parameters': tool.get('parameters', {}),
        'required_permissions': tool.get('required_permissions', []),
        'usage_count': tool.get('usage_count', 0)
    }