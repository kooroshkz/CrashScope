"""
Cache management for API responses.
"""

import time
from typing import Dict, Tuple, Any, Optional


class CacheManager:
    """Manages caching for API responses to reduce API calls."""
    
    def __init__(self, default_timeout: int = 600):
        """Initialize cache manager.
        
        Args:
            default_timeout: Default cache timeout in seconds
        """
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self.default_timeout = default_timeout
    
    def get(self, key: str, timeout: Optional[int] = None) -> Optional[Any]:
        """Get value from cache if not expired.
        
        Args:
            key: Cache key
            timeout: Cache timeout in seconds (uses default if None)
            
        Returns:
            Cached value or None if expired/missing
        """
        if key not in self._cache:
            return None
        
        cache_time, value = self._cache[key]
        timeout = timeout or self.default_timeout
        
        if time.time() - cache_time > timeout:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (time.time(), value)
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
    
    def cleanup_expired(self, timeout: Optional[int] = None) -> int:
        """Remove expired entries from cache.
        
        Args:
            timeout: Expiry timeout (uses default if None)
            
        Returns:
            Number of entries removed
        """
        timeout = timeout or self.default_timeout
        current_time = time.time()
        expired_keys = []
        
        for key, (cache_time, _) in self._cache.items():
            if current_time - cache_time > timeout:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)