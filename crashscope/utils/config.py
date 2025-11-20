"""
Configuration management for CrashScope.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for environment variables and settings."""
    
    _loaded = False
    
    @classmethod
    def _ensure_loaded(cls):
        """Ensure environment variables are loaded."""
        if not cls._loaded:
            load_dotenv()
            cls._loaded = True
    
    @classmethod
    def get_tomtom_api_key(cls) -> str:
        """Get TomTom API key from environment."""
        cls._ensure_loaded()
        api_key = os.getenv('TOMTOM_API_KEY')
        if not api_key:
            raise ValueError("TOMTOM_API_KEY not found in environment")
        return api_key
    
    @classmethod
    def get_cache_timeout(cls) -> int:
        """Get cache timeout in seconds."""
        cls._ensure_loaded()
        return int(os.getenv('CACHE_TIMEOUT', '600'))  # 10 minutes
    
    @classmethod
    def get_request_timeout(cls) -> int:
        """Get API request timeout in seconds."""
        cls._ensure_loaded()
        return int(os.getenv('REQUEST_TIMEOUT', '10'))
    
    @classmethod
    def get_osm_overpass_url(cls) -> str:
        """Get OpenStreetMap Overpass API URL."""
        cls._ensure_loaded()
        return os.getenv(
            'OSM_OVERPASS_URL',
            'https://overpass-api.de/api/interpreter'
        )
    
    @classmethod
    def get_weather_api_url(cls) -> str:
        """Get Open-Meteo weather API URL."""
        cls._ensure_loaded()
        return os.getenv(
            'WEATHER_API_URL',
            'https://api.open-meteo.com/v1/forecast'
        )