from enum import Enum

class EvictionPolicy(str, Enum):
    LRU = "lru"
    # LFU = "lfu"
    # FIFO = "fifo"