# Distributed Cache

A modular caching system implemented in Python, featuring a thread-safe cache with TTL support and pluggable eviction policies. This repository is structured to support future expansion toward a networked, multi-node distributed cache.

---
## Setup + Testing
Clone the repository and optionally create a virtual environment: 

```bash
git clone https://github.com/calebgetahun/distributed-cache.git
cd distributed-cache

python3 -m venv venv
source venv/bin/activate  # optional

#for testing
pytest
```

---
## Features

- O(1) LRU cache implementation using a hashmap + doubly linked list  
- Optional TTL-based expiration  
- Thread-safe operations  
- Basic cache statistics (hits, misses, evictions, etc.)  
- Unit tests for core behavior  

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
