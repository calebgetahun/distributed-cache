import pytest
from cache.lru import LRUCache, Node

@pytest.fixture
def small_cache():
    return LRUCache(capacity=2)

@pytest.fixture
def large_cache():
    return LRUCache(capacity=4)

def test_one():
    cache = LRUCache(capacity=4)
    node_one = Node(1, 4)
    node_two = Node(2, 6)
    node_three = Node(3, 7)

    cache._add_to_front(node_two)
    cache._add_to_front(node_one)
    cache._move_to_front(node_two)
    cache._add_to_front(node_three)
    

    cache._pop_lru()
    # cache.put(1, 1)
    # cache.put(2, 2)

    assert cache.head.next is node_three
    assert node_two.next is cache.tail
    assert cache.tail.prev is node_two
    