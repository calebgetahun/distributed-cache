from dataclasses import dataclass
from typing import Any, Hashable, Optional

@dataclass
class Node:
    key: Optional[Hashable] = None
    val: Any = None
    prev: Optional["Node"] = None
    next: Optional["Node"] = None
    expiration_time: Optional[float] = None  # UNIX timestamp