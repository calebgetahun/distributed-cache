from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Hashable, TypeVar, Optional

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    gets: int = 0
    sets: int = 0


class Cache(ABC, Generic[K, V]):
    """
    Abstract cache interface.

    Implementations (LRU, LFU, FIFO, etc.) should be drop-in replaceable.
    """

    @abstractmethod
    def get(self, key: K) -> Optional[V]:
        ...

    @abstractmethod
    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        """
        ttl is in seconds. If None: no expiration.
        """
        ...

    @abstractmethod
    def delete(self, key: K) -> bool:
        """
        Return True if key existed and was removed, False otherwise.
        """
        ...

    @abstractmethod
    def get_stats(self) -> CacheStats:
        ...

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all entries from the cache.
        """
        ...
