"""
Redis caching implementation for Owlban Group Platform
"""

import json
import pickle
from typing import Any, Optional, Union
import redis
from redis import Redis
import os
from functools import wraps
from datetime import timedelta

class RedisCache:
    """
    Redis cache implementation with TTL support and serialization
    """

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0,
                 password: Optional[str] = None, decode_responses: bool = False):
        """
        Initialize Redis connection

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            decode_responses: Whether to decode responses as strings
        """
        self.redis_url = os.getenv('REDIS_URL', f'redis://:{password}@{host}:{port}/{db}' if password else f'redis://{host}:{port}/{db}')

        try:
            self.client = Redis.from_url(
                self.redis_url,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.client.ping()
            self.connected = True
            print("✅ Redis cache connected successfully")
        except redis.ConnectionError:
            print("❌ Redis connection failed - cache will be disabled")
            self.client = None
            self.connected = False

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.connected or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value is None:
                return None

            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
        except Exception as e:
            print(f"❌ Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[Union[int, timedelta]] = None) -> bool:
        """
        Set value in cache with optional TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live (seconds or timedelta)

        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            return False

        try:
            # Serialize value - try JSON first, then pickle
            try:
                serialized_value = json.dumps(value)
            except (TypeError, ValueError):
                serialized_value = pickle.dumps(value)

            if ttl is not None:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                return bool(self.client.setex(key, ttl, serialized_value))
            else:
                return bool(self.client.set(key, serialized_value))
        except Exception as e:
            print(f"❌ Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        if not self.connected or not self.client:
            return False

        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"❌ Cache delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.connected or not self.client:
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"❌ Cache exists error: {e}")
            return False

    def clear(self, pattern: str = "*") -> bool:
        """
        Clear cache keys matching pattern

        Args:
            pattern: Pattern to match (default: "*" for all keys)

        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            return False

        try:
            keys = self.client.keys(pattern)
            if keys:
                return bool(self.client.delete(*keys))
            return True
        except Exception as e:
            print(f"❌ Cache clear error: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """
        Get TTL for a key

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -2 if key doesn't exist, -1 if no TTL
        """
        if not self.connected or not self.client:
            return -2

        try:
            return self.client.ttl(key)
        except Exception as e:
            print(f"❌ Cache TTL error: {e}")
            return -2

    def is_connected(self) -> bool:
        """
        Check if Redis is connected

        Returns:
            True if connected, False otherwise
        """
        return self.connected

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        if not self.connected or not self.client:
            return {'connected': False}

        try:
            info = self.client.info()
            return {
                'connected': True,
                'keys': self.client.dbsize(),
                'memory_used': info.get('used_memory_human', 'N/A'),
                'connections': info.get('connected_clients', 0),
                'uptime': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            print(f"❌ Cache stats error: {e}")
            return {'connected': False, 'error': str(e)}

# Global cache instance
_cache_instance = None

def get_cache() -> RedisCache:
    """
    Get global cache instance (singleton pattern)

    Returns:
        RedisCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance

def cached(ttl: Optional[Union[int, timedelta]] = None, key_prefix: str = ""):
    """
    Decorator to cache function results

    Args:
        ttl: Time to live for cache entry
        key_prefix: Prefix for cache key

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            if not cache.is_connected():
                return func(*args, **kwargs)

            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator

def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    key_parts = []
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)
