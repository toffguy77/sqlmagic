import time
from typing import Dict, Any, Optional
from functools import wraps

class SimpleCache:
    def __init__(self, ttl: int = 300):  # 5 minutes
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            if time.time() - self.cache[key]["timestamp"] < self.ttl:
                return self.cache[key]["value"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self.cache[key] = {"value": value, "timestamp": time.time()}
    
    def clear(self):
        self.cache.clear()

cache = SimpleCache()

def cached(key_func=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            result = await func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        return wrapper
    return decorator