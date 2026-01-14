from .factory import CacheFactory
from .eviction import EvictionPolicy
import time

# Example usage of the LRU cache using CacheFactory. IMPORTANT: not meant to be production example
lru_cache = CacheFactory.create_cache(
    capacity=3,
    policy=EvictionPolicy.LRU
)
lru_cache.put(1, 4, ttl=3.0)
lru_cache.put(2, 5, ttl=1.0)
lru_cache.put(3, 6)
lru_cache.put(4, 7)

print(lru_cache.get(1)) # None because evicted
print(lru_cache.get(2)) # 5 because TTL hasn't expired
time.sleep(1.2)
print(lru_cache.get(2)) # None because TTL has passed
