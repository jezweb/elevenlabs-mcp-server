"""ElevenLabs API client wrapper for audio operations."""

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
    """Async client for ElevenLabs Audio API."""
    
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
    
    async def _request_binary(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> bytes:
        """Make an API request that returns binary data."""
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
            return response.content
        
        try:
            return await _do_request()
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
    
    # Text-to-Speech Methods
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        voice_settings: Optional[Dict] = None,
        output_format: str = "mp3_44100_128"
    ) -> bytes:
        """Convert text to speech."""
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings or {}
        }
        
        return await self._request_binary(
            "POST",
            f"/text-to-speech/{voice_id}",
            json_data=data,
            params={"output_format": output_format}
        )
    
    async def text_to_speech_stream(
        self,
        text: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        voice_settings: Optional[Dict] = None,
        output_format: str = "mp3_44100_128"
    ) -> AsyncClient:
        """Stream text to speech."""
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings or {}
        }
        
        client = await self._get_client()
        response = await client.post(
            f"/text-to-speech/{voice_id}/stream",
            json=data,
            params={"output_format": output_format}
        )
        response.raise_for_status()
        return response
    
    async def text_to_speech_with_timestamps(
        self,
        text: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        voice_settings: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate speech with word timestamps."""
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings or {}
        }
        
        return await self._request(
            "POST",
            f"/text-to-speech/{voice_id}/with-timestamps",
            json_data=data
        )
    
    # Speech-to-Text Methods
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language_code: Optional[str] = None,
        diarize: bool = False
    ) -> Dict[str, Any]:
        """Convert speech to text."""
        files = {
            "audio": ("audio.mp3", audio_data, "audio/mpeg")
        }
        params = {}
        if language_code:
            params["language_code"] = language_code
        if diarize:
            params["diarize"] = "true"
        
        return await self._request(
            "POST",
            "/speech-to-text",
            files=files,
            params=params
        )
    
    # Sound Generation Methods
    
    async def generate_sound_effect(
        self,
        text: str,
        duration_seconds: Optional[float] = None
    ) -> bytes:
        """Generate sound effect from text description."""
        data = {
            "text": text
        }
        if duration_seconds:
            data["duration_seconds"] = duration_seconds
        
        return await self._request_binary(
            "POST",
            "/sound-generation",
            json_data=data
        )
    
    # Audio Processing Methods
    
    async def isolate_audio(
        self,
        audio_data: bytes
    ) -> bytes:
        """Remove background noise from audio."""
        files = {
            "audio": ("audio.mp3", audio_data, "audio/mpeg")
        }
        
        return await self._request_binary(
            "POST",
            "/audio-isolation",
            files=files
        )
    
    # Voice Transformation Methods
    
    async def speech_to_speech(
        self,
        audio_data: bytes,
        voice_id: str,
        model_id: str = "eleven_english_sts_v2",
        voice_settings: Optional[Dict] = None,
        output_format: str = "mp3_44100_128"
    ) -> bytes:
        """Transform voice in audio to target voice."""
        files = {
            "audio": ("audio.mp3", audio_data, "audio/mpeg")
        }
        data = {
            "model_id": model_id,
            "voice_settings": json.dumps(voice_settings or {})
        }
        
        return await self._request_binary(
            "POST",
            f"/speech-to-speech/{voice_id}",
            files=files,
            params={**data, "output_format": output_format}
        )
    
    # Model and Voice Information Methods
    
    async def get_voices(self) -> List[Dict[str, Any]]:
        """Get available voices."""
        response = await self._request("GET", "/voices", use_cache=True)
        return response.get("voices", [])
    
    async def get_voice(self, voice_id: str) -> Dict[str, Any]:
        """Get voice details."""
        return await self._request("GET", f"/voices/{voice_id}", use_cache=True)
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Get available models."""
        response = await self._request("GET", "/models", use_cache=True)
        return response
    
    # Utility Methods
    
    async def test_connection(self) -> bool:
        """Test API connection."""
        try:
            await self._request("GET", "/user/subscription", use_cache=False)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False