from typing import TypeVar, Generic, Type, Dict, Hashable, Callable
from .base import Cache
from .eviction import EvictionPolicy
from .lru import LRUCache
from .sharded import ShardedCache

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

class CacheFactory(Generic[K, V]):

    _registry: Dict[EvictionPolicy, Callable[[int], Cache[K, V]]] = {
        EvictionPolicy.LRU: LRUCache
    }

    @classmethod
    def register(cls, policy: EvictionPolicy, cache_cls: Callable[[int], Cache[K, V]]) -> None:
        cls._registry[policy] = cache_cls

    @classmethod
    def create_cache(cls, 
                     capacity: int, 
                     policy: EvictionPolicy, 
                     shards: int = 1,
    ) -> Cache[K, V]:
        if policy not in cls._registry:
            raise NotImplementedError(f"{policy} has not been implemented")
        
        if shards <= 0:
            raise ValueError("shards must be a positive integer")
        
        if shards > capacity:
            raise ValueError("shards cannot exceed capacity")
        
        cache_cls = cls._registry[policy]

        if shards == 1:
            return cache_cls(capacity)
        
        base = capacity // shards
        rem = capacity % shards
        shard_caches = [
            cache_cls(base + (1 if i < rem else 0)) for i in range(shards)
        ]

        return ShardedCache(shard_caches)
