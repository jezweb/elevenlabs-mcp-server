"""Configuration management for ElevenLabs MCP servers."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration for ElevenLabs MCP servers."""
    
    # API Configuration
    API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.elevenlabs.io/v1")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Server Configuration
    SERVER_NAME: str = "elevenlabs-mcp"
    SERVER_VERSION: str = "0.1.0"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default
    
    # Feature Flags
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENABLE_ADVANCED_FEATURES: bool = os.getenv("ENABLE_ADVANCED_FEATURES", "false").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        errors = []
        
        if not cls.API_KEY:
            errors.append("ELEVENLABS_API_KEY environment variable is required")
        
        if not cls.API_BASE_URL:
            errors.append("API_BASE_URL cannot be empty")
        
        if cls.API_TIMEOUT <= 0:
            errors.append("API_TIMEOUT must be positive")
        
        if cls.MAX_RETRIES < 0:
            errors.append("MAX_RETRIES cannot be negative")
        
        if errors:
            error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)
        
        return True
    
    @classmethod
    def get_headers(cls) -> dict:
        """Get API headers with authentication."""
        return {
            "xi-api-key": cls.API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if API is properly configured."""
        return bool(cls.API_KEY)
    
    @classmethod
    def mask_api_key(cls) -> str:
        """Return masked API key for logging."""
        if not cls.API_KEY:
            return "not-set"
        if len(cls.API_KEY) <= 8:
            return "***"
        return f"{cls.API_KEY[:4]}...{cls.API_KEY[-4:]}"