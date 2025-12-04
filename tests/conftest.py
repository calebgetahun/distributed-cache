import pytest
from cache.factory import CacheFactory
from cache.lru import LRUCache
from cache.eviction import EvictionPolicy

@pytest.fixture
def small_cache() -> LRUCache[str, int]:
    return CacheFactory.create_cache(capacity=3, policy=EvictionPolicy.LRU)