"""Cache utilities using Redis."""

import json
import pickle
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Optional, Union

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from mlperf.utils.config import get_settings
from mlperf.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Global Redis client
_redis_client: Optional[redis.Redis] = None
_connection_pool: Optional[ConnectionPool] = None


def get_connection_pool() -> ConnectionPool:
    """Get or create Redis connection pool."""
    global _connection_pool
    
    if _connection_pool is None:
        _connection_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_POOL_SIZE,
            decode_responses=settings.REDIS_DECODE_RESPONSES,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        logger.info(f"Created Redis connection pool for {settings.REDIS_URL}")
    
    return _connection_pool


async def get_redis_client() -> redis.Redis:
    """Get or create async Redis client."""
    global _redis_client
    
    if _redis_client is None:
        pool = get_connection_pool()
        _redis_client = redis.Redis(connection_pool=pool)
        
        # Test connection
        try:
            await _redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            _redis_client = None
            raise
    
    return _redis_client


async def close_redis() -> None:
    """Close Redis connections."""
    global _redis_client, _connection_pool
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Closed Redis client")
    
    if _connection_pool is not None:
        await _connection_pool.disconnect()
        _connection_pool = None
        logger.info("Closed Redis connection pool")


class Cache:
    """Cache interface using Redis."""
    
    def __init__(self, prefix: str = "openperf"):
        self.prefix = prefix
        self._client: Optional[redis.Redis] = None
    
    async def _get_client(self) -> redis.Redis:
        """Get Redis client."""
        if self._client is None:
            self._client = await get_redis_client()
        return self._client
    
    def _make_key(self, key: str) -> str:
        """Create namespaced cache key."""
        return f"{self.prefix}:{key}"
    
    async def get(
        self,
        key: str,
        default: Any = None,
        deserialize: bool = True
    ) -> Any:
        """Get value from cache."""
        try:
            client = await self._get_client()
            value = await client.get(self._make_key(key))
            
            if value is None:
                return default
            
            if deserialize and isinstance(value, (str, bytes)):
                try:
                    # Try JSON first
                    if isinstance(value, bytes):
                        value = value.decode()
                    return json.loads(value)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Try pickle
                    if isinstance(value, str):
                        value = value.encode()
                    return pickle.loads(value)
            
            return value
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None,
        serialize: bool = True
    ) -> bool:
        """Set value in cache."""
        try:
            client = await self._get_client()
            
            if serialize:
                try:
                    # Try JSON first for better compatibility
                    value = json.dumps(value)
                except (TypeError, ValueError):
                    # Fall back to pickle for complex objects
                    value = pickle.dumps(value)
            
            # Convert timedelta to seconds
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            elif ttl is None:
                ttl = settings.CACHE_TTL
            
            cache_key = self._make_key(key)
            
            if ttl > 0:
                await client.setex(cache_key, ttl, value)
            else:
                await client.set(cache_key, value)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from cache."""
        try:
            client = await self._get_client()
            cache_keys = [self._make_key(key) for key in keys]
            return await client.delete(*cache_keys)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            client = await self._get_client()
            return await client.exists(self._make_key(key)) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter."""
        try:
            client = await self._get_client()
            return await client.incrby(self._make_key(key), amount)
        except Exception as e:
            logger.error(f"Cache incr error for key {key}: {e}")
            return None
    
    async def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement a counter."""
        try:
            client = await self._get_client()
            return await client.decrby(self._make_key(key), amount)
        except Exception as e:
            logger.error(f"Cache decr error for key {key}: {e}")
            return None
    
    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set expiration time for a key."""
        try:
            client = await self._get_client()
            
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            return await client.expire(self._make_key(key), ttl)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> Optional[int]:
        """Get time to live for a key."""
        try:
            client = await self._get_client()
            ttl = await client.ttl(self._make_key(key))
            return ttl if ttl >= 0 else None
        except Exception as e:
            logger.error(f"Cache ttl error for key {key}: {e}")
            return None
    
    async def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with a given prefix."""
        try:
            client = await self._get_client()
            pattern = f"{self.prefix}:{prefix}*"
            
            # Use scan to avoid blocking on large datasets
            deleted = 0
            async for key in client.scan_iter(match=pattern, count=100):
                await client.delete(key)
                deleted += 1
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache clear_prefix error: {e}")
            return 0
    
    async def get_many(self, *keys: str) -> dict:
        """Get multiple values at once."""
        try:
            client = await self._get_client()
            cache_keys = [self._make_key(key) for key in keys]
            values = await client.mget(cache_keys)
            
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        if isinstance(value, bytes):
                            value = value.decode()
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        if isinstance(value, str):
                            value = value.encode()
                        try:
                            result[key] = pickle.loads(value)
                        except Exception:
                            result[key] = value
                else:
                    result[key] = None
            
            return result
            
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return {key: None for key in keys}
    
    async def set_many(
        self,
        mapping: dict,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set multiple values at once."""
        try:
            client = await self._get_client()
            
            # Prepare values
            cache_mapping = {}
            for key, value in mapping.items():
                try:
                    serialized = json.dumps(value)
                except (TypeError, ValueError):
                    serialized = pickle.dumps(value)
                cache_mapping[self._make_key(key)] = serialized
            
            # Set values
            await client.mset(cache_mapping)
            
            # Set expiration if needed
            if ttl is not None:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                
                for key in cache_mapping:
                    await client.expire(key, ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False


def cached(
    key_func: Optional[Callable] = None,
    ttl: Optional[Union[int, timedelta]] = None,
    prefix: str = "func"
):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        cache = Cache(prefix=f"openperf:{prefix}")
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                if args:
                    key_parts.extend(str(arg) for arg in args)
                if kwargs:
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # Call function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)
            
            await cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        # Add cache control methods
        wrapper.invalidate = lambda *args, **kwargs: cache.delete(
            key_func(*args, **kwargs) if key_func else f"{func.__name__}:{':'.join(str(arg) for arg in args)}"
        )
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


# Create default cache instance
default_cache = Cache()


# Convenience functions
async def cache_get(key: str, default: Any = None) -> Any:
    """Get value from default cache."""
    return await default_cache.get(key, default)


async def cache_set(
    key: str,
    value: Any,
    ttl: Optional[Union[int, timedelta]] = None
) -> bool:
    """Set value in default cache."""
    return await default_cache.set(key, value, ttl)


async def cache_delete(*keys: str) -> int:
    """Delete keys from default cache."""
    return await default_cache.delete(*keys)


async def cache_clear(prefix: str = "") -> int:
    """Clear cache keys with prefix."""
    return await default_cache.clear_prefix(prefix)