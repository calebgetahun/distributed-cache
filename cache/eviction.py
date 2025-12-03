from enum import Enum

class EvictionPolicy(Enum):
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    ARC = "arc"
    TinyLFU = "tinylfu"