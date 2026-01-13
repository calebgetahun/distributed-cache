from __future__ import annotations
import time
from threading import Lock
from typing import Dict, Optional, TypeVar, Generic, Hashable

from .base import Cache, CacheStats
from .node import Node

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
    
class LRUCache(Cache[K, V], Generic[K, V]):
    """
    Simple in-memory LRU cache with O(1) get/put.

    - Not distributed (yet).
    - Thread-safe at the method level via a lock
    """
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("LRUCache capacity must be > 0")
    
        self.capacity = capacity
        self.cache: Dict[K, Node] = {}

        #sentinel heads for easier pointer usage
        self.head = Node()
        self.tail = Node()

        self.head.next = self.tail
        self.tail.prev = self.head

        self._lock = Lock()
        self._stats = CacheStats()

    def _add_to_front(self, node) -> None:
        """Insert node at front of list after head node"""
        if node.prev is not None or node.next is not None:
            raise RuntimeError("Attempting to add a node that already contains linkages")
        
        node.next = self.head.next
        node.prev = self.head

        self.head.next.prev = node
        self.head.next = node

    def _remove(self, node) -> None:
        """Remove node from list"""
        if node is self.head or node is self.tail:
            return
        
        if node.prev is None or node.next is None:
            raise RuntimeError("Attempting to remove a detached node")
        
        prev = node.prev
        nxt = node.next
        prev.next = nxt
        nxt.prev = prev

        node.prev = None
        node.next = None

    def _move_to_front(self, node) -> None:
        """
        Move selected node to the front of our DLL. Useful for refreshing what the most recently used node was
        """
        if node is self.head or node is self.tail:
            return
        
        if node.prev is self.head and self.head.next is node:
            return    
        
        self._remove(node)
        self._add_to_front(node)

    def _pop_lru(self) -> Optional[Node]:
        """
        Remove and return the least recently used *real* node.
        Returns None if cache is empty.
        """
        to_remove = self.tail.prev
        if to_remove is None or to_remove is self.head:
            return None

        self._remove(to_remove)
        return to_remove
    
    def _is_expired(self, node: Node, now: Optional[float] = None) -> bool:
        """
        Check if node is expired given the ttl it currently holds
        """
        if node is None:
            return False
        if node.expiration_time is None:
            return False
        if now is None:
            now = time.time()
        return now >= node.expiration_time
    
    def _delete_node(self, key: K, node: Node) -> None:
        """
        deletes a node from the cache and DLL
        """
        self._remove(node)
        if key in self.cache:
            del self.cache[key]

    def get(self, key: K) -> Optional[V]:
        with self._lock:
            self._stats.gets += 1
            node = self.cache.get(key)

            if node is None:
                self._stats.misses += 1
                return None
            
            now = time.time()

            if self._is_expired(node, now):
                self._delete_node(key, node)
                self._stats.misses += 1
                return None

            self._move_to_front(node)
            self._stats.hits += 1
            return node.val
    
    def put(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        with self._lock:
            now = time.time()
            node = self.cache.get(key)
            expiration_time = (now + ttl) if ttl is not None else None

            self._stats.puts += 1

            if node is not None:
                node.val = value
                node.expiration_time = expiration_time
                self._move_to_front(node)
                
                return

            new_node = Node(key, value)
            new_node.expiration_time = expiration_time
            self._add_to_front(new_node)
            self.cache[key] = new_node

            if len(self.cache) > self.capacity:
                lru = self._pop_lru()
                if lru is not None and lru.key in self.cache:
                    del self.cache[lru.key]
                    self._stats.evictions += 1
        
    def delete(self, key: K) -> bool:
        """
        Return True if key existed and was removed, False otherwise.
        """
        with self._lock:
            node = self.cache.get(key)
            if node is None:
                return False

            self._delete_node(key, node)
            return True

    def get_stats(self) -> CacheStats:
        """
        Returns collected stats for gets, puts, hits, misses, and evictions.
        """
        with self._lock:
            stats = self._stats
            return CacheStats(
                hits=stats.hits,
                misses=stats.misses,
                evictions=stats.evictions,
                gets=stats.gets,
                puts=stats.puts
            )

    def clear(self) -> None:
        """
        Remove all entries from the cache.
        """
        with self._lock:
            self.cache.clear()
            self.head.next = self.tail
            self.tail.prev = self.head
            self._stats = CacheStats()
    