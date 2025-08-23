"""ElevenLabs API client wrapper."""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, List
from urllib.parse import urljoin

import httpx
from httpx import AsyncClient, Response

from .config import Config
from .utils import retry_with_backoff

logger = logging.getLogger(__name__)


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
    
    # Agent Management Methods
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all conversational AI agents."""
        response = await self._request("GET", "/convai/agents", use_cache=True)
        return response.get("agents", [])
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent details."""
        return await self._request("GET", f"/convai/agents/{agent_id}", use_cache=True)
    
    async def create_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent."""
        return await self._request("POST", "/convai/agents", json_data=config)
    
    async def update_agent(self, agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent configuration."""
        return await self._request("PATCH", f"/convai/agents/{agent_id}", json_data=config)
    
    async def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent."""
        return await self._request("DELETE", f"/convai/agents/{agent_id}")
    
    # Knowledge Base Methods
    
    async def list_knowledge_base(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List knowledge base documents."""
        params = {"agent_id": agent_id} if agent_id else {}
        response = await self._request("GET", "/convai/knowledge-base", params=params, use_cache=True)
        return response.get("documents", [])
    
    async def add_document_url(self, name: str, url: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add document from URL."""
        data = {
            "name": name,
            "url": url,
            "metadata": metadata or {}
        }
        return await self._request("POST", "/convai/knowledge-base/url", json_data=data)
    
    async def add_document_text(self, name: str, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add document from text."""
        data = {
            "name": name,
            "text": text,
            "metadata": metadata or {}
        }
        return await self._request("POST", "/convai/knowledge-base/text", json_data=data)
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document."""
        return await self._request("DELETE", f"/convai/knowledge-base/{document_id}")
    
    # Conversation Methods
    
    async def list_conversations(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List conversations."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if agent_id:
            params["agent_id"] = agent_id
        
        response = await self._request("GET", "/convai/conversations", params=params, use_cache=True)
        return response.get("conversations", [])
    
    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation details."""
        return await self._request("GET", f"/convai/conversations/{conversation_id}", use_cache=True)
    
    async def get_transcript(self, conversation_id: str) -> str:
        """Get conversation transcript from the main conversation endpoint.
        
        Note: The dedicated /transcript endpoint has been deprecated.
        Transcript data is now included in the main conversation response.
        """
        conversation = await self._request("GET", f"/convai/conversations/{conversation_id}", use_cache=True)
        
        # Extract transcript from conversation data
        transcript_data = conversation.get("transcript", [])
        if isinstance(transcript_data, list):
            # Format transcript from message list
            lines = []
            for message in transcript_data:
                role = message.get("role", "unknown")
                content = message.get("message", "")
                lines.append(f"{role}: {content}")
            return "\n".join(lines)
        elif isinstance(transcript_data, str):
            return transcript_data
        else:
            return ""
    
    # Utility Methods
    
    async def test_connection(self) -> bool:
        """Test API connection."""
        try:
            await self._request("GET", "/user/subscription", use_cache=False)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False