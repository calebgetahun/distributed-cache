from typing import Any, Dict, Optional
from threading import Lock
from .node import Node
from .base import Cache
    
class LRUCache(Cache):
    """
    Simple in-memory LRU cache with O(1) get/put.

    - Not distributed (yet).
    - Thread-safe at the method level via a lock.
    """

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("LRUCache capacity must be > 0")
    
        self.capacity: int = capacity
        self.cache = Dict[Any: Node] = {}

        #sentinel heads for easier pointer usage
        self.head = Node()
        self.tail = Node()

        self.head.next = self.tail
        self.tail.prev = self.head

        self._lock = Lock()

    def _add_to_front(self, node):
        """Insert node at front of list after head node"""
        if node.prev is not None or node.next is not None:
            raise RuntimeError("Attempting to add a node that already contains linkages")
        
        node.next = self.head.next
        node.prev = self.head

        self.head.next.prev = node
        self.head.next = node

    def _remove(self, node):
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

    def _move_to_front(self, node):
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

    def get(self, key) -> Optional[Any]:
        with self._lock:
            node = self.cache.get(key)
            if node is None:
                return None

            self._move_to_front(node)
            return node.val
    
    def put(self, key, value):
        with self._lock:
            if key in self.cache:
                node = self.cache[key]
                node.val = value
                self._move_to_front(node)
                return

            new_node = Node(key, value)
            self._add_to_front(new_node)
            self.cache[key] = new_node

            if len(self.cache) > self.capacity:
                lru = self._pop_lru()
                if lru is not None:
                    del self.cache[lru.key]
            
        new_node = Node(key, value)
        self._add_to_front(new_node)
        self.cache[key] = new_node
        