import pytest
from cache.factory import create_cache
from cache.lru import LRUCache
from cache.eviction import EvictionPolicy

@pytest.fixture
def small_cache() -> LRUCache[str, int]:
    return create_cache(capacity=3, policy=EvictionPolicy.LRU)