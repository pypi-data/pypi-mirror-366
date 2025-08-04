"""Advanced caching system for gdmongolite - Redis, Memory, Smart Invalidation"""

import json
import hashlib
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
import pickle
import weakref

from .core import Schema, DB, QueryResponse
from .exceptions import GDMongoError


class CacheManager:
    """Base cache manager interface"""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        raise NotImplementedError
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        raise NotImplementedError
    
    async def clear(self) -> bool:
        """Clear all cache"""
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        raise NotImplementedError


class MemoryCache(CacheManager):
    """In-memory cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.expiry = {}
        self.max_size = max_size
        self.access_order = []
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        if key in self.cache:
            # Check expiry
            if key in self.expiry and datetime.now() > self.expiry[key]:
                await self.delete(key)
                return None
            
            # Update access order for LRU
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            return self.cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in memory cache"""
        # Evict if at max size
        if len(self.cache) >= self.max_size and key not in self.cache:
            await self._evict_lru()
        
        self.cache[key] = value
        
        if ttl > 0:
            self.expiry[key] = datetime.now() + timedelta(seconds=ttl)
        
        # Update access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from memory cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.expiry:
                del self.expiry[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return True
        return False
    
    async def clear(self) -> bool:
        """Clear all memory cache"""
        self.cache.clear()
        self.expiry.clear()
        self.access_order.clear()
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache"""
        if key in self.cache:
            # Check expiry
            if key in self.expiry and datetime.now() > self.expiry[key]:
                await self.delete(key)
                return False
            return True
        return False
    
    async def _evict_lru(self):
        """Evict least recently used item"""
        if self.access_order:
            lru_key = self.access_order[0]
            await self.delete(lru_key)


class RedisCache(CacheManager):
    """Redis cache implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self._connected = False
    
    async def _connect(self):
        """Connect to Redis"""
        if not self._connected:
            try:
                import aioredis
                self.redis = aioredis.from_url(self.redis_url)
                self._connected = True
            except ImportError:
                raise GDMongoError("aioredis not installed. Install with: pip install aioredis")
            except Exception as e:
                raise GDMongoError(f"Failed to connect to Redis: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        await self._connect()
        try:
            value = await self.redis.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            print(f"Redis get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in Redis cache"""
        await self._connect()
        try:
            serialized = pickle.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        await self._connect()
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all Redis cache"""
        await self._connect()
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            print(f"Redis clear error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        await self._connect()
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False


class SmartCache:
    """Smart caching with automatic invalidation"""
    
    def __init__(self, cache_manager: CacheManager, db: DB):
        self.cache = cache_manager
        self.db = db
        self.invalidation_rules = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0
        }
    
    def add_invalidation_rule(self, collection: str, cache_patterns: List[str]):
        """Add cache invalidation rule for collection changes"""
        if collection not in self.invalidation_rules:
            self.invalidation_rules[collection] = []
        self.invalidation_rules[collection].extend(cache_patterns)
    
    async def get_or_set(
        self, 
        key: str, 
        fetch_func: Callable, 
        ttl: int = 3600,
        force_refresh: bool = False
    ) -> Any:
        """Get from cache or fetch and set"""
        if not force_refresh:
            cached_value = await self.cache.get(key)
            if cached_value is not None:
                self.cache_stats["hits"] += 1
                return cached_value
        
        self.cache_stats["misses"] += 1
        
        # Fetch fresh data
        if asyncio.iscoroutinefunction(fetch_func):
            fresh_value = await fetch_func()
        else:
            fresh_value = fetch_func()
        
        # Cache the result
        await self.cache.set(key, fresh_value, ttl)
        self.cache_stats["sets"] += 1
        
        return fresh_value
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache keys matching pattern"""
        # This is a simplified implementation
        # In production, you'd use Redis SCAN or similar
        self.cache_stats["invalidations"] += 1
        
        # For now, just clear all cache
        await self.cache.clear()
    
    async def invalidate_collection(self, collection: str):
        """Invalidate cache for collection changes"""
        if collection in self.invalidation_rules:
            for pattern in self.invalidation_rules[collection]:
                await self.invalidate_pattern(pattern)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "miss_rate": 1 - hit_rate
        }


class QueryCache:
    """Cache for database queries"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.default_ttl = 300  # 5 minutes
    
    def _generate_cache_key(self, schema: Schema, operation: str, **kwargs) -> str:
        """Generate cache key for query"""
        key_data = {
            "collection": schema._collection_name,
            "operation": operation,
            "params": kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return f"query:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def get_cached_query(
        self, 
        schema: Schema, 
        operation: str, 
        **kwargs
    ) -> Optional[Any]:
        """Get cached query result"""
        cache_key = self._generate_cache_key(schema, operation, **kwargs)
        return await self.cache.get(cache_key)
    
    async def cache_query_result(
        self, 
        schema: Schema, 
        operation: str, 
        result: Any,
        ttl: int = None,
        **kwargs
    ):
        """Cache query result"""
        cache_key = self._generate_cache_key(schema, operation, **kwargs)
        await self.cache.set(cache_key, result, ttl or self.default_ttl)
    
    async def invalidate_schema_cache(self, schema: Schema):
        """Invalidate all cache for a schema"""
        # This would need a more sophisticated implementation in production
        await self.cache.clear()


class CachedSchema:
    """Schema wrapper with automatic caching"""
    
    def __init__(self, schema: Schema, query_cache: QueryCache):
        self.schema = schema
        self.query_cache = query_cache
        self._wrap_methods()
    
    def _wrap_methods(self):
        """Wrap schema methods with caching"""
        original_find = self.schema.find
        
        def cached_find(**kwargs):
            """Cached find method"""
            cursor = original_find(**kwargs)
            original_to_list = cursor.to_list
            
            async def cached_to_list():
                # Check cache first
                cached_result = await self.query_cache.get_cached_query(
                    self.schema, "find", **kwargs
                )
                if cached_result is not None:
                    return cached_result
                
                # Fetch from database
                result = await original_to_list()
                
                # Cache result
                await self.query_cache.cache_query_result(
                    self.schema, "find", result, **kwargs
                )
                
                return result
            
            cursor.to_list = cached_to_list
            return cursor
        
        self.schema.find = cached_find


class CacheDecorator:
    """Decorator for caching function results"""
    
    def __init__(self, cache_manager: CacheManager, ttl: int = 3600):
        self.cache = cache_manager
        self.ttl = ttl
    
    def __call__(self, func: Callable):
        """Decorator implementation"""
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            key_string = json.dumps(key_data, sort_keys=True, default=str)
            cache_key = f"func:{hashlib.md5(key_string.encode()).hexdigest()}"
            
            # Check cache
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache result
            await self.cache.set(cache_key, result, self.ttl)
            
            return result
        
        return wrapper


class CacheWarmer:
    """Pre-warm cache with frequently accessed data"""
    
    def __init__(self, cache_manager: CacheManager, db: DB):
        self.cache = cache_manager
        self.db = db
        self.warming_tasks = []
    
    def add_warming_task(
        self, 
        name: str, 
        fetch_func: Callable, 
        cache_key: str,
        interval_seconds: int = 3600,
        ttl: int = 7200
    ):
        """Add cache warming task"""
        task = {
            "name": name,
            "fetch_func": fetch_func,
            "cache_key": cache_key,
            "interval": interval_seconds,
            "ttl": ttl,
            "last_run": None
        }
        self.warming_tasks.append(task)
    
    async def warm_cache(self, task_name: str = None):
        """Warm cache for specific task or all tasks"""
        tasks_to_run = self.warming_tasks
        
        if task_name:
            tasks_to_run = [t for t in self.warming_tasks if t["name"] == task_name]
        
        for task in tasks_to_run:
            try:
                # Fetch data
                if asyncio.iscoroutinefunction(task["fetch_func"]):
                    data = await task["fetch_func"]()
                else:
                    data = task["fetch_func"]()
                
                # Cache data
                await self.cache.set(task["cache_key"], data, task["ttl"])
                task["last_run"] = datetime.now()
                
                print(f"Cache warmed for task: {task['name']}")
                
            except Exception as e:
                print(f"Cache warming failed for {task['name']}: {e}")
    
    async def start_background_warming(self):
        """Start background cache warming"""
        async def warming_loop():
            while True:
                for task in self.warming_tasks:
                    if (task["last_run"] is None or 
                        datetime.now() - task["last_run"] >= timedelta(seconds=task["interval"])):
                        await self.warm_cache(task["name"])
                
                await asyncio.sleep(60)  # Check every minute
        
        asyncio.create_task(warming_loop())


# Integration with gdmongolite core
def add_caching_to_db(db: DB, cache_manager: CacheManager = None):
    """Add caching capabilities to DB instance"""
    if cache_manager is None:
        cache_manager = MemoryCache()
    
    db.cache_manager = cache_manager
    db.smart_cache = SmartCache(cache_manager, db)
    db.query_cache = QueryCache(cache_manager)
    db.cache_warmer = CacheWarmer(cache_manager, db)
    
    # Add cache decorator
    db.cached = lambda ttl=3600: CacheDecorator(cache_manager, ttl)
    
    return db


# Export all classes
__all__ = [
    "CacheManager",
    "MemoryCache", 
    "RedisCache",
    "SmartCache",
    "QueryCache",
    "CachedSchema",
    "CacheDecorator",
    "CacheWarmer",
    "add_caching_to_db"
]