# Distributed Cache

⚠️ **Experimental / R&D Repository**  
This repo contains exploratory work around caching and early distributed-system experiments.  

👉 The polished, production-oriented **in-process cache library** lives here:  
https://github.com/calebgetahun/cachelocal

---
A modular caching system implemented in Python, featuring a thread-safe cache with TTL support and pluggable eviction policies. This repository is structured to support future expansion toward a networked, multi-node distributed cache.

---
## Features

- O(1) LRU cache implementation using a hashmap + doubly linked list  
- Optional TTL-based expiration  
- Thread-safe operations  
- Basic cache statistics (hits, misses, evictions, etc.)  
- Unit tests for core behavior
- Local sharding with N caches each with per shard eviction

---
## Usage Example
```python
from cache.factory import CacheFactory
from cache.eviction import EvictionPolicy

lru_cache = CacheFactory.create_cache(
    capacity=3,
    policy=EvictionPolicy.LRU
)
lru_cache.put(1, 4, ttl=3.0)
value = lru_cache.get(1)
```

---
## License
MIT License
