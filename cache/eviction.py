from enum import Enum

class EvictionPolicy(str, Enum):
    LRU = "LRU"
    # LFU = "lfu"
    # FIFO = "fifo"