# cache/factory.py
from typing import TypeVar
from .base import Cache
from .eviction import EvictionPolicy
from .lru import LRUCache

K = TypeVar("K")
V = TypeVar("V")

def create_cache(capacity: int, policy: EvictionPolicy) -> Cache[K, V]:
    if policy == EvictionPolicy.LRU:
        return LRUCache(capacity)
    
    raise NotImplementedError(f"{policy} not implemented yet")