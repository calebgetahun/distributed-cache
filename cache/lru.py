from typing import Optional, List, Any

class Node:
    def __init__(self, key=-1, value=-1, prev=None, next=None):
        self.key = key
        self.val = value
        self.prev = prev
        self.next = next
    
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = dict()

        #sentinel heads for easier pointer usage
        self.head = Node()
        self.tail = Node()

        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_front(self, node):
        if node.prev or node.next:
            return
        
        node.next = self.head.next
        node.next.prev = node
        self.head.next = node
        node.prev = self.head

    def _remove(self, node):
        if node is self.head or node is self.tail:
            return
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

        #node to be moved to the front is detached so we should just add to front instead
        if not node.next and not node.prev:
            self._add_to_front(node)
            return
        
        node.prev.next = node.next
        node.next.prev = node.prev

        node.prev = None
        node.next = None

        self._add_to_front(node)

    def _pop_lru(self):
        to_remove = self.tail.prev
        if to_remove is self.head and self.head.next is self.tail:
            return
        

        to_remove.prev.next = self.tail
        self.tail.prev = to_remove.prev

        to_remove.prev = None
        to_remove.next = None

    def get(self, key) -> Optional[Any]:
        if key not in self.cache:
            return None

        node = self.cache[key]
        self._move_to_front(node)
        return node.val
    
    def put(self, key, value):
        if self.capacity == 0:
            return
        
        if key in self.cache:
            self.cache[key].val = value
            self._move_to_front(self.cache[key])
            return

        if len(self.cache) == self.capacity:
            node = self.tail.prev
            r_key = node.key
            self._pop_lru()
            del self.cache[r_key]
            
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._move_to_front(new_node)
