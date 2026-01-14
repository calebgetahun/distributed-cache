from typing import TypeVar, Generic, Dict, Hashable, Callable, List
from .base import Cache
from .eviction import EvictionPolicy
from .lru import LRUCache

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
    def create_local_cache(cls, capacity: int, policy: EvictionPolicy) -> Cache[K, V]:
        if capacity <= 0:
            raise ValueError("capacity must be greater than 0")
        
        cache_cls = cls._registry.get(policy)

        if cache_cls is None:
            raise NotImplementedError(f"{policy} has not been implemented")
    
        return cache_cls(capacity)
    
    @classmethod
    def create_local_shards(
        cls,
        total_capacity: int,
        policy: EvictionPolicy,
        shard_ids: List[int],
    ) -> Dict[int, Cache[K, V]]:
        if not shard_ids:
            raise ValueError("shard_ids cannot be empty")
        if total_capacity <= 0:
            raise ValueError("total_capacity must be greater than 0")
        if len(shard_ids) != len(set(shard_ids)):
            raise ValueError("shard_ids must contain unique values")
        
        cache_cls = cls._registry.get(policy)
        if cache_cls is None:
            raise NotImplementedError(f"{policy} has not been implemented")

        n = len(shard_ids)
        if n > total_capacity:
            raise ValueError("owned shard count cannot exceed total_capacity")

        base = total_capacity // n
        rem = total_capacity % n

        shards: Dict[int, Cache[K, V]] = {}
        for i, shard_id in enumerate(shard_ids):
            shard_capacity = base + (1 if i < rem else 0)
            shards[shard_id] = cache_cls(shard_capacity)

        return shards
