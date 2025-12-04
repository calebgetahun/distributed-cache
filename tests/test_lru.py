import pytest
from .conftest import small_cache
import time

from cache.lru import LRUCache


def test_get_on_missing_key_returns_none_and_counts_miss(small_cache):
    assert small_cache.get("missing") is None
    stats = small_cache.get_stats()
    assert stats.gets == 1
    assert stats.misses == 1
    assert stats.hits == 0
    assert stats.puts == 0
    assert stats.evictions == 0


def test_basic_put_and_get_and_overwrite(small_cache):
    small_cache = LRUCache[str, int](capacity=2)

    small_cache.put("a", 1)
    small_cache.put("b", 2)

    assert small_cache.get("a") == 1
    assert small_cache.get("b") == 2

    # overwrite value
    small_cache.put("a", 42)
    assert small_cache.get("a") == 42

    # dict size should still be 2
    assert len(small_cache.cache) == 2

    stats = small_cache.get_stats()
    # 3 puts (a, b, a overwrite)
    assert stats.puts == 3
    # 3 gets (a, b, a)
    assert stats.gets == 3
    assert stats.hits == 3
    assert stats.misses == 0
    assert stats.evictions == 0


def test_lru_eviction_removes_least_recently_used(small_cache):
    small_cache.put("a", 1)
    small_cache.put("b", 2)
    small_cache.put("c", 3)

    # Access "a" so it becomes MRU, lru order now: b (LRU), c, a (MRU)
    assert small_cache.get("a") == 1

    # Insert "d" -> should evict "b"
    small_cache.put("d", 4)

    assert small_cache.get("b") is None  # evicted
    assert small_cache.get("a") == 1
    assert small_cache.get("c") == 3
    assert small_cache.get("d") == 4

    stats = small_cache.get_stats()
    assert stats.evictions == 1


def test_ttl_expiration_causes_miss_and_removes_key(small_cache):
    small_cache.put("a", 1, ttl=0.05)
    assert small_cache.get("a") == 1  # still alive

    time.sleep(0.06)

    # should be expired now
    assert small_cache.get("a") is None

    # and no longer in internal map
    assert "a" not in small_cache.cache

    stats = small_cache.get_stats()
    # gets: 2 (first hit, then miss)
    assert stats.gets == 2
    assert stats.hits == 1
    assert stats.misses == 1


def test_non_ttl_entry_does_not_expire_quickly(small_cache):
    small_cache.put("a", 1)
    time.sleep(0.05)
    # should still be there
    assert small_cache.get("a") == 1


def test_delete_removes_key_and_returns_bool(small_cache):
    small_cache.put("a", 1)
    assert small_cache.get("a") == 1

    # delete existing
    assert small_cache.delete("a") is True
    assert small_cache.get("a") is None
    assert "a" not in small_cache.cache

    # delete non-existing
    assert small_cache.delete("a") is False


def test_clear_resets_cache_and_stats(small_cache):
    small_cache.put("a", 1)
    small_cache.put("b", 2)
    _ = small_cache.get("a")

    small_cache.clear()

    assert small_cache.get("a") is None
    assert len(small_cache.cache) == 0

    stats = small_cache.get_stats()
    # after clear we expect fresh stats
    assert stats.hits == 0
    assert stats.misses == 1  # the get after clear
    assert stats.gets == 1
    assert stats.puts == 0
    assert stats.evictions == 0

    