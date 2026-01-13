from .base import Cache, CacheStats
from typing import Optional, TypeVar, List, Hashable, Callable, Generic

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

class ShardedCache(Cache[K, V], Generic[K, V]):
    def __init__(self, shards: List[Cache[K, V]], *, hash_fn: Callable[[K], int] = hash):
        if not shards:
            raise ValueError("ShardedCache requires at least one shard")
        
        self._shards = shards
        self._n = len(shards)
        self._hash_fn = hash_fn

    def _shard(self, key: K) -> Cache[K, V]:
        return self._shards[self._hash_fn(key) % self._n]
    
    def get(self, key: K) -> Optional[V]:
        return self._shard(key).get(key)

    def put(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        self._shard(key).put(key, value, ttl)

    def delete(self, key: K) -> bool:
        return self._shard(key).delete(key)

    def get_stats(self) -> CacheStats:
        total = CacheStats()
        for shard in self._shards:
            s = shard.get_stats()
            total.hits += s.hits
            total.misses += s.misses
            total.evictions += s.evictions
            total.gets += s.gets
            total.puts += s.puts
        return total

    def clear(self) -> None:
        for shard in self._shards:
            shard.clear()