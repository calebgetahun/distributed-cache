from typing import TypeVar, Generic, Type, Dict, Hashable
from .base import Cache
from .eviction import EvictionPolicy
from .lru import LRUCache

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

class CacheFactory(Generic[K, V]):

    _registry: Dict[EvictionPolicy, Type[Cache[K, V]]] = {
        EvictionPolicy.LRU: LRUCache
    }

    @classmethod
    def register(cls, policy: EvictionPolicy, cache_cls: Type[Cache[K, V]]) -> None:
        cls._registry[policy] = cache_cls

    @classmethod
    def create_cache(cls, capacity: int, policy: EvictionPolicy) -> Cache[K, V]:
        if policy not in cls._registry:
            raise NotImplementedError(f"{policy} has not been implemented")
        
        cache_cls = cls._registry[policy]
        return cache_cls(capacity)
